# Standing instructions for agents working on Smart-Claude V1

Plan: `SMART_CLAUDE_V1_IMPLEMENTATION_BRIEF.md` + `SMART_CLAUDE_V1_BRIEF_ADDENDUM.md`.
Evidence standard: `research/EVIDENCE_AUDIT.md`. Facts in brief §1 are verified; do not re-derive them.

## Order of work

Track A0 → Track A (A10 folded in) → Track B. A track starts only when the previous
track's definition of done is green.

## Hard constraints

- Nothing may require the user to run prompts, copy responses, or rate anything by hand.
- No paid API key. A0 runs Claude Code on the subscription via `CLAUDE_CODE_OAUTH_TOKEN`;
  the judge is a free-tier non-Anthropic model.
- `python -m pytest` stays green at every commit.
- Never edit anything under `research-results-2026-10-26/`; `research/recompute_archive_stats.py`
  must keep reproducing.
- No credentials in the repo, in committed output, or in logs.
- No new strategy/methodology documents beyond those the briefs name.

## Framing (set by the user, 2026-10-27)

- The project improves Claude's explanations: structure, organisation, sentence-level
  readability, register, persistence, repair. Track A is the deliverable.
- Claude-vs-GPT is settled and out of the evaluation entirely. The archive's GPT answers stay
  only as source material for COMMUNICATION_EXEMPLARS.md, never as a scoring target or baseline.
- The judge is a regression guard, not a discovery exercise. Its acceptance test is
  Claude-vs-Claude only, plus a floor test of deliberately degraded answers; the 0.20 flip cutoff
  is fixed in code. Fact capture is the primary measure and is never combined with pairwise. The
  failure to catch: answers that get prettier and emptier.
- Priority: Track A in full; Groq backend and acceptance test in parallel; the sweep waits until
  acceptance passes.

## Skill text rule

Every rule names an action the model takes. If a rule can be satisfied by writing a plain
undifferentiated paragraph, it is written wrong.

## Stop and ask the user if

- an invariant in brief §1 turns out to be wrong;
- A0's smoke test cannot produce a verifiable skill-off arm either way;
- an operation should be dropped or added.

Otherwise make the call, record it under "Decisions" below, and keep going.

## Report back after each track

What changed; the command output proving it is green; what was not verified; what the user
needs to decide. No progress narrative.

## Decisions (append as made)

- A0.2: `skillOverrides` via `--settings` is honoured by Claude Code 2.1.310 (observed in the
  `system/init` event: `explanation-lab` is absent from `skills` and `slash_commands`). The
  two-directory fallback is not needed. Each row runs in a fresh sandbox outside the repo with
  its own `CLAUDE_CONFIG_DIR`, so user-level skills, CLAUDE.md, memory and plugins cannot leak in.
- A0.2: the message is passed on stdin rather than as an argument (Windows argument limits).
- A0.2: tools restricted to `Skill,Read` with `--permission-mode dontAsk`, identical in every arm.
- A0.1: response files stay pure response text (disclaimers would corrupt word counts and judge
  input). Disclaimers go in each run's `COLLECTION_NOTICE.md`, every per-row metadata file, every
  judge/screener output, and the harness README.
- A0.2: the automated sweep is a new run `evaluation/runs/pilot16-cc` (16 cases x 4 conditions x 3
  samples = 192 rows). The existing `pilot16` sheet (1 sample, manual) is left untouched.
- A0.3: judge backend Google AI Studio over stdlib `urllib`, key in the `x-goog-api-key` header
  (never in the URL). Default model `gemini-3.5-flash-lite` (the archive's model; free-tier
  availability unverified; override with `JUDGE_MODEL`). Calls cached on disk by exact request.
- A0.3: misconceptions in TEST_CASES are plain strings; the judge ids them `m1..mN` by position.
- A0.4: an item is non-diagnostic if the judge answers it correctly with no text in more than half
  of the attempts (options shuffled, temperature 1.0). Free-text items are carried through
  unscreened and excluded from the survival rate.
- A0.2: the stored CLAUDE_CODE_OAUTH_TOKEN was 3 lines with internal spaces and no `sk-ant-oat`
  prefix (401 after stripping whitespace). collect_cc now refuses any token with internal
  whitespace instead of mangling it. Only surrounding whitespace is stripped.
