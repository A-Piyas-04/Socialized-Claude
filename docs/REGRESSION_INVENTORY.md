# Regression inventory

One row per failure this project has actually seen, with the policy text that answers
it, the deterministic check that would notice its return, and an honest statement of
what the check can and cannot see.

Read the second column as *the rule exists and is still worded this way*. No row means
the model obeys the rule. Obedience is a conversational observation, and this
repository cannot make it.

Per-phase detail lives in `docs/phase-3-implementation.md`,
`docs/phase-4-implementation.md`, `docs/phase-4b-token-efficiency.md` and
`docs/phase-4c-visual-restoration.md`, `docs/communication-recovery.md`,
`docs/communication-experience-upgrade.md` and `docs/communication-priority-correction.md`.
This page is the roll-up, and the place to add
a row when a new regression is found.

Run everything here with `python scripts/verify.py` (see `docs/VALIDATION.md`).

## How to read the status column

- **Structurally tested** — a test fails if the policy text or the shipped package
  loses the rule. The rule's presence is protected; its effect is not.
- **Observable only in conversation** — nothing offline can see it. It needs someone
  to use the skill and notice. These are the rows that matter most and are guarded least.
- **Heuristic only** — a number is reported and never gates, because the measure is an
  estimate or a style signal rather than a defect.

## Phase 1 — the explanation core

| # | Regression | Policy source | Protection | Status |
|---|---|---|---|---|
| P1-01 | A full tutorial in answer to a code request or a quick factual question | Intent strategies in `SKILL.md`; Strategy B/E; `communication/strategies.md` | `test_visual_restoration.py::test_the_five_strategies_and_their_priorities_are_untouched`, `test_refinement_policy.py::test_quick_answer_is_natural_not_a_rigid_cap` | Structurally tested |
| P1-02 | Research treatment ids or methodology jargon leaking into the shipped skill | `skill/socialized/` text | `test_skill_structure.py::test_skill_never_exposes_research_treatment_ids` | Structurally tested |
| P1-03 | A rule a plain undifferentiated paragraph would satisfy (the skill-text rule in `AGENTS.md`) | every operation block | `test_skill_structure.py::test_presentation_rules_name_actions_not_prohibitions`, `::test_close_rules_name_actions`, `::test_plain_language_rules_name_actions`, `test_visual_restoration.py::test_every_restored_rule_names_an_action` | Structurally tested |
| P1-04 | The answer does not come first, or the explanation is pitched at the wrong level | Step 1, `op:sequencing`, `op:register` | `structural_metrics.py` reports `answer_first_offset` as a labelled heuristic that never gates | Heuristic only |

## Phase 3 — multi-turn behaviour

| # | Regression | Policy source | Protection | Status |
|---|---|---|---|---|
| P3-01 | Re-explaining the whole topic instead of the part the person is stuck on | `op:repair`, Step 1 conversation read, Step 3 non-repetition check | `test_multiturn_policy.py::test_repair_operation_covers_the_multiturn_cases`, `::test_step1_reads_the_conversation_so_far`, `::test_step3_checks_non_repetition_and_preference_scope` | Structurally tested |
| P3-02 | A one-reply preference ("shorter, just this once") leaking into every later turn | `op:persistence` | `test_multiturn_policy.py::test_persistence_operation_scopes_one_reply_preferences` | Structurally tested |
| P3-03 | Follow-up reading becoming conditional, so a correction turn is missed | always-on follow-up rules | `test_multiturn_policy.py::test_followup_reading_is_always_on` | Structurally tested |
| P3-04 | Continuity claims that outrun what the conversation established | accuracy rules | `test_multiturn_policy.py::test_accuracy_rules_bound_conversation_continuity` | Structurally tested |
| P3-05 | Whether repair actually lands on the confusing part in a live exchange | — | none possible offline | Observable only in conversation |

## Phase 4 — communication refinement

