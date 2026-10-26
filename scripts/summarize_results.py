"""Validate and summarize an evaluation run.

    python scripts/summarize_results.py evaluation/runs/<run_id>               # write summary.md / summary.json
    python scripts/summarize_results.py evaluation/runs/<run_id> --check-only  # only report data problems

Inputs (all inside the run folder; everything except run_sheet.csv is optional):
    run_sheet.csv, responses/*.md, blind/blind_key.csv, blind/ratings/*.csv,
    comprehension/responses.csv, comprehension/exposure.csv

Missing or malformed data is reported, never silently dropped. Nothing here computes a
"comprehension score" from text features; comprehension comes only from human test data.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402

C_CONDITIONS = {"C_skill", "C_skill_explicit"}


@dataclass
class Issues:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def bootstrap_ci(values: list[float], n_boot: int, seed: int) -> tuple[float, float] | None:
    if len(values) < 2 or n_boot <= 0:
        return None
    rng = random.Random(seed)
    n = len(values)
    means = sorted(statistics.fmean(rng.choices(values, k=n)) for _ in range(n_boot))
    low = means[int(0.025 * (n_boot - 1))]
    high = means[int(0.975 * (n_boot - 1))]
    return low, high


def paired_summary(x: dict[str, float], y: dict[str, float], n_boot: int, seed: int) -> dict:
    keys = sorted(set(x) & set(y))
    diffs = [x[k] - y[k] for k in keys]
    ci = bootstrap_ci(diffs, n_boot, seed)
    return {
        "n": len(diffs),
        "mean_diff": mean(diffs),
        "sd_diff": statistics.stdev(diffs) if len(diffs) > 1 else None,
        "ci95": list(ci) if ci else None,
        "wins": sum(d > 0 for d in diffs),
        "ties": sum(d == 0 for d in diffs),
        "losses": sum(d < 0 for d in diffs),
    }


def fmt(value, digits: int = 2) -> str:
    if value is None:
        return "–"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def fmt_ci(ci) -> str:
    return f"[{ci[0]:.2f}, {ci[1]:.2f}]" if ci else "–"


# ---------------------------------------------------------------------------
# Loading and validation
# ---------------------------------------------------------------------------

def check_columns(path: Path, found: list[str], expected: list[str], issues: Issues) -> bool:
    missing = [c for c in expected if c not in found]
    if missing:
        issues.error(f"{path.name}: missing column(s) {missing}")
        return False
    extra = [c for c in found if c not in expected]
    if extra:
        issues.warn(f"{path.name}: unexpected column(s) {extra} ignored")
    return True


def load_run(run_dir: Path, cases: dict, conditions: dict, issues: Issues) -> list[dict]:
    sheet = run_dir / "run_sheet.csv"
    if not sheet.is_file():
        issues.error(f"run sheet not found: {sheet}")
        return []
    columns, rows = es.read_csv(sheet)
    if not check_columns(sheet, columns, es.RESULTS_COLUMNS, issues):
        return []
    seen = set()
    for row in rows:
        rid = row["row_id"] or "(blank row_id)"
        if rid in seen:
            issues.error(f"run sheet: duplicate row_id {rid}")
        seen.add(rid)
        if row["case_id"] not in cases:
            issues.error(f"{rid}: unknown case_id '{row['case_id']}'")
        if row["condition"] not in conditions["conditions"]:
            issues.error(f"{rid}: unknown condition '{row['condition']}'")
        path = run_dir / row["response_file"] if row["response_file"] else None
        row["_has_response"] = bool(path and path.is_file() and path.read_text(encoding="utf-8").strip())
        if not row["_has_response"]:
            issues.error(f"{rid}: response file missing or empty ({row['response_file'] or 'no path'})")
            row["_words"] = None
        else:
            row["_words"] = es.word_count(path.read_text(encoding="utf-8"))
        for column in es.RESULTS_REQUIRED:
            if row["_has_response"] and not row[column]:
                issues.error(f"{rid}: required column '{column}' is empty")
        activation = row["activation_observed"].lower()
        if activation and activation not in es.ACTIVATION_VALUES:
            issues.error(f"{rid}: activation_observed '{row['activation_observed']}' not in {sorted(es.ACTIVATION_VALUES)}")
        if row["condition"] in C_CONDITIONS and activation == "na":
            issues.error(f"{rid}: activation_observed is 'na' for a skill condition")
        if row["batch"] != "skill_off" and row["_has_response"] and not row["skill_zip_sha256"]:
            issues.warn(f"{rid}: skill_zip_sha256 not recorded")
        row["_activation"] = activation
        row["_expectation"] = cases.get(row["case_id"], {}).get("skill_expectation", "")
    labels = {r["model_label"] for r in rows if r["model_label"]}
    if len(labels) > 1:
        issues.warn(f"run uses more than one model label: {sorted(labels)}")
    return rows


def parse_score(value: str, dim: str, ctx: str, issues: Issues):
    if value == "":
        issues.error(f"{ctx}: '{dim}' is empty")
        return None
    if es.is_na(value):
        if dim in es.DIMENSIONS_ALLOWING_NA:
            return "NA"
        issues.error(f"{ctx}: '{dim}' does not allow NA")
        return None
    try:
        score = int(value)
    except ValueError:
        issues.error(f"{ctx}: '{dim}' value '{value}' is not an integer 1-5 or NA")
        return None
    if not 1 <= score <= 5:
        issues.error(f"{ctx}: '{dim}' value {score} outside 1-5")
        return None
    return score


def parse_count(value: str, column: str, ctx: str, issues: Issues) -> int | None:
    if value == "":
        issues.error(f"{ctx}: '{column}' is empty (use 0)")
        return None
    try:
        count = int(value)
    except ValueError:
        issues.error(f"{ctx}: '{column}' value '{value}' is not a whole number")
        return None
    if count < 0:
        issues.error(f"{ctx}: '{column}' is negative")
        return None
    return count


def load_ratings(run_dir: Path, rows: list[dict], cases: dict, issues: Issues) -> tuple[dict, list[dict]]:
    blind_dir = run_dir / "blind"
    key_path = blind_dir / "blind_key.csv"
    if not key_path.is_file():
        issues.warn("no blind/blind_key.csv yet; rating analyses skipped")
        return {}, []
    columns, key_rows = es.read_csv(key_path)
    if not check_columns(key_path, columns, es.BLIND_KEY_COLUMNS, issues):
        return {}, []
    row_by_id = {r["row_id"]: r for r in rows}
    key = {}
    for k in key_rows:
        if k["row_id"] not in row_by_id:
            issues.error(f"blind key: row_id {k['row_id']} not in run sheet")
            continue
        key[k["blind_id"]] = row_by_id[k["row_id"]]

    ratings: list[dict] = []
    rating_files = sorted((blind_dir / "ratings").glob("*.csv")) if (blind_dir / "ratings").is_dir() else []
    if not rating_files:
        issues.warn("no ratings files in blind/ratings/")
    for path in rating_files:
        columns, raw = es.read_csv(path)
        if not check_columns(path, columns, es.RATINGS_COLUMNS, issues):
            continue
        filled = [r for r in raw if any(r[d] for d in es.DIMENSIONS)]
        if len(filled) < len(raw):
            issues.error(f"{path.name}: {len(raw) - len(filled)} of {len(raw)} rows not yet rated")
        for r in filled:
            ctx = f"{path.name}/{r['blind_id']}"
            if r["blind_id"] not in key:
                issues.error(f"{ctx}: blind_id not in blind key")
                continue
            source = key[r["blind_id"]]
            if r["case_id"] and r["case_id"] != source["case_id"]:
                issues.error(f"{ctx}: case_id '{r['case_id']}' does not match the key ('{source['case_id']}')")
            case = cases.get(source["case_id"], {})
            valid_facts = {f["id"] for f in case.get("critical_facts", [])}
            parsed = {"rater": r["rater_id"] or path.stem, "blind_id": r["blind_id"], "row": source}
            for dim in es.DIMENSIONS:
                parsed[dim] = parse_score(r[dim], dim, ctx, issues)
            for column in es.COUNT_COLUMNS:
                parsed[column] = parse_count(r[column], column, ctx, issues)
            for column in ("critical_facts_present", "critical_facts_contradicted"):
                ids = es.split_list(r[column])
                bad = [i for i in ids if i not in valid_facts]
                if bad:
                    issues.error(f"{ctx}: {column} has ids not in case {source['case_id']}: {bad}")
                parsed[column] = [i for i in ids if i in valid_facts]
            codes = [c.upper() for c in es.split_list(r["adherence_violations"])]
            bad_codes = [c for c in codes if c not in es.ADHERENCE_CODES]
            if bad_codes:
                issues.error(f"{ctx}: unknown adherence code(s) {bad_codes}")
            parsed["adherence"] = {c for c in codes if c in es.ADHERENCE_CODES}
            parsed["rank"] = None
            if r["rank_within_case"]:
                try:
                    parsed["rank"] = int(r["rank_within_case"])
                except ValueError:
                    issues.error(f"{ctx}: rank_within_case '{r['rank_within_case']}' is not an integer")
            else:
                issues.warn(f"{ctx}: rank_within_case is empty")
            parsed["recognized"] = r["suspected_condition_recognized"].lower() in {"yes", "y", "true", "1"}
            ratings.append(parsed)
    rated = {r["blind_id"] for r in ratings}
    unrated = sorted(set(key) - rated)
    if rating_files and unrated:
        issues.error(f"{len(unrated)} blinded response(s) have no rating at all")
    return key, ratings


# ---------------------------------------------------------------------------
# Rating analyses
# ---------------------------------------------------------------------------

def response_level(ratings: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for r in ratings:
        grouped[r["blind_id"]].append(r)
    out = {}
    for blind_id, group in grouped.items():
        row = group[0]["row"]
        entry = {"row": row, "n_raters": len(group)}
        for dim in es.DIMENSIONS:
            nums = [g[dim] for g in group if isinstance(g[dim], int)]
            entry[dim] = mean(nums)
        entry["critical_flag"] = any((g["critical_errors"] or 0) > 0 or g["critical_facts_contradicted"] for g in group)
        entry["critical_errors_mean"] = mean([g["critical_errors"] for g in group if g["critical_errors"] is not None])
        entry["adherence_any"] = set().union(*(g["adherence"] for g in group))
        out[blind_id] = entry
    return out


def case_level(responses: dict[str, dict], metric: str) -> dict[str, dict[str, float]]:
    """{condition: {case_id: mean over samples}} for one metric."""
    acc: dict[tuple[str, str], list[float]] = defaultdict(list)
    for entry in responses.values():
        value = entry.get(metric)
        if value is not None:
            acc[(entry["row"]["condition"], entry["row"]["case_id"])].append(value)
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for (condition, case_id), values in acc.items():
        out[condition][case_id] = statistics.fmean(values)
    return out


def rank_case_level(ratings: list[dict]) -> dict[str, dict[str, float]]:
    acc: dict[tuple[str, str], list[int]] = defaultdict(list)
    for r in ratings:
        if r["rank"] is not None:
            acc[(r["row"]["condition"], r["row"]["case_id"])].append(r["rank"])
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for (condition, case_id), values in acc.items():
        out[condition][case_id] = statistics.fmean(values)
    return out


def agreement(ratings: list[dict]) -> dict[str, dict]:
    by_response: dict[str, list[dict]] = defaultdict(list)
    for r in ratings:
        by_response[r["blind_id"]].append(r)
    out = {}
    for dim in es.DIMENSIONS:
        exact = within1 = pairs = 0
        abs_diffs = []
        for group in by_response.values():
            nums = [g[dim] for g in group if isinstance(g[dim], int)]
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    d = abs(nums[i] - nums[j])
                    pairs += 1
                    exact += d == 0
                    within1 += d <= 1
                    abs_diffs.append(d)
        out[dim] = {
            "pairs": pairs,
            "exact": exact / pairs if pairs else None,
            "within_one": within1 / pairs if pairs else None,
            "mean_abs_diff": mean(abs_diffs),
        }
    return out


# ---------------------------------------------------------------------------
# Comprehension analyses
# ---------------------------------------------------------------------------

def load_comprehension(run_dir: Path, conditions: dict, n_boot: int, seed: int, issues: Issues) -> dict | None:
    comp_dir = run_dir / "comprehension"
    responses_path = comp_dir / "responses.csv"
    if not responses_path.is_file():
        return None
    bank = es.load_item_bank()
    items = {i["item_id"]: (topic_id, i) for topic_id, t in bank.items() for i in t["items"]}
    columns, rows = es.read_csv(responses_path)
    if not check_columns(responses_path, columns, es.COMPREHENSION_RESPONSE_COLUMNS, issues):
        return None

    scores: dict[tuple[str, str, str, str], list[tuple[str, float]]] = defaultdict(list)
    meta: dict[tuple[str, str], str] = {}
    for n, r in enumerate(rows, start=2):
        ctx = f"comprehension/responses.csv line {n}"
        if r["item_id"] not in items:
            issues.error(f"{ctx}: unknown item_id '{r['item_id']}'")
            continue
        topic_id, item = items[r["item_id"]]
        if r["topic_id"] != topic_id:
            issues.error(f"{ctx}: item {r['item_id']} belongs to topic {topic_id}, not '{r['topic_id']}'")
            continue
        if r["condition"] not in conditions["conditions"]:
            issues.error(f"{ctx}: unknown condition '{r['condition']}'")
            continue
        phase = r["phase"].lower()
        if phase not in es.COMPREHENSION_PHASES:
            issues.error(f"{ctx}: phase '{r['phase']}' not in {sorted(es.COMPREHENSION_PHASES)}")
            continue
        if (phase == "pre") != (item["phase"] == "pre"):
            issues.error(f"{ctx}: item {r['item_id']} is a {item['phase']} item but phase is '{phase}'")
            continue
        if r["score"] == "":
            issues.error(f"{ctx}: score is empty")
            continue
        try:
            score = float(r["score"])
        except ValueError:
            issues.error(f"{ctx}: score '{r['score']}' is not a number")
            continue
        maximum = 2 if item["format"] == "free_text" else 1
        if not 0 <= score <= maximum:
            issues.error(f"{ctx}: score {score} outside 0-{maximum}")
            continue
        key = (r["participant_id"], topic_id)
        if key in meta and meta[key] != r["condition"]:
            issues.error(f"{ctx}: participant {key[0]} has two conditions for topic {topic_id}")
        meta[key] = r["condition"]
        scores[(r["participant_id"], topic_id, phase, r["item_id"])].append((r["grader_id"].lower(), score))

    grader_pairs = grader_exact = 0
    resolved: dict[tuple[str, str, str, str], float] = {}
    for key, values in scores.items():
        final = [s for g, s in values if g == "resolved"]
        graded = [s for g, s in values if g != "resolved"]
        if len(graded) >= 2:
            grader_pairs += 1
            grader_exact += len(set(graded)) == 1
        resolved[key] = final[0] if final else statistics.fmean(graded)

    exposure = {}
    exposure_path = comp_dir / "exposure.csv"
    if exposure_path.is_file():
        columns, exp_rows = es.read_csv(exposure_path)
        if check_columns(exposure_path, columns, es.EXPOSURE_COLUMNS, issues):
            exposure = {(r["participant_id"], r["topic_id"]): r for r in exp_rows}
    else:
        issues.warn("comprehension/exposure.csv not found; attention exclusions and clarity ratings skipped")

    def num(value: str) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    per_pt: dict[tuple[str, str], dict] = {}
    excluded_attention = excluded_ceiling = 0
    for (pid, topic_id), condition in meta.items():
        topic_items = bank[topic_id]["items"]
        def total(phase: str, kinds: set[str] | None = None, fmt_: str = "mc") -> float | None:
            selected = [i for i in topic_items if i["format"] == fmt_ and (i["phase"] == "pre") == (phase == "pre")
                        and (kinds is None or i["type"] in kinds)]
            got = [resolved.get((pid, topic_id, phase, i["item_id"])) for i in selected]
            if not selected or any(g is None for g in got):
                return None
            return sum(got)
        n_pre = sum(1 for i in topic_items if i["phase"] == "pre")
        n_post_mc = sum(1 for i in topic_items if i["phase"] == "post" and i["format"] == "mc")
        pre, post = total("pre"), total("post")
        entry = {
            "condition": condition, "pre": pre, "post_mc": post,
            "transfer_misconception": total("post", {"transfer", "misconception"}),
            "explain": total("post", None, "free_text"),
            "delayed_mc": total("delayed"),
            "gain": (post / n_post_mc - pre / n_pre) if pre is not None and post is not None else None,
        }
        exp = exposure.get((pid, topic_id))
        if exp:
            seconds, words = num(exp["reading_seconds"]), num(exp["stimulus_words"])
            flagged = exp["attention_flag"].lower() in {"yes", "y", "true", "1"} or (
                seconds is not None and words is not None and seconds < 15 and words > 150)
            entry["clarity"] = num(exp["perceived_clarity"])
            entry["confidence"] = num(exp["confidence_after"])
            if flagged:
                excluded_attention += 1
                continue
        if pre is not None and pre >= n_pre:
            entry["gain"] = None
            excluded_ceiling += 1
        per_pt[(pid, topic_id)] = entry

    outcomes = ["transfer_misconception", "explain", "gain", "delayed_mc"]
    by_condition = {}
    for condition in sorted({e["condition"] for e in per_pt.values()}):
        group = [e for e in per_pt.values() if e["condition"] == condition]
        by_condition[condition] = {
            o: mean([e[o] for e in group if e.get(o) is not None]) for o in [*outcomes, "pre", "post_mc", "clarity", "confidence"]
        }
        by_condition[condition]["n"] = len(group)

    contrasts = {}
    participants = sorted({pid for pid, _ in per_pt})
    for target, reference in (("C_skill_explicit", "B_prompt"), ("C_skill_explicit", "A_normal"), ("B_prompt", "A_normal")):
        contrasts[f"{target} - {reference}"] = {}
        for outcome in outcomes:
            x, y = {}, {}
            for pid in participants:
                for (p, _), e in per_pt.items():
                    if p != pid or e.get(outcome) is None:
                        continue
                    if e["condition"] == target:
                        x[pid] = e[outcome]
                    elif e["condition"] == reference:
                        y[pid] = e[outcome]
            contrasts[f"{target} - {reference}"][outcome] = paired_summary(x, y, n_boot, seed)

    by_topic = defaultdict(dict)
    for (pid, topic_id), e in per_pt.items():
        by_topic[topic_id].setdefault(e["condition"], []).append(e["transfer_misconception"])
    by_topic_means = {t: {c: mean([v for v in vals if v is not None]) for c, vals in conds.items()}
                      for t, conds in by_topic.items()}
    return {
        "participants": len(participants),
        "participant_topics_analysed": len(per_pt),
        "excluded_attention": excluded_attention,
        "ceiling_excluded_from_gain": excluded_ceiling,
        "explain_grader_pairs": grader_pairs,
        "explain_grader_exact_agreement": grader_exact / grader_pairs if grader_pairs else None,
        "by_condition": by_condition,
        "by_topic_transfer_misconception": by_topic_means,
        "contrasts": contrasts,
    }


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

MIN_CASES = 10
MIN_PARTICIPANTS = 6


def gate(entry: dict, n: int, minimum: int) -> dict:
    """Downgrade a verdict reached on too little data."""
    if entry["status"] in {"MET", "NOT_MET"} and n < minimum:
        entry["detail"] += f" (only {n}; at least {minimum} needed)"
        entry["status"] = "INSUFFICIENT_DATA"
    return entry


def criteria(rows, responses, rank_levels, comparisons, words_cl, comprehension,
             min_cases: int = MIN_CASES, min_participants: int = MIN_PARTICIPANTS) -> list[dict]:
    out = [{"id": "S1", "criterion": "Installs without structural errors",
            "status": "NOT_EVALUATED", "detail": "Record the upload result manually (RUNBOOK.md §3)."}]
    rated_cases = {e["row"]["case_id"] for e in responses.values()}

    eligible = [r for r in rows if r["condition"] == "C_skill" and r["_expectation"] == "should_apply" and r["_has_response"]]
    observed = [r for r in eligible if r["_activation"] in {"yes", "no", "unclear"}]
    if observed:
        rate = sum(r["_activation"] == "yes" for r in observed) / len(observed)
        out.append(gate({"id": "S2", "criterion": "Natural activation >= 60% on should_apply",
                         "status": "MET" if rate >= 0.6 else "NOT_MET", "detail": f"{rate:.0%} of {len(observed)}"},
                        len(observed), min_cases))
    else:
        out.append({"id": "S2", "criterion": "Natural activation >= 60% on should_apply", "status": "NOT_EVALUATED",
                    "detail": "No C_skill should_apply rows with activation recorded."})

    def hijack_rate(conds: set[str]) -> tuple[int, int]:
        group = [e for e in responses.values() if e["row"]["condition"] in conds
                 and e["row"]["_expectation"] == "should_not_apply"]
        return sum("HIJACK" in e["adherence_any"] for e in group), len(group)
    c_hits, c_n = hijack_rate(C_CONDITIONS)
    a_hits, a_n = hijack_rate({"A_normal"})
    if c_n:
        met = c_hits <= 1 and (not a_n or c_hits / c_n <= a_hits / a_n + 1e-9)
        out.append({"id": "S3", "criterion": "No hijacking of non-teaching requests", "status": "MET" if met else "NOT_MET",
                    "detail": f"HIJACK in {c_hits}/{c_n} C responses vs {a_hits}/{a_n} A responses"})
    else:
        out.append({"id": "S3", "criterion": "No hijacking of non-teaching requests", "status": "NOT_EVALUATED", "detail": "No rated should_not_apply C responses."})

    flags = case_level(responses, "critical_flag")
    c, b, a = flags.get("C_skill_explicit", {}), flags.get("B_prompt", {}), flags.get("A_normal", {})
    if c and b:
        c_total, b_total = sum(v > 0 for v in c.values()), sum(v > 0 for v in b.values())
        introduced = [k for k, v in c.items() if v > 0 and b.get(k, 1) == 0 and a.get(k, 1) == 0]
        met = c_total <= b_total and not introduced
        out.append(gate({"id": "S4", "criterion": "No critical errors introduced", "status": "MET" if met else "NOT_MET",
                         "detail": f"cases with a critical error: C_explicit {c_total}, B {b_total}; introduced by C: {introduced or 'none'}"},
                        len(rated_cases), min_cases))
    else:
        out.append({"id": "S4", "criterion": "No critical errors introduced", "status": "NOT_EVALUATED", "detail": "Needs rated C_skill_explicit and B_prompt."})

    ratio = words_cl.get("ratios", {}).get("C_skill_explicit / A_normal")
    length_ignored = sum("LENGTH_IGNORED" in e["adherence_any"] for e in responses.values() if e["row"]["condition"] in C_CONDITIONS)
    if ratio and ratio.get("should_apply") is not None:
        other = ratio.get("other")
        met = ratio["should_apply"] <= 1.5 and (other is None or other <= 1.2) and length_ignored == 0
        n_cases = len({r["case_id"] for r in rows if r["condition"] == "C_skill_explicit" and r["_words"] is not None})
        out.append(gate({"id": "S5", "criterion": "No systematic verbosity", "status": "MET" if met else "NOT_MET",
                         "detail": f"median ratio should_apply {fmt(ratio['should_apply'])}, other {fmt(other)}; LENGTH_IGNORED in C: {length_ignored}"},
                        n_cases, min_cases))
    else:
        out.append({"id": "S5", "criterion": "No systematic verbosity", "status": "NOT_EVALUATED", "detail": "Needs C_skill_explicit and A_normal responses."})

    comp = comparisons.get("C_skill_explicit vs B_prompt")
    win = rank_levels.get("C_skill_explicit vs B_prompt")
    if comp:
        primary_ok = all(
            comp[d]["mean_diff"] is not None and comp[d]["mean_diff"] > 0 and comp[d]["ci95"] and comp[d]["ci95"][0] > 0
            for d in es.PRIMARY_DIMENSIONS)
        rank_ok = bool(win and win["n"] and win["wins"] / win["n"] >= 0.6)
        detail = "; ".join(f"{d}: {fmt(comp[d]['mean_diff'])} {fmt_ci(comp[d]['ci95'])}" for d in es.PRIMARY_DIMENSIONS)
        if win and win["n"]:
            detail += f"; ranked above B in {win['wins']}/{win['n']} should_apply cases"
        n_compared = max(comp[d]["n"] for d in es.PRIMARY_DIMENSIONS)
        out.append(gate({"id": "S6", "criterion": "Pedagogical preference over B",
                         "status": "MET" if primary_ok or rank_ok else "NOT_MET", "detail": detail},
                        n_compared, min_cases))
    else:
        out.append({"id": "S6", "criterion": "Pedagogical preference over B", "status": "NOT_EVALUATED", "detail": "Needs rated C_skill_explicit and B_prompt."})

    if comprehension:
        cb = comprehension["contrasts"]["C_skill_explicit - B_prompt"]["transfer_misconception"]
        ca = comprehension["contrasts"]["C_skill_explicit - A_normal"]["transfer_misconception"]
        if cb["n"] and ca["n"]:
            met = cb["mean_diff"] >= 0 and ca["mean_diff"] >= 0
            out.append(gate({"id": "S7", "criterion": "Comprehension signal (directional)", "status": "MET" if met else "NOT_MET",
                             "detail": f"C-B {fmt(cb['mean_diff'])} {fmt_ci(cb['ci95'])} (n={cb['n']}); C-A {fmt(ca['mean_diff'])} {fmt_ci(ca['ci95'])} (n={ca['n']})"},
                            min(cb["n"], ca["n"]), min_participants))
        else:
            out.append({"id": "S7", "criterion": "Comprehension signal (directional)", "status": "NOT_EVALUATED", "detail": "Not enough paired participants."})
    else:
        out.append({"id": "S7", "criterion": "Comprehension signal (directional)", "status": "NOT_EVALUATED", "detail": "No comprehension data in this run."})
    return out


def words_summary(rows: list[dict], comparisons_list: list[list[str]]) -> dict:
    by_cond = defaultdict(lambda: defaultdict(list))
    case_words: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["_words"] is None:
            continue
        group = "should_apply" if r["_expectation"] == "should_apply" else "other"
        by_cond[r["condition"]][group].append(r["_words"])
        case_words[r["condition"]][r["case_id"]].append(r["_words"])
    medians = {c: {g: median(v) for g, v in groups.items()} for c, groups in by_cond.items()}
    expectation = {r["case_id"]: r["_expectation"] for r in rows}
    ratios = {}
    for x, y in comparisons_list:
        if x not in case_words or y not in case_words:
            continue
        per_group = defaultdict(list)
        for case_id in set(case_words[x]) & set(case_words[y]):
            denominator = statistics.fmean(case_words[y][case_id])
            if denominator > 0:
                group = "should_apply" if expectation[case_id] == "should_apply" else "other"
                per_group[group].append(statistics.fmean(case_words[x][case_id]) / denominator)
        ratios[f"{x} / {y}"] = {g: median(per_group.get(g, [])) for g in ("should_apply", "other")}
    return {"median_words": medians, "ratios": ratios}


def summarize(run_dir: Path, n_boot: int = 10000, seed: int = 0, min_cases: int = MIN_CASES,
              min_participants: int = MIN_PARTICIPANTS) -> tuple[dict, Issues]:
    issues = Issues()
    cases = es.load_cases()
    conditions = es.load_conditions()
    rows = load_run(run_dir, cases, conditions, issues)
    _, ratings = load_ratings(run_dir, rows, cases, issues) if rows else ({}, [])
    responses = response_level(ratings)
    present = {r["condition"] for r in rows}
    comparison_pairs = [p for p in conditions["comparisons"] if p[0] in present and p[1] in present]

    activation = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for r in rows:
        if r["condition"] in C_CONDITIONS or r["batch"].startswith("variant:"):
            activation[r["condition"]][r["_expectation"]][r["_activation"] or "missing"] += 1

    dims_by_condition = {}
    for condition in sorted(present):
        group = [e for e in responses.values() if e["row"]["condition"] == condition]
        dims_by_condition[condition] = {"n_responses": len(group)}
        for dim in es.DIMENSIONS:
            dims_by_condition[condition][dim] = mean([e[dim] for e in group if e[dim] is not None])

    per_protocol = {}
    activated = [e for e in responses.values() if e["row"]["condition"] == "C_skill" and e["row"]["_activation"] == "yes"]
    if activated:
        per_protocol = {"n_responses": len(activated),
                        **{d: mean([e[d] for e in activated if e[d] is not None]) for d in es.DIMENSIONS}}

    comparisons, rank_levels = {}, {}
    ranks = rank_case_level(ratings)
    eligible_cases = {cid for cid, c in cases.items() if c["skill_expectation"] == "should_apply"}
    for x, y in comparison_pairs:
        label = f"{x} vs {y}"
        comparisons[label] = {}
        for i, dim in enumerate(es.DIMENSIONS):
            levels = case_level(responses, dim)
            comparisons[label][dim] = paired_summary(levels.get(x, {}), levels.get(y, {}), n_boot, seed + i)
        rx = {k: v for k, v in ranks.get(x, {}).items() if k in eligible_cases}
        ry = {k: v for k, v in ranks.get(y, {}).items() if k in eligible_cases}
        stats = paired_summary({k: -v for k, v in rx.items()}, {k: -v for k, v in ry.items()}, 0, seed)
        rank_levels[label] = {"n": stats["n"], "wins": stats["wins"], "ties": stats["ties"], "losses": stats["losses"]}

    adherence = {}
    for condition in sorted(present):
        group = [e for e in responses.values() if e["row"]["condition"] == condition]
        if group:
            adherence[condition] = {code: sum(code in e["adherence_any"] for e in group) / len(group)
                                    for code in sorted(es.ADHERENCE_CODES)}
    accuracy = {}
    for condition in sorted(present):
        group = [e for e in responses.values() if e["row"]["condition"] == condition]
        if group:
            accuracy[condition] = {
                "responses": len(group),
                "responses_with_critical_error": sum(e["critical_flag"] for e in group),
                "mean_critical_errors": mean([e["critical_errors_mean"] for e in group if e["critical_errors_mean"] is not None]),
            }
    mean_rank = {}
    for condition in sorted(present):
        values = [r["rank"] for r in ratings if r["row"]["condition"] == condition and r["rank"] is not None]
        mean_rank[condition] = mean(values)

    words = words_summary(rows, comparison_pairs + [["C_skill_explicit", "A_normal"]])
    comprehension = load_comprehension(run_dir, conditions, n_boot, seed, issues)
    summary = {
        "run_dir": str(run_dir),
        "rows": len(rows),
        "responses_present": sum(r["_has_response"] for r in rows),
        "ratings": len(ratings),
        "raters": sorted({r["rater"] for r in ratings}),
        "recognized_condition_flags": sum(r["recognized"] for r in ratings),
        "activation": {c: {e: dict(v) for e, v in d.items()} for c, d in activation.items()},
        "dimension_means": dims_by_condition,
        "per_protocol_C_skill_activated_only": per_protocol,
        "comparisons": comparisons,
        "rank_wins_should_apply": rank_levels,
        "mean_rank": mean_rank,
        "adherence_rates": adherence,
        "accuracy": accuracy,
        "words": words,
        "agreement": agreement(ratings),
        "comprehension": comprehension,
        "criteria": criteria(rows, responses, rank_levels, comparisons, words, comprehension,
                             min_cases, min_participants),
        "issues": {"errors": issues.errors, "warnings": issues.warnings},
    }
    return summary, issues


def render_markdown(s: dict) -> str:
    L = ["# Evaluation summary", "",
         f"Run: `{s['run_dir']}`. Rows: {s['rows']}; responses present: {s['responses_present']}; "
         f"rating rows: {s['ratings']}; raters: {', '.join(s['raters']) or 'none'}.", "",
         "Pilot-scale descriptive statistics. Intervals are 95% bootstrap percentile intervals over cases "
         "(or participants). Rater scores are judgements of explanation quality, not measurements of "
         "comprehension. Success criteria are engineering targets, not validated thresholds.", ""]
    L += ["## Success criteria (engineering targets)", "", "| ID | Criterion | Status | Detail |", "|---|---|---|---|"]
    L += [f"| {c['id']} | {c['criterion']} | {c['status']} | {c['detail']} |" for c in s["criteria"]]
    L += ["", "## Data issues", ""]
    issues = s["issues"]
    if not issues["errors"] and not issues["warnings"]:
        L.append("None.")
    L += [f"- ERROR: {e}" for e in issues["errors"][:200]]
    L += [f"- warning: {w}" for w in issues["warnings"][:200]]
    if len(issues["errors"]) > 200 or len(issues["warnings"]) > 200:
        L.append("- (truncated; see summary.json)")
    L += ["", "## Activation (skill conditions)", "", "| Condition | Expectation | yes | no | unclear | missing |", "|---|---|---:|---:|---:|---:|"]
    for condition, by_exp in sorted(s["activation"].items()):
        for exp, counts in sorted(by_exp.items()):
            L.append(f"| {condition} | {exp} | {counts.get('yes', 0)} | {counts.get('no', 0)} | {counts.get('unclear', 0)} | {counts.get('missing', 0)} |")
    L += ["", "## Dimension means by condition", ""]
    if s["dimension_means"]:
        conds = sorted(s["dimension_means"])
        L += ["| Dimension | " + " | ".join(conds) + " |", "|---|" + "---:|" * len(conds)]
        L.append("| responses rated | " + " | ".join(str(s["dimension_means"][c]["n_responses"]) for c in conds) + " |")
        for dim in es.DIMENSIONS:
            L.append(f"| {dim} | " + " | ".join(fmt(s["dimension_means"][c][dim]) for c in conds) + " |")
    if s["per_protocol_C_skill_activated_only"]:
        pp = s["per_protocol_C_skill_activated_only"]
        L += ["", f"Per-protocol C_skill (activation observed, n={pp['n_responses']}; biased subset): "
              + ", ".join(f"{d} {fmt(pp[d])}" for d in es.PRIMARY_DIMENSIONS)]
    L += ["", "## Paired comparisons (by case)", ""]
    for label, dims in s["comparisons"].items():
        rank = s["rank_wins_should_apply"].get(label, {})
        L += [f"### {label}", "", "| Dimension | n | mean diff | 95% CI | W/T/L |", "|---|---:|---:|---|---|"]
        for dim, st in dims.items():
            L.append(f"| {dim} | {st['n']} | {fmt(st['mean_diff'])} | {fmt_ci(st['ci95'])} | {st['wins']}/{st['ties']}/{st['losses']} |")
        if rank:
            L.append(f"| rank (should_apply) | {rank['n']} | | | {rank['wins']}/{rank['ties']}/{rank['losses']} |")
        L.append("")
    L += ["## Accuracy", "", "| Condition | responses | with critical error | mean critical errors |", "|---|---:|---:|---:|"]
    for c, a in s["accuracy"].items():
        L.append(f"| {c} | {a['responses']} | {a['responses_with_critical_error']} | {fmt(a['mean_critical_errors'])} |")
    L += ["", "## Adherence violations (share of responses flagged by at least one rater)", ""]
    if s["adherence_rates"]:
        conds = sorted(s["adherence_rates"])
        L += ["| Code | " + " | ".join(conds) + " |", "|---|" + "---:|" * len(conds)]
        for code in sorted(es.ADHERENCE_CODES):
            L.append(f"| {code} | " + " | ".join(f"{s['adherence_rates'][c][code]:.0%}" for c in conds) + " |")
    L += ["", "## Length", "", "| Condition | median words (should_apply) | median words (other) |", "|---|---:|---:|"]
    for c, m in sorted(s["words"]["median_words"].items()):
        L.append(f"| {c} | {fmt(m.get('should_apply'), 0)} | {fmt(m.get('other'), 0)} |")
    L += ["", "| Ratio | median (should_apply) | median (other) |", "|---|---:|---:|"]
    for label, r in s["words"]["ratios"].items():
        L.append(f"| {label} | {fmt(r.get('should_apply'))} | {fmt(r.get('other'))} |")
    L += ["", "## Mean within-case rank (1 = best)", ""]
    L += [f"- {c}: {fmt(v)}" for c, v in s["mean_rank"].items()]
    L += ["", "## Inter-rater agreement", "", "| Dimension | pairs | exact | within 1 | mean abs diff |", "|---|---:|---:|---:|---:|"]
    for dim, a in s["agreement"].items():
        L.append(f"| {dim} | {a['pairs']} | {fmt(a['exact'])} | {fmt(a['within_one'])} | {fmt(a['mean_abs_diff'])} |")
    L.append(f"\nResponses where a rater suspected the condition: {s['recognized_condition_flags']}.")
    comp = s["comprehension"]
    L += ["", "## Human comprehension", ""]
    if not comp:
        L.append("No comprehension data in this run.")
    else:
        L += [f"Participants: {comp['participants']}; participant-topics analysed: {comp['participant_topics_analysed']}; "
              f"excluded for attention: {comp['excluded_attention']}; ceiling (excluded from gain only): {comp['ceiling_excluded_from_gain']}; "
              f"explain-item grader exact agreement: {fmt(comp['explain_grader_exact_agreement'])} over {comp['explain_grader_pairs']} pairs.", ""]
        L += ["| Condition | n | pre | post MC | transfer+misconception | explain | gain | clarity | confidence |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for c, m in comp["by_condition"].items():
            L.append(f"| {c} | {m['n']} | {fmt(m['pre'])} | {fmt(m['post_mc'])} | {fmt(m['transfer_misconception'])} | {fmt(m['explain'])} | {fmt(m['gain'])} | {fmt(m['clarity'])} | {fmt(m['confidence'])} |")
        L += ["", "| Contrast | outcome | n | mean diff | 95% CI | +/0/- |", "|---|---|---:|---:|---|---|"]
        for label, outcomes in comp["contrasts"].items():
            for outcome, st in outcomes.items():
                L.append(f"| {label} | {outcome} | {st['n']} | {fmt(st['mean_diff'])} | {fmt_ci(st['ci95'])} | {st['wins']}/{st['ties']}/{st['losses']} |")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and summarize an evaluation run.")
    parser.add_argument("run_dir")
    parser.add_argument("--check-only", action="store_true", help="report data problems without writing a summary")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--min-cases", type=int, default=MIN_CASES,
                        help="below this many cases a criterion reports INSUFFICIENT_DATA instead of MET/NOT_MET")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    summary, issues = summarize(run_dir, args.bootstrap, args.seed, min_cases=args.min_cases)
    for message in issues.errors:
        print(f"ERROR   {message}")
    for message in issues.warnings:
        print(f"WARNING {message}")
    if args.check_only:
        print(f"{'OK' if not issues.errors else 'PROBLEMS FOUND'}: {len(issues.errors)} error(s), {len(issues.warnings)} warning(s)")
        return 1 if issues.errors else 0
    if not run_dir.is_dir():
        return 1
    (run_dir / "summary.json").write_bytes((json.dumps(summary, indent=2, default=list) + "\n").encode("utf-8"))
    (run_dir / "summary.md").write_bytes(render_markdown(summary).encode("utf-8"))
    print(f"Wrote {run_dir / 'summary.md'} and summary.json ({len(issues.errors)} data error(s) listed inside)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
