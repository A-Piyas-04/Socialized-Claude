# Skill upgrade plan — presentation, voice, visuals, durability

> **Written for:** the project owner and whoever implements the phases.
> **Scope:** `skill/socialized/` only. No plugin work in any phase.
> **Branch:** started on `skill-only` at `2714c69` — the last commit before plugins
> existed. Phases 1–3 are `280a31e`, `1b8a1b4`, and `a105958` on `skill-only`.
> Phase 4 is on `skill-upgrade-phase-4`, branched from `d2657e2`.
> **Status (2026-11-02):** all four phases ✅ complete. Each phase's behavioural
> check is still open, and only you can do it.

---

## 🎯 What this plan is

You asked for fifteen things. They are not fifteen separate jobs — they fall into
four groups, and the groups have a required order. Voice changes are pointless if
the page is still a wall of text. Emoji and diagrams are decoration if the voice
is still a textbook. And all of it is worthless if the markdown renders broken.

So: **space first, then voice, then visuals, then durability.**

| Phase | Theme | Your words it answers | Status |
| --- | --- | --- | --- |
| 1 | 🧱 Space and hierarchy | better structure, spacious, whitespace in one view, font size and style, many sections, bullet structure | ✅ complete |
| 2 | 💬 Human voice | conversation between two people, sequential, analogy, scenario, examples, no unexplained jargon | ✅ complete |
| 3 | 👀 Visual and colour | flowcharts, diagrams, huge emoji set, colourful characters, markdown over SVG | ✅ complete |
| 4 | 🛡️ Durability | markdown never breaks, and none of the above silently regresses | ✅ complete |

---

## ⚠️ The constraint that shapes everything

When this plan was written, `SKILL.md` was **472 of its 500 permitted body
lines**, which left 28 lines of room. Every item on your list adds instructions.
Written naively, the list needed roughly 150 new lines, and that did not fit.

Here is how the budget moved through each phase (one block is 10 lines). The
rendered count is the full build, which has a test guard of 460.

```
start     ███████████████████████████████████████████████░░░  472 / 500
Phase 1   ████████████████████████████████████████████░░░░░░  439 / 500   rendered 392
Phase 2   ███████████████████████████████████████████████░░░  471 / 500   rendered 418
Phase 3   █████████████████████████████████████████████████░  485 / 500   rendered 432
Phase 4   █████████████████████████████████████████████████░  494 / 500   rendered 441
```

After Phase 4, **6 body lines** remain. Any further rule must displace one.

Three consequences, which the phases are built around:

- 🔁 **Phase 1 must reclaim space before it spends any.** A compression pass over
  the twelve operations — merging duplicate wordings, not dropping rules — is the
  first task, not a nice-to-have.
- 🗂️ **Bulk material goes into reference files.** References are not line-capped.
  The emoji catalogue and the conversation patterns belong there, with one
  pointer line each in `SKILL.md`.
- ✋ **Every later addition must displace something.** Once Phase 1's headroom is
  spent, a new rule means an old rule is merged or cut. Say which, in writing.

The other standing limits: `pytest` stays green at every commit, and
`research-results-2026-10-26/` is never touched.

---

## 🧱 Phase 1 — Space and hierarchy ✅ complete

**Goal:** a reply that can be taken in at a glance, not decoded.

### What changes for the reader

Before Phase 1, a section was allowed to be a 4-sentence, 80-word paragraph. That is still a block. You
asked for air, so the target drops and the blank line becomes structural rather
than incidental.

**Before and after, same content:**

```diff
- Write-back caching delays the write to main memory until the line is evicted,
- which means a crash between the cache write and the eviction loses the data,
- and this is why write-back is paired with a battery-backed cache in storage
- controllers that cannot tolerate that window.
+ Write-back caching delays the write to main memory until the line is evicted.
+
+ **The risk:** a crash in that window loses the data.
+
+ That is why storage controllers pair write-back with a battery-backed cache.
```

### Edits

