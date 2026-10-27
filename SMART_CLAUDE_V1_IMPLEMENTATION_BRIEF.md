# Implementation Brief — Smart-Claude V1

**Audience:** AI coding agent with full write access to the `smart-claude` repository.
**Date:** 2026-10-27.
**Mode:** Implementation only. No human experiments, no manual response collection, no data-gathering tasks of any kind are to be requested of the user. Every claim this work makes must be checkable by running a command in the repo.

---

## 0. How to read this brief

Work in two tracks. **Track A is required and must be completed and green before Track B is started.** Track B is a separate deliverable in a separate directory and must not import from or modify Track A's code.

Do not re-derive the facts in §1. They were established by direct inspection of the repository and are given so you do not spend turns rediscovering them.

Do not write new strategy, research-direction, or methodology documents. Two already exist (`research/EVIDENCE_AUDIT.md`, `SMART_CLAUDE_COMMUNICATION_DIRECTION.md`) and the project's failure mode to date has been producing principles faster than evidence. Produce code, skill text, tests, and the two artifact files named in A6.

---

## 1. Ground truth about the repository

Read these before editing. They are accurate as of this brief.

**Layout**

```
skill/explanation-lab/SKILL.md            200 lines, 5 operations, op-marker tagged
skill/explanation-lab/references/         explanation-methodology.md,
                                          explanation-examples.md,
                                          treatment-selection.md
scripts/skilllib.py                       OPERATIONS, VARIANTS, marker parsing, validation rules
scripts/package_skill.py                  builds dist ZIPs, --variant / --all-variants
scripts/validate_skill.py                 structural validation of source and ZIP
scripts/summarize_results.py              run validation + summary
scripts/make_run_sheet.py                 run-sheet generation
evaluation/conditions.json                machine-readable mirror of BASELINE_INSTRUCTIONS.md
evaluation/TEST_CASES.json                33 cases, 10 categories
evaluation/RUBRIC.md                      9 dimensions + critical-fact coding + adherence codes
research-results-2026-10-26/inputs/input-dataset.json
                                          5 questions, 30 imported answers (the only response corpus)
tests/                                    172 passing tests
```

**Key constants in `scripts/skilllib.py`**

```python
OPERATIONS = ("sequencing", "mechanism", "examples", "terms", "structure")   # line 21
VARIANTS = {"full", "core", "seq", "mech", "seq-mech"}                       # line 24
MARKER_RE = r"^\s*<!--\s*(/?)op:([a-z,\-]+)\s*-->\s*$"                       # line 41
DESCRIPTION_MAX_CLAUDE_AI = 200
BODY_MAX_LINES = 500          # SKILL.md is at 200; there is room
TOC_REQUIRED_OVER_LINES = 100
```

**Invariants you must not break**

- `tests/test_evaluation_schema.py` asserts `evaluation/conditions.json` and `evaluation/BASELINE_INSTRUCTIONS.md` stay identical in content. Edit both or neither.
- `package_skill.py` builds must stay byte-identical across runs. Do not introduce timestamps, dict-ordering dependence, or unsorted globs.
- Every op-tagged block must have a matching close marker; `skilllib.py` already rejects malformed ones and a test covers it.
- Skill `description` must stay ≤ 200 characters.

**What the evidence actually supports** (from `research/EVIDENCE_AUDIT.md`, verified)

- T2 (sequencing) and T3 (mechanism) are included as *hypotheses*, not proven techniques. Keep them.
- T5 (structure) was deferred because 8 of its 10 "serious" verdicts were a numeric detector firing on list numbering — a detector artifact, not a quality finding. **The deferral rested on an artifact.** That is the justification for Track A.
- No comprehension evidence exists for anything. Do not write text or comments that imply otherwise.

---

# TRACK A — Skill V1

Goal: turn presentation from a suppressed non-operation into a first-class, ablatable operation, and add the two behaviours the user-complaint corpus shows matter and the current skill does not address: register calibration and conversational repair.

