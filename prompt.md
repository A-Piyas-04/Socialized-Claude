# MASTER IMPLEMENTATION PROMPT
# ExplanationLab → Claude Explanation Skill V0

## 0. Your Role

You are an expert AI engineering agent specializing in:

- LLM behavior and instruction following
- Pedagogical explanation design
- Claude Agent Skills
- Experimental AI evaluation
- Software engineering and reproducible research
- Human comprehension and communication quality

You are responsible for implementing the first experimental version of a research-backed Claude explanation-improvement Skill.

**This is an implementation task, not a brainstorming task.**

Analyze the provided research materials, make justified technical decisions, write all necessary files, execute available tests, and produce an installable, documented artifact.

Do not stop after producing a plan.

---

# 1. Project Background

## 1.1 Our Ultimate Goal

We want to improve how Anthropic's Claude explains and communicates information.

We have observed that Claude sometimes produces explanations that are technically correct but fail to make the underlying concepts genuinely understandable.

Possible problems include:

- Introducing advanced concepts before the necessary foundations.
- Explaining what something is without explaining why it exists.
- Presenting technical terms without building mental models.
- Skipping intermediate reasoning steps.
- Providing abstractions instead of understandable mechanisms.
- Producing explanations that are formally correct but difficult to internalize.
- Overloading the reader with unrelated information.
- Providing examples without connecting them to the underlying concept.
- Failing to adapt explanations to the user's knowledge and actual question.

Our ultimate objective is NOT to make Claude imitate ChatGPT's style.

The objective is to make Claude more effective at communicating knowledge, especially when teaching complex concepts.

A successful explanation should help the reader:

1. Understand the core concept.
2. Understand why the concept exists.
3. Understand how it works.
4. Connect it to prerequisite knowledge.
5. Form an accurate mental model.
6. Apply that understanding to unfamiliar situations.
7. Retain factual and conceptual accuracy.

These are design objectives, not empirically established outcomes.

## 1.2 Why This Project Exists

Ordinary system prompts and generic instructions such as:

"Explain step by step."

"Explain simply."

"Explain like a good teacher."

have not reliably produced the communication improvements we want.

Therefore, our research focuses on identifying concrete explanation operations rather than simply using stronger generic prompts.

We created ExplanationLab to experimentally investigate these operations.

## 1.3 Our Current Research

Repository:

https://github.com/A-Piyas-04/claude-chatgpt-explanation-lab

Experimental archive:

research-results-2026-10-26.zip

The archive contains results from our previous explanation experiments.

Inspect all relevant reports, datasets, scripts, prompts, configurations, and available experimental outputs.

Do not assume the summaries in this prompt replace the actual evidence.

## 1.4 Known Preliminary Findings

Previous analysis identified the following:

**Experiment 3**

- Approximately 60 single-treatment transformation runs.
- Six explanation treatments.
- Five topics.
- Two original explanation sources: Claude and ChatGPT.
- T2, prerequisite-aware concept sequencing, performed relatively well on automated fidelity screening.
- Some T2 outputs made very limited changes.
- Therefore, fidelity alone cannot establish that T2 improves comprehension.

**Experiment 4**

- Approximately 20 cross-model rewriting runs.
- Different rewriting models produced different fidelity outcomes.
- Cross-model generalization was not conclusively established.

**Experiment 5**

- The AI comprehension proxy answered all 15 questions correctly even without reading the explanations.
- This created a ceiling effect.
- Consequently, the experiment could not determine whether explanation transformations improved comprehension.

Important:

These findings are preliminary.

Verify them against the actual files.

Document any discrepancies.

Do not fabricate experimental conclusions.

---

# 2. Non-Negotiable Product Constraints

The following are hard requirements.

### No API key for users

The eventual user must NOT need:

- An Anthropic API key.
- An OpenAI API key.
- A Gemini API key.
- Paid third-party inference.
- A separate LLM hosting account.
- A local GPU or self-hosted LLM.

The product should operate using the user's existing Claude environment.

Normal Claude account access, product eligibility, and usage limits may still apply.

### Claude-native first

The first prototype must be a custom Claude Skill.

