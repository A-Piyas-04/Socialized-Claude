# Architecture — Socialized-Claude

Current as of version 2.2.0 (`metadata.version: 2.2.0`): the V2 Phase 9 layout
plus Approach B Phases 1 and 2 (`docs/ADAPTIVE_COMMUNICATION_PLAN.md`).

## What the skill does

Socialized-Claude is an instructions-only Claude Skill (id `socialized`; the
display name cannot be the id, because a skill id may not contain "claude").
When Claude loads it, the skill guides Claude to compose explanations that:

1. **Answer first.** The first one or two sentences reply to the question asked,
   before any background, list, or heading except the title.
2. **Lead with what the intent needs**: a fact, a causal chain, numbered steps,
   a recommendation with its tradeoff, or a diagnosis with one fix.
3. **Calibrate idea by idea**: sort the ideas an answer rests on into known,
   missing and uncertain, start from the nearest known one, and teach only what
   is missing.
4. **Order ideas by dependency.** Nothing is used before its groundwork, and a
   missing prerequisite is taught briefly rather than merely named.
5. **Make the causal mechanism explicit** for why and how questions: what
   triggers what, the obvious approach and how it fails, and the tradeoff that
   follows.
6. **Follow one page shape** for any answer of two or more sections: a `#`
   title with a `---` under it, the answer, an overview diagram for a chain or
   process, a one-line map, numbered `##` sections split by `---`, a 🙋 reader's
   question, short glosses on first use, and a 🎯 takeaway. A 🧠 analogy
   callout and a 🧪 check callout appear only where the intent calls for them.
7. **Show shape instead of describing it**: Mermaid flowcharts and sequence
   diagrams, tables, block-character bars, `diff` contrasts, status and
   navigation emoji, all as markdown. An artifact (HTML, SVG, interactive
   widget) is built only on claude.ai, and only when the person explicitly asks.
8. **Read like a person talking**: plain one-claim sentences, active voice,
   direct address, contractions, and the reader's next question written into
   the answer.
9. **Render safely**: closed fences, plain table separator rows, matching cell
   counts, plain Mermaid labels, no heading jumps, palette-only emoji.

It also tells Claude to **leave non-teaching requests alone**, to keep length
proportional, and to preserve accuracy and uncertainty.

The skill does not change Claude's model, call any other model or service, or
run code.

## Files and progressive disclosure

```
socialized/
├── SKILL.md                         Level 2: loaded when Claude triggers the skill
├── LICENSE.txt                      MIT; added by the build, never read by Claude
└── references/
    ├── explanation-methodology.md   Level 3: behaviour by request type (§1–14),
    │                                strategy by intent (§15), repair (§16),
    │                                work reports (§17)
    ├── explanation-examples.md      Level 3: weak/better pairs as complete laid-out
    │                                answers, visual forms, restraint cases
    ├── treatment-selection.md       Level 3: selection defaults, conflicts,
    │                                length budget, failure modes
    ├── conversation-grammar.md      Level 3: worked 🙋 question patterns, register
    │                                ladder, direct address and contractions
    ├── emoji-palette.md             Level 3: 153 navigation icons in seven groups,
    │                                plus the closed status six
    └── layout-exemplars.md          Level 3: three gold answers in the page shape
                                     (full build only)
```

| Level | What | When it is in Claude's context |
|---|---|---|
| 1 | `name` + `description` (164 characters) | Always, in every chat where the skill is enabled |
| 2 | `SKILL.md` body (485 source lines, 420 rendered) | Only after Claude decides the request matches the description |
| 3 | Reference files | Only if Claude chooses to read one for the current request |

`SKILL.md` alone is a complete working skill. The references cover harder cases
and bulk material (the palette, the gold answers), so a short factual exchange
never pays their context cost.

## The workflow inside SKILL.md

In file order:

1. **Scope gate.** Is this a request to understand something? If not, respond
   normally. Three always-on pointers route standing instructions, corrections,
   and work reports to their operations even when nothing is explained.
2. **Page shape.** The slot order for answers of two or more sections. Each slot
   sits inside its operation's markers, so a single-operation build carries only
   its own slots. "The shape is fixed; the wording never is." The 🧠 slot fills
   only in a why, how or walkthrough answer with nothing known to lean on, and
   the 🧪 slot only for a learner.
