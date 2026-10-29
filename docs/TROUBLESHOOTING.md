# Troubleshooting

Symptoms grouped by where they happen. Each row names the likely cause and the next action.
If nothing here matches, open an issue with the prompt, the surface, and what you expected —
see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Installing on claude.ai

| Symptom | Likely cause | Do this |
|---|---|---|
| Upload rejected | The archive was unzipped and re-zipped, so `SKILL.md` sits at the root | Upload `dist/socialized.zip` as it is. Check with `python -m zipfile -l dist/socialized.zip`: every entry must start with `socialized/`. |
| Upload rejected, mentioning the description | The description is too long | The shipped one is 164 characters. Anthropic's specification allows 1,024; this repository enforces a stricter 200 (`scripts/skilllib.py`). If you edited it, shorten it and run `python scripts/validate_skill.py`. |
| No **Skills** section in settings | Code execution is off, or the plan or region lacks Skills | Turn on code execution ("create and edit files") in settings. On Team or Enterprise, ask an Owner. |
| **Upload plugin** rejects the archive | Wrong archive, or more than one `plugin.json` | Use `dist/socialized-claude-plugin.zip`. It holds exactly one, at `socialized/.claude-plugin/plugin.json`. |
| Uploaded, but nothing appears in a chat | The chat was open before you enabled it | Start a new chat. |

## Installing in Claude Code

| Symptom | Likely cause | Do this |
|---|---|---|
| `marketplace add` says it can't find the marketplace | A bare path was read as GitHub `owner/repo` shorthand | Start the path with `./` or `../`: `claude plugin marketplace add ./`. |
| `plugin install socialized` fails | The marketplace name is missing | Use `claude plugin install socialized@socialized-claude`, or `claude plugin install socialized --marketplace ./`. |
| Installed, but no `/socialized` in the `/` menu | The session started before the install | Run `/reload-plugins`, or start Claude Code again. |
| `plugin update` says "nothing to update" | The plugin is read from its folder, not a cloned copy | Expected for a local-path marketplace. Edits take effect at the next session start or `/reload-plugins`. |
| `plugin validate` fails on `LICENSE` | You ran `--profile directory` | Expected today. The repository has no licence yet — [LICENSING.md](LICENSING.md). Plain `claude plugin validate ./plugins/socialized` passes. |
| The plugin vanished after removing a marketplace | Removing a marketplace uninstalls everything from it | That is documented behaviour. Re-add the marketplace and reinstall. |

## Behaviour in conversation

| Symptom | Likely cause | Do this |
|---|---|---|
| The skill never seems to load | Claude decides per message; the request may not look like an explanation request | Start with `Use the socialized skill for this.` If natural activation is consistently poor on requests it should match, that is worth reporting. |
| It loads for unrelated requests | Description matching is Claude's decision | The skill tells Claude to answer non-teaching requests normally, so the answer itself should be unaffected. Report the prompt if it isn't. |
| Answers got longer | Over-application | Report the prompt and the answer. Avoiding added length is an explicit design target, not a side effect to tolerate. |
| A short factual question got a lesson | Scope rule not applied | Report it. The skill's scope section is supposed to prevent exactly this. |
| The answer narrates its own method ("applying the sequencing operation…") | Meta-commentary, a known historical failure mode | Report it. This regressed before and is specifically guarded against. |
| A one-off preference ("shorter, just this time") kept applying | Persistence rule over-applied | Say "back to normal length". Report it. |
| A correction got the same explanation again | Repair rule not applied | Report the correction turn verbatim. |
| It works in claude.ai but not in Claude Code | Installs do not travel from claude.ai to a machine you installed on separately | Install on both, or add the plugin on claude.ai and let it sync to Claude Code. |

## Checking the repository itself

| Symptom | Do this |
|---|---|
| Anything looks stale or inconsistent | `python scripts/verify.py`. It prints the exact command for each failure. |
| `skill-drift` or `plugin-drift` fails | You edited the source without rebuilding: `python scripts/package_skill.py` then `python scripts/build_plugin.py`. |
| `version-lock` fails | A package's bytes changed. That needs a deliberate version decision — bump `version` in `plugins/socialized/.claude-plugin/plugin.json`, then `python scripts/version_lock.py --update`. |
| `tree-unchanged` fails | A check wrote to the working tree. That is a bug in the check; report it with the `git status --porcelain` output. |
| A ZIP's bytes differ between your machine and CI | Should not happen: the archives pin their host byte. If it recurs, report the platform and the `python scripts/package_skill.py --check` output. |
| `archive-stats` fails | Something under `research-results-2026-10-26/` changed. That directory is read-only by project rule; restore it with `git checkout`. |

## Reporting something

Useful reports contain the prompt verbatim, the surface (claude.ai chat, Claude Code, Cowork),
whether activation was visible in the activity panel, and the answer you got. For anything that
looks like a security problem, use [SECURITY.md](../SECURITY.md) instead of a public issue.
