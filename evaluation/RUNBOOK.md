# Runbook — running the evaluation by hand in Claude

This procedure needs a normal Claude account and no API key. Nothing here
automates the Claude interface. Every message is sent by a person and every
response is copied by a person.

Allow about 3–5 hours of operator time for the 132-response pilot, and about
half that for the reduced `pilot16` run.

---

## 0. Before you start

1. **Account.** You need a Claude plan with Skills and code execution available.
   Anthropic's documentation lists custom Skills on Pro, Max, Team, and
   Enterprise. The Help Center article "How to create custom skills" also
   mentions Free. Check what your account shows. Code execution (file creation)
   must be enabled, because custom Skills depend on it.
2. **Tools on your computer.** Python 3.10+ and `pip install -r requirements-dev.txt`.
3. **Build and check the skill:**
   ```
   python scripts/validate_skill.py
   python scripts/package_skill.py
   ```
   Note the `zip_sha256` in `dist/socialized.manifest.json`. Every C row
   records it.
4. **Create the run sheet and message files:**
   ```
   python scripts/make_run_sheet.py --run-id pilot-2026-11-01 --seed 1
   ```
   This creates `evaluation/runs/pilot-2026-11-01/` containing:
   - `run_sheet.csv`: one row per response to generate, in randomized order
     within each batch
   - `messages/<row_id>.txt`: the **exact** text to paste for each row
   - `responses/`: empty, for you to fill

   Useful options:
   - `--subset pilot16` for the reduced pilot
   - `--samples 2 --subset variance12` for the sampling-variance round
   - `--conditions A_normal,B_prompt,C_skill,C_skill_explicit,D_skill_text` to add D

---

## 0b. Faster: let the run assistant handle the files (recommended)

Instead of opening each message file and creating each response file by hand
(§2 and §4), run:

```
python scripts/run_assistant.py evaluation/runs/pilot-2026-11-01
```

It asks once for your session settings: surface, model name, thinking setting,
and operator. Then, for each row, in run-sheet order:

1. It copies the exact message to your clipboard.
2. In Claude: **New chat** → **Ctrl+V** → **Enter**. Wait for the answer, then
   click the **copy** button under it.
3. Back in the terminal, press **Enter**. The assistant saves
   `responses/<row_id>.md` and fills the row's date, surface, model, thinking
   setting, and operator.
4. For skill rows, it also asks what you saw in the activity panel
   (`y`, `n`, or `u`).

At each batch boundary, it pauses and tells you to switch the skill off or on in
**Customize → Skills**. It continues only after you type `ok`.

Other commands at the `>` prompt:

| Key | Action |
|---|---|
| `c` | Copy the message again |
| `n <text>` | Add a note, e.g. `n regenerated once after a network error` |
| `s` | Skip the row for now |
| `q` | Quit |

Progress is saved after every row. Rerun the same command to continue. It
refuses to save if the clipboard still holds the message you sent, holds the
previous response, or is empty.

It never touches Claude's website. It only uses your clipboard and the files in
the run folder. The rules in §1–§4 (new chat per row, no regenerating, same
model) still apply. `--batch skill_off` or `--batch skill_on` limits a session to
one batch.

---

## 1. Keep everything except the condition constant

| Setting | Rule |
|---|---|
| Model | Select the **same model** in the model picker for every row. Write its label exactly as shown in `model_label`. |
| Extended thinking / effort | Same setting for every row. Record it in `thinking_setting`. |
| Surface | Use one surface (e.g. claude.ai in a desktop browser) for the whole run. |
| Memory | Turn memory off, or make sure it is in the same state for every row. Chats should not reference earlier chats. |
| Personal preferences / styles | Clear custom instructions in profile preferences, and use the default style. Otherwise identical for every row. |
| Projects | **Do not** use a Project. Project instructions and knowledge would contaminate every condition. |
| Other skills | Disable all other custom skills for the whole run. Leave Anthropic's built-in document skills at their default for every row. |
| Date | Finish each batch in one session. If the model changes or the interface announces an update mid-batch, stop and redo the batch. |

---

## 2. Batch `skill_off` (conditions A, B, and D)

1. Open the Skills settings. This is **Customize → Skills** in current
   interfaces; some versions show it under **Settings → Features**. Make sure
   `socialized` is **not enabled**. On the first run it is not uploaded
   yet, which is fine.
2. For each `skill_off` row of `run_sheet.csv`, in order:
   1. Start a **new chat**. Never reuse a chat between rows.
   2. Open `messages/<row_id>.txt`, copy the whole content, paste it as the
      first message, and send it.
   3. When the response finishes, copy it with the response's copy button (this
      keeps Markdown) and save it as `responses/<row_id>.md`.
   4. Fill in the row: `date`, `model_label`, `thinking_setting`,
      `surface`, `operator`, and `activation_observed = na` for A, B, and D.
   5. Note anything unusual in `notes`: an error, a regenerated response, or a
      refusal. **Never regenerate** to get a "better" answer. If a response
      fails technically (a network error), regenerate once and note it.

