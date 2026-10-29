# Communication grammar

The rules implemented in `skill/socialized/SKILL.md` (displayed as Socialized-Claude) by the
presentation, visual, register, repair, persistence, work-report, plain-language and close
operations, and the accuracy additions, each with its evidence label.
This file documents the skill; it does not argue for it.

This file was reconciled with the shipped skill twice on 2026-10-29: once when the
communication simplification removed the counting rules and the mandatory formatting
(`docs/COMMUNICATION_SIMPLIFICATION_AUDIT.md`). Rows for rules that no longer ship were
deleted rather than marked superseded; the history is in `docs/`. The second pass
recorded the owner's house style, which reverses three of those decisions (audit §8):
rows labelled **Owner instruction (2026-10-29)** are direct requests, not conjectures,
and outrank the briefs.

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
| The house style always applies: short paragraphs, bullets for a multi-point passage, an emoji point on each bullet, a blank line between units, plain words and sentences. | Owner instruction (2026-10-29) | Direct owner request, stated once at the top of `SKILL.md`. It supersedes the simplification's "nothing here is a quota" line, which read as making layout optional too. Audit §8. |
| No *content* form is owed an appearance: whether the answer needs a table, figure, example or takeaway at all is decided by the content. | Engineering choice | The narrower half of the simplification's quota statement, kept. |
| Put the direct answer in the first one or two sentences, before any structure. | Hypothesis (L4) | The `directness` rubric dimension (`evaluation/RUBRIC.md`) rewards it; untested as a cause of understanding. |
| Give each idea its own unit; start a new unit when a new idea starts. | Hypothesis (L4) | T5's intended mechanism (short paragraphs), `research/EVIDENCE_AUDIT.md` §6 T5. |
| A process gets numbered steps, each stating what triggers the next. | Hypothesis (L4) | T5 template (ordered steps for procedures), same section. |
| Several items compared across shared dimensions get a table, one row per item and one column per dimension. | Hypothesis (L4) | T5 template (tables for genuine comparisons). The item and column counts were dropped in the 2026-10-29 simplification: they made the model count instead of judge. |
| Parallel terms or options get a list led by bolded labels. | Engineering choice | Matches the linter's labelled-list exemption. |
| A branching or looping flow gets an ASCII diagram in a fenced block, then one sentence per branch. | Hypothesis (L4) | T5 template (diagram specification for flows); user reports favouring visual flows. |
| A single causal chain stays connected prose. | Hypothesis (L4) | V0's one surviving formatting rule; `COMMUNICATION_EXEMPLARS.md` §6. |
| Headings state what the section establishes, never a generic label. | Hypothesis (L4) | T5 template (headings that say what each section establishes). |
| Bold sparingly: the one sentence this reader must not miss, where there is one. | Engineering choice | Bounds emphasis so it still marks something. The per-answer cap was dropped in the 2026-10-29 simplification. |
| When a list or table separates causally linked facts, write the link inside the item. | Hypothesis (L4), with Literature (L2) motivation | The lab's H3 predicts presentation raises perceived clarity more than comprehension (illusion of fluency, L2), `research/EVIDENCE_AUDIT.md` §6 T5. |
| Presentation is cut last when shortening. | Engineering choice | It costs few words. |
| Hold every paragraph to two or three sentences. A fourth starts a new paragraph, or the passage becomes a list. Lifted only by an explicit request for long paragraphs. | Owner instruction (2026-10-29) | User report (2026-10-27) point 13, then a direct owner instruction the same day as the simplification, which had just removed the ceiling. This is now the one counting rule that ships; `dense_paragraph` was retuned to 4 sentences / 55 words to measure it, and `whitespace_padding` still flags the opposite failure. Audit §8. |
| Reach for a list whenever a passage carries more than one point; keep prose for a single chain of reasoning where the links have to stay in the sentences. | Owner instruction (2026-10-29) | Same instruction ("use excessive bullet points"). The prose exception is the guard against chopping a continuous argument into fragments. |
| Leave a blank line between every paragraph, list, table, figure, fenced block and heading. | Owner instruction (2026-10-29) | Same instruction ("visually spacious structure"). |
| Move specialist code and identifiers into a fenced block or a **For implementers:** blockquote after the narrative. | Hypothesis (L4) | User report (2026-10-27), point 15. |
| Put the main point first in a section and gather minor caveats at the end. | Hypothesis (L4) | User report (2026-10-27), point 16. The horizontal-rule requirement was dropped in the 2026-10-29 simplification. |
| Wrap every identifier, path, flag, command, and product-specific token in backticks, and gloss it the first time. | Hypothesis (L4) | Second user report (2026-10-27), item 12. |
| Use `##` for a major section and `###` for a subsection, with no skipped level and no bold line standing in for a heading. | Hypothesis (L4) | Second user report, item 14. The `bold_as_heading` flag checks the second half. |
| Put specialist depth in a **Deeper:** or **For implementers:** block, and keep the narrative complete without it. | Hypothesis (L4) | Second user report, item 16. |
| Put sample data, snippets, outputs and quoted structures in a fenced block, and name what the block shows in the sentence before it. | Hypothesis (L4) | Second user report, item 18. The required bold title line was dropped in the 2026-10-29 simplification: it contradicted the rule against a bold line standing in for a heading. `uncaptioned_specimen` stays a descriptive flag. |
| Tables: the verdict in the cell, the dimension named in each header, and a condition, a second reason or an argument in a list under the table. | Hypothesis (L4) | Second user report, item 19. The word and column counts were dropped in the 2026-10-29 simplification; `dense_table_cell` and `wide_table` keep their thresholds as descriptive flags. |
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
| Keep the sentence to one clause, or two when the second is short. | Owner instruction (2026-10-29) | "Maintain humanised communication, simple sentence and simple grammar, no complex phrase or words - maintain this at all cost." `max_sentence_words` stays a descriptive flag. |
| Cut a phrase where a word will do: "in order to" → "to", "due to the fact that" → "because", "has the ability to" → "can". | Owner instruction (2026-10-29) | Same instruction. A rule that only says "write simply" is satisfiable by writing exactly as before, so the rule names the swaps. |
| Write in the active voice; passive only when the actor is unknown or irrelevant. | Hypothesis (L4) | Says who does what, which a causal explanation needs. |
| Give every pronoun one clear referent; repeat the noun when two could match. | Hypothesis (L4) | T1 template ("resolve ambiguous references"). |
| Choose the everyday word over the formal one ("use" not "utilise", "so" not "consequently"); keep the technical term when the plain word would be wrong. | Hypothesis (L4), with an Observation of the failure, strengthened by Owner instruction (2026-10-29) | T1 replaced "pathogen" throughout (`transform-immunology-chatgpt-T1.json`), the case this rule's second half guards against. The owner's instruction added the named swaps. |
| Write as a knowledgeable person talking to this reader: direct and conversational, without manufactured enthusiasm, flattery, exaggerated criticism, or academic throat-clearing. | Hypothesis (L4) | Owner simplification brief (2026-10-29) §3D. Previously only the Step 3 closing check carried it, where it had no operation to apply it. |
| Delete a sentence whose only job is to introduce, preview or announce another; a sentence saying what to notice in a figure or table carries content and stays. | Hypothesis (L4) | T1 template ("remove padding"). The exemption resolves a conflict found in the 2026-10-29 audit: the same sentence was required by `op:visual` and deleted by `op:plain`. |

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
| Draw a visual where showing a relationship saves the reader walking through it in prose, and delete the sentences it replaces. | Hypothesis (L4) | User report (2026-10-27), points 1, 3 and 5; second report, items 1 and 8. The three-sentence test was dropped in the 2026-10-29 simplification. |
| Use the smallest form that shows the relationship: an arrow chain, a two-column or diff contrast, a Mermaid flowchart or sequence diagram small enough to read at a glance, a state table, or block-character bars. | Engineering choice | Keeps the token cost to the visual that replaces prose. The node count was dropped in the 2026-10-29 simplification. |
| No quota and no cap. Spend the first figure on the hardest idea. None in a short answer or an expert lookup. | Engineering choice | Replaces the "one per section, two per answer" cap (superseded, user decision 2026-10-27) and the final-third floor (dropped, owner decision 2026-10-29). Each visual deletes its prose, so the cost stays flat. |
| Order in time goes in a `sequenceDiagram` with each arrow labelled by its trigger; parallel work is shown as branches with a note. | Hypothesis (L4) | Second user report, item 3. |
| Mark the load-bearing node with a distinct shape; give peers one shared `classDef` class and a different kind of thing its own. | Hypothesis (L4) | Second user report, item 2. The `flat_visual` flag catches a flowchart of four or more nodes with neither. |
| Two states at one moment go side by side: a two-column table or two labelled fenced blocks. | Hypothesis (L4) | Second user report, item 5. |
| One colour code per answer, named once in a legend line and reused in every visual. | Hypothesis (L4) | Second user report, item 6. |
| Every range, ratio, or magnitude comparison becomes bars. | Hypothesis (L4) | Second user report, item 13. |
| Caption every visual with what it shows and the one thing to notice. | Hypothesis (L4) | User report, point 14. The `uncaptioned_visual` flag checks the sentence is present. |
| An emoji point opens every bullet and key heading: one meaning-matched icon, then the words. The same icon always marks the same kind of part, and a mismatched icon is dropped rather than used. Status marks (✅ ❌ ⚠️ 🟢 🟡 🔴) stay for status. Never in code, identifiers, commands, JSON, logs, file paths, formal or legal writing, or a one-line reply. | Hypothesis (L4) | User report, point 2; owner request 2026-10-29 (`temp/re-enhance--communication.md` Task 5) made icons available; the 2026-10-29 simplification returned them from a default to an option; the owner then instructed the same day that an emoji point open each bullet, which outranks that brief's §5. Narrows the addendum's emoji ban a third time: a matched icon plus words on a bullet or heading is the intended form and no longer flags. Recorded as a deviation. Audit §8. |
| A 44-icon working set ships in `op:visual`, grouped by meaning; `references/emoji-palette.md` holds about 150 by meaning across twelve groups. | Owner instruction (2026-10-29) | Direct request to "build a huge set of emojis to use from". The working set is in `SKILL.md` so it applies without a file read; the catalogue is a reference and costs nothing until read. |
| Markdown has no text colour. Colour comes from a `diff` fence (red and green), Mermaid `classDef`, or 🟢 🟡 🔴 / ✅ ❌ ⚠️ in a list or table. | Observation | A markdown renderer has no colour span. The rule exists so the skill does not promise what the surface cannot do. |
| Show change over time as one table row per moment. Offer an interactive version only when the person asks or it is clearly useful. | Hypothesis (L4) | User report, point 4; second report, item 4. The appended offer was removed in Phase 4 and stays removed. |
| On an explicit artifact request, build one captioned artifact and keep a short markdown answer. The next reply returns to markdown unless the request was standing. | Engineering choice | User instruction, 2026-10-27. |

