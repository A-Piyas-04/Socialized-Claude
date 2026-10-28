# Phase 2 — Claude Plugin MVP

Phase 2 makes Socialized-Claude installable as a Claude Code plugin and documents
every honest integration path. It changes **no** communication behaviour: the
twelve explanation operations, the Phase 1 intent section, the reference files,
and the existing claude.ai skill package are untouched. The plugin's skill is
generated from the same source, so the plugin and the standalone skill behave
identically.

> **Written for:** the project owner and a Phase 2 acceptance reviewer.

## Architecture

```text
skill/socialized/                       canonical skill (source of truth, unchanged)
  SKILL.md, references/*.md
dist/socialized.zip                      claude.ai custom-skill package (unchanged)

plugins/socialized/                      the Claude Code plugin
  .claude-plugin/plugin.json             manifest (source of truth, hand-written)
  skills/socialized/                     GENERATED from skill/socialized/ (byte-identical to dist/socialized.zip)
    SKILL.md, references/*.md
  README.md                              maintainer note (not shipped in the plugin ZIP)
.claude-plugin/marketplace.json          local marketplace listing the plugin by relative path
dist/socialized-claude-plugin.zip        distributable plugin archive (root folder: socialized/)
scripts/build_plugin.py                  renders the plugin from the skill; --check guards drift
```

**No divergence by construction.** `scripts/build_plugin.py` renders the canonical
skill (full variant, operation markers stripped) into
`plugins/socialized/skills/socialized/`. The result is byte-for-byte the same as
the files inside `dist/socialized.zip`. `python scripts/build_plugin.py --check`
fails if the committed plugin tree **or** the distributable ZIP **or** its sidecar
manifest is stale, and the test suite asserts the same, so the copies cannot drift
unnoticed.

### `--check` now verifies the ZIP, not just its existence

Earlier `--check` only confirmed `dist/socialized-claude-plugin.zip` existed on
disk. A hand-edited, truncated, or stale archive would have passed. `--check` now
opens the archive and verifies it against the canonical generated files:

- **Invalid archive / corruption** — a non-ZIP or a ZIP with a bad CRC
  (`zipfile.testzip`) is reported instead of crashing.
- **Incorrect root** — the archive must have exactly one top-level folder,
  `socialized/`.
- **Missing / extra / modified files** — every member (minus the `socialized/`
  prefix) is compared by exact bytes against `zip_files(plugin_files())`.
- **Metadata drift** — once contents line up, the whole archive is compared
  byte-for-byte against a fresh deterministic rebuild, catching timestamp,
  permission, or ordering drift. Builds are already deterministic (fixed
  `1980-01-01` entry dates, fixed mode bits, sorted entries), so a clean tree
  rebuilds identically.
- **Manifest consistency** — `dist/socialized-claude-plugin.manifest.json` must
  agree with the archive: `plugin`, `zip`, `zip_root`, the archive `zip_sha256`,
  and every per-file hash.

`--check` is strictly read-only: it never rebuilds or rewrites an archive it finds
invalid (a dedicated test asserts a tampered ZIP is left untouched). Rebuilds
happen only on a bare `python scripts/build_plugin.py`.

## Changed and new files

| File | Status | Purpose |
|---|---|---|
| `plugins/socialized/.claude-plugin/plugin.json` | new (source) | Plugin manifest: `name: socialized`, `displayName: Socialized-Claude`, `version: 0.1.0`. |
| `.claude-plugin/marketplace.json` | new (source) | Local marketplace for one-command install in Claude Code. |
| `plugins/socialized/skills/socialized/**` | new (generated) | The plugin's skill, rendered from `skill/socialized/`. |
| `plugins/socialized/README.md` | new | Maintainer note; marks generated files; excluded from the ZIP. |
| `scripts/build_plugin.py` | updated | Reproducible build + `--check` sync guard; `--check` now verifies the ZIP contents and manifest, not just existence. |
| `dist/socialized-claude-plugin.zip` (+ `.manifest.json`) | new (generated) | Distributable plugin archive. |
| `tests/test_plugin_structure.py` | updated | 21 offline tests (manifest, sync, ZIP shape, marketplace, and ZIP/manifest corruption + drift). |
| `skill/socialized/**`, `dist/socialized.zip` | unchanged | Phase 1 skill and claude.ai package preserved. |

