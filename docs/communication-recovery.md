# Communication-quality recovery (pre-release)

Policy v0.5.0, plugin v0.6.0. Brief: `temp/re-enhance--communication.md`.
Behavioural reference: `docs/COMMUNICATION_BASELINE.md`.

The owner rejected v0.5.2's communication quality before public release, from three
real answers: database replication, an architecture decision, and CPU cache
coherence. This is a targeted recovery, not a new phase. Eight existing rules were
refined in place, one bullet was added to `op:visual`, and two Step 3 checks were
extended. No operation, marker, variant, section or reference file was added.

**Nothing here shows that answers improved.** Behavioural acceptance stays with the
owner.

---

## 1. Policy history

v0.5.2's skill text is byte-identical to the Phase 4C calibration (`d99ba57`).
`git diff d99ba57 HEAD -- skill/` is empty, so Phases 5 and 6 changed no skill text.

| Version | Commit | What it did to presentation |
|---|---|---|
| V0 (Explanation Lab) | `0612b5a` | `op:structure`: "Default to connected prose"; no visual op, no cell or paragraph limits |
| Consolidated | `5bcd925` | `op:presentation` with shape-to-form defaults; the causal-link rule "When a list **or table** separates two causally linked facts, write the link inside the item" |
| Visual skill | `1eb1552`, `c44ba6d` | `op:visual` (Mermaid, `sequenceDiagram`, one visual per shaped idea); numbered headings; `---` rules; **Deeper:** blocks; cell "six words or fewer, never a sentence"; 80-word paragraphs |
| Phase 1 | `0439b2e` | Policy modules only; `SKILL.md` unchanged |
| Phase 2 | `2714c69` | Strategies embedded. Strategy D: "engage the actual proposal, weigh the tradeoff…, and give a reasoned recommendation" |
| Phase 3 | `1d0bc9e` | Multi-turn only |
| Phase 4 | `92e8eb8` | Coverage floor removed; one representation per idea; accuracy scoping for products and concurrency |
| Phase 4B | `d7d897f` | Compression; idea-change paragraph rule folded into a clause; "never a sentence" dropped |
| Phase 4C | `a573455` | Coverage, density and separator restored; form-from-content in every strategy, including "a table for options against their tradeoffs" |
| 4C calibration = v0.5.2 | `d99ba57` | Cells may hold "a short sentence where the comparison needs one"; Step 3 cell check becomes "stay scannable"; accuracy adds settings, unstated workload and no carry-over between databases |

## 2. Findings

Each finding separates what the diff shows from what is inferred about behaviour.

### 2.1 Paragraph-length table cells (Test B)

**Verified.**

- The calibration removed the only countable cell limit, in both the rule and Step 3.
- The causal-link rule, unchanged since `5bcd925`, told a table to carry its
  "because" inside the item.
- Phase 4C put tables into decision answers. The calibration's accuracy rules then
  added settings, workload and failure modes to state.
- No rule said where a row's argument goes when it does not fit.

**Hypothesis.** Decision answers now got tables with more to say per row, a rule
that put the reasoning in the cell, and no limit to stop it. This is the
best-supported link in the report. Test B is exactly this failure, and v0.5.2 is the
calibrated text.

### 2.2 Diagrams retold as numbered steps (Tests A and C)

**Verified.**

- `op:presentation` prescribes numbered steps for a process (since `5bcd925`).
- `op:visual` prescribes a `sequenceDiagram` for order in time (since `c44ba6d`).
- The arbitration between them is "keep to one representation per idea" (Phase 4)
  and "delete the sentences it replaces" (since `1eb1552`).
- No version, V0 to v0.5.2, said what the text beside a figure should do.

**Hypothesis.** Deleting "the sentences it replaces" reads as deleting the
description of the shape, not the step-by-step narration. With no positive job for
the text, the model fills it by walking the arrows. Phase 4C's restored preference
for figures made diagram-plus-steps more frequent.

### 2.3 One database taught as the general mechanism (Test A)