It should be usable through supported Claude Skill installation mechanisms.

### No external LLM dependencies

The Skill must not secretly call another model or API.

No external inference service.

No hidden paid functionality.

### No separate chatbot

Do not build:

- A React frontend.
- A Next.js application.
- A FastAPI backend.
- A separate Claude client.
- An API-based LLM proxy.
- A browser extension in V0.

Those might be considered in later phases, but they are explicitly outside the scope of this implementation.

### Preserve accuracy

Improving readability must not come at the expense of factual or conceptual correctness.

### Do not invent evidence

Experimental results must remain distinguishable from hypotheses and engineering assumptions.

---

# 3. Primary Mission

Deliver two main artifacts:

## Artifact A — Claude Explanation Skill V0

An installable Claude Skill that applies selected explanation techniques contextually.

The Skill should make Claude explain concepts more effectively without making every answer unnecessarily long or formulaic.

## Artifact B — Evaluation Framework

A reproducible evaluation package for comparing:

A. Normal Claude

B. Claude with optimized communication instructions

C. Claude with Explanation Skill V0

The evaluation must determine whether the Skill provides measurable benefits beyond ordinary prompting.

The framework must distinguish between:

- Explanation quality
- Factual accuracy
- Skill activation
- Instruction adherence
- Actual comprehension

Do not collapse these dimensions into a single vague "quality" score.

---

# 4. Phase 1 — Research and Evidence Audit

Before implementing the Skill, analyze the experimental archive and relevant repository materials.

## 4.1 Inspect the Evidence

Identify:

- Experiment objectives
- Tested treatments
- Source explanations
- Transformation instructions
- Dataset sizes
- Topics
- Evaluation questions
- Automated metrics
- Judge configurations
- Raw responses
- Failure cases
- Research limitations

Trace claims to source files.

Do not rely only on report summaries when the underlying results are available.

## 4.2 Build an Evidence Matrix

For each treatment, record:

| Property | Description |
|---|---|
| Treatment ID | T1–T6 |
| Treatment name | Original experimental designation |
| Intended mechanism | What it attempts to improve |
| Evidence | Relevant experiment results |
| Fidelity risk | Risk of altering meaning |
| Comprehension evidence | Whether understanding improved |
| Confidence | Level of evidential support |
| V0 decision | Include, conditional, defer, or exclude |

Carefully distinguish:

- A treatment producing fewer errors.
- A treatment changing fewer words.
- A treatment improving readability.
- A treatment improving comprehension.

These are not interchangeable.

## 4.3 Analyze All Six Treatments

Investigate the exact definitions in the experiment files.

Expected treatment categories include:

T1 — Vocabulary or terminology clarification

T2 — Prerequisite-aware concept sequencing

T3 — Causal or mechanistic explanation

T4 — Concrete examples and analogies

T5 — Visual or structural presentation

T6 — Audience adaptation

Do not assume these labels capture the full experimental treatment definitions.

Use the original definitions where available.

## 4.4 Decide Which Treatments Belong in V0

We expect T2 and T3 to be primary candidates.

However, you must assess whether the evidence and engineering tradeoffs justify their inclusion.

Other treatments may be used conditionally.

Avoid the simplistic approach of enabling all six treatments for every explanation.

The purpose of the Skill is to improve understanding, not maximize the number of transformations.

## 4.5 Required Research Output

Create:

`research/EVIDENCE_AUDIT.md`

Include:

- Experimental summary
- Evidence matrix
- Treatment decisions
- Methodological limitations
- Contradictory or ambiguous results
- Why the selected V0 mechanisms were chosen
- What we still do not know

Use evidence references such as file paths, row identifiers, or experiment IDs wherever possible.

---

# 5. Phase 2 — Define the Explanation Methodology

Develop a coherent explanation methodology based on the research.

This must be practical and operational.

Avoid generic motivational teaching advice.

## 5.1 Explanation Diagnosis

Before constructing an educational explanation, Claude should contextually consider:

- What is the user actually asking?
- What knowledge is necessary to answer?
- What prerequisites are likely missing?
- Is the user asking what, why, how, or when?
- Does the concept require a mechanism explanation?
- Would an example clarify a difficult abstraction?
- Is the user requesting a short answer or a detailed walkthrough?
- Would extra explanation create unnecessary cognitive load?

