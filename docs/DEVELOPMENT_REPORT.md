# Development Report — Explanation Lab V0

Date: 2026-10-26.

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

## 7. Exactly what to do next to test the skill in Claude

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
