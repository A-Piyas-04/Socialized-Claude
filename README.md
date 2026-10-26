# Explanation Lab V0: a Claude Skill for better explanations

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

1. Get `dist/explanation-lab.zip`.
2. In claude.ai, open **Customize → Skills** (or **Settings → Features**),
   upload the ZIP, and enable it. Code execution must be on.
3. Ask a "how" or "why" question, or start a message with
   `Use the explanation-lab skill for this.`

Full instructions, eligibility, activation checks, and troubleshooting:
[`docs/INSTALLATION.md`](docs/INSTALLATION.md).

## Repository layout

```
skill/explanation-lab/        The installable skill (source)
  SKILL.md                    Core workflow and operations
  references/                 Loaded on demand: methodology, examples, selection rules
dist/explanation-lab.zip      Built package to upload (plus .manifest.json with hashes)
research/
  EVIDENCE_AUDIT.md           What the prior experiments do and do not show; treatment decisions
  recompute_archive_stats.py  Regenerates every number in the audit from the raw archive
evaluation/                   Manual, no-API evaluation framework (see evaluation/README.md)
  EVALUATION_PLAN.md, RUBRIC.md, BASELINE_INSTRUCTIONS.md, RUNBOOK.md
  TEST_CASES.json             33 held-out cases
  comprehension/              Human pre/post/transfer protocol and item bank
scripts/                      validate_skill, package_skill, make_run_sheet,
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

```
pip install -r requirements-dev.txt
python -m pytest                          # 172 tests
python scripts/validate_skill.py          # validate the skill source
python scripts/package_skill.py           # rebuild dist/explanation-lab.zip (deterministic)
python scripts/validate_skill.py dist/explanation-lab.zip
python research/recompute_archive_stats.py
```

Offline validation shows the package is well-formed. It does **not** show that
Claude loads or follows the skill.

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
