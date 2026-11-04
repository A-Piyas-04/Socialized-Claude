# Development Report — Explanation Lab V0, and the state since

Date: 2026-10-26 (V0, §1–7). §8 brings it up to date on 2026-11-04.

> **Read §8 first for the current state.** §1–7 record V0 as it was built: the
> skill was then called `explanation-lab`, had five operations and three
> reference files, and shipped as `dist/explanation-lab.zip`. It is now
> `socialized` (Socialized-Claude), with thirteen operations and six references.

## 1. What was inspected

- **The research archive** `research-results-2026-10-26/`, every file:
  - the experiment 3, 4, and 5 reports and CSVs
  - all 60 Experiment 3 and 10 Experiment 4 raw transform records
  - the 5 study configs, 5 proxy results, and 5 proxy reports
  - the input dataset (5 questions, 30 imported answers) and study items
  - the before/after examples and the archive's scripts
- **The ExplanationLab repository**, public, `main` at `2548dfc`:
  - `transformations/strategies.py`, which holds the exact T1–T6 instruction
    templates. The archive contains only treatment names.
  - `transformations/fidelity.py` (detector rules)
  - `prompts/builtin.py` (the Experiment 2 tutor and pedagogical prompts)
  - `evaluation/rubrics.py` (judge dimensions)
  - `Docs/RESEARCH_FOUNDATIONS.md` (evidence levels, hypotheses H1–H5)
- **Anthropic documentation**, checked on 2026-10-26:
  - the Agent Skills overview
  - the authoring best practices
  - the Help Center article "How to create custom skills"
  - `anthropics/skills` → `skill-creator/scripts/quick_validate.py`

## 2. What was implemented

| Deliverable | Location |
|---|---|
| A. Installable skill | `dist/explanation-lab.zip` (+ `.manifest.json`) |
| B. Skill source | `skill/explanation-lab/SKILL.md`, `references/*.md` |
| C. Research audit | `research/EVIDENCE_AUDIT.md`, `research/recompute_archive_stats.py` |
| D. Evaluation framework | `evaluation/`: plan, rubric, conditions, 33 test cases, runbook, templates, comprehension protocol and item bank |
| E. Local validation | `scripts/validate_skill.py`, `scripts/package_skill.py`, evaluation scripts, `tests/` |
| F. Installation instructions | `docs/INSTALLATION.md` |
| G. This report | `docs/DEVELOPMENT_REPORT.md` |

Also included:

- `docs/ARCHITECTURE.md` and `docs/LIMITATIONS.md`
- `README.md` and `CHANGELOG.md`
- ablation variants via `package_skill.py --variant`

## 3. Why these treatments

Full reasoning is in `research/EVIDENCE_AUDIT.md` §6–8. In short:

- **T2 (dependency ordering) and T3 (mechanism) are the core operations.** They
  target the problems the brief describes. The evidence for both is weak, so
  they are adopted as hypotheses, not as proven techniques:
  - T2's 9/10 clean screen includes 4 unchanged outputs.
  - T3 had the worst fidelity record of the six, partly by construction, because
    its job is to add content under a "don't add content" constraint.
- **Each observed failure mode became an explicit guardrail:**

  | Treatment | Observed failure | Rule in the skill |
  |---|---|---|
  | T2 | 13 signposting phrases | No signposting |
  | T2 | One false "mutually dependent" claim | Never assert a dependency that is not real |
  | T2 | Naming prerequisites without teaching them | Teach a missing prerequisite, don't list it |
  | T3 | Certainty creep | Keep claims at their original strength |
  | T3 | Hedge loss | Preserve hedges |
  | T3 | Meta-commentary | No meta-commentary |
  | T3 | About 40% median length inflation | Length budget |

- **T6 (audience adaptation) became the calibration gate.** It decides how much
  of T2 and T3 to apply, which guards against the expertise-reversal risk.
- **T4 (examples) and T1 (terms) are conditional.**
- **T5 (structure) is deferred** to a single "format only for real shape" rule.
- **Not all six are stacked.** The prior "structured pedagogical" prompt did
  that and doubled median length, with no discriminating quality measure.

## 4. Discrepancies found in the preliminary findings

