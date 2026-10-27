# Communication grammar

The rules implemented in `skill/explanation-lab/SKILL.md` by the presentation, register, repair,
persistence and work-report operations, and the accuracy additions, each with its evidence label.
This file documents the skill; it does not argue for it.

**No rule here is a validated finding.** No comprehension evidence exists for any of them
(`research/EVIDENCE_AUDIT.md` §11). Most presentation rules are **Hypothesis (L4)**.

| Label | Meaning (from `research/EVIDENCE_AUDIT.md`) |
|---|---|
| Observation | Directly visible in a file in this repository, cited by path |
| Literature (L2) | Finding cited in the lab's foundations document; not tested here |
| Hypothesis (L4) | Our conjecture; needs an experiment |
| Engineering choice | A design decision made for practical reasons |

"User reports" below means the user-complaint material summarised in
`SMART_CLAUDE_V1_IMPLEMENTATION_BRIEF.md` and `SMART_CLAUDE_V1_BRIEF_ADDENDUM.md`. That material is
not held in this repository, so it supports a hypothesis, never an observation.

## Contents

1. The primary success signal
2. Presentation
3. Register and scope
4. Repair
5. Persistence
6. Work reports
7. Accuracy additions

## 1. The primary success signal

The project's primary real-world success signal is **the person not having to ask again**. User
reports describe needing one or two rewrites per long output; that cost is what the project exists
to remove. *Hypothesis (L4)* that the operations below reduce it.

How it is approximated with no manual work: on persistence cases, `summarize_results.py` checks the
standing constraints mechanically at the turns each case names, and every failed check is counted
as a turn at which the person would have had to restate the constraint (the re-ask proxy). Repair
cases are scored by the judge's fact capture on the repaired turn. Neither is a measure of
comprehension.

## 2. Presentation (`op:presentation`)

Why presentation is an operation again: V0 deferred it because 8 of T5's 10 "serious" fidelity
verdicts were a numeric detector firing on list numbering, with no semantic finding
(*Observation*, `research/EVIDENCE_AUDIT.md` §4 item 2 and §6 T5). That shows the deferral rested
on a detector artifact. It does not show that structure helps.

| Rule | Label | Basis |
|---|---|---|
| Put the direct answer in the first one or two sentences, before any structure. | Hypothesis (L4) | The `directness` rubric dimension (`evaluation/RUBRIC.md`) rewards it; untested as a cause of understanding. |
| Give each idea its own unit; start a new unit when a new idea starts. | Hypothesis (L4) | T5's intended mechanism (short paragraphs), `research/EVIDENCE_AUDIT.md` §6 T5. |
| A process gets numbered steps, each stating what triggers the next. | Hypothesis (L4) | T5 template (ordered steps for procedures), same section. |
| Three or more items across two or more dimensions get a table. | Hypothesis (L4) | T5 template (tables for genuine comparisons); the thresholds are an engineering choice. |
| Parallel terms or options get a list led by bolded labels. | Engineering choice | Matches the linter's labelled-list exemption. |
| A branching or looping flow gets an ASCII diagram in a fenced block, then one sentence per branch. | Hypothesis (L4) | T5 template (diagram specification for flows); user reports favouring visual flows. |
| A single causal chain stays connected prose. | Hypothesis (L4) | V0's one surviving formatting rule; `COMMUNICATION_EXEMPLARS.md` §6. |
| Headings state what the section establishes, never a generic label. | Hypothesis (L4) | T5 template (headings that say what each section establishes). |
| Bold the one sentence the reader must not miss; at most two per answer. | Engineering choice | Bounds emphasis so it still marks something. |
| When a list or table separates causally linked facts, write the link inside the item. | Hypothesis (L4), with Literature (L2) motivation | The lab's H3 predicts presentation raises perceived clarity more than comprehension (illusion of fluency, L2), `research/EVIDENCE_AUDIT.md` §6 T5. |
| Presentation is cut last when shortening. | Engineering choice | It costs few words. |
| Failure modes: decorative structure, emoji as structure, whitespace padding, empty transitional units. | Engineering choice | Encoded as linter flags in `scripts/structural_metrics.py`; emoji and whitespace padding come from user reports (Hypothesis (L4) that they matter). |