No existing test was modified or weakened.

## Compatibility matrix

What actually runs, per surface, verified against current Anthropic documentation
(code.claude.com/docs/en/plugins and support.claude.com, checked 2026-10-28).

| Surface | Install method | What runs | Activation | Always-on guidance? | Plan / prerequisites |
|---|---|---|---|---|---|
| **claude.ai normal chat** | Upload `dist/socialized.zip` as a custom **skill** (Customize → Skills); or add the plugin (Customize → Plugins → custom upload / marketplace) | Skill only — hooks and sub-agents are greyed out in chat | Claude selects the skill when it judges it relevant, or when you name it | **No.** A skill is selected per-request, not forced on every answer | Any paid plan for plugins; Free–Enterprise for custom skills. Code execution must be on |
| **claude.ai Projects** | Same skill/plugin, plus optional Project **instructions** (see below) | Skill + Project instructions for chats in that Project | Skill as above; Project instructions apply to every chat **in that Project only** | Within a Project, Project instructions are applied each turn; they do **not** reach chats outside the Project | Projects-capable plan |
| **Claude Code (terminal / IDE ext.)** | `claude plugin marketplace add .` then `/plugin install socialized@socialized-claude`; or `claude --plugin-dir ./plugins/socialized` | Skill (plugin could also carry hooks/agents/MCP — none added here) | Skill loads when relevant or via `/socialized:socialized`; name + description sit in context each turn | Not from the skill. Optional opt-in `CLAUDE.md` snippet gives per-user/per-project standing guidance | Claude Code ≥ 2.1.x |
| **Cowork / Claude Desktop** | Same plugin install | Skill (and, unlike chat, hooks/sub-agents if a plugin had them) | Skill selected when relevant | No skill-based always-on | Paid plan |

**The honest headline:** installing the plugin or skill makes the guidance
*available*. It does not guarantee the guidance runs on every answer. No supported
plugin component forces always-on communication changes in claude.ai normal chat.

## Persistent guidance — supported options only

### claude.ai normal chat
A skill is chosen per request. There is no documented account-wide
custom-instruction API we can ship a file for. To raise the odds the skill
triggers, keep its description accurate (it is) and name it when you want it.

### claude.ai Projects (optional, scoped)
If you want standing communication guidance for a body of work, create a Project
and paste this into its instructions. It applies to chats **in that Project only**:

```text
When you explain, answer the question in the first sentence, then add only what
this reader needs. Use plain sentences (one claim each, active voice). Lead with
the mechanism for "why/how" questions. Match the intent: teaching builds a mental
model; coding leads with the working solution; debugging leads with the likely
cause and one fix; discussion weighs the real tradeoff; a quick question gets a
quick answer. Use markdown structure and a visual only when the content's shape
calls for it. Keep a requested deliverable (code, JSON, an email) in its own form.
```

Do not expect this to affect chats outside the Project.

### Claude Code (optional, reversible, opt-in)
Claude Code reads `CLAUDE.md` at user scope (`~/.claude/CLAUDE.md`) and project
scope (`<repo>/.claude/CLAUDE.md`). A plugin-root `CLAUDE.md` is **not** loaded
(the validator warns about it), so standing guidance belongs in one of those
files, not in the plugin. To opt in, paste this marked block; to uninstall, delete
the block. It does not overwrite anything else in the file.