---

## 3. Install the skill (first time only)

1. Go to **Customize → Skills** (or **Settings → Features**) and upload
   `dist/socialized.zip`.
2. If the upload fails, record the exact error message. Criterion S1 has failed,
   so stop and see `docs/INSTALLATION.md` → Troubleshooting.
3. Enable `socialized`. Check that no other custom skill is enabled.

---

## 4. Batch `skill_on` (conditions C_skill and C_skill_explicit)

Repeat the §2 procedure for each `skill_on` row, with one addition.

**Record activation evidence before copying the response:**

| What you see | `activation_observed` | `activation_evidence` (examples) |
|---|---|---|
| The tool-activity or thinking panel shows Claude reading `socialized/SKILL.md` or naming the skill | `yes` | "Tool panel: read socialized/SKILL.md" |
| A reference file under `socialized/references/` is also read | `yes`, and list the files in `references_loaded` | "Also read references/explanation-examples.md" |
| No visible sign of the skill being loaded | `no` | "No tool activity shown" |
| Something ambiguous (collapsed panel, unclear label) | `unclear` | Describe what you saw |

Rules:

- **Do not ask Claude whether it used the skill**, in the same chat or a new
  one. The question changes the conversation, and the answer is self-report,
  not evidence.
- Expand the activity or thinking panel if the interface collapses it. The
  Help Center's own advice for checking activation is to "review Claude's
  thinking".
- Interfaces differ in what they show. If your interface never shows skill
  loading, record `unclear` and say so in `notes`. Activation then cannot be
  measured on that surface, and the analysis must rely on `C_skill_explicit`.

**Why this matters.** A `C_skill` response that looks like the A response may
simply mean the skill was not loaded. That is an **activation failure**, not a
failure of the explanation method. The summary separates the two using this
column.

---

## 5. Ablation batches (later rounds only)

For each variant (`core`, `seq`, `mech`, `seq-mech`, `full`):

1. Build it with `python scripts/package_skill.py --all-variants`. The ZIPs go to
   `dist/ablation/`.
2. In Skills settings, **delete** the currently installed `socialized`, then
   upload `dist/ablation/socialized--<variant>.zip` and enable it. All
   variants share one name, so only one can be installed at a time.
3. Run that variant's rows (`batch = variant:<variant>`). Record the variant's
   `zip_sha256` from `dist/ablation/socialized--<variant>.manifest.json`.
4. After the last variant, reinstall the production `dist/socialized.zip`.

---

## 6. Check completeness

```
python scripts/summarize_results.py evaluation/runs/pilot-2026-11-01 --check-only
```

This lists missing response files, unfilled required columns, and invalid
values. Fix every problem before blinding.

---

## 7. Blind the responses

```
python scripts/prepare_blind_packet.py evaluation/runs/pilot-2026-11-01 --raters r1,r2 --seed 7
```

This creates `evaluation/runs/pilot-2026-11-01/blind/`:

- `packet/<case_id>.md`: one file per case, with the question, context,
  audience, reference facts, and the responses in random order under blind IDs
  only
- `ratings/ratings_r1.csv`, `ratings/ratings_r2.csv`: one row per blind ID,
  pre-filled with the IDs, for each rater
- `blind_key.csv`: maps blind IDs to conditions. **Keep this away from raters**
  until rating is finished.
- `blinding_warnings.txt`: responses that mention the skill or other
  condition-revealing text. Do not edit responses. Rate them as they are; the
  mention is itself an `INTERNAL_LABEL` violation.

Give raters `packet/`, their own ratings CSV, and `RUBRIC.md`. Nothing else.

---

## 8. Rate

Each rater:

1. Does the calibration step in `RUBRIC.md`.
2. For each case file, reads the question and audience, then scores every
   response in their ratings CSV according to `RUBRIC.md`.
3. Returns the CSV unchanged apart from the filled cells.

---

## 9. Summarize

```
python scripts/summarize_results.py evaluation/runs/pilot-2026-11-01
```

This writes `summary.md` and `summary.json` into the run folder. They contain:

- completeness and agreement diagnostics
- activation, adherence, accuracy, and length tables
- dimension means
- paired comparisons with bootstrap intervals
- the S1–S7 criteria table

S1 comes from your notes, and S7 comes from the comprehension study; both must
be entered manually.

---

## 10. What to store

Keep the whole `evaluation/runs/<run_id>/` folder. It contains the raw
responses, the run sheet, the blind key, and the ratings. Commit it, or archive
it with the skill version (`zip_sha256`) it tested. Remove anything personal
from `notes` before sharing.
