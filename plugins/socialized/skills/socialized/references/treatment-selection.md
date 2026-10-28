# Choosing and balancing operations

How to decide which operations to use when they pull in different directions,
how to spend a limited length budget, and which failure modes the rules in
`SKILL.md` exist to prevent.

## Contents

1. Selection defaults
2. Resolving conflicts
3. The length budget
4. Failure modes to avoid

## 1. Selection defaults

Start from "use nothing" and add an operation only when you can name the
specific gap it fills for this reader.

- **Ordering by dependency** fits whenever the answer has more than one idea
  and the reader may lack one of the earlier ones. If the natural order already
  works, leaving it alone is correct.
- **Mechanism** fits when the question is why or how, or when the reader's
  confusion is about cause. It is unnecessary when the user wants a fact, a
  definition, or a procedure to follow.
- **One running example** fits when the idea is abstract and the reader is not an
  expert, when they ask for one, or when a concrete case would expose a likely
  misconception. Reuse that same case in later sections.
- **Defining a term** fits when the term is load-bearing and this reader
  probably doesn't know it.
- **Plain sentences** fit every explanation. They change how each sentence is
  built, not what it says, and they cost no extra words.
- **Presentation** fits every answer with more than one idea. Pick the form from
  the content's shape: steps for a process, a table for three or more items on
  shared dimensions, prose for a single causal chain. Leave a blank line between
  units, and end a paragraph by four sentences. A two-sentence answer gets two
  sentences and nothing else.
- **A visual** fits each idea whose content has a shape that would take three or
  more sentences to describe, and it replaces those sentences. There is no cap per
  answer; the cost stays flat because each figure deletes its prose. Keep to one
  representation per idea, and add a second only when it carries a materially
  different dimension. Spend the first one on the hardest idea, and support the
  last third of the answer at least as well as the first. Render it as markdown.
  Build an artifact only when the person explicitly asks for one.
- **A takeaway** fits a long or multi-section teaching answer whose last sentence
  does not already land the point. A check question, with its answer, fits only
  when the person asks to practise or be tested, the exchange is a tutorial, or
  one question resolves a real uncertainty. A quick, practitioner, or expert
  answer ends when the content ends.

## 2. Resolving conflicts

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
- **An example beats an analogy** when both would work. A direct case from the
  domain cannot mislead about the domain the way an analogy can.

## 3. The length budget

When something has to go, keep content in this order of priority, from highest
to lowest:

- The direct answer to the question asked.
- A caveat without which the answer would mislead.
- A missing prerequisite this reader needs.
- A missing causal step.
- The tradeoff or limit that follows from the mechanism.
- The form that shows the content's shape (steps, table rows, headings).
- An example.
- Visuals that replaced prose. When one must go, cut the visual on the easiest
  idea and keep the one on the hardest.
- The takeaway sentence. Cut the check question before the takeaway.

Cut from the bottom. An answer that has to be scrolled should earn every
paragraph.
Presentation costs few words, so it is cut last, not first: when shortening,
drop sentences and keep the steps, rows, and headings that show the shape.

## 4. Failure modes to avoid

Earlier rewriting experiments that applied each operation unconditionally
produced these failures. The rules in `SKILL.md` exist to prevent them.

- **Naming prerequisites instead of teaching them.** "To understand this, we
  first rely on the client-server model, packets, and reliable delivery" lists
  three ideas and teaches none of them.
- **Signposting.** "Now that these foundations are in place…", "With the
  structure established, we can examine…". These add length and no
  understanding. Let the order speak for itself.
- **Inventing dependencies.** Saying two ideas are "mutually dependent", or that
  one is "defined by" another, when they are not. Only state a dependency that
  is real.
- **Certainty creep.** Adding a cause and, along the way, turning "can lose data"
  into "will lose data" or adding "never" and "guaranteed". Keep the original
  strength of every claim.