```markdown
<!-- BEGIN socialized-claude -->
Prefer Socialized-Claude communication when you explain: answer first, plain
sentences, mechanism for why/how, intent-aware priorities (teaching / coding /
debugging / discussion / quick answer), markdown structure and visuals only when
the content's shape calls for them, and a requested deliverable left in its own
form. Full skill: /socialized:socialized.
<!-- END socialized-claude -->
```

### Hooks
No hook is included. Hooks do not run in claude.ai normal chat, and none is needed
to make the skill available. Adding a `UserPromptSubmit` hook to force the guidance
would only work in Claude Code / Cowork, would bloat every prompt, and is not
required by any Phase 2 deliverable. Recorded as out of scope.

## Validation results

Run locally on 2026-10-28, Claude Code 2.1.311, Windows (PowerShell).

| Check | Command | Result |
|---|---|---|
| Full test suite | `python -m pytest` | **420 passed, 1 skipped** |
| Canonical skill validator | `python scripts/validate_skill.py` | PASSED (0 errors, 0 warnings) |
| claude.ai skill ZIP | `python scripts/validate_skill.py dist/socialized.zip` | PASSED (0 errors, 0 warnings) |
| Plugin ↔ skill + ZIP + manifest sync | `python scripts/build_plugin.py --check` | In sync |
| **Plugin manifest (CLI)** | `claude plugin validate ./plugins/socialized` | **✔ Validation passed** |
| **Marketplace (CLI)** | `claude plugin validate ./.claude-plugin/marketplace.json` | **✔ Validation passed** |

> Note: `python scripts/validate_skill.py dist/socialized-claude-plugin.zip`
> *fails by design* — that tool validates a **claude.ai skill** layout (SKILL.md at
> the ZIP root). The plugin archive has a different, correct shape (`socialized/`
> → `.claude-plugin/plugin.json` + `skills/socialized/…`). The plugin ZIP is
> validated by `build_plugin.py --check` and `tests/test_plugin_structure.py`, not
> by the skill validator.

## Plugin installation acceptance (Claude Code CLI)

Run locally on 2026-10-28, Claude Code 2.1.311, Windows. All steps below are
**non-model** CLI operations: no Anthropic API key, no credits, and no model
conversation was started.

| Step | Command | Result |
|---|---|---|
| CLI version | `claude --version` | `2.1.311 (Claude Code)` |
| Local marketplace add | `claude plugin marketplace add ./ --scope local` | ✔ Added marketplace `socialized-claude` (local settings) |
| Install from marketplace | `claude plugin install socialized@socialized-claude --scope local -y` | ✔ Installed `socialized@socialized-claude` (scope: local) |
| Installed list | `claude plugin list` | `socialized@socialized-claude` 0.1.0, enabled, read from `plugins/socialized` |
| Component inventory | `claude plugin details socialized` | **Skills (1) socialized**; Agents/Hooks/MCP/LSP all 0; always-on ~47 tok, on-invoke ~5.8k tok |
| Cleanup | `claude plugin uninstall … --scope local` + `claude plugin marketplace remove socialized-claude` | ✔ Uninstalled and marketplace removed; `plugin list` back to empty, only the built-in `anthropic-plugin-directory` marketplace remains |

**What this proves:** the marketplace manifest and plugin manifest are accepted by
the real CLI; the plugin installs cleanly from the local marketplace; and the
installed package exposes exactly one skill component, `socialized`, with its files
read from the plugin folder. The skill is therefore **discoverable** to Claude Code
as `/socialized:socialized`.

**CLI quirks observed:**

- `claude plugin marketplace add .` is rejected (`Invalid marketplace source
  format`); the CLI requires an explicit `./` (or `owner/repo` / URL). Use
  `claude plugin marketplace add ./`.
- `/plugin install socialized@socialized-claude` is an interactive in-session
  slash command. The headless equivalent used here is
  `claude plugin install socialized@socialized-claude`.
- Install used `--scope local` so nothing in the user's global plugin config was
  touched; the install also wrote **nothing** to the git working tree.

