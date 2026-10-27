"""Automated screening judge over a collected run (Track A0.3).

    python scripts/judge.py evaluation/runs/<run_id>                    # facts + pairwise + dimensions
    python scripts/judge.py evaluation/runs/<run_id> --tasks facts      # one task only
    python scripts/judge.py evaluation/runs/<run_id> --calibration      # emit the hand-scoring calibration set

Three tasks, in decreasing order of trust:
  facts      which of the case's critical_facts the response states, and which
             common_misconceptions it asserts (comprehension-class; the primary signal)
  pairwise   forced-choice overall preference between two conditions' responses
  dimension  forced-choice on navigability and register_fit only

Every pair is judged in both presentation orders. A pair whose verdict flips with the order is
discarded, and the flip rate is reported as the judge's own reliability estimate. Responses
are stripped of anything naming the skill before the judge sees them.

Fact capture and preference are reported in separate tables and never combined. The judge is
a screening instrument, not the human evaluation, and never feeds S1-S7.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402
import judgelib as jl  # noqa: E402

TASKS = ("facts", "pairwise", "dimension")
JUDGED_DIMENSIONS = {
    "navigability": (
        "Which answer lets this reader find the part they need without reading it from start to finish? "
        "Prefer the answer whose form shows the shape of its content (stages, comparisons, distinct parts). "
        "Do not reward structure that is decorative: headings over one-sentence sections, bullets that "
        "break up a single argument, or emphasis on everything."),
    "register_fit": (
        "Which answer pitches its technical level to this particular reader? Prefer the answer that uses "
        "the field's correct terms at the reader's own level, explains terms the reader would not know, "
        "and neither invents jargon, name-drops without explanation, nor talks down to the reader."),
}
OVERALL_QUESTION = (
    "Which answer would leave this reader with a more accurate and usable understanding of what they "
    "actually asked? Judge substance and fit to the question, not length.")
SKILL_MENTION_RE = re.compile(r"(?i)explanation[\s_-]*lab(?:\s+skill)?|socialized(?:-claude)?(?:\s+skill)?")
CALIBRATION_SIZE = 20


def blind(text: str) -> str:
    return SKILL_MENTION_RE.sub("[redacted]", text)


def misconception_ids(case: dict) -> dict[str, str]:
    return {f"m{i}": text for i, text in enumerate(case.get("common_misconceptions", []), start=1)}


def request_text(case: dict) -> str:
    if case.get("turns"):
        earlier = "\n".join(f"- Turn {n}: {t.strip()}" for n, t in enumerate(case["turns"][:-1], start=1))
        return (f"Earlier user turns in this conversation (the assistant answered each one live):\n{earlier}\n"
                f"Final user turn, which the answer below replies to: {case['turns'][-1].strip()}")
    context = f"Earlier context: {case['context']}\n" if case.get("context") else ""
    return f"{context}Question: {case['question']}"


# ---------------------------------------------------------------------------
# Prompts and parsing (pure)
# ---------------------------------------------------------------------------

def facts_prompt(case: dict, response: str) -> str:
    facts = "\n".join(f"- {f['id']}: {f['fact']}" for f in case["critical_facts"])
    misconceptions = "\n".join(f"- {k}: {v}" for k, v in misconception_ids(case).items()) or "- (none)"
    return (
        "You are checking an answer against a fixed list of facts and misconceptions. You are not rating "
        "its quality.\n\n"
        f"{request_text(case)}\n\n"
        f"ANSWER:\n<<<\n{blind(response)}\n>>>\n\n"
        f"FACTS:\n{facts}\n\nMISCONCEPTIONS:\n{misconceptions}\n\n"
        "For each fact, decide whether the answer states it, in any wording. A fact counts only if the "
        "answer actually says it, not if it is merely compatible with the answer. For each misconception, "
        "decide whether the answer asserts it as true; mentioning it in order to correct it does not count.\n"
        'Reply with JSON only: {"facts_stated": ["<fact id>", ...], "misconceptions_asserted": ["<id>", ...]}')


def pair_prompt(case: dict, first: str, second: str, question: str) -> str:
    return (
        "Two answers to the same request are shown. They are labelled 1 and 2 in random order.\n\n"
        f"Reader: {case.get('audience') or 'an intelligent adult'}\n{request_text(case)}\n\n"
        f"ANSWER 1:\n<<<\n{blind(first)}\n>>>\n\nANSWER 2:\n<<<\n{blind(second)}\n>>>\n\n"
        f"{question}\nYou must choose one. Reply with JSON only: {{\"winner\": 1}} or {{\"winner\": 2}}")


def parse_facts(text: str, case: dict) -> tuple[list[str], list[str]]:
    data = jl.parse_json_object(text)
    valid_f = {f["id"] for f in case["critical_facts"]}
    valid_m = set(misconception_ids(case))
    stated = sorted({str(i) for i in data.get("facts_stated", []) if str(i) in valid_f})
    asserted = sorted({str(i) for i in data.get("misconceptions_asserted", []) if str(i) in valid_m})
    return stated, asserted


def parse_winner(text: str) -> int:
    value = jl.parse_json_object(text).get("winner")
    if str(value) not in {"1", "2"}:
        raise jl.JudgeError(f"winner must be 1 or 2, got {value!r}")
    return int(value)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def load_responses(run_dir: Path) -> list[dict]:
    _, rows = es.read_csv(run_dir / "run_sheet.csv")
    out = []
    for row in rows:
        path = run_dir / row["response_file"]
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            out.append({**row, "text": path.read_text(encoding="utf-8").strip()})
    return out


def run_facts(judge: jl.CachedJudge, responses: list[dict], cases: dict) -> list[dict]:
    out = []
    for r in sorted(responses, key=lambda r: r["row_id"]):
        case = cases[r["case_id"]]
        if not case.get("critical_facts"):
            continue
        stated, asserted = parse_facts(judge.ask(facts_prompt(case, r["text"])), case)
        out.append({"row_id": r["row_id"], "case_id": r["case_id"], "condition": r["condition"],
                    "sample_index": r["sample_index"], "n_facts": len(case["critical_facts"]),
                    "facts_stated": ";".join(stated), "n_stated": len(stated),
                    "misconceptions_asserted": ";".join(asserted)})
    return out


def build_pairs(responses: list[dict], comparisons: list[list[str]]) -> list[tuple[str, dict, dict]]:
    index = {(r["condition"], r["case_id"], r["sample_index"]): r for r in responses}
    pairs = []
    for x, y in comparisons:
        for (cond, case_id, sample), rx in sorted(index.items()):
            if cond == x and (y, case_id, sample) in index:
                pairs.append((f"{x} vs {y}", rx, index[(y, case_id, sample)]))
    return pairs


def run_pairwise(judge: jl.CachedJudge, pairs: list, cases: dict, task: str, question: str,
                 seed: int) -> list[dict]:
    rng = random.Random(f"{seed}:{task}")
    out = []
    for label, rx, ry in pairs:
        case = cases[rx["case_id"]]
        x_first = rng.random() < 0.5
        orders = [(rx, ry), (ry, rx)] if x_first else [(ry, rx), (rx, ry)]
        verdicts = []
        for first, second in orders:
            winner = parse_winner(judge.ask(pair_prompt(case, first["text"], second["text"], question)))
            chosen = first if winner == 1 else second
            verdicts.append("x" if chosen is rx else "y")
        consistent = verdicts[0] == verdicts[1]
        out.append({"task": task, "comparison": label, "case_id": rx["case_id"], "sample_index": rx["sample_index"],
                    "x_row": rx["row_id"], "y_row": ry["row_id"], "first_shown": "x" if x_first else "y",
                    "verdict_order1": verdicts[0], "verdict_order2": verdicts[1],
                    "consistent": "yes" if consistent else "no", "winner": verdicts[0] if consistent else ""})
    return out


# ---------------------------------------------------------------------------
# Aggregation (pure)
# ---------------------------------------------------------------------------

def fact_tables(fact_rows: list[dict], comparisons: list[list[str]]) -> dict:
    by_condition: dict[str, list[dict]] = defaultdict(list)
    for r in fact_rows:
        by_condition[r["condition"]].append(r)
    conditions = {}
    for cond, group in sorted(by_condition.items()):
        conditions[cond] = {
            "responses": len(group),
            "mean_fact_capture": statistics.fmean(r["n_stated"] / r["n_facts"] for r in group),
            "responses_asserting_misconception": sum(bool(r["misconceptions_asserted"]) for r in group),
        }
    per_case: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in fact_rows:
        per_case[r["condition"]][r["case_id"]].append(r["n_stated"] / r["n_facts"])
    contrasts = {}
    for x, y in comparisons:
        shared = sorted(set(per_case.get(x, {})) & set(per_case.get(y, {})))
        if not shared:
            continue
        diffs = [statistics.fmean(per_case[x][c]) - statistics.fmean(per_case[y][c]) for c in shared]
        contrasts[f"{x} vs {y}"] = {"cases": len(diffs), "mean_diff": statistics.fmean(diffs),
                                    "wins": sum(d > 0 for d in diffs), "ties": sum(d == 0 for d in diffs),
                                    "losses": sum(d < 0 for d in diffs)}
    return {"by_condition": conditions, "contrasts": contrasts}


def pairwise_tables(pair_rows: list[dict]) -> dict:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in pair_rows:
        grouped[(r["task"], r["comparison"])].append(r)
    tables: dict[str, dict] = defaultdict(dict)
    for (task, label), group in sorted(grouped.items()):
        consistent = [r for r in group if r["consistent"] == "yes"]
        x_wins = sum(r["winner"] == "x" for r in consistent)
        tables[task][label] = {"pairs": len(group), "order_flips": len(group) - len(consistent),
                               "flip_rate": (len(group) - len(consistent)) / len(group),
                               "consistent": len(consistent), "x_wins": x_wins, "y_wins": len(consistent) - x_wins,
                               "x_win_share": x_wins / len(consistent) if consistent else None}
    flip = {}
    for task in sorted({r["task"] for r in pair_rows}):
        group = [r for r in pair_rows if r["task"] == task]
        flip[task] = sum(r["consistent"] == "no" for r in group) / len(group)
    return {"tables": dict(tables), "flip_rate_by_task": flip}


def fluency_checks(facts: dict, pairwise: dict) -> list[dict]:
    """Preference up while fact capture is flat or down: fluency bought instead of understanding."""
    out = []
    overall = pairwise["tables"].get("pairwise", {})
    for label, pref in sorted(overall.items()):
        fact = facts["contrasts"].get(label)
        if pref["x_win_share"] is None or fact is None:
            continue
        preferred = pref["x_win_share"] > 0.5
        out.append({"comparison": label, "x_win_share": pref["x_win_share"], "consistent_pairs": pref["consistent"],
                    "fact_capture_mean_diff": fact["mean_diff"], "cases": fact["cases"],
                    "flag": preferred and fact["mean_diff"] <= 0})
    return out


def fmt(value, digits: int = 2) -> str:
    return "–" if value is None else (f"{value:.{digits}f}" if isinstance(value, float) else str(value))


def render(summary: dict) -> str:
    L = ["# Automated judge summary", "", es.SURFACE_NOTICE, "", es.JUDGE_NOTICE, "",
         f"Judge: `{summary['backend']}` / `{summary['model']}`. Responses: {summary['responses']}.", ""]
    checks = summary["fluency_checks"]
    L += ["## Preference versus fact capture", "",
          "Read these two columns separately; they are different instruments and are never combined. "
          "A flagged row means the judge preferred the first condition while its fact capture was flat or lower.", "",
          "| Comparison | preferred share (x) | consistent pairs | fact-capture diff (x - y) | cases | flag |",
          "|---|---:|---:|---:|---:|---|"]
    L += [f"| {c['comparison']} | {fmt(c['x_win_share'])} | {c['consistent_pairs']} | {fmt(c['fact_capture_mean_diff'])} "
          f"| {c['cases']} | {'PREFERENCE UP, FACTS FLAT/DOWN' if c['flag'] else ''} |" for c in checks]
    if not checks:
        L.append("| (no comparison has both measures) | | | | | |")
    f = summary["facts"]
    L += ["", "## Fact capture (comprehension-class screening)", "",
          "| Condition | responses | mean fact capture | responses asserting a misconception |", "|---|---:|---:|---:|"]
    L += [f"| {c} | {v['responses']} | {fmt(v['mean_fact_capture'])} | {v['responses_asserting_misconception']} |"
          for c, v in f["by_condition"].items()]
    L += ["", "| Contrast | cases | mean diff | W/T/L |", "|---|---:|---:|---|"]
    L += [f"| {k} | {v['cases']} | {fmt(v['mean_diff'])} | {v['wins']}/{v['ties']}/{v['losses']} |"
          for k, v in f["contrasts"].items()]
    p = summary["pairwise"]
    L += ["", "## Judge reliability: order-flip rate", "",
          "Share of pairs whose verdict changed when the presentation order was reversed. Flipped pairs are discarded.", ""]
    L += [f"- {task}: {fmt(rate)}" for task, rate in p["flip_rate_by_task"].items()] or ["- no pairs judged"]
    for task, tables in p["tables"].items():
        title = "Overall preference" if task == "pairwise" else f"Dimension: {task}"
        L += ["", f"## {title} (preference-class)", "",
              "| Comparison | pairs | flips | flip rate | consistent | x wins | y wins | x share |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
        L += [f"| {k} | {v['pairs']} | {v['order_flips']} | {fmt(v['flip_rate'])} | {v['consistent']} | {v['x_wins']} "
              f"| {v['y_wins']} | {fmt(v['x_win_share'])} |" for k, v in tables.items()]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Calibration set
# ---------------------------------------------------------------------------

def calibration_sample(responses: list[dict], size: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    by_condition: dict[str, list[dict]] = defaultdict(list)
    for r in sorted(responses, key=lambda r: r["row_id"]):
        by_condition[r["condition"]].append(r)
    for group in by_condition.values():
        rng.shuffle(group)
    chosen = []
    while len(chosen) < size and any(by_condition.values()):
        for cond in sorted(by_condition):
            if by_condition[cond] and len(chosen) < size:
                chosen.append(by_condition[cond].pop())
    rng.shuffle(chosen)
    return chosen


def write_calibration(run_dir: Path, responses: list[dict], fact_rows: list[dict], cases: dict, out_md: Path,
                      out_key: Path, seed: int) -> int:
    chosen = calibration_sample([r for r in responses if cases[r["case_id"]].get("critical_facts")],
                                CALIBRATION_SIZE, seed)
    verdicts = {r["row_id"]: r for r in fact_rows}
    L = ["# Judge calibration set", "", es.SURFACE_NOTICE, "", es.JUDGE_NOTICE, "",
         f"{len(chosen)} responses sampled across conditions from `{run_dir.as_posix()}`. Conditions and the "
         "judge's verdicts are withheld in `judge_calibration_key.json`. Scoring these by hand (tick the facts "
         "each response states and the misconceptions it asserts) and comparing with the key gives an agreement "
         "rate for the judge. Optional; nothing depends on it.", ""]
    key = []
    for n, r in enumerate(chosen, start=1):
        case = cases[r["case_id"]]
        blind_id = f"CAL{n:02d}"
        L += [f"## {blind_id}", "", request_text(case).replace("\n", "  \n"), "", "Response:", "", "````",
              blind(r["text"]), "````", "", "Facts stated (tick):"]
        L += [f"- [ ] {f['id']}: {f['fact']}" for f in case["critical_facts"]]
        L += ["", "Misconceptions asserted (tick):"]
        L += [f"- [ ] {k}: {v}" for k, v in misconception_ids(case).items()] or ["- (none)"]
        L.append("")
        v = verdicts.get(r["row_id"], {})
        key.append({"blind_id": blind_id, "row_id": r["row_id"], "condition": r["condition"],
                    "judge_facts_stated": v.get("facts_stated", "").split(";") if v.get("facts_stated") else [],
                    "judge_misconceptions_asserted": (v.get("misconceptions_asserted", "").split(";")
                                                      if v.get("misconceptions_asserted") else [])})
    out_md.write_bytes("\n".join(L).encode("utf-8"))
    out_key.write_bytes((json.dumps({"notice": es.JUDGE_NOTICE, "items": key}, indent=2) + "\n").encode("utf-8"))
    return len(chosen)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def judge_run(run_dir: Path, backend: jl.Backend, tasks: tuple[str, ...] = TASKS, seed: int = 0) -> dict:
    cases = es.load_cases()
    conditions = es.load_conditions()
    responses = load_responses(run_dir)
    out_dir = run_dir / "judge"
    judge = jl.CachedJudge(backend, out_dir / "cache", progress=True)
    present = {r["condition"] for r in responses}
    comparisons = [p for p in conditions["comparisons"] if p[0] in present and p[1] in present]
    fact_rows = run_facts(judge, responses, cases) if "facts" in tasks else []
    pairs = build_pairs(responses, comparisons)
    pair_rows = []
    if "pairwise" in tasks:
        pair_rows += run_pairwise(judge, pairs, cases, "pairwise", OVERALL_QUESTION, seed)
    if "dimension" in tasks:
        for dim, question in JUDGED_DIMENSIONS.items():
            pair_rows += run_pairwise(judge, pairs, cases, dim, question, seed)
    facts = fact_tables(fact_rows, comparisons)
    pairwise = pairwise_tables(pair_rows) if pair_rows else {"tables": {}, "flip_rate_by_task": {}}
    summary = {"notice": [es.SURFACE_NOTICE, es.JUDGE_NOTICE], "backend": backend.name, "model": backend.model,
               "responses": len(responses), "facts": facts, "pairwise": pairwise,
               "fluency_checks": fluency_checks(facts, pairwise),
               "judge_calls": judge.calls, "cache_hits": judge.hits}
    out_dir.mkdir(parents=True, exist_ok=True)
    fact_cols = ["row_id", "case_id", "condition", "sample_index", "n_facts", "facts_stated", "n_stated",
                 "misconceptions_asserted"]
    pair_cols = ["task", "comparison", "case_id", "sample_index", "x_row", "y_row", "first_shown",
                 "verdict_order1", "verdict_order2", "consistent", "winner"]
    if fact_rows:
        es.write_csv(out_dir / "fact_capture.csv", fact_cols, fact_rows)
    if pair_rows:
        es.write_csv(out_dir / "pairwise.csv", pair_cols, pair_rows)
    (out_dir / "judge_summary.json").write_bytes((json.dumps(summary, indent=2) + "\n").encode("utf-8"))
    (out_dir / "judge_summary.md").write_bytes(render(summary).encode("utf-8"))
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Automated screening judge over a collected run.")
    parser.add_argument("run_dir")
    parser.add_argument("--tasks", default=",".join(TASKS), help=f"comma-separated subset of {', '.join(TASKS)}")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--min-interval", type=float, default=6.0, help="seconds between judge calls (free tier)")
    parser.add_argument("--calibration", action="store_true",
                        help="write evaluation/judge_calibration_set.md and the withheld key")
    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)
    tasks = tuple(t.strip() for t in args.tasks.split(",") if t.strip())
    unknown = [t for t in tasks if t not in TASKS]
    if unknown:
        parser.error(f"unknown task(s) {unknown}")
    if not (run_dir / "run_sheet.csv").is_file():
        print(f"judge: run sheet not found in {run_dir}", file=sys.stderr)
        return 1
    try:
        backend = jl.backend_from_env(min_interval=args.min_interval)
        if args.calibration:
            summary = judge_run(run_dir, backend, ("facts",), args.seed)
            _, fact_rows = es.read_csv(run_dir / "judge" / "fact_capture.csv")
            n = write_calibration(run_dir, load_responses(run_dir), fact_rows, es.load_cases(),
                                  es.EVAL_DIR / "judge_calibration_set.md", es.EVAL_DIR / "judge_calibration_key.json",
                                  args.seed)
            print(f"Wrote evaluation/judge_calibration_set.md ({n} responses) and judge_calibration_key.json")
            return 0
        summary = judge_run(run_dir, backend, tasks, args.seed)
    except jl.JudgeUnavailable as exc:
        print(f"judge: {exc}. Progress is cached; rerun the same command to resume.", file=sys.stderr)
        return 2
    except jl.JudgeError as exc:
        print(f"judge: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {run_dir / 'judge' / 'judge_summary.md'} ({summary['judge_calls']} judge calls, "
          f"{summary['cache_hits']} cached). Flip rate: {summary['pairwise']['flip_rate_by_task'] or 'n/a'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