These decisions should usually happen internally.

Do not force Claude to print a diagnostic checklist.

## 5.2 Prerequisite-Aware Sequencing

When appropriate, introduce foundational concepts before dependent concepts.

Example:

User asks:

"How does Redis caching work?"

A weak explanation may immediately introduce:

- Cache-aside
- Write-through
- TTL
- Cache invalidation
- Eviction policies

A stronger sequence may establish:

1. Why repeatedly retrieving data can be expensive.
2. What caching means.
3. Where Redis fits.
4. How a cache hit and cache miss work.
5. Why the cache can become stale.
6. Where TTL and invalidation become necessary.

However, avoid explaining prerequisites that the user already understands.

Do not force an introductory explanation for advanced users asking narrow technical questions.

## 5.3 Causal and Mechanistic Explanation

Where relevant, explain the chain of cause and effect.

A teaching explanation should help answer:

- Why does this mechanism exist?
- What problem does it solve?
- What happens internally?
- Why does each step occur?
- What would happen if a step failed?
- What tradeoff or limitation follows from the mechanism?

Example:

Weak:

"Write-back caching improves write performance."

Stronger:

"Instead of immediately sending every write to slower storage, the system first updates the cache and marks that data as modified. Several writes may then be combined before reaching storage. This reduces immediate storage operations, but modified data can be lost if the cache fails before it is written back."

This is an illustrative example, not a validated experimental output.

Do not interpret "causal explanation" as requiring lengthy explanations for every sentence.

## 5.4 Adaptive Examples

Use examples when they materially improve understanding.

A useful example should:

- Be relevant to the mechanism.
- Contain enough concrete detail.
- Preserve conceptual accuracy.
- Be explicitly connected to the abstract explanation.
- Avoid introducing unnecessary complexity.

Do not always use analogies.

Sometimes a direct technical example is more effective.

## 5.5 Explanation Depth

Use progressive depth when appropriate.

Possible structure:

- Core intuition
- Mechanism
- Concrete walkthrough
- Important limitation or tradeoff

But this is not a mandatory output template.

The explanation should adapt to user intent.

A simple factual question may need only one sentence.

A complex learning question may require substantial explanation.

## 5.6 Meaning Preservation

The Skill must not:

- Fabricate facts.
- Invent causal relationships.
- Present speculation as established fact.
- Replace technical accuracy with misleading analogies.
- Change the meaning of the user's requested topic.
- Introduce unnecessary claims merely to make the explanation more engaging.

When the model is uncertain, the explanation must preserve that uncertainty.

## 5.7 Behavior Across Different User Requests

Explicitly define behavior for:

- Beginner concept learning
- Intermediate technical explanation
- Advanced technical questions
- Why/how questions
- Direct factual questions
- Comparisons
- Requests for examples
- Step-by-step walkthroughs
- Follow-up confusion
- Requests for concise explanations
- Non-educational tasks

The Skill must not hijack unrelated tasks.

For example, a user requesting code changes should not automatically receive a long educational essay.

---

# 6. Phase 3 — Implement the Claude Skill

## 6.1 Technical Requirements

Follow the latest official Anthropic documentation for custom Claude Skills.

Official references:

https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

https://support.claude.com/en/articles/12512198-how-to-create-custom-skills

https://github.com/anthropics/skills

Verify current requirements before implementation.

The Skill must use:

`SKILL.md`

with valid YAML frontmatter.

At minimum:

```yaml
---
name: explanation-lab
description: Improve concept explanations through prerequisite-aware sequencing, causal reasoning, and adaptive examples. Use when the user asks to learn, understand, or clarify complex ideas.
---
```

You may improve this description, especially for reliable activation.

The Skill name should comply with current Anthropic naming requirements.

## 6.2 Progressive Disclosure

Keep the primary `SKILL.md` focused and actionable.

Do not dump the full research paper or experimental archive into the Skill.

Supporting documents may be placed in `references/`.

Claude should load only the additional information needed for the current request.

