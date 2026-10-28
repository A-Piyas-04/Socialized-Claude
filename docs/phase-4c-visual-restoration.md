# Phase 4C — restoring visual communication quality

Policy v0.4.0, plugin v0.5.0. Brief: `temp/v1.0.4c.md`.

Phase 4 fixed four real defects (forced quizzes, forced previews, redundant
visuals, automatic demo offers) and Phase 4B cut activation tokens by 9.5%. One of
the four fixes overshot: the visual-coverage floor was replaced by a negative rule,
and the pre-send check stopped asking whether a visual was *missing*. Answers drifted
into long prose — the owner's microservices / Redis / RabbitMQ / Kubernetes
discussion came back as four substantial prose sections instead of a comparison.

Phase 4C restores the coverage expectation, paragraph density and section separation,
adds form selection to the non-teaching strategies, and reinstates nothing Phase 4 was
right to remove.

**Final calibration (§6).** Live conversational tests accepted the restoration and
found the restored rules too prescriptive. The calibration turned them from
unconditional requirements into strong, context-sensitive preferences: no visual
quota, no mandatory final-third figure, no ban on sentences in table cells. It also
strengthened the accuracy rules in place. Sections 1–5 describe the restoration as
shipped before that calibration; §6 records what changed and why, and the numbers in
§4 and §5 are the calibrated ones.

---

## 1. Regression analysis

### 1.1 Confirmed instruction changes

Diffed `1d0bc9e` (pre-Phase-4) → `92e8eb8` (Phase 4) → `d7d897f` (Phase 4B).

| # | Where | Pre-Phase-4 | After Phase 4 / 4B | Phase |
|---|---|---|---|---|
| R1 | `op:visual`, coverage | "Give the hardest section its visual before giving any section a second one. Give the last third of the answer at least the visual support of the first." | "Give the hardest section its visual first; **do not require a visual for every shaped idea, every section, or the final third**." | 4 |
| R2 | `op:visual`, trigger | "Use this for **every** idea … when spelling that shape out would take three or more sentences." + "Draw **one visual for each such idea**." | "…and a visual **would show that relationship better than** three or more sentences." + "Draw a visual for each such idea **when it clarifies the relationship**." | 4 |
| R3 | `op:visual`, count | (no cap; `treatment-selection.md` said so explicitly) | "**Prefer one strong representation per idea**"; the reference dropped "There is no cap per answer; the cost stays flat because each figure deletes its prose." | 4 |
| R4 | Step 3, visual check | "Does **each idea with a shape have its visual**, including the hardest and the last sections?" | "Does **each visual** clarify a real relationship, with a caption…" | 4 |
| R5 | Step 3, decoration | "Does every heading, list, table, **diagram**, and bolded sentence mark a real division in the content? **Remove any that only decorate.**" | "Does every heading, list, table, and bold sentence mark a real division?" | 4B |
| R6 | `op:presentation`, density | "**Start a new paragraph when the idea changes, even when the paragraph is short.**" (its own rule) | Folded into the first bullet as the clause "Start a new unit when the idea changes". | 4B |
| R7 | `op:presentation`, separation | "Add a horizontal rule (`---`) under the heading structure between major topics in an answer of three or more sections." | Removed. | 4 |
| R8 | `op:presentation`, tables | "one idea of six words or fewer, **never a sentence**" | "one idea of six words or fewer" | 4B |
| R9 | `treatment-selection.md`, failure modes | "**One diagram carrying the whole answer.** … Each idea with a shape gets its own." | "… then prose for a later, **harder** idea whose shape a figure would clarify." | 4 |
| R10 | Layout | Operations first, always-on core last. | Core first, Step 3 last; activation 5,379 tokens against a 5,000-token compaction re-attach window, so Step 3 partly fell outside it. | 4B |

R1 also contradicted an owner decision recorded in `AGENTS.md` ("Visual budget (user,
2026-10-27, second report): … Each idea with a shape gets one visual … the last third
gets at least the first third's support"). Phase 4 overrode it without recording a
deviation.

### 1.2 Hypotheses about the behavioural effect

Not measured. Ranked by how much of the regression each would explain.

1. **R1 + R4 together remove every force pushing a visual into an answer.** R1 left
   only a negative rule, and R4 left a checklist item that can delete a figure but
   never add one. Together they turn "draw one per shaped idea, then prune" into
   "prune what you drew", with nothing upstream of the pruning. This is the most
   likely primary cause.
