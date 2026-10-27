"""Acceptance test for the automated judge: Claude-vs-Claude only, plus a floor test.

    python scripts/judge_acceptance.py                                     # research/judge_acceptance/<backend>-<model>.{md,json}
    python scripts/judge_acceptance.py --run evaluation/runs/<id> --pair V_full,C_skill_explicit

The judge is a regression guard for changes to Claude's explanations, so it is accepted only if
it can tell two Claude answers apart reliably and rejects answers that are worse by construction.

Consistency pairs: the archive's Claude answers to the same question under different prompt
styles (base vs tutor, base vs pedagogical, tutor vs pedagogical; 5 topics each), plus any
same-case, same-sample pairs from a collected run (--run/--pair, e.g. V0 vs V1). Every pair is
judged in both presentation orders; the order-flip rate measures consistency.

Floor test: each Claude base answer against three deterministic degradations of itself:
  truncated      the first ~40% of its words, cut at a sentence boundary
  fact_removed   every statement of one checklist fact removed, recurrences included (hand-listed
                 exact edits in FACT_REMOVALS, all 5 topics)
  buried         the opening (answer) paragraph moved to the end
  formatted_emptier
                 the fact_removed text with headings, bullets and bold added: it looks more
                 organised and contains less. This is the failure presentation changes risk.
A consistent judge can still be useless, so the floor is required whatever the flip rate:
  - pairwise: the original wins in both orders on >= FLOOR_MIN_SHARE of the truncated,
    fact_removed and buried pairs;
  - presentation: the original wins in both orders on >= FLOOR_MIN_SHARE of formatted_emptier
    pairs, and the formatted-and-emptier version is never preferred consistently;
  - fact capture: fact_removed, formatted_emptier, and truncations hand-checked to drop a fact
    (TRUNCATION_LOSES_FACTS), capture fewer facts than the original in >= FLOOR_MIN_SHARE of
    cases and never more; buried (all facts kept) captures the same number in >= FLOOR_MIN_SHARE
    of cases.
All thresholds were fixed before any data was seen. Fact capture and preference are reported
separately and never combined.

The archive's GPT answers are not used: Claude-vs-GPT is out of the evaluation. The archive is
read-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402
import judge as jd  # noqa: E402
import judgelib as jl  # noqa: E402
import structural_metrics as sm  # noqa: E402

ARCHIVE_INPUT = es.REPO_ROOT / "research-results-2026-10-26" / "inputs" / "input-dataset.json"
OUT_DIR = es.REPO_ROOT / "research"
CACHE_DIR = OUT_DIR / "judge_acceptance_cache"
STYLE_PAIRS = (("base", "tutor"), ("base", "pedagogical"), ("tutor", "pedagogical"))
DEGRADATIONS = ("truncated", "fact_removed", "buried", "formatted_emptier")
MAX_FLIP_RATE = 0.20
FLOOR_MIN_SHARE = 0.80
TRUNCATE_SHARE = 0.40
# Hand-chosen from the archive's Claude base answers: one checklist fact per topic, and an exact
# (old, new) edit for every place that states or directly implies it, including recurrences in
# summary tables and closing paragraphs. Each `old` must occur exactly once.
FACT_REMOVALS: dict[str, tuple[str, tuple[tuple[str, str], ...]]] = {
    "caching": ("caching_f3", (
        ("Crash recovery is easier because memory holds the latest data.", ""),
        ("A crash or power loss can lose data that was only in the cache.", ""),
        ("Data-loss risk on crash\tLow\tHigher\n", ""),
        (", embedded systems, and storage or database layers that need durability guarantees.",
         ", and embedded systems."),
        (", while “write-through” modes are offered when you can’t afford to lose recent writes.", "."),
    )),
    "databases": ("databases_f4", (
        ("Storage space.", ""),
        ("An index stores a copy of the indexed columns plus pointers.", ""),
        ("Wide or numerous indexes can rival or exceed the size of the table itself, and they compete with "
         "table data for buffer cache memory.", ""),
        ("indexes trade write speed and space for read speed", "indexes trade write speed for read speed"),
    )),
    "immunology": ("immunology_f3", (
        ("Memory.", ""),
        ("This is the key payoff.", ""),
        ("After the response winds down, long-lived memory B and T cells remain, sometimes for decades.", ""),
        ("They are the “trained” part of the system.", ""),
        ("Memory cells recognize it right away.", ""),
        ("Because of this, some vaccines need boosters: for some pathogens, memory fades over time, or the "
         "pathogen mutates (as with flu and COVID-19), so the immune system needs a refresher or an update.", ""),
    )),
    "interest": ("interest_f1", (
        ("Simple interest is calculated only on your original amount (the principal).", ""),
        ("Simple interest: you earn $50 every year, always 5% of the original $1,000.", ""),
        ("After 10 years: $1,000 + $500 = $1,500.", ""),
        ("Simple: A = P(1 + rt)\n", ""),
        ("Simple interest grows by the same fixed amount each period, which is a straight line.", ""),
    )),
    "tcp": ("tcp_f3", (
        ("ACK (client → server): The client sends a segment with ACK set and acknowledgment number y+1. This says: "
         "“I got yours too.” The connection is now established, and data can flow in both directions (the third "
         "segment can already carry data).", ""),
        ("That’s four pieces of information: two SYNs and two ACKs. The server combines its ACK of the client’s "
         "SYN with its own SYN into one segment, which is why four messages collapse into three.", ""),
        ("Step 3 proves to the server that the client can actually receive its packets, so the return path "
         "works. Without it, the server could not be sure its SYN-ACK arrived, and each side would not have "
         "confirmation that the other has agreed on its numbers.", ""),
        ("With three steps, the client’s final ACK must carry y+1; if the client didn’t send the original SYN, "
         "it responds to the SYN-ACK with a reset (RST), and the server drops the half-open connection.", ""),
        ("Defenses like SYN cookies avoid allocating state until the final ACK arrives.", ""),
    )),
}
# Hand-checked: in these topics the truncated text drops at least one checklist fact. TCP's truncation
# keeps its opening purpose statement and all three steps, so it is excluded from the fact gate (it
# stays in the pairwise floor).
TRUNCATION_LOSES_FACTS = frozenset({"caching", "databases", "immunology", "interest"})


# ---------------------------------------------------------------------------
# Archive and degradations (pure)
# ---------------------------------------------------------------------------

def load_archive(path: Path = ARCHIVE_INPUT) -> tuple[dict, list[dict]]:
    """Cases keyed by question id, and the Claude answers only."""
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = {}
    for q in data["questions"]:
        cases[q["id"]] = {"question": q["text"], "context": None, "audience": None, "common_misconceptions": [],
                          "critical_facts": [{"id": f"{q['topic']}_f{i}", "fact": f}
                                             for i, f in enumerate(q["factual_checklist"], start=1)],
                          "topic": q["topic"]}
    responses = []
    for a in data["imported_answers"]:
        if a["provider"] != "anthropic":
            continue
        style = a["label"].split(" - ", 1)[1].strip().lower()
        topic = cases[a["question_id"]]["topic"]
        responses.append({"row_id": f"{topic}__{style}", "case_id": a["question_id"], "condition": style,
                          "sample_index": "1", "style": style, "text": a["text"].strip()})
    return cases, responses


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def split_sentences(paragraph: str) -> list[str]:
    return [s for s in sm.SENTENCE_SPLIT_RE.split(paragraph) if s.strip()]


def truncate(text: str, share: float = TRUNCATE_SHARE) -> str:
    limit = max(1, int(len(sm.words(text)) * share))
    kept, count = [], 0
    for para in paragraphs(text):
        sentences_kept = []
        for sentence in split_sentences(para):
            if count >= limit:
                break
            sentences_kept.append(sentence)
            count += len(sm.words(sentence))
        if sentences_kept:
            kept.append(" ".join(sentences_kept))
        if count >= limit:
            break
    return "\n\n".join(kept)


def remove_fact(text: str, topic: str) -> tuple[str, str | None]:
    """Apply the hand-listed edits that remove every statement of this topic's chosen fact."""
    if topic not in FACT_REMOVALS:
        return text, None
    fact_id, edits = FACT_REMOVALS[topic]
    missing = [old[:50] for old, _ in edits if text.count(old) != 1]
    if missing:
        raise ValueError(f"{topic}: removal list does not match the answer exactly once: {missing}")
    for old, new in edits:
        text = text.replace(old, new)
    text = re.sub(r"(?m)^ +| +$", "", re.sub(r" {2,}", " ", text))
    return re.sub(r"\n{3,}", "\n\n", text).strip(), fact_id