- **Experiment 4 is smaller than described.** It has 20 CSV rows but only 10 new
  rewrites; the other 10 rows reuse Experiment 3 runs.
- **Experiment 4 is not cross-model in the intended sense.** Both rewriters are
  Gemini models, and no Claude ↔ ChatGPT rewrite was run.
- **"Some T2 outputs made very limited changes" understates it.** 4/10 made no
  change at all, and T6 made no change in 6/10.
- **Most "serious concerns" for T4 and T5 are detector artifacts.** The numeric
  detector fires on list numbering and on illustrative example numbers.
- **One proxy difference is an artifact.** The "2/3 correct with quote" for TCP
  Claude comes from quote matching failing on an ellipsis.
- **The archive's word counters disagree.** For example, T5's median change is
  +31 in the CSV and +77.5 in the raw diff statistics.
- **The all-5/5 judge claim cannot be verified.** The judge outputs are not in
  the archive.
- **One candidate before/after example is unusable for review.** The databases
  example has identical before and after texts.

## 5. Tests run, and results

| Check | Result |
|---|---|
| `python -m pytest` | **172 passed** |
| `python scripts/validate_skill.py` (source) | Passed, 0 errors, 0 warnings |
| `python scripts/validate_skill.py dist/explanation-lab.zip` | Passed, 0 errors, 0 warnings |
| Anthropic `quick_validate.py` on the extracted production ZIP | "Skill is valid!" |
| Anthropic `quick_validate.py` on the extracted `seq` ablation ZIP | "Skill is valid!" |
| `python research/recompute_archive_stats.py` | Reproduces the archive's verdict counts; 0 CSV/JSON mismatches |
| `python scripts/package_skill.py --all-variants` | All 5 variants built and validated; builds are byte-identical across runs |
| `make_run_sheet.py` on the full suite with 5 conditions | 165 rows; messages checked by hand for B and follow-up formatting |

### Problems found during development (all fixed)

- **CRLF line endings.** The editor wrote CRLF on Windows. Files were
  normalized, `.gitattributes` now forces LF, and the packager normalizes
  regardless.
- **Case-insensitive `SKILL.md` check.** On Windows, the validator accepted a
  lowercase `skill.md` because the filesystem is case-insensitive. It now
  checks the exact name.
- **Leaky core wording.** The always-on core mentioned prerequisites and causal
  steps, which would have leaked those operations into the `core` and
  single-operation ablation variants. The wording was neutralized and the
  remaining lines tagged.
- **Verdicts on tiny samples.** The summary could report S6 as "MET" from 3
  cases. Criteria now report `INSUFFICIENT_DATA` below 10 cases or 6
  participants.
- **Answer key always first.** Every comprehension item stored the correct answer
  first. Option shuffling is now an explicit protocol rule, checked by a test.

## 6. What remains unverified

- **Upload, enabling, and activation in claude.ai have not been tried.** I had
  no access to a Claude account interface. Offline validation is not evidence
  that Claude loads or follows the skill.