| # | Regression | Policy source | Protection | Status |
|---|---|---|---|---|
| P4-01 | Automatic closing quiz or takeaway on a code fix, a decision or a quick answer | `op:close`, Step 3 close check, `controls.md` | `test_refinement_policy.py::test_close_check_question_is_conditional`, `test_visual_restoration.py::test_quizzes_previews_and_demo_offers_stay_conditional` | Structurally tested |
| P4-02 | Mechanical intro previews and section maps | `op:plain`, `op:presentation` | `test_refinement_policy.py::test_section_preview_is_optional` | Structurally tested |
| P4-03 | Diagram + table + state-table stacks for one mechanism | `op:visual`, Step 3 visual check | `test_refinement_policy.py::test_visuals_are_value_based`, `test_visual_restoration.py::test_visual_redundancy_rules_from_phase_4_are_kept`, `::test_step_3_prunes_decorative_structure_including_diagrams` | Structurally tested |
| P4-04 | Unrequested interactive or artifact offers | `op:visual` change-over-time rule | `test_refinement_policy.py::test_interactive_offer_is_not_default`, `test_skill_structure.py::test_visual_rules_name_actions_and_keep_artifacts_opt_in` | Structurally tested |
| P4-05 | Absolute technical claims with no configuration or scale qualifier | accuracy rules, `core.md` principle 6 | `test_refinement_policy.py::test_accuracy_rules_scope_implementation_and_concurrency`, `test_visual_restoration.py::test_accuracy_rules_discourage_absolute_and_unsupported_claims` | Structurally tested |
| P4-06 | Rigid response templates and word caps replacing judgement | intent strategies, `op:close` | `test_refinement_policy.py::test_quick_answer_is_natural_not_a_rigid_cap`, `test_visual_restoration.py::test_no_word_cap_was_added_to_the_explanation_itself` | Structurally tested |
| P4-07 | Dense walls of text: long paragraphs, long list items, unscannable tables | `op:presentation`, Step 3 density checks | `test_visual_restoration.py::test_step_3_checks_paragraph_and_list_density_and_table_scannability`, `::test_table_cells_scan_without_banning_sentences`; `structural_metrics.py` flags `dense_paragraph`, `dense_table_cell`, `wide_table` | Structurally tested (rules) / Heuristic only (flags) |

## Phase 4B — token efficiency

| # | Regression | Policy source | Protection | Status |
|---|---|---|---|---|
| P4B-01 | The activation surface growing past its ceiling | `scripts/token_budgets.json` (`activation.max` 5,600; `target` 5,000 advisory) | `scripts/token_budget.py --check`, `test_token_budget.py::test_repository_passes_its_configured_budgets` | Structurally tested |
| P4B-02 | The always-on core drifting below the operations, so compaction re-attach drops it | `SKILL.md` section order | `test_token_budget.py::test_always_on_core_precedes_every_operation`, `::test_always_on_core_survives_compaction_reattach` | Structurally tested |
| P4B-03 | A reference file silently disappearing or losing its link | `SKILL.md` reference section | `test_skill_structure.py::test_required_reference_files_exist_and_are_linked`, `scripts/validate_skill.py` | Structurally tested |
| P4B-04 | Token counts presented as billed Anthropic usage | report header in `token_budget.py` | `docs/VALIDATION.md`; the report labels itself a local estimate | Structurally tested (label) |
| P4B-05 | Whether a rule in an on-demand reference is read at all in a real turn | — | none possible offline; this is why owner-set visual rules stayed in `SKILL.md` | Observable only in conversation |
| P4B-06 | Counts depending on a tokenizer cached only on one machine | `token_budget.py` counter selection | `test_token_budget.py::test_legacy_tokenizer_is_never_downloaded`, `::test_heuristic_tracks_the_legacy_tokenizer_when_cached` | Structurally tested |

## Phase 4C — visual communication, restored and calibrated