2. **R2's stacked gates make the trigger a taste judgement.** "Would a visual show
   this better?" and "does it clarify?" are both satisfiable by answering "the prose
   is fine", which is the default. The pre-Phase-4 trigger was mechanical: count the
   sentences the description would take.
3. **No strategy carried form guidance for non-teaching replies.** The reported
   regression was an *architecture discussion* — Strategy D. Strategy D says "weigh
   the tradeoff it turns on" and nothing about form; the table rule lives in a
   sub-bullet of `op:presentation`, an operation whose own header frames it around
   explanation. With R1 and R4 gone, nothing pulled a four-option comparison toward a
   table. (Confirmed as an instruction gap; its contribution is a hypothesis.)
4. **R3 removed the answer to the cost objection.** Without "each figure deletes its
   prose", "prefer one strong representation" reads as an economy argument against
   figures in general, not just against duplicates of one idea.
5. **R6 + R7 + R5 raise paragraph density directly.** A paragraph-break rule demoted
   to a clause, no rule between major topics, and no instruction to prune decoration
   including diagrams.
6. **R10 may drop the checks in long sessions.** Activation exceeded the documented
   5,000-token re-attach limit, and Step 3 is last. In a long Claude Code session the
   visual checks could be absent after compaction. Plausible for Claude Code; it does
   not explain claude.ai chats.

### 1.3 What was not a cause

- The quiz, preview and demo-offer changes. They remove endings and prefaces; neither
  affects paragraph length or table use.
- The accuracy/epistemic scoping. It constrains claims, not form.
- Phase 4B's rewording of `op:presentation` and `op:visual`. Line-by-line, it is
  compression with the same rules, apart from R5, R6 and R8.

---

## 2. Instructions changed in Phase 4C

Listed as shipped by the restoration. C1–C3, C5, C6 and C9 were then calibrated; see
§6 for their final wording.

| ID | Where | Change |
|---|---|---|
| C1 | `op:visual` | Trigger is one cue again — the length of the prose description. Phase 4's second judgement gate removed. |
| C2 | `op:visual` | "Draw a visual for each such idea … ; there is no cap per answer." |
| C3 | `op:visual` | "Give the hardest section its visual first, **and give the last third of the answer at least the visual support of the first**." The negative rule is deleted. |
| C4 | `op:visual` | Kept from Phase 4: "Keep to one representation per idea, and add a second only when it carries a materially different dimension"; colour/emoji/legend only where they speed a comparison; conditional interactive offer; opt-in artifacts. |
| C5 | Step 3 | "Does each idea with a shape have its visual, including the hardest section and the last third? Does each one clarify a real relationship, with a caption, its replaced prose gone, and one colour code?" — coverage **and** pruning. |
| C6 | Step 3 | Density check gains list items: paragraph (4 sentences / ~80 words), list item (~25 words), table cell (6 words). |
| C7 | Step 3 | "Does every heading, list, table, **diagram**, and bold sentence mark a real division, or does one only decorate?" |
| C8 | `op:presentation` | "Start a new unit when the idea changes, **even when the current one is short**" (merged into the unit rule, so it costs no extra line). |
| C9 | `op:presentation` | Table cell: "one idea of six words or fewer, **never a sentence**". |
| C10 | `op:presentation` | "…and a **horizontal rule (`---`) between major topics** in an answer of three or more sections." |
| C11 | Strategy section | New line applying to all five strategies: "In every strategy, pick the form from the content: a table for options against their tradeoffs, a diagram for a flow or an interaction, steps for a procedure, a fenced block for code, prose for a single chain or a casual reply." |
| C12 | `treatment-selection.md` | §1 visual entry restored (each shaped idea, no cap, cost stays flat, last third supported) with Phase 4's one-representation clause kept; failure mode "One diagram carrying the whole answer" restored. |
| C13 | `communication/controls.md` | Visualizations and Formatting controls follow C1–C3, C8 and C11; version 0.4.0. |
| C14 | `communication/core.md` | New principle 11, "Readable presentation": unit per idea, form from shape, and split a dense paragraph rather than dropping a mechanism. Principles 1–10 keep their numbers (docs cite them by number). |
| C15 | `communication/strategies.md` | Strategy A "Avoid" gains "long undifferentiated prose where the content has a shape a table or a diagram would show". |