- A0.2: the VS Code extension updated Claude Code mid-session and briefly removed the binary. The
  harness prefers a pinned install (`%LOCALAPPDATA%\smart-claude\cc-2.1.311`, npm
  `@anthropic-ai/claude-code@2.1.311`) and stops a run if the version changes between rows.
- A0.2 multi-turn: rows are sent as `--input-format stream-json` user turns, each only after the
  previous turn's result, in one session. Claude Code emits an init event per turn; each is verified
  and all must share one session id. Transcripts go to `responses/<row>.turns.json`.
- A0.2: each run freezes its skill build under `<run>/skill_build/`; pilot16-cc pins V0.
- A0.3: free tier, 2026-10-27: Pro-class models return 429 on the first call; gemini-3.8-flash is
  listed but mostly 503; gemini-3.6-flash serves but has a 20 requests/day/model cap; requests for
  3.5 and 3.7 are silently answered by 3.6 and 3.8. Default judge is gemini-3.6-flash; the backend
  refuses rerouted answers and stops at once on a per-day 429.
- A0.3: the judge acceptance test runs on the 30 archive answers (judge_acceptance.py), because no
  smoke output exists yet.
- A1: explanation-methodology.md also carried `op:structure` markers and was renamed with the rest.
- A3/A10.3: scope discipline folded into op:register. The gloss-or-omit rule for names and
  foreign terms lives in the always-on accuracy rules, not in op:register.
- A3: register's practitioner default explicitly overrides Step 1's "new to this field" default.
- A8: SKILL.md compactness test raised from 250 to 300 rendered lines (277 with nine operations).
- A9: 12 variants (10 from the brief plus persist and wrep) and 45 cases (33 + 8 + 2 persistence +
  2 work_report).
- A6: archive answers lost their markdown headings in copying; recorded as a caveat in the
  structural baseline.
- Reframe (user, 2026-10-27): Claude-vs-GPT removed. Structural baseline now covers the 15 archive
  Claude answers. Cross-provider acceptance runs kept as superseded.
- op:plain added (10 operations, 13 variants); linter gains max_sentence_words and
  passive_sentence_count; SKILL.md renders at about 295 lines (guard 300).
- Judge backend: Groq (OpenAI-compatible) is the default; model default openai/gpt-oss-120b, to be
  confirmed against Groq's model list when the key arrives. Groq's free tier also has per-day
  token caps; the backend stops on any per-day limit.
- Acceptance floor: fact removal is hand-listed (databases, immunology, interest). Caching and TCP
  facts recur across sections and cannot be removed cleanly. The TCP truncation keeps all four
  facts, so it is left out of the fact gate but kept in the pairwise floor.
- Thresholds frozen by the user: 0.20 flip cutoff, 0.80 floor shares, TCP truncation outside the
  fact gate. Loosening any of them after data counts as a deviation.
- Floor adds `formatted_emptier`: the fact-removed text plus headings, bullets and bold. The judge is
  rejected if it ever prefers it consistently, or if the original wins fewer than 80% of those pairs.
- Fact removal now covers all five topics, every recurrence included (caching f3, tcp f3 added), as
  exact edits that must each match once.
- Keep the fake-judge test pattern: each gate gets a fake judge that fails only that gate
  (shorter-preferring, position-biased, format-rewarding).
- Before any Groq run: `scripts/judge_capacity.py --tpd <cap>` measures real tokens per call and
  projects days. Stop and report if acceptance or the sweep would take more than about 3 days.
- `answer_first_offset` and `passive_sentence_count` are labelled heuristics and never gate.
- Socialized-Claude (user, 2026-10-27): the skill id is `socialized` because the
  validator rejects `claude` in a name. The display name is Socialized-Claude.
  `pilot16-cc` stays frozen as `explanation-lab`; collect_cc reads the id from
  the run manifest.
- Visuals are markdown by default. An artifact is built only on claude.ai, and
  only when the person explicitly asks for one. A one-off request covers that
  reply; "from now on" is a standing instruction.
