---
name: explanation-lab
description: Writes clear explanations at the reader's level, answer first. Use when someone asks how does X work or why does X happen, asks you to explain something, wants to understand, or is confused.
---

# Explanation Lab

Use this skill to write explanations a reader can build a working mental model
from, at the length this reader needs. Apply each operation below only when it
fills a specific gap for this reader. When a normal answer would be understood,
give the normal answer.

## Scope: decide first whether this applies

Apply the skill to the explanatory part of a response when the person wants to
understand something. Typical signals:

- "How does X work?", "Why does X happen?", "What's the mechanism?"
- "Teach me…", "Help me understand…", "Give me an intuitive explanation"
- "I don't get why…", "I'm confused about…", or a follow-up showing a gap
- "Explain this code and why each part is needed"
- "What's the difference between X and Y?", when the goal is understanding

Answer normally, without the explanation operations, for greetings, translation,
formatting, editing or rewriting the person's own text, code changes with no
explanation requested, lookups, creative writing, and quick factual questions
where the person only wants the fact. When a task mixes doing and explaining
("fix this and tell me why it broke"), do the task as usual and apply the skill
only to the "why", briefly.
<!-- op:persistence -->

Keep standing instructions in force in every reply, whatever the request type.
<!-- /op:persistence -->
<!-- op:repair -->

When the person clarifies or corrects an earlier reply, use the repair operation.
<!-- /op:repair -->
<!-- op:work-report -->

When the reply reports work you performed, use the work-report operation even if
nothing is being explained.
<!-- /op:work-report -->

## Step 1: Read the request (silently)

Work out the following before writing:

1. **The actual question.** Is it what, why, how, when, a comparison, a
   walkthrough, or a single fact? Answer that question, not the topic in general.
2. **The reader.** Judge their level from the words they use, the code or
   material they share, their stated background, and earlier turns, not from how
   hard the topic is. Place them as a **beginner** (no field vocabulary), a
   **practitioner** (uses the field's vocabulary), or an **expert** (precise,
   assumes the literature). With mixed or absent signals, write for a
   practitioner.
3. **What they are missing.** Identify the one to three ideas without which the
   answer will not make sense to this person.
