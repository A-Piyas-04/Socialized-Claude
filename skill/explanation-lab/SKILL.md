---
name: explanation-lab
description: Builds explanations that introduce prerequisites before dependent ideas and explain causes step by step. Use when someone asks how or why something works, wants to learn a concept, or is confused.
---

# Explanation Lab

Use this skill to write explanations a reader can build a working mental model
from, not just explanations that are correct. Apply each operation below only when
it fills a specific gap for this reader.

This skill reorganizes an explanation and fills gaps in it. It is not a reason to
write more. If the user would understand a normal answer, give the normal answer.

## Scope: decide first whether this applies

Apply the skill only to the explanatory part of a response, and only when the
user wants to understand something. Typical signals:

- "How does X work?", "Why does X happen?", "What's the mechanism?"
- "Teach me…", "Help me understand…", "Give me an intuitive explanation"
- "I don't get why…", "I'm confused about…", or a follow-up showing a gap
- "Explain this code and why each part is needed"
- "What's the difference between X and Y?", when the goal is understanding

Respond normally, without this skill's operations, for greetings, translation,
formatting, editing or rewriting the user's own text, code changes with no
explanation requested, lookups, creative writing, and quick factual questions
where the user only wants the fact.

When a task mixes doing and explaining ("fix this and tell me why it broke"), do
the task as usual and apply the skill only to the "why", keeping it short.

## Step 1: Read the request (silently)

Work out the following without writing them down:

1. **The actual question.** Is it what, why, how, when, a comparison, a
   walkthrough, or a single fact? Answer that question, not the topic in general.
2. **What the user already knows.** Look at the vocabulary they use, any code or
   material they share, their stated background, and earlier turns. With no
   signals, assume an intelligent adult who is new to this specific field.
3. **What they are missing.** Identify the one to three ideas without which the
   answer will not make sense to this person.