| # | Regression | Policy source | Protection | Status |
|---|---|---|---|---|
| P4C-01 | A complex mechanism left with no figure, especially late in a long answer | `op:visual` preference and its escape clause; "keep that support even across the answer" | `test_visual_restoration.py::test_visual_is_the_preferred_treatment_for_a_shaped_idea`, `::test_visual_support_stays_even_across_a_long_answer`, `::test_coverage_suppressing_wording_is_gone` | Structurally tested |
| P4C-02 | The opposite failure: a forced visual quota or a per-answer cap | same rules, read the other way | `test_visual_restoration.py::test_no_visual_or_formatting_quota`, `::test_form_selection_is_not_a_mandatory_visual`, `::test_short_answers_still_get_sentences` | Structurally tested |
| P4C-03 | Step 3 pruning figures but never noticing a missing one | Step 3 coverage question | `test_visual_restoration.py::test_step_3_asks_about_missing_visuals_not_only_redundant_ones` | Structurally tested |
| P4C-04 | Non-teaching replies losing form guidance altogether | form-from-content line in the strategy section | `test_visual_restoration.py::test_strategies_pick_the_form_from_the_content` | Structurally tested |
| P4C-05 | Depth cut instead of split when an answer gets long | `op:presentation`, Step 3 | `test_visual_restoration.py::test_technical_depth_is_preserved_by_splitting_not_cutting` | Structurally tested |
| P4C-06 | `treatment-selection.md` or the `communication/` modules drifting from the skill | reference and module text | `test_visual_restoration.py::test_treatment_selection_agrees_with_the_calibrated_visual_rule`, `::test_policy_modules_agree_with_the_restored_rules`, `::test_policy_readme_records_the_regression_and_the_fix` | Structurally tested |
| P4C-07 | Whether the calibrated preference produces the right number of visuals for a real reader | — | none possible offline; the calibration itself came from live tests | Observable only in conversation |

## Communication-quality recovery (policy v0.5.0, plugin v0.6.0)

Found by the owner in three real v0.5.2 answers; see `docs/COMMUNICATION_BASELINE.md`.

| # | Regression | Policy source | Protection | Status |
|---|---|---|---|---|
| CR-01 | Table cells that each hold a paragraph of arguments | `op:presentation` table-cell rule, Step 3 | `test_communication_recovery.py::test_table_rows_keep_the_verdict_and_move_the_argument_under_the_table`, `::test_causal_links_are_no_longer_routed_into_table_cells`, `::test_table_cells_still_have_no_absolute_word_limit` | Structurally tested |
| CR-02 | A diagram followed by numbered steps or prose that retell its arrows | `op:visual` figure-versus-text rule, Step 3 | `test_communication_recovery.py::test_figure_and_text_have_different_jobs`, `::test_retelling_becomes_reasons_without_banning_a_walkthrough` | Structurally tested |
| CR-03 | One database's internals taught as how every database works | accuracy rules | `test_communication_recovery.py::test_general_mechanism_precedes_a_labelled_system_version` | Structurally tested |
| CR-04 | A decision answer that buries the recommendation inside the tradeoffs | Strategy D | `test_communication_recovery.py::test_decisions_lead_with_the_recommendation` | Structurally tested |
| CR-05 | An assumption restated on every sentence until paragraphs go dense | accuracy rules | `test_communication_recovery.py::test_assumed_scale_is_stated_once_with_what_would_change_the_answer` | Structurally tested |
| CR-06 | Whether the three prompts now produce the desired answers | — | none possible offline; the owner reruns the prompts in `docs/COMMUNICATION_BASELINE.md` | Observable only in conversation |

## Communication-experience upgrade (policy v0.6.0, plugin v0.7.0)

Owner request after the recovery, from six presentation weaknesses; see `docs/communication-experience-upgrade.md`.

| # | Regression | Policy source | Protection | Status |
|---|---|---|---|---|
| CX-01 | Several independently important claims in one paragraph | `op:presentation` one-idea rule, Step 3 | `test_communication_experience.py::test_one_primary_idea_per_paragraph_and_a_ceiling_not_a_target`, `::test_step_3_checks_mixed_claims_and_decorative_icons` | Structurally tested |
| CX-02 | A comparison table whose cells hide the decision | `op:presentation` glanceable-verdict rule | `test_communication_experience.py::test_table_cells_make_the_primary_decision_visible` | Structurally tested |
| CX-03 | Core, supporting and optional detail mixed in one unit | `op:sequencing` internal priority, `op:presentation` essential-before-edge-cases | `test_communication_experience.py::test_hierarchy_is_internal_priority_not_a_template` | Structurally tested |
| CX-04 | Every shaped idea described in prose, with no form variety | `op:visual` architecture cue, form-from-content | `test_communication_experience.py::test_visual_forms_include_architecture_and_existing_grammar` | Structurally tested |
| CX-05 | A diagram, then a table, then prose that all retell the same arrows | `op:visual` figure-versus-text plus comparison-table clause | `test_communication_experience.py::test_a_comparison_table_does_not_retell_the_diagram` | Structurally tested |
| CX-06 | An example that restates the definition | `op:examples` state–action–mechanism–result | `test_communication_experience.py::test_examples_trace_state_action_mechanism_result` | Structurally tested |
| CX-07 | No semantic icons, or an icon on every line, or an icon inside code | `op:visual` semantic-icon rule | `test_communication_experience.py::test_semantic_icons_are_navigation_not_decoration`, `test_structural_metrics.py` heading-nav exemption | Structurally tested |
| CX-08 | Whether ordinary conversations now read better | — | none possible offline; behavioural acceptance is the owner's | Observable only in conversation |