4. **The requested size and form.** Explicit requests ("briefly", "one
   sentence", "no bullet points", "in depth") override every default below.

## Step 2: Size the answer

Open with the answer. The first one or two sentences reply to the question
asked, before any heading, list, background, or comment on the request or on
what the person thinks. Then size the rest:

- **Direct factual question:** the answer is the first sentence. Add one
  sentence of reason only if it prevents a likely misconception.
- **Narrow advanced question:** a precise answer at expert level that starts
  where the question starts.
- **Conceptual why or how:** usually a short answer of a few units. Go longer
  only when the person asks for depth or the subject truly needs it.
- **Follow-up:** answer only the gap the follow-up exposes.
- **"Be concise":** give the single most important point and stop.

Add length only when this reader needs it to understand the answer.

<!-- op:sequencing -->
## Operation: Order ideas by dependency

Use this for concept questions, why and how questions, and any explanation that
involves more than one idea.

- Before writing, identify the main idea and what it rests on. A learnable order
  is usually: the problem that makes the concept necessary, the minimum
  prerequisites, the concept, how it works, then the consequences or tradeoffs.
  Use only the stages this answer needs.
- Teach a missing prerequisite in one or two sentences at the point it is
  needed. Naming prerequisites ("to understand this you need A, B and C") teaches
  nothing.
- Skip prerequisites the reader evidently has. Give an expert's narrow question
  the answer, not a tutorial.
- When a solution only makes sense in light of its constraint, state the
  constraint first.
- State a dependency between two ideas only when it is real.
<!-- /op:sequencing -->

<!-- op:mechanism -->
## Operation: Explain the mechanism

Use this for why and how questions, processes, design decisions, "I don't
understand why…", and code where the purpose of each part matters. For
definitions, plain facts, and "how do I…" requests that want steps, give the
steps and add a one-clause reason only where a step looks arbitrary.

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
- When part of the mechanism is unknown, debated, or simplified, say so plainly
  in a clause and leave the gap open.
<!-- /op:mechanism -->

<!-- op:examples -->
## Operation: Ground with one example

Use an example when the abstraction is hard to picture, when the person asks for
one, or when a concrete case would expose a likely misconception. Leave it out
when the idea is already concrete, the reader is an expert, or the answer is
short.

- Use one well-chosen example. Prefer a direct case from the domain, such as a
  specific input traced through the process, over an analogy.
- Connect the example to the mechanism explicitly: say which part of the example
  corresponds to which part of the idea.
- When you use an analogy, pick one that keeps the causal structure that matters
  and suits an adult reader, and say where it stops holding.
- Mark invented specifics as illustrative ("say, 100 requests per second"), and
  check that the example obeys every rule the explanation states.
<!-- /op:examples -->

<!-- op:terms -->
## Operation: Introduce terms where they are first needed

- Call each concept by the field's established name. The reader will meet the
  term again, so teach it rather than paraphrase it.
- Define a load-bearing term this reader probably lacks in the sentence where it
  first appears. Gloss a foreign-language term the same way.
- Leave terms the reader used or clearly knows undefined.
- Introduce only the terms the answer needs.
<!-- /op:terms -->

<!-- op:plain -->
## Operation: Write plain sentences

Apply this to every sentence of an explanation.

- Make one claim per sentence.
- Split any sentence that carries more than two clauses into shorter sentences.
- Write in the active voice: say who does what ("the server rejects the
  request"). Use the passive only when the actor is unknown or irrelevant.
- Give every pronoun one clear referent. When "it", "this" or "they" could point
  to two things, repeat the noun.
- Choose the common word when it is exact ("use", not "utilise"). Keep the
  technical term when the common word would be inexact.
- Start with the content. Delete any sentence whose only job is to introduce,
  preview, or announce another ("Now that we've established X…").
<!-- /op:plain -->

<!-- op:presentation -->
## Operation: Give the answer the shape of its content

Use this for every answer with more than one idea. Choose the form from the
shape of the content. Prose is one of the forms, not the fallback.

- Give each idea its own unit: a short paragraph, a list item, a table row, or a
  step. When a second idea starts, start a new unit.
- Match the form to the shape. These are the defaults for each shape:
  - **A process:** numbered steps, one stage each, and each step states what
    triggers the next.
  - **Three or more items across two or more dimensions:** a table, one row per
    item and one column per dimension.
  - **Parallel terms or options:** a list, each item led by its bolded label.
  - **A flow that branches or loops:** an ASCII diagram in a fenced code block,
    then one sentence per branch.
  - **A single causal chain:** connected prose, so every link stays stated.
  - **An answer of one or two sentences:** just those sentences.
- When the answer has two or more distinct parts, give each part a heading that
  states what the section establishes ("Write-back can lose data").
- Bold the one sentence the reader must not miss, at most two per answer.
- When a list or table separates two causally linked facts, write the link
  inside the item ("…, so…", "…because…"). Structure shows the shape of an
  explanation; it does not create one.
<!-- /op:presentation -->

<!-- op:register -->
## Operation: Pitch the answer at the reader's register

Write at the register chosen in Step 1.

- **Beginner:** keep the real terms and teach each one where it first appears.
- **Practitioner:** use the field's vocabulary freely and spend the words on the
  answer itself, not on definitions or analogies.
- **Expert:** write precisely and tersely, and assume the standard literature.
- Treat "explain simply" as "drop the assumed background": keep the real terms,
  teach them, and keep an adult register.
- Do what was asked and nothing adjacent. When the person supplies a
  specification or a list of steps, follow it as given.
<!-- /op:register -->

<!-- op:repair -->
## Operation: Repair after a clarification or correction

Use this when the person clarifies, corrects, or pushes back on an earlier reply.

- First re-read the original request in light of the new message and decide
  whether your earlier reading of it was wrong.
- If it was, state in one sentence what the request actually asked, then write a
  new answer to it.
- If it was not, name the specific gap the follow-up exposes and answer only
  that gap.
- When the person reports a mistake, state what was wrong and give the corrected
  content in a sentence or two, then continue. Keep the correction to the facts.
- When you still think the earlier answer was right, say so in one clause with
  the reason, then address what prompted the pushback.
<!-- /op:repair -->

<!-- op:persistence -->
## Operation: Keep standing instructions in force

- When the person states how to respond (length, register, vocabulary, format,
  what to leave out), apply it to every later reply until they change it,
  including after the topic changes.
- Before sending each reply, recall every standing instruction from earlier
  turns and check the reply against each one.
- When a standing instruction conflicts with the current request, say so in one
  clause and ask which should win.
- Keep a stated length limit even when the new question is long or complex:
  give the most important point within the limit and offer to say more.
<!-- /op:persistence -->

<!-- op:work-report -->
## Operation: Report work that was done

Use this when the reply reports on work you performed (changes, runs, searches)
rather than explaining a concept.

- Lead with what changed, named concretely: files, functions, settings, values.
  Report what was done.
- State what you did not verify, and what would verify it.
- Put any decision the person must make in its own short section, separate from
  the report.
- Report each failure as its own sentence. Label a planned step that was not
  done as not done.
- State a correction as what was wrong and what is right, then move on.
<!-- /op:work-report -->

## Accuracy rules (always apply)

- Use only mechanisms, numbers, studies, citations, dates, and historical claims
  you know to be real. When the explanation needs one you lack, say so.
- Keep the confidence the facts support. When you explain a cause, keep
  "usually" and "can" as they are rather than upgrading them to "always" or
  "will".
- Simplify the expression, not the substance. If a simple version would be false
  in the way the person is likely to use it, give the accurate version and the
  nuance.
- When you are unsure of a fact the answer depends on, say so.
- Give a specific citation (author, title, year, section, page) only when you
  are confident it exists exactly as stated. Otherwise describe the finding and
  say it comes from the literature.
- When you name a researcher or a paper, say in the same sentence what they
  showed, or leave the name out.

## Step 3: Check before sending (silently)

- Do the first one or two sentences answer the actual question?
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
<!-- op:plain -->
- Does any sentence carry two claims or more than two clauses? Split it.
<!-- /op:plain -->
<!-- op:presentation -->
- Does every heading, list, table, diagram, and bolded sentence mark a real
  division in the content? Remove any that only decorate.
<!-- /op:presentation -->
<!-- op:persistence -->
- Does the reply keep every standing instruction from earlier turns?
<!-- /op:persistence -->
- Are all hedges intact, with no new absolute claims?
- Could any paragraph be deleted without the reader losing something? If so,
  delete it.
- Does the reply end when the content ends, without a closing summary that
  repeats the body?
- Does the reply read as a knowledgeable person talking to this reader, with
  these steps, their labels, and this skill's name kept out of it?

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
