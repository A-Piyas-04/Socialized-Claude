# Explanation Lab: install and use

## The file

`dist/explanation-lab.zip`. Upload it as it is; don't unzip and re-zip it.

## Upload it

1. Open claude.ai (web or desktop app).
2. Go to **Customize → Skills**. On some versions it is **Settings → Features**.
3. Choose to add or upload a skill, and pick `explanation-lab.zip`.

You need a plan that includes Skills, with code execution ("create and edit
files") turned on. On Team and Enterprise plans an admin may need to allow it.

## Turn it on

In the Skills list, switch **explanation-lab** on. Start a new chat afterwards;
chats that were already open don't pick it up.

## What changes

When you ask Claude to explain something ("how does…", "why does…", "I don't
get…", "explain this code"), the answer:

- **Starts with the answer**, before any background or headings.
- **Puts ideas in order**, so nothing is used before it is introduced.
- **Explains the cause**, step by step, for why and how questions.
- **Takes the shape of the content**: numbered steps for a process, a table for
  comparisons, a small diagram for a branching flow, a couple of sentences when
  that is all it takes.
- **Uses plain sentences**: one point each, active voice, everyday words where
  they are exact.
- **Pitches at your level.** It reads your wording and assumes you know the
  basics of the field unless you show otherwise. Say "I'm new to this" or "I'm an
  expert" to move it.
- **Remembers how you asked it to answer** (for example "keep it under 100
  words") for the rest of the chat.
- **After a correction, re-reads your request** and answers what you meant,
  instead of repeating itself.
- **When it reports work it did**, says what changed, what it didn't check, and
  what it needs from you.

It doesn't make answers longer for the sake of it, and it leaves other requests
alone: translation, editing your text, quick facts, greetings, and creative
writing get normal answers.

## Make it apply explicitly

Claude decides on its own when to use the skill, so it won't load every time.
To make sure it does, start your message with:

```
Use the explanation-lab skill for this.
```

## Turn it off

- **For good:** switch **explanation-lab** off in Customize → Skills, or delete
  it there. New chats won't use it.
- **For one message:** say "Answer normally, without the explanation-lab skill."
