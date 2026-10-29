# Installing Socialized-Claude

No API key, paid inference, separate account or local model. The skill runs inside your
existing Claude account and uses your normal usage limits.

> **Checked 2026-10-29** against Claude Code 2.1.311 and Anthropic's documentation at
> [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins) and
> [claude.com/docs/plugins/overview](https://claude.com/docs/plugins/overview). Claude's menus
> change; if your screen differs, the current pages are
> [claude.ai/customize/skills](https://claude.ai/customize/skills) and
> [claude.ai/customize/plugins](https://claude.ai/customize/plugins).

Which paths have actually been exercised, and which are documented-only, is the table in
[COMPATIBILITY.md](COMPATIBILITY.md#install-paths). Pick a path:

| You use | Go to |
|---|---|
| claude.ai or the desktop app | [Skill upload](#1-claudeai--upload-the-skill) or [plugin upload](#2-claudeai--upload-the-plugin) |
| Claude Code, just trying it | [One session](#3-claude-code--one-session) |
| Claude Code, keeping it | [Install from the marketplace](#4-claude-code--install-it) |

## Requirements

- **A Claude plan with Skills.** Documented for Free, Pro, Max, Team and Enterprise.
- **Code execution enabled** ("create and edit files") for custom skills on claude.ai. On Team
  and Enterprise, an Owner may need to allow it.
- **Claude Code 2.1.311** is what the commands below were verified on. The `.zip` form of
  `--plugin-dir` and one-step `--marketplace` installs need recent versions.
- Custom skills you upload to claude.ai are **private to your account**.

## 1. claude.ai — upload the skill

The file is `dist/socialized.zip`. Upload it as it is; do not unzip and re-zip it. The archive
must contain the `socialized/` folder at its root, which is what claude.ai looks for:

```bash
python -m zipfile -l dist/socialized.zip
# socialized/
# socialized/SKILL.md
# socialized/references/...
```

1. Open **[Customize → Skills](https://claude.ai/customize/skills)** in claude.ai or the
   desktop app.
2. Upload `dist/socialized.zip`.
3. Make sure the **socialized** toggle is on.
4. Start a **new chat** — chats opened before you enabled it do not pick it up.

Rebuild it yourself after a source edit:

```bash
python scripts/validate_skill.py
python scripts/package_skill.py
```

## 2. claude.ai — upload the plugin

Uploading the plugin instead of the skill has one real advantage: a plugin on your account also
reaches **Cowork** and **Claude Code** as a synced plugin, so you install once.

1. Open **[Customize → Plugins](https://claude.ai/customize/plugins)**.
2. **Add → Upload plugin**, and choose `dist/socialized-claude-plugin.zip`.
3. Turn it on.

Anthropic documents the upload as accepting a `.zip` "as long as the archive holds one
`.claude-plugin/plugin.json`". Ours holds exactly one, at
`socialized/.claude-plugin/plugin.json`, within the documented limits (5,000 files / 200 MB;
this plugin is 6 files and 25 KB).

> **Unverified.** Nobody on this project has run this upload. The archive matches the
> documented requirement, which is not the same as having seen it accepted. If it is rejected,
> use path 1, which has the same skill content.

## 3. Claude Code — one session

No install, nothing written to your settings:

```bash
claude --plugin-dir ./dist/socialized-claude-plugin.zip   # the archive, directly
claude --plugin-dir ./plugins/socialized                  # or the folder
```

Both verified. `claude --plugin-dir ./dist/socialized-claude-plugin.zip plugin list` reports
`socialized@inline` with `Status: ✔ loaded`. Then ask a "how" or "why" question, or run
`/socialized`.

## 4. Claude Code — install it

```bash
claude plugin marketplace add ./
claude plugin install socialized@socialized-claude
```

Start the path with `./`: Claude Code reads a bare `name/name` as GitHub `owner/repo`
shorthand. Once the repository is public you can install from GitHub in one step instead:

```bash
claude plugin install socialized --marketplace A-Piyas-04/Socialized-Claude
```

Confirm it:

```bash
claude plugin list       # socialized@socialized-claude, Status: ✔ enabled
claude plugin details socialized@socialized-claude
```

`details` also prints Claude Code's own token estimate for the plugin. It differs from this
repository's estimate; both are estimates, neither is a bill. See
[COMPATIBILITY.md](COMPATIBILITY.md#token-cost).

Inside a session, the equivalents are `/plugin marketplace add ./`, `/plugin install`, and
`/plugin` for the panel. A plugin installed from the command line loads at the next session
start, or after `/reload-plugins`.

### Updating

```bash
claude plugin update socialized@socialized-claude
```

For a marketplace added from a local path, the plugin is read from its folder, so this reports
"nothing to update" and your edits take effect at the next session start. That is expected.

### Uninstalling

```bash
claude plugin uninstall socialized@socialized-claude
claude plugin marketplace remove socialized-claude      # optional
```

Removing the marketplace also uninstalls every plugin installed from it. For a `--plugin-dir`
session, just start Claude Code without the flag.

The full round trip — add, install, list, details, update, uninstall, remove — was run on
2.1.311 and returned the machine to its exact prior state.

## 5. Other ways

- **Manual skill folder.** Copy `skill/socialized/` to `~/.claude/skills/socialized/`, or to
  `.claude/skills/socialized/` in a project. The `<!-- op:… -->` markers in the source are HTML
  comments and harmless. The plugin is the maintained path.
- **Project-scoped install.** `claude plugin install socialized@socialized-claude --scope
  project` enables it for everyone working in that repository; each collaborator still runs the
  install once on their own machine. Reversible by uninstalling at the same scope.
- **An opt-in `CLAUDE.md` block** for standing guidance, with its scope and how to undo it:
  [`phase-2-implementation.md`](phase-2-implementation.md).
- **Claude API.** Possible through the Skills API, but that needs an API key, which is outside
  this project's no-key scope.

## Verifying what you installed

Builds are deterministic and platform-independent, so you can check a download against the
source rather than trusting it:

```bash
python scripts/package_skill.py --check    # the claude.ai ZIP matches the source
python scripts/build_plugin.py --check     # the plugin tree and ZIP match the source
```

Per-file SHA-256 digests are in `dist/socialized.manifest.json` and
`dist/socialized-claude-plugin.manifest.json`; the archive digests are also in
`scripts/version_lock.json`.

## Checking that it was used

Expand Claude's activity or thinking panel and look for `socialized/SKILL.md` being read.

- Seeing it read is evidence of activation.
- Seeing nothing does **not** prove it was skipped — some surfaces show less detail.
- Asking Claude "did you use the skill?" is self-report and proves nothing.

The answer should never mention the skill, its steps, or words like "operations". If it does,
that is a defect worth reporting.

For why "installed", "available", "invoked" and "reliably applied" are four different things,
see [COMPATIBILITY.md](COMPATIBILITY.md#activation-four-different-things).

## When something goes wrong

[TROUBLESHOOTING.md](TROUBLESHOOTING.md) covers upload rejections, marketplace errors,
activation that never happens, and answers that come out longer than they should.

One note that belongs here: `claude plugin validate ./plugins/socialized` passes, including
`--strict` and `--profile directory`. The directory profile still warns that the plugin has no
listing icon; that warning does not fail validation. The licence is MIT and ships inside both
archives — see [LICENSING.md](LICENSING.md).
