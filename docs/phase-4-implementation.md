# Phase 4 — Communication refinement

Phase 4 makes four behaviours **selective instead of automatic** — closing quizzes,
intro/section previews, redundant visuals, and interactive-demo offers — and
tightens **epistemic scoping** of product-specific and concurrency claims. It adds
**no new operation, no new marker, and no new variant**: every change edits the
existing operations, Step 3 checks, accuracy rules, and the reusable policy modules.

> **Written for:** the project owner and a Phase 4 acceptance reviewer.

## Why this phase exists

Real-use checks across Python coding, React debugging, connection pooling/
replication, architecture discussion and Kubernetes showed an over-application of
educational formatting: automatic end-of-answer quizzes, mechanical intro previews,
redundant diagram + table + state-table stacks for one mechanism, tutorial framing
on advice/code/follow-ups, automatic interactive-demo offers, and occasional
over-confident technical simplifications. The fix is **selective communication**,
not blanket brevity: long answers, diagrams, tables, examples, and the occasional
question stay available whenever they demonstrably help.

## Issue log and traceability

| ID | Observed failure | Root instruction | Change | Regression check | Status |
|---|---|---|---|---|---|
| P4-01 | Automatic closing quizzes / takeaways | `op:close`, Step 3 close check, `controls.md` Conclusions | A check question is added **only** when the person asks to practise or be tested, the exchange is explicitly a tutorial, or one focused check resolves a real uncertainty — never on code, a fix, a decision, or a quick answer by category. The takeaway is optional. "I don't understand X" gets a clearer explanation, not a quiz. | `test_refinement_policy.py::test_close_check_question_is_conditional`, `::test_close_rules_still_name_actions`, existing `test_close_rules_name_actions` | Done |
| P4-02 | Redundant intro / section-map previews | `op:plain` (retained map), `op:presentation` (numbered-heading map) | `op:plain` no longer keeps a mandatory map; both the sentence roadmap and the heading map are added **only when** a complex, multi-part answer needs orienting. | `::test_section_preview_is_optional`, existing `test_plain_language_rules_name_actions` | Done |
| P4-03 | Diagram / table repetition; visual per section | `op:visual`, Step 3 visual check, `controls.md` Visualizations | Draw a visual **only when it clarifies**; prefer one strong representation per idea and add a second only for a materially different dimension; dropped the every-section / final-third requirement; colour, status emoji and legends only when they speed a comparison. | `::test_visuals_are_value_based`, existing `test_visual_rules_name_actions_and_keep_artifacts_opt_in` | Done |
| P4-04 | Automatic interactive/demo offers | `op:visual` (change-over-time rule) | The interactive-version offer is made **only when asked or clearly useful and feasible**, never appended by default. Artifacts stay opt-in. | `::test_interactive_offer_is_not_default` | Done |
| P4-05 | Overgeneralized / over-confident claims | Accuracy rules, `core.md` principle 6 | Scope a product-specific implementation, version or default to its system; flag a common implementation as common not universal; separate a simplified mental model from precise internals; state concurrency/replication/durability assumptions instead of a categorical guarantee; keep causal steps a requested mechanism needs; a diagram must not imply a guarantee the mechanism lacks. | `::test_accuracy_rules_scope_implementation_and_concurrency`, `::test_diagram_claims_are_scoped` | Done |
| P4-06 | Rigid response-type framing | Intent strategies, `op:close` | Quick answers are "answer directly and naturally", with "one sentence and stop" as the usual shape, not a rigid cap; the five strategies and the coding/debugging/discussion deliverables are preserved. | `::test_quick_answer_is_natural_not_a_rigid_cap` | Done |

## Exact files changed and why

| File | Change | Why |
|---|---|---|
| `skill/socialized/SKILL.md` | `op:close`, `op:plain`, `op:presentation`, `op:visual` refined; two accuracy rules added; quick-answer strategy softened; two Step 3 checks rewritten; the mandatory horizontal-rule-between-topics bullet removed as compulsory decoration | This is the only file Claude loads, so the behaviour has to change here |
| `skill/socialized/references/explanation-examples.md` | The change-over-time example now offers an interactive version conditionally, not by default | Keep the examples consistent with the refined `op:visual` |
| `communication/core.md` | Principle 6 gains implementation/mental-model/concurrency scoping; version → 0.3.0 | Reusable accuracy source stays consistent |
| `communication/strategies.md` | Strategy A "Avoid" list names mechanical previews, forced quizzes, and repeated-mechanism diagrams; version → 0.3.0 | Document the refined teaching defaults |
| `communication/controls.md` | Formatting, Visualizations, and Conclusions controls rewritten to the selective policy; version → 0.3.0 | Keep the depth/format/visual module in step |
| `communication/README.md` | Policy version 0.3.0 + Phase 4 change table | Traceability |
| `plugins/socialized/.claude-plugin/plugin.json` | `version` 0.2.0 → **0.3.0** | `version` pins installs; the shipped skill content changed |
| `plugins/socialized/skills/socialized/**` | Regenerated | Generated artifact, rebuilt by `scripts/build_plugin.py` |
| `dist/socialized.zip`, `dist/socialized-claude-plugin.zip` (+ manifests) | Regenerated | Propagate the refined canonical skill |
| `tests/test_refinement_policy.py` | **New**, 14 tests | Verify the shipped Phase 4 policy; separate file so prior test files are untouched |
| `tests/test_multiturn_policy.py` | Two version assertions updated 0.2.0 → 0.3.0 | The policy-module and plugin versions were bumped this phase; coverage of behaviour is unchanged |
| `CHANGELOG.md`, `docs/LIMITATIONS.md`, this file | Updated / new | Issue log and residual-limitation deliverables |