def is_title(paragraph: str) -> bool:
    return "\n" not in paragraph and len(sm.words(paragraph)) <= 8 and not paragraph.endswith(".")


def prettify(text: str) -> str:
    """Headings, bullets and bold on the same content: the look of organisation, nothing added."""
    blocks = ["## Overview"]
    for i, para in enumerate(paragraphs(text)):
        if is_title(para):
            blocks.append("## " + para.rstrip(":"))
        elif "\t" in para:
            blocks.append(para)
        elif i == 0:
            blocks.append(f"**{para}**")
        else:
            items = [s.strip() for line in para.split("\n") for s in split_sentences(line) if s.strip()]
            blocks.append("\n".join(f"- **{s}**" if j == 0 else f"- {s}" for j, s in enumerate(items)))
    return "\n\n".join(blocks)


def bury(text: str) -> str:
    parts = paragraphs(text)
    return "\n\n".join(parts[1:] + parts[:1]) if len(parts) > 1 else text


def degraded_versions(original: dict, case: dict) -> list[dict]:
    removed_text, removed_id = remove_fact(original["text"], case["topic"])
    versions = {"truncated": (truncate(original["text"]), None), "fact_removed": (removed_text, removed_id),
                "buried": (bury(original["text"]), None),
                "formatted_emptier": (prettify(removed_text), removed_id)}
    out = []
    for kind in DEGRADATIONS:
        text, fact_id = versions[kind]
        if kind in {"fact_removed", "formatted_emptier"} and fact_id is None:
            continue
        out.append({**original, "row_id": f"{original['row_id']}__{kind}", "condition": f"base_{kind}",
                    "degradation": kind, "removed_fact": fact_id, "text": text})
    return out