- **Exact menu paths and eligibility are unconfirmed.** The menu paths ("Customize
  → Skills" vs "Settings → Features") and Free-plan eligibility differ between
  Anthropic's own documents.
- **Activation evidence may not be visible.** Whether the claude.ai interface
  shows skill loading clearly enough to record activation is unknown.
- **Any effect on explanation quality, accuracy, or length is unmeasured.**
- **Comprehension items are unscreened.** Their difficulty and ceiling risk are
  unknown.
- **Spreadsheet-edited files are untested.** The scripts were exercised with
  synthetic data only. Real rater files edited in Excel may raise formatting
  issues, which the validators should report.
- **The skill's factual examples were checked by me, not by domain experts.**

## 7. V0's next steps (superseded)

These were the steps for the V0 build. File names and counts are V0's; the
current steps are in §8.

1. **Install it.** Upload `dist/explanation-lab.zip` following
   `docs/INSTALLATION.md`. If the upload is rejected, run
   `python scripts/validate_skill.py dist/explanation-lab.zip` and record the
   error message. That result is criterion S1.
2. **Smoke test** in three new chats, with the activity panel expanded:
   - "Why does a metal spoon feel colder than a wooden one at room
     temperature?" (should load)
   - "Translate 'good morning' into German" (should not)
   - the same spoon question prefixed with `Use the explanation-lab skill for
     this.`

   For each, note whether `explanation-lab/SKILL.md` is shown being read. This
   tells you whether natural activation is measurable on your surface.
3. **Generate the reduced pilot:**
   `python scripts/make_run_sheet.py --run-id pilot16 --subset pilot16 --seed 1`.
   Then run `python scripts/run_assistant.py evaluation/runs/pilot16`, which
   copies each message and saves each response for you, while following the
   rules in `evaluation/RUNBOOK.md` §1–4 (64 responses).
4. **Validate the run:**
   `python scripts/summarize_results.py evaluation/runs/pilot16 --check-only`.
   Fix every reported gap.
5. **Blind it:**
   `python scripts/prepare_blind_packet.py evaluation/runs/pilot16 --raters r1,r2 --seed 7`.
   Two raters, ideally not you, score it using `evaluation/RUBRIC.md`.
6. **Summarize:** `python scripts/summarize_results.py evaluation/runs/pilot16`.
   Read `summary.md`. With only 16 cases, expect many `INSUFFICIENT_DATA`
   criteria. Treat this round as a test of the instruments and of activation.
7. **Run the full pilot** (33 cases) and then the comprehension item screening,
   in the order given in `evaluation/EVALUATION_PLAN.md`.

## 8. State on 2026-11-04 (build `fd6a5ce`)

### What changed since V0

| Stage | What it added | Recorded in |
|---|---|---|
| V1 | `op:structure` became `op:presentation`; new `register`, `repair`, `persistence`, `work-report`, `plain`; automated Claude Code collection; screening judge; 45 test cases; structural linter | `CHANGELOG.md`, `AGENTS.md` Decisions |
| Rename | Skill id `socialized`, display name Socialized-Claude; `pilot16-cc` stays frozen as `explanation-lab` | `AGENTS.md` Decisions |
| Visual depth | New `visual` and `close` operations | `CHANGELOG.md` |
| Upgrade Phases 1–4 | Space and hierarchy, a 13th operation `conversational`, the emoji palette, always-on "Markdown that renders", `lint_markdown.py` | `docs/SKILL_UPGRADE_PLAN.md` |
| V2 Phases 5–9 | Version stamp, render probe, strategy moved to methodology §15, the page shape, rule conflicts resolved, `layout-exemplars.md`, callout kinds, overview flowchart | `docs/SKILL_UPGRADE_PLAN_V2.md` |

### Checks, as of this date

| Check | Result |
|---|---|
| `python -m pytest -q` | **563 passed, 1 skipped** |
| `python scripts/validate_skill.py` (source) | Passed, 0 errors, 0 warnings |
| `dist/socialized.zip` | Byte-identical to a fresh build (SHA-256 `8e1a2c0a…`) |
| `SKILL.md` body | 485 of 500 lines (test guard 485); rendered full build 420 (guard 460) |
| Description | 164 characters (claude.ai limit 200) |
| Operations / variants | 13 / 16 |
| References | 6 files |

### What remains unverified

- **No evaluation has run.** The `pilot16-cc` automated run holds no
  responses, and no result of the Claude-only judge acceptance test is
  recorded.
- **The Phase 9 build has not been seen on claude.ai.** The last layout capture
  (round 5) used build `208b8aa`, before Phase 9.
- **Layout consistency is unmeasured.** Each round is one answer per prompt.
- **Rendering of `rect rgb(...)` in a `sequenceDiagram`** on claude.ai.
- **Anthropic's `quick_validate.py`** has not been re-run since V0.
- **Every V0 item in §6** still holds, except that upload and explicit
  invocation on claude.ai now work (layout rounds 2–5).

### Next steps

1. **Upload the current ZIP** to claude.ai and capture round 6 for the three
   prompts in `evaluation/layout_prompts.json`.
2. **Build Phase 10** of `docs/SKILL_UPGRADE_PLAN_V2.md`: an automated layout
   conformance score and before-and-after runs through `collect_cc`.
3. **Run the judge acceptance test** on Groq once `scripts/judge_capacity.py`
   shows it fits in about three days; the sweep waits until it passes.