3. **Step 1: read the request (silently).** The intent (answer, why or how,
   walk me through, decide, debug), the reader idea by idea (known, missing,
   uncertain) and their register (beginner, practitioner, expert, or mixed;
   practitioner by default), the one to three missing ideas, and the requested
   size and form.
4. **Step 2: lead with what the intent needs.** Answer first, then one default
   per intent, with a pointer to methodology §15 for code and mixed intents. A
   requested deliverable (code, an email, JSON) comes back in its own form, and
   an explicit size or form request overrides every default.
5. **Thirteen operations.** Ordering, mechanism, one running example, terms,
   plain sentences, conversational voice, presentation, visual, register,
   repair, persistence, work report, and close. Each carries its own "use when"
   and "skip when" rules, and every rule names an action.
6. **Accuracy rules (always on).** No invented mechanisms or facts, hedges
   preserved, simplify expression rather than substance, citations only when
   certain.
7. **Markdown that renders (always on).** Seven rules covering fences, pipes,
   the separator row, cell counts, Mermaid labels, heading steps, the blank line
   before `---`, and palette-only emoji.
8. **Step 3: check before sending (silently).** Twelve labelled checks (Answer,
   Order, Mechanism, Example, Terms, Sentences, Voice, Layout, Visuals, Close,
   Markdown and accuracy, Tone). Each operation's check sits inside its markers.
9. **Reference files.** One line per reference saying when to read it.

## How operations are selected

The skill starts from "use nothing" and adds an operation only when Claude can
name the gap it fills for this reader (`references/treatment-selection.md` §1).
Conflicts are resolved by fixed rules (§2):

- directness beats strict ordering for specific questions
- the user's stated length beats everything
- expertise beats scaffolding
- accuracy beats simplicity
- the example carries the answer; the analogy sits beside it
- the answer comes first; the scenario opens the first section
- a practitioner still gets short glosses, and an analogy only where nothing
  they know shows the mechanism; an expert gets neither
- intent picks the devices: decisions and debugging get no analogy and no quiz
- size comes from the `#` title, not from deeper headings, because `##`, `###`
  and `####` render alike on claude.ai
- the page shape is fixed; the wording never is

When something must be cut, a priority list says what goes first (§3). This
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
| Example rules (one running case, mapped, illustrative numbers marked) | **Observed**: T4's added examples carried invented specifics; worked-example literature (L2) | Guardrail plus hypothesis |
| Presentation: answer first, one idea per unit, form matched to shape (from T5) | V0's deferral rested on a detector artifact (**Observed**: 8/10 serious T5 verdicts were list-number triggers); illusion-of-fluency literature (L2) | **Provisional (hypothesis)** |
| Register: three registers, practitioner default, practitioner glosses | User reports; expertise-reversal literature (L2); round-2 answers left terms unglossed under the old practitioner rule | **Provisional (hypothesis)** |
| Repair, persistence, work reports | User reports (not held in this repository) | **Provisional (hypothesis)** |
| Plain language (sentence level, from T1) | T1's fidelity record (**Observed**: 7/10 clean, no no-op outputs); cognitive-load literature (L2) | **Provisional (hypothesis)** |
| Conversational voice, visual, close | User requests (`docs/SKILL_UPGRADE_PLAN.md`) | **Provisional (hypothesis)** |
| `#` title, `##` only, depth from `---` and callouts | **Observed**: the claude.ai render probe shows only `#` visibly larger; blockquotes render dimmer | Renderer constraint |
| Page shape slots | claude.ai rounds 2–5, one hand-supplied answer per prompt (`evaluation/layout_capture/`) | **Provisional**: layout follows the rules; consistency and comprehension unmeasured |
| Citation integrity | Second-hand figure quoted in the V1 addendum | Engineering choice |
| Audience calibration (from T6) | Expertise-reversal literature (L2); T6 itself was barely exercised (6/7 clean outputs unchanged) | Engineering choice |
| Length budget and scope gate | The brief's anti-patterns; Experiment 2 length inflation | Engineering choice |
| 164-character description | claude.ai Help Center limit of 200 characters | Platform requirement |

**Nothing in the skill is validated as improving comprehension.** The evaluation
framework exists to test it. The V1 rules and their labels are listed in
`COMMUNICATION_GRAMMAR.md`; the later changes are recorded in
`docs/SKILL_UPGRADE_PLAN.md` (Phases 1–4) and `docs/SKILL_UPGRADE_PLAN_V2.md`
(Phases 5–10).

