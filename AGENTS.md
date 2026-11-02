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
- Skill upgrade Phase 1 (space and hierarchy, `docs/SKILL_UPGRADE_PLAN.md`), user
  2026-11-02: paragraph ceiling tightened to three sentences / about 50 words, as a
  ceiling with a stated exception for one continuous causal argument. The matching
  gate thresholds move with it: `DENSE_SENTENCES` 5→4, `DENSE_PARAGRAPH_WORDS` 80→50
  (verified: 0 of the 24 structural fixtures change `dense_paragraph` status).
- Phase 1 added to `op:presentation`: blank line as unit separator with visible
  separation at three or more units; an emphasis ladder (`##`/`###`/`####` for size,
  bold/italic/`code`/blockquote for style, three distinct levels at three or more
  sections); prefer more, smaller sections (split past ~12 lines); and a bolded-label
  lead for bullets.
- Phase 1 reclaim, dropping no rule, each a duplicate wording: removed the
  `op:sequencing` obvious-approach bullet (kept the fuller `op:mechanism` copy); this
  removes that rule from the single-op `seq` ablation arm only — `full` and the frozen
  `pilot16-cc`/`explanation-lab` build are unaffected. Removed the duplicate accuracy
  "unsure of a fact" bullet; folded the beginner-register rule into "explain simply";
  compressed the `op:close` interactive-offer and `op:plain` section-map rules; and
  compressed Step 3 from 17 questions to 11 (every check kept; the four presentation
  and three visual questions merged to two each).
- Phase 1 metrics: added never-gating heuristics `whitespace_ratio`,
  `units_per_section`, `emphasis_levels_used`; `heading_count` (pre-existing) is now
  labelled a heuristic in `lint_response.py`. None appear in
  `decorative_structure_flags`. SKILL.md body is 439 lines (guard 500), rendered 392
  (test guard 460).
