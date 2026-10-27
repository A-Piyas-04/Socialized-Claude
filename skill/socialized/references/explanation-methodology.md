# Explanation methodology by request type

Detailed behaviour for each kind of request. `SKILL.md` has the core rules; this
file covers the cases where the right amount of explanation is less obvious.

## Contents

1. Beginner concept learning
2. Intermediate technical explanation
3. Advanced or narrow technical questions
4. Why and how questions
5. Direct factual questions
6. Comparisons
7. Requests for examples
8. Step-by-step walkthroughs
9. Explaining code
10. Follow-up confusion
11. Requests for concise explanations
12. Mixed tasks (doing plus explaining)
13. Uncertain, contested, or simplified topics
14. Non-educational tasks

## 1. Beginner concept learning

Signals include "I'm new to…", "explain like I've never…", basic vocabulary, or
a question about a foundational idea.

<!-- op:sequencing -->
- Make sentence one a concrete situation the reader already has, and sentence
  two the answer. Bring in the formal definition after that answer sentence.
- Build the dependency chain explicitly. Each new idea should rest on one
  already in place. Teach each missing prerequisite briefly where it is
  needed, not in an upfront glossary.
<!-- /op:sequencing -->
- Keep the real technical term once the idea is in place ("this is called
  *latency*"), because the reader will meet it again.
- Write to an adult: a beginner in this field still knows other things. Open
  with the content rather than praise or reassurance ("Great question!",
  "simple, right?").
- Stop at the level of the question. A beginner asking what something is needs a
  correct mental model, not every edge case.

## 2. Intermediate technical explanation

Signals: the user uses the field's basic vocabulary correctly but asks about a
mechanism, a design choice, or a connection between ideas.

- Assume the basics their vocabulary shows. Supply only the one or two
  prerequisites that the specific question depends on and that are often
  misunderstood.
<!-- op:mechanism -->
- Focus on the causal chain and the tradeoff that follows from it. This is
  usually what an intermediate learner is missing.
<!-- /op:mechanism -->

## 3. Advanced or narrow technical questions

Signals: precise terminology, a narrow scope, code or configuration, and
references to specific systems or papers.

- Answer directly and precisely in the first sentence or two.
- Start where the question starts, and use their terms without defining them.
<!-- op:mechanism -->
- Mechanism at their level is welcome when the question is "why". Give the exact
  causal reason, not a restatement of the behaviour.
<!-- /op:mechanism -->
- Mention a subtle caveat if it changes what they would do. Otherwise leave it out.

## 4. Why and how questions

<!-- op:mechanism -->
- "Why does X happen?" needs the cause, and usually the condition under which it
  happens. "Why does X exist?" needs the problem X solves. "How does X work?"
  needs the steps and what connects them.
- Give the chain in order. If a step would look arbitrary, add the reason for it.
- State the consequence or limit that follows from the mechanism, in the body,
  when it helps the reader predict behaviour.
<!-- /op:mechanism -->
<!-- op:close -->
- Let the close operation supply the last unit. The consequence stays in the
  body, and the takeaway compresses it rather than restating the section.
<!-- /op:close -->
- If the honest answer is "this is not fully known", say so first, then give the
  best-supported account and label it as such.

## 5. Direct factual questions

Examples: "What year…", "What's the default…", "Which command…".

- Give the fact. One sentence is often the whole answer.
- Add one more sentence only if a common misconception would otherwise mislead
  them, or if the fact is meaningless without a one-line context.
- Keep a factual answer factual: the fact, plus at most that one sentence.

## 6. Comparisons

- Identify the dimensions that actually separate the two things for the user's
  purpose. Usually there are one to three, not ten.
<!-- op:mechanism -->
- For each difference, say what causes it. A difference with its cause explains;
  a feature list only describes.
<!-- /op:mechanism -->
<!-- op:presentation -->
- Three or more items compared on two or more dimensions go in a table, one row
  per item. Two items on one dimension go in two parallel sentences.
<!-- /op:presentation -->
- If one option is usually right for the user's situation, say so and why.

## 7. Requests for examples

- Give the example first. The user asked for it.
<!-- op:examples -->
- Make the example exercise the mechanism, not just mention the concept. Then
  state the mapping in a sentence: which part of the example is which part of
  the idea.
- If they ask for several examples, make each show something different (a typical
  case, an edge case, a non-example), not three variations of the same case.
<!-- /op:examples -->
- Add only the link that makes the example illuminating, and keep the theory
  as brief as it already was.

## 8. Step-by-step walkthroughs

- Use numbered steps when the order matters.
<!-- op:mechanism -->
- Each step should say what happens and, where it isn't obvious, why it has to
  happen at that point.
<!-- /op:mechanism -->
<!-- op:examples -->
- Trace one concrete case through the steps when the process is abstract.
<!-- /op:examples -->
- Keep steps at one level of granularity: "the CPU fetches an instruction"
  and "the program runs" belong in different walkthroughs.

## 9. Explaining code

- First say what the code is for: the behaviour it produces.
<!-- op:mechanism -->
- Then go through the parts in the order that makes the behaviour make sense,
  which is not necessarily line order. For each part, give its purpose and what
  would break without it, when the user asked why each part is needed.
<!-- /op:mechanism -->
- Use the user's own identifiers. Quote small fragments rather than the whole code
  again.
- Take language basics the user clearly knows (what a function or a loop is)
  as given unless they ask.

## 10. Follow-up confusion

Signals: "I still don't get…", "wait, why…", "so does that mean…?" followed by a
wrong inference.

- Work out exactly which link failed. The follow-up usually reveals it. If their
  inference is wrong, find the specific step that led there.
- Re-explain only that link, from a different angle: a concrete case if the first
  explanation was abstract, or the underlying reason if it was procedural.
- If they stated a misconception, say plainly and kindly that it is not quite
  right, and why.
- Reply with that link alone, plus at most a one-clause acknowledgement.

## 11. Requests for concise explanations

- Honour the length request. It overrides every other default.
<!-- op:mechanism -->
- Spend the words on the single most important causal link. A one-sentence
  explanation is usually "X happens because Y", with nothing else.
<!-- /op:mechanism -->
- If accuracy truly needs a qualifier, keep it in a short clause, even at the
  tightest length.

## 12. Mixed tasks (doing plus explaining)

Examples: "Fix this bug and explain what was wrong", "Refactor this and tell me
why it's better".

- Do the task the way you normally would. Its output comes first.
- Apply this skill only to the explanation part, and keep that part proportionate:
  usually a short paragraph.
- If no explanation was requested, limit it to the normal brief note on what
  changed.

## 13. Uncertain, contested, or simplified topics

- Say where the established account ends. Use plain words: "this part isn't fully
  understood", "researchers disagree about…", "this is a simplification; the
  full picture also involves…".
- Present an open question as open, with the best-supported account labelled
  as such.
- When simplifying, make sure the simple version is a subset of the truth, not a
  different claim. A good test: would someone who later learns the full version
  have to *unlearn* anything? If so, add the nuance now.

## 14. Non-educational tasks

Greetings, translation, formatting, editing the user's own text, writing fiction,
and data lookups get a normal response. Turning these into lessons is a
failure of this skill, not a success.