- Interactive output without an artifact is a state table (one row per moment).
  The addendum's emoji ban is narrowed: ✅ ❌ ⚠️ 🟢 🟡 🔴 may mark status when at
  least two distinct markers share a list or table. Headings stay unmarked.
  Recorded as a deviation.
- SKILL.md compactness guard raised from 300 to 380 rendered lines.
- `visual_count` is a heuristic and never a gate. `dense_paragraph` and
  `uncaptioned_visual` are flags.
- Visual budget (user, 2026-10-27, second report): the "one per section, two per
  answer" cap is superseded. Each idea with a shape gets one visual and each
  visual deletes the prose it replaces. The hardest section gets its visual
  first; the last third gets at least the first third's support.
- Interactive offer (user, 2026-10-27): artifacts stay opt-in. Content that
  changes over time gets a state table and one closing line offering an
  interactive version.
- Mermaid `classDef` classes carry colour as one code per answer, named once.
  The emoji legend stays limited to status in lists and tables.
- SKILL.md compactness guard raised from 380 to 460 rendered lines (394 now).
- New flags: `dense_table_cell`, `wide_table`, `bold_as_heading`,
  `uncaptioned_specimen`, `flat_visual`. New heuristics that never gate:
 `visuals_first_half`, `visuals_second_half`, `max_table_cell_words`,
 `heading_depth_max`.
- Phase 4B: token counts use Anthropic's legacy public tokenizer
 (`Xenova/claude-tokenizer`, local cache only) or a stdlib heuristic calibrated to
 it; both are labelled local estimates. The activation budget is `max` 5,500
 (regression gate) and `target` 5,000 (advisory, from the documented compaction
 re-attach limit), configurable in `scripts/token_budgets.json`.
- Phase 4B: the always-on core (Scope, Strategies, Steps 1–2, Accuracy rules,
 Reference files) precedes the operations so it survives Claude Code's 5,000-token
 compaction re-attach. Option B (visual drawing grammar moved to an on-demand
 reference) is documented, not implemented: about 400 tokens saved against a real
 risk of losing owner-set visual rules when the reference is not read.
- Phase 4C: Phase 4's visual change is split. Its anti-redundancy half stands; its
 removal of the coverage floor is reversed, because that floor is an owner decision
 (see "Visual budget") that Phase 4 overrode without recording a deviation. `op:visual`
 draws one visual per shaped idea with no cap, hardest section first, last third
 supported at least as well as the first, and Step 3 asks for coverage again, not only
 pruning. Quizzes, previews, demo offers and opt-in artifacts stay as Phase 4 left them.
- Phase 4C: `activation.max` raised 5,500 → 5,600 (now 5,466 legacy / 5,513 heuristic).
 The gate is a regression ceiling about 2% above current size, not a frozen threshold;
 `target` stays 5,000. Consequence recorded: Step 3 is now wholly outside Claude Code's
 5,000-token compaction re-attach window, while the rules it checks stay inside.
- Phase 4C: two Phase 4 assertions inverted on purpose in
 `tests/test_refinement_policy.py`, with the reason in the file. The restored rules have
 their own suite, `tests/test_visual_restoration.py`.