**Runtime invocation was NOT executed.** Confirming that typing
`/socialized:socialized` in a live session actually loads and applies the skill
requires an authenticated, interactive Claude model session, which would start a
model conversation. Per the task constraints (no silent paid/model conversation),
that was deliberately not run. Discoverability is verified; behavioural activation
is not.

### Shortest manual runtime check (owner, one session)

```text
claude --plugin-dir ./plugins/socialized
# in the session, open the activity/thinking panel, then:
/socialized:socialized
# ask an ordinary "how does X work?" question and confirm the skill fires
```

(Or, after `claude plugin marketplace add ./` + `/plugin install
socialized@socialized-claude`, run `/socialized:socialized` the same way.) This is
the only step that needs a real, signed-in session; everything else above is
reproducible offline or with non-model CLI calls.

`claude plugin validate ./plugins/socialized` additionally reported two
**directory-submission** advisories that it states "do not change the result":
a missing `LICENSE`/`license`, and a missing listing `icon`. These are required
only to *submit the plugin to Anthropic's public directory*, not for local install
or claude.ai upload. They are left for the owner to decide (see Limitations).

**Not tested:** runtime activation and conversational quality. Structural and CLI
validation show the plugin is well-formed and loads; they cannot show the skill
changes Claude's behaviour. Confirm that with ordinary conversations (below).

## Install quick reference

- **claude.ai skill (simplest):** upload `dist/socialized.zip` at Customize → Skills.
- **Claude Code, no marketplace:** `claude --plugin-dir ./plugins/socialized`, then run `/socialized:socialized`.
- **Claude Code, via marketplace:** `claude plugin marketplace add .` then `/plugin install socialized@socialized-claude`.
- **Distributable archive:** `dist/socialized-claude-plugin.zip` (root folder `socialized/`), loadable with `claude --plugin-dir ./socialized-claude-plugin.zip` or via a custom plugin upload.
- Rebuild everything: `python scripts/package_skill.py && python scripts/build_plugin.py`.

## Known limitations

- **No always-on guarantee anywhere.** Skills activate when Claude judges them
  relevant. The best supported standing guidance is scoped (a Project, or an
  opt-in `CLAUDE.md` block), never global.
- **Runtime behaviour unverified.** See above; this is a structural MVP.
- **Directory submission not ready.** A `LICENSE` and a square icon are needed to
  submit to Anthropic's public plugin directory. Not added, because the license is
  the owner's choice.
- **claude.ai custom *plugin* upload format is under-documented.** The support
  article confirms custom plugin upload exists but not the exact archive shape;
  the reliable claude.ai path remains the custom-**skill** ZIP, which is specified.
- **Version 0.1.0 is an experimental MVP**, not a production `v1.0` release.

### Carried to Phase 4 (communication refinements — deliberately NOT fixed here)
The owner's four real-chat sanity checks were strong but noted refinements. These
are communication-engine matters, out of Phase 2 scope, and recorded for Phase 4:

- repeated introductory section previews;
- unnecessary closing quiz / comprehension questions;
- occasionally rigid tutorial structure;
- (related) redundant visualizations.

Fixing these means touching the operations and would risk the Phase 1 behaviour
Phase 2 must preserve. See `docs/LIMITATIONS.md`.

## Handoff — for a Phase 2 acceptance review

Share these so a reviewer can reproduce the result:

1. Output of `python -m pytest`, `python scripts/build_plugin.py --check`, and
   `claude plugin validate ./plugins/socialized`.
2. `plugins/socialized/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
3. `dist/socialized-claude-plugin.zip` and its `.manifest.json`.
4. One or two ordinary conversations in claude.ai and/or Claude Code after
   installing, with the activity/thinking panel open, to show whether the skill
   loads. (No paid API, no bulk scoring.)
5. A decision on the plugin `license` and whether directory submission is wanted.