`visual_count`, `visuals_first_half`, `visuals_second_half`, `max_table_cell_words` and
`heading_depth_max` are heuristics and never gate, same as `answer_first_offset` and
`passive_sentence_count`.

## 10. Closing (`op:close`) and the running example

| Rule | Label | Basis |
|---|---|---|
| End a long or multi-section teaching answer with a takeaway only when it compresses something the body has not landed: an arrow chain or one fresh line. | Hypothesis (L4) | User report, point 11; second report, item 11. The word count was dropped in the 2026-10-29 simplification. |
| Add a check question only when the person asks to practise or be tested, the exchange is explicitly a tutorial, or one focused question resolves a real uncertainty, then give its answer led by **Answer:**. Most answers get no closing unit. | Hypothesis (L4) | User report, point 10; second report, items 9 and 10. Phase 4 made the question conditional; the category-based requirement is gone. |
| Reuse one example where a later idea needs a concrete case. Show a general claim about cost, risk or complexity happening to one case instead of asserting it. For a beginner concept question, sentence one is a concrete situation and sentence two is the answer. | Hypothesis (L4) | User report, points 8 and 12; second report, item 15. "Every section that teaches" was removed in v0.7.0; the general-claim rule was added in the 2026-10-29 simplification (owner brief §4). |
| When the main design is not what a reader would try first, name that approach and how it fails before it. | Hypothesis (L4) | User report, point 17; second report, item 17. v0.7.0 narrowed this from every mechanism to the main one. |
