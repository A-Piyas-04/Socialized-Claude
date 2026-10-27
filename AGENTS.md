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