**Verified.** The scoping rule has existed since Phase 4 ("Scope a product-specific
implementation … to its system"). The calibration added "carry no database's …
behaviour over to another unchecked". Both say *what* to scope, never *how* the
answer is laid out.

**Hypothesis.** A scoping clause can be met with "in PostgreSQL, for example" inside
a general paragraph, so the general account and one system's internals stay
interleaved.

### 2.4 Dense paragraphs (Tests A and C)

**Verified.** The density limits at v0.5.2 match `c44ba6d`: four sentences or about
80 words, a new unit when the idea changes, and about 25 words per list item. They
were not weakened. What grew were the accuracy rules (Phase 4 and the calibration).
For concurrency and replication they ask for acknowledgements, durability, failure
modes, consistency, settings and unstated workload. They give no placement.

**Hypothesis.** These requirements are met as inline clauses on each claim, so
sentences exceed `op:plain`'s two-clause rule exactly in the topics of Tests A and C.
The causal-depth rules (every mechanism shows the obvious approach failing, since
`c44ba6d`) may add to the density too. They were left alone, because the owner
reported strong causal reasoning as a *strength* in Test C.

### 2.5 Weak separation of core mechanism and depth (Tests A and C)

**Verified.** The **Deeper:** rule is unchanged since `c44ba6d`. It never said what
counts as specialist depth.

**Hypothesis (weak).** Without named contents, variants and one system's edge cases
stay in the main thread.

### 2.6 Recommendation buried in tradeoffs (Test B)

**Verified.** Since Phase 2, Strategy D's own sequence ends with the recommendation:
"weigh the tradeoff …, and give a reasoned recommendation". Step 2's answer-first
rule applies to all replies.

**Hypothesis.** The strategy's order competes with Step 2, and the tradeoffs come
first.

### 2.7 Information hierarchy and documentation-like answers: not changed

**Verified.** Several rules give a documentation look:

- headings numbered whenever an answer has three or more sections (since `1eb1552`);
- `---` rules (restored in 4C);
- a titled fenced block for every specimen;
- backticks on every identifier.

**Not changed.** None of the owner's three observations names headings, numbering or
rules. The owner also accepted the 4C restoration of that structure in live tests.
Changing it would be speculative. It is recorded as the first candidate if the next
round of owner tests reports a document register (§6).

### 2.8 Not causes

These are confirmed by diff to touch no presentation rule:

- Phase 3's multi-turn rules;
- Phase 4's quiz, preview and demo-offer removals;
- Phases 5 and 6;
- Phase 4B's moving of the "each figure pays for itself" argument to
  `treatment-selection.md`. That text is an argument, not a rule.

### 2.9 Information architecture (Task 2): already covered, no new rule

The brief names Task 2 — distinguishing core, supporting and optional information,
establishing core understanding before substantial optional detail, and not
congesting one paragraph with several independently important explanations — as its
highest-priority task. This recovery adds **no new rule for it**, because its
substance is already distributed across rules that ship and are structurally tested.

**Verified.** The brief's three asks each map to an existing instruction:

- *Core before optional ordering.* `op:sequencing` orders ideas by dependency and
  puts the main idea and its prerequisites before consequences; `op:presentation`
  says "Put the main point first in its section, and gather minor caveats into one
  short unit at its end."
- *A skippable layer for optional detail.* `op:presentation`'s **Deeper:** /
  **For implementers:** blockquote defers variants, tuning and one system's edge
  cases, "keeping the narrative complete for a reader who skips it" (named by R7).
- *One idea per unit, not several per paragraph.* `op:presentation`'s "Give each
  idea its own unit… Start a new unit when the idea changes" is exactly the brief's
  critical rule, and `op:plain`'s one-claim / two-clause limits enforce it at the
  sentence level. Causal relationships are preserved by `op:mechanism` (state the
  chain) and the list-item link rule.

The brief itself frames these as distinctions that "guide information selection and
ordering internally" and states "this does not mean every answer must have three
sections", so a literal core/supporting/optional tier would risk the template shape
Task 8 forbids.

**What this recovery did for Task 2 indirectly.** The dense-paragraph fault (§2.4)
is the observable symptom of congested information. R5 (state each assumption once,
not as a clause on every sentence) removes the main driver of that density without a
new architecture rule. R8 (a demonstration stage in the learnable order) and R9
(trace the example to the behaviour) sharpen the core-before-detail sequence.

**Not done.** No explicit three-tier rule, because adding one would cost scarce
activation headroom (§4) for substance already present, and the owner's three
observations named table cells, figure/prose redundancy and scoping — not a missing
tiering rule. Recorded as a candidate if a later owner test reports core and optional
detail interleaved despite the rules above.

---

## 3. Changes

R3 is a new bullet in `op:visual`. Every other change rewords or extends an existing
bullet.

| # | Where | Before | After | Addresses |
|---|---|---|---|---|
| R1 | `op:presentation`, table cells | "…move a longer explanation to a list under the table." | "When a row needs a condition, a second reason, or an argument, keep the verdict in the cell and give the reasoning in a list under the table, one item per row." Sentences in cells stay allowed; no word cap. | 2.1 |
| R2 | `op:presentation`, causal links | "When a list **or table** separates…, write the link inside the item" | "When a list separates…". Tables take the link under the table (R1). | 2.1 |
| R3 | `op:visual`, new bullet | — | "Give a figure and its text different jobs: the diagram shows who acts in what order, a state table what each step changes, and the sentences after them why each step happens. Turn numbered steps or prose that only retell the arrows into that why, unless this reader needs the steps in words as well." | 2.2 |
| R4 | Accuracy rules, scoping | (no layout) | "Teach the general mechanism first, then label one system's own version ("In PostgreSQL, …")." | 2.3 |
| R5 | Accuracy rules, assumptions | "State any workload, scale, or traffic pattern the answer assumes and the person has not given." | "…, and what would change the answer. State each assumption once, where it first matters, not as a clause on every sentence." | 2.4, Test B |
| R6 | Strategy D | "engage the actual proposal, weigh the tradeoff it turns on, and give a reasoned recommendation" | "lead with the recommendation and the reason that decides it, then weigh the tradeoffs behind it … and name what would make a rejected one worth adopting" | 2.6, Test B |
| R7 | `op:presentation`, depth layer | "Put specialist depth in a blockquote…" | "Put specialist depth (variants, tuning, one system's edge cases) in a blockquote…" | 2.5 |
| R8 | `op:sequencing`, learnable order | "…the concept, how it works, then consequences…" | "…how it works, a concrete case that shows it working, then consequences…". "Use only the stages this answer needs" stays. | Task 4 |
| R9 | `op:examples` | (trace the case through the process) | adds "Trace it to the moment the behaviour in question shows (a conflict, a failure, a recovery), not only the smooth path." | Task 4 |
| R10 | Step 3 | "Does every table cell stay scannable" / "its replaced prose gone" | adds "with its argument under the table" / "text after it adding the why rather than a retelling" | 2.1, 2.2 |

**Mirrored, at no activation cost:**

- `treatment-selection.md`: the visual entry gains the figure-versus-text split.
  "A congested table" now names an argument in a cell, not a sentence, which had
  contradicted the calibration. New failure modes: "A diagram retold in steps", "One
  system taught as the rule" and "Qualifiers on every sentence".
- `explanation-examples.md`: two new weak-and-better pairs, "A decision table with
  its reasoning underneath" and "A figure and the text beside it". Their topics are
  kept off the three test prompts, so the skill is not tuned to them.
- `communication/` modules to v0.5.0: `controls.md` (formatting, visualisations),
  `strategies.md` (Strategy D), `core.md` (principles 6 and 11), and a README change
  summary.

**Deliberately not done:**

- No Phase 1 restoration, and no "never a sentence" or six-word cell cap.
- No visual quota, mandatory figure, quiz, takeaway, preview or template.
- No change to headings or numbering (§2.7), and no change to the mechanism op's
  causal depth (§2.4).
- No explicit core/supporting/optional tier for Task 2 (§2.9); its substance already
  ships in `op:sequencing`, `op:presentation` and `op:plain`.
- No rule moved into a reference file.

## 4. Token budget

These are local estimates from the legacy public tokenizer, with the heuristic in
brackets. They are not measured API usage.

| Surface | v0.5.2 | v0.6.0 | Change |
|---|---:|---:|---:|
| `activation` (loaded `SKILL.md`) | 5,543 [5,588] | **5,760 [5,813]** | +217 (+3.9%) [+225, +4.0%] |
| `metadata` | 37 | 37 | 0 |
| references, on demand | 8,281 | 8,858 | +577 |
| distributable skill | 13,824 | 14,618 | +794 |

The first draft cost +257 tokens. Trimming it to +217 meant three cuts:

- a strategy-line sentence that duplicated R3 was dropped;
- a table clause made redundant by R1 was dropped (R2 is shorter than the rule it
  replaced);
- R3 to R5 and R10 were tightened.

No owner-set rule was cut to make room.

**Gate.** `activation.max` was raised from 5,600 to 5,900 in
`scripts/token_budgets.json`, with the reason recorded there. It stays a regression
ceiling: there are 140 tokens of headroom by the legacy count and 87 by the
heuristic. The advisory `target` stays at 5,000, and activation is now 760 tokens
above it. Against the Phase 4 baseline (5,946), activation is still −3.1%.

**Compaction window.** These sections now sit past Claude Code's 5,000-token re-attach
window:

- `op:work-report` (partly);
- `op:close`;
- Step 3.

Before, only part of `op:close` and Step 3 sat past it. Every new rule except R10 is
in the strategy section, the accuracy rules, `op:sequencing`, `op:examples`,
`op:presentation` or `op:visual`, all inside the window. None of this affects
claude.ai.

**Line guards.** Raw `SKILL.md` is 480 of 500 lines; rendered, it is 432 of 460.

## 5. Validation

```
python -m pytest -q                          584 passed, 2 skipped   (565 before)
python scripts/verify.py --with-cli          11 passed, 0 failed, 0 skipped
python scripts/token_budget.py --check       All budgeted components are within budget.
python scripts/token_budget.py --tokenizer heuristic --check
                                             All budgeted components are within budget.
python scripts/validate_skill.py             PASSED (0 errors, 0 warnings)
```

`verify.py --with-cli` covers both `--check` drift modes, the version lock, archive
recomputation, and the Claude CLI's validation of the plugin and the local
marketplace.

**Tests.**

- New suite `tests/test_communication_recovery.py`, 19 tests. It checks:
  - each rule in §3, in the source and in both packages;
  - that cells still have no absolute word limit;
  - that a walkthrough in words stays allowed;
  - that no Phase 4 to 4C fix was reversed;
  - that the references and modules agree with the skill;
  - that `COMMUNICATION_BASELINE.md` claims no stored v0.5.2 output.
- The three policy-version assertions were moved from 0.4.0 to 0.5.0.
- No other test changed or was weakened. None encoded the problem directly. The
  problem was the *absence* of a rule.

**Packaging.**

- Plugin `version` 0.5.2 → 0.6.0. This is a minor bump because the shipped skill
  text changed.
- Both ZIPs, both manifests, the `plugins/socialized/` tree and
  `scripts/version_lock.json` were regenerated.

## 6. Remaining uncertainties and risks

- **No behavioural evidence.** No live answer, judge run, paid call or campaign was
  made. Whether the three prompts now produce the desired answers is unknown.
- **The causal account is a hypothesis.** §2's changes are confirmed by diff. Which
  of them produced which observed fault is argued, not measured.
- **Split decisions.** R1 moves a row's reasoning under the table. The reader may now
  have to join a row with its note. The rule limits this to rows that need it.
- **The escape clause can reopen the redundancy.** "Unless this reader needs the
  steps in words as well" is a judgement. If the model reads every reader as needing
  both, R3 changes nothing.
- **Assumption-once may under-hedge.** R5 keeps every accuracy requirement but
  states each assumption once. A reader who skims past that one statement misses it.
- **Over-fitting.** The rules were written against three technical,
  practitioner-level prompts. Beginner and non-technical answers are untested.
- **Documentation register untested (§2.7).** If the owner's next tests report
  answers that read like documentation, the unconditional numbered headings are the
  first candidate.
- **Budget headroom is thin again.** The next rule will need a consolidation or
  another deliberate raise.
