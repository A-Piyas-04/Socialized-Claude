# Socialized-Claude

**A Claude Skill that changes how Claude explains things: answer first, ideas in dependency
order, the causal mechanism made explicit, and a visual where the mechanism is hard.**

No API key. No paid inference. No separate service or backend. It is a folder of Markdown that
installs into the Claude account you already have.

> **Status: release candidate, pre-1.0, unpublished.** Every offline check is green and both
> install paths are structurally validated. **No controlled evaluation has been run**, so there
> is no evidence that explanations are measurably clearer. See
> [What is and is not established](#what-is-and-is-not-established).
>
> **No licence has been chosen yet**, so this repository is not open source and cannot be
> redistributed. [`docs/LICENSING.md`](docs/LICENSING.md).

## The problem

Ask Claude how something works and the answer is usually correct. It is not always *usable*:
the point arrives in paragraph four, a term is used before it is defined, the mechanism is
described but never explained, and the last third of a long answer loses the structure the
first third had.

Socialized-Claude is a set of rules for those specific failures. Each rule names an action —
not "be clear", but "introduce the prerequisite before the idea that needs it".

## What it is, and what it is not

| It is | It is not |
|---|---|
| A Claude Skill: Markdown instructions Claude loads when a request matches | A new model, a fine-tune, or a model wrapper |
| 12 operations selected per request, plus always-on accuracy rules | An always-on modifier of every answer |
| Installable on claude.ai, Cowork and Claude Code from one source | A hosted service or an API product |
| Free to run inside your existing plan | Something needing an API key or paid inference |
| Text only — no code runs on your machine | A plugin with hooks, agents or MCP servers |

## What it changes

| The answer | Instead of |
|---|---|
| Starts with the answer | Arrives at the answer in paragraph four |
| Introduces an idea before the idea that needs it | Defines the term after using it |
| Names the cause, step by step | Describes what happens, not what makes it happen |
| Takes the shape of its content — steps, a table, a small diagram | Undifferentiated paragraphs, or headings on things that aren't sections |
| Keeps its support to the last third | Front-loads one diagram, then goes bare |
| Holds a standing instruction for the whole chat | Obeys once, then drifts |
| After a correction, answers what you meant | Repeats itself louder |

It deliberately leaves translation, editing, quick facts, greetings, creative writing and
ordinary code changes alone. Full account: [`docs/USAGE.md`](docs/USAGE.md).

## Install

Pick one. Both come from the same source and behave identically.

### claude.ai — upload the skill

1. Download `dist/socialized.zip`.
2. Open **[Customize → Skills](https://claude.ai/customize/skills)** in claude.ai or the
   desktop app, upload the ZIP, and turn it on. Code execution must be enabled.
3. Start a new chat and ask a "how" or "why" question, or start your message with
   `Use the socialized skill for this.`

### Claude Code — try it for one session

```bash
claude --plugin-dir ./dist/socialized-claude-plugin.zip
```

Verified: the archive loads directly, no install, no extraction.

### Claude Code — install it

```bash
claude plugin marketplace add ./
claude plugin install socialized@socialized-claude
```

Uninstall with `claude plugin uninstall socialized@socialized-claude`. The full round trip —
add, install, update, uninstall, remove — is verified on Claude Code 2.1.311.

**Which paths are tested, and on what:** [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md).
**Step-by-step, with the plugin-upload path and uninstall:**
[`docs/INSTALLATION.md`](docs/INSTALLATION.md).

## Did it actually apply?

Four different things get called "it's working". They are not the same:

| State | How you confirm it |
|---|---|
| **Installed** | `claude plugin list`, or the Skills list in claude.ai |
| **Available** | The skill appears in the `/` menu |
| **Invoked** | The activity panel shows `socialized/SKILL.md` being read |
| **Reliably applied** | **Not established.** Nothing here measures it. |

Claude decides per message whether to load a skill. Natural activation is **never guaranteed**
— that is how Skills work. Explicit invocation is the reliable path. Asking Claude "did you use
the skill?" proves nothing: it is self-report, and the question changes the conversation.

## What is and is not established

**Established**, by [`python scripts/verify.py`](docs/VALIDATION.md) and the CLI:

- The skill is well-formed and both archives match the source byte for byte.
- Builds are deterministic and platform-independent — you can rebuild and compare.
- `claude plugin validate` passes, including `--strict`.
- Install, update and uninstall work in Claude Code.
- The policy contracts in [`docs/REGRESSION_INVENTORY.md`](docs/REGRESSION_INVENTORY.md) are
  still present in the text.

**Not established**, and not claimed anywhere:

- That Claude's explanations are measurably better. No controlled comparison has been run.
- That anyone understands the answers more. No comprehension study exists.
- That activation is reliable or universal.
- Any token saving in billed usage. The counts here are local estimates.

There are no benchmark numbers, win rates or improvement percentages in this repository,
because none have been earned. [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) is the long version.

## Check it yourself

```bash
pip install -r requirements-dev.txt
python scripts/verify.py
```

One command, no network, no Claude authentication, no API key. It runs the tests, validates the
skill source and the committed ZIP, checks both distributables against the source, checks the
token budgets and the version lock, recomputes the research archive statistics, and confirms it
changed nothing. `--with-cli` adds the optional `claude plugin validate` tier, which reports
**skipped** rather than passed when the CLI is missing.

The same gate runs in CI on `main` and on pull requests
([`.github/workflows/validate.yml`](.github/workflows/validate.yml)), with no secrets and no
publishing, so it runs unchanged on a fork.

This shows the project is internally consistent. It does **not** show that Claude loads the
skill, follows it, or explains anything better.

## Layout

```
skill/socialized/        The installable skill — source of truth
  SKILL.md                 12 operations, scope rules, accuracy rules
  references/              Loaded on demand: methodology, examples, selection
communication/           Reusable policy modules
plugins/socialized/      Claude Code plugin (manifest + generated skill)
.claude-plugin/          Local marketplace listing the plugin
dist/                    Both archives, each with a per-file hash manifest
scripts/                 Build, validation and evaluation tooling
tests/                   Offline test suite
docs/                    Installation, usage, compatibility, troubleshooting, limitations
research/                EVIDENCE_AUDIT.md and the script that reproduces its numbers
evaluation/              No-API evaluation framework (not yet run)
research-results-2026-10-26/   Read-only experiment archive
```

## Where the design came from

The ExplanationLab archive holds three experiments: 60 single-treatment rewrites, 10 rewrites by
a second model, and an answerability study that hit a ceiling — the proxy answered all 15 items
with no explanation at all.

[`research/EVIDENCE_AUDIT.md`](research/EVIDENCE_AUDIT.md) is blunt about what that supports:
prerequisite sequencing had the best automated fidelity screen, but 4 of its 9 "clean" runs were
unchanged copies of the source; **no treatment has any comprehension evidence**; and several
observed failure modes were caused by the treatment instructions themselves — signposting, a
false "mutually dependent" claim, meta-commentary.

So sequencing and mechanism are used as **hypotheses guarded against those failure modes**, not
as proven techniques. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) separates what is
evidence-driven from what is provisional.

## Documentation

| Document | For |
|---|---|
| [`docs/INSTALLATION.md`](docs/INSTALLATION.md) | Every install path, update and uninstall |
| [`docs/USAGE.md`](docs/USAGE.md) | What changes, how to steer it, five worked requests |
| [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md) | Tested vs unverified, per surface |
| [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Symptoms and what to do |
| [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) | What this project does not know |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How the pieces fit |
| [`docs/VALIDATION.md`](docs/VALIDATION.md) | What each check proves |
| [`docs/RELEASE_READINESS.md`](docs/RELEASE_READINESS.md) | Release checklist, with current status |
| [`docs/LICENSING.md`](docs/LICENSING.md) | The open licence decision |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Setup, the one command, what gets rejected |
| [`SECURITY.md`](SECURITY.md) | Private reporting, and why the attack surface is text |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed, by version |

## Licence

**None yet.** See [`docs/LICENSING.md`](docs/LICENSING.md) for the open decision between MIT and
Apache-2.0, the third-party content audit, and what applying a choice takes. Until a `LICENSE`
file exists, default copyright applies: you may read this repository, but no right to use,
modify or redistribute it has been granted.