- **Dropped hedges.** Expanding an explanation and losing the "usually", "can",
  or "in most cases" that made it true.
- **Causal padding.** Putting "because" or "as a result" in every sentence, or
  expanding steps the reader already understands. In one experiment this added
  about 40% to typical length, with no measured gain in understanding.
- **Unsupported elaboration.** Adding mechanism details that sound right but go
  beyond what is actually established, or meta-commentary about what "the
  source" does not say.
- **Examples that read as facts.** Specific numbers, addresses, or company
  behaviour invented to make an example concrete, without marking them as
  illustrative.
- **Examples that break the mechanism.** An example whose details contradict the
  rule being explained. Check the example against every rule you state.
- **Decorative structure.** Headings over one-sentence sections, bullets that
  chop one continuous argument into fragments, a table with one meaningful
  column, or bolding so frequent that nothing stands out.
- **Emoji as structure.** Emoji used as bullet markers or section icons, or a
  status marker that is not from the legend or stands alone in its list.
- **Whitespace padding.** Every sentence its own paragraph when the sentences
  form one continuous argument. A unit break marks an idea break, not a line
  break.
- **Empty transitional units.** A paragraph or heading whose only content is
  announcing what comes next.
- **A wall of text.** A paragraph past four sentences, or a list item that
  carries a second idea. Split it and leave the blank line.
- **Effort that decays.** The first screen gets spacing and figures, and the
  back half reverts to dense paragraphs. Give the last section the treatment of
  the first.
- **A congested table.** Sentences in cells, more than four columns, or a header
  that names nothing. Shorten the cells and move the rest to a list.
- **A bold line for a heading.** A bold phrase on its own line that announces a
  section. Use `##` or `###`.
- **A specimen left inline.** Sample data, a snippet, or an output folded into a
  sentence. Lift it into a titled fenced block.
- **Depth with no layer.** Specialist detail interleaved with the core thread.
  Put it in a **Deeper:** block the reader can skip.
- **Identifiers at body weight.** A path, flag, or product name in plain text
  mid-sentence. Put it in backticks.
- **A decorative diagram.** A figure that restates a shape the prose already
  made obvious, or a second figure in a section that already has one.
- **A visual on top of the same prose.** The sentences that describe the shape
  stay after the figure. Delete them once the figure carries them.
- **An uncaptioned figure.** A diagram, table, or bar block with no sentence
  saying what it shows and what to notice.
- **An unrequested artifact.** An HTML, SVG, or interactive file when the
  person did not explicitly ask for an artifact, an SVG, or something to click.
  "Explain this visually" is a request for the markdown form.
- **One diagram carrying the whole answer.** A single early figure, then prose for
  every later and harder idea. Each idea with a shape gets its own.
- **A figure whose parts all look alike.** Identical boxes with nothing marking
  the key node, the peers, or a different kind of thing.
- **Structure without time.** A box-and-arrow map of a process whose point is
  order or waiting. Use a `sequenceDiagram`.
- **Colour used once.** One coloured element, so nothing else in the answer is
  encoded. Name one code and reuse it in every figure.
- **Quantities left in sentences.** Ratios and ranges stated as numbers when
  their scale is the point. Draw the bars.
- **A quiz on a quick answer.** A check question after a fact, a lookup, or an
  expert reply. Those end when the content ends.
- **A question nobody can check.** An open prompt with no options and no answer.
  Give three options or a short factual answer, then the answer itself.
- **A recap instead of a compression.** A closing paragraph that restates the
  body. The takeaway is an arrow chain or one line of 25 words or fewer.
- **An abandoned example.** A case introduced early that vanishes in the middle
  sections. Carry it into every section that teaches.
- **Motivation given once.** The obvious approach and its failure shown for the
  first mechanism only. Repeat the move for each one.
- **Over-expansion.** Every operation applied to every answer. The goal is an
  answer that is easier to understand, not one that is longer.
