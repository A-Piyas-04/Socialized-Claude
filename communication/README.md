# Communication policy modules (v0.1.0)

Reusable communication policy for Socialized-Claude, Phase 1. Three modules:

| File | Purpose |
|---|---|
| `core.md` | Universal principles that hold across every task, with the precedence order. |
| `strategies.md` | Five intent-sensitive strategies (teaching, coding, debugging, discussion, quick answers) plus mixed-intent and scope boundaries. |
| `controls.md` | Depth, formatting, visual, and density controls. |

## Relationship to the skill

The production behaviour lives in `skill/socialized/SKILL.md` and its reference
files, already structured as twelve conditional operations. These modules **distil
and index** that policy into the three reusable surfaces the Phase 1 brief asked
for. Each rule here names the SKILL.md operation or step that enforces it, so the
modules stay a map of the skill rather than a second, divergent copy of it.

Policy version `0.1.0` tracks these modules. The skill's own version history stays
in `CHANGELOG.md`; the baseline before this phase is the git tag
`baseline-pre-v1.0.1-communication`.

## Why these files are at the repo root, not inside the skill

The skill package is validated and tested to contain exactly `SKILL.md` and its
three `references/` files. The brief (§5) requires the modules to be "independent
of Claude-specific packaging" and warns (Risk D) against assuming that creating a
file makes Claude read it. Placing the modules inside the skill would either break
packaging or add files the skill never loads. So they live here, as source the
skill is built to agree with — not as runtime dependencies.

The skill does not read these modules at runtime, and no critical behaviour
depends on them being loaded. The critical teaching behaviour is already embedded
directly in `SKILL.md`.

## Change summary (Phase 1)

What the brief asked to preserve, relax, or add, and what was actually done:

| Area | Action | Result |
|---|---|---|
| Language, grammar, mechanism, sequencing, visuals | Preserve | Unchanged; already enforced by `op:plain`, `op:mechanism`, `op:sequencing`, `op:presentation`, `op:visual`. |
| Mandatory headings / summaries / quizzes / examples / diagrams | Relax | Already conditional in SKILL.md (3+ sections for numbered headings; teaching/beginner/confusion for check questions; shape-driven for visuals). No further relaxation needed. |
| Five intent strategies | Add | Full guidance in `strategies.md`; a compact priority list is also embedded in `SKILL.md` ("Match the communication strategy to the intent") so the installed skill carries it. |
| Universal principles + precedence | Add | `core.md`. |
| Depth / formatting / density controls | Add | `controls.md`, mapped to `op:presentation`, `op:visual`, `op:close`, Step 2. |
| SKILL.md entry point and packaging | Preserve | The 4-file package and 12-operation set are unchanged; one non-operation, always-on section was added. Structural tests stay green with no edits. |

The five intent strategies are embedded in `SKILL.md` as a compact priority list
(which intent leads with what), while their full detail stays in `strategies.md`.
The section chooses priorities, not templates, and applies the explanation
operations only to the explanatory part of a reply, so coding, debugging,
discussion, and quick answers do not inherit the teaching structure.

## What this does not establish

These are static policy documents. Passing the repository's structural and
packaging checks shows the skill is well-formed; it does not show that
communication quality improved. That is verified only through real Claude.ai
conversations.
