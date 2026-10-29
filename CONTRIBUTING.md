# Contributing

Thanks for looking. This is a small, single-maintainer project with an unusual property: most
of what it ships is **instruction text that changes how a model writes**, so a one-word edit to
`SKILL.md` is a behavioural change, while a 300-line docs edit usually isn't. The checks below
exist to keep that distinction visible.

> **Licence:** the project is MIT-licensed ([`LICENSE`](LICENSE)). By submitting a pull
> request you agree that your contribution is licensed under the same terms. See
> [`docs/LICENSING.md`](docs/LICENSING.md).

## Setup

No API key, no Claude authentication, no network, no paid service.

```bash
git clone https://github.com/A-Piyas-04/Socialized-Claude.git
cd Socialized-Claude
pip install -r requirements-dev.txt      # pyyaml, pytest
python scripts/verify.py
```

Python 3.11 or later. CI runs 3.11 and 3.13.

## The one command

```bash
python scripts/verify.py
```

It runs the test suite, validates the skill source and the committed ZIP, checks both
distributables against the source without rebuilding them, checks the local token budgets and
the version lock, recomputes the research archive statistics, and confirms it changed nothing
in your working tree. Each failure prints the exact command to reproduce it. `--list` shows the
checks; `--with-cli` adds the optional `claude plugin validate` tier, which reports **skipped**
rather than passed when the CLI is unavailable.

`python scripts/verify.py` must be green in every commit. It is the same gate CI runs.

Details: [`docs/VALIDATION.md`](docs/VALIDATION.md).

## Where to make a change

| You want to change | Edit | Then |
|---|---|---|
| What Claude does | `skill/socialized/SKILL.md` or `skill/socialized/references/**` | Rebuild both packages (below) |
| A reusable policy module | `communication/**` | Keep it consistent with the skill text |
| Documentation | the `.md` file | Nothing — no package changes |
| Build or validation tooling | `scripts/**` | Add a test in `tests/` |

**`plugins/socialized/**` is generated. Never edit it by hand** — `build_plugin.py` overwrites
it and `verify.py` fails on the drift.

### Rebuilding after a skill edit

```bash
python scripts/package_skill.py      # dist/socialized.zip + manifest
python scripts/build_plugin.py       # plugins/socialized/** + dist/...plugin.zip + manifest
```

Builds are deterministic and platform-independent: the same source produces byte-identical
archives on Windows, macOS and Linux. If that ever stops being true, it is a bug.

### Version lock

A changed distributable needs a deliberate version decision — that is the point of the lock,
not an obstacle to route around.

```bash
# after rebuilding, with a reason to call it a new version:
# 1. bump "version" in plugins/socialized/.claude-plugin/plugin.json
# 2. rebuild again (the manifest is inside the plugin ZIP)
python scripts/version_lock.py --update
```

A documentation-only edit changes no package and needs no bump. The project is pre-1.0 and two
tests assert it: a `1.` version is a deliberate edit to both, not an accident.

## Writing skill text

One rule governs the whole file, from [`AGENTS.md`](AGENTS.md):

> **Every rule names an action the model takes. If a rule can be satisfied by writing a plain
> undifferentiated paragraph, it is written wrong.**

Beyond that:

- The skill must leave non-teaching requests alone. Anything that makes a one-line question
  get a lesson is a regression, not a feature.
- No meta-commentary. An answer must never narrate the operation it is applying. This has
  regressed before; [`docs/REGRESSION_INVENTORY.md`](docs/REGRESSION_INVENTORY.md) lists it
  with the others.
- Mind the token budget. `python scripts/token_budget.py` reports it, and the activation gate
  is a regression ceiling, not a target to grow into.
- Read [`docs/REGRESSION_INVENTORY.md`](docs/REGRESSION_INVENTORY.md) before changing an
  operation. It says which past failures are structurally tested and which are observable only
  in conversation — the second kind will not be caught by any test you run.

## Claims

This project is strict about what it says it can do, and pull requests are held to it:

- Nothing may claim Claude's answers are measurably better. Nothing here measures that.
- No win rate, judge score or improvement percentage.
- No token saving in billed usage. The counts are local estimates.
- No claim of reliable or universal activation.

[`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) is the standing account of what is and is not
established. If a change would make a claim there out of date, update it in the same pull
request.

## Pull requests

1. Branch from `main`.
2. Make the change, rebuild packages if you touched the skill.
3. `python scripts/verify.py` — green.
4. Say in the description whether behaviour changed, and which regression in the inventory the
   change touches, if any.

CI runs the same gate on pull requests, on Python 3.11 and 3.13, with `contents: read`, no
secrets, and no publishing — so it runs unchanged on a fork.

## Things that are deliberately not accepted

- Edits to `research-results-2026-10-26/`. It is a read-only archive and
  `research/recompute_archive_stats.py` must keep reproducing its numbers.
- New strategy or methodology documents. The project's documents are the ones already named in
  the briefs.
- Anything that requires a paid API key or hosted service to run or validate.
- Credentials, tokens or personal paths in the repository, in output, or in logs.
