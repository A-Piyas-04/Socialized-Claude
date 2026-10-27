# Changelog

## Unreleased

### Skill (V1)
- `op:structure` renamed to `op:presentation` and rewritten as a positive
  operation: answer first, one idea per unit, form chosen from the content's
  shape (steps, tables for 3+ items on 2+ dimensions, labelled lists, fenced
  diagrams for branching flows, prose for a single causal chain), headings that
  state what a section establishes, at most two bolded sentences. The four
  prose-default prohibitions are gone; decorative structure, emoji as
  structure, whitespace padding and empty transitions are failure modes.
- New operations: `register` (three registers, practitioner default, with scope
  discipline folded in), `repair`, `persistence`, `work-report`, and`n  `plain` (sentence-level readability, reinstating T1's sentence rules). Ten
  operations in total.
- Accuracy rules: specific citations only when confident they exist; named
  researchers, papers and foreign or field terms glossed in the same sentence.
- Variants `pres`, `seq-pres`, `seq-mech-pres`, `reg`, `rep`, `persist`,
  `wrep`, `plain` (13 in total), mirrored as `V_*` conditions with their contrasts.

### Evaluation
- Automated collection with Claude Code (`scripts/collect_cc.py`): isolated
  sandbox per row, arm verified from the `system/init` event, real multi-turn
  conversations, frozen per-run builds, resumable, refuses `ANTHROPIC_API_KEY`.
- Automated screening judge (`scripts/judge.py`, `scripts/judgelib.py`): fact
  capture, both-orders pairwise preference with flip rate, `navigability` and
  `register_fit`; `scripts/judge_acceptance.py` tests the judge on archive
  answers; `scripts/screen_items.py` screens comprehension items for diagnostic
  power.
- Rubric: `navigability` and `register_fit` (11 dimensions) and the
  preference-versus-comprehension rule.
- 12 new cases (45 in total): register, repair, decorative-structure controls,
  persistence (machine-checked standing constraints), work report.
- `scripts/structural_metrics.py` and `scripts/lint_response.py`, with a
  baseline for the 10 archive base answers; summaries add structural
  descriptors and a persistence re-ask proxy, none of which feed S1–S7.

### Docs
- `COMMUNICATION_GRAMMAR.md` (every rule with its evidence label) and
  `COMMUNICATION_EXEMPLARS.md` (3 archive pairs, 9 constructed).

- Added `scripts/run_assistant.py`, an interactive clipboard helper for
  manual response collection. It copies each message, saves each copied
  response, fills the run sheet, pauses at skill on/off batch boundaries, and
  can resume. It does not interact with Claude's website. Covered by 14 tests,
  for 186 in total.

## 0.1.0 — 2026-10-26 (V0, experimental)

First implementation. Not yet evaluated in Claude.

### Skill
- `explanation-lab` skill with a scope gate, silent request reading, answer
  sizing, and two core operations: dependency ordering and mechanism.
- Three conditional operations: one mapped example, terms at first use, and
  formatting only for real shape.
- Accuracy rules (no invented mechanisms, hedges preserved) and natural
  delivery (no visible workflow or labels).
- References: per-request-type methodology, weak/better examples across four
  domains plus restraint cases, and selection, conflict, and failure-mode rules.
- Description of 196 characters, within claude.ai's 200-character limit.

### Research
- Evidence audit of the ExplanationLab 2026-10-26 archive, with a script that
  regenerates every cited number.

### Evaluation
- 33 held-out test cases, a 9-dimension anchored rubric with accuracy and
  adherence coding, and condition definitions (A, B, C natural, C explicit,
  optional D, ablation variants).
- Runbook for manual execution without an API.
- Human comprehension protocol with a draft item bank.
- Scripts: run sheet, blind packet, summary with bootstrap intervals and gated
  criteria, and Latin-square assignment.

### Tooling
- Validator covering the official frontmatter rules plus packaging, safety, and
  marker checks.
- Deterministic packager with ablation variants and manifests.
- 172 offline tests.