| Where | Change |
| --- | --- |
| `SKILL.md` all 12 operations | Compression pass. Merge rules stated twice in different wordings. Target: reclaim 60–80 lines. **Drop no rule** — list every merge. |
| `op:presentation` | Paragraph ceiling 4 sentences / 80 words → **3 sentences / 50 words**. State it as a ceiling, not a target. |
| `op:presentation` | New rule: a blank line is a unit separator, and a section of three or more units gets visible separation (sub-heading, rule, or labelled list). |
| `op:presentation` | New rule on **emphasis range** — markdown has no font sizes, so name the real ladder: `##` / `###` / `####` for size, and bold, italic, `code`, blockquote for style. Require at least three distinct levels in any answer with three or more sections. |
| `op:presentation` | Strengthen the sectioning rule: prefer more, smaller sections over fewer, longer ones. A section running past about 12 lines gets split or sub-headed. |
| `op:presentation` | Bullet structure: a bullet leads with a **bolded label**, then the claim. Sub-bullets carry detail, never a second top-level idea. |
| `scripts/structural_metrics.py` | `DENSE_PARAGRAPH_WORDS` 80 → 50, `DENSE_SENTENCES` 5 → 4. Add `whitespace_ratio`, `heading_count`, `units_per_section`, `emphasis_levels_used` as **heuristics that never gate**. |

### ✅ Acceptance

- ✅ `SKILL.md` body is **439 lines** (was 469), rendered full variant **392** —
  under both guards, leaving headroom for Phases 2–4. _(done 2026-11-02)_
- ✅ `python -m pytest -q` green: **401 passed, 1 skipped**. _(done 2026-11-02)_
- ⬜ Run three of your own prompts. The test is whether a section fits in one screen
  without scrolling, and whether you can find the answer by scanning headings
  alone. **This behavioural check is still yours — it cannot be automated.**

### 🚨 Risk

A 3-sentence ceiling can **fragment a connected causal argument** — the chain
"A, because B, which means C" gets chopped into three orphan lines. The guard is
an explicit prose exception: sentences forming one continuous argument stay
together, and the ceiling yields to that. Write the exception into the same rule,
not somewhere else.

---

## 💬 Phase 2 — Human voice ✅ complete

**Goal:** the answer reads like a person explaining to a person, not a reference
manual being recited.

### What changes for the reader

This was the phase with the least existing support. Here is each ask, checked
against the skill before and after Phase 2:

| Your ask | Before Phase 2 | After |
| --- | --- | --- |
| Analogy | ⚠️ Deprioritised in `op:examples` | ✅ Equal standing |
| Scenario | ❌ Absent | ✅ Opens teaching answers |
| Two-person flow | ❌ One-directional only | ✅ `op:conversational` |
| Sequential explanation | ✅ `op:sequencing` | ✅ Unchanged |
| No unexplained jargon | ✅ `op:terms`, loose | ✅ Gloss before use |

So Phase 2 is mostly **new behaviour**, and it needs Phase 1's reclaimed lines.

### The core idea: the implied second voice

A textbook asserts. A conversation **anticipates**. The move is to write the
reader's next question into the page, then answer it:

> **"So why not just write to memory every time?"**
>
> Because then every write waits on memory, and memory is roughly a hundred times
> slower than the cache. You would pay that cost on every single write.

That is the whole technique: surface the objection, then resolve it. It costs one
heading and two sentences, and it is what makes prose feel like speech.

### Edits

| Where | Change |
| --- | --- |
| `op:examples` | **Reverse the analogy demotion.** Analogy becomes a first-class tool for a beginner or an unfamiliar mechanism. Keep the existing guard: it must preserve the causal structure, and the answer must say where it stops holding. |
| `op:examples` | New rule: **scenario**. Open a teaching answer with a concrete situation — someone doing something, and something going wrong — before any definition. |
| `op:examples` | New rule: trace an example as **state → action → result**, so the reader sees change, not a static snapshot. |
| **New** `op:conversational` | A new operation, or a renamed `op:plain` if the line budget is tight. **Shipped as a new 13th operation.** Carries: the reader's-question move; direct address ("you"); the contraction-friendly register; the ban on announcing ("In this section we will…"). |
| `op:terms` | Tighten to a hard rule: **no term, acronym or phrase appears before a plain-language gloss in the same sentence or the one before it.** No exception for "obvious" terms. |
| **New** `references/conversation-grammar.md` | The bulk material: 8–10 worked question-and-answer patterns, a register ladder, and weak/better pairs. Kept out of `SKILL.md`; one pointer line added to "Reference files". |
| `SKILL.md` Step 3 | Two new checks: "Does the answer surface the reader's next question at least once in a teaching answer?" and "Does any term appear before its gloss?" |

