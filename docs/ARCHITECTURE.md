# Architecture — Explanation Lab V0

## What the skill does

Explanation Lab is an instructions-only Claude Skill. When Claude loads it, the
skill guides Claude to compose explanations that:

1. **Order ideas by dependency.** Nothing is used before its groundwork, and a
   missing prerequisite is taught briefly rather than merely named.
2. **Make the causal mechanism explicit** for why and how questions: what
   triggers what, why the mechanism exists, and the tradeoff that follows.
3. Apply three **conditional** operations only when they fill a specific gap:
   one mapped example, a definition at first use, and formatting that follows
   the content's real shape.

It also tells Claude to **leave non-teaching requests alone**, to keep length
proportional, and to preserve accuracy and uncertainty.

The skill does not change Claude's model, call any other model or service, or
run code.

## Files and progressive disclosure

```
explanation-lab/
├── SKILL.md                              Level 2: loaded when Claude triggers the skill
└── references/
    ├── explanation-methodology.md        Level 3: per-request-type behaviour
    ├── explanation-examples.md           Level 3: weak/better pairs + restraint cases
    └── treatment-selection.md            Level 3: conflicts, length budget, failure modes
```

| Level | What | When it is in Claude's context |
|---|---|---|
| 1 | `name` + `description` (196 characters) | Always, in every chat where the skill is enabled |
| 2 | `SKILL.md` body (about 180 lines, 1,500 words) | Only after Claude decides the request matches the description |
| 3 | Reference files | Only if Claude chooses to read one for the current request |

`SKILL.md` alone is a complete working skill. The references cover harder cases,
so a short factual exchange never pays their context cost.

## The workflow inside SKILL.md

1. **Scope gate.** Is this a request to understand something? If not, respond
   normally.
2. **Read the request (silently).** Work out the actual question type, what the
   user already knows (their vocabulary, code, background, earlier turns), the
   one to three missing ideas, and the requested size.
3. **Size the answer.** Defaults per request type. An explicit length request
   overrides all of them.
4. **Operations.** Dependency ordering, mechanism, example, terms,
   presentation, register, repair, persistence, work report. Each carries its
   own "use when" and "skip when" rules, and every rule names an action.
5. **Accuracy rules.** No invented mechanisms or facts, hedges preserved,
   simplify expression rather than substance.
6. **Check before sending (silently).**
7. **Deliver naturally.** No visible workflow, no internal labels, no template
   headings.

## How operations are selected

The skill starts from "use nothing" and adds an operation only when Claude can
name the gap it fills for this reader (`references/treatment-selection.md`).
Conflicts are resolved by fixed rules:

- directness beats strict ordering for specific questions
- the user's stated length beats everything
- expertise beats scaffolding
- accuracy beats simplicity

When something must be cut, a priority list says what goes first. This
selectivity is the main design difference from the earlier "structured
pedagogical" prompt, which asked for every technique at once and roughly doubled
answer length (`research/EVIDENCE_AUDIT.md` §2.1).

## What is research-backed and what is provisional

Labels follow `research/EVIDENCE_AUDIT.md`.

| Element | Basis | Status |
|---|---|---|
| Ordering by dependency (from T2) | Best fidelity record in Experiment 3 (inflated by no-op outputs); prerequisite-structure literature (L2) | **Provisional (hypothesis)**: no comprehension evidence |
| Mechanism (from T3) | The project brief's problem statement; no supporting experiment | **Provisional (hypothesis)**: highest observed fidelity risk, so guarded |
| Ban on signposting and naming-without-teaching | **Observed**: T2's template produced 13 signposting phrases and one false dependency claim | Evidence-driven guardrail |
| Ban on meta-commentary; hedges preserved; no certainty creep | **Observed**: T3 produced 8 meta-comments, 4 certainty and 2 hedge-loss flags, and a corrupted phrase | Evidence-driven guardrail |
| Example rules (one, mapped, illustrative numbers marked) | **Observed**: T4's added examples carried invented specifics; worked-example literature (L2) | Guardrail plus hypothesis |
| Presentation: answer first, one idea per unit, form matched to shape (from T5) | V0's deferral rested on a detector artifact (**Observed**: 8/10 serious T5 verdicts were list-number triggers); illusion-of-fluency literature (L2) motivates the guardrail | **Provisional (hypothesis)** |
| Register: three registers, practitioner default, no characterising the person | User reports; expertise-reversal literature (L2) | **Provisional (hypothesis)** |
| Repair, persistence, work reports | User reports (not held in this repository) | **Provisional (hypothesis)** |
| Citation integrity | Second-hand figure quoted in the V1 addendum | Engineering choice |
| Audience calibration (from T6) | Expertise-reversal literature (L2); T6 itself was barely exercised (6/7 clean outputs unchanged) | Engineering choice |
| Length budget and scope gate | The brief's anti-patterns; Experiment 2 length inflation | Engineering choice |
| 196-character description | claude.ai Help Center limit of 200 characters | Platform requirement |