# ---------------------------------------------------------------------------
# Verdicts (pure)
# ---------------------------------------------------------------------------

def floor_verdicts(floor_rows: list[dict], fact_by_row: dict[str, int], pairs_meta: list[dict]) -> dict:
    pairwise_ok = [r["winner"] == "x" for r, m in zip(floor_rows, pairs_meta) if m["degradation"] != "formatted_emptier"]
    pretty = [r["winner"] for r, m in zip(floor_rows, pairs_meta) if m["degradation"] == "formatted_emptier"]
    by_kind: dict[str, list[tuple[int, int]]] = defaultdict(list)
    must_drop: list[tuple[int, int]] = []
    for meta in pairs_meta:
        counts = (fact_by_row[meta["original"]], fact_by_row[meta["degraded"]])
        by_kind[meta["degradation"]].append(counts)
        if meta["degradation"] in {"fact_removed", "formatted_emptier"} or (
                meta["degradation"] == "truncated" and meta["topic"] in TRUNCATION_LOSES_FACTS):
            must_drop.append(counts)
    lower = [d < o for o, d in must_drop]
    higher = [d > o for o, d in must_drop]
    same = [d == o for o, d in by_kind.get("buried", [])]
    share = lambda xs: sum(xs) / len(xs) if xs else None  # noqa: E731
    result = {
        "pairwise_original_wins_share": share(pairwise_ok),
        "formatted_emptier_original_wins_share": share([w == "x" for w in pretty]),
        "formatted_emptier_preferred_count": sum(w == "y" for w in pretty),
        "fact_lower_share": share(lower),
        "fact_higher_count": sum(higher),
        "buried_fact_same_share": share(same),
        "fact_counts": {k: [{"original": o, "degraded": d} for o, d in v] for k, v in by_kind.items()},
    }
    result["pairwise_floor_passed"] = result["pairwise_original_wins_share"] is not None and \
        result["pairwise_original_wins_share"] >= FLOOR_MIN_SHARE
    result["presentation_floor_passed"] = (result["formatted_emptier_original_wins_share"] is not None
                                           and result["formatted_emptier_original_wins_share"] >= FLOOR_MIN_SHARE
                                           and result["formatted_emptier_preferred_count"] == 0)
    result["fact_floor_passed"] = (result["fact_lower_share"] is not None and result["fact_lower_share"] >= FLOOR_MIN_SHARE
                                   and result["fact_higher_count"] == 0
                                   and result["buried_fact_same_share"] is not None
                                   and result["buried_fact_same_share"] >= FLOOR_MIN_SHARE)
    return result


