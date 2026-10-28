# Installing and using Socialized-Claude

No API key, paid inference, separate account, or local model is needed. The
skill runs inside your existing Claude account and uses your normal usage limits.

> **Interface note.** Claude's menus change over time. The paths below come from
> Anthropic's documentation as checked on 2026-10-26: the platform "Agent Skills"
> overview and the Help Center article "How to create custom skills". If your
> screen differs, search the Help Center for "custom skills".

## 1. Requirements

- **A Claude plan with Skills.** Anthropic's platform documentation lists
  custom Skills in claude.ai for **Pro, Max, Team, and Enterprise**. The Help
  Center's skill-creation article also lists **Free**. Check your own Settings.
- **Code execution enabled.** Custom skills depend on Claude's code-execution
  ("create and edit files") capability. On Team and Enterprise plans, an
  administrator may need to allow it.
- **Per-user installation.** Custom skills uploaded to claude.ai are private to
  your account. They do not sync to the Claude API or to Claude Code.

## 2. Locate the installable file

```
dist/socialized.zip
```

It contains one folder, `socialized/`, with `SKILL.md` and a `references/`
folder inside. That is the structure claude.ai expects. Do not unzip and re-zip
it. If you change the skill source, rebuild it:

```
pip install -r requirements-dev.txt
python scripts/validate_skill.py
python scripts/package_skill.py
```

## 3. Upload and enable

1. Open claude.ai (web or desktop app).
2. Go to **Customize → Skills**. Some interface versions show Skills under
   **Settings → Features** instead.
3. Choose to add or upload a skill, and select `dist/socialized.zip`.
4. Make sure the `socialized` toggle is **on**.
5. Optional: to test this skill on its own, turn other custom skills off.

## 4. Use it

Ask for explanations as usual, for example:

- "How does a heat exchanger work?"
- "I don't understand why recursion doesn't loop forever."
- "Explain this function and why each part is needed."

Claude decides whether to load the skill, based on the skill's description.
Loading is **not guaranteed**. Requests that are not about understanding
something (translation, formatting, greetings, code changes) should not trigger
it, and the skill itself tells Claude to answer those normally.

### Explicit invocation

To ask for it directly, start your message with:

```
Use the socialized skill for this.
```

## 5. Check that it was used

When Claude uses a skill, it reads the skill's files. Where the interface shows
Claude's tool activity or thinking, expand it and look for
`socialized/SKILL.md` being read. The Help Center suggests reviewing
Claude's thinking to confirm a skill is loading.

- Seeing the file read is **evidence of activation**.
- Seeing nothing does **not** prove the skill was skipped. Some surfaces show
  less detail.
- **Asking Claude "did you use the skill?" is not reliable evidence.** It is
  self-report, and it changes the conversation.

The answer should not mention the skill, its steps, or labels such as
"operations". If it does, that is a defect worth reporting.

## 6. Disable or uninstall

- **Disable:** turn off the `socialized` toggle in Skills settings. New
  chats will no longer have it.
- **Uninstall:** delete it from the Skills list.
- **Switching to an ablation variant** (evaluation only): delete the installed
  `socialized` first. All variants share the same name.

## 7. Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Upload rejected | ZIP structure, name, or description invalid | Run `python scripts/validate_skill.py dist/socialized.zip`. Upload the ZIP from `dist/`, not a re-zipped folder. The ZIP must contain the `socialized/` folder at its root. |
| Upload rejected, mentioning description length | claude.ai's 200-character description limit | The shipped description is 164 characters. If you edited it, shorten it. The validator enforces 200. |
| No Skills section in settings | Plan or region lacks Skills, or code execution is off | Enable code execution. Check plan eligibility. Ask your admin on Team or Enterprise plans. |
| Skill never seems to load | Toggle off, chat started before enabling, or the description didn't match | Start a new chat after enabling. Try the explicit invocation line. Check the activity panel. |
| Skill loads for unrelated requests | Description matching is decided by Claude | Report the prompt. The skill tells Claude to answer non-teaching requests normally, so the response itself should be unaffected. |
| Answers became longer | Possible over-application | Report the prompt and response. Avoiding verbosity is an explicit design target (`evaluation/EVALUATION_PLAN.md`, S5). |
| Works in claude.ai but not elsewhere | Skills don't sync across surfaces | For Claude Code, copy `skill/socialized/` to `~/.claude/skills/socialized/`. Other surfaces need their own upload. |

## 8. Other Claude surfaces (optional)

- **Claude Code.** Place the folder (rendered, or the source folder; the
  `<!-- op:… -->` markers in the source are HTML comments and harmless) at
  `~/.claude/skills/socialized/` or `.claude/skills/socialized/` in a
  project. Or install the plugin (next section), which is the maintained path.
- **Claude API.** Possible through the Skills API, but that requires an API key,
  so it is outside V0's no-key scope.

## 9. Claude Code plugin (Phase 2)

Socialized-Claude is also packaged as a Claude Code plugin. The plugin's skill is
generated from the same source as `dist/socialized.zip`, so behaviour is identical.

**Try it in one session (no install):**

```
claude --plugin-dir ./plugins/socialized
```

Then run `/socialized:socialized`, or just ask a "how"/"why" question.

**Install it from the bundled local marketplace:**

```
claude plugin marketplace add .
/plugin install socialized@socialized-claude
```

**Validate the plugin yourself:**

```
claude plugin validate ./plugins/socialized
```

**Distributable archive:** `dist/socialized-claude-plugin.zip`. Its root folder is
`socialized/`. Rebuild both artifacts after any skill change:

```
python scripts/package_skill.py        # dist/socialized.zip (claude.ai skill)
python scripts/build_plugin.py         # plugins/socialized/** + dist/socialized-claude-plugin.zip
python scripts/build_plugin.py --check # fail if the generated plugin is stale
```

**What runs where, and persistent-guidance options** (Projects, an opt-in
`CLAUDE.md` block): see [`docs/phase-2-implementation.md`](phase-2-implementation.md).
Installing the plugin makes the skill *available*; it is selected per request, not
forced on every answer. There is no always-on guarantee in claude.ai normal chat.

**Uninstall:** `/plugin uninstall socialized@socialized-claude`, or
`claude plugin marketplace remove socialized-claude`. For a `--plugin-dir`
session, just start Claude Code without the flag.