## 6.3 Suggested Directory Structure

```text
explanation-lab-v0/
├── README.md
├── CHANGELOG.md
│
├── skill/
│   └── explanation-lab/
│       ├── SKILL.md
│       └── references/
│           ├── explanation-methodology.md
│           ├── treatment-selection.md
│           └── explanation-examples.md
│
├── research/
│   └── EVIDENCE_AUDIT.md
│
├── evaluation/
│   ├── EVALUATION_PLAN.md
│   ├── RUBRIC.md
│   ├── TEST_CASES.json
│   ├── BASELINE_INSTRUCTIONS.md
│   ├── RUNBOOK.md
│   ├── RESULTS_TEMPLATE.csv
│   └── README.md
│
├── tests/
│   ├── test_skill_structure.py
│   ├── test_test_cases.py
│   └── test_evaluation_schema.py
│
├── scripts/
│   ├── validate_skill.py
│   ├── package_skill.py
│   └── summarize_results.py
│
├── dist/
│   └── explanation-lab.zip
│
└── docs/
    ├── INSTALLATION.md
    ├── ARCHITECTURE.md
    └── LIMITATIONS.md
```

This structure is a recommendation.

Adapt it if necessary, but preserve the separation between:

- Installable Skill
- Research
- Evaluation
- Packaging
- Documentation

**Important:** The installable ZIP should contain the Skill directory with `SKILL.md` at the proper relative location. Do not package the entire repository as the Skill.

## 6.4 Skill Instruction Design

The Skill should implement a compact explanation workflow:

**Step A — Understand the request**

Determine what explanation is needed and what the user already appears to know.

**Step B — Choose the explanation strategy**

Select only the operations likely to help.

**Step C — Construct the explanation**

Generate the explanation in a pedagogically appropriate sequence.

**Step D — Check the explanation**

Verify that:

- Necessary foundational concepts are available.
- Causal connections are explained where needed.
- Important steps are not skipped.
- Examples are consistent with the mechanism.
- The answer directly addresses the user's question.
- Unnecessary verbosity has been avoided.
- Factual uncertainty is preserved.

**Step E — Deliver the answer naturally**

Do not display the internal workflow.

Do not mention treatment identifiers such as T2 or T3 to ordinary users.

Avoid repetitive headings such as "What," "Why," and "How" unless those headings genuinely help.

## 6.5 Examples and Counterexamples

Include examples demonstrating:

- A weak explanation.
- A better explanation.
- The specific pedagogical difference.

Also include cases where the Skill should refrain from adding detail.

Use examples from multiple domains, including:

- Software engineering
- Computer science
- Mathematics
- Everyday concepts

Do not copy large portions of the experimental dataset unnecessarily.

Avoid creating examples that resemble the final evaluation cases too closely.

This helps reduce evaluation contamination.

## 6.6 Activation Behavior

The Skill must activate appropriately for requests such as:

- "Explain how this works."
- "Teach me this concept."
- "I don't understand why this happens."
- "Explain the mechanism."
- "Give me an intuitive explanation."
- "Explain the code and why each part is necessary."

It should not activate unnecessarily for:

- Basic greetings
- Pure translation requests
- Simple formatting tasks
- Requests for unrelated document modifications
- Tasks that do not involve teaching or explanation

Important:

Do not claim that automatic activation is guaranteed.

Claude controls Skill loading.

Design explicit activation tests as well as automatic-discovery tests.

---

# 7. Phase 4 — Build the Evaluation Framework

Evaluation is a first-class deliverable.

A Skill that installs successfully is not necessarily a Skill that improves explanations.

## 7.1 Experimental Conditions

We need three comparison conditions:

### Condition A — Normal Claude

The user asks the question without any explanation-specific customization.

No explanation Skill.

No special communication instructions.

### Condition B — Optimized Prompt Baseline

Use the same Claude model and question, but add a carefully designed generic explanation instruction.

Example:

"Explain clearly, introduce relevant prerequisites, explain how and why things work, and use examples when helpful. Avoid unnecessary complexity."

Improve this baseline if appropriate.

The goal is to make it a serious comparison rather than a deliberately weak prompt.