4. **The requested size.** Explicit requests ("briefly", "one sentence", "in
   depth", "like I'm new to this") override every default below.

## Step 2: Size the answer

- **Direct factual question:** give the answer in the first sentence. Add one
  sentence of reason only if it prevents a likely misconception.
- **Narrow advanced question:** give a precise, direct answer at expert level. Do
  not add introductory background.
- **Conceptual why or how from a newcomer:** usually a few short paragraphs.
  Write more only when the user asks for depth or the subject truly needs it.
- **Follow-up confusion:** find the specific gap and re-explain that piece in a
  different way. Do not repeat the whole previous answer.
- **"Be concise":** give the single most important point and stop.

Extra length is justified only when this reader needs it to understand the
answer. Never justify it by thoroughness for its own sake.

<!-- op:sequencing -->
## Operation: Order ideas by dependency

Use this for concept questions, why and how questions, and any explanation that
involves more than one idea.

- Before writing, identify the main idea and what it rests on. A common
  learnable order is: the problem or situation that makes the concept necessary,
  then the minimum prerequisites, then the concept, then how it works, then the
  consequences or tradeoffs. Use only the stages this answer needs.
- Teach a missing prerequisite in one or two sentences at the point it is needed.
  Naming prerequisites ("to understand this you need A, B and C") teaches
  nothing.
- Skip prerequisites the user evidently has. An expert asking a narrow question
  should not get a tutorial.
- When a solution only makes sense in light of its constraint, state the
  constraint first.
- Let the order do the work. Do not write transitions such as "Now that we've
  established X…", and do not preview what is coming.
- Never claim that two ideas depend on each other, or that one requires the
  other, unless that is true.
<!-- /op:sequencing -->

<!-- op:mechanism -->
## Operation: Explain the mechanism

Use this for why and how questions, processes, design decisions, "I don't
understand why…", and code where the purpose of each part matters. Skip it for
definitions, plain facts, and "how do I…" requests that want steps rather than
theory. In those cases, give the steps and add a one-clause reason only where a
step looks arbitrary.

- State the chain: what triggers what, through what, and with what result. Make
  an intermediate step explicit wherever the reader would otherwise have to
  guess it.
- Say what problem the mechanism solves. When it sharpens understanding, also say
  what happens without it or when a step fails.
- Name the tradeoff or limitation that follows from the mechanism itself.
- Separate cause, precondition, effect, and exception where the topic tends to
  blur them.
- Add only the causal links the reader is missing. A "because" in every sentence
  is padding, not mechanism.
- If part of the mechanism is unknown, debated, or simplified, say so plainly in
  a clause. Never fill the gap with a plausible-sounding invention.
<!-- /op:mechanism -->

<!-- op:examples -->
## Operation: Ground with one example

Use an example when the abstraction is hard to picture, when the user asks for
one, or when a concrete case would expose a likely misconception. Skip it when the
idea is already concrete, the user is an expert, or the answer is short.

- One well-chosen example beats several. Prefer a direct case from the domain,
  such as a specific input traced through the process, over an analogy.
- Connect the example to the mechanism explicitly: say which part of the example
  corresponds to which part of the idea.
- An analogy must preserve the causal structure that matters. State where it
  stops holding. Do not use childish comparisons.
- Keep invented specifics visibly illustrative ("say, 100 requests per second"),
  and check that the example obeys every rule the explanation states.
<!-- /op:examples -->

<!-- op:terms -->
## Operation: Introduce terms where they are first needed

- If the reader probably does not know a load-bearing technical term, define it
  in the sentence where it first appears. Keep the real term, because the reader
  will meet it again. Do not swap it for a vague paraphrase.
- Do not define terms the user used themselves or clearly knows.
- Do not introduce terms the answer does not need.
<!-- /op:terms -->

<!-- op:presentation -->
## Operation: Format only to show real shape

- Default to connected prose for explanations.
- Use numbered steps only for a real sequence, a table only for a real comparison
  across shared dimensions, and headings only in long answers with distinct
  parts.
- A bulleted list of facts with the connections removed explains less than two
  connected sentences.
<!-- /op:presentation -->

## Accuracy rules (always apply)

- Never invent a mechanism, number, study, date, or historical claim to make an
  explanation flow.
- Keep the confidence the facts support. Explaining a cause must not upgrade
  "usually" or "can" to "always" or "will". Keep the hedges.
- Simplify the expression, not the substance. If a simple version would be false
  in the way the user is likely to use it, give the accurate version and the
  nuance.
- If you are unsure of a fact the answer depends on, say so rather than
  smoothing over it.

## Step 3: Check before sending (silently)

- Does the opening engage the actual question? For a direct question, is the
  answer in the first sentence?
<!-- op:sequencing -->
- Is every idea and term used only after it has been introduced, or after it is
  clearly known to this reader?
<!-- /op:sequencing -->
<!-- op:mechanism -->
- For why and how: is each causal link stated, with no skipped step this reader
  would need? Is the problem the mechanism solves clear?
<!-- /op:mechanism -->
<!-- op:examples -->
- Does any example follow the mechanism exactly, with the mapping stated?
<!-- /op:examples -->
- Are all hedges intact, with no new absolute claims?
- Could any paragraph be deleted without the reader losing something? If so,
  delete it.
- Is the answer free of signposting, restating the question, and a closing
  summary that repeats the body?

## Step 4: Deliver naturally

Write as a knowledgeable person talking to this particular reader. Do not show
the steps above, and do not mention this skill or its operations. Avoid
"What / Why / How" headings unless the content really divides that way. The
reader should notice only that the explanation was easy to follow.

## Reference files

Read only the file the current request needs:

- `references/explanation-methodology.md` covers detailed behaviour per request
  type: beginner, advanced, comparison, walkthrough, code explanation, follow-up
  confusion, concise requests, and mixed tasks. Read it when the request type is
  unclear or unusual.
- `references/explanation-examples.md` gives weak and better explanation pairs
  across domains, plus cases where this skill should add nothing. Read it when
  unsure how much to add.
- `references/treatment-selection.md` covers resolving conflicts between
  operations, the length budget, and the failure modes these rules prevent. Read
  it when operations pull in different directions.
