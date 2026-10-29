# Communication simplification audit

Policy 0.9.0, plugin 0.10.0. 2026-10-29.

§1–§7 are the simplification. **§8 is an addendum recording the owner's house-style
instruction later the same day, which deliberately reverses three of the decisions
below.** Read §8 before treating §1–§7 as current.

Six rounds of communication work (Phase 4, Phase 4C, its calibration, v0.5.0
recovery, v0.6.0 experience upgrade, v0.7.0 priority correction) each diagnosed a
real fault and each answered it by writing more instruction text. This round
removes instead. No operation was added, no module was added, and the rule count
went down in every file that holds rules.

What this report does not establish: that answers became easier to read. Every
finding below is about the instruction text, not about model behaviour. §7 lists
what only a real conversation can settle.

---

## 1. What was wrong

### 1.1 The same rule existed in four places, in four wordings

Each rule had a home in `skill/socialized/SKILL.md` and a restatement in
`communication/core.md`, `communication/controls.md` and
`skill/socialized/references/treatment-selection.md` §1. The restatements were
written to "index" the skill, but each round edited them at a different rate, so
the copies drifted.

**Verified.** The table-cell rule is the clearest case. At the start of this round:

| File | What it said |
|---|---|
| `SKILL.md` `op:presentation` | "one idea, about six words where a phrase will do and a short sentence where the comparison needs one" |
| `communication/controls.md` | "a phrase where one will do, a short sentence where the comparison needs one" (no word count) |
| `references/treatment-selection.md` §4 | "An argument in a cell … more than four columns" |
| `COMMUNICATION_GRAMMAR.md` | "at most four columns; each cell one idea, about six words …" |

`COMMUNICATION_GRAMMAR.md` had drifted furthest. It still documented five rules
that had been removed from the skill in v0.5.0–v0.7.0: numbered headings with a
one-line map, "give the last section the same paragraph sizes as the first",
"carry one example through every section that teaches", "for every mechanism, not
only the first, name the approach a reader would try first", and a closing check
question for every teaching, beginner and confusion answer. A reader auditing the
policy from that file would have found rules the skill no longer contains.

### 1.2 Rules told the model to count

**Verified.** Shipped in `SKILL.md` at the start of this round: four sentences or
80 words per paragraph, about 25 words per list item, about six words per table
cell, at most four columns, Mermaid flowcharts of ten nodes or fewer with labels
of four words or fewer, arrow chains for four steps or fewer, takeaways of 25
words or fewer, at most two bold sentences per answer, a visual where prose "would
take three or more sentences", a table for "three or more items across two or more
dimensions", and a horizontal rule and heading numbers at three or more sections.

Eleven thresholds is a budget the model has to track while also answering the
question. None of them was evidence-based: `COMMUNICATION_GRAMMAR.md` labels them
*Engineering choice* or *Hypothesis (L4)*, and `research/EVIDENCE_AUDIT.md` §11
records that no comprehension evidence exists for any presentation rule.

### 1.3 Four pairs of instructions contradicted each other

**Verified** by reading the shipped text:

| Conflict | Where |
|---|---|
| "Lift every example … into its own fenced block **under a bold title line**" against "a heading wherever **a bold line would announce a section**" | both in `op:presentation` |
| "**Delete every sentence** whose only job is to introduce, preview, announce" against "**Write one sentence before each visual** that names what it shows" | `op:plain` against `op:visual` |
| "Give each distinct part of a multi-part answer **a heading**" against "Do not force a heading over a one-sentence section" | `op:presentation` against `controls.md` and the failure modes |
| "Open with the answer … **before any heading**" against "**Number the headings**… and add a one-line map" | Step 2 against `op:presentation` |

The second pair is the likely mechanism behind the repeated complaint of
diagram/prose repetition. One rule demanded a sentence beside every figure and
another deleted sentences that announce; the stable way to satisfy both is to
write a sentence that restates the figure's content, which is exactly the
repetition v0.5.0, v0.6.0 and v0.7.0 each tried to rule out.