### Condition C — Explanation Skill V0

The same Claude model and question, with our Skill installed and enabled.

Avoid additional explanation instructions outside the Skill.

## 7.2 Important Fairness Requirement

A Skill may be loaded automatically, while a baseline instruction may be injected through a different product mechanism.

These conditions are not necessarily equivalent.

Document exactly how each condition is configured.

Distinguish between:

- Natural Skill activation.
- Confirmed Skill execution.
- Explicitly requested Skill usage.

An apparent failure may be an activation failure rather than a failure of the explanation methodology.

We should measure these separately.

## 7.3 Test Dataset

Create a diverse initial evaluation suite.

Target approximately 24–36 questions distributed across several categories.

Suggested categories:

- Foundational concepts
- Mechanism-heavy concepts
- Abstract concepts
- Multi-step processes
- Comparisons and tradeoffs
- Follow-up clarification
- Advanced questions
- Concise factual questions
- Negative controls where extra teaching is inappropriate

Use a mix of domains.

Do not evaluate only software engineering.

Each test case should have:

- Stable unique ID
- Category
- Difficulty
- User question
- Assumed audience knowledge
- Expected explanation properties
- Common misconceptions
- Critical facts that must be preserved
- Reasoning gaps to watch for

Prefer original held-out evaluation prompts.

Avoid simply reusing the same topics and explanations used to design the Skill.

## 7.4 Example Test Case Schema

```json
{
  "id": "mechanism_001",
  "category": "mechanism",
  "difficulty": "intermediate",
  "question": "Why can write-back caching improve performance?",
  "audience": "Software engineering student familiar with basic caching",
  "expected_properties": [
    "Explains deferred writes",
    "Explains why storage operations may be reduced",
    "Explains consistency or durability tradeoffs"
  ],
  "common_misconceptions": [
    "Write-back always writes immediately",
    "Write-back has no data-loss risk"
  ],
  "critical_facts": [
    "Modified cached data may not yet be persisted",
    "Write-back can reduce immediate storage write overhead"
  ]
}
```

Use realistic questions and diverse difficulty.

## 7.5 Evaluation Rubric

Create clear, anchored scoring guidelines.

Evaluate:

1. Prerequisite sequencing
2. Mechanistic clarity
3. Conceptual completeness
4. Directness
5. Appropriate depth
6. Example effectiveness
7. Accuracy
8. Cognitive load
9. Responsiveness to user intent

Define each score explicitly.

Do not merely say "score from 1 to 5."

Describe what a 1, 3, and 5 mean for each category, or use an equally reproducible scoring framework.

Do not treat surface-level formatting as equivalent to comprehension.

## 7.6 Real Comprehension Evaluation

This is essential.

Our previous comprehension proxy failed because the model could answer all questions without reading the explanations.

Do not repeat that methodology.

Design a small human comprehension protocol that measures learning.

Possible components:

- Pre-test
- Explanation exposure
- Post-test
- Application question
- Misconception detection
- Delayed recall when feasible

Comprehension questions must require use of the explained mechanism rather than simply retrieving common factual knowledge.

Where practical, compare questions answered before and after exposure to the explanation.

Evaluate transfer to unfamiliar scenarios.

Randomize or counterbalance explanation conditions across participants.

Avoid showing multiple versions of the same explanation to one participant without accounting for carryover effects.

Provide a clear practical procedure for a small pilot.

Do not invent participant results.

## 7.7 Automated Evaluation

Automated evaluation may supplement, but must not replace, comprehension testing.

Create tools for:

- Structural validity
- Result completeness
- Schema checking
- Basic statistical summaries
- Accuracy-check workflows
- Human rating aggregation
- Comparisons between conditions

Do not assume that an LLM judge's subjective scores are ground truth.

Do not implement a fake "comprehension score" based only on word count, headings, readability formulas, or semantic similarity.

## 7.8 Evaluation Execution Without API Keys

The evaluation should be executable manually using normal Claude chats.

Do not require an API for the initial test.

Create a runbook explaining:

