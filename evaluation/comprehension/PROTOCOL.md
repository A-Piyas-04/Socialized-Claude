# Human Comprehension Pilot — Protocol

**Purpose.** Measure whether people **understand more** after reading an
explanation from each condition, using questions that require the explained
mechanism.

**Status: designed, not run.** No participant data exists. Do not report any
result from this protocol until it has actually been carried out.

## 1. Why this design (and what it fixes)

The earlier AI-proxy study (`research/EVIDENCE_AUDIT.md` §2.4) failed for two
reasons:

- **Its items were recall-level.** The proxy answered all 15 items correctly
  without reading any explanation, so 0 items could detect a difference.
- **It used no human learners.** An AI model answering questions shows what the
  text supports. It does not show that a reader learned.

This protocol addresses both:

1. **Human participants.**
2. **A pre-test**, so each topic's ceiling is measured per person.
3. **Mechanism items.** Items require prediction, transfer to a new situation,
   or correcting a misconception, rather than repeating a term.
4. **Topics novices rarely know** (`ITEM_BANK.json`), checked by an
   item-screening step **before** any explanation is generated.
5. **A within-participant Latin square.** Every participant reads one
   explanation per condition, each on a different topic. That avoids exposing
   anyone to two versions of the same explanation, which would cause carryover.

## 2. Conditions and stimuli

| Condition | How the explanation is produced |
|---|---|
| `A_normal` | Topic's `stimulus_question` sent as in `BASELINE_INSTRUCTIONS.md`, condition A |
| `B_prompt` | Same, condition B |
| `C_skill_explicit` | Same, explicit-invocation condition with the skill installed |

**Explicit invocation** is used so the study tests the explanation method rather
than activation reliability.

Generate the stimuli **once**, using `make_run_sheet.py` (one sample per topic ×
condition, following the `RUNBOOK.md` procedure), and freeze them. Each
participant sees the same frozen text for a given topic and condition.

Present stimuli as plain text with the original Markdown rendered. Remove nothing
except interface chrome. Record each stimulus's word count. Length differences
are part of the condition and are reported, not equalized.

## 3. Item screening (before generating stimuli)

1. Recruit 4–6 people from the same population as the participants. They will
   not take part in the pilot.
2. Give them **only** the pre-test and post-test multiple-choice items for all
   three topics, with no explanation.
3. Revise or drop any item answered correctly by more than about 60% of
   screeners, and any item whose distractors nobody picks. Record every change
   in a screening log.
4. **Freeze the item bank** (record its file hash). Items must not be edited after
   stimuli are generated or read.

## 4. Participants

- **Pilot size.** 12 or 18 adults: multiples of 6, so the counterbalancing
  sequences are used equally often.
- **Eligibility.** No formal training in physics or engineering, which cover
  all three topics. Ask about this in the familiarity question.
- **Consent.** Obtain informed consent. Follow your institution's requirements
  for human-participant research. Collect no identifying information in the
  result files; use participant codes (`P01`, `P02`, …).
- **Compensation and setting.** Use the same for everyone. Sessions take about
  35–45 minutes.

## 5. Assignment (Latin square)

```
python scripts/assign_comprehension.py --participants 18 --seed 3 --out evaluation/runs/<run_id>/comprehension/assignment.csv
```

The script cycles through the 6 orderings of the 3 conditions and rotates topic
order, so each condition appears equally often with each topic and in each
position. Participants are assigned in order of arrival.

## 6. Session procedure

**Shuffle the answer options** of every multiple-choice item when presenting it.
`ITEM_BANK.json` stores the correct option first for authoring convenience, so
presenting the stored order would give the answer away. Either shuffle per
participant, or fix one random order per item and record it in the screening log.
The experimenter scores against the item's key, so shuffling does not affect
`responses.csv`.

For each participant, in their assigned order of 3 topics:

1. **Familiarity.** "How familiar are you with how [topic] works?" (1 = not at
   all, 5 = could explain it to others).
2. **Pre-test.** The topic's 3 `pre` items, without an explanation. No feedback.
3. **Exposure.** Show the assigned explanation. No time limit; record reading
   time. The participant presses "continue" when done and **cannot return**.
4. **Post-test.** The topic's 4 `post` multiple-choice items in a fixed order,
   then the `explain` free-text item **last**. Free-text explanation is itself a
   learning activity (self-explanation), so placing it after the multiple-choice
   items keeps it from affecting them.
5. **Confidence.** "How well do you now understand how [topic] works?" (1–5).
6. **Perceived clarity.** "How clear was the explanation?" (1–5). This is
   recorded so it can be compared against comprehension, not as a substitute for
   it.

After all 3 topics, record any technical problems.

**Optional delayed test.** After 2–7 days, readminister the `post` items and the
`explain` item without the explanation. Record the delay in days.

## 7. Scoring

- **Multiple-choice items.** 1 if correct, 0 otherwise. Wrong answers also
  record the misconception tag from `ITEM_BANK.json`.
- **`explain` items.** Scored 0–2 using the item's rubric by **two graders blind
  to condition**. A different person hands them shuffled answers with condition
  removed. Report agreement, and resolve disagreements by discussion. The
  resolved score is the analysed score.
- **Per participant × topic, `summarize_results.py` computes:**
  - `pre` (0–3) and `post_mc` (0–4)
  - `transfer` (post items typed `transfer`) and `misconception` (post items
    typed `misconception`)
  - `explain` (0–2)

## 8. Analysis (pre-specified)

Each participant has one score per condition, on different topics. For each
participant, `summarize_results.py` computes the within-participant contrasts
C − B and C − A on:

| Outcome | Status |
|---|---|
| Transfer + misconception items, post-test | **Primary** |
| `explain` score | Secondary |
| Post − pre proportion correct | Secondary |
| Delayed post-test, if collected | Secondary |

It reports the mean contrast, a 95% bootstrap interval over participants, and the
number of participants with a positive, zero, or negative contrast. Per-topic
condition means are reported too, because topic and condition are only partly
separable at this sample size.

Also reported (descriptive):

- confidence and perceived clarity by condition, and their correlation with
  scores. **If clarity ratings favour a condition that does not show better
  comprehension, report that as a finding.**
- reading time and stimulus length by condition.

**Exclusions** (decided now, applied blind to condition):

- A topic for a participant whose pre-test is 3/3 is excluded from the
  gain-score analysis because of the ceiling. It stays in the post-test
  analysis. The count is reported.
- Reading time under 15 seconds for a stimulus over 150 words is flagged as
  inattentive and excluded from that topic's analysis. The count is reported.

**Interpretation.** With 12–18 participants and 3 topics, this pilot can show
the **direction** and rough size of an effect, and whether the instruments work
(no ceiling, sensible item difficulty, grader agreement). It cannot establish
superiority. A positive pilot justifies a properly powered study. It does not
justify claiming that the skill improves comprehension.

## 9. Files

| File | Template | Contents |
|---|---|---|
| `assignment.csv` | generated by `assign_comprehension.py` | participant × position × topic × condition |
| `exposure.csv` | `EXPOSURE_TEMPLATE.csv` | familiarity, reading time, confidence, clarity, flags |
| `responses.csv` | `RESPONSES_TEMPLATE.csv` | one row per participant × item, with score |

Put these in `evaluation/runs/<run_id>/comprehension/`. `summarize_results.py`
picks them up automatically.