## A1. Add three operations to the operation system

In `scripts/skilllib.py`:

```python
OPERATIONS = (
    "sequencing", "mechanism", "examples", "terms",
    "presentation",   # replaces "structure"
    "register",
    "repair",
)

VARIANTS: dict[str, frozenset[str]] = {
    "full":          frozenset(OPERATIONS),
    "core":          frozenset(),
    "seq":           frozenset({"sequencing"}),
    "mech":          frozenset({"mechanism"}),
    "seq-mech":      frozenset({"sequencing", "mechanism"}),
    "pres":          frozenset({"presentation"}),
    "seq-pres":      frozenset({"sequencing", "presentation"}),
    "seq-mech-pres": frozenset({"sequencing", "mechanism", "presentation"}),
    "reg":           frozenset({"register"}),
    "rep":           frozenset({"repair"}),
}
```

Rename `op:structure` → `op:presentation` throughout `SKILL.md` and `references/treatment-selection.md`. Keep the rename mechanical and separate from the content rewrite in A2 — do them as two commits so the diff is reviewable.

Mirror the new variants into `evaluation/conditions.json` as `V_pres`, `V_seq_pres`, `V_seq_mech_pres`, `V_reg`, `V_rep`, following the exact shape of the existing `V_*` entries, and add the matching rows to `evaluation/BASELINE_INSTRUCTIONS.md`. Add the useful contrasts to the `comparisons` array: `["V_pres","V_core"]`, `["V_seq_pres","V_seq"]`, `["V_seq_mech_pres","V_seq_mech"]`.

## A2. Rewrite the presentation operation

**Delete these four instructions.** They are the reason the skill suppresses structure:

| File | Text to remove |
|---|---|
| `SKILL.md` ~139 | "Default to connected prose for explanations." |
| `SKILL.md` ~143–144 | "A bulleted list of facts with the connections removed explains less than two connected sentences." |
| `SKILL.md` ~141–142 | "…and headings only in long answers with distinct parts." |
| `SKILL.md` ~184 | "Avoid 'What / Why / How' headings unless the content really divides that way." |

**Write the replacement as positive operations, not permissions.** The failure of the old block is that every line was a prohibition, so the model's cheapest compliant output was unbroken prose. The new block must tell the model what to *do*. Cover:

- **Answer first.** The direct answer to the question asked occupies the opening, before any structure. Structure never delays the answer.
- **One idea per unit.** A unit is a short paragraph, a row, or a step. When a second idea starts, a new unit starts.
- **Match the form to the shape of the content.** A process gets visually distinguishable stages with the transition between them stated. A comparison across shared dimensions gets aligned rows. A set of coordinate terms gets a labelled list. A single causal chain stays as connected prose — prose is one of the forms, not the default and not the fallback.
- **Make the moving parts visible.** For a flow with branching, an ASCII diagram in a fenced block beats three paragraphs describing the same branch.
- **Emphasis marks the load-bearing sentence**, and is used at most once or twice per response.
- **Headings are allowed in medium-length answers** whenever the answer has more than one distinct part, and should say what the section establishes rather than naming a generic category.

**Keep exactly one constraint from the old block**, and state it as the operation's own guardrail rather than as a reason to avoid structure:

> Structure shows the shape of an explanation; it does not create one. A list whose items have no stated relationship to each other has removed the explanation and kept the facts. If splitting content into units loses a causal link, state the link inside the unit.

Add the anti-pattern that the new operation can produce, in the same style as the existing failure-mode list: **decorative structure** — headings over one-sentence sections, bullets for prose, a table with one meaningful column, bolding so frequent that nothing stands out.

In `references/treatment-selection.md` §3, the cut-order currently ends `… an example → Formatting`. Move presentation **above** examples and add one line: presentation costs few words, so it is cut last, not first. Remove the §4 failure-mode entry "Formatting presented as clarity" and replace it with the decorative-structure entry above; the old wording asserted a comprehension finding the project does not have.