**Not changed** (brief §5.8): `scripts/package_skill.py`, `scripts/build_plugin.py`,
`scripts/validate_skill.py`, `tests/test_plugin_structure.py`,
`.claude-plugin/marketplace.json`. Both build scripts were *run*, never edited.

## Preserved from Phases 1–3

The twelve operations, fifteen variants, the five intent strategies, the running
example, causal mechanism with the obvious-approach-that-fails move, the visual
grammar (`sequenceDiagram`, `classDef`, bars, one colour code), the register
ladder, and the Phase 3 multi-turn repair/persistence/continuity rules are all
intact. `test_multiturn_policy.py` still passes unchanged except for the two version
pins. Nothing in the accuracy rules, the scope gate, or the reference methodology
was weakened.

## Size and contract

| Guard | Before (Phase 3) | After (Phase 4) | Limit |
|---|---|---|---|
| Rendered lines (compactness test) | 443 | **450** | < 460 |
| Raw body lines (validator) | 492 | **498** | ≤ 500 |
| Operations / variants | 12 / 15 | **12 / 15** | fixed |

Seven rendered / six raw lines were added net. The new conditional policy was offset
by consolidating redundant prose (the section-map rule left `op:plain`; the mandatory
horizontal-rule decoration was dropped; several bullets were tightened), so no guard
was raised. Two raw lines of slack remain; the next addition still needs a
consolidation.

## Validation — real results

```
python -m pytest                                        448 passed, 1 skipped
python scripts/validate_skill.py                        PASSED (0 errors, 0 warnings)
python scripts/validate_skill.py dist/socialized.zip    PASSED (0 errors, 0 warnings)
python scripts/build_plugin.py --check                  Plugin is in sync with the canonical skill.
claude plugin validate ./plugins/socialized             √ Validation passed
claude plugin validate ./.claude-plugin/marketplace.json  √ Validation passed
```

The suite was 434 before Phase 4; the 14 new tests are additive. The plugin-directory
LICENSE/icon advisories are pre-existing and do not affect the verdict (see
`docs/LIMITATIONS.md`, "directory submission not prepared").

## Behavioural spot-checks — documented, not run

These are optional natural-use checks. They are **not** batch experiments, and no
model calls were made. The policy edits do not, on their own, prove any change in
Claude's output; only a controlled comparison could.

| # | Prompt | What good looks like |
|---|---|---|
| 1 | "Write a Python timing decorator." | Code first; no mandatory multiple-choice quiz. |
| 2 | "Why does useEffect fetch twice in development?" | Likely cause + fix, hypothesis marked as such; no quiz. |
| 3 | "Should my 100-user app start with Kubernetes/RabbitMQ?" | Honest recommendation and tradeoffs; no classroom ending. |
| 4 | "Explain database replication internals." | Real mechanisms, one apt diagram; no redundant diagram + table. |
| 5 | "I understood primary vs replica, but how are changes transferred?" | Addresses the transmission mechanism only; no re-teaching. |
| 6 | "Teach me replication then quiz me without showing answers." | Honours the requested quiz; hides the answer. |
| 7 | "Use a sequence diagram and comparison table." | Produces both distinct outputs as asked. |

## Residual limitations and Phase 5

- Offline structural tests show the policy is **present and well-formed**; they
  cannot show that Claude is less likely to append a quiz or a redundant diagram in
  a real conversation. That needs ordinary chats, not these assertions.
- The epistemic-scoping rules are instructions, not a verifier. Nothing checks a
  claim against a source; accuracy still rests on the model and the accuracy rules.
- `SKILL.md` is at 498/500 raw lines. Any further behavioural rule needs a real
  consolidation first. A candidate for Phase 5 is folding the three Scope operation
  pointers, kept here deliberately as the only signal that repair/persistence/
  work-report apply outside explanations.
- Phase 5 could add a small labelled behavioural comparison (skill-on vs skill-off)
  for the quiz/preview/visual rates, using the existing Claude-vs-Claude judge, not a
  paid API.

## Git status

Branch `v1.0.4`; the tree was clean before Phase 4. Nothing was committed, amended,
rebased, or pushed — the changes are left for the owner to review.
