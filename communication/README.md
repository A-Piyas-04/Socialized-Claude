# Communication policy modules (v0.8.0)

Reusable communication policy for Socialized-Claude. Three modules:

| File | Purpose |
|---|---|
| `core.md` | Universal principles that hold across every task, with the precedence order. |
| `strategies.md` | Five intent-sensitive strategies, across-turns handling, and the scope boundaries. |
| `controls.md` | Depth, presentation, example, visual, icon, closing and density controls. |

## These modules index the skill; they are not a second copy of it

The production behaviour lives in `skill/socialized/SKILL.md` and its reference
files, structured as twelve conditional operations. These modules **distil and
index** that policy into the three reusable surfaces the Phase 1 brief asked for.
Each entry names the SKILL.md operation or step that states the rule in full.

Until v0.8.0 each module carried its own wording of the same rules. Six rounds of
revision changed the skill and the modules at different rates, so the two
diverged — the modules still held numeric thresholds the skill had dropped. The
2026-10-29 communication simplification turned them into indexes so there is one
wording of each rule and nothing to keep in sync
(`docs/COMMUNICATION_SIMPLIFICATION_AUDIT.md`).

The skill does not read these modules at runtime, and no critical behaviour
depends on them being loaded. The critical teaching behaviour is embedded
directly in `SKILL.md`.

## Why these files are at the repo root, not inside the skill

The skill package is validated and tested to contain exactly `SKILL.md` and its
three `references/` files. The brief (§5) requires the modules to be "independent
of Claude-specific packaging" and warns (Risk D) against assuming that creating a
file makes Claude read it. Placing the modules inside the skill would either
break packaging or add files the skill never loads. So they live here, as source
the skill is built to agree with — not as runtime dependencies.

## Version history

Policy version `0.8.0` tracks these modules. The skill's own version history is
in `CHANGELOG.md`; the baseline before this line of work is the git tag
`baseline-pre-v1.0.1-communication`.

| Policy | What it was |
|---|---|
| 0.1.0 | Phase 1: the three modules created. |
| 0.2.0 | Phase 3: across-turns guidance for follow-ups, corrections and mixed intent. |
| 0.3.0 | Phase 4: communication refinement — selective quizzes, optional previews, value-based visuals, tighter epistemic scoping. |
| 0.4.0 | Phase 4C: the visual-coverage and paragraph-density rules Phase 4 removed, restored and then calibrated to preferences. |
| 0.5.0 | Pre-release communication-quality recovery — where information belongs between a table, a figure and the prose beside it. |
| 0.6.0 | Communication-experience upgrade — semantic icons as navigation aids, architecture diagrams as a named form. |
| 0.7.0 | Communication priority correction — one planning order, conflicting instructions removed rather than added to. |
| 0.8.0 | Communication simplification — the accumulated counting rules and formatting mandates removed, the four documentation surfaces reduced to one source, icons returned from a default to an option. |

Each round's reasoning is in `docs/`: `phase-4-implementation.md`,
`phase-4c-visual-restoration.md`, `communication-recovery.md`,
`communication-experience-upgrade.md`, `communication-priority-correction.md`,
and `COMMUNICATION_SIMPLIFICATION_AUDIT.md`. Those reports hold the per-round
change tables that used to be duplicated here.

The behavioural reference for acceptance is `docs/COMMUNICATION_BASELINE.md`.

## What this does not establish

These are static policy documents. Passing the repository's structural and
packaging checks shows the skill is well-formed; it does not show that
communication quality improved. That is verified only through real Claude
conversations.
