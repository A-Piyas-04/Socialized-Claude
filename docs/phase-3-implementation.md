# Phase 3 — Adaptive conversation behaviour

Phase 3 makes the skill use the conversation it is actually given: read what a
follow-up is doing, repair the exact gap, scope preferences correctly, and never
claim continuity it does not have. It adds **no new operation, no new marker, no
new variant, and no second conversation engine** — the guidance extends the
existing `op:repair` and `op:persistence` and the always-on request-reading step.

> **Written for:** the project owner and a Phase 3 acceptance reviewer.

## Already present vs. what Phase 3 adds

| Behaviour the brief asks for | Already there | Phase 3 adds |
|---|---|---|
| Follow-up correction / clarification handling | `op:repair` (re-read the request, answer only the exposed gap, correct a reported mistake, defend a right answer) | Smallest-unresolved-part-first; **change the method, not the wording**, when the first explanation failed; check a disputed claim **before conceding** and fix whatever followed from it |
| Standing user preferences | `op:persistence` (carry forward until changed, recall each before sending, flag conflicts, keep length limits) | **Scope**: an instruction limited to one reply ("for this answer", "this time") applies once and is then dropped |
| Reader level | Step 1.2 (judge level from their words, material, earlier turns) | Treat as known **only what the person has shown**, judged from the active task |
| Intent / task switching | Phase 1 intent section (five strategies, mixed intents) | Shape follows the new task on a follow-up (code request → code first; quick fact stays quick) |
| Follow-up confusion detail | `references/explanation-methodology.md` §10 | Step 1.5: read silently what the follow-up is doing, including feedback *about the reply itself* (too long, too complex, too shallow, too much jargon, wrong format) |
| Accuracy | Accuracy rules | **Continuity honesty**: refer back only to what the conversation contains; name what is missing instead of reconstructing it; claim no cross-session recall |

Nothing was removed. The twelve operations, the five strategies, the reference
files, grammar/visual/sequencing guidance, and both ZIP layouts are unchanged.

## Exact files changed and why

| File | Change | Why |
|---|---|---|
| `skill/socialized/SKILL.md` | Step 1 gains item **5 "The conversation so far"**; `op:repair` +3 rules; `op:persistence` +1 rule; accuracy rules +1 rule; Step 3 +2 gated checks | This is the only file Claude actually loads, so the policy has to live here (brief §85) |
| `communication/strategies.md` | New **"Across turns"** section; version → 0.2.0 | Reusable source of truth for the full across-turns policy, incl. the four correction cases |
| `communication/core.md` | Principle 9 gains preference **scope**; version → 0.2.0 | Keeps the precedence/principle module consistent |
| `communication/controls.md` | Version → 0.2.0 | Version parity across the module set |
| `communication/README.md` | Policy version 0.2.0 + Phase 3 change table | Traceability |
| `plugins/socialized/.claude-plugin/plugin.json` | `version` 0.1.0 → **0.2.0** | `version` **pins installs**; leaving it would withhold the new content from users who already installed 0.1.0 |
| `plugins/socialized/skills/socialized/**` | Regenerated | Generated artifact, rebuilt by `scripts/build_plugin.py` |
| `dist/socialized.zip`, `dist/socialized-claude-plugin.zip` (+ manifests) | Regenerated | Propagation of the revised canonical skill |
| `tests/test_multiturn_policy.py` | **New**, 14 tests | Verifies the shipped policy, in a separate file so Phase 2's test file is untouched |
| `CHANGELOG.md`, `docs/LIMITATIONS.md`, this file | Updated / new | Deliverables 3 and 5 |

**Not touched** (Phase 2 parallel-work safety, brief §8): `scripts/build_plugin.py`,
`tests/test_plugin_structure.py`, `docs/phase-2-implementation.md`,
`.claude-plugin/marketplace.json`, `scripts/package_skill.py`, the validators.
Both build scripts were *run*, never edited.

## How the update reaches both installation paths

`skill/socialized/` is the single source of truth. Both artifacts are regenerated
from it, so neither can drift:

```
skill/socialized/SKILL.md
   ├─ python scripts/package_skill.py  → dist/socialized.zip            (claude.ai custom skill)
   └─ python scripts/build_plugin.py   → plugins/socialized/skills/...  (Claude Code plugin)
                                       → dist/socialized-claude-plugin.zip
```

The plugin's skill stays byte-identical to the claude.ai skill;
`python scripts/build_plugin.py --check` and two tests enforce that. To pick up
Phase 3, re-upload `dist/socialized.zip` in claude.ai, and update/reinstall the
plugin in Claude Code (the `0.2.0` bump is what releases it to existing installs).

## Tests and validators — real results

