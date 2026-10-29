# Compatibility

What has actually been tested, on what, and what is only documented. Anything in the
**Unverified** column has not been observed by this project and should not be relied on.

Checked 2026-10-29 against Claude Code **2.1.311** and Anthropic's documentation at
[code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins) and
[claude.com/docs/plugins/overview](https://claude.com/docs/plugins/overview).

## Install paths

| # | Surface | Artifact | Status | How it was checked |
|---|---|---|---|---|
| 1 | Claude Code, one session | `dist/socialized-claude-plugin.zip` | ✅ Verified | `claude --plugin-dir ./dist/socialized-claude-plugin.zip plugin list` → `socialized@inline`, `Status: ✔ loaded` |
| 2 | Claude Code, one session | `plugins/socialized/` folder | ✅ Verified | Same command against the folder |
| 3 | Claude Code, installed | local marketplace in this repo | ✅ Verified | `marketplace add` → `install` → `list` → `update` → `uninstall` → `marketplace remove`, full round trip, baseline restored |
| 4 | Claude Code, installed | GitHub marketplace (`A-Piyas-04/Socialized-Claude`) | ⚠️ Unverified | Needs the repository to be public and a clean machine. Same `marketplace.json` that path 3 used. |
| 5 | Claude Code, manual | `skill/socialized/` copied to `~/.claude/skills/` | ⚠️ Unverified | Documented by Anthropic; not exercised here |
| 6 | claude.ai chat | `dist/socialized.zip` via **Customize → Skills** | ⚠️ Unverified | Archive layout matches the documented requirement (`socialized/SKILL.md` at the archive root) |
| 7 | claude.ai chat | `dist/socialized-claude-plugin.zip` via **Customize → Plugins → Add → Upload plugin** | ⚠️ Unverified | Documented to accept a `.zip` "as long as the archive holds one `.claude-plugin/plugin.json`". Ours holds exactly one, at `socialized/.claude-plugin/plugin.json`. |
| 8 | Cowork | via the claude.ai account (path 7) | ⚠️ Unverified | Documented to load skills from account plugins |
| 9 | Claude API | Skills API | ❌ Out of scope | Requires a paid API key, which this project does not use |

Paths 6, 7 and 8 need a claude.ai account action and cannot be exercised from this repository.
They are **documented-compatible, not tested**. Do not read ⚠️ as "broken" — it means nobody
here has seen it work.

## What this plugin contains, and therefore where it works

The plugin ships **one skill and nothing else**: no agents, hooks, MCP servers, LSP servers,
commands, output styles, themes or `bin/` executables. Verified with
`claude plugin details socialized@socialized-claude`, which reported `Skills (1) socialized`
and zero of everything else.

That matters, because surfaces differ only in which components they load:

| Component | Chat | Cowork | Claude Code | In this plugin? |
|---|---|---|---|---|
| Skills | Loads | Loads | Loads | **Yes, one** |
| Commands | Loads as a skill | Loads | Loads | No |
| Agents | Ignored | Loads | Loads | No |
| Hooks | Ignored | Loads | Loads | No |
| MCP connectors | Connectors tab | Loads | Loads | No |
| `bin/` executables | **Refuses the plugin** | **Refuses the plugin** | Loads | No |

Since the only component is a skill, and skills load everywhere, there is no surface on which
this plugin is partial — and no surface on which it can run code, reach a network service, or
execute anything on your machine.

## Requirements

| Requirement | Detail |
|---|---|
| Claude plan | Skills are documented for Free, Pro, Max, Team and Enterprise. The plugin directory's **Discover** list is Pro, Max, Team and Enterprise. |
| Code execution | Must be on for custom skills in claude.ai ("create and edit files"). Team and Enterprise may need an admin to allow it. |
| Claude Code version | 2.1.311 verified. `--plugin-dir` with a `.zip`, and one-step `--marketplace` install, need recent versions (2.1.275+ in a session, 2.1.292+ from the shell). |
| API key | **None.** No paid inference, no separate service, no backend. |
| Account limits (claude.ai) | Up to 25 self-added marketplaces; a plugin may hold 5,000 files and 200 MB. This plugin is 6 files and 25 KB. |

## Activation: four different things

Most confusion about Skills comes from treating these as one state. They are not.

| State | What it means | How you confirm it |
|---|---|---|
| **Installed** | The files are on your account or machine | `claude plugin list`, or the Skills/Plugins list in claude.ai |
| **Available** | Claude can see the skill's description this session | `/` menu lists it; `/plugin` **Installed** tab |
| **Invoked** | Claude chose to load `SKILL.md` for this message | The activity/thinking panel shows the file being read, or you typed `/socialized` |
| **Reliably applied** | Claude follows the skill's rules across a conversation | **Not established.** No controlled measurement exists. |

Installing gets you the first two. The third is Claude's decision per message and is **not
guaranteed** — that is how Skills work, not a defect in this one. The fourth is the open
question this project has not answered; see [LIMITATIONS.md](LIMITATIONS.md).

## Token cost

Two independent estimates, neither a billing measurement:

| Source | Always on | When invoked |
|---|---|---|
| This repository (`python scripts/token_budget.py`) | 37 tokens (metadata) | 5,543 tokens (`SKILL.md`) + up to 8,281 for references read on demand |
| Claude Code (`claude plugin details`) | ~67 tokens | ~7.7k tokens |

They disagree, and both say they are estimates. Ours counts the rendered Markdown with
Anthropic's legacy public tokenizer; Claude Code's counts whatever it wraps the skill in. Treat
either as an order of magnitude, and neither as what you will be billed.

## Known platform limitations

- **Skills do not sync from Claude Code to claude.ai.** A plugin installed from the command
  line stays on that machine. The reverse does sync: a plugin added on claude.ai reaches
  Claude Code as a `@synced` plugin.
- **Cloud sessions** (claude.ai/code) do not load plugins you installed on your own machine.
- **Chats started before you enable the skill** do not pick it up. Start a new one.
- **Relative `source` paths in a marketplace** resolve only for Git-added and local-path
  marketplaces, which is why path 3 above uses `./`.
- **Directory submission has not been attempted.** `--profile directory` validation passes now
  that the MIT licence is in place ([LICENSING.md](LICENSING.md)); the plugin still has no
  listing icon, which the validator reports as a warning.
