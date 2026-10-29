# Communication priority correction

Policy v0.7.0, plugin v0.8.0. Branch `recovery/communication-quality`, unmerged.

The v0.7.0 plugin (policy v0.6.0) failed behavioural acceptance on two real CPU
cache-coherence answers, one through the claude.ai plugin and one through the
standalone skill. The two packages' `SKILL.md` files are byte-identical, so the
cause is the instruction text, not the packaging. This change removes and merges
competing instructions rather than adding new ones. No operation, marker, variant
or module was added.

**Nothing here shows that answers improved.** Behavioural acceptance stays with
the owner.

---

## 1. What failed (owner report, responses not stored)

- Both answers were dense and repetitive: the same mechanism was told in a
  diagram, again in a second diagram, again in prose, and again in a recap.
- The plugin answer's MESI state diagram drew a **read**-triggered transition from
  Modified to Invalid. A remote read moves a Modified line to Shared after a
  write-back; only a remote write (or read-for-ownership) invalidates it.
- Neither answer used meaning-matched icons.

---

## 2. Conflicting instructions found

Each row is an existing instruction that, together with others, pushed length,
repetition, or extra figures. Locations refer to v0.6.0 `SKILL.md` and its
references.

| # | Instruction | Where | Effect |
|---|---|---|---|
| C1 | Six-stage "learnable order" (problem → prerequisites → concept → how → case → consequences) | `op:sequencing` | Read as a template |
| C2 | "Name the obvious approach and how it fails … repeat this for every later mechanism" | `op:sequencing` and `op:mechanism`, Step 3, "Motivation given once" | One extra paragraph per mechanism |
| C3 | Tradeoff named unconditionally | `op:mechanism` | A tradeoff paragraph whether or not it helps |
| C4 | Example applied "in every section that teaches" | `op:examples`, Step 3, "An abandoned example" | The example retells what a figure shows |
| C5 | "The diagram shows who acts in what order, a state table what each step changes, and the sentences after them why" | `op:visual` | A recipe for three tellings of one mechanism |
| C6 | "Add a second only when it carries a materially different dimension" | `op:visual`, `treatment-selection.md` | No test for "different", so two figures of the same transitions both pass |
| C7 | Coverage floor: support "even across the answer", "in the last third as much as the first" | `op:visual`, Step 3, "One diagram carrying the whole answer", "Effort that decays" | Counted figures instead of asking what each shows |
| C8 | Takeaway on every long answer | `op:close` | Another restatement |
| C9 | Core → mechanism → optional hierarchy stated in two places | `op:sequencing`, `op:presentation` | Duplicate rules |
| C10 | Every icon mention a gate: "never as a template or a requirement", "colour, an icon, or a legend only where…", "Are icons navigation, not decoration?", "Decorative icons" | `op:visual`, Step 3, `treatment-selection.md` | No default, so icons were left out |
| C11 | Paragraph size stated as numbers in four places | `op:presentation` ×2, Step 3, "A wall of text" | Ceilings filled; idea separation weak |
| C12 | Accuracy rules covered sentences, not figures | Accuracy rules | Diagrams escaped the factual check |

---

## 3. What was removed, merged, or rewritten

| Conflict | Action | Now |
|---|---|---|
| C1, C9 | Replaced | One planning order in always-on Step 2. `op:sequencing` keeps dependency order plus "show the essential mechanism working on a simple case before variants and implementation detail". |
| C2 | Removed duplicate, narrowed | Stated once, in `op:mechanism`: the main mechanism, and a later one only when it would otherwise look arbitrary. The Step 3 check and the failure mode are gone. |
| C3 | Narrowed | "When it changes what the reader would expect or do." |
| C4 | Narrowed | Reused wherever a later idea needs a concrete case; where a figure already makes an idea concrete, the example adds only what the figure lacks. The trace is state → action → result. |
| C5 | Rewritten | "Give every figure, table, and paragraph a different job: a figure shows what happens and in what order, a table compares options or tracks state, and the text says why and what follows." |
| C6 | Rewritten as a preference with a test | "Prefer one representation per mechanism, and add another whenever it shows something the first cannot (its states versus its order in time, its structure versus its flow), naming that difference in its caption." No cap. |
| C7 | Replaced with a value test | "Give the hardest section its visual first, and give a later idea its own when it is just as hard and would otherwise be dense prose." The last-third check is gone. Recorded as a deviation from the owner's "Visual budget" decision, with the owner's approval. |
| C8 | Narrowed | A takeaway only when it compresses something the body has not already landed. |
| C10 | Replaced | One default-preference icon rule (§4). The second gate is gone. Step 3 asks whether icons are used, not only whether they decorate. |
| C11 | Merged | One idea-based rule: each independently important idea its own unit, cause, mechanism and consequence apart, essential before optional. The four-sentence ceiling stays once in `op:presentation`; Step 3 checks ideas, not numbers. |
| C12 | Extended in place | The first accuracy rule now covers every arrow, state, transition and table cell (§4). |