- Skill upgrade Phase 2 (human voice, `docs/SKILL_UPGRADE_PLAN.md`), user 2026-11-02:
  added a 13th operation `op:conversational` (heading "Write the reader's next
  question into the answer"), carrying the implied-second-voice move, direct address,
  contractions, and the anti-chattiness guard (no praise, no staged persona). This is
  the stop-and-ask approval AGENTS.md requires for adding an operation. OPERATIONS is
  now 13, VARIANTS 16 (new `conv` single-op key).
- Phase 2: no `V_conv` sweep arm added to `evaluation/conditions.json`; the sweep
  stays at 15 arms, so no extra judge tokens. The arm can be added later in one data
  edit when the sweep is run.
- Phase 2 `op:examples`: the analogy demotion is reversed — a direct case is kept
  where one is concrete, and analogy is given equal standing for a beginner or a
  mechanism with no everyday counterpart; the keep-the-causal-structure guard stays.
  The mirror in `references/treatment-selection.md` ("an example beats an analogy")
  is left as the conflict-resolution rule it already is (it says "when both would
  work"), so no change was needed there. Also widened the scenario rule from
  beginners to any teaching answer, and added state→action→result tracing.
- Phase 2 `op:terms`: tightened to gloss-before-use for every term, acronym, and set
  phrase (foreign terms included), with no writer-obviousness exception. The old
  "leave terms the reader used or clearly knows undefined" latitude is narrowed to
  only terms the reader themselves used; the "clearly knows" half is dropped.
- Phase 2: new reference `references/conversation-grammar.md` (worked reader's-question
  patterns, a register ladder, direct-address/contraction pairs). SKILL.md body is 471
  lines (guard 500), rendered 418 (test guard 460).
- Skill upgrade Phase 3 (visual and colour, `docs/SKILL_UPGRADE_PLAN.md`), user
  2026-11-02: icons become two layers. Status stays the closed six (✅ ❌ ⚠️ 🟢 🟡 🔴),
  lists and tables only, two or more distinct markers, never on a heading. Navigation
  is open: one icon opening a heading, callout, or bullet label, meaning-matched,
  teaching and long answers only, never in code. This supersedes "headings stay
  unmarked" and the "and no other symbols" clause for navigation icons only.
- Phase 3: new reference `references/emoji-palette.md`, 153 navigation icons in seven
  meaning groups (state, flow, risk, data, people, time, tooling), single code points
  from Emoji 11 or earlier (no ZWJ, flags, skin tones, keycaps). `op:visual` keeps a
  42-icon working set inline. The linter's `NAV_ICONS` is parsed from the palette's
  table rows (minus the status six), so the two cannot drift.
- Phase 3 `op:visual`: colour is named as the three techniques that render (`diff`
  fence, `classDef`, status emoji), merged into the existing one-colour-code bullet.
  Every branching or time-ordered mechanism in a teaching answer gets a diagram
  regardless of the three-sentence bar. The artifact exception now requires the
  markdown answer to stay complete without the artifact (was "a short markdown
  answer"). Step 3's two visual questions absorb the new checks (no new question).
  `treatment-selection.md` mirrors the always-diagram rule and gains "emoji soup" and
  "colour promise" failure modes; "emoji as structure" became "emoji as decoration".
- Phase 3 linter: `emoji_structure` now exempts a heading or list item opening with a
  palette icon; status markers on headings and off-palette emoji still flag. The
  `emoji_structure` fixture's 🚀 (now in the palette) became 🎃. New never-gating
  heuristic `icon_count`; `visual_count` already existed, so it was not re-added.
  `research/baseline_structural_metrics.json` regenerated (only `icon_count` added).
- Phase 3 budget: nothing merged away beyond the colour bullet; SKILL.md body is 485
  lines (guard 500), rendered 432 (test guard 460), leaving 15 body lines for Phase 4.
- Skill upgrade Phase 4 (durability, `docs/SKILL_UPGRADE_PLAN.md`), user 2026-11-02: new
  always-on section "Markdown that renders (always apply)" between the accuracy rules
  and Step 3, with no op markers, so every variant including `core` carries it. Six
  rules: fence width, escaped pipes, row cell count plus the four-column cap, plain
  Mermaid labels, no heading jumps, palette-only emoji. Step 3 gains one unmarked
  check. The four-column and no-skip rules stay in `op:presentation` as well.
- Phase 4 reclaim, dropping no rule: `op:presentation`'s three blank-line/new-unit
  bullets became two plus the visible-separation bullet; `op:conversational`'s
  no-praise and no-persona bullets became one (5 rules remain). SKILL.md body is 494
  lines (guard 500), rendered 441 (test guard 460).
- Phase 4 linter `scripts/lint_markdown.py` (standalone, stdlib only, exit 1 on any
  break): `unclosed_fence`, `nested_fence`, `table_pipe_mismatch`, `wide_table`,
  `mermaid_label` (flowchart node and edge labels only; sequence-diagram text is
  free), `heading_jump` (the first heading may start at any level),
  `emoji_outside_palette`. The emoji check covers U+1F000–U+1FAFF plus joiners, flag
  letters and keycaps; U+2600–U+27BF symbols such as a check mark are not flagged,
  because they render as text glyphs everywhere. A nested same-width fence reports
  `nested_fence` and the `unclosed_fence` that follows, since a renderer does the same.
  It is not wired into `lint_response.py` or the evaluation harness.
- Phase 4 tests: `tests/test_markdown_safety.py` (one crafted break per code, a clean
  sample, legitimate fixtures, and every skill file must pass) and
  `tests/test_presentation_upgrade.py` (a 33-rule registry checked against the
  single-op or core build, a removal test per rule, and ties between skill numbers and
  linter thresholds). The phrase tests in `test_skill_structure.py` stay. The change
  record for Phases 1–4 lives in `docs/SKILL_UPGRADE_PLAN.md`, not a new document.
- Skill upgrade V2 Phase 5 (diagnose, `docs/SKILL_UPGRADE_PLAN_V2.md`), user
  2026-11-02: the round-2 claude.ai answers were supplied by the user (raw markdown and
  screenshots), not captured through `collect_cc`. This is a user-approved exception to
  "nothing by hand", for this diagnosis only. The evidence is in
  `evaluation/layout_capture/round2/`, with `capture.json` recording build `e93f3c0`
  and the explicit `/socialized` invocation. It says nothing about auto-activation.
- Phase 5: `SKILL.md` frontmatter carries `metadata: {version: "2.0-dev"}`, identical
  in every variant. `evaluation/render_probe.md` is the one-message probe for claude.ai
  heading sizes. `evaluation/layout_prompts.json` starts with the two round-2 prompts,
  stored verbatim without the `/socialized` prefix.
- Phase 5 finding: the model writes `##` sections and `###` sub-sections. The render
  probe (`evaluation/layout_capture/render_probe-claude-ai.png`) shows `##`, `###`,
  `####` and a bold line at one size on claude.ai; only `#` is visibly larger.
  Blockquote text renders dimmer than body.
- V2 decision 2 (user, 2026-11-02): an answer's one `#` title is underlined, because
  the `#` size gain alone is not apparent. Only the title is underlined; `##` section
  headings are not. The underline probe (`evaluation/underline_probe.md`, screenshot
  `evaluation/layout_capture/underline_probe-claude-ai.png`) showed `<u>` printed
  literally, and combining U+0332 underlining but broken at spaces and unsafe for
  copy and screen readers. The user chose a `---` line directly under the title, with
  a blank line between them so it stays a thematic break rather than a setext
  heading. Phase 7 writes the rule. `tests/test_layout_capture.py`
  pins the round-2 baseline (no `lint_markdown` break; heading levels {2, 3} and {2}).
  It is a record, not a gate.
- Phase 5 finding: `icon_count` misses an icon that follows a section number
  (`## 1. 🧩`). It is left unchanged, as a heuristic that never gates; Phase 10's
  conformance score handles numbered headings.
- Skill upgrade V2 Phase 6 (make room), user 2026-11-02: the user approved moving the
  strategy section fully to a reference, which reverses its embedding in `2714c69`.
  It is now `references/explanation-methodology.md` §15, always-on, and `SKILL.md`
  keeps the heading and a 3-line pointer. The repair and work-report bullets moved to
  §16 and §17 inside `op:repair` and `op:work-report` markers. Each operation keeps its
  `## Operation:` heading and a one-paragraph pointer, and the Scope pointers became
  marked bullets. No new skill file was added.
- Phase 6 Step 3: 17 questions became 12, labelled and in page-shape order, not the
  9 the plan named. Every operation check stays inside its own markers, so each
  single-op ablation build keeps its check. The persistence check was cut as a
  duplicate of `op:persistence`'s "check the reply against each one".
- Phase 6 merges, dropping no rule:
  - visible separation with the `---` between topics;
  - the parts-get-headings rule with smaller sections and the numbered map;
  - "render as markdown" with the artifact rule;
  - the load-bearing node and `classDef` peers with the colour-code rule;
  - Step 2's closing length line (a duplicate) was removed;
  - the `op:sequencing` expert clause was shortened, because Step 2 carries it.
- Phase 6 counts: the `SKILL.md` body is 440 lines in the validator's count (it was
  494), and 389 rendered (guard 460). A raw-body guard of 440 or fewer is in
  `test_skill_structure.py`. `test_presentation_upgrade.py` gains a `MOVED` registry
  (moved rule in the reference, plus its pointer) with removal tests. The V2 change
  record is `docs/SKILL_UPGRADE_PLAN_V2.md`.
