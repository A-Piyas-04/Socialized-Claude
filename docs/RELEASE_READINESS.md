# Release readiness

**Executed 2026-10-29** against commit `1dbe3b7` (branch `production`, identical to `main` and
`origin/main`) plus the Phase 6 documentation changes in the working tree.

**Verdict: not releasable. One blocker is owner-decidable and open (licence); two items are
unverified because they need a claude.ai account action.** Everything mechanical passes.

Nothing has been published, tagged, pushed or submitted. A staged candidate lives in
`dist/release-candidate/` (git-ignored), produced by `python scripts/stage_release.py`.

## Status

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Offline gate | ✅ Pass | `python scripts/verify.py` → `9 passed, 0 failed, 0 skipped` |
| 2 | Test suite | ✅ Pass | `python -m pytest -q` → `561 passed, 1 skipped` |
| 3 | Claude CLI gate | ✅ Pass | `python scripts/verify.py --with-cli` → 11 checks, CLI tier ran (not skipped), Claude Code 2.1.311 |
| 4 | `claude plugin validate --strict` | ✅ Pass | Plugin and marketplace both `✔ Validation passed` |
| 5 | Directory-submission profile | ❌ **Fail** | `--profile directory` → `LICENSE_MISSING`. See item 6. |
| 6 | **Licence** | ❌ **BLOCKER — OWNER DECISION REQUIRED** | No `LICENSE` file. [LICENSING.md](LICENSING.md) has the MIT/Apache-2.0 comparison and the third-party audit. |
| 7 | Private vulnerability reporting | ❌ **Owner action** | [`SECURITY.md`](../SECURITY.md) points at GitHub private advisories; the setting is **not enabled**, so the link 404s until **Settings → Code security** turns it on. |
| 8 | Package determinism | ✅ Pass | Both `--check` modes clean; host byte pinned, so Windows and Linux builds are byte-identical. Hosted CI green on `1dbe3b7`. |
| 9 | Package hygiene | ✅ Pass | Both archives hold only Markdown and one JSON manifest; no `.git`, no secrets, no absolute or traversal paths, 6 files / 25 KB |
| 10 | Version lock | ✅ Pass | `0.5.1`, digests match `scripts/version_lock.json` and both `.manifest.json` files |
| 11 | Version decision | ⚠️ Open | Still `0.5.1`. See [Version](#version) below — **1.0.0 is not appropriate yet.** |
| 12 | Claude Code install smoke test | ✅ Pass | Full round trip on 2.1.311, baseline restored. See [What was tested](#what-was-tested). |
| 13 | claude.ai Skill upload | ⚠️ **Unverified** | Archive layout matches the documented requirement; nobody here has run the upload |
| 14 | claude.ai plugin upload | ⚠️ **Unverified** | Same; documented to accept our archive shape |
| 15 | Public documentation | ✅ Pass | README, installation, usage, compatibility, troubleshooting, contributing, security, licensing; links checked by test |
| 16 | No unsupported claims | ✅ Pass | Guarded by `tests/test_public_release.py`; no benchmark, win rate or improvement figure anywhere |
| 17 | Hosted CI on the release commit | ✅ Pass | Run `40745196820`, `success`, head SHA `1dbe3b7`, Python 3.11 and 3.13 |
| 18 | Release-candidate staging | ✅ Pass | `python scripts/stage_release.py` → 4 artifacts, SHA-256 digests, summary; refuses to run if the gate fails |
| 19 | Manual communication spot-check | ⚠️ **Not run** | Needs ordinary conversations; see [below](#7-manual-communication-spot-check) |
| 20 | Directory / marketplace submission | ⬜ Not attempted | Blocked by items 6 and 7, and requires owner approval |

## What was tested

Claude Code 2.1.311, 2026-10-29, from a clean baseline (no plugins installed, no custom
marketplaces), restored exactly afterwards:

```
claude plugin validate ./plugins/socialized                → ✔ Validation passed
claude plugin validate ./plugins/socialized --strict        → ✔ Validation passed
claude plugin validate ./.claude-plugin/marketplace.json    → ✔ Validation passed
claude plugin validate ./plugins/socialized --profile directory
                                                            → ✘ Validation failed (LICENSE_MISSING)
claude --plugin-dir ./dist/socialized-claude-plugin.zip plugin list
                                                            → socialized@inline, ✔ loaded
claude plugin marketplace add ./                            → ✔ Successfully added
claude plugin install socialized@socialized-claude          → ✔ Successfully installed (user)
claude plugin list                                          → ✔ enabled, 0.5.1
claude plugin details socialized@socialized-claude          → Skills (1), everything else 0
claude plugin update socialized@socialized-claude           → already at latest
claude plugin uninstall socialized@socialized-claude        → ✔ Successfully uninstalled
claude plugin marketplace remove socialized-claude          → ✔ Successfully removed
```

No model call, no billed usage, no paid API. `claude plugin details` also reported the plugin's
own token estimate (~67 always-on, ~7.7k on invoke), which differs from this repository's
estimate; both are estimates and neither is a bill.

## Version

The candidate stays **0.5.1**. Phase 6 changed documentation, added a staging script and added
tests; **no package bytes changed**, so no bump is required and none was made.

`1.0.0` would be appropriate only after items 6, 7, 13, 14 and 19 are resolved — a licence
exists, the claude.ai paths have been seen to work, and someone has read a handful of real
answers. Reaching 1.0 also means deliberately editing the two tests that assert the pre-1.0
state (`test_plugin_structure.py::test_plugin_manifest_is_valid` and
`test_multiturn_policy.py::test_plugin_version_tracks_the_shipped_content`). Doing that because
a checklist reached the end would be the wrong reason.

Note for whoever applies the licence: adding `"license"` to `plugin.json` **does** change the
plugin ZIP's bytes, so that change needs a version bump and
`python scripts/version_lock.py --update`.

## Remaining work, in order

### 1. Licence (owner)

Choose MIT or Apache-2.0 — or say something else — and the mechanical steps in
[LICENSING.md](LICENSING.md#what-applying-the-decision-takes) apply it. Until then items 5, 6
and 20 stay failed and the README cannot call the project open source.

### 2. Enable private vulnerability reporting (owner)

**Settings → Code security → Private vulnerability reporting.** One switch. Until it is on,
`SECURITY.md` names a channel that does not accept reports.

### 3. claude.ai smoke tests (owner, one account action each)

Upload `dist/socialized.zip` under **Customize → Skills**, and
`dist/socialized-claude-plugin.zip` under **Customize → Plugins → Add → Upload plugin**.
Confirm each appears, enable it, ask one question that should trigger it and one that should
not, with the activity panel open. Write down what was observed — activation is Claude's
decision per message and is not guaranteed.

### 4. Manual communication spot-check

Six to ten prompts, read once each, looking only for the failures marked *observable only in
conversation* in [REGRESSION_INVENTORY.md](REGRESSION_INVENTORY.md):

- a teaching question — is a mechanism left without a figure that needs one?
- a long answer — does the last third keep the support the first third got?
- a short factual question — does it stay short, with no quiz and no preview?
- a code fix — no tutorial framing, no closing check question?
- a correction turn ("no, I meant the write path") — is the reply targeted?
- a one-off preference ("shorter, just this time") then a normal question — did it stop?

Write the observations down as observations. They are not a measurement, and a good
spot-check is not evidence that explanations are clearer.

### 5. Then, and only with explicit approval

Tag, publish a GitHub release with the staged artifacts and digests, and consider directory
submission. None of this has been prepared beyond the staged candidate, and no automation in
this repository can perform it.

## What the release notes may not claim

- Not that Claude's answers are measurably better. Nothing here measures that.
- Not a token saving in billed usage. The counts are local estimates.
- Not universal or reliable activation.
- No judge score, win rate or improvement percentage.

What may be claimed: the skill is well-formed; the packages match the source byte for byte and
rebuild identically on any platform; `claude plugin validate --strict` passes; install, update
and uninstall work in Claude Code; and the policy contracts in
[REGRESSION_INVENTORY.md](REGRESSION_INVENTORY.md) are structurally protected.
