# Phase 4B — Token efficiency and instruction architecture

The `SKILL.md` text that loads on activation is about **9.5% smaller** (5,946 to
5,379 local-estimate tokens). The always-on core now sits ahead of the twelve
operations. In long Claude Code sessions, the accuracy rules and reference pointers
therefore survive the 5,000-token re-attach after auto-compaction. The pre-4B
layout lost both.

All twelve operations, every Phase 3 multi-turn rule and every Phase 4 refinement
still ship. No rule was dropped; true duplicates were merged. Claude Code's own
estimator (`claude plugin details`) agrees with the local count: about 6.4k to
about 5.8k tokens on invoke.

> **All counts are local estimates, not measured Claude API usage.** Anthropic does
> not publish the tokenizer of current Claude models. No runtime savings were
> measured, and no model was called.

## 1. Token audit (Task 1)

**Method.** `scripts/token_budget.py` counts every instruction surface with
Anthropic's public pre-Claude-3 tokenizer (`Xenova/claude-tokenizer`, read from the
local Hugging Face cache, never downloaded by the tool). It also runs a stdlib
heuristic calibrated against that tokenizer, which stays within about 1% on
`SKILL.md`. The activation figure is the shipped `SKILL.md`, frontmatter included and
markers stripped, byte-identical to `dist/socialized.zip`.

