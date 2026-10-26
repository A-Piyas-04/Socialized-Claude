# Evidence Audit — ExplanationLab archive 2026-10-26

Audit date: 2026-10-26. Auditor: implementation agent for Explanation Skill V0.

This document records what the ExplanationLab archive does and does not show, and
how that evidence was used to choose the V0 Skill's explanation operations.

Every number below can be regenerated with:

```
python research/recompute_archive_stats.py
```

The script reads only `research-results-2026-10-26/`. Treatment instruction texts
and detector logic were read from the public ExplanationLab repository
(`github.com/A-Piyas-04/claude-chatgpt-explanation-lab`, `main` at commit
`2548dfc`), files `apps/api/explanationlab/transformations/strategies.py`,
`transformations/fidelity.py`, `prompts/builtin.py`, `evaluation/rubrics.py`, and
`Docs/RESEARCH_FOUNDATIONS.md`. That repository is not vendored here.

## Evidence labels used in this document

Following the lab's own scheme (`Docs/RESEARCH_FOUNDATIONS.md`):

| Label | Meaning |
|---|---|
| **Observation** | Directly visible in an archive file. Cited by path. |
| **Literature (L2)** | Learning-science finding cited in the lab's foundations document. Not tested here. |
| **Hypothesis (L4)** | Our conjecture. Needs an experiment. |
| **Engineering choice** | A design decision made for practical reasons, not because evidence demands it. |

Nothing in this audit is a **validated result** about comprehension. None exists.

---

## 1. What was inspected

| Source | What it contains | Used for |
|---|---|---|
| `research-results-2026-10-26/README.md`, `NEXT_STEPS.md` | Archive summary and known gaps | Claims to verify |
| `experiments/experiment-3/experiment-3-report.md`, `experiment-3-results.csv` | 60 single-treatment rows | Verdict counts |
| `experiments/experiment-3/transforms/*/transform-*.json` (60 files) | Full rewrite text, analysis, plan, diff stats, fidelity warnings, numeric drift | All per-run checks |
| `experiments/experiment-4/experiment-4-report.md`, `experiment-4-results.csv` | 20 rewriter cells for T2 | Rewriter comparison |
| `experiments/experiment-4/cross/cross-*.json` (10 files) | Second-rewriter T2 outputs | Rewriter comparison |
| `experiments/experiment-5/*` | 5 study configs, 5 proxy result files, 5 proxy reports, CSV | Ceiling check |
| `inputs/input-dataset.json` | 5 questions with factual checklists, 30 imported answers | Sources, prompt-style lengths |
| `inputs/study-items.json` | 15 multiple-choice proxy items | Item difficulty |
| `examples/candidate-before-after.md` | One T2 before/after pair per topic | Qualitative inspection |
| `scripts/*.py` | Report builder and stage runners | How rows were produced |
| Lab repo `strategies.py` | **Exact T1–T6 instruction templates** | Treatment definitions |
| Lab repo `fidelity.py` | Deterministic detector rules | Interpreting verdicts |
| Lab repo `prompts/builtin.py` | Experiment 2 "tutor" and "pedagogical" prompts | Baseline design |

Not available in the archive: the app database (`apps/api/explanationlab.sqlite3`,
referenced by `scripts/build_reports.py`), the Gemini judge scores, and any human
participant data. The reports therefore cannot be regenerated with the archive's
own `build_reports.py`. `recompute_archive_stats.py` recomputes the counts from the
raw JSON files instead, and it agrees with both published CSVs (0 verdict
mismatches).

---

## 2. Experimental summary

### 2.1 Source material (inputs)

- **Observation.** 5 questions, all "moderate" difficulty: write-through vs
  write-back caching, B-tree indexes, the TCP three-way handshake, vaccines, and
  compound vs simple interest (`inputs/input-dataset.json`). Domains are 3
  software engineering, 1 biology, 1 finance.
