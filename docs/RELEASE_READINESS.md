# Release-readiness checklist

For Phase 6, when a release is actually decided. Nothing here has been executed:
this repository has published nothing, tagged nothing, and submitted nothing.

Work down the list in order. Anything that fails stops the release rather than being
noted as a known issue.

## 1. Offline gate

```
python scripts/verify.py
```

All checks must read PASS. A SKIP in the offline tier is a failure to investigate,
not a pass. Record the summary line in the release notes.

## 2. Optional Claude CLI gate

```
python scripts/verify.py --with-cli
```

If the CLI is installed, `claude plugin validate ./plugins/socialized` and
`claude plugin validate ./.claude-plugin/marketplace.json` must both pass. If it is
not installed, the result is "skipped, not passed" — say so in the release notes
instead of implying it passed.

## 3. Canonical package hashes

```
python scripts/version_lock.py
```

Then record, in the release notes, the version and both digests from
`scripts/version_lock.json`:

| Artifact | Where the digest lives |
|---|---|
| `dist/socialized.zip` | `scripts/version_lock.json`, `dist/socialized.manifest.json` |
| `dist/socialized-claude-plugin.zip` | `scripts/version_lock.json`, `dist/socialized-claude-plugin.manifest.json` |

The per-file digests in the two manifests let anyone verify a downloaded archive
without trusting the release page. Builds are deterministic, so a reader can rebuild
from source and compare bytes.

## 4. Version decision

- Bump `version` in `plugins/socialized/.claude-plugin/plugin.json` on purpose, not
  because a check demanded it.
- `python scripts/version_lock.py --update` after the bump.
- `CHANGELOG.md`: move the `Unreleased` section under the new version.
- Decide whether this release is still pre-1.0. Two tests currently assert it is
  (`test_plugin_structure.py::test_plugin_manifest_is_valid` and
  `test_multiturn_policy.py::test_plugin_version_tracks_the_shipped_content` reject a
  `1.` version); a real 1.0 is a deliberate edit to both, not an accident.

## 5. Install smoke test, both paths

Do these by hand on a clean account or profile, and write down what was observed.

**claude.ai Skill**

1. Upload `dist/socialized.zip` in Settings → Capabilities → Skills.
2. Confirm it appears with the name **Socialized-Claude** and its description.
3. Ask one question that should trigger it ("how does X work?") and one that should
   not ("fix this typo"), with the activity panel open.
4. Record whether activation was visible. Activation is the model's decision and is
   not guaranteed — see `docs/LIMITATIONS.md`.

**Claude Code plugin**

1. `/plugin marketplace add <repo or local path>`
2. `/plugin install socialized`
3. Confirm the skill is listed, then run one explanation-shaped prompt.
4. Confirm uninstall works and leaves nothing behind.

## 6. Licence decision

There is **no `LICENSE` file in the repository yet**. "Open source" cannot be claimed
until one exists. Decide the licence, add the file, and state it in `README.md`, the
plugin manifest if the field is used, and the marketplace entry. Check that the
research material under `research-results-2026-10-26/` and anything quoted in
`COMMUNICATION_EXEMPLARS.md` is compatible with the licence chosen.

## 7. Manual communication spot-check

Not a graded exercise, and not a bulk one. Six to ten prompts, read once each,
looking only for the failures in `docs/REGRESSION_INVENTORY.md` that are marked
*Observable only in conversation*:

- a teaching question ("how does a database index work?") — is a mechanism left
  without a figure that needs one?
- a long answer — does the last third keep the support the first third got?
- a short factual question — does it stay short, with no quiz and no preview?
- a code fix — no tutorial framing, no closing check question?
- a correction turn ("no, I meant the write path") — is the reply targeted rather
  than a re-explanation?
- a one-off preference ("shorter, just this time") followed by a normal question —
  did the preference stop?

Write the observations down as observations. They are not a measurement, and a good
spot-check is not evidence that explanations are clearer.

## 8. What the release notes must not claim

- Not that Claude's answers are measurably better. Nothing here measures that.
- Not a token saving in billed usage. The counts are local estimates.
- Not universal or reliable activation.
- No judge score, win rate, or improvement percentage.

What can be claimed: the skill is well-formed, the packages match the source byte for
byte, both install paths are documented and smoke-tested, and the policy contracts
listed in `docs/REGRESSION_INVENTORY.md` are structurally protected.

## 9. Out of scope here

Directory or marketplace submission, marketing assets, release automation that
publishes artifacts, and any public performance claim all belong to Phase 6 and are
deliberately absent from Phase 5's CI.