### 1.4 Optional capabilities had been promoted to defaults

**Verified.** v0.7.0 made a meaning-matched icon "the **default** on key headings,
callouts and labels of a substantive explanation" after v0.6.0's selective version
did not appear in the owner's test answers. That is the "every heading must contain
an emoji" shape the simplification brief rules out (§5). The same pattern had
already run once on visuals: Phase 4C restored a per-shaped-idea visual
requirement, its calibration softened it to a preference, and v0.7.0 replaced the
coverage floor with a value test.

**Hypothesised, not verified:** that the promotion is why the icons still did not
appear. An instruction that is simultaneously a default and carries five
exclusions ("never in code, JSON, formal or casual replies", "no quota") is
ambiguous about whether any given heading qualifies. Ambiguity, not absence, is
the plausible cause — but nothing in this repository can distinguish the two.

### 1.5 The test suite was the ratchet

**Verified.** Five test files — `test_refinement_policy.py` (Phase 4),
`test_visual_restoration.py` (Phase 4C), `test_communication_recovery.py`
(v0.5.0), `test_communication_experience.py` (v0.6.0),
`test_communication_priority.py` (v0.7.0), 1,336 lines in all — each asserted the
exact wording its own round had written. `test_visual_restoration.py` asserted the
literal string `"Prefer a visual"`; `test_skill_structure.py` asserted
`"bold title line"`, `"six words"` and `"four columns"`; several asserted rule
counts as minimums (`len(rules) >= 8`), which pass by adding a rule and fail by
merging two.

The consequence is structural: with the previous round's phrasing frozen, the
cheapest way to change behaviour was to add text beside it. Six rounds of
additive edits is what that incentive produces.

### 1.6 Step 3 grew one line per round