- **Observation.** 30 imported web-chat answers: 5 questions × 2 providers
  (`claude-sonnet-5-5`, `gpt-6-luna`) × 3 prompt styles (`base`, `tutor`,
  `pedagogical`). Each answer carries the limitation note: "Generation settings,
  system prompt and any product-side scaffolding are unknown."
- **Observation.** The `tutor` and `pedagogical` styles are Experiment 2's
  conditions B and C (`prompts/builtin.py`). `tutor` is the one-line "Act as a
  helpful tutor. Explain clearly, step by step, using simple language and practical
  examples." `pedagogical` is a 10-step structured teaching process that already
  asks for prerequisites, ordering, mechanism, grounding, and term definitions.
- **Observation.** Median answer length by style: base 491 words, tutor 693,
  pedagogical 1,098.5. The structured prompt more than doubled length.
- **Observation (unverifiable here).** `NEXT_STEPS.md` states the Gemini judge
  gave 5/5 on all nine dimensions for all 30 answers. The judge outputs are not in
  the archive, so this cannot be checked. If true, Experiment 2 produced no
  discriminating quality evidence.

### 2.2 Experiment 3 — single-treatment rewrites

- **Observation.** 60 runs = 5 topics × 2 source answers (`base` only) × 6
  treatments. Each run uses `gemini-3.5-flash-lite` for every stage: A (analysis),
  B (planning), C (treatment rewrite), and D (fidelity review).
- **Observation.** The task is **rewriting an existing answer**, not generating a
  new one. Every treatment carries the hard constraint "Do not invent facts…
  Do not change any technical claim… If the source is wrong, leave it wrong."
- **Observation.** The fidelity verdict is driven mostly by deterministic
  detectors (`fidelity.py`):
  - `numeric_change` (severity high, so the verdict becomes `serious_concerns`):
    any number whose count differs between source and rewrite. This includes
    list markers ("1.", "2.") and illustrative numbers in an added example.
  - `omitted_caveat` and `unjustified_certainty`: substring counts of hedges
    ("can ", "may ") and absolutes ("never", "always"), compared before and after.
  - `boundary_violation`: headings, tables, or more than 2 list items added by any
    treatment other than T5.
  - One LLM reviewer from the same model family as the rewriter.

| Treatment | Runs | Clean | Warnings | Serious | Output identical to source | Clean **and** changed | Median similarity | Median word change (CSV) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| T1 | 10 | 7 | 1 | 2 | 0 | 7 | 0.904 | +54 |
| T2 | 10 | 9 | 0 | 1 | **4** | **5** | 0.965 | +0 |
| T3 | 10 | 1 | 6 | 3 | 0 | 1 | 0.788 | +212 |
| T4 | 10 | 3 | 2 | 5 | 2 | 1 | 0.899 | +95.5 |
| T5 | 10 | 2 | 0 | 8 | 0 | 2 | 0.912 | +31 |
| T6 | 10 | 7 | 1 | 2 | **6** | **1** | 1.000 | +0 |

"Identical" means `word_similarity ≥ 0.999` in the run's `changes[0].stats`. In
every such case, the fidelity notes confirm it: "The rewritten explanation is
identical to the original explanation."

### 2.3 Experiment 4 — second rewriter, T2 only

- **Observation.** The CSV has 20 rows, but only **10 are new rewrites** (by
  `gemini-3.1-flash-lite`, `cross-*.json`). The other 10 rows are the Experiment 3
  T2 runs, reused (same `variant_response_id`).
- **Observation.** The new rewriter's verdicts: 6 clean, 1 warning, 3 serious. It
  never returned an identical text (median similarity 0.816, median +45 words).
- **Observation.** The planned design, ChatGPT ↔ Claude website rewrites, was
  **not run** (`NEXT_STEPS.md` item 1). Both rewriters are Gemini models. The
  comparison is therefore **between two rewriter models of one family**, not
  between providers.

