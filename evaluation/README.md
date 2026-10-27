# Evaluation framework

This folder holds everything needed to test whether Explanation Lab V0 improves
explanations beyond normal Claude and beyond a strong generic prompt. Every step
runs by hand in ordinary Claude chats. No API key is needed, and nothing
automates the Claude interface.

**No evaluation has been run yet.** The folder contains instruments, not results.

## Files

| File | Purpose |
|---|---|
| `EVALUATION_PLAN.md` | What is measured, the conditions, the design, the analysis, the success criteria, and the ablation extension |
| `BASELINE_INSTRUCTIONS.md` | Exact text and product mechanism for each condition (A, B, C natural, C explicit, optional D, ablation variants) |
| `conditions.json` | Machine-readable copy of the conditions, used by the scripts (a test keeps it identical to the Markdown) |
| `TEST_CASES.json` | 33 held-out cases with expected properties, misconceptions, critical facts, and reasoning gaps |
| `RUBRIC.md` | Anchored 1–5 scores for 11 dimensions, critical-fact coding, adherence codes, ranking, and rater calibration |
| `RUNBOOK.md` | Step-by-step operator procedure: settings, batches, activation evidence, blinding, summarizing |
| `RESULTS_TEMPLATE.csv` | Columns of the run sheet (generation log) |
| `RATINGS_TEMPLATE.csv` | Columns of a rater's sheet |
| `comprehension/PROTOCOL.md` | Human pre/post/transfer comprehension pilot with a Latin-square design |
| `comprehension/ITEM_BANK.json` | Draft items for 3 topics (must be screened before use) |
| `comprehension/RESPONSES_TEMPLATE.csv`, `EXPOSURE_TEMPLATE.csv` | Comprehension data columns |

## Five-command workflow

```
python scripts/package_skill.py                                   # build dist/explanation-lab.zip
python scripts/make_run_sheet.py --run-id pilot-1 --seed 1        # run sheet + exact messages
python scripts/run_assistant.py evaluation/runs/pilot-1           # clipboard helper while you chat in Claude
python scripts/summarize_results.py evaluation/runs/pilot-1 --check-only
python scripts/prepare_blind_packet.py evaluation/runs/pilot-1 --raters r1,r2
#   ... raters fill blind/ratings/*.csv using RUBRIC.md ...
python scripts/summarize_results.py evaluation/runs/pilot-1        # summary.md + summary.json
```

For the comprehension pilot:

```
python scripts/assign_comprehension.py --participants 18 --out evaluation/runs/pilot-1/comprehension/assignment.csv
```

## What is kept separate

| Dimension | Measured by | Never inferred from |
|---|---|---|
| Skill activation | Operator observation at generation time | Response quality |
| Instruction adherence | Blind adherence codes | Overall scores |
| Explanation quality | 9 anchored rater dimensions | Length, formatting, readability formulas |
| Factual accuracy | Critical-fact and error coding | Rater impressions of clarity |
| Comprehension | Human pre/post/transfer tests | Rater scores, or any AI model answering questions |
