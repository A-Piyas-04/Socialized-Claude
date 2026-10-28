# Limitations — Explanation Lab V0

Read this before drawing any conclusion from using or testing the skill.

## About the skill

- **Activation is not guaranteed.** Claude decides whether to load a skill by
  matching the request against its description. Eligible requests may not
  trigger it, and occasionally unrelated ones may.
- **Instruction-following varies** by model, model version, conversation
  length, other enabled skills, and product-side system prompts that we cannot
  see. A change to any of these can change the skill's effect.
- **It does not modify Claude's model weights.** It is text that Claude reads.
  It can only steer what Claude already does.
- **It cannot guarantee a better explanation.** It encodes hypotheses about what
  makes explanations work. Some responses may be worse than Claude's default,
  for example through over-structuring or omitting a useful example.
- **It cannot inspect hidden reasoning.** The "silent" diagnosis and checking
  steps are instructions. Whether Claude actually performs them cannot be
  observed, only inferred from outputs.
- **It has no independent verifier.** Nothing checks the explanation with a
  second model or a source of truth. Accuracy rests on Claude and on the
  skill's accuracy rules.
- **Claude account limits still apply.** Plan eligibility, usage limits, and
  code-execution availability are set by Anthropic.
- **Surfaces are separate.** A skill uploaded to claude.ai is not available in
  the API or Claude Code, and vice versa.
- **Interface details change.** Menu paths and what the interface shows as
  activation evidence may differ from the documentation.

## About the evidence

- **Human comprehension improvements are unproven.** No person has been tested.
  No experiment so far has measured comprehension in a way that could detect a
  difference (`research/EVIDENCE_AUDIT.md` §2.4).
- **The operation choice is a hypothesis.** It rests on automated fidelity
  screening of Gemini rewrites, learning-science literature, and the project
  brief. Fidelity screening shows only that a rewrite did not obviously break
  the text. Its best scores were partly produced by rewrites that changed
  nothing.
- **Rewrite evidence may not transfer to generation.** All prior experiments
  rewrote existing answers with Gemini. The skill asks Claude to compose
  answers.
- **The prior judge was uninformative.** It reportedly gave 5/5 to every
  answer. The judge outputs are not in the archive, so this could not be
  checked.
- **Small, narrow prior data.** 10 runs per treatment, 5 topics at moderate
  difficulty, 1 sample per cell.

## About the evaluation framework

- **Manual execution.** Results depend on careful operators. Copying,
  settings, and timing errors are possible. The runbook and validation scripts
  reduce but do not remove this.
- **Mechanisms differ between conditions.** The B instruction sits in the user
  message, and the skill loads optionally from the system context. The explicit
  and D conditions exist to separate these, but they are not perfectly
  equivalent.
- **Rater scores are judgements.** They can be biased by length, style, or
  recognising a condition. Blinding and anchors help but do not eliminate this.
- **The presentation, register, repair, persistence, work-report and plain-language operations
  are untested hypotheses, and the structural linter measures form only.** No
  data of any kind supports them yet. A response can pass every linter check and
  still be wrong; the linter cannot tell.
- **Automated results characterise Claude Code, not claude.ai.** The harness
  runs `claude -p`, whose system prompt and scaffolding differ from claude.ai's;
  activation rates in particular do not transfer. The judge is a free-tier
  non-Anthropic model with a small daily quota, a screening instrument whose own
  reliability is reported as its order-flip rate.
- **The operations reach beyond the skill's trigger.** Persistence and work
  reports matter outside explanations, but the skill's description only triggers
  on explanation requests, so natural activation will rarely load them there.
- **The pilot is small.** 45 cases, 2 raters, and 12–18 comprehension
  participants can show direction and expose problems with the instruments. They
  cannot establish superiority. Criteria are engineering targets.
- **Comprehension items are unscreened drafts.** They must pass the screening
  step before use. Only 3 topics exist, so topic and condition effects are only
  partly separable.
- **Activation evidence depends on the interface.** If the interface does not
  show skill loading, natural activation cannot be measured, and only explicit
  invocation results are interpretable.

## Phase 2 (plugin) limitations and Phase 4 backlog

- **No always-on communication.** The Phase 2 plugin makes the skill *available*
  on supported surfaces; skills are selected when Claude judges them relevant, not
  forced on every answer. No supported plugin component gives always-on behaviour
  in claude.ai normal chat. The best supported standing guidance is scoped: a
  claude.ai Project's instructions, or an opt-in `CLAUDE.md` block in Claude Code.
  See `docs/phase-2-implementation.md`.
- **Plugin runtime behaviour is unverified.** `claude plugin validate` passes and
  the structure is sound, but structural checks cannot show the skill changes
  Claude's behaviour. Confirm with ordinary conversations.
- **Directory submission not prepared.** Submitting to Anthropic's public plugin
  directory needs a `LICENSE`/`license` and a listing icon; neither is added,
  because the license is the owner's decision.

## Phase 3 (multi-turn) limitations

- **No memory of any kind.** The multi-turn policy plans a reply from the turns
  the host actually supplies. There is no durable memory, no hidden state, no
  cross-session recall, and no retrieval. Where a referred-to turn is absent, the
  skill is instructed to say what is missing rather than reconstruct it.
