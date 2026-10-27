# Rating Rubric — Explanation Lab V0 evaluation

Raters score each response **blind to condition**. A response appears in the
packet with only its blind ID, the test case's question, any context, and the
assumed audience.

The rubric has four separate instruments. **Never average them into one score.**

| Instrument | What it measures | Filled by | File |
|---|---|---|---|
| A. Dimension scores (11 dimensions, 1–5) | Explanation quality as judged by an informed reader | Blind raters | `RATINGS_TEMPLATE.csv` |
| B. Critical-fact and error coding | Factual accuracy against the case's critical facts | Blind raters | `RATINGS_TEMPLATE.csv` |
| C. Adherence codes | Specific behaviours the skill is meant to avoid | Blind raters | `RATINGS_TEMPLATE.csv` |
| D. Within-case rank | Overall preference among the responses to one case | Blind raters | `RATINGS_TEMPLATE.csv` |

Skill activation is **not** rated here. The operator records it at generation time
(see `RUNBOOK.md`). Comprehension is measured with human learners
(`comprehension/PROTOCOL.md`), not with this rubric. A rater's judgement that an
explanation "seems clear" is not evidence that anyone learned from it.

---

## General rules for raters

1. Read the question, the context, and the assumed audience first. Judge the
   response **for that audience and that request**, not for yourself.
2. Score each response on its own before ranking any of them.
3. **Do not reward length.** A longer answer earns a higher score only if the extra
   content is something this reader needed.
4. **Do not reward formatting outside `navigability`.** Headings, bullets, and
   bold text are not evidence of understanding. On every other dimension, ask
   what the reader would know afterwards.
5. Use the case's `critical_facts`, `common_misconceptions`, and
   `expected_properties` (in the rater sheet) as the reference. If you believe a
   reference fact is wrong, note it in `rater_notes` and score against what is
   true.
6. Use whole numbers. Use 2 and 4 when a response falls between the anchors.
7. Use `NA` only where a dimension says it is allowed.
8. If you recognise the writing style of a condition, do not let that influence
   you. Note it in `rater_notes` so blinding failures can be counted.

### Preference versus comprehension

Dimension scores (A) and within-case ranks (D) are **preference-class**
measures: they record what an informed reader judges better. The critical-fact
coding in §B is the **comprehension-class** measure available in this rubric: it
records what the response actually conveys. Presentation changes are expected to
move the first. A presentation change counts as a **regression** if it moves the
second downward, however much it raises the first. Raters score both, and the
two are never averaged or combined into one number.

---

## A. Dimension scores

### 1. `prerequisite_sequencing`

Are the ideas this reader needs introduced before they are used, without
explaining what the reader already knows?

| Score | Anchor |
|---|---|
| 1 | Central terms or ideas are used before they are introduced, or the answer depends on knowledge this audience clearly lacks. |
| 3 | Mostly well ordered, but one or two ideas arrive before their groundwork, **or** some background is explained that this reader already has. |
| 5 | Every idea rests on something already established or known to this audience. No unneeded background. |

`NA` is allowed for single-fact answers and negative controls.

### 2. `mechanistic_clarity`

For why and how questions: is the cause-and-effect chain explicit?

| Score | Anchor |
|---|---|
| 1 | States *what* without *why* or *how*, or causal claims are vague ("improves performance", "makes it more efficient"). |
| 3 | The main causal link is present, but an intermediate step this reader needs is skipped, **or** the mechanism is padded with steps the reader did not need. |
| 5 | Each causal link the reader needs is stated. The problem the mechanism solves is clear, and the stated consequences follow from it. |

`NA` is allowed when the question needs no mechanism (single facts,
translation, greetings).

### 3. `conceptual_completeness`

Are the ideas needed for a correct, usable understanding present?

| Score | Anchor |
|---|---|
| 1 | The central idea of the question is missing or wrong. |
| 3 | The central idea is present, but an expected property that matters for this question is missing. |
| 5 | Everything this reader needs is present. Not every optional expected property is required. |

### 4. `directness`

Does the response engage the actual question early and stay on it?

| Score | Anchor |
|---|---|
| 1 | The answer is buried, missing, or replaced by a related topic. |
| 3 | Answers the question, but after a preamble, or with tangents the reader must skip. |
| 5 | Engages the question immediately. Every part serves it. |

### 5. `appropriate_depth`

Do the level and length match the audience and any explicit request?

| Score | Anchor |
|---|---|
| 1 | Badly mismatched: a tutorial for an expert, a wall of jargon for a beginner, or an explicit length request ignored. |
| 3 | Roughly right, with stretches that are too deep or too shallow. |
| 5 | Consistently calibrated, and any explicit length or format request is respected. |

### 6. `example_effectiveness`

If the response contains examples or analogies, do they aid understanding?

| Score | Anchor |
|---|---|
| 1 | Examples are decorative, unrelated, internally inconsistent with the mechanism, or misleading. |
| 2 | No example, where one was clearly needed (an abstract idea for a non-expert, or an example was requested). |
| 3 | Relevant example, but the mapping to the concept is left implicit, or an analogy's limits are not stated where they matter. |
| 5 | Apt example, explicitly mapped to the concept, consistent with the mechanism, and limits stated where relevant. |

Use `NA` when the response has no example **and** none was needed.

### 7. `accuracy`

