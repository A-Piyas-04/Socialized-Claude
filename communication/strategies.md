# Communication strategies — intent-sensitive guidance

Version 0.8.0. Five strategies for the kind of request, plus how a follow-up is
handled and where the policy stops.

**This file is an index, not a second copy of the policy.** The five strategies
ship in `skill/socialized/SKILL.md` under "Match the communication strategy to
the intent"; the across-turns behaviour ships in **Step 1.5**, `op:repair` and
`op:persistence`. Read the skill for the wording that ships.

This is not a runtime classifier and not a routing pipeline. The model reads the
request and applies the relevant guidance directly, combining strategies where a
request mixes intents. Keeping the five distinct is the point: a universal
template that makes every reply look the same is the failure this file guards
against.

| Strategy | Objective | Leads with | Applies | Avoids |
|---|---|---|---|---|
| **A — Teaching and explanation** | An accurate mental model | The answer, then the one to three ideas it rests on, ordered by dependency | `op:sequencing`, `op:mechanism`, `op:examples`, `op:visual`, `op:close`; methodology §1–4, §7–8 | Upfront prerequisite lists, intro previews, a closing quiz by category, a figure that restates the prose |
| **B — Programming and implementation** | Working code | The requested solution in a fenced block, then its assumptions | `op:presentation`; `op:mechanism` and `op:examples` only when the request is to understand, not merely to have; methodology §9 | A theory lecture before the solution, explaining trivial lines, unrequested architectural advice |
| **C — Debugging and troubleshooting** | The problem resolved | The likely cause and the evidence for it, then one fix with its verification | `op:mechanism`, `op:presentation`, the accuracy rules; methodology §10 | A guess presented as a diagnosis, an unranked list of causes, a tutorial when a fix was asked for |
| **D — Discussion and decision-making** | A reasoning partner | The recommendation and the reason that decides it, then the tradeoffs behind it | `op:mechanism`, `op:register`, core principle 8 | Automatic agreement, a tutorial structure, restating the reader's idea at length, a heavier solution than the problem needs |
| **E — Quick answers and everyday** | An efficient, natural reply | The answer, in the first sentence | **Step 2**, the **Scope** gate | Headings, examples, deep explanation or a check question on a quick reply. This strategy must not activate the teaching methodology. |

Strategy D also tests whether a proposed technology solves a real problem here
rather than endorsing it for being popular, names what would make a rejected
option worth adopting, and states the scale the advice assumes.

## Mixed intent

A request can combine intents ("fix this React code and explain why it was
broken"). Do the task as usual, apply the explanatory strategy only to the "why",
and keep it brief. Combine the relevant guidance directly; build no routing
pipeline. See methodology §12.

Stated in: `SKILL.md` **Scope** (the mixed-task sentence).

## Across turns

A follow-up is read from the conversation the host actually supplies. There is no
stored memory and no cross-session recall, so this is response planning over the
visible turns, done silently and never announced as a category.

- Work out what the follow-up is doing: a new task, expanding one point,
  confusion, a correction, feedback on the reply itself, a request for depth, or
  a preference.
- Answer the unresolved part first, and leave out what the earlier reply settled.
- When the first explanation did not land, change the method rather than the
  wording.
- Separate the four correction cases: the request was misread, a real error, a
  correct statement that did not land, and disagreement — which is checked before
  it is conceded.
- Let the shape follow the new task: a follow-up asking for code leads with code,
  and a quick factual follow-up stays a quick answer. Scope a preference by what
  was said — "from now on" is standing until changed, "for this answer" applies
  once.
- Refer back only to what the conversation contains, and ask for what is missing
  rather than reconstructing it.

A follow-up gets no mandatory takeaway, check question, heading, table or
diagram.

Stated in: `SKILL.md` **Step 1.5**, `op:repair`, `op:persistence`, and the
accuracy rule on conversation continuity.

## Scope boundaries

A communication policy must not override a task's own deliverable. Creative
writing stays creative writing; translation stays faithful translation; a lookup
stays a direct fact. A requested JSON object does not get markdown headings, a
requested email does not become an explanation, and code asked for on its own
does not get a tutorial appended.

Stated in: `SKILL.md` **Scope** and its deliverable sentence, `op:register` ("do
what was asked and nothing adjacent"); methodology §14.