## A3. Add the register operation

This targets the most-cited complaint in the project's user-evidence corpus: there is no middle setting between invented jargon and over-simplification.

New `op:register` block in `SKILL.md`. Content:

- Three registers exist, not two: **beginner** (no field vocabulary assumed, terms taught at first use), **practitioner** (field vocabulary used freely, no teaching, no analogies), **expert** (precise, terse, assumes the literature). Default to practitioner when signals are mixed or absent, because it is the register that is currently missing.
- Infer the register from the vocabulary the person uses, the code or material they share, and their stated background — never from the topic's difficulty.
- "Explain simply" means *drop assumed background*, not *switch to a childish analogy*. Keep the real terms and teach them.
- Use the field's own established term. Do not coin a new phrase for a concept that already has a name, and do not substitute a vague paraphrase for a term the reader will meet again.
- Do not name scholars, papers, or foreign-language terms without saying what they mean in the same sentence.
- Never open by characterising what the person thinks or assumes. Answer what they asked.

That last rule is not stylistic padding: the corpus shows "your base idea is right, but not for the reasons you think" as a specific, repeatedly-named irritant. Phrase it as a concrete prohibition on that construction.

## A4. Add the repair operation

Targets the follow-up/clarification failure. New `op:repair` block in `SKILL.md`:

- When the person clarifies, corrects, or pushes back, the first move is to re-read the original request under the new information and ask whether the earlier interpretation was wrong. Re-interpret before defending.
- If the earlier reading was wrong, say what the request actually asked for and answer that. Do not re-deliver the previous answer with different wording.
- Repair the specific gap, not the whole topic. A follow-up is not a request to re-explain from the start.
- When the person reports a mistake, state what was wrong and give the corrected content. Do not catalogue the error, do not count prior occurrences, and do not promise future behaviour.
- When a correction is genuinely contested, say so in one clause and give the reason — do not simply concede, and do not escalate.

## A5. Extend the rubric and the test set

`evaluation/RUBRIC.md` — add two dimensions in the existing anchored 1/3/5 format:

- **`navigability`** — can a reader find the part of the answer they need without reading it linearly? 1 = undifferentiated block; 5 = the structure of the content is visible at a glance.
- **`register_fit`** — is the technical level matched to this reader? 1 = invented jargon, unexplained name-drops, or condescension; 5 = the reader's own level, correct field terms, nothing talked down.

Add a short section **"Preference versus comprehension"** to the rubric's general rules. State plainly: dimension scores and within-case ranks are preference-class measures; the critical-fact coding in §B is the comprehension-class measure; presentation changes are expected to move the first; a presentation change counts as a regression if it moves the second downward. Raters score both and the two are never averaged together.

`evaluation/TEST_CASES.json` — add cases, preserving the existing schema exactly (`id`, `category`, `domain`, `difficulty`, `question`, `context`, `audience`, `skill_expectation`, `expected_length`, `expected_properties`, `common_misconceptions`, `critical_facts`, `reasoning_gaps`):

- 3 new `register` cases: the same underlying question posed by an evident beginner, an evident practitioner, and an evident expert. The practitioner case is the discriminating one.
- 3 new `repair` cases, each a two-turn case where turn two contradicts the interpretation turn one would naturally take.
- 2 new `decorative_structure` negative controls: questions whose honest answer is two sentences of prose, where any heading or bullet is a failure. These exist to catch over-application of the new presentation operation and are as important as the positive cases.

Update `tests/test_test_cases.py` so the new categories are recognised and the schema check still passes across all cases.

## A6. Build the two artifact files — from data already in the repo

These are the files the direction document asked for. Build them **only** from material already present, with no new collection.

**`COMMUNICATION_EXEMPLARS.md`** — paired weak/better explanations. Sources, in order of preference:

