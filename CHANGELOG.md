# Changelog

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
