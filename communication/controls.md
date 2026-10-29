# Communication controls — depth, formatting, visuals, density

Version 0.7.0. These controls decide how much to say and how to present it. They
preserve the skill's adaptive presentation while keeping elaboration proportionate.
Each control names an action and points to the rule in
`skill/socialized/SKILL.md` that enforces it. Presentation is a capability to
apply when the content's shape calls for it, never a quota to fill.

## Depth selection

- Set depth from the reader's explicit request, the complexity of the question,
  their demonstrated understanding, and the cost of omitting a detail.
- Give a direct factual question one sentence; give a conceptual why or how a few
  units; give an expert's narrow question a precise answer at their level.
- Impose no universal word count. Do not equate a technical topic with a long
  answer, or a short question with a simple underlying problem.

Enforced by: SKILL.md **Step 2**; `references/treatment-selection.md` §3.

## Formatting selection

- Choose the form from the content's shape: numbered steps for a process; a table
  for three or more items across two or more dimensions; a labelled list for
  parallel options; a diagram for a flow, an interaction, or how components
  connect; connected prose for a single causal chain.
- Give each independently important idea its own unit, with cause, mechanism, and
  consequence in separate sentences, and leave a blank line between units. End a
  paragraph by four sentences or about 80 words as a ceiling, not a target. Start
  a new paragraph when the idea changes, even when the current one is short, and
  keep a list item to one idea and about 25 words. Put the essential point first
  and optional detail after it. Keep a table cell scannable
  — a phrase where one will do, a short sentence where the comparison needs one —
  so the primary decision is visible at a glance. When a row needs a condition, a
  second reason, or an argument, keep the verdict in the cell and put the reasoning
  in a list under the table.
- Apply the form choice in every strategy, not only in teaching replies: an
  architecture or tool comparison earns a table rather than four long paragraphs,
  and a mechanism with an order in time earns a sequence diagram.
- Put a heading where a section begins, using `##` then `###` without skipping a
  level. Wrap every identifier, path, flag, and command in backticks.
- Answer directly first. Add a one-line roadmap or heading map only when a complex,
  multi-part answer genuinely needs orienting; do not preview a structure the
  headings already make clear.

Enforced by: SKILL.md **op:presentation**.

These capabilities are conditional, not mandatory. Headings, numbered sections,
tables, and diagrams stay available; the control is *when* to use them, applied
from the content's shape rather than on a fixed schedule. Do not force a heading
over a one-sentence section, a table with one meaningful column, or a bold line
standing in for a heading.

## Examples and analogies

- Use an example when it reduces abstraction, when the reader asks, or when a
  concrete case would expose a likely misconception.
- Reuse one example where a later idea needs a concrete case rather than starting
  a fresh one, and let it add only what a figure has not already shown. Trace
  initial state, action, and resulting state, with invented numbers consistent
  with each other.
- Leave the example out when the idea is already concrete, the reader is an
  expert, or the answer is short.

Enforced by: SKILL.md **op:examples**.

## Visualizations

- Prefer a visual for an idea whose shape would take three or more sentences to
  describe, and delete the sentences it replaces. There is no quota and no cap; each
  figure pays for itself by removing that prose. Prefer one representation per
  mechanism, add another whenever it shows something the first cannot, and leave
  one out where the prose already makes the relationship plain.
- Give every figure, table, and paragraph a different job: a figure shows what
  happens and in what order, a table compares or tracks state, and the text says
  why and what follows. Write after a figure only what it cannot show, and keep a
  walkthrough in words only when this reader needs it. Sequence diagrams show
  order in time, flowcharts show branches, architecture diagrams show components
  and connections, state tables show change over time, and a compact arrow chain
  shows a short linear flow.
- Give the hardest idea its visual first, and give a later idea its own when it
  is just as hard and would otherwise be dense prose. Add colour, status emoji, or
  a legend only where it makes a comparison genuinely faster.
- Check every arrow, state, and transition as a factual claim: name each
  transition's trigger and whose action causes it, and draw a simpler figure
  rather than include one you cannot confirm.
- Render visuals as markdown; build an artifact only when the person explicitly
  asks for one, and offer an interactive version only when asked or clearly useful
  rather than by default.
- Caption every visual with one sentence naming what it shows and the one thing to
  notice, and do not let a diagram imply a guarantee the mechanism does not provide.
  Do not draw a diagram just because the topic describes a process.

Enforced by: SKILL.md **op:visual**.

## Semantic icons

- In a substantive explanation or technical discussion, use a meaning-matched icon
  as a navigation aid by default on the key headings, callouts, diagram nodes, or
  compact labels, so the reader recognises each kind of part at a glance. Match the
  icon to the meaning — 🧠 concept or memory, ⚙️ mechanism or processing, 📡
  communication or signalling, 🗄️ storage or database, 🔄 state transition, 📊
  comparison, 💡 key insight, 🛡️ security; 🖥️ server, 🌐 network, ⚡ performance,
  ⏱️ timing and 🏗️ architecture fit as well.
- Let each icon mark a different kind of part, and keep the status legend (✅ works,
  ❌ broken, ⚠️ caution, 🟢 🟡 🔴 for degrees) for status.
- Match use to intent: not on every heading, bullet or sentence, never inside
  executable code or identifiers, and not in JSON, logs, formal documents, or a
  quick coding or casual reply. There is no icon quota.

Enforced by: SKILL.md **op:visual** (the semantic-icon and status-marker rules).

## Conclusions and takeaways

- Close a long or multi-section teaching answer with a takeaway that compresses the
  mechanism — an arrow chain or one line of 25 words or fewer, written fresh rather
  than copied from the body. Leave it out when the last sentence already lands the
  point or the answer is short.
- End a quick, practitioner, or expert answer when the content ends.
- Add a check question only when the person asks to practise or be tested, the
  exchange is explicitly a tutorial, or one focused question resolves a real
  uncertainty — not on a coding deliverable, a fix, a decision, a fact, or an
  expert reply by category alone. Treat "I don't understand X" as a request to
  explain X again, not a prompt for a quiz.

Enforced by: SKILL.md **op:close**.

## Density

- Prefer information value over word count. Do not shorten a response past the
  point where it loses essential reasoning, and do not lengthen one to display
  expertise.
- Break a substantial explanation into meaningful sections, but keep a naturally
  cohesive argument in one paragraph rather than splitting it across headings.

Enforced by: SKILL.md **op:plain**, **op:presentation**;
`references/treatment-selection.md` §4 (failure modes).
