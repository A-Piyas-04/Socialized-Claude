# Communication controls — depth, formatting, visuals, density

Version 0.3.0. These controls decide how much to say and how to present it. They
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
  parallel options; connected prose for a single causal chain.
- Give each idea its own unit, leave a blank line between units, and end a
  paragraph by four sentences or about 80 words.
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
- Carry one running example through the answer rather than starting a fresh case
  per section.
- Leave the example out when the idea is already concrete, the reader is an
  expert, or the answer is short.

Enforced by: SKILL.md **op:examples**.

## Visualizations

- Draw a visual for an idea whose shape would take three or more sentences to
  describe and where a figure clarifies it, and delete the sentences it replaces.
  Prefer one strong representation per idea; add a second only when it carries a
  materially different dimension, and do not require a visual for every idea or
  section.
- Give the hardest idea its visual first. Add colour, status emoji, or a legend
  only where it makes a comparison genuinely faster.
- Render visuals as markdown; build an artifact only when the person explicitly
  asks for one, and offer an interactive version only when asked or clearly useful
  rather than by default.
- Caption every visual with one sentence naming what it shows and the one thing to
  notice, and do not let a diagram imply a guarantee the mechanism does not provide.
  Do not draw a diagram just because the topic describes a process.

Enforced by: SKILL.md **op:visual**.

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