```
python -m pytest                                        434 passed, 1 skipped
python scripts/validate_skill.py                        PASSED (0 errors, 0 warnings)
python scripts/validate_skill.py dist/socialized.zip    PASSED (0 errors, 0 warnings)
python scripts/build_plugin.py --check                  Plugin is in sync with the canonical skill.
claude plugin validate ./plugins/socialized             ✔ Validation passed
```

Baseline before Phase 3 was 420 passed, 1 skipped. **No existing test was
modified or weakened**; the 14 new tests are additive and live in their own file.

What the new tests assert (shipped policy, not a planning document):

- the operation contract is unchanged — 12 operations, 15 variants, balanced
  markers, and `op:repair` / `op:persistence` each still a single unique heading;
- no `## Operation:` heading mentions conversation/follow-up/multi-turn, so there
  is no parallel engine;
- Step 1 has exactly five items and the fifth reads the conversation silently;
- follow-up reading survives the zero-operation `core` build, so it cannot be
  ablated away, while `op:repair`'s own rules remain correctly gated;
- repair covers non-repetition, method-switching, and check-before-conceding, and
  every rule still names an action;
- persistence distinguishes standing from one-reply instructions;
- the accuracy rules bound continuity claims;
- the multi-turn policy is present in **both** the claude.ai ZIP and the plugin,
  with markers stripped, and the two stay in sync.

## Packaging / line-budget tradeoff

`SKILL.md` is close to its guards, which is the main cost of this phase:

| Guard | Before | After | Limit |
|---|---|---|---|
| Rendered lines (compactness test) | 422 | **443** | < 460 |
| Raw body lines (validator) | 469 | **492** | ≤ 500 |

24 raw lines were added with **8 raw / 16 rendered lines of slack left**. No
consolidation was needed this phase, but the next addition to `SKILL.md` will
need one. The cheapest candidate is the three one-line operation pointers in the
**Scope** section, which restate each operation's own "Use this when…" line
(~13 raw lines); they were deliberately kept because they are the only signal
that repair/persistence/work-report apply outside explanations. Guards were not
raised — raising a guard to fit more prose would hide the real cost.

## Verified locally vs. still needs a real conversation

**Verified locally:** the policy is present and well-formed in the loaded
`SKILL.md` and in both installed artifacts; packaging, manifests and sync are
correct; the operation contract and all prior tests are intact; the plugin
manifest passes the Claude Code CLI validator.

**Not verified, and not verifiable offline:** that Claude actually adapts across
turns. Offline string and structure assertions cannot show conversational
behaviour. Two or three ordinary chats are enough to spot a severe regression.

### Optional acceptance scenarios (ordinary chats; no scoring exercise)

| # | Setup → follow-up | What good looks like |
|---|---|---|
| A | "Explain database replication." → "I understand primary and replica. I don't get how the replica knows what changed." | Goes straight to change records / log application. No re-teaching of roles, no repeat diagram. |
| B | "Explain Kubernetes architecture simply." → "Now explain the technical role of the API server and etcd." | Raises depth, builds on what was established, no beginner restart. |
| C | "That was too long. Just tell me the two actual reasons." | Exactly two reasons. No quiz, no headings. |
| D | After an explanation: "Now write a Python function for this." | Code first. No automatic tutorial or re-explanation. |
| E | "That claim is wrong; the docs say…" | Checks the evidence; corrects the affected part and what followed, or keeps it with a reason. No reflexive concession, no full restatement. |
| F | "For the next answer only, use a table." → later, a new question | Table once, then back to normal. The instruction does not persist. |

These are regression spot-checks, **not** evidence of measured comprehension gains.

## Host-context limits (no overclaiming)

- There is **no durable memory, hidden state, or cross-session recall**. Phase 3
  is response planning over the turns the host supplies; where a referenced turn
  is absent, the skill is told to say what is missing rather than invent it.
- **Installation is not activation.** A skill is selected when Claude judges it
  relevant, or when named. Phase 3 does not change that, and nothing here makes
  the guidance always-on. See `docs/phase-2-implementation.md`.
- Phase 4 still owns the observed closing-quiz, intro-preview, rigid-tutorial and
  duplicate-visual refinements. Phase 3 touched none of them; it only states that
  a follow-up gets no *mandatory* takeaway, check question, heading, table or
  diagram, which was already the controls' position and prevents a direct conflict
  with multi-turn adaptation (brief §79).

## Git status

- Branch `v1.0.3`; Phase 2's work (`4c2134c`, comprehensive ZIP verification) was
  already committed and the tree was clean before Phase 3 began, so nothing of
  the parallel work was overwritten, reverted, amended, squashed or pushed.
- Phase 3 changes are left for the owner to review. Nothing was pushed and no
  remote state was changed.