**Nothing in the skill is validated as improving comprehension.** The evaluation
framework exists to test it. Every V1 rule and its label is listed in
`COMMUNICATION_GRAMMAR.md`.

## Ablation support

Operation-specific blocks in the source are wrapped in HTML-comment markers:

```
<!-- op:mechanism -->
...
<!-- /op:mechanism -->
```

A block tagged with several operations (`op:sequencing,examples`) is kept only
when all of them are enabled.

`scripts/package_skill.py` strips every marker for the production ZIP. With
`--variant`, it also removes the blocks of disabled operations:

| Variant | Operations kept |
|---|---|
| `core` | none (scope, calibration, accuracy, delivery) |
| `seq` | ordering |
| `mech` | mechanism |
| `seq-mech` | ordering + mechanism |
| `pres` | presentation |
| `seq-pres` | ordering + presentation |
| `seq-mech-pres` | ordering + mechanism + presentation |
| `reg` | register |
| `rep` | repair |
| `persist` | persistence |
| `wrep` | work report |
| `full` | all nine (production) |

All variants keep **identical name and description**, so automatic activation
sees the same metadata. Tests enforce this, and also that each variant contains
exactly its operations.

## Packaging and validation

- `scripts/validate_skill.py` checks:
  - frontmatter keys and the official name rules (lowercase and hyphens, ≤ 64
    characters, no "anthropic" or "claude")
  - the description: non-empty, no angle brackets, ≤ 1,024 characters for the
    API and ≤ 200 for claude.ai
  - an exact-case `SKILL.md`, a folder name matching the skill name, and a body
    under 500 lines
  - that referenced files exist, with no escaping or absolute paths and no
    backslashes
  - that references are one level deep, and reference files over 100 lines
    have a contents section
  - that operation markers are balanced
  - for secrets and external-inference or network code
- `scripts/package_skill.py` builds a **deterministic** ZIP (fixed timestamps,
  sorted entries, LF line endings) and validates the ZIP itself after building.
  It writes a manifest with SHA-256 hashes, which evaluation rows record so
  results trace back to an exact skill build.
- Anthropic's own `skill-creator/scripts/quick_validate.py` was also run against
  the extracted production and `seq` ZIPs during development, and reported
  "Skill is valid!" for both. It is not vendored here.

## Why no external API is needed

The skill is plain Markdown that Claude reads inside the user's own Claude
session. Claude generates the explanation itself. There is no model call, no
server, no key, and no network access. The validator rejects provider endpoints,
API-key variables, SDK imports, and HTTP-client code inside the skill folder.

## What Claude controls, not this implementation

- **Whether the skill loads.** Claude matches requests against the description.
  We can only write a good description and test it.
- **Whether reference files are read.** `SKILL.md` suggests when each one helps.
- **How faithfully the instructions are followed.** This varies with the model,
  the conversation context, other enabled skills, and product-side system
  prompts.
- **Which model runs.** The user's model selection.
- **What the interface shows** as activation evidence.

## Evaluation architecture (summary)

See `evaluation/README.md`. Conditions A (normal), B (strong generic prompt),
C (skill, natural and explicit), and optional D (skill text pasted as a prompt)
can be run by hand. Responses are blinded and scored on 11 anchored dimensions,
with separate accuracy coding, adherence codes, and ranks. Activation is
recorded by the operator. Comprehension is measured only with human
pre/post/transfer tests.

The automated harness (`evaluation/AUTOMATED_HARNESS.md`) collects the same run
sheets with Claude Code instead: one sandbox per row, the arm verified from the
`system/init` event, multi-turn cases sent as live turns in one session, and each
run pinned to its own frozen skill build (`<run>/skill_build/`). An automated
non-Anthropic judge then screens fact capture and both-orders pairwise
preference, and `scripts/lint_response.py` adds structural descriptors. These
characterise the skill text on the Claude Code surface, are screening
instruments rather than the human evaluation, and never feed S1–S7.
