# Evaluation Plan — Explanation Lab V0

**Status: planned, not yet run.** No results exist. Nothing in this document is a
finding.

## 1. What the evaluation must answer, separately

| # | Question | Measure | Instrument |
|---|---|---|---|
| Q1 | Does the skill install and load? | Upload success; activation recorded per response | `RUNBOOK.md` §3, run sheet |
| Q2 | When the skill is eligible, does Claude load it without being asked? When it is not eligible, does Claude leave it alone? | Activation rate by `skill_expectation` | Run sheet `activation_observed` |
| Q3 | Does the output follow the skill's behavioural rules? | Adherence-violation rates | Rubric §C |
| Q4 | Is the explanation better as an explanation? | 9 dimension scores, within-case rank | Rubric §A and §D |
| Q5 | Is it accurate? | Critical facts, errors, unsupported certainty | Rubric §B |
| Q6 | Does it make answers longer? | Word counts, length ratios | `summarize_results.py` |
| Q7 | Do people understand more afterwards? | Pre/post/transfer comprehension | `comprehension/PROTOCOL.md` |

Q4 is **not** evidence for Q7. Raters judging clarity is a different measurement
from learners demonstrating understanding (the illusion-of-fluency literature
predicts the two can diverge). Both are reported separately.

## 2. Conditions

Defined exactly in `BASELINE_INSTRUCTIONS.md` and `conditions.json`. Pilot
conditions are `A_normal`, `B_prompt`, `C_skill`, and `C_skill_explicit`.
`D_skill_text` is optional.

**Activation states.** The analysis distinguishes three of them:

- **Natural activation.** `C_skill` rows where the operator saw evidence that the
  skill was loaded.
- **Confirmed execution.** Any C row with direct evidence that `SKILL.md` was read
  (for example, the tool-activity panel shows the file being read).
- **Explicit request.** `C_skill_explicit` rows, which also record whether
  loading was observed.

A `C_skill` response without activation is still analysed as `C_skill`
(intention-to-treat). The per-protocol subset (activated only) is reported
separately and **labelled as biased**: Claude chooses which prompts activate the
skill, so that subset is not a random sample of prompts.

## 3. Test set

`TEST_CASES.json` contains 33 held-out cases:

| Category | n | `skill_expectation` |
|---|---:|---|
| foundational | 4 | should_apply |
| mechanism | 5 | should_apply |
| abstract | 3 | should_apply |
| multi_step_process | 3 | should_apply |
| comparison | 4 | should_apply |
| follow_up | 3 | should_apply |
| advanced | 3 | apply_briefly |
| concise_factual | 3 | 2 should_not_apply, 1 apply_briefly |
| negative_control | 4 | should_not_apply |
| mixed_task | 1 | apply_briefly |

The cases cover 12 domains. Topics are disjoint from the research archive's five
topics and from every example inside the skill. The test
`tests/test_test_cases.py::test_cases_are_held_out` checks this with keyword
lists.

## 4. Design

### 4.1 Pilot round 1

- **Cells.** 33 cases × 4 conditions × 1 sample = 132 responses.
- **Reduced pilot** (if time is short). The 16-case stratified subset marked
  `pilot16` in `scripts/make_run_sheet.py` gives 64 responses.
- **Order.** The skill toggle is account-wide, so responses are generated in two
  batches: `skill_off` (A, B, D) and `skill_on` (C_skill, C_skill_explicit).
  Within a batch, the order of case × condition is randomized
  (`make_run_sheet.py --seed`). Both batches should be finished on the same day
  with the same model selected.

### 4.2 Sampling variance (round 1b)

Claude's outputs vary between identical requests. For a 12-case subset, generate
a second sample in every condition (`--samples 2`). Differences between
conditions are only meaningful if they are larger than differences between two
samples of the same condition. The summary reports within-condition sample
spread where two samples exist.

### 4.3 Follow-up cases

Round 1 uses a fixed quoted context (same message for all conditions). A later
round may use the natural two-turn form, where each condition generates its own
first answer. That is more realistic but confounds the follow-up with the
quality of the first answer.

### 4.4 Raters

- At least **2 raters**, ideally people who did not generate the responses.
- Each rater scores every response in the blind packet.
- Calibration comes first (`RUBRIC.md`, "Rater calibration").
- Raters see each case's responses together, in a random order, labelled only
  by blind ID.

### 4.5 Human comprehension pilot

This is separate from the rating study. See `comprehension/PROTOCOL.md`: 3
topics, a within-participant Latin square over `A_normal`, `B_prompt`, and
`C_skill_explicit`, and 12–18 participants.

## 5. Analysis

The unit of analysis is the **case**. For each response, scores are averaged over
raters, then averaged over samples within each case × condition. Every
comparison is **paired by case**.

For each comparison in `conditions.json` and each dimension,
`summarize_results.py` reports:

- n (cases with both conditions rated)
- mean paired difference and its standard deviation
- a 95% bootstrap percentile interval (10,000 resamples of cases, fixed seed)
- wins / ties / losses across cases

Also reported:

- activation rates by condition and `skill_expectation`
- adherence-code rates
- critical-error totals
- median word counts and the median paired length ratio
- mean within-case rank
- inter-rater agreement per dimension (exact, within one point, mean absolute
  difference)

No significance tests are reported, and no superiority claims are made from
the pilot. With 25 eligible cases and 2 raters, the pilot is meant to estimate
variability and expose problems with the instruments, not to settle the
question.

Pre-declared primary quality outcomes: `mechanistic_clarity` and
`prerequisite_sequencing`. These are the two dimensions the core operations
target. Their guardrails are `accuracy`, `appropriate_depth`, and
`responsiveness_to_intent`. The other dimensions are secondary.

