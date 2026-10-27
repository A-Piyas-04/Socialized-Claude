# Superseded judge acceptance runs (kept, not deleted)

These cached verdicts come from the first design of `scripts/judge_acceptance.py`, which judged
Claude-vs-GPT pairs from the archive. That design was **superseded on 2026-10-27**: the project
now improves Claude's explanations, Claude-vs-GPT comparisons are out of the evaluation, and the
acceptance test is Claude-vs-Claude plus a floor test of degraded answers. Nothing here counts
toward accepting or rejecting a judge.

Both runs stopped at the Gemini free tier's 20 requests per day per model.

| Model | Pairs judged in both orders | Order flips | Note |
|---|---:|---:|---|
| `gemini-3.6-flash` | 6 | 0 | All six consistent verdicts favoured the Claude answer. |
| `gemini-2.5-flash` | 9 | 2 | Both flips were base-vs-base pairs (interest, databases); all seven consistent verdicts favoured the Claude answer. |

With every consistent verdict going one way and no within-provider control pair judged, neither
run can distinguish discrimination from a fixed preference.

Files: `gemini-3.6-flash/` and `gemini-2.5-flash/` are the judge caches (model output only, keyed
by a hash of the exact request; no credentials).
