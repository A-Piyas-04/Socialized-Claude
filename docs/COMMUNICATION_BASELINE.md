# Communication baseline

A lightweight behavioural reference for Socialized-Claude: three real prompts, what
the owner observed from v0.5.2, and what a good answer should do. It is not an
automated evaluation. Behavioural acceptance stays with the project owner, who
checks a few ordinary conversations by hand after each communication change.

Every statement below is in one of four categories, and each section says which:

| Category | Meaning |
|---|---|
| Captured model responses | Text a model actually produced, stored in this repository |
| Desired behaviour | What the owner wants an answer to do; a target, not an observation |
| Structural tests | Offline checks that a rule ships in the skill text; they test text, not answers |
| Unverified assumptions | Beliefs about how a rule changes behaviour that nobody has measured |

The regression analysis behind the rules is in `docs/communication-recovery.md`.

## Captured model responses

**The three v0.5.2 answers are not stored in this repository.** The owner ran them
in real conversations with the installed v0.5.2 skill and reported the observed
strengths and weaknesses below. Those observations are the only record. No text is
quoted from them here, and none should be reconstructed.

The only genuine captured responses in the repository predate the skill:

- `research-results-2026-10-26/inputs/input-dataset.json` holds 15 Claude answers
  to five questions (caching, B-tree indexes, the TCP handshake, vaccines, compound
  interest), copied from web chat on 2026-10-26 with unknown settings. No
  Socialized-Claude version produced them, and none answers the three prompts here.
  Some markdown was lost in copying.
- `COMMUNICATION_EXEMPLARS.md` exemplars 1–3 quote excerpts from those answers with
  their IDs. Exemplars 4–13 are constructed, not captured.
- `evaluation/runs/pilot16` and `evaluation/runs/pilot16-cc` hold run sheets and
  messages but no responses.

No captured response from any Socialized-Claude version, V0 to v0.5.2, is stored in
the repository. So no version can be cited as the "good earlier" baseline from
evidence here.

## Test A — database replication

**Prompt (verbatim):**

> Explain how database replication works internally. I want to understand exactly
> how changes travel from the primary database to replicas, what happens when
> multiple writes occur simultaneously, and how replicas recover after losing their
> connection. Explain the actual mechanisms, not just definitions.

**Observed in v0.5.2 (owner report, not stored):**

- Dense technical paragraphs.
- Repetition between diagrams and explanations.
- Implementation-specific mechanisms generalized across databases.
- Weak separation between essential mechanisms and deeper implementation details.

**Desired behaviour:**

- Build the core mechanism up in order: the change log, shipping it, applying it.
- Establish it with one concrete case, such as two writes and one replica falling
  behind, and carry that case through.
- Teach the general mechanism first. Label PostgreSQL-specific behaviour (WAL
  streaming, replication slots) as PostgreSQL's, and do not present it as how every
  database works.
- Use a diagram for who sends what to whom. Use a table for state changes, such as
  each replica's position over time, or for a real comparison.
- After a diagram, explain why each step happens rather than retelling its arrows.
- Put deeper internals in a layer a reader can skip.

**Rules that target this:** the accuracy rule to teach the general mechanism first
and label one system's version; the `op:visual` rule giving a figure and its text
different jobs; the **Deeper:** block's named contents; the running example traced
to the moment the behaviour shows.

## Test B — architecture decision

**Prompt (verbatim):**

> I'm building a task management application for around 500 users. I'm considering
> PostgreSQL, Redis, RabbitMQ, microservices, and Kubernetes. Which technologies
> should I actually use, which should I avoid, and why? Challenge my assumptions and
> recommend a practical architecture.

**Observed in v0.5.2 (owner report, not stored):**

- Extremely long table cells.
- Multiple technical arguments compressed into individual cells.
- Weak separation between quick recommendations and detailed tradeoffs.
- Unsupported assumptions about traffic and infrastructure requirements.

**Desired behaviour:**

- Open with a direct recommendation.
- Make the comparison scannable: each cell holds the verdict and the one reason that
  decides it.
- Put conditions, exceptions and longer arguments in a list under the table, one
  item per technology that needs one.