def strata(rows: list[dict]) -> dict:
    out = {}
    for label in sorted({r["comparison"] for r in rows}):
        group = [r for r in rows if r["comparison"] == label]
        consistent = [r for r in group if r["consistent"] == "yes"]
        out[label] = {"pairs": len(group), "flips": len(group) - len(consistent),
                      "x_wins": sum(r["winner"] == "x" for r in consistent),
                      "y_wins": sum(r["winner"] == "y" for r in consistent)}
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run_pairs(run_dir: Path, x: str, y: str) -> tuple[dict, list]:
    cases = es.load_cases()
    responses = [r for r in jd.load_responses(run_dir) if r["condition"] in {x, y}]
    return cases, jd.build_pairs(responses, [[x, y]])


def acceptance(backend: jl.Backend, cache_dir: Path = CACHE_DIR, seed: int = 0,
               extra: tuple[dict, list] | None = None) -> dict:
    cases, responses = load_archive()
    judge = jl.CachedJudge(backend, cache_dir, progress=True)
    index = {(r["case_id"], r["style"]): r for r in responses}
    consistency = [(f"claude-{a} vs claude-{b}", index[(cid, a)], index[(cid, b)])
                   for a, b in STYLE_PAIRS for cid in sorted(cases) if (cid, a) in index and (cid, b) in index]
    floor, floor_meta, degraded = [], [], []
    for cid in sorted(cases):
        original = index.get((cid, "base"))
        if not original:
            continue
        for version in degraded_versions(original, cases[cid]):
            degraded.append(version)
            floor.append((f"floor: original vs {version['degradation']}", original, version))
            floor_meta.append({"original": original["row_id"], "degraded": version["row_id"],
                               "topic": cases[cid]["topic"], "degradation": version["degradation"],
                               "removed_fact": version["removed_fact"]})
    consistency_rows = jd.run_pairwise(judge, consistency, cases, "pairwise", jd.OVERALL_QUESTION, seed)
    floor_rows = jd.run_pairwise(judge, floor, cases, "pairwise", jd.OVERALL_QUESTION, seed + 1)
    run_rows: list[dict] = []
    if extra:
        run_cases, run_pair_list = extra
        run_rows = jd.run_pairwise(judge, run_pair_list, run_cases, "pairwise", jd.OVERALL_QUESTION, seed + 2)
    for rows, pair_list in ((consistency_rows, consistency), (floor_rows, floor)):
        for row, (_, rx, _) in zip(rows, pair_list):
            row["topic"] = cases[rx["case_id"]]["topic"]
    originals = [index[(cid, "base")] for cid in sorted(cases) if (cid, "base") in index]
    fact_rows = jd.run_facts(judge, originals + degraded, cases)
    fact_by_row = {r["row_id"]: r["n_stated"] for r in fact_rows}
    all_pairs = consistency_rows + floor_rows + run_rows
    flips = sum(r["consistent"] == "no" for r in all_pairs)
    flip_rate = flips / len(all_pairs) if all_pairs else None
    floor_result = floor_verdicts(floor_rows, fact_by_row, floor_meta)
    flip_ok = flip_rate is not None and flip_rate <= MAX_FLIP_RATE
    return {
        "notice": es.JUDGE_NOTICE,
        "backend": backend.name, "model": backend.model,
        "thresholds": {"max_flip_rate": MAX_FLIP_RATE, "floor_min_share": FLOOR_MIN_SHARE},
        "pairs": len(all_pairs), "order_flips": flips, "flip_rate": flip_rate, "flip_rate_passed": flip_ok,
        "floor": floor_result,
        "accepted": (flip_ok and floor_result["pairwise_floor_passed"] and floor_result["presentation_floor_passed"]
                     and floor_result["fact_floor_passed"]),
        "strata": strata(all_pairs),
        "floor_pairs": floor_meta,
        "pair_rows": all_pairs,
        "fact_rows": fact_rows,
        "judge_calls": judge.calls, "cache_hits": judge.hits,
    }