## Ablation support

Operation-specific blocks in the source are wrapped in HTML-comment markers:

```
<!-- op:mechanism -->
...
<!-- /op:mechanism -->
```

A block tagged with several operations (`op:sequencing,examples`) is kept only
when all of them are enabled. The gold answers in `layout-exemplars.md` sit in
one block tagged with all six shape operations, so only the `full` build ships
them.

`scripts/package_skill.py` strips every marker for the production ZIP. With
`--variant`, it also removes the blocks of disabled operations:

| Variant | Operations kept |
|---|---|
| `core` | none (scope, page-shape answer slot, strategy, accuracy, markdown, delivery) |
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
| `plain` | plain language |
| `conv` | conversational voice |
| `visual` | visual |
| `close` | close |
| `full` | all thirteen (production) |

All variants keep **identical name, description and version stamp**, so
automatic activation sees the same metadata. Tests enforce this, and also that
each variant contains exactly its operations. `evaluation/conditions.json` has a
`V_*` sweep arm for every variant except `conv`, which can be added in one data
edit when the sweep runs.

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
  sorted entries, LF line endings), adds the repository `LICENSE` as
  `LICENSE.txt`, and validates the ZIP itself after building.
  It writes a manifest with SHA-256 hashes, which evaluation rows record so
  results trace back to an exact skill build.
- Tests hold tighter line guards than the validator: the source body at 485
  lines or fewer, and the rendered full build under 460.
- Anthropic's own `skill-creator/scripts/quick_validate.py` was run against the
  extracted V0 production and `seq` ZIPs, and reported "Skill is valid!" for
  both. It is not vendored here and has not been re-run on the V2 build.

## Offline checks on answers

Two linters read a response file. Neither is wired into the evaluation harness,
and neither gates the skill text.

- `scripts/lint_markdown.py`: renderer safety. Exit 1 on any break. Codes:
  `unclosed_fence`, `nested_fence`, `table_pipe_mismatch`,
  `broken_table_separator`, `wide_table`, `mermaid_label`, `heading_jump`,
  `emoji_outside_palette`.
- `scripts/lint_response.py` (over `scripts/structural_metrics.py`): structural
  flags such as `dense_paragraph`, `dense_table_cell`, `bold_as_heading`,
  `emoji_structure`, `linear_ascii_flow`, `uncaptioned_visual`, plus labelled
  heuristics that never gate (`icon_count`, `visual_count`, `whitespace_ratio`,
  `heading_count`, `answer_first_offset`, and others). The navigation icon set
  is parsed from `emoji-palette.md`, so the two cannot drift.

`tests/test_examples_shape.py` requires every fenced answer in
`explanation-examples.md` and `layout-exemplars.md` to pass both with zero flags.

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
- **How markdown renders.** Heading sizes, blockquote colour and Mermaid support
  are set by the surface; Claude Code shows Mermaid as source.
- **What the interface shows** as activation evidence.

## Evaluation architecture (summary)

See `evaluation/README.md`. Conditions A (normal), B (strong generic prompt),
C (skill, natural and explicit), and optional D (skill text pasted as a prompt)
can be run by hand over 45 test cases. Responses are blinded and scored on 11
anchored dimensions, with separate accuracy coding, adherence codes, and ranks.
Activation is recorded by the operator. Comprehension is measured only with
human pre/post/transfer tests.

The automated harness (`evaluation/AUTOMATED_HARNESS.md`) collects the same run
sheets with Claude Code instead: one sandbox per row, the arm verified from the
`system/init` event, multi-turn cases sent as live turns in one session, and each
run pinned to its own frozen skill build (`<run>/skill_build/`). An automated
non-Anthropic judge (Groq by default) then screens fact capture and both-orders
pairwise preference, and `scripts/lint_response.py` adds structural descriptors.
These characterise the skill text on the Claude Code surface, are screening
instruments rather than the human evaluation, and never feed S1–S7.

Layout on claude.ai is tracked separately in `evaluation/layout_capture/`
(rounds 2–5, hand-supplied by the owner, with lint output per round) against
the prompts in `evaluation/layout_prompts.json`. Phase 10 of the V2 plan replaces
this with an automated conformance score; it is not built yet.