- Phase 4C: form selection ("a table for options against their tradeoffs, a diagram for
 a flow or an interaction, …") added to the strategy section so it applies to
 non-teaching replies. The reported regression was a Strategy D architecture discussion,
 which previously had no form guidance at all.
- Phase 4C calibration (user, 2026-10-28, live tests): the restoration is accepted and
 its restored rules are softened from requirements to strong, context-sensitive
 preferences. `op:visual` prefers a visual per shaped idea with an explicit escape
 clause, no quota and no cap; the final-third floor becomes "keep that support even
 across the answer"; a table cell may be a short sentence. This supersedes the
 "Visual budget" decision's "each idea with a shape gets one visual" as a requirement,
 keeping it as the default preference. Recorded as a deviation from that decision.
- Phase 4C calibration: accuracy rules split in two and strengthened in place —
 configuration-dependent guarantees, unstated workload or scale assumptions, and
 cross-implementation carry-over. No new operation (still 12 and 15 variants).
- Phase 4C calibration: `activation` 5,543 legacy / 5,588 heuristic, inside the 5,600
 gate with about 12 heuristic tokens spare; the gate was not raised again.
- Phase 5: one offline entry point, `python scripts/verify.py` (pytest, skill validation
 on source and ZIP, both `--check` drift modes, token budgets, version lock, archive
 recomputation, working-tree check). The optional `claude` CLI tier is `--with-cli` and
 reports skipped, never passed, when the CLI is unavailable. No new dependency: pytest and
 pyyaml were already in requirements-dev.txt.
- Phase 5: `package_skill.py` gained the `--check` mode it lacked, matching
 `build_plugin.py`. A missing ablation ZIP is not drift, because `dist/ablation/` is
 git-ignored; an ablation ZIP that is present is still checked.
- Phase 5: change control moved from a hardcoded version literal in
 `test_multiturn_policy.py` to `scripts/version_lock.json`, which ties the plugin
 `version` to the SHA-256 of both packages. A changed package needs a version decision; a
 documentation-only edit needs none. The pre-1.0 guard stays.
- Phase 5: `.github/workflows/validate.yml` runs the same gate on push to `main`, on pull
 requests and on demand, Python 3.11 and 3.13, `permissions: contents: read`, no secrets,
 no publishing. `actions/checkout@v7` (v7.0.0 verified upstream) and
 `actions/setup-python@v6` (newest major verified). No hosted run has been observed.
- Phase 5: `docs/VALIDATION.md` is the canonical validation explanation; README and
 ARCHITECTURE link to it. `docs/REGRESSION_INVENTORY.md` marks each regression as
 structurally tested, observable only in conversation, or heuristic only.
 `docs/RELEASE_READINESS.md` is the Phase 6 checklist and was not executed.
- Phase 5: there is no `LICENSE` file in the repository. "Open source" is not a claim this
 repository can make yet; it is item 6 of the release-readiness checklist.
- CI fix: ZIP builds were platform-dependent — `zipfile` defaults `create_system` to 0 on
 Windows and 3 elsewhere, so a Linux rebuild differed from the Windows-built committed
 archives in the central directory's "version made by" host byte alone, failing both
 `--check` drift gates and 5 tests. `package_skill.zip_bytes` now pins
 `ZIP_CREATE_SYSTEM = 0`, the value the committed archives already carry, so no package
 changed, no version decision was needed, and the version lock still holds.
- Phase 6: no licence was chosen. `claude plugin validate --profile directory` refuses a
 submission for `LICENSE_MISSING`, so the blocker is Anthropic's, not a style preference.
 `docs/LICENSING.md` compares MIT and Apache-2.0 and recommends MIT if the owner has no
 preference; nothing was applied. Adding `license` to plugin.json changes the plugin ZIP's
 bytes, so it needs a version bump too.
- Phase 6: documentation corrections found against current Anthropic docs — the skill
 description limit is 1,024 (spec), not the 200 the docs claimed; the repository's stricter 200
 is kept as a house rule and now labelled as one. Menu paths are Customize → Skills and
 Customize → Plugins. A local marketplace path must start with `./`.
- Phase 6: install/update/uninstall verified on Claude Code 2.1.311 from a clean baseline and
 restored exactly. `--plugin-dir` loads `dist/socialized-claude-plugin.zip` directly; recorded
 as a supported path. claude.ai skill and plugin upload stay unverified: they need an account
 action and cannot be exercised from the repository.
- Phase 6: a release workflow in GitHub Actions was deliberately not added. Staging is
 `python scripts/stage_release.py`, local and publish-incapable by construction (guarded by a
 test), because the owner holds Git and publishing control. Output goes to git-ignored
 `dist/release-candidate/`.
- Phase 6: `docs/INSTALL_AND_USE.md` deleted. Nothing linked to it; its content is in
 `docs/USAGE.md`.
- Phase 6: version stays 0.5.1. Documentation, a new script and new tests changed no package
 bytes. 1.0.0 is not a Phase 6 entitlement; it waits on the licence, the claude.ai smoke tests
 and the manual spot-check.
- Licence (user, 2026-10-29): MIT, `Copyright (c) 2026 Ahnaf Shahriar Pias`. Root `LICENSE` is
 the single source; `package_skill.py` and `build_plugin.py` ship it as `socialized/LICENSE` in
 both archives and in `plugins/socialized/LICENSE`, outside `render_files()` so it is never
 skill text or token-budgeted. `license: MIT` also on the marketplace entry. Plugin
 0.5.1 → 0.5.2 (patch: package bytes changed, skill text did not). `plugin.json` author stays
 `A-Piyas-04`. The research-archive note lives in `docs/LICENSING.md`, not in the archive.
- Repository protection (user, 2026-10-29): `main` is guarded by a repository ruleset, not
 classic branch protection. It requires a pull request with 0 approvals (GitHub never lets an
 author approve their own pull request, and the owner is the sole maintainer), both
 `offline validation` jobs from GitHub Actions, an up-to-date branch, no force pushes and no
 deletion. CODEOWNERS review is not required for the same reason; `.github/CODEOWNERS` still
 requests it. The bypass list is empty; the owner keeps admin and can edit the ruleset.
 No package bytes changed, so the version stays 0.5.2.
- Communication recovery (user, 2026-10-29): public release paused until three owner-run
 prompts (replication, an architecture decision, cache coherence) read well. Fixed in place,
 no new operation: a table cell keeps the verdict and the reasoning goes under the table (no
 word cap, sentences still allowed); a figure shows what happens and its text says why;
 Strategy D leads with the recommendation; one system's internals are labelled after the
 general mechanism; an assumption is stated once. Headings and numbering were left alone
 because no observation named them. `activation.max` 5,600 → 5,900 (5,760 legacy / 5,813
 heuristic). Policy 0.5.0, plugin 0.6.0. Work is on `recovery/communication-quality`, unmerged.
 `docs/COMMUNICATION_BASELINE.md` is the behavioural reference; behavioural acceptance is
 the owner's.
- Communication-experience upgrade (user, 2026-10-29): after the recovery, the owner asked
 for a better presentation experience (dense paragraphs, congested tables, diagram/prose
 repetition, weak hierarchy, limited visual variety, semantic icons). Refined in place, no
 new operation: one idea per paragraph with four sentences as a ceiling not a target;
 glanceable table verdicts; internal core → mechanism → optional priority; architecture
 diagrams named beside the existing Mermaid grammar; figure vs table vs prose keep different
 jobs; examples trace state → action → result; meaning-matched icons as navigation, never
 required, never inside code. The addendum's emoji ban is narrowed a second time: a heading
 may open with a navigation icon. Policy 0.6.0, plugin 0.7.0. Still on
 `recovery/communication-quality`, unmerged. Behavioural acceptance is the owner's.
- Communication priority correction (user, 2026-10-29): v0.7.0 failed acceptance on two
 cache-coherence answers (dense, repetitive, no icons, a read-triggered M → I transition).
 Conflicting instructions were removed or merged, not added to: one planning order in Step 2
 (essential understanding → effective representation → necessary detail); the obvious-approach
 move stated once; the example reused only where needed; every figure, table and paragraph a
 different job. One representation per mechanism is a **preference, never a cap** (user):
 another is added whenever it shows something the first cannot. The coverage floor ("even
 across the answer", "last third as much as the first") is replaced by a value test, by owner
 choice; recorded as a deviation from "Visual budget". Meaning-matched icons are now the
 **default** on key headings, callouts and labels of a substantive explanation (no quota,
 never in code, JSON, formal or casual replies). The first accuracy rule covers every arrow,
 state and transition, with triggers named. The failed responses are described, not stored
 (user). `activation.max` 6,200 → 6,150 (6,035 legacy / 6,084 heuristic). Policy 0.7.0,
 plugin 0.8.0. Still on `recovery/communication-quality`, unmerged.
- Communication simplification (user, 2026-10-29): after v0.7.0 the owner asked for the
 instruction system to be *simplified*, not extended again. Audit
 `docs/COMMUNICATION_SIMPLIFICATION_AUDIT.md`. Four verified causes: the same rule
 stated in up to four files in four wordings; eleven counting thresholds; four pairs of
 rules that cannot both be satisfied; and optional capabilities promoted to defaults.
 A fifth cause is the test suite itself — five round-specific suites froze each round's
 phrasing, so the cheapest change was always to add text beside it.
 Removed, not added to: every counting rule; heading numbering, the one-line map, the
 mandatory horizontal rule and the required bold title line; the icon default (icons and
 status markers are one optional rule again). Added once, up front: "Nothing here is a
 quota." Added as rules replacing overlapping bullets: show a general claim about cost,
 risk or complexity happening to one case (owner brief §4); direct conversational
 register in `op:plain`. `references/treatment-selection.md` §1 deleted as pure
 restatement; `communication/*.md` rewritten as indexes that point at the one place each
 rule is stated. `COMMUNICATION_GRAMMAR.md` reconciled — it still documented five rules
 that stopped shipping in v0.5.0–v0.7.0.
 **The 12 operations and 15 variants were examined and kept**, because six map to the
 archive study's treatments and each variant is a planned sweep arm; merging headings
 removes no instruction. Recorded as a deliberate decision, not a default.
 Five policy test files (1,336 lines) replaced by one invariant-based
 `tests/test_communication_policy.py`; every dropped assertion is listed in the audit §4.
 `test_activation_exceeds_the_phase_4_baseline_by_a_recorded_decision` restored to `<`,
 as its docstring invited. `activation.max` 6150 → 5750 (5648 heuristic), below the
 Phase 4 baseline for the first time since Phase 4C; Step 3 and `op:close` still sit
 outside the 5,000-token compaction re-attach window. Policy 0.8.0, plugin 0.9.0. Still
 on `recovery/communication-quality`, unmerged. Behavioural acceptance is the owner's.
 **Not done:** the brief's §1 comparison against `Microservices Architecture Advice.html`
 and the paired Claude response. Neither file is in the repository or the working tree.
- Owner house style (user, 2026-10-29, same day as the simplification): the owner
 specified the output format directly and said to change, remove or add whatever it took.
 Recorded in `docs/COMMUNICATION_SIMPLIFICATION_AUDIT.md` §8. **It reverses three of the
 simplification's decisions, deliberately:** one counting rule ships again (two or three
 sentences per paragraph), the "nothing here is a quota" preamble is replaced by a
 narrower one, and an emoji point is the default on every bullet and key heading rather
 than optional. A direct owner instruction outranks the simplification brief's §5, and
 the audit says so in place of quietly contradicting itself.
 New always-on `SKILL.md` "House style" section before the first operation: short
 paragraphs, bullets over prose for a multi-point passage, an emoji point per bullet, a
 blank line between units, plain words and sentences. Escape hatch in one sentence — an
 explicit request lifts one and then stands. `op:plain` names the swaps ("use" not
 "utilise", "in order to" → "to") because a rule that only says "write simply" is
 satisfiable by writing exactly as before. `op:visual` carries a 44-icon working set; the
 full ~150-icon catalogue is a **new fourth reference**, `references/emoji-palette.md`.
 Markdown has no text colour, so the skill names the three techniques that render
 (`diff` fence, Mermaid `classDef`, status emoji) instead of promising colour.
 `structural_metrics.py` retuned to measure the shipped rules: `DENSE_SENTENCES` 5 → 4,
 `DENSE_PARAGRAPH_WORDS` 80 → 55, `heading_nav_exempt` extended to bullets so the
 intended emoji form does not flag, `NAV_ICONS` 23 → ~100. Still never gates.
 Two tests inverted on purpose with the reason in each docstring; the activation test
 flips for the second time. `activation.max` 5750 → 6350 (6178). **`SKILL.md` is at 495 of the
 validator's 500 body lines**, reached after a compression pass that merged wording
 across every operation without dropping a rule — the next addition must displace
 something. `op:register` now sits past the 5,000-token compaction re-attach window.
 Policy 0.9.0, plugin 0.10.0. Still on `recovery/communication-quality`, unmerged.
 Main risk recorded, not resolved: a two-sentence paragraph cap can fragment a connected
 causal argument. The guard is `op:presentation`'s prose exception plus the
 `whitespace_padding` flag; whether it holds is a conversational question.
