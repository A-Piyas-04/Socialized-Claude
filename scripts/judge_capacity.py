"""Measure the judge's real token cost and project days to finish, before committing to a run.

    python scripts/judge_capacity.py --tpd 200000       # tokens per day allowed for the model

Makes two real calls through the cache the acceptance test uses (one pairwise prompt, one
fact-capture prompt), so they are not wasted. Reads tokens per call from the API's `usage` field
and request limits from its x-ratelimit headers, then projects:

  acceptance   every prompt of scripts/judge_acceptance.py, sized exactly (built offline)
  pilot sweep  evaluation/runs/pilot16-cc: fact capture on every response, pairwise preference
               and the two judged dimensions on every comparison pair, both orders; responses do
               not exist yet, so their length is estimated from the archive's Claude answers

Prompt tokens are scaled from characters with the ratio measured on the real calls; completion
tokens use the measured average. Writes research/judge_capacity.json and prints the projection.
If the projection exceeds --max-days, it says so: do not start a run that cannot finish.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402
import judge as jd  # noqa: E402
import judge_acceptance as ja  # noqa: E402
import judgelib as jl  # noqa: E402

OUT_PATH = es.REPO_ROOT / "research" / "judge_capacity.json"
SWEEP_RUN = es.EVAL_DIR / "runs" / "pilot16-cc"


class RecordingBackend:
    """Collects every prompt the acceptance test would send, without calling anything."""

    name, model = "recording", "none"

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete(self, prompt: str, temperature: float) -> str:
        self.prompts.append(prompt)
        return '{"facts_stated": [], "misconceptions_asserted": []}' if "FACTS:" in prompt else '{"winner": 1}'


def acceptance_prompts(tmp: Path) -> list[str]:
    recorder = RecordingBackend()
    ja.acceptance(recorder, cache_dir=tmp)
    return recorder.prompts


def sweep_prompt_chars(run_dir: Path, mean_response_chars: float) -> tuple[list[int], list[int]]:
    """Estimated sizes of fact and pairwise prompts for a run whose responses may not exist yet."""
    cases = es.load_cases()
    conditions = es.load_conditions()
    _, rows = es.read_csv(run_dir / "run_sheet.csv")
    stand_in = "x" * int(mean_response_chars)
    facts = [len(jd.facts_prompt(cases[r["case_id"]], stand_in)) for r in rows
             if cases[r["case_id"]].get("critical_facts")]
    present = {r["condition"] for r in rows}
    pairs = [p for p in conditions["comparisons"] if p[0] in present and p[1] in present]
    keys = {(r["case_id"], r["sample_index"]) for r in rows}
    pairwise = []
    for case_id, _ in sorted(keys):
        for _ in pairs:
            for question in (jd.OVERALL_QUESTION, *jd.JUDGED_DIMENSIONS.values()):
                size = len(jd.pair_prompt(cases[case_id], stand_in, stand_in, question))
                pairwise += [size, size]
    return facts, pairwise


def project(prompt_chars: list[int], tokens_per_char: float, completion: float) -> int:
    return int(sum(c * tokens_per_char + completion for c in prompt_chars))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure judge token cost and project days to finish.")
    parser.add_argument("--tpd", type=int, required=True, help="tokens per day allowed for the judge model")
    parser.add_argument("--rpd", type=int, default=None, help="requests per day (read from headers if omitted)")
    parser.add_argument("--max-days", type=float, default=3.0)
    args = parser.parse_args(argv)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        prompts = acceptance_prompts(Path(tmp))
    pair_prompt = next(p for p in prompts if "ANSWER 1:" in p)
    fact_prompt = next(p for p in prompts if "FACTS:" in p)
    try:
        backend = jl.backend_from_env(min_interval=0)
        judge = jl.CachedJudge(backend, ja.CACHE_DIR, progress=True)
        measured = []
        for prompt in (pair_prompt, fact_prompt):
            judge.ask(prompt)
            usage = getattr(backend, "last_usage", {}) if judge.calls else {}
            if not usage:
                raise jl.JudgeError("no usage recorded (prompt was already cached or the backend reports none)")
            measured.append({"kind": "pairwise" if prompt is pair_prompt else "facts", "prompt_chars": len(prompt),
                             "prompt_tokens": usage.get("prompt_tokens"),
                             "completion_tokens": usage.get("completion_tokens"),
                             "total_tokens": usage.get("total_tokens")})
            judge.calls = 0
        limits = getattr(backend, "last_limits", {})
    except jl.JudgeError as exc:
        print(f"judge_capacity: {exc}", file=sys.stderr)
        return 1
    tokens_per_char = statistics.fmean(m["prompt_tokens"] / m["prompt_chars"] for m in measured)
    completion = statistics.fmean(m["completion_tokens"] for m in measured)
    _, archive = ja.load_archive()
    mean_chars = statistics.fmean(len(r["text"]) for r in archive)
    sweep_facts, sweep_pairs = sweep_prompt_chars(SWEEP_RUN, mean_chars)
    rpd = args.rpd or int(limits.get("x-ratelimit-limit-requests", 0) or 0) or None
    plans = {}
    for name, chars in (("acceptance", [len(p) for p in prompts]), ("pilot sweep", sweep_facts + sweep_pairs)):
        tokens = project(chars, tokens_per_char, completion)
        days_tokens = tokens / args.tpd
        days_requests = len(chars) / rpd if rpd else None
        plans[name] = {"calls": len(chars), "projected_tokens": tokens, "days_by_tokens": round(days_tokens, 2),
                       "days_by_requests": round(days_requests, 2) if days_requests else None,
                       "days": round(max(days_tokens, days_requests or 0), 2)}
    result = {"notice": es.JUDGE_NOTICE, "backend": backend.name, "model": backend.model, "measured": measured,
              "tokens_per_prompt_char": round(tokens_per_char, 4), "mean_completion_tokens": round(completion, 1),
              "rate_limit_headers": limits, "tokens_per_day": args.tpd, "requests_per_day": rpd,
              "sweep_response_chars_estimate": round(mean_chars), "plans": plans}
    OUT_PATH.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    for m in measured:
        print(f"measured {m['kind']}: {m['prompt_tokens']} prompt + {m['completion_tokens']} completion tokens")
    for name, plan in plans.items():
        print(f"{name}: {plan['calls']} calls, ~{plan['projected_tokens']:,} tokens -> {plan['days']} day(s) "
              f"(tokens {plan['days_by_tokens']}, requests {plan['days_by_requests']})")
    too_long = [n for n, p in plans.items() if p["days"] > args.max_days]
    if too_long:
        print(f"STOP: {', '.join(too_long)} would take more than {args.max_days} days at this model's limits.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