**Verified.** The pre-send checklist reached nine marker-gated checks plus three
global ones, several of which asked about rule compliance ("Does any table cell
stay scannable, with its argument under the table, and is every unit set off by a
blank line?") rather than about the draft a reader would receive.

---

## 2. What changed

### 2.1 `skill/socialized/SKILL.md`

| Change | Detail |
|---|---|
| One statement about quotas, up front | "Nothing here is a quota. No answer owes the reader a table, a figure, a heading, an icon, an example or a takeaway. The content's shape decides, every time." It replaces the escape clause each round had bolted onto its own rule. |
| Every counting rule removed | All eleven in §1.2. Paragraphs are now "one idea per paragraph, and a paragraph that has taken on a second one splits"; tables are "the verdict in the cell, the dimension named in each header"; a Mermaid flowchart is "small enough to read at a glance". |
| Four contradictions resolved at source | The bold title line is gone (the block is named in the sentence before it); `op:plain` now exempts a sentence that says what to notice in a figure; a one-sentence section explicitly needs no heading; heading numbers and the mandatory horizontal rule are gone. |
| Icons returned to optional | One rule, in `op:visual`, holding both the navigation icons and the status markers: "Optional, where it genuinely helps the reader navigate or compare … Neither is ever required, and neither belongs on every heading or every item." The full vocabulary stays. |
| Concrete demonstration added | `op:examples`: "When a claim is a general property — complexity, cost, risk, latency, failure — show it happening once instead of asserting it: the situation, what the mechanism does, and what the reader is left with." This is the owner brief §4 requirement, and it replaced two overlapping bullets rather than adding a twelfth. |
| Conversational register made an instruction | `op:plain`: "Write as a knowledgeable person talking to this reader: direct and conversational, without manufactured enthusiasm, flattery, exaggerated criticism, or academic throat-clearing." Previously this existed only as the last line of Step 3, where no operation applied it while drafting. |
| Step 3 halved | Nine checks down to seven, each about the draft rather than about a rule. The two global ones do the work the per-operation checks were splitting: "does every part do a job nothing else does" and "could the reader find the answer, then the reasoning, without re-reading". |
| Scope moved up | "Return a requested deliverable … without wrapping it in explanation" now sits in the Scope section, where the decision is made, instead of at the end of the strategy list. |

Activation cost: **6035 → 5648** local-estimate tokens (−6.4%), back below the
Phase 4 baseline of 5966 for the first time since Phase 4C, with no rule moved to
an on-demand reference. `scripts/token_budgets.json` `activation.max` lowered
6150 → 5750.

### 2.2 `skill/socialized/references/treatment-selection.md`

§1 "Selection defaults" deleted: it restated, for each of the twelve operations,
the "Use this for…" sentence already at the top of that operation in `SKILL.md`.
The file now opens by saying it does not repeat that. §4 failure modes were
grouped under five named headings and cut from about sixty entries to those that
carry something a rule does not — a named failure, an observed case, or a
measurement ("in one experiment this added about 40% to typical length"). One
failure mode was added, from the owner brief §4: "An abstract argument left
abstract."

### 2.3 `communication/core.md`, `strategies.md`, `controls.md`

Rewritten as indexes. Each entry names what the model does and points to the one
place in `SKILL.md` that states the rule, so there is no second wording to drift.
The eleven core principles, the five strategies, the across-turns cases and the
control categories all survive as structure — they are the surfaces the Phase 1
brief requires — but they no longer carry their own version of the rule text.
Together the three files fell from 5,117 to 3,837 local-estimate tokens.

`communication/README.md` held one change-summary table per round, 4,121
tokens of history duplicating the reports in `docs/`. It is now a map, a
versioned one-line-per-round table, and pointers to those reports.

### 2.4 `COMMUNICATION_GRAMMAR.md`

Reconciled with the shipped skill. Rows for the five rules found in §1.1 that no
longer ship were deleted; the rows whose rules changed now state the current rule
and say what was dropped and when. Two rows were added: the no-quota statement
and the conversational-register rule.

### 2.5 Tests

The five round-specific files were deleted and replaced by one
`tests/test_communication_policy.py` (31 tests, 412 lines) organised around invariants
rather than round phrasings:

- **A. Nothing is a quota** — no counting rule appears in the skill or its
  references; the no-quota statement is made once; no form is mandatory; icons are
  optional; visuals have no quota and no cap; closings stay conditional; artifacts
  and interactive offers stay opt-in.
- **B. One source per rule** — the modules declare themselves indexes, carry no
  threshold the skill has dropped, and the reference does not restate the
  operation triggers.
- **C. Rules name actions** — every operation bullet names an action; every Step 3
  check is a question about the draft; Step 3 has at most nine checks.
- **D. Behaviour that must survive** — the twelve accuracy requirements, the
  always-on diagram-accuracy rule under the zero-operation build, general claims
  shown rather than asserted, the five strategies and their leads, the scope gate,
  figure/table/prose jobs, table verdicts, the depth layer, both resolved
  contradictions, conversational register, the multi-turn operations, and the
  12-operation / 15-variant contract.
- **E. Both installs agree** — the ZIP and the plugin tree carry the rendered
  source, and activation stayed below the Phase 4 baseline.

§4 lists what each deleted file asserted and where that assertion now lives.

---

## 3. What was deliberately preserved

**The twelve operations and fifteen ablation variants.** The simplification brief
invited reconsidering them. They were examined and kept, for a reason other than
their existing: six of the twelve (`sequencing`, `mechanism`, `examples`, `terms`,
`presentation`, `register`) map to the treatments the archive study separates, and
each of the fifteen variants is a planned arm of the evaluation sweep
(`scripts/skilllib.py` `VARIANTS`, `evaluation/`). Merging two headings would
remove no instruction — the complexity was the rule text inside the operations and
the four-way duplication around them, which is what this round removed. Candidates
considered and rejected: `terms` into `register` (both are reader-level, but
`terms` is a studied treatment and `register` is not), `sequencing` into
`mechanism` (the study separates them), `close` into `presentation` (different
levels; `close` is where the no-mandatory-quiz rule lives).

**Everything the accuracy rules require.** All twelve requirements survive, with
their wording tightened but nothing dropped: hedges, product scoping, the general
mechanism before one system's version, the settings a guarantee depends on,
acknowledgement and durability assumptions, an assumed workload stated once,
citation discipline, conversation continuity, and the rule holding every arrow in
a figure to the same standard as a sentence. `test_communication_policy.py`
asserts each one, and asserts that diagram accuracy survives the zero-operation
build so no ablation can remove it.

**The drawing grammar.** `op:visual` keeps arrow chains, Mermaid `flowchart` and
`sequenceDiagram`, side-by-side state blocks, `diff` fences, block-character bars,
state tables, `classDef` classes and the one-colour-code rule. Phase 4B's Option B
(moving this to an on-demand reference) stays rejected for the reason recorded
then: a reference that is not read drops owner-set visual rules.

**Markdown by default and artifacts on explicit request.** Unchanged.

**The five intent strategies**, their leads, and form-from-content in every
strategy, not only teaching replies.

**Packaging and installation.** No change to `package_skill.py`,
`build_plugin.py`, the four-file skill layout, the ZIP names, the marketplace
entry or either install path. No new dependency, no API, no service.

---

## 4. Tests removed, and where their assertions went

| Deleted file | Assertions kept | Assertions dropped, and why |
|---|---|---|
| `test_refinement_policy.py` (248 lines) | Quizzes, previews, demo offers and artifacts stay conditional; accuracy rules scope implementation and concurrency; diagram claims are scoped; the quick answer is not a rigid cap; both installs ship the policy | "No new operation marker or variant" and the line budgets duplicate `test_skill_structure.py`; `test_section_preview_is_optional` asserted the removed numbered-heading exception |
| `test_visual_restoration.py` (411 lines) | No visual or formatting quota; redundancy rules; short answers get sentences; strategies pick the form; no word cap on the explanation; accuracy rules; multi-turn operations survive; the contract; rules name actions | Every assertion of a Phase 4C phrasing the calibration or v0.7.0 had already superseded: `"Prefer a visual"`, the three-sentence cue, "even across the answer", the horizontal-rule requirement, paragraph and list-item word counts, and `test_policy_readme_records_the_regression_and_the_fix` (that README no longer holds per-round tables) |
| `test_communication_recovery.py` (258 lines) | Table verdict and reasoning placement; decisions lead with the recommendation; assumed scale stated once; figure and text have different jobs; general mechanism before a labelled system version; the depth layer names specialist depth; the example reaches the behaviour in question | "Table cells still have no absolute word limit" (no cell rule has a limit to check); the Step 3 wording checks, now covered by the two global checks |
| `test_communication_experience.py` (263 lines) | Table cells make the decision visible; visual forms include architecture diagrams; the status legend survives; examples trace state → action → result | The 80-word ceiling assertion; `test_semantic_icons_are_navigation_not_decoration`, which asserted the default this round removed; the internal-hierarchy phrasing, merged into Step 2 in v0.7.0 |
| `test_communication_priority.py` (156 lines) | Repetition drivers are gone; one representation stays a preference; the visual grammar survives; diagram accuracy is always on; Step 3 stayed short; both installs carry the same skill | `test_icons_are_a_default_preference_with_exclusions`, inverted on purpose — the new `test_icons_are_optional_not_a_default` asserts the opposite and names why; `test_linter_accepts_every_default_icon_on_a_heading` (no icon is expected on a heading now); `test_activation_shrank`, superseded by the budget test |

`tests/test_token_budget.py::test_activation_exceeds_the_phase_4_baseline_by_a_recorded_decision`
was renamed to `test_activation_stays_under_the_phase_4_baseline` and its
assertion restored from `>` to `<`. Its own docstring had said to restore it "only
by compressing those rules, not by deleting this test", which is what happened.

Three assertions in `tests/test_skill_structure.py` and one in
`tests/test_multiturn_policy.py` were updated: stale required phrases
(`"bold title line"`, `"six words"`, `"four columns"`, `"Prefer a visual"`,
`"25 words"`), the module version string, and three rule-count minimums that
treated more rules as better.

---

## 5. Validation

`python scripts/verify.py` and `python -m pytest` on Python 3.13, Windows, 2026-10-29.

| Check | Result |
|---|---|
| `python -m pytest` | **553 passed, 2 skipped** |
| `python scripts/validate_skill.py` (source) | PASSED, 0 errors, 0 warnings |
| `python scripts/validate_skill.py` on `dist/socialized.zip` | PASSED, 0 errors, 0 warnings |
| `python scripts/package_skill.py --check` | no drift |
| `python scripts/build_plugin.py --check` | no drift |
| `python scripts/token_budget.py --check` | all budgeted components within budget |
| `python scripts/version_lock.py` | lock matches plugin 0.9.0 and both package hashes |
| `python research/recompute_archive_stats.py` | reproduces |

Package changes and the version decision: both ZIPs changed bytes, so plugin
0.8.0 → **0.9.0** (minor, pre-1.0: shipped instructions changed in a way a user
will notice). Policy modules 0.7.0 → **0.8.0**. `scripts/version_lock.json`
updated by `version_lock.py --update`.

### Numbers

| Surface | Before | After | Change |
|---|---|---|---|
| `SKILL.md` activation tokens | 6035 | 5648 | −6.4% |
| `SKILL.md` rendered lines | 449 | 432 | −17 |
| `references/treatment-selection.md` | 242 lines | 190 lines | −52 |
| `communication/` three modules | 5,117 tokens | 3,837 tokens | −25% |
| `communication/README.md` | 4,121 tokens | 936 tokens | −77% |
| Policy test files | 5 files, 1,336 lines | 1 file, 412 lines | −69% |
| Counting rules in shipped text | 11 | 0 | — |
| Contradictory rule pairs found | 4 | 0 | — |

Line and token counts are local estimates from `scripts/token_budget.py`
(`Xenova/claude-tokenizer` where cached, otherwise the calibrated stdlib
heuristic). They are not Claude API usage.

---

## 6. Expected benefits

Stated as expectations, not results. None is established by the checks in §5.

- **Less formatting pressure.** With no thresholds to track and no form owed an
  appearance, the content's shape is the only input to the presentation decision.
- **Less diagram/prose repetition.** The caption contradiction in §1.3 made
  restating a figure the stable way to satisfy both rules. Removing it removes
  that pressure; whether the repetition stops is a behavioural question.
- **Icons appear where they help, or not at all.** Returning them to optional
  trades the chance of their appearing for the certainty that they are not a
  decoration requirement. If the owner wants them more often, the lever is the
  wording of one rule in one place, not a new rule.
- **Concrete arguments.** The general-property rule names the move the owner's
  microservices example wanted: show one request crossing two services and losing
  its reply, rather than describing distributed-system complexity.
- **Future changes stay small.** One wording per rule, and tests that assert
  invariants instead of phrasings, mean the next round can edit a rule rather than
  add one beside it.

## 7. Remaining uncertainties

- **Whether answers read better.** Static checks cannot show it. The owner's
  ordinary Claude conversations decide, with the microservices/Kafka question as
  the first acceptance case.
- **Whether removing the counting rules loosens structure too far.** The
  thresholds were never evidence-based, but they were specific. "One idea per
  paragraph" asks for judgement where "80 words" asked for arithmetic, and
  judgement can drift. The linter flags (`dense_paragraph`, `dense_table_cell`,
  `wide_table`, `max_sentence_words`) keep their thresholds as descriptive
  measures, so drift is observable on a sampled answer even though nothing gates
  on it.
- **Whether icons appear at all.** §1.4's hypothesis — that ambiguity rather than
  absence kept them out of v0.7.0's answers — is untested. If they still do not
  appear, the diagnosis in §1.4 was wrong and the lever is the trigger wording.
- **Whether the twelve operations were the right call.** Keeping them rests on the
  ablation sweep that has not run (it waits on judge acceptance, per `AGENTS.md`).
  If that sweep ever shows two operations indistinguishable, merging them becomes
  an evidence-based decision rather than a cosmetic one.
- **The reference material.** The owner brief names a ChatGPT response exported as
  `Microservices Architecture Advice.html` and a Claude response to the same
  question. Neither file is in this repository and neither was supplied in the
  working tree, so the comparison in brief §1 was not performed. The techniques the
  brief itself describes — concrete scenarios over general properties, a clear
  information hierarchy, content-driven form, natural register — were implemented
  from the brief's own description. **This is the one part of the brief that was
  not carried out as written.** Supplying the two files would allow it.

---

## 8. Addendum: the owner's house style (policy 0.9.0, plugin 0.10.0)

Same day, after the simplification shipped. The owner asked for a specific output
format and said to change, remove or add whatever it took to get it. This section
records what that reversed, because three of the changes contradict §1–§7 above.

### 8.1 What was asked for

- 📏 Short paragraphs only — two or three lines — whatever the topic, unless the
  person explicitly asks for long ones.
- 🔹 Heavy use of bullet points.
- 🏷️ Emoji points on the bullets, drawn from a large set.
- 🌬️ A visually spacious structure.
- 📊 Diagrams and colour-coded markdown where they are needed.
- 💬 Simple sentences and simple grammar, kept at all cost.

### 8.2 What it reverses

| §1–§7 said | The house style says | Why the owner's version wins |
|---|---|---|
| No counting rule ships; "80 words" asked for arithmetic where judgement belongs | One counting rule ships: two or three sentences per paragraph | A direct instruction from the owner outranks a brief's §5. It is one threshold, not eleven, and it is stated once |
| "Nothing here is a quota. No answer owes the reader a table, a figure, a heading, an icon…" | Five layout rules always apply | The quota statement read as making the layout optional too. It is replaced by a narrower one: the house style governs layout, content forms stay conditional |
| Icons are optional, and "never belongs on every heading or every item" | An emoji point opens every bullet and key heading | Direct owner instruction. §1.4 had argued the v0.7.0 default was the problem; the owner's answer is that it is the intent |

Two tests are inverted on purpose and say so in their docstrings:
`test_emoji_points_are_the_default_on_bullets_and_key_headings` in
`tests/test_communication_policy.py`, and
`test_activation_exceeds_the_phase_4_baseline_by_a_recorded_decision` in
`tests/test_token_budget.py`, which flips for the second time.

What §1–§7 keeps: the other ten counting rules stay gone, the four contradictions
stay resolved, one wording per rule, and the modules stay indexes.

### 8.3 What was added

**`SKILL.md` gains a "House style: always on" section**, before the first
operation so it is read first and sits inside Claude Code's 5,000-token compaction
re-attach window. Five rules, each with its escape hatch in one sentence: an
explicit request lifts one, and then stands until changed.

**`op:presentation`** holds the paragraph cap, the bullets-first rule, one idea and
one emoji point per item, and the blank-line rule.

**`op:plain`** names the swaps instead of only asking for simplicity: one clause
per sentence or two when the second is short, the everyday word over the formal one
("use" not "utilise", "so" not "consequently"), and the phrase cut to a word ("in
order to" → "to", "has the ability to" → "can"). A rule that only says "write
simply" is satisfiable by writing exactly as before.

**`op:visual`** holds a 44-icon working set grouped by meaning, the consistency
rule (same icon for the same kind of thing, drop it rather than mismatch), the
exclusions (code, identifiers, commands, JSON, logs, file paths, formal or legal
writing, one-line replies), and the colour techniques.

**`references/emoji-palette.md`** is new: about 150 icons by meaning across twelve
groups, the three colour techniques with worked examples, and a "what not to do"
list. It is the fourth reference file. Both expected-file sets in
`tests/test_skill_structure.py` and `tests/test_plugin_structure.py` were updated.

### 8.4 Colour: what markdown can actually do

Markdown has **no text colour**. The skill says so rather than promising it, and
names the three things that do render:

- 🎨 A `diff` fence — `-` lines red, `+` lines green. Best for a broken and fixed
  pair.
- 🎨 Mermaid `classDef` — real fill and stroke colour inside a diagram, one code
  per answer, named once.
- 🎨 Status emoji — 🟢 🟡 🔴 and ✅ ❌ ⚠️ are the only way to colour a table cell
  or a bullet.

### 8.5 The linter now measures the house style

`scripts/structural_metrics.py` changed so its flags track the shipped rules
instead of the removed ones:

- `DENSE_SENTENCES` 5 → 4 and `DENSE_PARAGRAPH_WORDS` 80 → 55, so a paragraph that
  breaks the two-or-three-sentence rule flags.
- `heading_nav_exempt` now covers bullets and numbered items, not only headings. A
  bullet opening with a meaning-matched icon plus words is the intended form, so it
  must not raise `emoji_structure`. A bare or status-only mark on a heading still
  flags.
- `NAV_ICONS` grew from 23 to about 100, covering the working set and the palette.

These stay descriptive. Nothing gates on them.

### 8.6 Cost

| Surface | Before | After |
|---|---|---|
| `activation` tokens | 5,648 | 6,178 |
| `activation.max` ceiling | 5,750 | 6,350 |
| `SKILL.md` body lines | 429 | 495 (validator limit: 500) |
| `SKILL.md` rendered lines | 432 | 459 |
| `ref:emoji-palette.md` | — | 2,699 tokens, on demand only |

The house style costs about 530 activation tokens, more than the simplification's
390-token saving, so activation is above the Phase 4 baseline (5,966) again. The
full palette went to a reference, which costs nothing until read. `SKILL.md` is at 495 body
lines against the validator's limit of 500 — **five lines of headroom, so the next
addition to it has to displace something.** Keeping it under that limit took a compression pass across
`op:sequencing`, `op:mechanism`, `op:examples`, `op:terms`, `op:presentation`,
`op:visual`, `op:register`, `op:repair`, `op:persistence`, `op:work-report`,
`op:close`, Step 1, Step 2, the accuracy rules and the scope list. No rule was
dropped in that pass; wording was merged.

One consequence: `op:register` now falls past the 5,000-token compaction re-attach
window, joining `op:repair`, `op:persistence`, `op:work-report`, `op:close` and
Step 3. The explanation operations that do the teaching, and the house style
itself, stay inside. `tests/test_token_budget.py::test_always_on_core_survives_compaction_reattach`
records the list.

### 8.7 What is still unverified

- Whether answers actually read this way. Static tests show the rules ship.
- **Whether the paragraph cap damages explanations that need a connected argument.**
  A two-sentence ceiling on a causal chain risks fragmenting it. `op:presentation`
  keeps "prose for a single chain of reasoning, where the links have to stay in the
  sentences" as the exception, and `treatment-selection.md` still names
  "whitespace padding" and "bullets that chop one continuous argument into
  fragments" as failures. Whether that is enough is a conversational question.
- **Whether an emoji on every bullet stops reading as a signal.** The consistency
  rule and the "drop it rather than mismatch" rule are the guards. The linter's
  `emoji_structure` flag no longer fires on the intended form, so it will not catch
  this; only reading will.
- Whether `SKILL.md` at the 500-line limit is maintainable. It is not, for growth.
  The next round has to remove before it adds.
