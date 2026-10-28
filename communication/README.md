# Communication policy modules (v0.4.0)

Reusable communication policy for Socialized-Claude. Three modules:

| File | Purpose |
|---|---|
| `core.md` | Universal principles that hold across every task, with the precedence order. |
| `strategies.md` | Five intent-sensitive strategies (teaching, coding, debugging, discussion, quick answers), the across-turns guidance for follow-ups, mixed-intent, and scope boundaries. |
| `controls.md` | Depth, formatting, visual, and density controls. |

## Relationship to the skill

The production behaviour lives in `skill/socialized/SKILL.md` and its reference
files, already structured as twelve conditional operations. These modules **distil
and index** that policy into the three reusable surfaces the Phase 1 brief asked
for. Each rule here names the SKILL.md operation or step that enforces it, so the
modules stay a map of the skill rather than a second, divergent copy of it.

Policy version `0.4.0` tracks these modules (`0.1.0` was Phase 1; `0.2.0` added the
Phase 3 across-turns guidance; `0.3.0` added the Phase 4 communication refinements —
selective quizzes, previews, and visuals, and tighter epistemic scoping; `0.4.0`
restores the visual-coverage and paragraph-density rules Phase 4 removed, keeping
the selective quiz, preview, and demo-offer behaviour). The
skill's own version history stays in
`CHANGELOG.md`; the baseline before this work is the git tag
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

## Change summary (Phase 3 — across turns)

| Area | Action | Result |
|---|---|---|
| `op:repair`, `op:persistence` | Extend | Refined in place, not duplicated: repair gains smallest-gap-first, change-the-method, and check-before-conceding; persistence gains one-reply preference scope. |
| Follow-up purpose reading | Add | `SKILL.md` Step 1.5 — read silently what the follow-up is doing, and whether a preference is standing or one-reply. No labels printed, no classifier. |
| Conversation continuity | Add | Accuracy rule: refer back only to what the conversation contains; name what is missing; claim no cross-session recall. |
| Across-turns policy | Add | `strategies.md` → "Across turns", including the four correction cases and shape-follows-task. |
| 12 operations, 5 strategies, packaging | Preserve | No new `op:` marker, no new operation, no new variant. ZIP layouts and install paths unchanged. |

Phase 3 adds no parallel conversation engine: it is policy inside the existing
operations, planned silently over the turns the host supplies.

## Change summary (Phase 4 — communication refinement)

| Area | Action | Result |
|---|---|---|
| Closing quizzes | Conditionalize | `op:close` and `controls.md` add a check question only when the person asks for practice, the exchange is a tutorial, or a focused check resolves a real uncertainty — never on code, fixes, decisions, or quick answers by category. "I don't understand X" gets a clearer explanation, not a quiz. |
| Intro previews / section maps | Make optional | `op:plain` no longer keeps a mandatory section map; `op:presentation` adds a heading map only when a long answer needs orienting. |
| Redundant visuals | Value-based selection | `op:visual` draws a figure only when it clarifies, prefers one strong representation per idea, and drops the every-section / final-third requirement. Colour, status emoji, and legends only when they speed a comparison. *(The coverage floor was restored in Phase 4C; one-representation-per-idea and the colour gate stand.)* |
| Automatic demo offers | Remove default | The interactive-version offer is made only when asked or clearly useful, never appended by default. |
| Overgeneralized claims | Scope assumptions | Accuracy rules and `core.md` scope product-specific implementations, separate mental models from internals, and state concurrency/replication assumptions instead of categorical guarantees. |
| 12 operations, 5 strategies, packaging | Preserve | No new `op:` marker, operation, or variant; `SKILL.md` stays within its line budgets; both install paths regenerated. |

Phase 4 removes formatting that served the policy rather than the reader; it keeps
the strengths of Phases 1–3 (causal mechanism, running examples, visual literacy,
adaptive register, multi-turn repair).

## Change summary (Phase 4C — visual communication restored)

Phase 4 over-corrected: it replaced the visual-coverage floor with a negative rule
and turned the pre-send check from "does each shaped idea have its visual?" into a
pruning-only check. Answers drifted toward long prose. Phase 4C reverses that drift
without reinstating anything Phase 4 was right to remove.

| Area | Action | Result |
|---|---|---|
| Visual coverage | Restore | `op:visual` draws a visual for **each** shaped idea, with no cap per answer, and supports the last third at least as well as the first. The negative "do not require a visual for every shaped idea, every section, or the final third" is gone. |
| Pre-send check | Restore | Step 3 asks again whether each idea with a shape has its visual, including the hardest section and the last third, so a missing figure can be added and not only a redundant one pruned. |
| Visual redundancy | Keep Phase 4 | One representation per idea; a second only for a materially different dimension; colour, status emoji, and legends only where they speed a comparison. |
| Paragraph density | Restore | `op:presentation` starts a new paragraph when the idea changes even when the current one is short; Step 3 checks list-item length as well as paragraph and table-cell length. |
| Section separation | Restore | A horizontal rule (`---`) between major topics in an answer of three or more sections. |
| Form in non-teaching replies | Add | The strategy section picks the form from the content in **every** strategy — a table for three or more options against their tradeoffs, a diagram for a flow or an interaction, steps for a procedure, a fenced block for code, prose for a single chain or a casual reply. |
| Decorative structure | Restore | Step 3 asks whether every heading, list, table, **diagram**, and bold sentence marks a real division or only decorates. |
| Quizzes, previews, demo offers, artifacts | Preserve | Unchanged from Phase 4: no mandatory check question, no automatic section map, no appended interactive offer, artifacts opt-in. |
| Technical depth | Preserve | `core.md` principle 11 splits a dense paragraph into connected units rather than dropping a mechanism. No word caps were added. |

### Final calibration

Live conversational tests accepted the restoration and found the restored rules too
prescriptive. The requirements became strong, context-sensitive preferences. No
operation, marker, variant or module was added, so the modules stay at v0.4.0.

| Area | Action | Result |
|---|---|---|
| Visual coverage | Soften to a preference | "**Prefer** a visual for such an idea … **leave one out where the prose already makes the relationship plain**". No quota and no cap, and no per-idea requirement. |
| Long answers | Soften | "Keep the support **even across the answer**, so a later section that needs a figure gets one" replaces the final-third floor. |
| Table cells | Allow sentences | "One idea, about six words where a phrase will do and a short sentence where the comparison needs one." Step 3 asks whether a cell stays scannable. |
| Section separator | Soften | The horizontal rule goes where an answer of three or more sections **turns to a new topic**. |
| Accuracy | Strengthen in place | `core.md` principle 6 and the skill's accuracy rules name the settings a guarantee depends on, state an assumed workload or scale the person has not given, and carry no database's or broker's behaviour over to another unchecked. |
| Everything else | Keep | The comparison-table cue, the Mermaid grammar, paragraph density, heading rules, the Step 3 scannability and decoration checks, and the form-from-content line are unchanged. Mandatory quizzes, takeaways, previews, unrequested artifacts and templates stay absent. |

## What this does not establish

These are static policy documents. Passing the repository's structural and
packaging checks shows the skill is well-formed; it does not show that
communication quality improved. That is verified only through real Claude.ai
conversations.
