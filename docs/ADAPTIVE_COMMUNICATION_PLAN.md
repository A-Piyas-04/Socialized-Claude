# Socialized-Claude — Approach B: Adaptive Communication Intelligence

**Status:** Planning · **Baseline:** Approach A (successful skill, V2 Phase 9, build `fd6a5ce`)  
**Objective:** Improve *communication decisions* while retaining Approach A's excellent presentation.

## Non-negotiable rules

- **Freeze Approach A.** Tag the known-good production commit (e.g., `v2-approach-a-stable`) and preserve its installable ZIP. Do not develop Approach B on the production branch.
- **Stay a Claude Skill.** No plugin migration, paid API, new server, or external inference dependency.
- **Do not replace the formatting system.** Every experiment starts from the frozen skill and must preserve useful formatting, readable visuals, and factual correctness.
- **No evaluation bureaucracy.** Use a small number of real Claude conversations, reuse the existing offline linters where useful, and avoid manual batch copying/scoring.
- **Add only behavior that solves an observed problem.** Prefer revising or simplifying existing operations over layering on new mandatory rules.
- **The owner commits.** The agent edits files and runs read-only checks. It never commits, pushes, tags, branches, merges or creates releases. It hands back the changed files and a suggested commit message, and the owner runs git.
- **Revert by default.** If improvements are weak or inconsistent, keep Approach A in production.

## Starting point

The existing skill already has **13 operations**, including reader register, sequencing, answer length, conversational questions, repair, and persistence. The opportunity is to make their *selection and calibration* more context-sensitive—not to claim these capabilities are absent. Existing evidence mainly supports presentation improvements; improved comprehension is not yet demonstrated. The planned V2 Phase 10 conformance work is still unimplemented and need not block this roadmap.

---

## Phase 0 — Protect the baseline

**Goal:** Make regression and rollback straightforward.

**Implement**
1. Create a stable Git tag and archive the current working skill ZIP with its commit hash.
2. Create an isolated branch, `experiment/adaptive-communication`.
3. Record the specific formatting behaviors that must not regress (readable headings, spacing, diagrams when useful, short units, and correct Markdown).

**Deliverable:** Immutable baseline + experimental branch + short preservation checklist.

**Exit condition:** The current skill can be reinstalled exactly as before, even if every Approach B experiment fails.

### Phase 0 record (2026-11-04)

