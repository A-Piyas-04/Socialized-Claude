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

It contains one folder, `socialized/`, with `SKILL.md`, `LICENSE.txt` and a
`references/` folder of six files inside. That is the structure claude.ai expects. Do not
unzip and re-zip it. If you change the skill source, rebuild it:

```
pip install -r requirements-dev.txt
python scripts/validate_skill.py
python scripts/package_skill.py
```

The build is deterministic: the same source always gives the same ZIP, and
`dist/socialized.manifest.json` records its SHA-256. `SKILL.md`'s frontmatter
carries a version stamp (`metadata: {version: "2.2.0"}`), so you can tell
which build is installed.

## 3. Upload and enable

1. Open claude.ai (web or desktop app).
2. Go to **Customize → Skills**. Some interface versions show Skills under
   **Settings → Capabilities** or **Settings → Features** instead.
3. If an older `socialized` is installed, delete it first. An old build stays
   active until you do, and answers will follow its older rules.
4. Choose to add or upload a skill, and select `dist/socialized.zip`.
5. Make sure the `socialized` toggle is **on**.
6. Optional: to test this skill on its own, turn other custom skills off.

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

To ask for it directly on claude.ai, start your message with `/socialized`
(the form used for the layout captures in `evaluation/layout_capture/`), or
with:

```
Use the socialized skill for this.
```

### What a long answer looks like

An answer of two or more sections follows a fixed page shape: a `#` title with a
`---` under it, the answer in one or two sentences, an overview diagram for a
chain or process, a one-line map, numbered `##` sections with an icon each, a
🙋 reader's question, and a 🎯 takeaway. A why or how answer adds a 🧠 analogy
callout when nothing the reader knows already shows the mechanism, and a learner
gets a 🧪 check question. Decision and debugging answers get neither.
`skill/socialized/references/layout-exemplars.md` has three complete examples.

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
| Long answers have no title, icons, or 🎯 🧪 callouts | An older build is still installed | Delete `socialized` from Skills, upload the current `dist/socialized.zip`, and start a new chat. This caused every round-1 layout failure in `docs/SKILL_UPGRADE_PLAN_V2.md`. |
| A table prints as raw `\|` text | A broken separator row or a pipe inside a cell | Save the answer to a file and run `python scripts/lint_markdown.py answer.md`. Report what it finds. |
| Works in claude.ai but not elsewhere | Skills don't sync across surfaces | For Claude Code, copy `skill/socialized/` to `~/.claude/skills/socialized/`. Other surfaces need their own upload. |

## 8. Other Claude surfaces (optional)

- **Claude Code.** Place the folder (rendered, or the source folder; the
  `<!-- op:… -->` markers in the source are HTML comments and harmless) at
  `~/.claude/skills/socialized/` or `.claude/skills/socialized/` in a
  project. The terminal shows Mermaid diagrams as source text, not as drawings.
- **Claude API.** Possible through the Skills API, but that requires an API key,
  so it is outside this project's no-key scope.
