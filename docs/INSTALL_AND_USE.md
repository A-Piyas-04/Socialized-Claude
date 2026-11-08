# Socialized-Claude: install and use

## The file

`socialized.zip`, version 2.2.0, from the
[latest release](https://github.com/A-Piyas-04/Socialized-Claude/releases/latest)
or `dist/socialized.zip` in this repository. Upload it as it is; don't unzip and
re-zip it.

## Upload it

1. Open claude.ai (web or desktop app).
2. Go to **Customize → Skills**. On some versions it is **Settings →
   Capabilities** or **Settings → Features**.
3. If an older `socialized` is already installed, delete it first.
4. Choose to add or upload a skill, and pick `socialized.zip`.

You need a plan that includes Skills, with code execution ("create and edit
files") turned on. On Team and Enterprise plans an admin may need to allow it.

## Turn it on

In the Skills list, switch **socialized** on. Start a new chat afterwards;
chats that were already open don't pick it up.

## What changes

When you ask Claude to explain something ("how does…", "why does…", "I don't
get…", "explain this code", "should we do X or Y"), the answer:

- **Starts with the answer**, in the first one or two sentences.
- **Has a clear page shape** when it runs to two or more sections:
  - a `#` title with a line under it;
  - a one-line map of the numbered sections;
  - each section headed `##` with a matching icon, and a `---` line between
    sections.
- **Draws a diagram for a chain or a process**, right after the answer. It also
  uses a table for comparisons, bars for numbers, and coloured flowcharts for
  branches, all in plain markdown.
- **Puts ideas in order**, so nothing is used before it is introduced.
- **Explains the cause**, step by step, for why and how questions, including the
  obvious approach and why it fails.
- **Writes your next question into the page** as a 🙋 line, then answers it.
- **Gives one analogy** in a 🧠 callout, and says where it stops holding, when a
  why or how answer has nothing you already know to lean on. Decisions,
  debugging and expert answers get none.
- **Explains every specialist term** in a short parenthesis the first time it
  appears.
- **Ends with something to keep**: a 🎯 takeaway and, when you're learning (new
  to the topic, "teach me", or still confused), a 🧪 check question with its
  answer.
- **Fits the request.** A quick fact stays one or two sentences. "Help me decide"
  leads with a recommendation. "Why is this failing" leads with the likely cause
  and one fix.
- **Uses plain sentences**: one point each, active voice, everyday words where
  they are exact.
- **Pitches at your level.** It reads your wording and assumes you know the
  basics of the field unless you show otherwise. If you know a neighbouring field
  ("I've written Go for years but never looked inside a database"), it starts
  from what you know and teaches only what's missing. Say "I'm new to this" or
  "I'm an expert" to move it. An expert gets no glosses and no analogy.
- **Remembers how you asked it to answer** (for example "keep it under 100
  words") for the rest of the chat.
- **After a correction, re-reads your request** and answers what you meant,
  instead of repeating itself.
- **When it reports work it did**, says what changed, what it didn't check, and
  what it needs from you.

It builds an artifact (an interactive page, an SVG) only when you ask for one.
It doesn't make answers longer for the sake of it, and it leaves other requests
alone: translation, editing your text, quick facts, greetings, and creative
writing get normal answers. A short answer stays short, with no title or
sections.

## Make it apply explicitly

Claude decides on its own when to use the skill, so it won't load every time.
To make sure it does, start your message with `/socialized`, or with:

```
Use the socialized skill for this.
```

## Turn it off

- **For good:** switch **socialized** off in Customize → Skills, or delete
  it there. New chats won't use it.
- **For one message:** say "Answer normally, without the socialized skill."
