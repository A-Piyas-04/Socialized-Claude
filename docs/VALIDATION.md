# Validation — how to check this repository

One command runs every check that costs nothing and needs nothing but Python:

```
python scripts/verify.py
```

It exits non-zero if anything fails, prints the exact command to reproduce each
failure, and never writes into the repository. This page is the canonical
explanation; the README and `docs/INSTALLATION.md` link here rather than repeating it.

## Setting up a fresh environment

```
python -m venv .venv
.venv\Scripts\activate        # Windows;  source .venv/bin/activate  elsewhere
pip install -r requirements-dev.txt
python scripts/verify.py
```

Python 3.11 or newer. `requirements-dev.txt` is the whole dependency list:
`pytest` to run the suite and `pyyaml` to read the skill's frontmatter and the CI
workflow. Nothing else is needed, and nothing is downloaded at check time.

Run it from anywhere with an explicit root:

```
python /path/to/smart-claude/scripts/verify.py --project-root /path/to/smart-claude
```

## What the offline gate contains

| Check | Command it runs | What a pass means |
|---|---|---|
| `tests` | `python -m pytest -q` | the deterministic suite passes, including the protected policy contracts |
| `skill-source` | `scripts/validate_skill.py` | `skill/socialized/` is a well-formed skill: frontmatter, limits, markers, references, no secrets |
| `skill-zip` | `scripts/validate_skill.py dist/socialized.zip` | the committed claude.ai package is a well-formed skill in its own right |
| `skill-drift` | `scripts/package_skill.py --check` | the committed ZIP and manifest are what the current source builds |
| `plugin-drift` | `scripts/build_plugin.py --check` | the generated plugin tree, ZIP and manifest match the source |
| `token-budget` | `scripts/token_budget.py --check` | local token estimates stay inside `scripts/token_budgets.json` |
| `version-lock` | `scripts/version_lock.py` | neither package changed without a version decision |
| `archive-stats` | `research/recompute_archive_stats.py` | the research archive still reproduces the numbers in `research/EVIDENCE_AUDIT.md` |
| `tree-unchanged` | `git status --porcelain`, before and after | the checks modified nothing |

Both `--check` modes are read-only: they render the skill in memory and compare,
so a stale package is reported and stays stale until someone rebuilds it on purpose.

Useful flags: `--list` to see the checks without running them, `--only NAME`
(repeatable) to run one, `--verbose` to show output from passing checks too.

## The optional Claude CLI tier

```
python scripts/verify.py --with-cli
```

adds `claude plugin validate ./plugins/socialized` and
`claude plugin validate ./.claude-plugin/marketplace.json`. If the CLI is not
installed, or is on `PATH` but cannot be launched, those checks report **SKIP** and
the summary says "skipped, not passed". A skip never turns into a pass. Use
`--require-cli` to make an unavailable CLI a failure instead, on a machine where
you know it should work.

This tier is local only. Hosted CI cannot be relied on to install and run the
Claude CLI without authentication, so the workflow does not try.

## Regenerating the distributables after an intentional source edit

Editing `skill/socialized/` makes both packages stale. The sequence is:

```
python scripts/package_skill.py                        # rebuild dist/socialized.zip + manifest
python scripts/build_plugin.py                         # rebuild plugins/ and the plugin ZIP
# bump "version" in plugins/socialized/.claude-plugin/plugin.json
python scripts/version_lock.py --update                # record the new packages under that version
python scripts/verify.py                               # confirm no drift remains
```

Builds are deterministic — the same source produces byte-identical archives —
which is what lets the check compare instead of trusting a timestamp.

The version lock exists because `version` in the plugin manifest is what an
installed copy pins itself to. A changed package therefore needs a deliberate
version decision. A documentation or tooling edit changes no package and needs no
bump: the lock only reacts to the archives' bytes.

## What CI does

`.github/workflows/validate.yml` runs `python scripts/verify.py` on pushes to
`main`, on pull requests, and on demand, for Python 3.11 and 3.13. It has
read-only repository permissions, uses no secrets, and so runs unchanged on forks.
It then asserts the working tree is still clean.

## What none of this establishes

Offline validation is a consistency proof about files. It is not evidence about
behaviour. Specifically it does **not** show that:

- Claude **activates** the skill. Activation is the model's decision from the
  description, it differs by surface, and it is not observable from this repository.
- Claude **follows** the rules once the skill is loaded. The tests protect the
  *text and semantics* of the policy contracts — that no mandatory quiz, forced
  visual quota, or automatic preview has crept back in — not the model's obedience.
- The **token counts** are what Anthropic bills. They are local estimates from the
  legacy public tokenizer or a heuristic calibrated to it, labelled as such, and the
  compaction re-attach behaviour they reason about is documented, not measured here.
- Explanations are **clearer** for any reader. No comprehension measurement has been
  run. There is no model judge in this gate and no improvement score anywhere.

`docs/LIMITATIONS.md` has the long form. `docs/REGRESSION_INVENTORY.md` records,
issue by issue, which past failures are now structurally tested and which remain
observable only in a real conversation.
