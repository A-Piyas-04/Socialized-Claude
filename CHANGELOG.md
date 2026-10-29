# Changelog

## Unreleased

### Communication-experience upgrade (policy v0.6.0, plugin v0.7.0)
- Owner request after the v0.5.0 recovery: six presentation weaknesses (dense
  paragraphs, congested tables, diagram/prose repetition, weak hierarchy, limited
  visual variety, missing semantic icons). Brief `temp/re-enhance--communication.md`;
  write-up `docs/communication-experience-upgrade.md`. Refined in place; still 12
  operations and 15 variants. No quiz, takeaway, preview, visual quota, emoji
  template or response template was added.
- `op:presentation`: one primary idea per paragraph; four sentences / 80 words is a
  ceiling, not a target; two independently important claims never share a paragraph;
  lists only for genuinely distinct points; a table cell makes the primary decision
  visible at a glance.
- `op:sequencing`: internal priority is core understanding, then the supporting
  mechanism, then optional advanced detail, in separate units, not as a template.
- `op:visual`: architecture diagrams (components and connections) sit beside the
  existing Mermaid grammar. A comparison table summarises distinctions rather than
  retelling the diagram. A meaning-matched icon may label a heading, node, callout
  or compact label, intent-sensitively, and never inside code, identifiers, JSON or
  logs. The status legend stays. The old "no other symbols" / "headings stay words"
  restriction is gone.
- `op:examples`: a running example shows initial state, action, mechanism, resulting
  state, and why the result matters, with invented numbers consistent with each other.
- `communication/` modules move to 0.6.0. `emoji_structure` no longer flags a
  heading that opens with a navigation icon plus words.
- Activation is 5,760 → 6,085 tokens (legacy) / 5,813 → 6,124 (heuristic).
  `activation.max` is raised 5,900 → 6,200 as a regression ceiling; the target
  stays 5,000. This is the first time activation exceeds the Phase 4 baseline
  (5,946 / 5,966); recorded as a deviation. `op:repair` (partly) and
  `op:persistence` now sit past Claude Code's 5,000-token compaction re-attach,
  with `op:work-report`, `op:close` and Step 3. The new rules themselves stay
  inside the window.
- Plugin `version` 0.6.0 → 0.7.0. Both archives, both manifests, the plugin tree
  and `scripts/version_lock.json` were regenerated. New suite
  `tests/test_communication_experience.py`. Behavioural acceptance is the owner's.

### Communication-quality recovery (policy v0.5.0, plugin v0.6.0)
- Public release is paused: the owner rejected v0.5.2's communication quality on three
  real prompts (database replication, an architecture decision, CPU cache coherence).
  Regression analysis in `docs/communication-recovery.md`; the three prompts and the
  desired behaviour in the new `docs/COMMUNICATION_BASELINE.md`.
- `op:presentation`: a table cell keeps the verdict and its deciding reason; a
  condition, a second reason or an argument goes in a list under the table. Sentences
  in cells stay allowed, with no word cap. The causal-link rule no longer routes a
  table's "because" into the cell. Specialist depth is named: variants, tuning, one
  system's edge cases.
- `op:visual`: a figure and its text get different jobs. The diagram shows who acts
  in what order, a state table what each step changes, and the text after them why.
  Steps or prose that only retell the arrows become that why, unless the reader needs
  the steps in words as well.
- Strategy D leads with the recommendation and the reason that decides it, then the
  tradeoffs, and names what would make a rejected option worth adopting.
- Accuracy rules: teach the general mechanism first, then label one system's own
  version. State an assumed scale once, where it first matters, and say what would
  change the answer. Every Phase 4 and 4C accuracy requirement is kept.