- **Follow-up reading is silent and unobservable.** Whether Claude actually
  classifies a follow-up as confusion, a correction, or feedback cannot be seen,
  only inferred from the reply — the same limit as the Step 1 and Step 3 checks.
- **Offline tests prove presence, not behaviour.** `tests/test_multiturn_policy.py`
  shows the policy ships in the loaded `SKILL.md` and in both artifacts. It cannot
  show that Claude adapts across turns. The scenarios in
  `docs/phase-3-implementation.md` are regression spot-checks, not measurements.
- **`SKILL.md` is near its size guards** (415/460 rendered, 463/500 raw). Further
  additions require consolidating duplicate prose, not raising the guards.

**Phase 4 backlog — now addressed (policy v0.3.0, plugin v0.3.0).**
The owner's real-chat sanity checks noted these; Phase 4 conditionalized each one in
the explanation operations (`docs/phase-4-implementation.md`):

- repeated introductory section previews → `op:plain` / `op:presentation` add a map
  only when a complex answer needs orienting;
- unnecessary closing quiz / comprehension questions → `op:close` adds a check only
  when asked, in a tutorial, or to resolve a real uncertainty;
- occasionally rigid tutorial structure → intent strategies lead; quick answers are
  natural, not a one-sentence cap;
- redundant visualizations → `op:visual` prefers one strong representation per idea
  and drops the every-section / final-third requirement;
- over-confident simplifications → the accuracy rules scope product-specific and
  concurrency claims.

## Phase 4 (communication refinement) limitations

- **Selective, not proven.** Offline tests show the forced-quiz, forced-preview,
  forced-visual and forced-demo directives are gone from the loaded `SKILL.md` and
  both artifacts, and the conditional ones are present. They cannot show that Claude
  actually withholds a quiz or a redundant diagram in a live chat. The spot-checks
  in `docs/phase-4-implementation.md` are regression prompts, not measurements, and
  no controlled comparison was run.
- **Epistemic scoping has no verifier.** The new accuracy rules are instructions;
  nothing checks a claim against a source. Accuracy still rests on the model.
- **`SKILL.md` was at 498/500 raw lines** when Phase 4 shipped; Phase 4B's
  consolidation brought it back down.
- **One Phase 4 change was wrong and was reversed.** Making visuals "value-based"
  also removed the coverage floor and turned the pre-send visual check into a
  pruning-only check, and answers drifted into long prose. Phase 4C restored the
  floor and the check; the anti-redundancy half of the Phase 4 change stands. See
  `docs/phase-4c-visual-restoration.md` §1.

## Phase 4B (token efficiency) limitations

- **Counts are local estimates.** `scripts/token_budget.py` uses Anthropic's legacy
  public tokenizer or a heuristic calibrated to it. The real tokenizer of current
  models is unpublished, and Claude Code's own estimator runs about 8% higher.
  Runtime savings were not measured.
- **Activation is still above the documented 5,000-token target** (5,379 by the
  legacy count). In long Claude Code sessions the tail of Step 3, and possibly part
  of `op:close`, can fall outside what is re-attached after compaction. Going lower
  would mean moving the visual drawing grammar into an on-demand reference, which
  was proposed and not implemented (`docs/phase-4b-token-efficiency.md`, §4).
- **Order and wording changes are unmeasured.** The text moved and was tightened
  without a behavioural comparison.

## Phase 4C (visual communication restored) limitations

- **No behavioural evidence either way.** The regression was observed by the owner in
  real chats; the fix has not been. The 26 tests in `tests/test_visual_restoration.py`
  show which instructions ship, in the loaded `SKILL.md` and in both artifacts. They
  cannot show that Claude now produces the comparison table.
- **The cause is a ranked hypothesis.** The ten instruction changes in
  `docs/phase-4c-visual-restoration.md` §1.1 are confirmed by diff. Which of them
  produced the prose drift, and in what proportion, is not measured.
- **The three-sentence trigger is still estimated by the model.** Nothing counts the
  sentences a prose description would take.
- **Step 3 now sits wholly outside Claude Code's 5,000-token compaction re-attach
  window** (activation 5,466 local-estimate tokens; `op:close` is partly outside too).
  The rules the checks enforce stay inside it. Untested in a long session.
- **Nothing gates visual density.** `scripts/lint_response.py` carries
  `visual_count`, `dense_paragraph`, `wide_table` and `flat_visual`, but AGENTS.md
  fixes them as heuristics and flags that never gate.
- **`activation.max` was raised 5,500 → 5,600** to pay for the restored rules. The
  5,000-token advisory target is still exceeded, now by 466 tokens.

## Not in scope for V0

There is no chatbot, API client, proxy, browser extension, or automated UI
control. There is no LLM-judge pipeline: an LLM judge may be added later, only
as a labelled secondary analysis.

(V1 adds that labelled secondary analysis: `scripts/judge.py`, a screening
instrument that never feeds S1–S7. A browser extension is planned as a separate
deliverable that restyles and measures text and never rewrites it.)