## 6. Pilot success criteria (engineering targets)

These thresholds are **engineering targets chosen before data collection**, not
scientifically validated thresholds. Changing them after seeing results must be
recorded as a deviation.

`summarize_results.py` reports `INSUFFICIENT_DATA` instead of MET or NOT_MET when
a criterion rests on fewer than 10 cases (S2, S4, S5, S6) or fewer than 6 paired
participants (S7). This stops a handful of responses from producing a verdict.
The `--min-cases` option exists for testing and must not be lowered for real
runs.

| ID | Criterion | Target | Evaluated by |
|---|---|---|---|
| S1 | Installs without structural errors | ZIP uploads and can be enabled | Operator, `RUNBOOK.md` §3 |
| S2 | Natural activation on eligible cases | Activation observed in ≥ 60% of `should_apply` `C_skill` responses | Summary: activation table |
| S3 | No hijacking | `HIJACK` code on ≤ 1 `should_not_apply` response in C conditions, and no more often than in A | Summary: adherence table |
| S4 | No critical errors introduced | Total critical errors in C_skill_explicit ≤ B_prompt, and no case where C has a critical error that both A and B avoided | Summary: accuracy table |
| S5 | No systematic verbosity | Median paired length ratio C_skill_explicit / A_normal ≤ 1.5 on `should_apply`, and ≤ 1.2 on the other cases; `LENGTH_IGNORED` never in C | Summary: verbosity table |
| S6 | Pedagogical preference | C_skill_explicit vs B_prompt: positive mean paired difference on both primary dimensions with the 95% interval excluding 0, **or** C ranked above B in ≥ 60% of `should_apply` cases | Summary: comparisons |
| S7 | Comprehension signal | In the human pilot: mean post-test score on transfer and misconception items for C ≥ B and ≥ A, with no topic where C is clearly worse. Reported with intervals; directional only. | `comprehension/PROTOCOL.md` §8 |

### Decisions after the pilot

- **S1–S5 all pass, and S6 passes.** Proceed to the ablation round (§8) and a
  larger comprehension study.
- **S6 fails but S2 fails too.** Treat this as an activation problem first.
  Compare C_skill_explicit with B. If explicit wins, iterate on the description.
- **S6 fails with explicit invocation.** The methodology shows no advantage over a
  good prompt. Revise or narrow it, informed by the dimension-level results.
- **S4 or S5 fails.** Fix this before anything else. Do not ship a version that
  adds errors or length.

## 7. Threats to validity and mitigations

| Threat | Mitigation |
|---|---|
| Operator is also a rater | Prefer separate people. If unavoidable, wait at least a day before rating, and rely on the blind packet. |
| Model or product changes during the study | Record the model label and date per row. Finish each batch in one session. Rerun the batch if the model changes. |
| Raters recognise a condition's style | Raters note suspected recognition in `rater_notes`. The summary counts it. |
| Responses reveal the condition ("as the skill says…") | `prepare_blind_packet.py` flags mentions of the skill, which are also an `INTERNAL_LABEL` violation. |
| Length bias in raters | Rubric instructs against it. The summary reports length alongside quality, so the two can be checked against each other. |
| Test-case contamination | Topics are disjoint from research topics and skill examples (checked by test). |
| B is a different mechanism from C | Explicit-invocation condition and optional D condition. Mechanism recorded per row. |
| LLM-as-judge temptation | An LLM judge may be added only as a clearly labelled secondary analysis. It is never used for S1–S7. |

## 8. Ablation extension (later round)

**Goal.** Find which parts of the skill produce any benefit. Specifically:

- whether prerequisite ordering helps
- whether causal explanation helps
- whether combining them helps more
- whether adaptive selection of the other operations adds value

**Conditions.** `V_core`, `V_seq`, `V_mech`, `V_seq_mech`, and `V_full`. They are
built by `python scripts/package_skill.py --all-variants`. Each condition is a
temporary ZIP with the same name and description. All use the explicit
invocation line, so activation is held constant and the comparison is about
methodology.

**Cases.** The 25 `should_apply` cases, plus 4 negative controls as a hijack
check.

**Procedure.** Install one variant, run its batch, then delete it and install
the next. Record each variant's `zip_sha256` from its manifest.

**Comparisons** (in `conditions.json`):

| Comparison | Question |
|---|---|
| `V_seq` vs `V_core` | Does ordering help beyond the shared scaffold? |
| `V_mech` vs `V_core` | Does mechanism help beyond the scaffold? |
| `V_seq_mech` vs each single operation | Does combining them help? |
| `V_full` vs `V_seq_mech` | Do the conditional operations (examples, terms, structure) add value? |

**Interpretation cautions.**

- Combining operations is not assumed to be additive. More instructions can
  conflict or dilute each other. A combination doing worse than a single
  operation is a legitimate finding.
- `V_core` is itself an intervention: scope gating, calibration, and accuracy
  rules. Comparing it with `B_prompt` and `A_normal` shows how much of any
  effect comes from the wrapper rather than the operations.
- Ablation conclusions about *comprehension* still need the human protocol.
  Rating differences alone are not enough.

## 9. Optional automated checks

These run offline and support, but never replace, human evaluation:

- Structural validity of the skill (`scripts/validate_skill.py`).
- Completeness and schema validity of run sheets and ratings
  (`summarize_results.py` reports every gap).
- Length statistics.
- Activation and adherence tabulation.

There is **no** automated "comprehension score". Word counts, heading counts,
readability formulas, and semantic similarity are not measures of
understanding, and the tools do not present them as such.