- `op:sequencing` adds a concrete demonstration to the learnable order (still "only
  the stages this answer needs"). `op:examples` traces the case to the moment the
  behaviour shows. Step 3 checks a cell's argument and the text after a figure.
- References: two new weak-and-better pairs (a decision table with its reasoning
  underneath; a figure and the text beside it). New failure modes: a diagram retold in
  steps, one system taught as the rule, and qualifiers on every sentence. "A congested
  table" no longer forbids sentences, which had contradicted the 4C calibration.
- `communication/` modules move to 0.5.0. Still 12 operations and 15 variants. No
  quiz, takeaway, preview, visual quota or template is reintroduced.
- Activation is 5,543 → 5,760 tokens (legacy) / 5,588 → 5,813 (heuristic).
  `activation.max` is raised 5,600 → 5,900 as a regression ceiling; the target stays
  5,000. `op:work-report` (partly), `op:close` and Step 3 now sit past Claude Code's
  5,000-token compaction re-attach.
- Plugin `version` 0.5.2 → 0.6.0. Both archives, both manifests, the plugin tree and
  `scripts/version_lock.json` were regenerated. New suite
  `tests/test_communication_recovery.py` (19 tests). Suite 584 passed, 2 skipped.
- Not verified: no answer was regenerated. Behavioural acceptance is the owner's.

### Contribution protection
- `.github/CODEOWNERS` names `@A-Piyas-04` as owner of every path, so GitHub requests the
  maintainer's review on each pull request.
- `CONTRIBUTING.md` documents the fork, branch, validate, pull request, CI and review workflow;
  contributors need no write access.
- `main` is protected on GitHub by a repository ruleset: changes arrive by pull request, both
  CI jobs must pass, and force pushes and deletion are blocked. No approval count is required,
  so the sole maintainer can still merge their own pull requests.
- No package, version, skill text or communication policy changed.

### MIT licence (plugin v0.5.2)
- The project is released under the MIT License, `Copyright (c) 2026 Ahnaf Shahriar Pias`.
  The full, unmodified text is in the new root `LICENSE`.
- `plugins/socialized/.claude-plugin/plugin.json` and the marketplace entry in
  `.claude-plugin/marketplace.json` declare `"license": "MIT"`. Both pass
  `claude plugin validate --strict`.
- Both archives now ship the licence as `socialized/LICENSE`: beside `SKILL.md` in
  `dist/socialized.zip`, and at the plugin root in `dist/socialized-claude-plugin.zip`.
  `build_plugin.py` also writes `plugins/socialized/LICENSE`, so a marketplace install carries
  it. `package_skill.py` and `build_plugin.py` take it from the root `LICENSE`, and both
  `--check` modes catch a stale copy. It is not skill text: token estimates are unchanged.
- `claude plugin validate ./plugins/socialized --profile directory` now passes. It still warns
  `ICON_MISSING`, which does not fail validation.
- Plugin `version` 0.5.1 → 0.5.2: both packages changed bytes. The shipped skill files are
  byte-identical to 0.5.1. Both archives, both manifests and `scripts/version_lock.json`
  regenerated.
- `README.md`, `CONTRIBUTING.md` and `docs/LICENSING.md`, `RELEASE_READINESS.md`,
  `INSTALLATION.md`, `COMPATIBILITY.md`, `TROUBLESHOOTING.md` and `LIMITATIONS.md` updated
  from "no licence" to MIT. `docs/LICENSING.md` keeps the third-party audit and records that the
  research archive is included as research data.
- Tests: the archive inventories include `socialized/LICENSE`; new tests in
  `tests/test_public_release.py` check that the licence is MIT with the right copyright line,
  that `plugin.json` and the marketplace agree, and that both packages and the plugin tree ship
  the same bytes as `LICENSE`. Suite 565 passed, 2 skipped.
- No communication policy, operation, variant or reference file changed.

### Public documentation and release candidate (Phase 6)
- Public documentation set, written for first-time visitors rather than for the project's own
  history: a rewritten `README.md`, plus `docs/USAGE.md`, `docs/COMPATIBILITY.md`,
  `docs/TROUBLESHOOTING.md`, `docs/LICENSING.md`, `CONTRIBUTING.md` and `SECURITY.md`.
  `docs/INSTALL_AND_USE.md` was an orphan nothing linked to; its content is now in
  `docs/USAGE.md`.
- `docs/INSTALLATION.md` rewritten against current Anthropic documentation and against the CLI
  itself. Corrections: the menu paths are **Customize → Skills** and **Customize → Plugins**;
  the Agent Skills description limit is 1,024 characters, not 200 (this repository enforces a
  stricter 200 as a house rule, which the doc now says); a local marketplace path must start
  with `./`; and `--plugin-dir` accepts the plugin ZIP directly.
- Two install paths documented that were not before: `dist/socialized-claude-plugin.zip` loaded
  straight from the archive with `--plugin-dir`, and plugin upload on claude.ai, which also
  reaches Cowork and Claude Code as a synced plugin.
- Install, update and uninstall verified end to end on Claude Code 2.1.311 from a clean
  baseline, restored afterwards. `claude plugin validate --strict` passes for both the plugin
  and the marketplace. No model call and no billed usage.
- `claude plugin validate --profile directory` **fails on a missing licence**. The repository
  has no `LICENSE`, so it is not open source and cannot be submitted to Anthropic's directory.
  `docs/LICENSING.md` compares MIT and Apache-2.0, audits third-party content, and records the
  decision as the open blocker. No licence was chosen.
- `scripts/stage_release.py`: stages a release candidate into git-ignored
  `dist/release-candidate/` with SHA-256 digests and a human-readable summary of version,
  commit, gate output, artifacts and open blockers. It refuses to stage unless
  `python scripts/verify.py` passes, and it has no code path that can publish, tag or push.
- `tests/test_public_release.py`: 10 tests over what the existing suites did not cover - the
  public documentation set exists and is linked, no file claims a licence while none exists,
  every install path is documented, `SECURITY.md` publishes no unmonitored contact address,
  staging reports the licence blocker and reproduces the committed digests, and the staging
  script cannot publish.
- `docs/RELEASE_READINESS.md` is now an executed checklist: 20 items with pass, fail or
  unverified, the evidence for each, and the remaining work in order.
- No communication policy, operation, variant or reference file changed. Still 12 operations
  and 15 variants; both packages are byte-identical, so the version stays 0.5.1.

### Validation, CI and regression protection (Phase 5)
- One offline entry point: `python scripts/verify.py` runs the test suite,
  `validate_skill.py` on the source and on the committed ZIP, both `--check` drift
  modes, the token budgets, the new version lock, and the archive recomputation, then
  confirms the working tree is unchanged. It needs no network, no Claude
  authentication and no API key, prints the exact command for each failure, and
  propagates a non-zero exit status. `--project-root` lets it run from anywhere.
- An optional Claude CLI tier, `--with-cli`, runs `claude plugin validate` on the
  plugin and the marketplace. An unavailable CLI reports **skipped**, never passed;
  `--require-cli` turns that into a failure on a machine where it should work.
- `scripts/package_skill.py --check`: the read-only drift check the skill ZIP lacked.
  It renders the skill in memory and compares the committed archive and manifest
  member by member, including unsafe-path and root checks, without writing anything.
- `scripts/version_lock.py` and `scripts/version_lock.json`: a changed distributable
  now needs a deliberate version decision. Documentation-only edits change no package
  and need no bump. The hardcoded `0.5.1` assertion in `test_multiturn_policy.py` now
  reads the lock instead.
- `tests/test_release_integrity.py`: 58 tests over the gaps the earlier suites left -
  every defect `--check` should catch, member hygiene in both packages, marketplace
  and plugin metadata agreement, the version lock, the gate's own skip/fail handling,
  the CI workflow's permissions and contents, and broken relative links in the docs.
- `.github/workflows/validate.yml`: runs the same offline gate on pushes to `main`,
  on pull requests and on demand, for Python 3.11 and 3.13, with `contents: read`
  and no secrets, so it runs unchanged on forks. It publishes nothing.
- `docs/VALIDATION.md` is now the canonical explanation of how to check the
  repository; README and `docs/ARCHITECTURE.md` link to it instead of repeating it.
  `docs/REGRESSION_INVENTORY.md` maps each past regression to its policy source, its
  deterministic protection, and whether it is observable only in conversation.
  `docs/RELEASE_READINESS.md` is the Phase 6 checklist, unexecuted.
- No communication policy, operation, variant or reference file changed. Still 12
  operations and 15 variants; both packages are byte-identical to before.

### Final calibration (Phase 4C, plugin v0.5.1)
- Live conversational tests accepted the restoration below and found several restored
  rules too prescriptive. The requirements are now strong, context-sensitive
  preferences, with no operation, marker, variant, section or reference file added.
- `op:visual`: "**Prefer** a visual for such an idea … **leave one out where the prose
  already makes the relationship plain**" replaces "draw a visual for each such idea …
  there is no cap per answer". The final-third requirement becomes "keep that support
  even across the answer, so a later section that needs a figure gets one". The
  three-sentence cue stays as a signal, not a test to pass.
- `op:presentation`: a table cell is "one idea, about six words where a phrase will do
  and a short sentence where the comparison needs one" — the ban on sentences is gone.
  The horizontal rule now goes "where an answer of three or more sections turns to a
  new topic".
- Step 3: "Does a mechanism a figure would clarify still have one, in the last third as
  much as the first?" replaces the per-idea coverage question, and the six-word cell
  limit becomes "Does every table cell stay scannable?". Paragraph and list-item
  density checks are unchanged.
- Accuracy rules split in two and strengthened in place (task 3): carry no database's
  or broker's behaviour over to another unchecked; name the settings a guarantee
  depends on rather than stating it absolutely; state any workload, scale, or traffic
  pattern the answer assumes and the person has not given. `core.md` principle 6
  mirrors it.
- Kept: the comparison-table cue, the whole Mermaid grammar, paragraph density,
  heading rules and the section separator, the Step 3 scannability and decoration
  checks, the form-from-content line. Still absent: mandatory quizzes, automatic
  takeaways, section previews, unrequested artifacts, response templates.
- Activation 5,466 → 5,543 local-estimate tokens (+77; 5,514 → 5,588 by the
  heuristic), inside the 5,600 gate with about 12 heuristic tokens spare; the gate was
  not raised again. −6.8% against the Phase 4 baseline.
- Tests: six assertions in `tests/test_visual_restoration.py` re-pointed from
  requirement to preference wording, plus `test_no_visual_or_formatting_quota` (four
  quota phrases that must stay absent, checked in the source and both artifacts) and
  `test_accuracy_rules_discourage_absolute_and_unsupported_claims`. One pre-existing
  assertion in `tests/test_skill_structure.py` required the literal "for each such
  idea" and now requires "Prefer a visual". Suite 492 passed, 1 skipped.
- Plugin `version` 0.5.0 → 0.5.1. Both artifacts regenerated.

### Visual communication restored (Phase 4C, policy v0.4.0, plugin v0.5.0)
- `op:visual`: the coverage floor Phase 4 removed is back. A visual is drawn for
  **each** idea whose shape would take three or more sentences to describe, there is
  no cap per answer, the hardest section gets its visual first, and the last third of
  the answer gets at least the visual support of the first. Phase 4's negative rule
  ("do not require a visual for every shaped idea, every section, or the final
  third") and its second judgement gate ("when it clarifies the relationship") are
  gone; its anti-redundancy half stands — one representation per idea, a second only
  for a materially different dimension, and colour, status emoji or a legend only
  where they speed a comparison.
- Step 3: the visual check asks again whether each idea with a shape has its visual,
  including the hardest section and the last third, so a *missing* figure can be
  added and not only a redundant one pruned. It also checks list-item length
  alongside paragraph and table-cell length, and asks whether every heading, list,
  table, **diagram** and bold sentence marks a real division or only decorates.
- `op:presentation`: a new paragraph starts when the idea changes even when the
  current one is short; a table cell is never a sentence; a horizontal rule (`---`)
  separates major topics in an answer of three or more sections.
- Strategy section: in every strategy, teaching or not, the form comes from the
  content — a table for options against their tradeoffs, a diagram for a flow or an
  interaction, steps for a procedure, a fenced block for code, prose for a single
  chain or a casual reply. Architecture and tool comparisons were the regression the
  owner reported; Strategy D previously gave no form guidance at all.
- Nothing Phase 4 removed on purpose returns: no mandatory check question, no
  automatic section map, no appended interactive offer, artifacts still opt-in. No
  word cap was added, and technical depth is kept by splitting a dense paragraph
  into connected units rather than by dropping a mechanism (`core.md` principle 11).
- Activation grows from 5,379 to 5,466 local-estimate tokens (+87, +1.6%, legacy
  tokenizer; 5,418 to 5,514 by the heuristic). The `activation` `max` is raised 5,500 → 5,600
  as a regression ceiling about 2% above the new size; `target` stays 5,000. Step 3
  now sits wholly outside Claude Code's 5,000-token compaction re-attach window,
  while `op:visual` and `op:presentation` stay inside it. Offsetting consolidations
  are listed in `docs/phase-4c-visual-restoration.md` §5.
- New `tests/test_visual_restoration.py` (26 tests; suite 489 passed, 1 skipped).
  Two Phase 4 assertions were inverted on purpose and are documented in
  `tests/test_refinement_policy.py`.
- Policy modules move to 0.4.0 with a Phase 4C change table. Plugin `version`
  0.4.0 → 0.5.0. Both artifacts regenerated.

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