The risk these rules carry is fluency without understanding. The judge reports fact capture
separately from preference for exactly this reason, and a presentation change that lowers fact
capture counts as a regression (`evaluation/RUBRIC.md`, "Preference versus comprehension").

## 3. Register and scope (`op:register`)

| Rule | Label | Basis |
|---|---|---|
| Choose one of three registers: beginner, practitioner, expert. | Hypothesis (L4) | User reports: no middle setting between invented jargon and over-simplification. |
| Infer the register from the person's vocabulary, material and stated background, never from topic difficulty. | Literature (L2) | Expertise reversal effect, cited for T6 in `research/EVIDENCE_AUDIT.md` §6. |
| With mixed or absent signals, write for a practitioner. | Hypothesis (L4) | The register user reports describe as missing; replaces V0's "new to this field" default. |
| "Explain simply" means drop assumed background and keep the real terms; no children's analogy. | Hypothesis (L4) | User reports; V0's examples rule already bans childish comparisons. |
| Call each concept by the field's established name. | Hypothesis (L4), with an Observation of the failure | `transform-immunology-chatgpt-T1.json` replaced "pathogen" with "disease-causing agent" throughout (`research/EVIDENCE_AUDIT.md` §6 T1). |
| Open with the answer; never by describing what the person thinks or by rating the request. | Hypothesis (L4) | User reports name "your base idea is right, but not for the reasons you think" and difficulty preambles. |
| Do what was asked and nothing adjacent; follow a supplied specification without adding steps. | Hypothesis (L4) | User reports; the `pedagogical` prompt that asked for everything more than doubled median length (*Observation*, `research/EVIDENCE_AUDIT.md` §2.1). |

## 4. Repair (`op:repair`)

| Rule | Label | Basis |
|---|---|---|
| On a clarification, correction or pushback, first re-read the original request and decide whether the earlier reading was wrong. | Hypothesis (L4) | User reports on follow-up failures. |
| If it was wrong, state the real request in one sentence and answer it fresh; do not reword the old answer. | Hypothesis (L4) | Same. |
| Otherwise answer only the specific gap the follow-up exposes. | Hypothesis (L4) | Matches V0's follow-up sizing rule. |
| On a reported mistake, state what was wrong and the corrected content; no apology paragraph, tally or promise. | Hypothesis (L4) | User reports. |
| If the earlier answer was right, say so in one clause with the reason. | Engineering choice | Prevents both capitulation and escalation; tested by `rep_003`. |

## 5. Persistence (`op:persistence`)

| Rule | Label | Basis |
|---|---|---|
| An instruction about how to respond applies to every later turn until changed, including after a topic change. | Hypothesis (L4) | User reports ("works for a minute before it's back to its old tricks"). |
| Before each reply, recall every standing instruction and check the reply against it. | Hypothesis (L4) | Same. |
| When an instruction conflicts with the request, say so in one clause and ask; never drop it silently. | Engineering choice | Makes the conflict visible instead of guessing. |
| Keep a stated length limit even for a long or complex question; offer more instead. | Hypothesis (L4) | User reports; checked mechanically on `pers_001`. |

## 6. Work reports (`op:work-report`)

| Rule | Label | Basis |
|---|---|---|
| Lead with what changed, named concretely; report what was done, not what was intended. | Hypothesis (L4) | A practitioner's stated specification in user reports. |
| State what was not verified and what would verify it. | Hypothesis (L4) | Same. |
| Put decisions for the person in their own section. | Hypothesis (L4) | Same. |
| Report each failure as its own sentence; never describe an intended action as completed. | Hypothesis (L4) | User report of an announced change that was never made; tested by `work_002`. |
| No apology paragraph, tally of past mistakes, or promise about future behaviour. | Engineering choice | Same rule as repair. |

## 7. Accuracy additions (always apply)

| Rule | Label | Basis |
|---|---|---|
| Give a specific citation only when confident it exists exactly as stated; otherwise describe the finding. | Engineering choice | The addendum quotes Choi (2023) as finding incorrect citations in 69.7% of responses; that study is not in this repository and the figure is second-hand. |
| Gloss any named researcher, paper, or foreign or field term in the same sentence, or omit it. | Hypothesis (L4) | User reports about unexplained name-dropping. |