def fmt(value) -> str:
    return "–" if value is None else (f"{value:.2f}" if isinstance(value, float) else str(value))


def render(result: dict) -> str:
    f = result["floor"]
    verdict = "ACCEPTED" if result["accepted"] else "REJECTED"
    L = ["# Judge acceptance test (Claude vs Claude, with floor test)", "", es.JUDGE_NOTICE, "",
         "Inputs: the archive's Claude answers (`research-results-2026-10-26/inputs/input-dataset.json`, "
         "read-only) and deterministic degradations of them. GPT answers are not used.", "",
         f"Judge: `{result['backend']}` / `{result['model']}`. Thresholds fixed before any data: flip rate <= "
         f"{result['thresholds']['max_flip_rate']:.2f}; floor shares >= {result['thresholds']['floor_min_share']:.2f}.", "",
         f"## Verdict: **{verdict}**", "",
         "| Gate | Result | Passed |", "|---|---|---|",
         f"| Order-flip rate (consistency) | {result['order_flips']}/{result['pairs']} = {fmt(result['flip_rate'])} | "
         f"{'yes' if result['flip_rate_passed'] else 'no'} |",
         f"| Pairwise floor: original preferred in both orders | {fmt(f['pairwise_original_wins_share'])} | "
         f"{'yes' if f['pairwise_floor_passed'] else 'no'} |",
         f"| Presentation floor: original beats formatted-and-emptier | "
         f"{fmt(f['formatted_emptier_original_wins_share'])}; prettier version preferred "
         f"{f['formatted_emptier_preferred_count']} time(s) | {'yes' if f['presentation_floor_passed'] else 'no'} |",
         f"| Fact floor: truncated/fact-removed capture fewer facts | {fmt(f['fact_lower_share'])} (more in "
         f"{f['fact_higher_count']}); buried unchanged {fmt(f['buried_fact_same_share'])} | "
         f"{'yes' if f['fact_floor_passed'] else 'no'} |", "",
         "## Preference strata (x vs y)", "", "| Stratum | pairs | flips | x wins | y wins |",
         "|---|---:|---:|---:|---:|"]
    L += [f"| {k} | {v['pairs']} | {v['flips']} | {v['x_wins']} | {v['y_wins']} |" for k, v in result["strata"].items()]
    L += ["", "## Fact capture on the floor set (separate instrument)", "",
          "| Degradation | original facts → degraded facts |", "|---|---|"]
    L += [f"| {k} | " + ", ".join(f"{c['original']}→{c['degraded']}" for c in v) + " |"
          for k, v in f["fact_counts"].items()]
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Judge acceptance test (Claude vs Claude, with floor test).")
    parser.add_argument("--min-interval", type=float, default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--run", default=None, help="collected run to add same-case pairs from")
    parser.add_argument("--pair", default=None, help="two conditions in that run, e.g. V_full,C_skill_explicit")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(line_buffering=True)
    extra = None
    if args.run:
        if not args.pair or len(args.pair.split(",")) != 2:
            parser.error("--run needs --pair X,Y")
        extra = run_pairs(Path(args.run), *args.pair.split(","))
    try:
        kwargs = {"min_interval": args.min_interval} if args.min_interval is not None else {}
        result = acceptance(jl.backend_from_env(**kwargs), seed=args.seed, extra=extra)
    except jl.JudgeUnavailable as exc:
        print(f"judge_acceptance: {exc}. Progress is cached; rerun to resume.", file=sys.stderr)
        return 2
    except jl.JudgeError as exc:
        print(f"judge_acceptance: {exc}", file=sys.stderr)
        return 1
    out = OUT_DIR / "judge_acceptance" / re.sub(r"[^A-Za-z0-9.\-]+", "_", f"{result['backend']}-{result['model']}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    out.with_suffix(".md").write_bytes(render(result).encode("utf-8"))
    print(f"Wrote {out.with_suffix('.md').relative_to(es.REPO_ROOT).as_posix()}")
    print(render(result).split("## Preference strata")[0])
    print(f"judge calls {result['judge_calls']}, cached {result['cache_hits']}")
    return 0 if result["accepted"] else 3


if __name__ == "__main__":
    sys.exit(main())