### ✅ Acceptance

- ✅ Twelve operations became **thirteen** — Phase 1 freed the lines (body 471/500,
  rendered 418/460), so `op:conversational` was added rather than folded into
  `op:plain`. A `conv` variant key was added; no `V_conv` sweep arm. _(done 2026-11-02)_
- ✅ `python -m pytest -q` green: **404 passed, 1 skipped**. _(done 2026-11-02)_
- ⬜ Read an answer aloud. If you would not say that sentence to a colleague, the
  phase is not done. **This behavioural check, and watching for the chattiness risk
  below, is still yours — it cannot be automated.**

### 🚨 Risk

Conversational register degrades into **chattiness** — filler, false enthusiasm,
"Great question!". The guard is explicit: the second voice may only ask a question
the content then answers. No interjections, no praise, no personality for its own
sake.

---

## 👀 Phase 3 — Visual and colour ✅ complete

**Goal:** the page is colourful and diagrammatic in **markdown**, with SVG and
artifacts as rare exceptions.

### What changes for the reader

Two facts to design around:

- 🚫 Markdown has **no text colour**. Any rule promising colour in general cannot
  be followed. Three techniques actually render: a `diff` fence (red and green
  lines), Mermaid `classDef` (node fills), and emoji.
- 📊 Block characters (`█▓▒░`) are the only portable bar chart.

So "colourful characters" is the honest target, and the skill should name those
techniques rather than gesture at colour.

### The emoji change

The old rule was a **closed set of six** — ✅ ❌ ⚠️ 🟢 🟡 🔴 — with the words "and
no other symbols". You asked for a huge set to choose from, so Phase 3 replaced
that rule with a **two-layer system**:

| Layer | Set | Rule |
| --- | --- | --- |
| 🏷️ **Status** | Closed, the existing six | Semantic. Two or more distinct markers in one list or table. Meaning named in the caption. |
| 🧭 **Navigation** | Open, ~150 in a new reference | Decorative but meaningful. Opens a heading, a callout, or a bullet label. Must match the meaning of what it labels. |

Hard limits that keep it from becoming noise:

- ❌ Never inside code, JSON, a path, or an identifier.
- ❌ Never in a formal, casual, or one-line reply.
- ⚖️ No quota. An icon that does not aid navigation is deleted.

### Edits

| Where | Change |
| --- | --- |
| **New** `references/emoji-palette.md` | The ~150-icon catalogue, grouped by meaning (state, flow, risk, data, people, time, tooling). This is the "huge set to choose from", and it lives in a reference, not in `SKILL.md`. |
| `op:visual` | Replace the "no other symbols" clause with the two-layer system above. Point at the palette file. Keep a small working set (~40 icons) inline for common cases. |
| `op:visual` | Name the three rendering techniques explicitly (`diff` fence, Mermaid `classDef`, status emoji) in place of any general colour promise. |
| `op:visual` | Strengthen diagram coverage: **a flowchart or sequence diagram for every branching or time-ordered mechanism**, not only when prose would take three-plus sentences. |
| `op:visual` | Keep the markdown-first stance and narrow the SVG/artifact exception: only on explicit request, only on claude.ai, and the markdown answer stays complete without it. |
| `scripts/structural_metrics.py` | Extend `NAV_ICONS` to the full palette. Exempt the intended emoji-led bullet and heading forms so correct output does not flag. Add `visual_count` and `icon_count` as **heuristics that never gate**. **Shipped:** `NAV_ICONS` is parsed from the palette file; `visual_count` already existed, so only `icon_count` was added. |