## Communication priority correction (policy v0.7.0, plugin v0.8.0)

v0.7.0 failed acceptance on two cache-coherence answers; see `docs/communication-priority-correction.md`.

| # | Regression | Policy source | Protection | Status |
|---|---|---|---|---|
| PC-01 | One mechanism told again in a second figure, an example, a walkthrough and a recap | Step 2 planning order, `op:visual` one-job-per-form, Step 3 one-job check | `test_communication_priority.py::test_repetition_drivers_are_gone`, `::test_planning_order_lives_once_in_step_2` | Structurally tested |
| PC-02 | One-representation hardening into a cap that strips useful figures | `op:visual` preference with "add another whenever it shows something the first cannot" | `test_communication_priority.py::test_one_representation_stays_a_preference_not_a_cap`, `::test_visual_grammar_survives` | Structurally tested |
| PC-03 | A figure with a wrong transition trigger (read drawn where only a write causes it) | First accuracy rule, figure clause | `test_communication_priority.py::test_diagram_accuracy_is_always_on` (text only) | Structurally tested; correctness observable only in conversation |
| PC-04 | No semantic icons in a substantive explanation | `op:visual` icon default | `test_communication_priority.py::test_icons_are_a_default_preference_with_exclusions`, `::test_linter_accepts_every_default_icon_on_a_heading` | Structurally tested |
| PC-05 | Conflicting rules growing back | Step 3 size, activation size | `test_communication_priority.py::test_step_3_got_shorter`, `::test_activation_shrank`, `activation.max` | Structurally tested |
| PC-06 | Whether answers are now easier to understand | — | none possible offline; behavioural acceptance is the owner's | Observable only in conversation |

## Phase 5 — the packages and metadata that carry all of the above

| # | Regression | Policy source | Protection | Status |
|---|---|---|---|---|
| P5-01 | A policy edit that never reaches the installable packages | deterministic builds | `scripts/package_skill.py --check`, `scripts/build_plugin.py --check`, `test_release_integrity.py` check-mode tests | Structurally tested |
| P5-02 | A changed package committed with no version decision | `scripts/version_lock.json` | `scripts/version_lock.py`, `test_release_integrity.py::test_a_changed_package_without_a_bump_is_reported` | Structurally tested |
| P5-03 | A rename splitting the marketplace entry from the plugin manifest | `.claude-plugin/marketplace.json`, `plugins/socialized/.claude-plugin/plugin.json` | `test_release_integrity.py::test_marketplace_entry_and_plugin_manifest_agree` | Structurally tested |
| P5-04 | Unsafe or stray members in a published archive | packaging rules | `test_release_integrity.py::test_committed_package_members_are_safe_relative_paths`, `::test_committed_package_carries_no_tooling_or_secrets` | Structurally tested |
| P5-05 | An install path quietly dropped from the documentation | `README.md`, `docs/INSTALLATION.md` | `test_release_integrity.py::test_both_install_paths_stay_documented`, `::test_no_broken_relative_links_in_project_markdown` | Structurally tested |
| P5-06 | CI drifting away from the gate a contributor runs locally | `.github/workflows/validate.yml` | `test_release_integrity.py::test_ci_runs_the_same_offline_entry_point` and the other CI tests | Structurally tested |

## What is still unguarded

Three things, and no offline check can reach any of them:

1. **Activation.** Whether Claude loads the skill from its description, on each surface.
2. **Adherence.** Whether the loaded rules change the answer.
3. **Comprehension.** Whether a reader understands the result better.

The evaluation framework under `evaluation/` is built for 1 and 2 and needs a Claude
Code run to produce data; `research/` holds the archive analysis behind the policy
choices. Both are separate from this gate by design: no model judge, no paid API, and
no improvement score is claimed anywhere in this repository.

Comparative research on 3 would need participants and a protocol, and is deliberately
out of scope for v1.