### Deliberately not done

- No new operation, marker or variant (still 12 and 15).
- No new formatting framework and no new reference file.
- No reinstatement of mandatory quizzes, takeaways, section previews, interactive
  offers, heading depth or response templates.
- No word or length cap on the explanation. `op:presentation`'s limits bound a
  paragraph, a list item and a table cell — never the answer.
- No visual required for every *topic*: the floor is per shaped **idea**, and the
  three-sentence test still excludes short answers and practitioner lookups.

---

## 3. Visual communication principles now in the loaded skill

Mapped to the brief's Task 2 list.

| Brief item | Rule | Where |
|---|---|---|
| 1. Short paragraphs, one coherent idea | unit per idea; new paragraph on idea change even when short; 4 sentences / ~80 words | `op:presentation`, Step 3 |
| 2. Clear separation between concepts | blank line before every unit; horizontal rule between major topics | `op:presentation`, Step 3 |
| 3. Meaningful headings | a heading per distinct part, stating what the section establishes; `##` then `###`; no heading over a one-sentence section | `op:presentation`, `controls.md` |
| 4. Comparison tables | three or more items across two or more dimensions → a table, ≤4 columns; a table for options against their tradeoffs in every strategy | `op:presentation`, strategy section |
| 5. Mermaid diagrams | `flowchart` for a branch/loop/return; `sequenceDiagram` for order in time; preferred per shaped idea, hardest first, support kept even across the answer | `op:visual` |
| 6. Lists | labelled list for parallel options; numbered steps for a process | `op:presentation` |
| 7. Selective bold | bold the one sentence the reader must not miss, at most two per answer; bolded verb per step; bolded label per option | `op:presentation` |
| 8. Whitespace | blank line before every paragraph, list, table, code block, heading; rule between topics | `op:presentation`, Step 3 |
| Against excess | one claim per sentence, ≤2 clauses; ~25-word list items; 6-word table cells; prune anything that only decorates | `op:plain`, `op:presentation`, Step 3 |

---

## 4. Validation

Commands and results, run on this tree.

```
python -m pytest -q                              492 passed, 1 skipped
python scripts/validate_skill.py                 PASSED (0 errors, 0 warnings)
python scripts/package_skill.py                  PASSED dist/socialized.zip
python scripts/build_plugin.py --check           Plugin is in sync with the canonical skill.
python scripts/token_budget.py --check           All budgeted components are within budget.
python scripts/token_budget.py --tokenizer heuristic --check
                                                 All budgeted components are within budget.
python research/recompute_archive_stats.py       reproduces
```

New suite: `tests/test_visual_restoration.py`, 29 tests, grouped P4C-01…P4C-08.

| Group | Checks |
|---|---|
| P4C-01 | Visual is the preferred treatment for a shaped idea, with its escape clause; support stays even across a long answer; the three coverage-suppressing phrases **and** the four quota phrases absent; one trigger cue; Phase 4's redundancy rules kept; short answers still prose. |
| P4C-02 | Step 3 can still notice a *missing* figure, in the last third as much as the first, and still prunes; decoration check covers diagrams. |
| P4C-03 | Paragraph and list limits; table-cell scannability without banning sentences; idea-change paragraph break; horizontal rule at a topic turn. |
| P4C-04 | Form-from-content line present with all five cues; five strategies intact; no mandatory-diagram wording. |
| P4C-05 | Quizzes, previews and demo offers still conditional; no word cap added; depth preserved by splitting; accuracy rules cover configuration-dependent guarantees, unstated workloads and cross-implementation carry-over, with no new operation. |
| P4C-06 | Phase 3 multi-turn: `op:repair`, `op:persistence`, `op:work-report` rule counts, key phrases, and the scope routing for correction and work-report turns. |
| P4C-07 | 12 operations / 15 variants, markers balanced, both line budgets, every restored rule names an action, restored text present in the claude.ai ZIP **and** the plugin. |
| P4C-08 | `treatment-selection.md`, the three policy modules and the policy README agree with the skill. |

Two Phase 4 assertions were inverted on purpose, with the reason in
`tests/test_refinement_policy.py`:

- `test_visuals_are_value_based` now asserts only the anti-redundancy half.
- the Phase 4 `FORBIDDEN` list drops "Give the last third of the answer at least the
  visual support of the first", which Phase 4C reinstates.

**These checks do not show behavioural improvement.** They show which instructions
ship. No live comparison, judge run or paid API call was made, and no manual campaign
was run.

---

## 5. Token budget

Local estimates (Anthropic's legacy public tokenizer; the heuristic in brackets).
Baseline column is the pre-4B Phase 4 tree, as recorded in `scripts/token_baseline.json`.

| Surface | Phase 4 | Phase 4B | 4C restoration | 4C calibrated | 4B → final |
|---|---:|---:|---:|---:|---:|
| `activation` (loaded `SKILL.md`) | 5,946 [5,966] | 5,379 [5,418] | 5,466 [5,514] | **5,543 [5,588]** | +164 (+3.0%) [+170, +3.1%] |
| `metadata` | 37 | 37 | 37 | 37 | 0 |
| references, on demand | 8,202 | 8,221 | 8,262 | 8,281 | +60 |
| distributable skill | 14,148 | 13,600 | 13,728 | 13,824 | +224 |

Against the Phase 4 baseline, activation is still **−6.8%**. Phase 4B's saving is
kept; the restoration spent about a sixth of it and the calibration about another
sixth, most of the latter on the accuracy strengthening (§6, K7).

**What the 87 tokens bought:** C1–C3 (coverage floor), C5–C7 (three Step 3 checks),
C8–C10 (density and separation) and C11 (form in every strategy).

**Offsetting consolidations**, so the net cost stayed at +87 rather than about +190:

- the two paragraph-break rules merged into one (C8 adds no line);
- "the last section … same visuals" dropped from `op:presentation`, now covered by
  `op:visual`'s last-third rule;
- the visual cost argument ("each figure pays for itself") left in
  `treatment-selection.md`, which costs nothing until read;
- the reference-file pointers shortened;
- "Structure shows an explanation's shape; it does not create one." deleted — Step 3's
  new decoration check (C7) now carries it;
- the strategy form line written without "three or more", which `op:presentation`
  already states.

**Budget change.** `activation.max` raised 5,500 → 5,600 in `scripts/token_budgets.json`,
with the reason recorded there. That gate is a *regression ceiling about 2% above the
current size*, not an owner-frozen threshold; the raise keeps it doing its job at the
new size. `target` stays 5,000. The calibration fits inside the raised gate with about
12 tokens of heuristic headroom and did not raise it again.

**The tradeoff, stated plainly.** Activation remains above the 5,000-token advisory
target, and it is now 466 tokens above rather than 379. The report names what falls
outside Claude Code's compaction re-attach window:

| | Phase 4B | Phase 4C |
|---|---|---|
| Past 5,000 tokens | Step 3 (partly) | `op:close` (partly), Step 3 (all) |

So in a long Claude Code session after auto-compaction, the restored Step 3 checks
(C5–C7) may not be re-attached. The *rules* they check — C1–C3 and C8–C10 in
`op:visual` and `op:presentation` — stay inside the window, as does C11, which is in
the always-on core. The checklist is a backstop; the rules are the instruction. This
was chosen over the alternative the brief warns against: moving the visual drawing
grammar into an on-demand reference would have freed about 400 tokens and put the
owner-set visual rules at risk of never being read
(`docs/phase-4b-token-efficiency.md` §4).

---

## 6. Final calibration

Live conversational tests accepted the restoration and reported that several restored
rules were too prescriptive, risking the rigidity Phase 4 had removed. This was a
wording calibration: no operation, marker, variant, section or reference file was
added or removed, and `op:close`, `op:plain`, `op:repair`, `op:persistence` and
`op:work-report` were not touched.

| ID | Rule | Before (restoration) | After (calibrated) |
|---|---|---|---|
| K1 | `op:visual`, coverage | "**Draw** a visual for each such idea … ; **there is no cap per answer**." | "**Prefer** a visual for such an idea … **Leave one out where the prose already makes the relationship plain.**" |
| K2 | `op:visual`, long answers | "give the last third of the answer **at least the visual support of the first**" | "**keep that support even across the answer, so a later section that needs a figure gets one**" |
| K3 | `op:visual`, trigger | "**describing that relationship in prose would take** three or more sentences" | "**prose would take** three or more sentences **to describe that relationship**" — same cue, read as a signal rather than a test to pass |
| K4 | `op:presentation`, tables | "one idea of six words or fewer, **never a sentence**" | "one idea, **about six words where a phrase will do and a short sentence where the comparison needs one**" |
| K5 | `op:presentation`, separation | "a horizontal rule (`---`) **between major topics in** an answer of three or more sections" | "a horizontal rule (`---`) **where** an answer of three or more sections **turns to a new topic**" |
| K6 | Step 3 | "Does **each idea with a shape have its visual**, including the hardest section and the last third?" / "any **table cell six words**" | "Does **a mechanism a figure would clarify still have one**, in the last third as much as the first?" / "Does every table cell **stay scannable**?" |
| K7 | Accuracy rules | one bullet scoping implementation and concurrency claims | split in two: the first adds "**carry no database's or broker's behaviour over to another unchecked**"; the second adds "**Name the settings a guarantee depends on rather than stating it absolutely**" and "**State any workload, scale, or traffic pattern the answer assumes and the person has not given**" |

Mirrored in `treatment-selection.md` §1 and its failure modes, `controls.md`
(Visualizations, Formatting) and `core.md` principle 6. The policy modules stay at
v0.4.0: the calibration adjusts the same rules, it does not add policy.

**Kept, unchanged by the calibration:** the comparison-table cue (three or more items
across two or more dimensions), the whole Mermaid grammar (`flowchart`,
`sequenceDiagram`, `classDef`, load-bearing node shape, colour code), paragraph
density (four sentences / ~80 words, new unit on an idea change, ~25-word list
items), heading rules and the section separator, the Step 3 scannability and
decoration checks, and the form-from-content line in the strategy section.

**Still not reintroduced:** mandatory check questions, automatic takeaways, section
previews, interactive offers, unrequested artifacts, response templates.

**Tests updated**, per the calibration's own instruction to update tests that enforce
unconditional visualization rules:

- `tests/test_visual_restoration.py`: six tests re-pointed from requirement wording to
  preference wording, plus two new ones — `test_no_visual_or_formatting_quota` (a
  `QUOTA` list of four phrases that must stay absent, checked in the source and in
  both artifacts) and `test_accuracy_rules_discourage_absolute_and_unsupported_claims`.
- `tests/test_skill_structure.py`: one pre-existing assertion required the literal
  "for each such idea" in `op:visual`; it now requires "Prefer a visual". Nothing else
  in that suite was touched.

No other test was weakened. The Phase 4 suite, the Phase 3 multi-turn suite, the
packaging suites and the token-budget suite are unchanged and pass.

## 7. Remaining limitations

- **No behavioural evidence.** Everything above is static. The regression itself was
  observed by the owner in real chats; the fix has not been observed in real chats.
  Whether Claude now produces the comparison table is unverified.
- **The causal account of the regression is a hypothesis.** The instruction changes in
  §1.1 are confirmed by diff. Which of them produced the prose drift, and in what
  proportion, is not. R1 and R4 are ranked first by argument, not measurement.
- **The three-sentence trigger is still a judgement.** "Would describing this take
  three or more sentences?" is mechanical in form but estimated by the model. Nothing
  counts it.
- **The form-from-content line is one sentence against five strategies.** Whether it
  is enough to move a Strategy D answer to a table is untested; the alternative,
  per-strategy form rules, costs roughly four times the tokens.
- **Step 3 sits outside the compaction window** (§5). Untested in a long session.
- **No linter gate.** `scripts/lint_response.py` has `visual_count`,
  `dense_paragraph`, `wide_table`, `flat_visual` and the rest, but AGENTS.md fixes
  them as heuristics and flags that never gate, so nothing in CI measures an actual
  answer's visual density.
- **Phase 4's own fixes are equally unverified** and nothing here changes that.
- **`SKILL.md` is near its guards again**: 470/500 raw lines, 422/460 rendered, and
  `activation` is about 12 heuristic tokens under its gate. The next behavioural rule
  needs a consolidation first.
- **"Strong preference" is not measurable from the text.** The calibration's whole
  claim is that the pull toward a figure is still strong enough after the
  requirement was removed. The tests can only check that the preference wording and
  its escape clause are both present; whether the balance is right is unknown, and it
  is the same kind of judgement Phase 4 got wrong in the other direction.
