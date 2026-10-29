# Using Socialized-Claude

How the skill changes an answer, what it deliberately leaves alone, and how to steer it.

Installing is covered in [INSTALLATION.md](INSTALLATION.md). What is tested on which surface
is in [COMPATIBILITY.md](COMPATIBILITY.md).

## What changes when it applies

| The answer | Instead of |
|---|---|
| Starts with the answer | Starts with background and arrives at the answer |
| Introduces an idea before the idea that needs it | Uses a term, then defines it two paragraphs later |
| Names the cause, step by step, for *how* and *why* | Describes what happens without saying what makes it happen |
| Takes the shape of its content — steps for a process, a table for options against tradeoffs, a small diagram for a flow or for how components connect | Puts everything in undifferentiated paragraphs, or adds headings to things that aren't sections |
| May mark a heading or label with a meaning-matched icon when that helps you find the idea | Decorates every line, or puts emoji inside code |
| Draws the visual where the mechanism is hardest, and keeps that support to the end | Front-loads one diagram and lets the last third go bare |
| Writes plain sentences: one point each, active voice | Stacks clauses and hedges |
| Pitches at a practitioner unless you show otherwise | Explains the basics of your own field back to you |
| Keeps a standing instruction ("under 100 words") for the rest of the chat | Obeys once, then drifts back |
| After a correction, answers what you meant | Repeats the same explanation louder |
| When reporting work: what changed, what was not checked, what it needs from you | A confident summary with the gaps left out |
| Closes with something worth keeping | Closes with a quiz or a check-in question |

## What it deliberately does not touch

Translation, editing your prose, quick factual lookups, greetings, creative writing, and
ordinary code changes get ordinary answers. The skill's own text tells Claude to answer those
normally. A one-line question should get a one-line answer; if it starts getting a lesson,
that is a defect — see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Five requests and what to expect

> **These are illustrations of the rules, not transcripts.** They describe the shape of a good
> answer under each operation. For side-by-side weak/better pairs — three of them quoted
> verbatim from the research archive, the rest constructed — see
> [`COMMUNICATION_EXEMPLARS.md`](../COMMUNICATION_EXEMPLARS.md).

**Teaching — "How does a database index work?"**
Opens with what an index is for in one or two sentences, then walks the mechanism: where the
B-tree sits, what a lookup does with it, what a write costs. The hardest step gets the diagram,
not the easiest. Prerequisites arrive before the ideas that need them.

**Coding — "Why does this function return None?"**
Names the cause in the first line, points at the line responsible, gives the fix. No tutorial
framing around a bug you already understand, and no closing comprehension question.

**Debugging — "Requests time out under load but not in staging."**
Separates what is known from what is assumed, and says which assumption to test first. Where
the answer depends on configuration or on a workload you have not stated, it says so instead
of stating a guarantee flatly.

**Technical decision — "Postgres or DynamoDB for this?"**
A table of the options against the tradeoffs that actually differ, then a recommendation with
its condition attached. Not a neutral survey that leaves you where you started.

**Follow-up — "No, I meant the write path."**
Re-reads the original request against the correction and answers the narrower question. It does
not re-explain the read path with more words.

## Steering it

| You want | Say |
|---|---|
| To force it on | `Use the socialized skill for this.` or, in Claude Code, `/socialized` |
| To turn it off for one message | `Answer normally, without the socialized skill.` |
| A different level | "I'm new to this" or "I'm an expert" — it reads your wording and adjusts |
| A length limit that sticks | "Keep answers under 100 words" — it holds for the rest of the chat |
| A length limit for one answer | "Shorter, just this time" — it stops after that answer |
| Plain prose, no visuals | "No tables or diagrams" — standing instructions override the defaults |

Claude decides on its own whether to load a skill for a given message, so natural activation is
never guaranteed. Explicit invocation is the reliable path. See
[COMPATIBILITY.md](COMPATIBILITY.md#activation-four-different-things) for why "installed" and
"applied" are not the same thing.

## Telling whether it was used

Expand Claude's activity or thinking panel and look for `socialized/SKILL.md` being read.

- Seeing it read is evidence it activated.
- Seeing nothing is **not** evidence it was skipped — some surfaces show less detail.
- **Asking Claude "did you use the skill?" proves nothing.** It is self-report, and the question
  changes the conversation.

A correct answer never mentions the skill, its steps, or words like "operations". If it narrates
its own method, that is a defect worth reporting.

## What it will not do for you

It does not make Claude more accurate, more current, or better at reasoning. It changes how an
answer is organised and written. Whether that makes explanations easier to understand has not
been measured — [LIMITATIONS.md](LIMITATIONS.md) is the honest account.
