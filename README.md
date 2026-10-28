# Socialized-Claude: a Claude Skill for better explanations

An experimental, installable Claude Skill that helps Claude explain concepts so
readers can actually build a working mental model. It does this mainly by
**introducing prerequisites before the ideas that depend on them** and by
**making the causal mechanism explicit** for why and how questions. It applies
examples, term definitions, and formatting only when they fill a real gap, and
it leaves non-teaching requests alone.

It needs **no API key**, no paid inference, and no separate service. It runs
inside your normal Claude account.

> **Status: V0, untested in Claude.** The skill installs as a valid package and
> passes all offline checks. **No controlled evaluation has been run.** There is
> no evidence yet that it improves explanations or comprehension. The included
> evaluation framework is how to find out.

## Install

1. Get `dist/socialized.zip`.
2. In claude.ai, open **Customize → Skills** (or **Settings → Features**),
   upload the ZIP, and enable it. Code execution must be on.
3. Ask a "how" or "why" question, or start a message with
   `Use the socialized skill for this.`

Full instructions, eligibility, activation checks, and troubleshooting:
[`docs/INSTALLATION.md`](docs/INSTALLATION.md).

### As a Claude Code plugin

Socialized-Claude is also packaged as a Claude Code plugin (same skill, same
behaviour):

```
claude --plugin-dir ./plugins/socialized          # try it for one session
claude plugin marketplace add .                    # or install from the local marketplace
/plugin install socialized@socialized-claude
```

Installing makes the skill *available*; it is selected per request, not forced on
every answer. What runs on each surface, and the opt-in standing-guidance options,
are in [`docs/phase-2-implementation.md`](docs/phase-2-implementation.md).

## Repository layout

```
skill/socialized/        The installable skill (source of truth)
  SKILL.md                    Core workflow and operations
  references/                 Loaded on demand: methodology, examples, selection rules
communication/           Reusable policy modules (core, strategies, controls) — Phase 1
plugins/socialized/      Claude Code plugin (manifest + generated skill) — Phase 2
.claude-plugin/          Local marketplace listing the plugin
dist/socialized.zip      claude.ai skill package (plus .manifest.json with hashes)
dist/socialized-claude-plugin.zip   Claude Code plugin archive (root folder: socialized/)
research/
  EVIDENCE_AUDIT.md           What the prior experiments do and do not show; treatment decisions
  recompute_archive_stats.py  Regenerates every number in the audit from the raw archive
evaluation/                   Manual, no-API evaluation framework (see evaluation/README.md)
  EVALUATION_PLAN.md, RUBRIC.md, BASELINE_INSTRUCTIONS.md, RUNBOOK.md
  TEST_CASES.json             33 held-out cases
  comprehension/              Human pre/post/transfer protocol and item bank
scripts/                      validate_skill, package_skill, make_run_sheet, run_assistant,
                              prepare_blind_packet, summarize_results, assign_comprehension
tests/                        Offline tests (pytest)
docs/                         INSTALLATION, ARCHITECTURE, LIMITATIONS, DEVELOPMENT_REPORT
research-results-2026-10-26/  The ExplanationLab experiment archive (input, unchanged)
```

## Research basis, briefly

The ExplanationLab archive contains three experiments:

- Experiment 3: 60 single-treatment Gemini rewrites.
- Experiment 4: 10 new rewrites by a second Gemini model.
- Experiment 5: an AI-proxy answerability study that hit a ceiling. The proxy
  answered all 15 items without any explanation.

The audit ([`research/EVIDENCE_AUDIT.md`](research/EVIDENCE_AUDIT.md)) finds:

- **Prerequisite sequencing (T2) had the best automated fidelity screen.** But 4
  of its 9 "clean" runs were unchanged copies of the source.
- **No treatment has any comprehension evidence.**
- **Several observed failure modes were caused by the treatment instructions
  themselves:** signposting, a false "mutually dependent" claim, and
  meta-commentary.

V0 therefore uses sequencing and mechanism as **hypotheses**, guarded against
those failure modes, with the other techniques conditional. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for what is evidence-driven and
what is provisional.

## Run the offline checks

One command, no network, no API key, no Claude authentication:

```
pip install -r requirements-dev.txt
python scripts/verify.py
```

It runs the test suite, validates the skill source and the committed ZIP, checks
both distributables against the source without rebuilding them, checks the local
token budgets and the package version lock, and confirms it changed nothing. Add
`--with-cli` for the optional `claude plugin validate` tier, which reports **skipped**
rather than passed when the CLI is unavailable. `--list` shows the checks.

The same command runs in CI on pushes to `main` and on pull requests
([`.github/workflows/validate.yml`](.github/workflows/validate.yml)).

Offline validation shows the project is internally consistent: the skill is
well-formed, the packages match the source, and the policy contracts are still in
the text. It does **not** show that Claude loads the skill, follows it, or explains
anything better. Full detail, including how to rebuild the distributables after a
source edit: [`docs/VALIDATION.md`](docs/VALIDATION.md). What past failure is
protected by what check: [`docs/REGRESSION_INVENTORY.md`](docs/REGRESSION_INVENTORY.md).

## Evaluate it

The framework compares three conditions:

- **A.** Normal Claude.
- **B.** Claude with a carefully written generic explanation prompt.
- **C.** Claude with the skill, both natural and explicitly invoked.

Everything is done by hand in ordinary chats. The measures are kept separate:

- activation
- adherence
- 9 explanation-quality dimensions
- factual accuracy
- length
- human comprehension

Start with [`evaluation/README.md`](evaluation/README.md) and
[`evaluation/RUNBOOK.md`](evaluation/RUNBOOK.md).

## Next steps

1. **Install it.** Upload the ZIP to your Claude account and confirm it installs
   (criterion S1). Try a few prompts with the activity panel open to see whether
   activation is visible on your surface.
2. **Run the reduced pilot.** Use `make_run_sheet.py --subset pilot16` (64
   responses), have two raters score it, and run `summarize_results.py`.
3. **Fix any problems first.** If S4 (errors) or S5 (verbosity) fails, fix that
   before anything else. If natural activation is low but explicit invocation
   does well, iterate on the description.
4. **Screen the comprehension items, then run the human pilot** (12–18
   participants).
5. **Run the ablation round** only if the pilot shows a signal.

See [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) before interpreting anything.
