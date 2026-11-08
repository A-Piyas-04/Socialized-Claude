# Limitations — Socialized-Claude

Read this before drawing any conclusion from using or testing the skill.
Current as of version 2.2.0 (V2 Phase 9 plus Approach B Phases 1 and 2).

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
  for example through over-structuring, a forced analogy, or glosses that slow
  a reader who knew the terms.
- **The page shape can make answers look alike.** Every answer of two or more
  sections gets the same slots. The guards are that the shape starts at two
  sections, a short answer stays short, and the 🧠 and 🧪 slots depend on intent.
- **It does not yet adapt across a conversation.** Follow-ups that build on
  what was already taught, and repairs that change strategy rather than
  rephrasing, are planned (Approach B Phases 3 and 4) and not built.
- **The description triggers on explanation wording.** "How", "why", "understand"
  and "confused" load it. A decision or debugging request may not, even though
  the skill handles both; `/socialized` makes it apply.
- **It cannot inspect hidden reasoning.** The "silent" reading and checking
  steps are instructions. Whether Claude actually performs them cannot be
  observed, only inferred from outputs.
- **It has no independent verifier.** Nothing checks the explanation with a
  second model or a source of truth. Accuracy rests on Claude and on the
  skill's accuracy rules.
- **Claude account limits still apply.** Plan eligibility, usage limits, and
  code-execution availability are set by Anthropic.
- **Surfaces are separate.** A skill uploaded to claude.ai is not available in
  the API or Claude Code, and vice versa. An older build stays installed until
  it is deleted and replaced.
- **Interface details change.** Menu paths and what the interface shows as
  activation evidence may differ from the documentation.
- **The line budget is nearly spent.** The `SKILL.md` body is 485 of 500 lines
  (test guard 485). A new rule must displace or merge an old one.

## About rendering

Markdown has no font sizes and no text colour, and the surface decides how each
element looks.

- **Only `#` is visibly larger on claude.ai.** The render probe shows `##`,
  `###`, `####` and a bold line at one size, so depth below `##` comes from
  separators, lists and callouts.
- **Callouts render dimmer than body text** on claude.ai. The one sentence that
  must not be missed stays in body text.
- **Colour comes only from** `diff` fences, Mermaid `classDef` fills, and emoji.
- **Claude Code shows Mermaid as source**, so diagrams lose their value there.
- **Unverified on claude.ai:** whether `rect rgb(...)` highlights render in a
  `sequenceDiagram`, and whether every palette emoji renders on every device.
  The palette is limited to single code points from Emoji 11 or earlier.

## About the evidence

- **Human comprehension improvements are unproven.** No person has been tested.
  No experiment so far has measured comprehension in a way that could detect a
  difference (`research/EVIDENCE_AUDIT.md` §2.4).
- **The operation choice is a hypothesis.** It rests on automated fidelity
  screening of Gemini rewrites, learning-science literature, the project brief,
  and the owner's requests. Fidelity screening shows only that a rewrite did not
  obviously break the text. Its best scores were partly produced by rewrites
  that changed nothing.
- **Rewrite evidence may not transfer to generation.** All prior experiments
  rewrote existing answers with Gemini. The skill asks Claude to compose
  answers.
- **The layout evidence is thin.** Rounds 2–5 in `evaluation/layout_capture/`
  are one answer per prompt, two prompts per round, copied from claude.ai by the
  owner (a recorded exception to "nothing by hand"). Only round 2 records the
  invocation (`/socialized`), so they say nothing about natural activation, and
  consistency across runs is not measured. No round has been captured since
  Phase 9. The Approach B checks were one chat per prompt, with no baseline arm:
  the Phase 1 calibration pair (a student and a Go developer), and none yet for
  the Phase 2 short-fact and debugging prompts.
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
- **Most operations are untested hypotheses.** Presentation, visual, register,
  repair, persistence, work report, plain language, conversational voice, close,
  and the page shape have no outcome data of any kind yet.
- **The linters measure form only.** `lint_markdown.py` and `lint_response.py`
  read the text they are given. A response can pass every check and still be
  wrong, and neither can watch a live conversation. Their heuristics never gate.
- **Automated results characterise Claude Code, not claude.ai.** The harness
  runs `claude -p`, whose system prompt and scaffolding differ from claude.ai's;
  activation rates in particular do not transfer. The judge is a free-tier
  non-Anthropic model with a small daily quota, a screening instrument whose own
  reliability is reported as its order-flip rate. No result of its Claude-only
  acceptance test is recorded yet, and the `pilot16-cc` run holds no responses.
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

## Not in scope

There is no chatbot, API client, proxy, browser extension, or automated UI
control. The LLM judge (`scripts/judge.py`) is a labelled screening instrument
that never feeds S1–S7. The automated layout conformance score is planned
(V2 Phase 10) and not built.
