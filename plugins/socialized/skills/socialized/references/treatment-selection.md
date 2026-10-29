# Choosing and balancing operations

What to do when two rules in `SKILL.md` point different ways, how to spend a
limited length budget, and the failure modes those rules exist to prevent.

`SKILL.md` already says when each operation applies. This file does not repeat
that; read it when operations collide, when an answer has to be shortened, or
when a draft feels wrong and you want the name of what is wrong with it.

## Contents

1. Resolving conflicts
2. The length budget
3. Failure modes to avoid

## 1. Resolving conflicts

- **Directness beats strict ordering for specific questions.** If the user asked
  a specific question, answer it first. Then supply the one prerequisite that
  makes the answer make sense. The answer comes before any background.
- **The user's stated length beats everything.** "Briefly" means keep the single
  most important point and drop the rest.
- **Expertise beats scaffolding.** For a reader who evidently knows the field,
  skip background and give the precise answer at their level. Scaffolding that
  helps a newcomer slows an expert down.
- **Accuracy beats simplicity.** If the simple version would be wrong in a way
  that matters, give the accurate version with a short nuance.
- **The content's shape beats every presentation habit.** No form is owed an
  appearance. A heading, table, figure, icon, example or takeaway earns its place
  by doing something the prose cannot, or it does not go in.
- **An example beats an analogy** when both would work. A direct case from the
  domain cannot mislead about the domain the way an analogy can.

## 2. The length budget

When something has to go, keep content in this order of priority, from highest
to lowest:

- The direct answer to the question asked.
- A caveat without which the answer would mislead.
- A missing prerequisite this reader needs.
- A missing causal step.
- The tradeoff or limit that follows from the mechanism.
- The form that shows the content's shape (steps, table rows, headings).
- An example, kept when it is what makes a general claim concrete.
- Visuals that replaced prose. When one must go, cut the visual on the easiest
  idea and keep the one on the hardest.
- The takeaway sentence. Cut the check question before the takeaway.
- A figure, example, walkthrough or recap that repeats what another part already
  shows. Cut it first.

Cut from the bottom. An answer that has to be scrolled should earn every
paragraph.
Presentation costs few words, so it is cut last, not first: when shortening,
drop sentences and keep the steps, rows, and headings that show the shape.

## 3. Failure modes to avoid

Each of these was observed in a rewriting experiment or in a real answer. They
are named here because a named failure is easier to catch in a draft than a rule
is to recall.

### Explanation that does not explain

- **Naming prerequisites instead of teaching them.** "To understand this, we
  first rely on the client-server model, packets, and reliable delivery" lists
  three ideas and teaches none of them.
- **Signposting.** "Now that these foundations are in place…", "With the
  structure established, we can examine…". These add length and no
  understanding. Let the order speak for itself.
- **Inventing dependencies.** Saying two ideas are "mutually dependent", or that
  one is "defined by" another, when they are not.
- **Causal padding.** Putting "because" or "as a result" in every sentence, or
  expanding steps the reader already understands. In one experiment this added
  about 40% to typical length, with no measured gain in understanding.
- **Unsupported elaboration.** Mechanism details that sound right but go beyond
  what is established, or meta-commentary about what "the source" does not say.
- **An abstract argument left abstract.** "This adds operational complexity",
  "this introduces consistency risk", "this is expensive at scale" — asserted as
  a property, never shown happening to anything. Trace one case through it.
- **Examples that read as facts.** Specific numbers, addresses, or company
  behaviour invented to make an example concrete, without marking them as
  illustrative.
- **Examples that break the mechanism.** An example whose details contradict the
  rule being explained. Check the example against every rule you state.

### Accuracy lost while expanding

- **Certainty creep.** Adding a cause and, along the way, turning "can lose data"
  into "will lose data" or adding "never" and "guaranteed".
- **Dropped hedges.** Expanding an explanation and losing the "usually", "can",
  or "in most cases" that made it true.
- **One system taught as the rule.** One product's internals (a database's log
  format, a broker's acknowledgement mode) presented as how the whole category
  works. Teach the general mechanism, then label that system's version.
- **Qualifiers on every sentence.** The same assumption or setting restated as a
  clause in each sentence, until the mechanism is hard to follow. State it once,
  where it first matters.

### Structure that serves the format, not the reader

- **A wall of text.** A paragraph carrying two independently important ideas, or
  blurring cause, mechanism and consequence — often in the back half, after a
  well-spaced first screen.
- **Whitespace padding.** The opposite failure: every sentence its own paragraph
  when the sentences form one continuous argument. A unit break marks an idea
  break, not a line break.
- **Decorative structure.** Headings over one-sentence sections, bullets that
  chop one continuous argument into fragments, a table with one meaningful
  column, or bolding so frequent that nothing stands out.
- **Empty transitional units.** A paragraph or heading whose only content is
  announcing what comes next.
- **A congested table.** An argument in a cell (a condition, a second reason, an
  exception), or a header that names nothing. A short sentence in a cell is fine.
  Keep the verdict in the cell and move the reasoning to a list under the table.
- **A bold line for a heading.** A bold phrase on its own line that announces a
  section. Use `##` or `###`.
- **A specimen left inline.** Sample data, a snippet, or an output folded into a
  sentence. Lift it into a fenced block.
- **Depth with no layer.** Specialist detail interleaved with the core thread, so
  core, supporting and optional claims share one paragraph.
- **Identifiers at body weight.** A path, flag, or product name in plain text
  mid-sentence. Put it in backticks.

### Visuals that do not pay for themselves

- **The same mechanism told twice.** A figure that restates a shape the prose
  already made obvious; the sentences the figure replaced left in place; numbered
  steps that walk its arrows; a second figure, an example or a recap showing the
  same transitions again. A second figure stays when it shows something the first
  cannot, and a walkthrough when this reader needs the steps in words.
- **An elaborate figure that is wrong.** A transition with the wrong trigger
  (a read drawn where only a write causes it), or an arrow the mechanism does not
  have. A smaller figure that is right teaches more.
- **An uncaptioned figure.** A diagram, table, or bar block with nothing saying
  what it shows and what to notice.
- **A figure whose parts all look alike.** Identical boxes with nothing marking
  the key node, the peers, or a different kind of thing.
- **Structure without time.** A box-and-arrow map of a process whose point is
  order or waiting. Use a `sequenceDiagram`.
- **Decoration mistaken for navigation.** An icon on every heading or every
  bullet, the same icon on different kinds of part, one coloured element so
  nothing else is encoded, an emoji inside code, JSON or a formal document, or a
  status marker standing alone in its list.
- **An unrequested artifact.** An HTML, SVG, or interactive file when the person
  did not explicitly ask for an artifact, an SVG, or something to click.
  "Explain this visually" is a request for the markdown form.

### Endings nobody asked for

- **A quiz on a quick answer.** A check question after a fact, a lookup, or an
  expert reply. Those end when the content ends.
- **A question nobody can check.** An open prompt with no options and no answer.
- **A recap instead of a compression.** A closing paragraph that restates the
  body.
- **Over-expansion.** Every operation applied to every answer. The goal is an
  answer that is easier to understand, not one that is longer.