- How to configure each condition.
- How to keep model versions consistent.
- How to start clean conversations.
- How to ensure only the intended Skill is active.
- How to record outputs.
- How to record activation evidence where observable.
- How to distinguish failures of activation from failures of explanation quality.
- How to blind evaluators to the condition.
- How to store ratings.
- How to summarize results.

The framework should not claim it can programmatically control Claude web sessions without an authorized mechanism.

Do not introduce browser scraping or automated UI interaction.

## 7.9 Success Criteria

Define meaningful pilot success criteria before evaluation.

Suggested preliminary requirements:

- The Skill installs without structural errors.
- Intended activation is verified in a meaningful proportion of eligible cases.
- No critical factual error is introduced by the explanation methodology.
- The Skill does not systematically create excessive verbosity.
- Blind evaluators prefer Skill outputs over both baselines on pedagogical quality.
- Human comprehension outcomes show a positive signal.

For quantitative results:

Report paired differences, variability, sample sizes, and uncertainty.

Do not declare statistical superiority from a tiny sample or uncalibrated judge scores.

Set pilot thresholds explicitly, but label them as engineering targets rather than scientifically validated thresholds.

---

# 8. Phase 5 — Baseline and Ablation Design

We must distinguish what actually produces improvement.

Create an experimental extension for later ablation tests.

Potential configurations:

- T2 only
- T3 only
- T2 + T3
- Full adaptive Skill

Do not automatically build four separately installable production Skills unless necessary.

Instead, create a documented method for running these comparisons through temporary Skill variants.

The purpose is to determine:

- Whether prerequisite ordering helps.
- Whether causal reasoning helps.
- Whether combining them helps more.
- Whether adaptive selection adds value.

Do not claim that combining two good treatments necessarily improves performance.

More instructions can produce conflicting or redundant behavior.

---

# 9. Phase 6 — Validation and Packaging

Implement local validation scripts.

## 9.1 Structural Validation

Verify:

- `SKILL.md` exists.
- YAML frontmatter parses correctly.
- Required metadata exists.
- Metadata follows current naming requirements.
- Referenced files exist.
- No references escape the package directory.
- No API credentials or secrets are present.
- No unintended external inference dependencies exist.

## 9.2 Packaging

Generate:

`dist/explanation-lab.zip`

Ensure it contains the correct directory structure expected by claude.ai.

The Skill ZIP must not contain:

- Research datasets
- Unnecessary development dependencies
- Evaluation scripts
- API secrets
- Experimental raw outputs

Only include files needed by the Skill.

## 9.3 Testing

Implement and run available offline tests.

Test:

- Valid Skill metadata
- Required reference files
- Packaging integrity
- Evaluation dataset validity
- Result schema consistency
- Scoring aggregation
- Graceful handling of missing data

Where possible, reuse official Anthropic Skill validation tools.

Do not claim to have tested the Skill inside claude.ai unless you actually performed that test.

Offline structural validation is not proof of successful Claude activation.

---

# 10. Phase 7 — Documentation

Create practical documentation.

## INSTALLATION.md

Explain precisely how to:

- Locate the installable ZIP.
- Upload it to Claude.
- Enable it.
- Use it in a conversation.
- Attempt explicit invocation.
- Verify activation where supported.
- Disable or uninstall it.
- Troubleshoot failures.

Check the current official interface before specifying exact menu paths.

Explain account eligibility and any relevant Claude product limitations.

## ARCHITECTURE.md

Explain:

- What the Skill does.
- How the explanation methodology works.
- How treatments are selected.
- Which elements are research-backed.
- Which elements are provisional.
- Why no external API is needed.
- What behavior is controlled by Claude rather than by our implementation.

## LIMITATIONS.md

Include:

- Skill activation is not guaranteed.
- Instruction-following may vary by model and context.
- The Skill does not modify Claude's model weights.
- It cannot guarantee a better explanation.
- It cannot reliably inspect hidden reasoning.
- It does not provide a separate independent model-based verifier.
- Claude account limits still apply.
- Human comprehension improvements remain unproven until tested.

## README.md

Provide:

- Project summary
- Installation path
- Directory overview
- Research methodology
- How to run tests
- Evaluation instructions
- Current status
- Explicit next steps

---

# 11. Engineering Quality Requirements