Also merged: the `classDef`, colour-code and distinct-shape bullets became one; the
"last section" bullet left `op:presentation` (Step 3 still checks it); Step 3's
decoration check and "could any paragraph be deleted" became one check. Step 3 went
from 14 checks to 13.

**References.** `treatment-selection.md` merged five failure modes ("A decorative
diagram", "A visual on top of the same prose", "A diagram retold in steps", "One
diagram carrying the whole answer", "Effort that decays") into "The same mechanism
told twice" and a density clause. It deleted "Motivation given once" and "An
abandoned example". It added "An elaborate figure that is wrong" and a lowest
length-budget line that cuts repetition first. `explanation-examples.md` rewrote two
existing pairs: the figure-and-text pair now shows two forms with different jobs and
triggers on every transition, and the icon pair shows the default. No pair was
added.

**Kept unchanged:** the visual grammar (arrow chains, flowcharts, sequence
diagrams, state tables, two-state tables, bars, `classDef`, status markers),
artifacts opt-in, the selective quiz, the 12 operations and 15 variants,
multi-turn policies, packaging, CI and licensing.

---

## 4. The new priorities

**Planning order (Step 2, always on):**

> Plan silently in this order: the ideas this reader must leave with, and for a
> mechanism a simple concrete run that shows it working; then the forms that show
> those ideas best, each with its own job; then only the detail this reader needs,
> after the core is complete.

This is a planning priority, not an output template. A technical answer shows the
essential mechanism working on a simple case before variants and implementation
detail. Prerequisites and causal accuracy are unchanged.

**Semantic icons (`op:visual`):**

> Prefer meaning-matched icons as navigation in a substantive explanation or
> technical discussion: open the key headings, callouts, or diagram labels (not
> every one) with an icon that marks what kind of part it is (🧠 concept or memory,
> ⚙️ mechanism, 📡 signalling, 🗄️ storage, 🔄 state transition, 📊 comparison,
> 💡 key insight, 🛡️ security). Keep icons out of code, identifiers, JSON, logs,
> formal writing, and short or casual replies.

There is no quota and no every-heading rule. The status legend (✅ ❌ ⚠️ 🟢 🟡 🔴)
is unchanged. The linter's navigation-icon set gained 📊, so none of the eight
default icons is flagged on a heading.

**Diagram accuracy (first accuracy rule, every variant):**

> Hold every arrow, state, transition, and table cell in a figure to the same
> standard: label each transition with its trigger and whose action causes it (a
> read or a write, local or remote), and draw a simpler figure rather than include
> a transition you cannot confirm.

Nothing here is specific to cache coherence.

---

## 5. Token budget

Local estimates from the legacy public tokenizer, with the heuristic in brackets.
They are not measured API usage.

| Surface | v0.6.0 | v0.7.0 | Change |
|---|---:|---:|---:|
| `activation` (loaded `SKILL.md`) | 6,085 [6,124] | **6,035 [6,084]** | −50 [−40] |
| `metadata` | 37 | 37 | 0 |
| `treatment-selection.md`, on demand | 2,671 [2,724] | 2,665 [2,705] | −6 [−19] |
| `explanation-examples.md`, on demand | 4,674 [4,799] | 4,794 [4,909] | +120 [+110] |
| `explanation-methodology.md`, on demand | 1,812 [1,764] | 1,812 [1,764] | 0 |
| distributable skill | 15,242 | 15,306 | +64 |

Activation shrank while gaining the eight-icon vocabulary and the diagram-accuracy
clause. `explanation-examples.md` grew because its figure-and-text pair now shows
two forms used well; it is read only on demand. `activation.max` is lowered
6,200 → 6,150; the advisory `target` stays 5,000. Raw `SKILL.md` is 496 lines (was
499 of 500); rendered, 445 (was 451 of 460).

**Compaction window.** `op:repair` is back inside Claude Code's 5,000-token
re-attach window. `op:persistence` (partly), `op:work-report`, `op:close` and
Step 3 remain past it. claude.ai is unaffected.

---

## 6. Validation

`python scripts/verify.py` runs pytest, skill validation on source and ZIP, both
`--check` drift modes, token budgets, the version lock, archive recomputation and
the working-tree check. New suite `tests/test_communication_priority.py` checks:

- the planning order is in Step 2;
- the repetition-driving phrases are gone;
- one-representation stays a preference with no cap;
- the visual grammar survives;
- the icon default ships with its exclusions, and the linter accepts all eight icons;
- the diagram-accuracy clause ships in the `core` variant;
- Step 3 is shorter and activation is smaller;
- both installs carry the same `SKILL.md`.

Earlier suites whose pinned phrases were replaced say why at each changed
assertion.

---

## 7. Remaining limitations

- **No behavioural evidence.** Structural tests show which text ships, not that
  answers read better.
- **The diagram check is a request, not a guarantee.** The model can still draw a
  wrong transition; the rule asks it to name triggers and to prefer a smaller
  correct figure.
- **Judgement words remain.** "Key headings", "a different job" and "shows
  something the first cannot" can be under- or over-applied.
- **Icons are now a default.** If answers become over-decorated, the fix is in this
  one bullet, not a new gate.
