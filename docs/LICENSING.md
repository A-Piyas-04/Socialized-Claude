# Licensing: owner decision required

**Status: BLOCKER. The repository has no `LICENSE` file.**

Nothing in this repository may be described as open source until one exists. No licence has
been chosen here, and none was chosen on the owner's behalf.

## Why this blocks the release

It is not only a convention. Anthropic's own validator refuses a directory submission for it:

```
$ claude plugin validate ./plugins/socialized --profile directory
✘ LICENSE: License missing (LICENSE_MISSING). This plugin has no LICENSE file and
  plugin.json has no `license`. The directory requires one of them.
✘ Validation passed → Validation failed (--profile directory)
```

Observed on Claude Code 2.1.311, 2026-10-29. Without `--profile directory` the same command
prints `✔ Validation passed`, so the plugin is **loadable** today; it is **not submittable**.

Three further consequences:

| Without a licence | Effect |
|---|---|
| Legal | Default copyright applies. Others may read the repository but have no granted right to use, modify or redistribute it. |
| Directory | Submission to Anthropic's plugin directory is refused outright. |
| Claim | README, CHANGELOG and release notes cannot call the project open source. |

## The two reasonable options

Both are permissive, OSI-approved, and compatible with how this project is built (no vendored
third-party code, dev dependencies not redistributed). The real difference is patents and
notices, not permissiveness.

| | MIT | Apache-2.0 |
|---|---|---|
| Length | ~170 words | ~10,000 words |
| Permits commercial use, modification, redistribution | Yes | Yes |
| Requires the licence and copyright notice be kept | Yes | Yes |
| **Express patent grant from contributors** | No (silent) | **Yes** |
| **Patent retaliation clause** | No | Yes — a contributor who sues over patents loses their grant |
| Requires a `NOTICE` of significant changes | No | Yes, when a `NOTICE` file exists |
| Trademark grant | Silent | Explicitly withheld |
| Typical use | Small libraries, skills, templates | Projects expecting corporate contributors or adoption |
| SPDX id for `plugin.json` | `MIT` | `Apache-2.0` |

### What to weigh

- **MIT** is the lower-friction choice for a single-author Skill. It is short enough to read,
  and it is what most community Claude skills and plugins use. It says nothing about patents,
  which for a repository of Markdown policy text and small Python scripts is a small exposure.
- **Apache-2.0** is the safer choice if this project might take contributions from people
  employed by companies, or be adopted inside one. Corporate legal review generally prefers the
  explicit patent grant. The cost is a long file and the `NOTICE`/change-notice obligation.

**If the owner expresses no preference, MIT is the lighter fit for what this repository
actually is.** This is a recommendation, not a decision, and it has not been applied.

Other options (GPL-3.0, MPL-2.0, CC-BY-4.0, proprietary/all-rights-reserved) are deliberately
not listed. A copyleft licence would complicate reuse of the Skill text inside other people's
plugins, which is the main thing someone would do with it. If the owner wants one of these,
say so and it will be applied instead.

## Third-party content audit

Checked 2026-10-29. Nothing found that constrains the licence choice.

| Source | What it is | Obligation |
|---|---|---|
| `skill/socialized/**` | Original text written in this repository | None |
| `communication/**` | Original policy modules | None |
| `scripts/**`, `tests/**` | Original Python, standard library only | None |
| `research-results-2026-10-26/**` | The owner's own ExplanationLab experiment archive: prompts the owner wrote, and model outputs generated from the owner's own accounts | None identified. Model output ownership is governed by the provider's terms, not by a third-party licence. |
| `COMMUNICATION_EXEMPLARS.md` exemplars 1–3 | Short excerpts quoted verbatim from that archive, each with its file and ID | None identified; same origin as above |
| `COMMUNICATION_EXEMPLARS.md` exemplars 4–12 | Constructed for this repository | None |
| `pyyaml`, `pytest` | Dev-only dependencies, both MIT | Not redistributed. Neither appears in `dist/socialized.zip` or `dist/socialized-claude-plugin.zip`. |

No icons, fonts, images, vendored libraries or copied code from other projects are present. The
two distribution archives contain only Markdown and one JSON manifest, all written here —
confirmed by `python -m zipfile -l dist/socialized.zip`.

One point for the owner rather than a lawyer's question: the archive contains answers generated
by Google Gemini and OpenAI models. They are used as *source material* for exemplars, never
redistributed as a product. If a licence is applied to the repository as a whole, it is worth
stating in the LICENSE header, or in `research-results-2026-10-26/README.md`, that the archive
is included as research data rather than as licensed work product.

## What applying the decision takes

Once the owner names a licence, all of this is mechanical:

1. Add `LICENSE` at the repository root with the chosen text and the owner's copyright line.
2. Add `"license": "<SPDX-id>"` to `plugins/socialized/.claude-plugin/plugin.json`.
3. Rebuild both packages (`python scripts/package_skill.py`, `python scripts/build_plugin.py`),
   bump the version, and run `python scripts/version_lock.py --update`. **The plugin manifest is
   inside `dist/socialized-claude-plugin.zip`, so adding the field changes package bytes and
   needs a version decision.**
4. State the licence in `README.md` and in the marketplace entry.
5. Re-run `python scripts/verify.py` and
   `claude plugin validate ./plugins/socialized --profile directory`.
6. Remove this file's BLOCKER status and tick item 6 in
   [`RELEASE_READINESS.md`](RELEASE_READINESS.md).

Until step 1 happens, [`RELEASE_READINESS.md`](RELEASE_READINESS.md) keeps `LICENSE: OWNER
DECISION REQUIRED` as a failing item, and the release candidate stays unpublished.