| Category | Loads | Baseline | Phase 4B | Change |
|---|---|---:|---:|---:|
| Repository instruction files (skill source, `communication/`, persistent snippets, `AGENTS.md`) | mostly never at runtime | 23,516 | 23,159 | −1.5% (`AGENTS.md` grew with this phase's decision entries) |
| Distributable skill (`SKILL.md` + 3 references, as shipped) | — | 14,148 | 13,600 | −3.9% |
| Loaded on activation (`SKILL.md`) | when the skill triggers | **5,946** | **5,379** | **−9.5%** |
| References, on demand | only if Claude reads one | 8,202 | 8,221 | +0.2% |
| Always-on metadata (`name: description`) | every turn while enabled | 37 | 37 | 0% |
| Persistent opt-in snippets (Project instructions + `CLAUDE.md` block) | every turn, where pasted | 227 | 227 | 0% |

Per reference file (legacy tokenizer): `explanation-examples.md` 4,190, `treatment-selection.md`
2,198 → 2,219, `explanation-methodology.md` 1,814 → 1,812. The `communication/`
modules (5,475 tokens) and `AGENTS.md` (2,814) are never shipped; `AGENTS.md` loads
only in development sessions in this repository.

The plugin's `skills/socialized/` copy is byte-identical to the claude.ai package,
so both install paths load the same text.

## 2. Loading mechanism (Task 2)

Sources checked 2026-10-28: the Agent Skills overview
(docs.claude.com/en/docs/agents-and-tools/agent-skills/overview), Claude Code
"Skills", "Memory" and "Plugins" (code.claude.com/docs/en/skills, /memory, /plugins),
and the Help Center articles "Use skills in Claude" and "How can I create and manage
projects?".

| Surface | Always in context | Loads on activation | Needs an explicit read |
|---|---|---|---|
| claude.ai custom skill | `name` + `description` ("about 100 tokens per Skill") | `SKILL.md` body, read with bash when the request matches the description | Each reference file, only when Claude reads it |
| Claude Code skill | Skill listing (name + description, capped at 1,536 characters per entry; the listing scales at 1% of the context window) | Rendered `SKILL.md` enters the conversation as one message and **stays across later turns**; it is not re-read | Reference files |
| Claude Code plugin | Same listing entry per skill, on every turn even when unused | Same as a Claude Code skill | Same |
| claude.ai Project instructions | Applied to every chat in that Project only | — | — |
| `CLAUDE.md` | Loaded in full at session launch; `@imports` load with it and do not reduce cost | — | Subdirectory `CLAUDE.md` files load when Claude touches files there |

Two documented facts drive this phase:

- **Level 2 guidance.** The overview gives "Under 5k tokens" for the `SKILL.md` body.
- **Compaction.** "Claude Code re-attaches the most recent invocation of each skill
  after the summary, keeping the first 5,000 tokens of each." Text past that point
  is lost in long Claude Code sessions.

The docs also say that once a skill loads in Claude Code, "every line is a recurring
token cost."

**Not documented, so not claimed:** whether claude.ai keeps an earlier turn's
`SKILL.md` read in later turns or re-reads it; how often Claude actually reads a
reference file; and the size of the real Claude tokenizer relative to the legacy one.

## 3. Redundancy audit (Task 3)

| Finding | Example | Action |
|---|---|---|
| Rule stated twice | Mixed tasks: Scope ("do the task as usual and apply the skill only to the 'why'") and Strategies ("apply the explanation operations below only to the part that explains") | Kept the Scope version with its example |
| Overlapping bullets | `op:repair`: "check it before conceding…" and "When you still think the earlier answer was right, say so in one clause…" | Merged into one bullet; 7 bullets remain |
| Overlapping bullets | `op:presentation`: "give each idea its own unit… start a new unit" and "start a new paragraph when the idea changes…" | Merged |
| Restated rule | `op:work-report` "Lead with what changed…" followed by "Report what was done." | Removed the restatement |
| Meta prose | Strategies opening: three sentences explaining that strategies "choose priorities, not a fixed structure, so none of them is a template" | Two sentences |
| Self-check restates operations | Step 3 repeated each operation's wording at full length (515 tokens) | Each check kept, written as a short question (379) |
| **Contradiction with Phase 4** | `treatment-selection.md`: "A check question… fits teaching, beginners, and confusion follow-ups"; "A takeaway fits… any teaching request"; "Each idea with a shape gets its own [diagram]" | Rewritten to match the shipped `op:close` / `op:visual`; a reference read must not undo Phase 4 |
| Contradiction with Phase 4 | `explanation-methodology.md`: "Let the close operation supply the last unit" | Now "When a takeaway earns its place…" |

**Kept on purpose, although long:**

- the visual grammar (Mermaid `sequenceDiagram`, `classDef`, bars, the status legend);
- the presentation scanning rules;
- the three Scope pointers to repair, persistence and work-report;
- the running-example and obvious-approach rules.

These are the owner's recorded decisions and the core of the communication quality.
The sequencing and mechanism operations both keep a short "obvious approach that fails"
rule, because each ablation variant must stay self-contained.

## 4. Architecture comparison (Task 4)

| | A — optimized existing skill (implemented) | B — compact core + on-demand visual grammar (proposed) |
|---|---|---|
| Activation (legacy est.) | 5,379 | about 4,980 (moves about 464 tokens of visual drawing rules and artifact handling into a reference, adds a pointer) |
| Activation reliability | Unchanged: same description, same single file | Unchanged for the skill; the drawing rules apply only if Claude reads the new reference before drawing |
| Compatibility | claude.ai, Claude Code, plugin: identical | Same surfaces; the reference must be read via bash on claude.ai |
| Maintenance | Same 4 files and 12 marker blocks | A fifth file; `op:visual` split across two files; tests and ablation variants must follow |
| Regression risk | Low: wording and order only | **Substantial**: `classDef` colour codes, `sequenceDiagram` for time, bars, the emoji legend and the artifact opt-in rules would disappear from context whenever the reference is not read |
| Preserved functionality | All | All in the package, but not reliably in context |

**Recommendation: A.** B buys about 7% more on activation and carries a real risk of
regressing visuals the owner specified. Per the brief, B is documented here and not
implemented. Adopt it only after a skill-on comparison shows no loss. That comparison
would use the existing Claude-vs-Claude harness, comparing visual-form usage per
answer from `scripts/lint_response.py` between the two builds.

## 5. Implemented optimizations (Task 5)

| File | Change |
|---|---|
| `skill/socialized/SKILL.md` | Always-on core first (Scope, Strategies, Steps 1–2, **Accuracy rules**, **Reference files**), then the 12 operations, then Step 3. Duplicates merged, wording tightened, Step 3 shortened, reference pointers name when to read each file (including "which visual form fits"). |
| `skill/socialized/references/treatment-selection.md`, `explanation-methodology.md` | Pre-Phase-4 contradictions fixed (see §3). |
| `plugins/socialized/.claude-plugin/plugin.json` | `version` 0.3.0 → 0.4.0, because `version` pins installs and the shipped text changed. |
| `plugins/socialized/skills/socialized/**`, `dist/socialized.zip`, `dist/socialized-claude-plugin.zip` (+ manifests) | Regenerated by `package_skill.py` and `build_plugin.py`. |
| `scripts/token_budget.py`, `scripts/token_budgets.json`, `scripts/token_baseline.json` | New local token report, configurable budgets, recorded pre-4B baseline (both counters). |
| `tests/test_token_budget.py` | New, 15 tests. |
| `tests/test_multiturn_policy.py` | Plugin version pin 0.3.0 → 0.4.0. |

Unchanged:

- the description and activation metadata;
- the 12 operations, 15 variants and every marker;
- `communication/` (it indexes operations by name, and none was renamed);
- `package_skill.py`, `build_plugin.py` and `validate_skill.py`;
- the marketplace manifest.

No model call, backend, classifier or database was added.

### Section sizes (legacy tokenizer)

| Section | Before | After |
|---|---:|---:|
| Scope + pointers | 279 | 268 |
| Strategies | 391 | 331 |
| Step 1 / Step 2 | 333 / 192 | 311 / 187 |
| Accuracy rules | 345 | 314 |
| Reference files | 155 | 127 |
| Sequencing / mechanism / examples | 224 / 274 / 267 | 209 / 249 / 238 |
| Terms / plain | 101 / 166 | 96 / 158 |
| Presentation / visual | 755 / 785 | 675 / 725 |
| Register / repair / persistence / work-report / close | 148 / 279 / 172 / 139 / 296 | 141 / 260 / 169 / 133 / 292 |
| Step 3 | 515 | 379 |

Before Phase 4B, the sections past the first 5,000 tokens were part of the
Accuracy rules, all of Step 3, and the Reference files. After it, the legacy
tokenizer puts only part of Step 3 there; the heuristic also puts part of `op:close`
there. `token_budget.py` prints this list on every run.

## 6. Validation (Task 6)

Run 2026-10-28 on Windows with Claude Code 2.1.311. No model conversation was started.

```
python -m pytest                                          463 passed, 1 skipped   (448 before; +15 new)
python scripts/validate_skill.py                          PASSED (0 errors, 0 warnings)
python scripts/validate_skill.py dist/socialized.zip      PASSED (0 errors, 0 warnings)
python scripts/build_plugin.py --check                    Plugin is in sync with the canonical skill.
python scripts/token_budget.py --check                    All budgeted components are within budget.
                                                          Above advisory target (does not fail): activation
python research/recompute_archive_stats.py                exit 0
claude plugin validate ./plugins/socialized               √ Validation passed (pre-existing LICENSE/icon advisories)
claude plugin validate ./.claude-plugin/marketplace.json  √ Validation passed
claude plugin details socialized                          always-on ~47 tok; on-invoke ~6.4k → ~5.8k
```

The `plugin details` figure came from a local-scope install that was uninstalled
afterwards. `.claude/settings.local.json` is back to its original content.

**Budgets** (`scripts/token_budgets.json`) are configurable and come in two kinds:

- `max` gates `--check`. Activation's max is 5,500, a regression ceiling about 2%
  above the current size, so any growth is a deliberate edit of the file.
- `target` is advisory. Activation's target is the documented 5,000.

References have no limit, because the overview states bundled files cost nothing
until read. Override a max with `--budget activation=N`; `none` removes it.
Line-count guards (460 rendered / 500 raw) are unchanged; `SKILL.md` is now at
413 / 461.

## 7. Remaining uncertainties and regression risks

- **Tokenizer gap.** Both local counters approximate an older tokenizer. Claude Code's
  own estimator runs about 8% higher than the legacy count. Whether the real
  activation cost is under 5,000 is unknown, so 5,000 stays a target, not a gate.
- **Runtime savings are unmeasured.** Smaller instructions should cost fewer context
  tokens per activation. Prompt caching and product system prompts make the billed
  effect unknowable offline.
- **Order change.** The accuracy rules now come before the operations rather than
  after them. The text is the same, but its position in the prompt changed. Any
  effect on adherence is unmeasured.
- **Tightened wording.** Every behaviour-bearing phrase pinned by the Phase 3 and
  Phase 4 tests is unchanged. Merged and shortened bullets could still shift
  emphasis. The Phase 4 spot-check prompts (`docs/phase-4-implementation.md`) remain
  the quickest manual sanity check.
- **Reference reads.** How often Claude reads a reference is undocumented and was not
  measured. That is the main reason Option B was not implemented.
