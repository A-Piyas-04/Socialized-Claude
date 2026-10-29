# Communication controls — depth, presentation, visuals

Version 0.8.0. How much to say, and how to present it.

**This file is an index, not a second copy of the policy.** Each control names
what the model does and points to the rule in `skill/socialized/SKILL.md` that
states it in full. Before 0.8.0 this file carried its own wording of the same
rules, including numeric thresholds that outlived the skill's (see
`docs/COMMUNICATION_SIMPLIFICATION_AUDIT.md`).

Presentation is a capability to apply when the content's shape calls for it,
never a quota to fill. No answer owes the reader a table, a figure, a heading, an
icon, an example or a takeaway.

## Depth

| Control | What the model does | Stated in |
|---|---|---|
| Depth selection | Sets depth from the explicit request, the question's complexity, the reader's demonstrated understanding, and the cost of omitting a detail. | **Step 2** |
| Proportion | One sentence for a direct factual question; a few units for a conceptual why or how; a precise answer at their level for an expert's narrow question. | **Step 2** |
| No universal count | Imposes no word count, and does not equate a technical topic with a long answer or a short question with a simple problem. | **Step 2** |

## Presentation

| Control | What the model does | Stated in |
|---|---|---|
| Form from shape | Numbered steps for a process; a table for several items across shared dimensions; a labelled list for parallel options; a diagram for a flow, an interaction or how components connect; prose for a single causal chain. Applies in every strategy, not only teaching replies. | `op:presentation`, the strategy section |
| One idea per unit | Gives each independently important idea its own unit, starts a new one when the idea changes, keeps a continuous argument together with its link stated inside the unit, and splits a paragraph that has taken on a second idea. | `op:presentation` |
| Scannable tables | The verdict in the cell, the dimension in each header, and a condition, a second reason or an argument in a list under the table. | `op:presentation` |
| Hierarchy | Essential point first, optional points after, minor caveats together at the end, and specialist depth after the narrative it extends and marked as skippable. | `op:presentation` |
| Headings | `##` then `###` without skipping a level, each stating what the section establishes. No bold line standing in for a heading, and no heading over a one-sentence section. | `op:presentation` |
| Specimens and identifiers | Sample data, snippets, outputs and quoted structures in a fenced block, named in the sentence before it; identifiers, paths, flags and commands in backticks. | `op:presentation` |
| No preview | Answers directly first, and adds no roadmap or heading map the headings already make clear. | `op:plain` |

## Examples and analogies

| Control | What the model does | Stated in |
|---|---|---|
| When to use one | When the abstraction is hard to picture, when the reader asks, or when a concrete case would expose a likely misconception. Left out when the idea is already concrete, the reader is an expert, or the answer is short. | `op:examples` |
| Showing a general claim | Shows a claim about complexity, cost, risk, latency or failure happening to one case — the situation, what the mechanism does, what the reader is left with — instead of asserting it as a property. | `op:examples` |
| One example, reused | Reuses one case where a later idea needs a concrete one, and lets it add only what a figure has not already shown, traced to the moment the behaviour shows, with invented numbers marked and consistent. | `op:examples` |

## Visuals

| Control | What the model does | Stated in |
|---|---|---|
| When to draw | Where showing a relationship saves the reader walking through it in prose, with the sentences it replaces deleted. No quota and no cap; left out where the prose already makes the relationship plain, the answer is short, or a practitioner wants only the lookup. The first figure goes to the hardest idea. | `op:visual` |
| Different jobs | A figure shows what happens and in what order, a table compares options or tracks state, and the text says why and what follows. A second representation of one mechanism is added only when it shows something the first cannot, and names that difference. | `op:visual` |
| Form | Arrow chain for a short linear flow; Mermaid `flowchart` for branches, loops and component connections; Mermaid `sequenceDiagram` for order in time; a two-column table or two labelled blocks for two states; block-character bars for magnitude; one row per moment for change over time. | `op:visual` |
| Legibility | A distinct shape for the load-bearing node, `classDef` classes separating peers from a different kind of thing, and one colour code per answer named once. | `op:visual` |
| Accuracy | Every arrow, state and transition is a factual claim: each transition's trigger and whose action causes it are named, and a simpler figure beats one with a transition that cannot be confirmed. No figure implies a guarantee the mechanism does not provide. | **Accuracy rules**, `op:visual` |
| Markdown by default | Visuals are markdown. An artifact is built only on an explicit request for an artifact, an SVG or something to click, and an interactive version is offered only when asked or clearly useful. | `op:visual` |

## Icons

Optional, where they genuinely help the reader navigate or compare: a
meaning-matched icon on a key heading, callout or diagram label, or a status
marker in a list or table. The same icon always marks the same kind of part.
Never in code, identifiers, JSON, logs, formal writing, or a short or casual
reply; never on every heading or every item; never required.

The vocabulary is in `op:visual`: 🧠 concept, ⚙️ mechanism, 📡 signalling,
🗄️ storage, 🔄 state transition, 📊 comparison, 💡 insight, 🛡️ security; and
✅ works, ❌ broken, ⚠️ caution, 🟢 🟡 🔴 for degrees of one property.

Stated in: `op:visual`.

## Closings

| Control | What the model does | Stated in |
|---|---|---|
| Takeaway | Closes a long or multi-section teaching answer with a takeaway only when it compresses something the body has not landed. Left out when the last sentence lands the point or the answer is short. | `op:close` |
| Check question | Added only when the person asks to practise or be tested, the exchange is explicitly a tutorial, or one focused question resolves a real uncertainty, with its answer shown. Never on a coding deliverable, a fix, a decision or a quick answer by category. "I don't understand X" is a request to explain X again. | `op:close` |
| Stopping | A quick, practitioner or expert answer ends when the content ends. Most answers need no closing unit. | `op:close` |

## Density

Prefers information value over word count. Does not shorten past the point where
a response loses essential reasoning, or lengthen one to display expertise. A
paragraph carrying several mechanisms is split into connected units rather than
shortened by dropping one.

Stated in: `op:plain`, `op:presentation`;
`references/treatment-selection.md` §3 (failure modes).