1. The 10 base answers in `research-results-2026-10-26/inputs/input-dataset.json` (5 questions × 2 providers). These are the only real paired responses in the project.
2. `research-results-2026-10-26/examples/candidate-before-after.md`. **Skip the databases pair** — before and after are byte-identical (similarity 1.000) and it is unusable.
3. Newly written pairs, clearly labelled as constructed, where the archive has no case covering a needed situation (register, repair, and the negative controls will all need this).

Each exemplar carries: the request, the weak version, the better version, and **one sentence naming the single difference that matters**. Cover the different situations — process, comparison, single causal chain, short factual, follow-up repair — and include at least two exemplars where the better version is *less* structured than the weak one. Without those, the file teaches "add structure" rather than "match structure to shape."

**`COMMUNICATION_GRAMMAR.md`** — the rules implemented in A2–A4, each carrying the project's existing evidence label (`Observation` with a file path / `Literature (L2)` / `Hypothesis (L4)` / `Engineering choice`). Be strict: most presentation rules are **L4 hypotheses**, and the file must say so. Do not label anything a validated finding. This file documents the skill; it does not argue for it.

## A7. Replace human evaluation with an offline structural linter

Since no runs will be collected, the only automatable feedback loop is static analysis of response text. Build it honestly and label it honestly.

New `scripts/structural_metrics.py`. Pure functions over a markdown string, no model calls, no network:

```
word_count, block_count, mean_block_words, max_block_words,
heading_count, bullet_count, numbered_count, table_count,
code_block_count, emphasis_count, mean_sentence_words,
answer_first_offset        # words before the first sentence that is not a restatement
                           # of the question; heuristic, document it as such
decorative_structure_flags # headings with <2 sentences; tables with <2 data columns;
                           # bullet runs where no item contains a connective
                           # (because/so/therefore/which means/if)
```

New `scripts/lint_response.py` — CLI over a file or stdin, emitting the metrics plus flags, with a `--json` mode and a non-zero exit on any decorative-structure flag.

Wire it into `scripts/summarize_results.py` as an additional automated table, placed under the existing §9 "Optional automated checks" framing. **Keep that section's existing disclaimer verbatim and extend it:** these are structural descriptors, not a comprehension score. A response can score perfectly on every metric here and still be wrong, and the linter cannot tell. Do not let the linter's output feed any S1–S7 criterion.

Add `tests/test_structural_metrics.py` with hand-written fixtures covering each metric and each flag, including negative cases (a legitimately prose-only answer must produce zero flags).

Regenerate the baseline metrics for the 10 archive answers into `research/baseline_structural_metrics.json` via a `--regenerate` flag, so future skill text changes have something to compare against.

## A8. Validate, package, document

```bash
python -m pytest                                    # must stay green, now >172
python scripts/validate_skill.py                    # 0 errors, 0 warnings
python scripts/package_skill.py --all-variants      # all 10 variants build and validate
python scripts/validate_skill.py dist/explanation-lab.zip
python scripts/lint_response.py --help
python research/recompute_archive_stats.py          # must still reproduce; do not touch the archive
```

Check `SKILL.md` stays under `BODY_MAX_LINES` (500) and that the table of contents requirement triggered above 100 lines is satisfied. Check the description stays ≤ 200 characters; if you revise it, keep the trigger phrases ("how does", "why does", "explain", "understand", "confused") since activation depends on description matching.

Update `CHANGELOG.md` and `docs/ARCHITECTURE.md` for the new operations and variants. In `docs/LIMITATIONS.md`, add one entry: the presentation, register, and repair operations are untested hypotheses, and the structural linter measures form only.

## A9. Track A definition of done

- `OPERATIONS` has 7 entries; `VARIANTS` has 10; all build and validate.
- No prohibition-only phrasing remains in the presentation block.
- `conditions.json` and `BASELINE_INSTRUCTIONS.md` agree; schema test passes.
- 41 test cases (33 + 8), all schema-valid.
- `RUBRIC.md` has 11 dimensions and the preference/comprehension section.
- `COMMUNICATION_GRAMMAR.md` and `COMMUNICATION_EXEMPLARS.md` exist, every rule labelled, no unlabelled claims.
- Linter exists, tested, wired in, correctly disclaimed.
- Full test suite green; packaging reproducible across two consecutive runs (diff the ZIP hashes).

