# Communication grammar

The rules implemented in `skill/socialized/SKILL.md` (displayed as Socialized-Claude) by the
presentation, visual, register, repair, persistence, work-report, plain-language and close
operations, and the accuracy additions, each with its evidence label.
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
7. Plain language
8. Accuracy additions
9. Visuals
10. Closing

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
| End a paragraph at four sentences or about 80 words, and leave a blank line between units. | Hypothesis (L4) | User report (2026-10-27), point 13: dense paragraphs are hard to read. The `dense_paragraph` flag encodes the threshold; `whitespace_padding` still flags the opposite. |
| Number the headings of an answer with three or more sections, and put a one-line map after the answer sentence. | Hypothesis (L4) | User report (2026-10-27), point 7. A scoped exception to the plain-language ban on preview sentences. |
| Move specialist code and identifiers into a fenced block or a **For implementers:** blockquote after the narrative. | Hypothesis (L4) | User report (2026-10-27), point 15. |
| Put the main point first in a section and gather minor caveats at the end; separate major topics with a horizontal rule. | Hypothesis (L4) | User report (2026-10-27), point 16. |
| Wrap every identifier, path, flag, command, and product-specific token in backticks, and gloss it the first time. | Hypothesis (L4) | Second user report (2026-10-27), item 12. |
| Use `##` for a major section and `###` for a subsection, with no skipped level and no bold line standing in for a heading. | Hypothesis (L4) | Second user report, item 14. The `bold_as_heading` flag checks the second half. |
| Put specialist depth in a **Deeper:** or **For implementers:** block, and keep the narrative complete without it. | Hypothesis (L4) | Second user report, item 16. |
| Lift every example, sample, snippet, and quoted structure into its own fenced block under a bold title line. | Hypothesis (L4) | Second user report, item 18. The `uncaptioned_specimen` flag checks a label is present. |
| Tables: at most four columns; each cell one idea, about six words where a phrase will do and a short sentence where the comparison needs one; the header names the dimension. | Engineering choice, from Hypothesis (L4) | Second user report, item 19. The thresholds are a choice; `dense_table_cell` and `wide_table` encode them, and the Phase 4C calibration made the cell length a preference rather than a cap. |
| Give the last section the same paragraph sizes, visuals, and spacing as the first. | Hypothesis (L4) | Second user report, item 7. `visuals_first_half` and `visuals_second_half` describe it and never gate. |
| Failure modes: decorative structure, emoji as decoration, whitespace padding, empty transitional units, a wall of text. | Engineering choice | Encoded as linter flags in `scripts/structural_metrics.py`. The emoji rule is narrowed below. |

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

## 7. Plain language (`op:plain`)

This operation reinstates the sentence-level half of the archive's T1 treatment ("one claim per
sentence, plain equivalents, resolve ambiguous references, remove padding"), which V0 reduced to
defining terms only. Of the six treatments, T1 is the one whose archive record supports it in the
sense this project uses: 7 of 10 rewrites clean, no unchanged (no-op) outputs, both serious
verdicts numeric triggers with no semantic finding (*Observation*, `research/EVIDENCE_AUDIT.md`
§6 T1), plus cognitive-load literature (*Literature (L2)*, same section). That is support for low
fidelity risk, not comprehension evidence.

| Rule | Label | Basis |
|---|---|---|
| Make one claim per sentence. | Hypothesis (L4), with Literature (L2) motivation | T1 template; cognitive load theory, scoped "reduce load ≠ reduce content". |
| Split any sentence carrying more than two clauses. | Engineering choice | Makes "one claim per sentence" checkable; the threshold is a choice. |
| Write in the active voice; passive only when the actor is unknown or irrelevant. | Hypothesis (L4) | Says who does what, which a causal explanation needs. |
| Give every pronoun one clear referent; repeat the noun when two could match. | Hypothesis (L4) | T1 template ("resolve ambiguous references"). |
| Choose the common word when it is exact; keep the technical term when it is not. | Hypothesis (L4), with an Observation of the failure | T1 replaced "pathogen" throughout (`transform-immunology-chatgpt-T1.json`), the case this rule's second half guards against. |
| Delete any sentence whose only job is to introduce the next one, except the one-line section map. | Hypothesis (L4) | T1 template ("remove padding"); the map is the point-7 exception above. |

## 8. Accuracy additions (always apply)

