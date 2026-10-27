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