### ✅ Acceptance

- ✅ `references/emoji-palette.md` holds **153** navigation icons in seven meaning
  groups, plus the closed status six; `op:visual` carries a 42-icon working set.
  `SKILL.md` body **485/500**, rendered **432/460**. _(done 2026-11-02)_
- ✅ `python -m pytest -q` green: **410 passed, 1 skipped**. _(done 2026-11-02)_
- ⬜ Every emoji in the palette renders in your terminal **and** on claude.ai. Drop
  any that does not — this needs checking, not assuming. The palette is limited to
  single code points from Emoji 11 or earlier, but **the render check is still yours.**
- ⬜ A long answer of yours has at least one diagram, and no icon you would call
  decoration. **This behavioural check is still yours — it cannot be automated.**

### 🚨 Risk

An open emoji set drifts into **emoji soup**, where everything is marked and so
nothing stands out. The guard is the meaning-match requirement plus the
never-in-code rule. If an answer has more icons than headings, it has failed.

---

## 🛡️ Phase 4 — Durability ✅ complete

**Goal:** the markdown never breaks, and Phases 1–3 cannot silently regress.

### What changes for the reader

Nothing, when it works. That is the point. This phase exists because the previous
three add Mermaid blocks, nested fences, wide tables and emoji — exactly the
things that render as garbage when they go wrong.

**The failure modes worth naming:**

| Break | Cause | Rule that prevents it |
| --- | --- | --- |
| 🧨 Fence collapse | A fenced block inside a fenced block with the same backtick count | Outer fence uses more backticks than any inner one |
| 📐 Table rupture | An unescaped pipe inside a cell | Escape it, or move the content under the table |
| 🧩 Mermaid blank render | A parenthesis, quote or arrow inside a node label | Keep labels to plain words, four or fewer |
| 📏 Mobile overflow | More than four table columns | The existing four-column cap, enforced |
| 🔣 Tofu boxes | An emoji outside the common set | The palette is limited to Emoji 11 single code points; your render check confirms it |
| ⤵️ Heading jump | `##` straight to `####` | The existing no-skip rule, checked |

### Edits

| Where | Change |
| --- | --- |
| `SKILL.md` | **New always-on section: "Markdown that renders"** — the six rules above, stated as actions. Always-on rather than an operation, because a broken table in a casual reply is still broken. Place it in the always-on core so it survives context compaction. |
| `SKILL.md` Step 3 | One new check: "Does every fence close, every table row have matching pipes, and every Mermaid label stay plain?" |
| **New** `scripts/lint_markdown.py` | Offline renderer-safety checker: unbalanced fences, nested same-width fences, pipe-count mismatch, Mermaid label characters, heading-level jumps, table width. Operates on a response file, like the existing `lint_response.py`. |
| **New** `tests/test_markdown_safety.py` | Feeds known-broken samples to the linter and asserts each is caught. |
| **New** `tests/test_presentation_upgrade.py` | One invariant-based suite for Phases 1–3. Assert **behaviour, not phrasing** — phrase-pinned tests make "add more text beside it" the cheapest change, which is how instruction sets bloat. |
| `docs/` | Record every merge and every superseded rule from Phases 1–3 in one place. |

### ✅ Acceptance

- ✅ `python scripts/lint_markdown.py` catches all six break classes on crafted
  samples, under seven codes (fences get two: `unclosed_fence`, `nested_fence`).
  `SKILL.md` and every reference file pass it. _(done 2026-11-02)_
- ✅ `python -m pytest -q` green: **473 passed, 1 skipped**. In
  `tests/test_presentation_upgrade.py`, one removal test per rule deletes that
  rule from a copy of `SKILL.md` and checks it is reported missing, so removing
  any Phase 1–4 rule fails the suite. _(done 2026-11-02)_
- ✅ The 500-line budget holds: body **494/500**, rendered **441/460**. Two merges
  paid for the new section (see the change record below). _(done 2026-11-02)_
- ⬜ Run a long answer through `python scripts/lint_markdown.py`, then look at it
  rendered. **The linter only sees text you hand it; reading real output is still yours.**