- **Tag:** `skill-stable-format` (annotated), on `fd6a5ce`. `skill/` and `dist/` are byte-identical from `fd6a5ce` through `production` at `f79e2fc`.
- **ZIP sha256:** `8e1a2c0adb9b893e0f2d51f234024237d1607c6bdedc2d53fbcf3f12f9bed5b0`. The ZIP committed at the tag, a fresh `package_skill.py` build from the tag, the manifest, and the release download all match it.
- **Release:** [skill-stable-format](https://github.com/A-Piyas-04/Socialized-Claude/releases/tag/skill-stable-format), with the ZIP and its manifest attached.
- **Rollback:** in claude.ai, open Settings, then Capabilities, then Skills. Remove `socialized` and upload `socialized-skill-stable-format-fd6a5ce.zip`.
- **Branch:** `experiment/adaptive-communication`, cut from `production` at `f79e2fc`. `production` is not changed by Approach B work.

**Preservation checklist.** These must not regress. Each line names what catches a regression.

| Behaviour | Checked by |
|---|---|
| Markdown renders (fences, tables, Mermaid labels) | `scripts/lint_markdown.py`, zero breaks |
| `#` title, blank line, `---`, numbered `##` sections | Eye; `test_page_shape_slots_follow_their_operations` |
| Short units: paragraphs, list items, table cells | `dense_paragraph`, `dense_table_cell` flags |
| Mermaid for branches and time order | Eye; `linear_ascii_flow` flag |
| 🙋 question, 🧠 analogy, 🎯 takeaway, 🧪 check | Eye, on teaching answers |
| Icons from the palette only | `emoji_outside_palette` |
| Short factual answers stay short | Eye, on a direct-fact prompt |
| Examples and exemplars lint clean | `tests/test_examples_shape.py` |

---

## Phase 1 — Concept-level knowledge calibration

**Goal:** Explain only the missing concepts, rather than treating a user as uniformly beginner/practitioner/expert.

**Implement**
1. Infer **known concepts**, **missing concepts**, and **uncertain assumptions** from the user's question and prior turns.
2. Start from their most relevant existing knowledge; teach only prerequisites essential to the question.
3. Avoid inferring expertise from job title or from use of a single technical term.
4. When knowledge is uncertain, use a brief in-context gloss instead of interrupting with a questionnaire.
5. Keep this assessment implicit: no visible “knowledge profile” or repetitive preamble.

**Deliverable:** A small revision to existing `Step 1`, `op:register`, and/or `op:sequencing`, plus targeted examples.

**Quick check:** Ask the same technical question in a beginner context and an experienced-but-new-to-this-concept context. Both should be accurate, different in depth, and free of needless repetition.

**Go/no-go:** Keep only if explanations match the reader more accurately **without making them longer by default**.

---

## Phase 2 — Intent-sensitive depth and strategy

**Goal:** Choose the smallest explanation that fully satisfies the user's actual intent.

**Implement**
1. Distinguish “give me the answer,” “explain why,” “walk me through,” “help me decide,” and “debug this.”
2. For each, prioritize appropriate content: result, causal chain, procedure, tradeoffs, or diagnosis.
3. Make analogies, self-checks, overview diagrams, and expanded sections **conditional on usefulness**, while keeping Approach A's visual language available.
4. Respect explicit brevity, depth, and formatting requests over defaults.

**Deliverable:** A compact intent-to-strategy decision guide, updating existing methodology instead of adding a parallel system.

**Quick check:** Compare short factual, deep teaching, architecture decision, and debugging requests. Verify that Claude does not force one teaching template onto all four.

**Go/no-go:** Keep if responses become more targeted while long explanations remain visually excellent.

---

## Phase 3 — Adaptive multi-turn continuity

**Goal:** Make follow-up answers move the conversation forward instead of restarting the lesson.

**Implement**
1. Treat follow-ups as evidence of what the reader now knows and what remains unclear.
2. Answer the **new gap**, without repeating definitions already established unless needed.
3. Preserve the user's standing preferences (e.g., concise, visual, technical) across turns.
4. Handle topic changes cleanly; do not drag old assumptions into an unrelated subject.

**Deliverable:** Focused updates to existing follow-up, persistence, and conversational rules.

**Quick check:** Run one natural three- or four-turn teaching exchange with a correction and a narrowing follow-up.

**Go/no-go:** Keep if later answers are more relevant and less repetitive without losing essential context.

---

## Phase 4 — Intelligent communication repair

**Goal:** Respond to confusion by changing the *explanation strategy*, not just paraphrasing the same text.

**Implement**
1. Identify the likely failure: missing prerequisite, abstract language, skipped causal step, excessive detail, or misunderstanding of the question.
2. Repair that failure with the lowest-cost intervention: one prerequisite, a concrete example, a causal chain, or a different representation.
3. Acknowledge a genuine mistake directly and correct it; never invent certainty about why a user is confused.
4. Avoid patronizing reassurance and avoid repeating the original answer in full.

**Deliverable:** A concise repair decision procedure incorporated into the existing `op:repair` references.

**Quick check:** Give Claude a normal “I still don't get it” follow-up and a specific “you skipped step X” correction; inspect whether the responses differ meaningfully.

**Go/no-go:** Keep if the second attempt resolves the stated gap more directly than the frozen baseline.

---

## Phase 5 — Selective integration and regression check

**Goal:** Determine whether Approach B actually improves the skill and deserves production use.

**Implement**
1. Combine only the Phase 1–4 changes that passed their own checks; do not assume all must ship.
2. Use a **small, fixed set** of familiar situations: novice explanation, narrow expert question, short answer, decision, multi-turn follow-up, and repair.
3. Compare the frozen and experimental skills in actual Claude conversations. Automated scripts may check Markdown/structure, but cannot prove comprehension.
4. Check four outcomes: **better understanding**, **better relevance**, **no added verbosity**, and **no significant presentation regression**.
5. Record a brief decision: promote, partially promote, or discard. Document observed tradeoffs, not just success claims.

**Deliverable:** Candidate skill ZIP + compact comparison note + explicit promotion decision.

**Release gate:** Promote only when there is a **clear and repeatable qualitative advantage** on the target conversations, while preserving Approach A's strengths. Otherwise, keep the frozen baseline.

---

## Working loop for every phase

`Identify one communication failure → make one bounded change → try it in a real Claude chat → keep or revert`

The owner does **not** need to run 50 prompts, build a dataset, buy API credits, or manually score response batches. Existing tests and linters remain useful for catching technical regressions, but the key judgment is whether the resulting conversation is genuinely easier to understand.

## Scope boundaries

**In scope:** Skill text, supporting examples/references, selective offline regression checks, and packaging.  
**Out of scope:** Plugins, model fine-tuning, new agent orchestration, paid inference, heavy benchmark campaigns, external memory/database infrastructure, and any claim that presentation scores alone prove comprehension.

## Definition of success

A person receives an answer that starts from what they already understand, addresses the precise gap, uses the right amount of depth, adapts after feedback, and remains as readable as the frozen Approach A skill.

**Default outcome if uncertain:** Ship nothing new. Keep the successful baseline.
