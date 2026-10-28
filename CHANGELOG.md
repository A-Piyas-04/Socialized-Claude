# Changelog

## Unreleased

### Token efficiency (Phase 4B, plugin v0.4.0)
- The shipped `SKILL.md` that loads on activation drops from 5,946 to 5,379
  local-estimate tokens (−9.5%, Anthropic's legacy public tokenizer). Claude Code's
  `plugin details` estimate drops from about 6.4k to about 5.8k. These are not
  measured API usage.
- The always-on core (Scope, Strategies, Steps 1–2, Accuracy rules, Reference files)
  now precedes the twelve operations, and Step 3 stays last. Claude Code re-attaches
  only the first 5,000 tokens of a skill after auto-compaction; the old layout lost
  part of the accuracy rules and all reference pointers there.
- Duplicates merged (mixed-task rule, two repair pushback bullets, two
  presentation unit bullets, a work-report restatement), Step 3 shortened, reference
  pointers say when to read each file. No rule removed; every phrase pinned by the
  Phase 3 and Phase 4 tests is unchanged. Still 12 operations and 15 variants.
- `treatment-selection.md` and `explanation-methodology.md` no longer contradict
  Phase 4 (they still prescribed a check question for beginners and confusion
  follow-ups, a takeaway on every teaching answer, and a figure per shaped idea).
- New `scripts/token_budget.py` reports every instruction surface by how it loads,
  with configurable budgets (`scripts/token_budgets.json`: `max` gates `--check`,
  `target` is advisory) and the pre-4B baseline (`scripts/token_baseline.json`).
  New `tests/test_token_budget.py` (15 tests; suite 463 passed, 1 skipped).
- Plugin `version` 0.3.0 → 0.4.0. Both artifacts regenerated. Moving the visual
  drawing grammar into an on-demand reference was evaluated and not implemented
  (see `docs/phase-4b-token-efficiency.md`).

### Communication refinement (Phase 4, policy v0.3.0, plugin v0.3.0)
- `op:close`: a check question is added **only** when the person asks to practise or
  be tested, the exchange is explicitly a tutorial, or one focused question resolves
  a real uncertainty — never on a coding deliverable, a fix, a decision, or a quick
  answer by category. The takeaway is optional. "I don't understand X" gets a
  clearer explanation of X, not a quiz. The forced per-category quiz is gone.
- `op:plain` / `op:presentation`: the mandatory retained section map is removed; a
  sentence roadmap or heading map is added only when a complex, multi-part answer
  genuinely needs orienting.
- `op:visual`: draw a visual only when it clarifies; prefer one strong
  representation per idea and add a second only for a materially different dimension;
  dropped the every-shaped-idea / every-section / final-third requirement; colour,
  status emoji and legends only when they speed a comparison; a diagram must not
  imply a guarantee the mechanism lacks. The interactive-version offer is made only
  when asked or clearly useful, never appended by default; artifacts stay opt-in.
- Accuracy rules + `core.md`: scope a product-specific implementation, version or
  default to its system; flag a common implementation as common not universal;
  separate a simplified mental model from precise internals; state concurrency,
  replication and durability assumptions instead of a categorical guarantee; keep
  the causal steps a requested mechanism needs.
- Quick-answer strategy: "answer directly and naturally", with "one sentence and
  stop" as the usual shape, not a rigid cap. The five strategies are preserved.
- The mandatory horizontal-rule-between-topics decoration was removed (compulsory
  formatting that served the policy, not the reader).
- `communication/core.md`, `strategies.md`, `controls.md`, and the policy README
  move to version 0.3.0 with the Phase 4 change table.
- Plugin `version` 0.2.0 → 0.3.0 (`version` pins installs). Both artifacts
  regenerated from the canonical skill; the two copies stay byte-identical.
- No new operation, marker, or variant: still 12 operations and 15 variants. New
  `tests/test_refinement_policy.py` (14 tests, suite now 448 passed, 1 skipped);
  `test_multiturn_policy.py` updated only for the two version pins. `SKILL.md` is at
  450/460 rendered and 498/500 raw lines — net +7 rendered, offset by consolidating
  redundant prose; no guard raised (see `docs/phase-4-implementation.md`).

### Adaptive conversation behaviour (Phase 3, policy v0.2.0, plugin v0.2.0)
- `SKILL.md` Step 1 gains item 5, "The conversation so far": read silently what a
  follow-up is doing (new task, expanding a point, confusion, a correction,
  feedback on the reply itself, a request for an example or depth, a preference)
  and whether a preference is standing or for one reply. No label is printed and
  no classifier is added.
- `op:repair` extended in place (not duplicated): answer the unresolved part first
  and drop what the earlier reply settled or the person has shown they know;
  change the explanatory method rather than the wording when the first attempt did
  not land; check a disputed claim before conceding, then correct it and whatever
  followed from it, or keep it with a reason.
- `op:persistence` extended: an instruction scoped to one reply ("for this
  answer", "this time") applies once and is dropped; unscoped ones carry forward.
- New accuracy rule: refer back only to what the conversation contains, say what
  is missing instead of reconstructing it, and claim no cross-session recall.
- Step 3 gains two gated checks (follow-up non-repetition; one-reply scope).
- `communication/strategies.md` gains an "Across turns" section with the four
  correction cases and shape-follows-task; `core.md` principle 9 gains preference
  scope; all three modules and the policy README move to version 0.2.0.
- Plugin `version` 0.1.0 → 0.2.0, because `version` pins installs and the shipped
  skill content changed. Both artifacts regenerated from the canonical skill via
  `package_skill.py` and `build_plugin.py`; the two copies stay byte-identical.
- No new operation, marker, or variant: still 12 operations and 15 variants. New
  `tests/test_multiturn_policy.py` (14 tests, suite now 434 passed); no existing
  test modified. `SKILL.md` is at 443/460 rendered and 492/500 raw lines — the
  next addition needs a consolidation (see `docs/phase-3-implementation.md`).
- Phase 4 still owns the closing-quiz, intro-preview, rigid-tutorial and
  duplicate-visual refinements; Phase 3 changed none of them.

### Claude Code plugin MVP (Phase 2, plugin v0.1.0)
- New `plugins/socialized/` plugin: `.claude-plugin/plugin.json` (name
  `socialized`, display name Socialized-Claude, version 0.1.0) and a
  `skills/socialized/` skill generated from the canonical `skill/socialized/`.
  The generated skill is byte-identical to `dist/socialized.zip`, so the plugin
  and the claude.ai skill behave the same.
- New `.claude-plugin/marketplace.json` (local marketplace) and
  `dist/socialized-claude-plugin.zip` (archive root `socialized/`).
- New `scripts/build_plugin.py` renders the plugin from the skill and, with
  `--check`, fails on drift. `tests/test_plugin_structure.py` adds 11 offline
  tests (manifest, sync, ZIP shape, marketplace); suite is now 410 passed.
- `claude plugin validate` passes for the plugin and the marketplace (CLI
  2.1.311). Directory-submission advisories (missing LICENSE and icon) are noted
  and do not affect the verdict or local/claude.ai install.
- No communication behaviour changed: the 12 operations, the Phase 1 intent
  section, the reference files, and `dist/socialized.zip` are untouched; no
  existing test was modified. Compatibility matrix, honest activation limits, and
  opt-in persistent-guidance options are in `docs/phase-2-implementation.md`.
  Communication refinements (intro previews, closing quizzes, rigid tutorials,
  redundant visuals) are recorded for Phase 4 in `docs/LIMITATIONS.md`.

### Communication policy modules (Phase 1, v0.1.0)
- New `communication/` modules at the repo root: `core.md` (universal
  principles and precedence), `strategies.md` (five intent strategies plus
  mixed-intent and scope boundaries), `controls.md` (depth, formatting, visual,
  density), and a `README.md` with the change table and integration rationale.
- The modules distil and index `skill/socialized/SKILL.md`; each rule names the
  operation or step that enforces it. They live outside the skill package (which
  is tested to contain exactly SKILL.md and its three references) and the skill
  does not load them at runtime, per the brief's "independent of Claude-specific
  packaging" and Risk D requirements.
- `SKILL.md` gains one compact, always-on section, "Match the communication
  strategy to the intent", exposing the five intent strategies as a priority list
  (teaching, coding, debugging, discussion, quick answers) so the installed skill
  carries them. It is not an operation, adds no markers, and applies the
  explanation operations only to the explanatory part of a reply, so non-teaching
  intents do not inherit the teaching structure. The 12 operations, the 4-file
  package, and the reference files are unchanged; all 399 tests pass with no test
  modified. Baseline preserved as the git tag
  `baseline-pre-v1.0.1-communication`.

### Skill (Socialized-Claude, visual depth)
- Visual budget: one visual per idea with a shape, no per-answer cap (the
  earlier two-per-answer cap is superseded). The hardest section gets its visual
  first, and the last third is supported at least as well as the first.
- Visuals show time (`sequenceDiagram` with labelled arrows), mark the key node
  with a distinct shape, group peers with shared `classDef` classes, use one
  colour code per answer, place two states side by side, and draw every
  quantity as bars. Content that changes over time ends with a one-line offer of
  an interactive version; artifacts stay opt-in.
- Presentation: backticked and glossed identifiers, `##`/`###` hierarchy with no
  bold line as a heading, **Deeper:** blocks over a complete narrative, specimens
  lifted into titled fenced blocks, tables capped at four columns and six words
  per cell, and the same treatment for the last section as the first.
- Close: a verifiable question (three options or one short answer) followed by
  its **Answer:**, and a takeaway compressed to an arrow chain or 25 words.
- The running example reaches every teaching section; the obvious-approach move
  repeats for every mechanism.
- Linter: `dense_table_cell`, `wide_table`, `bold_as_heading`,
  `uncaptioned_specimen`, `flat_visual`; heuristics `visuals_first_half`,
  `visuals_second_half`, `max_table_cell_words`, `heading_depth_max` never gate.
  Compactness guard raised to 460 rendered lines.

### Skill (Socialized-Claude)
- The skill id is `socialized` and the display name is Socialized-Claude. The id
  cannot contain "claude" (reserved-word check). `evaluation/runs/pilot16-cc`
  stays frozen as `explanation-lab`; the collector reads the skill id from the
  run's manifest.
- New operations: `visual` (markdown diagrams, contrasts, bars and status
  legend; one captioned artifact only when the person explicitly asks) and
  `close` (a takeaway, and one check question on teaching answers). Twelve
  operations, 15 variants, including `V_visual` and `V_close`.
- Presentation: paragraph and bullet limits, blank lines between units, numbered
  headings with a one-line map, specialist material boxed, horizontal rules
  between major topics. Examples stay one running case. Mechanism names the
  obvious approach that fails.
- Linter: `dense_paragraph`, `uncaptioned_visual`; legend emoji exempt when a
  list uses two or more; `visual_count` is a heuristic and never a gate.
  Compactness guard raised to 380 rendered lines.

### Skill (V1)
- `op:structure` renamed to `op:presentation` and rewritten as a positive
  operation: answer first, one idea per unit, form chosen from the content's
  shape (steps, tables for 3+ items on 2+ dimensions, labelled lists, fenced
  diagrams for branching flows, prose for a single causal chain), headings that
  state what a section establishes, at most two bolded sentences. The four
  prose-default prohibitions are gone; decorative structure, emoji as
  structure, whitespace padding and empty transitions are failure modes.
- New operations: `register` (three registers, practitioner default, with scope
  discipline folded in), `repair`, `persistence`, `work-report`, and`n  `plain` (sentence-level readability, reinstating T1's sentence rules). Ten
  operations in total.
- Accuracy rules: specific citations only when confident they exist; named
  researchers, papers and foreign or field terms glossed in the same sentence.
- Variants `pres`, `seq-pres`, `seq-mech-pres`, `reg`, `rep`, `persist`,
  `wrep`, `plain` (13 in total), mirrored as `V_*` conditions with their contrasts.

### Evaluation
- Automated collection with Claude Code (`scripts/collect_cc.py`): isolated
  sandbox per row, arm verified from the `system/init` event, real multi-turn
  conversations, frozen per-run builds, resumable, refuses `ANTHROPIC_API_KEY`.
- Automated screening judge (`scripts/judge.py`, `scripts/judgelib.py`): fact
  capture, both-orders pairwise preference with flip rate, `navigability` and
  `register_fit`; `scripts/judge_acceptance.py` tests the judge on archive
  answers; `scripts/screen_items.py` screens comprehension items for diagnostic
  power.
- Reframe: the evaluation is Claude-vs-Claude only. The judge is a regression guard; its
  acceptance test uses Claude answers under different conditions plus a floor of deliberately
  degraded answers, with the 0.20 flip cutoff and 0.80 floor shares fixed in code. Earlier
  cross-provider acceptance runs are kept in `research/judge_acceptance_superseded/`.
- Groq judge backend (default) behind the same interface; Gemini kept for the Gemma fallback.
- Rubric: `navigability` and `register_fit` (11 dimensions) and the
  preference-versus-comprehension rule.
- 12 new cases (45 in total): register, repair, decorative-structure controls,
  persistence (machine-checked standing constraints), work report.
- `scripts/structural_metrics.py` and `scripts/lint_response.py`, with a
  baseline for the 15 archive Claude answers (GPT answers are exemplar source only); summaries add structural
  descriptors and a persistence re-ask proxy, none of which feed S1–S7.

### Docs
- `COMMUNICATION_GRAMMAR.md` (every rule with its evidence label) and
  `COMMUNICATION_EXEMPLARS.md` (3 archive pairs, 9 constructed).

- Added `scripts/run_assistant.py`, an interactive clipboard helper for
  manual response collection. It copies each message, saves each copied
  response, fills the run sheet, pauses at skill on/off batch boundaries, and
  can resume. It does not interact with Claude's website. Covered by 14 tests,
  for 186 in total.

## 0.1.0 — 2026-10-26 (V0, experimental)

First implementation. Not yet evaluated in Claude.

### Skill
- `explanation-lab` skill with a scope gate, silent request reading, answer
  sizing, and two core operations: dependency ordering and mechanism.
- Three conditional operations: one mapped example, terms at first use, and
  formatting only for real shape.
- Accuracy rules (no invented mechanisms, hedges preserved) and natural
  delivery (no visible workflow or labels).
- References: per-request-type methodology, weak/better examples across four
  domains plus restraint cases, and selection, conflict, and failure-mode rules.
- Description of 196 characters, within claude.ai's 200-character limit.

### Research
- Evidence audit of the ExplanationLab 2026-10-26 archive, with a script that
  regenerates every cited number.

### Evaluation
- 33 held-out test cases, a 9-dimension anchored rubric with accuracy and
  adherence coding, and condition definitions (A, B, C natural, C explicit,
  optional D, ablation variants).
- Runbook for manual execution without an API.
- Human comprehension protocol with a draft item bank.
- Scripts: run sheet, blind packet, summary with bootstrap intervals and gated
  criteria, and Latin-square assignment.

### Tooling
- Validator covering the official frontmatter rules plus packaging, safety, and
  marker checks.
- Deterministic packager with ablation variants and manifests.
- 172 offline tests.