### 🚨 Risk

A renderer-safety linter can only check **text you hand it**. It cannot watch a
live conversation. So this phase raises confidence; it does not prove the output
is good. Behavioural acceptance stays yours — read real answers.

---

## 📋 Order, and what is deliberately not here

**The order is not negotiable.** Phase 1 funds the others in line budget. Phase 2
is the only phase whose work is mostly new rather than a change to an existing
rule. Phase 3 depends on Phase 1's hierarchy to have headings worth labelling.
Phase 4 can only harden what already exists.

Each phase ends at a commit with `pytest` green, so you can stop after any of them
and keep what you have.

**Not in this plan, on purpose:**

- ❌ Any plugin work — no `plugins/`, no `build_plugin.py`, no marketplace entry.
- ❌ Any new operation beyond the single conversational one in Phase 2, and that
  one only if the line budget allows.
- ❌ Any counting rule beyond the paragraph ceiling. Thresholds that count things
  proved brittle before; prefer rules naming an action.
- ❌ Any claim that these phases improve comprehension. The harness in
  `evaluation/` is the only thing that could show that, and running it is a
  separate decision.

## ❓ Decisions

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | Paragraph ceiling at 3 sentences, or 2? | ✅ 3 sentences, about 50 words |
| 2 | Thirteen operations, or fold into `op:plain`? | ✅ Thirteen; no new sweep arm |
| 3 | About 150 icons, or a tighter set? | ✅ 153 icons, 42 inline |
| 4 | Stop after Phase 2, or run all four? | ✅ All four run |

Each resolved decision is recorded with its reasoning under "Decisions" in
`AGENTS.md`.

## 🧾 Change record (Phases 1–4)

Every merge and every superseded rule, in one place. No rule was dropped: each
merge folded one wording into another that already said the same thing.

### Merges

| Phase | Where | Merged |
| --- | --- | --- |
| 1 | `op:sequencing` | Obvious-approach bullet, kept in `op:mechanism` |
| 1 | Accuracy rules | Duplicate "unsure of a fact" bullet |
| 1 | `op:register` | Beginner rule, folded into "explain simply" |
| 1 | `op:close` | Interactive-offer rule, compressed |
| 1 | `op:plain` | Section-map rule, compressed |
| 1 | Step 3 | 17 questions became 11 |
| 3 | `op:visual` | Colour techniques, into the one-colour-code bullet |
| 3 | Step 3 | New visual checks, into the two visual questions |
| 4 | `op:presentation` | Blank-line and new-unit bullets, into two |
| 4 | `op:conversational` | No-praise and no-persona bullets, into one |

Phase 1's `op:sequencing` merge removes the obvious-approach rule from the
single-operation `seq` ablation build only. The `full` build and the frozen
`pilot16-cc` build are unaffected.

### Superseded rules

| Phase | Old rule | Replaced by |
| --- | --- | --- |
| 1 | Paragraph of 4 sentences or 80 words | 3 sentences or about 50, with a causal exception |
| 1 | `DENSE_SENTENCES` 5, `DENSE_PARAGRAPH_WORDS` 80 | 4 and 50 |
| 2 | "Prefer a direct case over an analogy" | Analogy given equal standing |
| 2 | Scenario only for beginners | Scenario opens any teaching answer |
| 2 | Terms the reader "clearly knows" stay undefined | Only terms the reader used |
| 3 | Six status icons "and no other symbols" | Status layer plus navigation layer |
| 3 | Headings stay unmarked | A palette icon may open a heading |
| 3 | Diagram only past three sentences | Every branch or time order in a teaching answer |
| 3 | Artifact plus "a short markdown answer" | Markdown complete without the artifact |
| 3 | `treatment-selection.md`: "emoji as structure" | "Emoji as decoration", plus "emoji soup" |
| 4 | Render rules only inside operations | Always-on "Markdown that renders" section |

**The takeaway:** your fifteen asks became four phases with a forced order. All
four are done, and the 6 body lines left mean any further rule must displace one.
