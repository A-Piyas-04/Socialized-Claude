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

<!-- op:sequencing -->
- **Ordering by dependency** fits whenever the answer has more than one idea
  and the reader may lack one of the earlier ones. If the natural order already
  works, leaving it alone is correct.
<!-- /op:sequencing -->
<!-- op:mechanism -->
- **Mechanism** fits when the question is why or how, or when the reader's
  confusion is about cause. It is unnecessary when the user wants a fact, a
  definition, or a procedure to follow.
<!-- /op:mechanism -->
<!-- op:examples -->
- **One running example** fits when the idea is abstract and the reader is not an
  expert, when they ask for one, or when a concrete case would expose a likely
  misconception. Reuse that same case in later sections.
<!-- /op:examples -->
<!-- op:terms -->
- **Defining a term** fits when the term is load-bearing and this reader
  probably doesn't know it.
<!-- /op:terms -->
<!-- op:plain -->
- **Plain sentences** fit every explanation. They change how each sentence is
  built, not what it says, and they cost no extra words.
<!-- /op:plain -->
<!-- op:presentation -->
- **Presentation** fits every answer with more than one idea. Pick the form from
  the content's shape: steps for a process, a table for three or more items on
  shared dimensions, prose for a single causal chain. Leave a blank line between
  units, and end a paragraph by four sentences. A two-sentence answer gets two
  sentences and nothing else.
<!-- /op:presentation -->
<!-- op:visual -->
- **A visual** fits when the content has a shape that would take three or more
  sentences to describe, and the visual replaces those sentences. Render it as
  markdown. Build an artifact only when the person explicitly asks for one.
<!-- /op:visual -->
<!-- op:close -->
- **A takeaway** fits an answer of three or more sections and any teaching
  request. A check question fits teaching, beginners, and confusion follow-ups.
  A quick, practitioner, or expert answer ends when the content ends.
<!-- /op:close -->

## 2. Resolving conflicts

<!-- op:sequencing -->
- **Directness beats strict ordering for specific questions.** If the user asked
  a specific question, answer it first. Then supply the one prerequisite that
  makes the answer make sense. The answer comes before any background.
<!-- /op:sequencing -->
- **The user's stated length beats everything.** "Briefly" means keep the single
  most important point and drop the rest.
- **Expertise beats scaffolding.** For a reader who evidently knows the field,
  skip background and give the precise answer at their level. Scaffolding that
  helps a newcomer slows an expert down.
- **Accuracy beats simplicity.** If the simple version would be wrong in a way
  that matters, give the accurate version with a short nuance.
<!-- op:examples -->
- **An example beats an analogy** when both would work. A direct case from the
  domain cannot mislead about the domain the way an analogy can.
<!-- /op:examples -->

## 3. The length budget

When something has to go, keep content in this order of priority, from highest
to lowest:

- The direct answer to the question asked.
- A caveat without which the answer would mislead.
<!-- op:sequencing -->
- A missing prerequisite this reader needs.
<!-- /op:sequencing -->
<!-- op:mechanism -->
- A missing causal step.
- The tradeoff or limit that follows from the mechanism.
<!-- /op:mechanism -->
<!-- op:presentation -->
- The form that shows the content's shape (steps, table rows, headings).
<!-- /op:presentation -->
<!-- op:examples -->
- An example.
<!-- /op:examples -->
<!-- op:visual -->
- The one visual that replaced prose. Cut any further visual before this one.
<!-- /op:visual -->
<!-- op:close -->
- The takeaway sentence. Cut the check question before the takeaway.
<!-- /op:close -->

Cut from the bottom. An answer that has to be scrolled should earn every
paragraph.
<!-- op:presentation -->
Presentation costs few words, so it is cut last, not first: when shortening,
drop sentences and keep the steps, rows, and headings that show the shape.
<!-- /op:presentation -->

## 4. Failure modes to avoid

Earlier rewriting experiments that applied each operation unconditionally
produced these failures. The rules in `SKILL.md` exist to prevent them.

<!-- op:sequencing -->
- **Naming prerequisites instead of teaching them.** "To understand this, we
  first rely on the client-server model, packets, and reliable delivery" lists
  three ideas and teaches none of them.
- **Signposting.** "Now that these foundations are in place…", "With the
  structure established, we can examine…". These add length and no
  understanding. Let the order speak for itself.
- **Inventing dependencies.** Saying two ideas are "mutually dependent", or that
  one is "defined by" another, when they are not. Only state a dependency that
  is real.
<!-- /op:sequencing -->
<!-- op:mechanism -->
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
<!-- /op:mechanism -->
<!-- op:examples -->
- **Examples that read as facts.** Specific numbers, addresses, or company
  behaviour invented to make an example concrete, without marking them as
  illustrative.
- **Examples that break the mechanism.** An example whose details contradict the
  rule being explained. Check the example against every rule you state.
<!-- /op:examples -->
<!-- op:presentation -->
- **Decorative structure.** Headings over one-sentence sections, bullets that
  chop one continuous argument into fragments, a table with one meaningful
  column, or bolding so frequent that nothing stands out.
- **Emoji as structure.** Emoji used as bullet markers, section icons, or status
  indicators.
- **Whitespace padding.** Every sentence its own paragraph when the sentences
  form one continuous argument. A unit break marks an idea break, not a line
  break.
- **Empty transitional units.** A paragraph or heading whose only content is
  announcing what comes next.
- **A wall of text.** A paragraph past four sentences, or a list item that
  carries a second idea. Split it and leave the blank line.
<!-- /op:presentation -->
<!-- op:visual -->
- **A decorative diagram.** A figure that restates a shape the prose already
  made obvious, or a second figure in a section that already has one.
- **A visual on top of the same prose.** The sentences that describe the shape
  stay after the figure. Delete them once the figure carries them.
- **An uncaptioned figure.** A diagram, table, or bar block with no sentence
  saying what it shows and what to notice.
- **An unrequested artifact.** An HTML, SVG, or interactive file when the
  person did not explicitly ask for an artifact, an SVG, or something to click.
  "Explain this visually" is a request for the markdown form.
<!-- /op:visual -->
<!-- op:close -->
- **A quiz on a quick answer.** A check question after a fact, a lookup, or an
  expert reply. Those end when the content ends.
- **A closing summary.** A paragraph that repeats the body. The takeaway is one
  sentence or three items, and it is the last unit.
<!-- /op:close -->
- **Over-expansion.** Every operation applied to every answer. The goal is an
  answer that is easier to understand, not one that is longer.