Is everything the response asserts true, with appropriate confidence? Fill in
instrument B first, then use it to choose this score.

| Score | Anchor |
|---|---|
| 1 | At least one **critical error**: contradicts a critical fact, or presents a listed misconception as true. |
| 2 | No critical error, but two or more minor errors. |
| 3 | One minor error, or one claim stated with more certainty than the facts support. |
| 4 | No errors, but some imprecision or a weakened hedge that could mislead slightly. |
| 5 | No errors detected. Uncertainty and conditions are preserved. |

### 8. `cognitive_load`

Is the difficulty intrinsic to the subject rather than added by the writing?
(5 means little added load.)

| Score | Anchor |
|---|---|
| 1 | Heavy added load: avoidable jargon, indirection, several ideas per sentence, padding, or signposting. |
| 3 | Some avoidable density or padding. |
| 5 | All remaining difficulty belongs to the subject itself. |

### 9. `responsiveness_to_intent`

Did the response do what the user actually wanted: the task, the scope, and the
format?

| Score | Anchor |
|---|---|
| 1 | Wrong kind of response, such as a lesson instead of a translation, or a long essay when one sentence was requested. |
| 3 | Right kind of response, but partly misreads the intent, for example by answering a more general question. |
| 5 | Exactly what was asked, including the evident implicit intent. |

### 10. `navigability`

Can this reader find the part of the answer they need without reading it
linearly? Judge whether the form shows the shape of the content, not how much
formatting there is.

| Score | Anchor |
|---|---|
| 1 | An undifferentiated block: several distinct ideas, stages, or items run together with nothing to show where one ends. Or structure that misleads: headings over one-sentence sections, bullets that break a single argument apart. |
| 3 | The main divisions are findable, but one part that has its own shape (a process, a comparison across shared dimensions, a branching flow) is buried in prose, or some structure is decorative. |
| 5 | The structure of the content is visible at a glance, and every heading, list, table, or diagram marks a real division. A short answer that is honestly two sentences of prose scores 5. |

### 11. `register_fit`

Is the technical level matched to this reader?

| Score | Anchor |
|---|---|
| 1 | Invented jargon, unexplained name-drops or foreign terms, or condescension (a children's analogy for an adult, characterising what the reader "really" thinks). |
| 3 | Mostly at the reader's level, but some terms are left unexplained for a beginner, or a practitioner is taught things they evidently know. |
| 5 | The reader's own level throughout: the field's correct terms, explained only where this reader needs it, nothing talked down. |

---

## B. Critical-fact and error coding

For each response, fill in:

| Field | How to fill it |
|---|---|
| `critical_facts_present` | Semicolon-separated IDs of critical facts the response states correctly, explicitly or by clear implication (e.g. `mech_003_cf1;mech_003_cf2`). |
| `critical_facts_contradicted` | IDs of critical facts the response **contradicts**. Contradiction is a critical error. |
| `critical_errors` | Count of critical errors: contradicted critical facts, listed misconceptions stated as true, or other false claims central to the answer. |
| `minor_errors` | Count of false or misleading claims that are peripheral to the answer. |
| `unsupported_certainty` | Count of claims made more absolute than the facts support (e.g. "always", "never", "guarantees"). |

A critical fact that is simply **absent** is neither present nor contradicted.
Absence is handled by `conceptual_completeness`, not counted as an error.

For negative controls, the critical fact is the task's correctness (for example,
the translation is correct).

---

## C. Adherence codes

Record every code that applies in `adherence_violations`, separated by
semicolons, or leave it empty. These codes apply equally to every condition.

| Code | Meaning |
|---|---|
| `SIGNPOST` | Transitions that announce structure ("Now that we've established…", "Let's now look at…"). |
| `META` | Talks about the explanation, its sources, or its own process ("I'll explain this in three steps", "the source does not specify"). |
| `VISIBLE_WORKFLOW` | Displays an internal checklist or diagnosis ("Your question is a 'why' question, so…"). |
| `INTERNAL_LABEL` | Mentions a skill, "operation", treatment ID, or similar internal label. |
| `TEMPLATE_HEADINGS` | Generic What / Why / How / Example headings where the content does not divide that way. |
| `NAMED_NOT_TAUGHT` | Lists prerequisites the reader needs without explaining them. |
| `PADDING` | Restates the question, or ends with a summary repeating the body. |
| `HIJACK` | Adds teaching to a request that did not ask for it. |
| `LENGTH_IGNORED` | Clearly exceeds an explicit length request. |
| `PATRONIZING` | Childish analogies, praise for the question, "simple, right?". |

---

## D. Within-case rank

After scoring every response for a case, rank them in `rank_within_case`: 1 is
the response you would most want this reader to receive, and there are no ties.
Ranking is a preference judgement. It is analysed separately from the dimension
scores.

---

## Rater calibration (before scoring)

1. Each rater independently scores the three calibration responses in the
   calibration packet. These are responses generated during a practice run and
   excluded from analysis.
2. The raters compare scores. Any dimension where raters differ by 2 or more
   points is discussed against the anchors until the reading of the anchor is
   agreed. **Scores are not changed to force agreement.**
3. Record calibration scores. They are not analysed as results.

Inter-rater agreement on the real packet is reported by `summarize_results.py`
(exact agreement, agreement within one point, and mean absolute difference per
dimension). Dimensions with poor agreement should be interpreted with caution or
re-anchored before the next round.