Use clean, maintainable engineering practices.

### Simplicity

Do not add frameworks unnecessarily.

The actual Claude Skill should remain lightweight.

### Traceability

Every major design decision should be explainable.

Link treatment decisions back to experimental evidence or clearly identified hypotheses.

### Reproducibility

Use stable test identifiers, structured result formats, and clear evaluation procedures.

### Portability

Keep the Skill compatible with Anthropic's documented format.

Do not unnecessarily depend on Claude Code-only features.

### Robustness

Validation scripts should fail clearly when files are missing or malformed.

### Testability

Evaluation instruments and tests should be independently usable.

### Scientific honesty

Distinguish:

- Observations
- Hypotheses
- Engineering choices
- Validated results

Never merge them into unsupported conclusions.

---

# 12. Strict Anti-Patterns

Do NOT:

1. Build a chatbot or API wrapper.
2. Require an Anthropic API key.
3. Introduce paid inference dependencies.
4. Make the Skill a giant generic system prompt.
5. Automatically expand every answer.
6. Enforce a fixed "What → Why → How → Example" template on every response.
7. Claim that T2 is proven best because it scored well on fidelity.
8. Assume more explanatory text means more comprehension.
9. Treat an AI judge as a substitute for real learning evaluation.
10. Invent experimental measurements.
11. Hide important limitations.
12. Build a browser extension in this phase.
13. Create an unnecessarily complex runtime.
14. Produce only documentation without implementation.
15. Declare the Skill successful before running a controlled evaluation.

---

# 13. Required Final Deliverables

At the end of implementation, I expect:

**A. Installable Skill**

`dist/explanation-lab.zip`

**B. Skill source**

`skill/explanation-lab/SKILL.md`

plus necessary references.

**C. Research audit**

`research/EVIDENCE_AUDIT.md`

**D. Evaluation framework**

Complete test cases, rubrics, baseline instructions, result templates, and execution runbook.

**E. Local validation**

Scripts and passing tests.

**F. Installation instructions**

Clear user-facing instructions requiring no API key.

**G. Development report**

Summarize:

- What you inspected
- What you implemented
- Why you selected those treatments
- What tests you ran
- What passed
- What failed
- What remains unverified
- Exactly what I should do next to test the Skill in Claude

---

# 14. Implementation Workflow

Execute in this order:

1. Inspect the repository and research archive.
2. Verify the experimental findings.
3. Produce the evidence audit.
4. Select the V0 explanation methodology.
5. Implement the actual Claude Skill.
6. Create reference examples and behavior guidance.
7. Design the controlled evaluation suite.
8. Implement local validation scripts.
9. Execute available tests.
10. Package the installable Skill ZIP.
11. Write installation and evaluation documentation.
12. Review the complete implementation for consistency.
13. Present final deliverables and a concise testing guide.

Do not ask me for decisions that can reasonably be made from the available evidence.

If something is genuinely missing, proceed with the best justified implementation and identify the limitation.

Do not falsely claim that an unexecuted test passed.

---

# 15. Acceptance Criteria

The task is complete only when:

- A valid installable Claude Skill exists.
- The Skill uses a research-informed explanation methodology.
- The Skill does not require an API key.
- Its activation description is appropriately scoped.
- It preserves accuracy and audience adaptation.
- Its implementation does not force unnecessary verbosity.
- The evaluation plan includes fair baselines.
- The evaluation includes a way to test human understanding.
- Local validation passes, or failures are documented.
- The final ZIP has been generated and inspected.
- The evidence audit identifies unsupported assumptions.
- Documentation explains how I can test it inside Claude.

Do not claim that explanation improvement has been demonstrated until empirical testing establishes it.

---

# 16. Final Instruction

Remember the core research objective:

**We are not trying to make Claude sound like ChatGPT. We are trying to identify and implement explanation mechanisms that make Claude genuinely better at communicating knowledge.**

The Skill is an experimental implementation of that research.

Treat the project as both software engineering and applied research.

Build the complete V0 implementation now, keep the architecture minimal, preserve scientific validity, and ensure that the resulting artifact can be tested by an ordinary Claude user without an Anthropic API key.