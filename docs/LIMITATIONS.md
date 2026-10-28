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

**Phase 4 backlog — communication refinements deliberately not changed in Phase 2.**
The owner's real-chat sanity checks were strong but noted these, to fix in Phase 4
(a communication-engine phase), not during plugin packaging:

- repeated introductory section previews;
- unnecessary closing quiz / comprehension questions on answers that don't need them;
- occasionally rigid tutorial structure;
- redundant visualizations.

These require editing the explanation operations, which Phase 2 must preserve.

## Not in scope for V0

There is no chatbot, API client, proxy, browser extension, or automated UI
control. There is no LLM-judge pipeline: an LLM judge may be added later, only
as a labelled secondary analysis.

(V1 adds that labelled secondary analysis: `scripts/judge.py`, a screening
instrument that never feeds S1–S7. A browser extension is planned as a separate
deliverable that restyles and measures text and never rewrites it.)
