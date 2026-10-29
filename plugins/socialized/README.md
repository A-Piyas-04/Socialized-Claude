# Socialized-Claude plugin

A Claude Code plugin that provides the Socialized-Claude communication skill.

## Install

```
/plugin install socialized --marketplace A-Piyas-04/Socialized-Claude
```

From a local clone, `claude plugin marketplace add ./` then
`claude plugin install socialized@socialized-claude`. Full instructions:
[`docs/INSTALLATION.md`](../../docs/INSTALLATION.md).

## Source of truth vs. generated

- **Source of truth (edit these):** `.claude-plugin/plugin.json` (the manifest);
  the skill content lives in the repository's `skill/socialized/`.
- **Generated (do not edit):** `skills/socialized/SKILL.md` and
  `skills/socialized/references/` are rendered from `skill/socialized/` by
  `scripts/build_plugin.py`. They are byte-identical to the contents of
  `dist/socialized.zip`, so the plugin and the standalone claude.ai skill behave
  the same. `LICENSE` is copied from the repository root (MIT).

Regenerate after any change to the canonical skill:

```bash
python scripts/build_plugin.py          # rewrite this tree and dist/socialized-claude-plugin.zip
python scripts/build_plugin.py --check  # fail if this tree is stale
```

This `README.md` is for maintainers and is excluded from the distributable ZIP.