---

# TRACK B — Browser extension (start only after A9)

## B1. Scope honestly, then build

A local extension can restyle text. It cannot build information architecture out of a wall of prose, because deciding that three sentences are a sequence and the fourth is an aside requires understanding the content. **Build the readability layer and the diagnostic view. Do not build a "restructurer" and do not claim one.**

Directory: `extension/`. Nothing in it imports from `scripts/`. It is a separate deliverable with its own `README.md` and its own tests.

## B2. MVP

Manifest V3, content script on `claude.ai`, no remote code, no network requests, no analytics, no data leaving the browser. State in `chrome.storage.local` only.

Features, in build order:

1. **Typographic readability layer.** Measured max line length, paragraph spacing, and a setting for maximum paragraph length that visually splits over-long paragraphs at sentence boundaries without altering text. Toggle on/off, off by default, per-site persisted.
2. **Response outline.** Derive a jump list from the rendered headings of a response and show it as a sidebar for responses over a length threshold. Pure navigation over structure the model actually produced. If a response has no headings, show nothing — do not invent them.
3. **Density diagnostic.** Port the metrics from `scripts/structural_metrics.py` to TypeScript, share the fixtures so both implementations are tested against the same expected outputs, and show a small badge: word count, longest paragraph, reading time, decorative-structure flags. This is the one feature that produces information the user does not already have.
4. **Re-ask counter.** Count, per conversation, how many user turns are clarifications or re-requests (heuristic: short turn, within N seconds of the previous response, matching a re-ask pattern). Store locally, display in the badge. This is the closest thing to a real quality signal that can be collected without any manual work.

## B3. Explicitly out of scope

- Any rewriting of response content, including "reformat this response."
- Any automated sending of messages to Claude on the user's behalf.
- Any DOM write that would survive as text if the user copied the response.
- Any network call whatsoever.

Selectors against a shipping web app break. Isolate every selector in one `selectors.ts` module with a documented fallback path and a feature-detection guard, so breakage degrades to doing nothing rather than to a broken page.

## B4. Track B definition of done

- Loads unpacked in Chrome, no console errors on a normal conversation.
- Every feature individually toggleable and off by default.
- TypeScript metrics and Python metrics produce identical output on the shared fixture set, enforced by a test.
- `extension/README.md` states plainly what the extension does and does not do, including that it cannot restructure content.

---

## Out of scope for both tracks

- Any task that asks the user to run prompts, copy responses, rate outputs, or recruit participants.
- Any LLM-as-judge pipeline. `evaluation/EVALUATION_PLAN.md` §7 bars it from the success criteria; do not add one through the back door as a "linter."
- Editing anything under `research-results-2026-10-26/`. It is the archive and must stay immutable; `recompute_archive_stats.py` must keep reproducing.
- Deleting `research/EVIDENCE_AUDIT.md` or weakening its claims. It is the project's standard of evidence.

## Commit sequence

1. `refactor: rename op:structure to op:presentation` (mechanical, no content change)
2. `skill: rewrite presentation as a positive operation`
3. `skill: add register calibration operation`
4. `skill: add conversational repair operation`
5. `build: add presentation, register, repair variants`
6. `evaluation: add navigability and register_fit, preference/comprehension split`
7. `evaluation: add register, repair, and decorative-structure cases`
8. `docs: add COMMUNICATION_GRAMMAR and COMMUNICATION_EXEMPLARS`
9. `tools: add structural metrics and response linter`
10. `docs: update changelog, architecture, limitations`
11. Track B, its own series.

## The one thing to get right

The previous version failed by telling the model what not to do, and the cheapest way to comply was to do nothing. Every rule you write in Track A must name an action the model takes. If a rule can be satisfied by writing an undifferentiated paragraph, it is written wrong — rewrite it.