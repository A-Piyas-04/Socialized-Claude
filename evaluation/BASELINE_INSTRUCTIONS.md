# Condition Configurations

This document defines exactly what each condition sends to Claude and through
which product mechanism. Copy instruction text **exactly**. The surrounding
procedure is in `RUNBOOK.md`.

## Summary

| Condition | Label in results | Explanation-specific content | Mechanism | Skill state |
|---|---|---|---|---|
| A. Normal Claude | `A_normal` | None | Plain question in a new chat | `socialized` **disabled** |
| B. Optimized prompt | `B_prompt` | Baseline instruction below | Pasted above the question, same message | `socialized` **disabled** |
| C. Skill, natural | `C_skill` | Skill only | Plain question; Claude decides whether to load the skill | `socialized` **enabled** |
| C. Skill, explicit | `C_skill_explicit` | Skill only | One fixed invocation line above the question | `socialized` **enabled** |
| D. Skill text as prompt (optional) | `D_skill_text` | The skill's instructions pasted as text | Pasted above the question, same message | `socialized` **disabled** |

In every condition, all other custom skills are disabled, memory and personal
preferences are off (or identical across conditions), the same model is
selected, and the extended-thinking setting is the same.

## Why these conditions

- **A vs C_skill** asks whether the installed skill changes ordinary use.
- **B vs C** asks whether the skill beats a serious, carefully written generic
  instruction. This is the comparison that matters most. Beating only A could
  mean that *any* explanation instruction helps.
- **C_skill vs C_skill_explicit** separates **activation** from **methodology**.
  If C_skill_explicit beats B but C_skill does not, the methodology may work but
  automatic loading is failing.
- **D vs C_skill_explicit** separates the skill's *content* from the skill
  *mechanism* (progressive disclosure, reference files loaded on demand). It is
  optional for the first pilot.

### Fairness note: product mechanisms differ

The skill's description sits in Claude's context from the start, and its body is
loaded only if Claude decides to read it. The B instruction is user-message text
that Claude always sees. A user-turn instruction is, if anything, a **stronger**
intervention than an optional skill, so B is a conservative baseline: it favours
B, not C. Record the mechanism with every result. Do not compare C_skill with B
without also reporting C_skill_explicit.

---

## Condition A — exact message

```
{question}
```

For follow-up cases, see the follow-up format below.

---

## Condition B — exact message

The baseline covers the same ideas as the skill (prerequisites, mechanism,
examples when helpful, calibrated length, accuracy), stated as a competent
generic instruction. This tests whether the skill's operational detail and
selectivity add anything beyond stating the same goals plainly. It deliberately
avoids the failure modes of weaker baselines: it does not ask for "simple
language" (risking patronizing output), and it does not mandate steps (risking
inflated length).

```
When you answer, explain in a way that helps me genuinely understand, not just
in a way that is correct:
- Work out what I'm actually asking and answer that directly.
- If the explanation depends on ideas I may not know, introduce them briefly
  before you use them, and skip what I clearly already know.
- For "why" or "how" questions, explain the cause and effect: what happens, why,
  and what follows from it.
- Use a concrete example only if it genuinely helps, and connect it to the idea.
- Match the length and depth to my question. Don't pad, and don't add
  unnecessary detail.
- Stay accurate. Keep any uncertainty or caveats that matter.

{question}
```

### Optional comparison baseline: B2 (prior research prompt)

To stay continuous with the earlier ExplanationLab study, the Experiment 2
"structured pedagogical" prompt (repository `prompts/builtin.py`,
`CONDITION_C_SYSTEM`) can be run as `B2_research_prompt`. Fill its learner-profile
fields from the case's `audience` field. That prompt is known to roughly double
answer length (`research/EVIDENCE_AUDIT.md` §2.1), so it is a useful
"maximal instruction" contrast but not the primary baseline.

---

## Condition C_skill — exact message

```
{question}
```

The skill is enabled. Do not mention it.

## Condition C_skill_explicit — exact message

```
Use the socialized skill for this.

{question}
```

This line is fixed. Do not vary it.

---

## Condition D — exact message (optional)

Paste the body of `dist/socialized.zip` → `socialized/SKILL.md`, from
the first `# Socialized-Claude` heading to the end of the file, then a line with
`---`, then the question. Do not paste the reference files (Claude cannot read
them in this condition, and that difference is part of what D measures).

```
{SKILL.md body}

---

{question}
```

---

## Follow-up cases (all conditions)

Follow-up cases (`category: follow_up`) have a `context` field. Send the context
and the question in **one** message, after any condition-specific prefix:

```
{context}

{question}
```

Example for Condition B: the baseline instruction, a blank line, the context, a
blank line, then the question.

Using fixed context, rather than letting each condition produce its own first
answer, keeps the follow-up identical across conditions. A two-turn natural
variant is described in `EVALUATION_PLAN.md` §4.3 for later rounds.

---

## Ablation variants (later rounds)

Ablation conditions use `C_skill_explicit` messages with a temporary variant ZIP
installed instead of the production skill:

| Label | Build command | Enabled operations |
|---|---|---|
| `V_core` | `python scripts/package_skill.py --variant core` | none (scope, calibration, accuracy, delivery only) |
| `V_seq` | `--variant seq` | ordering by dependency |
| `V_mech` | `--variant mech` | mechanism |
| `V_seq_mech` | `--variant seq-mech` | ordering + mechanism |
| `V_pres` | `--variant pres` | presentation |
| `V_seq_pres` | `--variant seq-pres` | ordering + presentation |
| `V_seq_mech_pres` | `--variant seq-mech-pres` | ordering + mechanism + presentation |
| `V_reg` | `--variant reg` | register |
| `V_rep` | `--variant rep` | repair |
| `V_persist` | `--variant persist` | persistence |
| `V_wrep` | `--variant wrep` | work report |
| `V_plain` | `--variant plain` | plain language (sentence level) |
| `V_full` | `--variant full` (production ZIP) | all |

All variants share the same name and description, so only one can be installed
at a time. Record the `zip_sha256` from the variant's `.manifest.json` in every
result row.