- State the assumed load once, and say what would change the recommendation.
- Challenge the assumptions without being dismissive: say what would make a rejected
  technology worth adopting.
- Show a simple architecture diagram only if it adds understanding beyond the table.

**Rules that target this:** the `op:presentation` table-cell rule (the verdict stays
in the cell, the reasoning goes under the table); Strategy D (lead with the
recommendation and the reason that decides it, then the tradeoffs); the accuracy
rule to state an assumed scale once, with what would change the answer.

## Test C — CPU cache coherence

**Prompt (verbatim):**

> Teach me how CPU cache coherence works in a multicore processor. I understand what
> CPU caches are, but I don't understand how multiple CPU cores keep their cached
> data consistent when they read and modify the same memory location. Explain the
> actual mechanism step by step, using a concrete example.

**Observed in v0.5.2 (owner report, not stored).** Strengths to keep:

- Good prerequisite ordering.
- Correct introduction of MESI states.
- Useful sequence diagram.
- Concrete two-core scenario.
- Strong causal explanation.

Weaknesses:

- Dense paragraphs.
- Numbered explanations repeating parts of the diagram.
- Some explanatory information better suited to state transitions.
- Insufficient distinction between the core mechanism and optional deeper
  discussion.

**Desired behaviour:**

- Keep the depth, the causal reasoning and the technical accuracy.
- Make the state transitions easy to follow, for example in a table with one row
  per event and one column per core's state.
- Explain why each transition happens, not merely narrate the diagram.
- Use compact representations where they help.
- Put protocol variants (MOESI, MESIF) and hardware detail in a skippable layer.

**Rules that target this:** the `op:visual` rule (a diagram shows who acts in what
order, a state table shows what each step changes, the text says why); the **Deeper:**
block's named contents; the Step 3 check on the text after a figure.

**Observed in v0.7.0 (owner report, not stored).** Two answers, one through the
claude.ai plugin and one through the standalone skill, failed acceptance. Both were
still dense and repetitive: the same transitions appeared in a state diagram, a
sequence diagram, prose and a recap. Neither used meaning-matched icons. The plugin
answer's state diagram drew a read-triggered Modified → Invalid transition; a remote
read takes a Modified line to Shared, and only a remote write invalidates it.

**Added desired behaviour (v0.8.0):**

- Each figure, table and paragraph does a job nothing else in the answer does; a
  second figure of the same transitions appears only when it shows something the
  first cannot.
- Every transition in a figure names its trigger, and read-triggered and
  write-triggered transitions are not confused.
- Key headings carry a few meaning-matched icons.

**Rules that target this (v0.8.0):** Step 2's planning order; `op:visual`'s
one-job-per-form and one-representation preference; the first accuracy rule's figure
clause; the icon default. See `docs/communication-priority-correction.md`.

## Structural tests

`tests/test_communication_recovery.py` checks the following offline:

- each rule named above ships in `SKILL.md`, in the claude.ai ZIP and in the plugin;
- the references and the policy modules agree with those rules;
- table cells still have no absolute word limit;
- a walkthrough in words is still allowed when the reader needs one;
- the 12 operations, the 15 variants and every Phase 4–4C fix are intact;
- this document keeps the three prompts and the four categories, and claims no
  stored v0.5.2 output.

These tests check text, not answers. **A passing suite does not show that any answer
improved.**

## Unverified assumptions

- That the observed weaknesses came from the rules changed here. The changes are
  verified by diff; their behavioural effect is a hypothesis
  (`docs/communication-recovery.md` §2).
- That moving a row's argument under the table keeps the table scannable without
  splitting one decision across two places the reader must join.
- That "unless this reader needs the steps in words as well" keeps useful
  reinforcement without letting the retelling back in.
- That the new rules transfer to other prompts. All three tests are technical and
  practitioner-level; nothing here covers a beginner or a non-technical subject.
- That the owner's three observations are representative. They are one answer per
  prompt, with sampling variation unknown.

## How to use this reference

After a communication change, the owner runs the three prompts in fresh
conversations with the installed skill and compares each answer with its "desired
behaviour" list. A pass is the owner's judgement. Record the result in the
CHANGELOG entry for the change. Store the answers themselves only if the owner
chooses to, labelled with the skill version, the surface and the date.
