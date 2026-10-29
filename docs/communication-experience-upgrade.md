# Communication-experience upgrade

Policy v0.6.0, plugin v0.7.0. Brief: `temp/re-enhance--communication.md`.

The owner asked for a better presentation experience from the installed skill,
after the v0.5.0 recovery, from six recurring weaknesses: dense paragraphs,
congested comparison tables, diagram/prose repetition, weak separation of
essential from optional detail, limited visual variety, and insufficient use of
semantic icon-style emojis. This upgrade refined existing operations in place.
No operation, marker, variant or module was added.

**Nothing here shows that answers improved.** Behavioural acceptance stays with
the owner.

---

## 1. What changed

| # | Where | Change | Addresses |
|---|---|---|---|
| E1 | `op:presentation` | One primary idea per paragraph; four sentences / 80 words is a ceiling, not a target; two independently important claims never share a paragraph; lists only for genuinely distinct points. | Dense paragraphs |
| E2 | `op:presentation` | A table cell keeps the verdict so the primary decision is visible at a glance; reasoning stays under the table. No word cap. | Congested tables |
| E3 | `op:sequencing`, `op:presentation` | Internal priority: core understanding, then the supporting mechanism, then optional advanced detail, in separate units. Not a three-section template. | Weak hierarchy |
| E4 | `op:visual`, form cues | Architecture diagrams (components and connections) sit beside sequence diagrams, flowcharts, state tables, compact arrow chains, comparison tables and fenced code. No quota. | Limited visual variety |
| E5 | `op:visual` | A comparison table summarises distinctions; it does not retell the diagram. The v0.5.0 figure-versus-text jobs stay. | Diagram/prose repetition |
| E6 | `op:examples` | A running example shows initial state, action, mechanism, resulting state, and why the result matters, with invented numbers consistent with each other. | Generic examples |
| E7 | `op:visual` | A meaning-matched icon (🗄️ storage, ⚙️ processing, 🔐 security, 💡 insight, …) may label a heading, diagram node, callout or compact label. Intent-sensitive: teaching and architecture may use them as navigation; a code-only, formal or casual reply stays undecorated unless an icon is natural. Never a template, never required, never inside code, identifiers, JSON or logs. The ✅ ❌ ⚠️ 🟢 🟡 🔴 status legend stays. | Semantic icons |

**Mirrored, at no activation cost:** `treatment-selection.md`, `explanation-examples.md`
(a semantic-icons pair), and `communication/` modules to v0.6.0.

**Linter.** `emoji_structure` still flags a decorative or status-only heading mark
and an emoji on every bullet. A heading that opens with a meaning-matched
navigation icon plus words is no longer a flag, so the metric matches the skill.

**Deliberately not done:**

- No new operation, marker, variant or response template.
- No sentence-count quota, table-cell word cap, diagram quota, or mandatory emoji.
- No restoration of quizzes, previews, forced takeaways, or unrequested artifacts.

## 2. Token budget

These are local estimates from the legacy public tokenizer, with the heuristic in
brackets. They are not measured API usage.

| Surface | recovery 0.6.0 | this upgrade | Change |
|---|---:|---:|---:|
| `activation` (loaded `SKILL.md`) | 5,760 [5,813] | **6,085 [6,124]** | +325 (+5.6%) [+311, +5.3%] |
| `metadata` | 37 | 37 | 0 |
| references, on demand | 8,858 | 9,157 | +299 |
| distributable skill | 14,618 | 15,242 | +624 |

`activation.max` is raised 5,900 → 6,200 in `scripts/token_budgets.json`, with
the reason recorded there. The advisory `target` stays 5,000.

This is the first time activation exceeds the Phase 4 baseline (5,946 / 5,966).
That is a recorded deviation from Phase 4B's "activation shrank" assertion: the
new rules are owner-set presentation behaviour and would be lost if moved to an
on-demand reference (the risk Phase 4B Option B documented and did not take).
`tests/test_token_budget.py` inverts the '<' assertion with the reason in the
file, the same pattern as Phase 4C.

**Compaction window.** These sections now sit past Claude Code's 5,000-token
re-attach:

- `op:repair` (partly);
- `op:persistence`;
- `op:work-report`;
- `op:close`;
- Step 3.

The new rules (paragraphs, tables, hierarchy, visual variety, icons, examples)
live in `op:sequencing`, `op:examples`, `op:presentation` and `op:visual`, all
inside the window. claude.ai is unaffected.

**Line guards.** Raw `SKILL.md` is 499 of 500 lines; rendered, it is 451 of 460.

## 3. Remaining limitations

- **No behavioural evidence.** Whether ordinary conversations now read better is
  for the owner to decide.
- **Icons are a judgement.** "Where it helps" and "unless an icon is natural" can
  be read as always or never. The rule names the intents that usually warrant
  them and the ones that usually do not.
- **Hierarchy is silent.** Core → mechanism → optional is internal priority, not
  a visible three-part shape. If answers still interleave those layers, the next
  change would have to make the split more visible, at a template cost the brief
  forbids.
- **The linter is still a heuristic.** It cannot tell a useful heading icon from
  a forced one; it only stops treating the permitted form as a defect.