### 2.4 Experiment 5 — AI answerability proxy

- **Observation.** 5 draft studies, 3 multiple-choice items each (15 items),
  covering 19 conditions. The TCP ChatGPT T2 variant was excluded after its
  `serious_concerns` verdict. The proxy model was `gemini-3.5-flash-lite`.
- **Observation.** The no-explanation control answered **15/15** correctly, so
  there were **0 diagnostic items**. The study cannot detect any effect.
- **Observation.** The items are textbook recall. For example, "Which message
  starts the TCP three-way handshake?" (`inputs/study-items.json`). The item
  labelled `C_transfer` for databases ("What additional resource does the index
  itself require?") is recall, not transfer.
- **Observation.** The only differences between conditions are two "correct but
  quote not found" cases (`proxy-tcp.json`, Claude base and Claude T2, item B).
  The quoted evidence contains an ellipsis ("…"), so exact string matching
  failed. This is a **quote-matching artifact**, not a comprehension difference.
- **Observation.** No human participant read any explanation (`README.md`).

---

## 3. Verification of the preliminary findings in the brief

| Brief's claim | Status | Notes |
|---|---|---|
| E3: ~60 single-treatment runs, 6 treatments, 5 topics, 2 sources | **Confirmed** | Exactly 60. Sources are the `base` answers only. |
| T2 performed relatively well on automated fidelity screening | **Confirmed, but misleading** | 9/10 clean, but 4 of those 9 are unchanged copies of the source. Only 5 clean runs changed the text, and 2 of those 5 only added transition phrases. |
| Some T2 outputs made very limited changes | **Understated** | 4/10 made **no** change. Median similarity was 0.965. |
| Fidelity alone cannot establish that T2 improves comprehension | **Confirmed** | Also: a clean verdict is mostly the absence of lexical and numeric triggers, not a semantic check (§4). |
| E4: ~20 cross-model rewriting runs | **Partly incorrect** | 20 rows, but 10 are reused E3 runs. The 10 new rewrites use a second Gemini model. No Claude or ChatGPT rewriter was used. |
| E4: different rewriters produced different fidelity outcomes | **Confirmed** | 9/10 vs 6/10 clean. The first rewriter's "advantage" is largely its no-op outputs (4 identical copies). Excluding them, it had 5 clean of 6 changed outputs, against the second rewriter's 6 of 10. |
| E4: cross-model generalization not established | **Confirmed** | It was not tested in the intended form at all. |
| E5: proxy answered all 15 questions without explanations; ceiling | **Confirmed** | 15/15. 0 diagnostic items. |
| E5 could not determine whether transformations improved comprehension | **Confirmed** | No human data either. |

---

## 4. What the automated fidelity screen actually measures

These points determine how much weight any verdict count can carry.

1. **No-op outputs score best.** An unchanged text cannot trigger any detector.
   T2 and T6 had the most clean verdicts and also the most identical outputs
   (4 and 6). Ranking treatments by clean-verdict rate rewards doing nothing.
2. **`numeric_change` penalizes the intended function of T4 and T5.**
   - T4 adds an example, which usually contains numbers. Examples: `0x7FFF1000`
     and "1,000 times" in `transform-caching-claude-T4.json`, and "10 million
     rows" in `transform-databases-claude-T4.json`.
   - T5 turns prose into numbered lists. Example: drift values "1", "2", "3" in
     `transform-immunology-claude-T5.json`.
   - All 8 serious T5 verdicts have no semantic finding from the LLM reviewer.
3. **Hedge and certainty detectors are substring counts.** In T3, "never"
   appearing once more yields `unjustified_certainty` whether or not a claim
   became stronger. These detectors are still relevant to T3: certainty creep
   and hedge loss are real risks when adding causal detail. But they are noisy.
4. **Only 6 semantic findings exist in 70 rewrites**, all from the LLM reviewer:

   | File | Finding | Substantive error? |
   |---|---|---|
   | `transform-interest-claude-T3.json` | "Alamo-like balances" inserted | **Yes**: corrupted text |
   | `cross-interest-chatgpt-T2-gemini-3.1-flash-lite.json` | "linear and exponential growth are mutually dependent" | **Yes**: false claim. T2's template step 3 explicitly asks to state mutual dependencies. |
   | `transform-immunology-chatgpt-T3.json` | Added phagocytosis, endocytosis, inactivation methods | Unsupported by the source; not necessarily false |
   | `transform-caching-claude-T4.json` | Illustrative address and loop count | Illustrative detail, flagged as new |
   | `transform-databases-claude-T4.json` | "10 million rows" example | Illustrative detail, flagged as new |
   | `transform-immunology-chatgpt-T4.json` | Influenza-shot example | Illustrative detail, flagged as new |

5. **The reviewer is from the same model family as the rewriter.** The lab's own
   docstring calls this "a weak check on its own". Every verdict is labelled
   `provisional: true`.
6. **The two word counters disagree.** The CSV columns (app metrics) and the JSON
   `changes[0].stats` give different numbers. For example, T5's median change is
   +31 in the CSV and +77.5 in the JSON, because Markdown table syntax is counted
   differently. This audit quotes the CSV for word change and the JSON for
   similarity.

---

## 5. Instruction artifacts (what the treatments taught the rewriter to do)

The exact templates in `strategies.py` explain several observed behaviours.
Counts come from `recompute_archive_stats.py` (regex counts over output text).

| Pattern | 10 source answers | E3 T2 | E4 T2 | E3 T3 | Cause in the template |
|---|---:|---:|---:|---:|---|
| Signposting ("Now that…", "Building on…", "With X established…") | 0 | 13 | 6 | 0 | T2 step 4: "Add only the connective sentences needed… ('now that X is in place, Y follows')" |
| Meta-commentary ("The source does not specify…") | 0 | 0 | 0 | 8 | T3: "write that the source does not specify it" |
| Causal connectives (because, therefore, causes, …) | 14 | 14 | 14 | 79 | T3 steps 1–4 (expand steps, state causes) |

**Observation.** The clearest T2 change (`transform-tcp-claude-T2.json`, shown in
`examples/candidate-before-after.md`) does two things:

- **Useful:** it moves the constraint ("each side must announce its starting number
  and have it confirmed: four pieces of information collapse into three messages")
  ahead of the three steps. The reader now knows what problem the steps solve
  before seeing them.
- **Not useful:** it opens with "To understand the three-way handshake, we first
  rely on the client-server model, network packets or segments, and reliable
  delivery…". This **names** prerequisites without **teaching** any of them, and
  adds five meta-transitions.

**Observation.** One `candidate-before-after.md` example (databases, ChatGPT) has
similarity 1.000. The before and after texts are identical, so it is unusable for
human review.

**Design consequence (engineering choice).** The Skill keeps T2's ordering
principle but explicitly forbids signposting, naming-without-teaching, and
asserting dependencies that are not real. It keeps T3's causal-chain principle
but forbids meta-commentary and padding with connectives, and it requires hedges
to be preserved.

---

## 6. Evidence matrix

Definitions are quoted or paraphrased from `strategies.py`. "Comprehension
evidence" is **none** for every treatment. That is stated explicitly each time so
that no row reads as if it had some.

### T1

| Property | Description |
|---|---|
| Treatment ID | T1 |
| Treatment name | Vocabulary and sentence clarification |
| Intended mechanism | Reduce lexical and syntactic load: plain equivalents for jargon, define load-bearing terms inline at first use, one claim per sentence, resolve ambiguous references, remove padding. Order and content untouched. |
| Evidence | E3: 7 clean, 1 warning, 2 serious; 0 identical outputs; median +54 words. Changes were mostly acronym expansion and inline definitions. One run replaced the domain term "pathogen" with "disease-causing agent" throughout (`transform-immunology-chatgpt-T1.json`). Both serious verdicts are numeric triggers with no semantic finding. |
| Fidelity risk | Low to moderate. Rewording preserves claims, but replacing technical vocabulary can obscure the terms the learner needs. |
| Comprehension evidence | None. |
| Confidence | Low (fidelity screen only). Literature (L2): cognitive load theory, with the scope limit "reduce load ≠ reduce content". |
| V0 decision | **Conditional.** Folded into one rule: define a load-bearing term at first use when the audience probably lacks it; keep domain terms rather than replacing them; no acronym sprawl. Not a standalone operation. |

### T2

| Property | Description |
|---|---|
| Treatment ID | T2 |
| Treatment name | Prerequisite-aware concept sequencing |
| Intended mechanism | No concept is used before it is introduced. Add the minimum missing prerequisite (1–2 sentences). State mutual dependencies. Add connective sentences. Wording untouched. |
| Evidence | E3: 9 clean / 0 warnings / 1 serious, but 4 clean outputs are unchanged copies. 5 clean outputs changed text: 3 reordered content (TCP Claude, immunology ChatGPT, interest Claude) and 2 only added transitions. E4 second rewriter: 6/10 clean, plus one false "mutually dependent" claim. The single serious E3 verdict (`transform-tcp-chatgpt-T2.json`, similarity 0.446, the largest restructuring) was triggered only by the numbers "3" and "4" occurring less often after two list items were removed. The LLM reviewer found no meaning change. Instruction artifacts: 13 signposting phrases. |
| Fidelity risk | Low when it only reorders. Moderate when it adds bridging content (one false claim in 10 E4 rewrites). |
| Comprehension evidence | None. E5 used T2 variants but had 0 diagnostic items. |
| Confidence | Low. The fidelity record is the best of the six, but inflated by no-ops. Literature (L2): prerequisite structure / knowledge spaces, with the scope limit that model-inferred dependency graphs are hypotheses. |
| V0 decision | **Include (primary), as a hypothesis.** Reformulated for generation: build the dependency order before writing; teach a missing prerequisite in one or two sentences rather than naming it; skip prerequisites the user evidently has; no signposting; never assert a dependency that is not real. |

### T3

| Property | Description |
|---|---|
| Treatment ID | T3 |
| Treatment name | Mechanism and causal explanation |
| Intended mechanism | Turn description into mechanism: explicit ordered steps, causes rather than correlations, how components interact, cause / effect / precondition / exception distinguished, unknowns marked rather than invented. |
| Evidence | E3: 1 clean / 6 warnings / 3 serious; median +212 words (the largest length increase); causal connectives rose from 14 to 79. Warning types: 4× unjustified certainty, 2× omitted caveat, 3× numeric, 2× boundary, 2× new claim. Semantic findings: one corruption ("Alamo-like balances") and one batch of unsourced biological detail. 8 meta-comments, which the template instructed. |
| Fidelity risk | **High in the rewrite setting**: certainty creep, hedge loss, unsupported elaboration, length inflation. Part of this is structural: under a "do not add facts" constraint, adding mechanism is itself flagged. |
| Comprehension evidence | None. |
| Confidence | Low. The lab's literature review cites no learning-science result specific to T3. Inclusion rests on the brief's problem statement ("explaining what something is without explaining why it exists") and is a **hypothesis (L4)**. |
| V0 decision | **Include (primary), bounded.** Used for why/how questions and mechanism-heavy topics only. Guardrails target each observed failure mode: preserve hedges and uncertainty; never invent a mechanism; state an unknown plainly; no meta-commentary; add only the causal links the reader is missing; include the tradeoff or failure consequence that follows from the mechanism; keep a length budget. |

### T4

| Property | Description |
|---|---|
| Treatment ID | T4 |
| Treatment name | Concrete examples and analogies |
| Intended mechanism | Add one realistic worked example and at most one analogy, each mapped explicitly to the concept, with the analogy's breaking point stated; skip when the plan says none is needed. |
| Evidence | E3: 3 clean / 2 warnings / 5 serious, but 2 of the 3 clean are identical copies (1 clean changed output). Serious verdicts come mainly from numbers inside added examples. 3 LLM "new claim" findings, all illustrative detail rather than errors. 2 boundary violations (examples formatted as lists or tables). Median +95.5 words. |
| Fidelity risk | Moderate. Illustrative specifics can be mistaken for facts, and an example's internal logic can contradict the mechanism. |
| Comprehension evidence | None. |
| Confidence | Low. Literature (L2): the worked-example effect, strongest for procedural domains, weaker for conceptual prose, and decaying with expertise. |
| V0 decision | **Conditional.** Use one example when an abstraction is hard to picture or the user asks for one. Prefer a direct technical example over an analogy. Map it to the mechanism explicitly, state where an analogy breaks, keep illustrative numbers visibly illustrative, and check the example obeys the mechanism. |

### T5

| Property | Description |
|---|---|
| Treatment ID | T5 |
| Treatment name | Structural and visual presentation |
| Intended mechanism | Headings that say what each section establishes, short paragraphs, ordered steps for procedures, tables for genuine comparisons, a diagram specification for flows. Wording unchanged. |
| Evidence | E3: 2 clean / 0 warnings / 8 serious. All 8 serious verdicts are numeric triggers (list numbering) with no semantic finding. 0 identical outputs. |
| Fidelity risk | Low for meaning. The serious count is a detector artifact. |
| Comprehension evidence | None. The lab's own hypothesis H3 predicts that presentation raises *perceived clarity* more than comprehension (illusion of fluency, L2). |
| Confidence | Low. |
| V0 decision | **Defer as an operation.** One minimal rule remains: use structure only when the content has that shape (ordered steps, a comparison across shared dimensions). Formatting is never treated as the improvement. |

### T6

| Property | Description |
|---|---|
| Treatment ID | T6 |
| Treatment name | Audience adaptation |
| Intended mechanism | Re-pitch for a learner profile: introduce what they probably don't know, don't explain what they know, adjust unpacking depth, keep facts identical across levels. |
| Evidence | E3: 7 clean / 1 warning / 2 serious, but **6 of the 7 clean outputs are unchanged copies**. The changed outputs mainly reformatted tables (2 boundary violations, 2 numeric triggers). In practice T6 was barely exercised. The archive does not show which learner profile was supplied. |
| Fidelity risk | Low as observed (it mostly did nothing). |
| Comprehension evidence | None. |
| Confidence | Very low (effectively untested). Literature (L2): the expertise reversal effect, under which scaffolding that helps novices can hinder experts. |
| V0 decision | **Conditional, as the calibration layer.** Not a rewrite step. It decides how much of T2 and T3 to apply: infer the audience from the message, skip known prerequisites, and match depth to the request. This guards against the expertise-reversal risk of applying T2 and T3 unconditionally. |

---

## 7. Treatment decisions and why

| Treatment | V0 role | Primary basis |
|---|---|---|
| T2 Prerequisite sequencing | **Core operation** | Brief's problem statement; best (if inflated) fidelity record; L2 prerequisite-structure literature; artifacts are fixable by instruction |
| T3 Mechanism / causal | **Core operation, bounded** | Brief's problem statement; L4 hypothesis only; failure modes are specific and addressable |
| T6 Audience adaptation | **Calibration gate** for T2/T3 | L2 expertise reversal; needed to stop T2/T3 over-applying |
| T4 Examples | **Conditional** | L2 worked-example effect; high misuse risk, so gated |
| T1 Vocabulary | **Conditional rule** (define at first use) | L2 cognitive load; low risk; small scope |
| T5 Structure | **Deferred** (shape-only formatting rule) | Lab H3 predicts fluency illusion; no reason to treat it as an improvement |

Why T2 and T3 and not "all six": the lab's Experiment 2 `pedagogical` prompt
already asks for all of these at once, and it doubled median length with no
discriminating quality measure. Stacking all six operations is the design most
likely to over-expand answers (anti-pattern 5 in the brief) and the one an ablation
can least disentangle.

Why not exclude T3 given its poor fidelity record: E3 measured T3 under a "do not
add content" rewrite constraint, where adding mechanism is partly flagged *by
construction*. In generation, accuracy is measured against facts, not against a
source text. The failure modes that remain relevant (certainty creep, hedge loss,
unsupported detail, length) are turned into explicit guardrails and are measured
in the evaluation (accuracy coding, word counts).

**This selection is a hypothesis to be tested, not a conclusion.** The ablation
design (`evaluation/EVALUATION_PLAN.md` §8) exists to check it.

---

## 8. The rewrite-to-generation transfer assumption

All archived evidence concerns **Gemini rewriting an existing answer**. The Skill
asks **Claude to compose an answer**. Differences that limit transfer:

- No source text exists, so "fidelity" becomes accuracy against world facts. The
  evaluation uses per-case critical facts and misconceptions instead.
- The rewriter was Gemini. The Skill runs on whatever Claude model the user has
  selected.
- E3 applied each treatment unconditionally. The Skill applies operations
  selectively, and selection itself is untested.
- E3 sources were long answers (roughly 290–840 words, depending on which archive word counter is used). The Skill must also handle short
  questions, follow-ups, and non-teaching requests.

---

## 9. Methodological limitations of the archive

1. One rewriter model for E3, and one model family for every stage including the
   reviewer.
2. n = 10 per treatment (5 topics × 2 sources), all at moderate difficulty, 3 of 5
   topics from software engineering.
3. One sample per cell. No variability estimate is possible.
4. The learner profile used for T2/T6 planning is not recorded in the archive.
5. The deterministic detectors are lexical. Verdict counts conflate artifacts
   with errors in both directions (§4).
6. The E5 proxy items are recall-level and were answerable without any text.
7. The judge produced constant scores (per `NEXT_STEPS.md`; unverifiable here).
8. Source answers were copied from web chat with unknown settings.
9. No human reader, no comprehension test, no delayed recall.

## 10. Contradictory or ambiguous results

- **T2 "best fidelity" vs T2 "changes little".** Both are true, and the first is
  partly caused by the second.
- **Rewriter comparison (E4).** The newer rewriter appears safer (9/10 vs 6/10)
  only because 4 of its 9 clean outputs are no-ops. On changed outputs the two
  are similar (5/6 vs 6/10), and n is too small to distinguish them.
- **T5 serious 8/10 vs "pure reformatting" in reviewer notes.** The reviewer notes
  describe faithful reformatting. The verdict comes from list-number detection.
- **E5 "2/3 with quote" for TCP Claude.** This is a quote-matching artifact, not
  a condition difference.
- **Word counts.** Two counters in the archive disagree (§4.6).

## 11. What we still do not know

- Whether any of T1–T6 improves human understanding, retention, or transfer.
- Whether prerequisite ordering helps when it actually changes the text (only 3
  substantive reorders exist).
- Whether mechanism elaboration helps or overloads, and for whom (expertise
  reversal).
- Whether selective application beats unconditional application.
- Whether effects seen in Gemini rewrites transfer to Claude generation.
- Whether a Skill changes behaviour more than an equivalent plain-text prompt.
- How reliably Claude loads the Skill without being asked.

---

## 12. Reproduction

```
python research/recompute_archive_stats.py          # Markdown summary
python research/recompute_archive_stats.py --json   # full data incl. per-group warning counts
```

The script and this audit were checked against each other on 2026-10-26.