| Rule | Label | Basis |
|---|---|---|
| Give a specific citation only when confident it exists exactly as stated; otherwise describe the finding. | Engineering choice | The addendum quotes Choi (2023) as finding incorrect citations in 69.7% of responses; that study is not in this repository and the figure is second-hand. |
| Gloss any named researcher, paper, or foreign or field term in the same sentence, or omit it. | Hypothesis (L4) | User reports about unexplained name-dropping. |

## 9. Visuals (`op:visual`)

Markdown is the default on every surface. An artifact is built only when the person explicitly
asks for one, and only where the surface can show it (claude.ai). *Engineering choice*, from the
user's instruction on 2026-10-27: markdown everywhere, artifacts on an explicit request.

| Rule | Label | Basis |
|---|---|---|
| Draw one visual for each idea whose content has a shape that would take three or more sentences, and delete those sentences. | Hypothesis (L4) | User report (2026-10-27), points 1, 3 and 5; second report, items 1 and 8. |
| Use the smallest form: an arrow chain, a two-column or diff contrast, a Mermaid block of at most ten nodes, or block-character bars. | Engineering choice | Keeps the token cost to the visual that replaces prose. |
| No per-answer cap. Give the hardest section its visual before any section gets a second, and give the last third at least the support of the first. None in a one- or two-sentence answer or an expert lookup. | Engineering choice | Replaces the earlier "one per section, two per answer" cap (superseded, user decision 2026-10-27). Each visual deletes its prose, so the cost stays flat. |
| Order in time goes in a `sequenceDiagram` with each arrow labelled by its trigger; parallel work is shown as branches with a note. | Hypothesis (L4) | Second user report, item 3. |
| Mark the load-bearing node with a distinct shape; give peers one shared `classDef` class and a different kind of thing its own. | Hypothesis (L4) | Second user report, item 2. The `flat_visual` flag catches a flowchart of four or more nodes with neither. |
| Two states at one moment go side by side: a two-column table or two labelled fenced blocks. | Hypothesis (L4) | Second user report, item 5. |
| One colour code per answer, named once in a legend line and reused in every visual. | Hypothesis (L4) | Second user report, item 6. |
| Every range, ratio, or magnitude comparison becomes bars. | Hypothesis (L4) | Second user report, item 13. |
| Caption every visual with what it shows and the one thing to notice. | Hypothesis (L4) | User report, point 14. The `uncaptioned_visual` flag checks the sentence is present. |
| Mark status only with ✅ ❌ ⚠️ 🟢 🟡 🔴, at least two distinct markers in the same list or table, and name them in the caption. Headings stay words. | Hypothesis (L4) | User report, point 2. Narrows the earlier emoji ban (addendum): legend markers in a list are exempt from `emoji_structure`; a heading is not. Recorded as a deviation. |
| Show change over time as one table row per moment, then end with one line offering an interactive version. | Hypothesis (L4) | User report, point 4; second report, item 4. Markdown cannot be clicked; the offer lets the person opt in to an artifact with one word (user decision 2026-10-27). |
| On an explicit artifact request, build one captioned artifact and keep a short markdown answer. The next reply returns to markdown unless the request was standing. | Engineering choice | User instruction, 2026-10-27. |

`visual_count`, `visuals_first_half`, `visuals_second_half`, `max_table_cell_words` and
`heading_depth_max` are heuristics and never gate, same as `answer_first_offset` and
`passive_sentence_count`.

## 10. Closing (`op:close`) and the running example

| Rule | Label | Basis |
|---|---|---|
| End a long or teaching answer with a takeaway compressed to an arrow chain or one line of 25 words or fewer, written fresh. | Hypothesis (L4) | User report, point 11; second report, item 11. |
| End teaching, beginner, and confusion follow-ups with one verifiable question (three lettered options or one short factual answer), then its answer led by **Answer:**. Quick, practitioner, and expert answers end when the content ends. | Hypothesis (L4) | User report, point 10; second report, items 9 and 10. |
| Carry one example through every section that teaches. For a beginner concept question, sentence one is a concrete situation and sentence two is the answer. | Hypothesis (L4) | User report, points 8 and 12; second report, item 15. |
| For every mechanism, not only the first, name the approach a reader would try first and how it fails. | Hypothesis (L4) | User report, point 17; second report, item 17. |
