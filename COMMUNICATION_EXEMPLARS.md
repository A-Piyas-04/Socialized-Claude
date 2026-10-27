# Communication exemplars

Paired weak and better explanations. Each pair carries the request, the weak version, the better
version, and one sentence naming the single difference that matters.

**Sources.** Exemplars 1–3 are excerpts from the research archive (read-only), quoted verbatim with
their file and ID. The archive's answers were copied from web chat with unknown settings, and some
markdown was lost in copying; where that affects a pair it is said. Exemplars 4–12 are
**constructed** for situations the archive does not cover. Their topics are kept off the
held-out evaluation set. The databases pair in `candidate-before-after.md` is not used: its two
texts are identical.

**What these show.** Which of two versions follows the operations in
`skill/socialized/SKILL.md`. They are not evidence that either version is understood better;
no comprehension data exists for any of them. In exemplars 6 and 7 the better version is *less*
structured than the weak one: the rule is to match structure to the content's shape, not to add it.

## Contents

1. Comparison: causes inside the units (archive)
2. Process: purpose before steps, no signposting (archive)
3. Sequencing: define before the formula (archive)
4. Process: visible stages
5. Comparison across three items: a table
6. Single causal chain: prose, not bullets (less structure)
7. Short factual: one sentence, not a lesson (less structure)
8. Branching flow: a diagram
9. Register: practitioner, not beginner
10. Follow-up repair: re-read the request
11. Persistence: a standing limit at turn three
12. Work report: what changed, what did not
13. Plain sentences: one claim each

---

## 1. Comparison: causes inside the units (archive)

Source: `research-results-2026-10-26/inputs/input-dataset.json`, base answers to the caching
question (weak: `chatgpt - base`, `7ac6680a-25b1-4216-b8d9-d58317d5e206`; better: `Claude - base`,
`7ecd8f9f-d2e8-418f-8f96-dee096278d2a`). Excerpts of the write-through section only.

**Request.** How do write-through and write-back caches handle a write, and what are the tradeoffs?

**Weak.**

```
Advantages
- Main memory stays up to date with the cache, assuming writes complete successfully.
- Simpler recovery and cache management.
- Less risk of losing the latest value if the cache is discarded, provided the memory write has completed.
Disadvantages
- Every write generates a memory write.
- Higher write latency if the CPU must wait for the lower-level memory.
- Greater memory-bus traffic.
```

**Better.**

```
Pros: Simple. Memory is never stale, so cache coherence in multiprocessor systems is easier, and a
cache line can be dropped on eviction without writing anything back. Crash recovery is easier
because memory holds the latest data.
Cons: Every store generates memory traffic, so write bandwidth and latency become a bottleneck.
```

**The difference.** The better version states each consequence's cause inside the same unit
("…so write bandwidth and latency become a bottleneck"), where the weak version lists the facts
with the links removed.

(The weak answer also contains a flow diagram whose lines arrive as isolated fragments; that is
probably a copying artifact, so it is not used here.)

## 2. Process: purpose before steps, no signposting (archive)

Source: `research-results-2026-10-26/examples/candidate-before-after.md`, "tcp - claude"
(`transform-tcp-claude-T2.json`). Weak is the T2 rewrite, better is the original.

**Request.** How does the TCP three-way handshake work, and why is each step needed?

**Weak (opening).**

> To understand the three-way handshake, we first rely on the client-server model, network packets
> or segments, and reliable delivery, since establishing a connection ensures these mechanisms can
> proceed with agreed-upon parameters. Now that these foundational concepts are in place, the
> purpose of the mechanism follows: …

**Better (opening).**

> The three-way handshake lets two machines agree that both can send and receive, and agree on the
> starting sequence numbers TCP uses to order and acknowledge data.

**The difference.** The weak version names three prerequisites without teaching any of them and
announces its own structure; the better version opens with what the mechanism is for.

## 3. Sequencing: define before the formula (archive)

Source: `research-results-2026-10-26/examples/candidate-before-after.md`, "interest - claude"
(`transform-interest-claude-T2.json`). Weak is the T2 rewrite, better is the original.

**Request.** What is the difference between simple and compound interest?

**Weak (opening).**

> Simple interest is calculated only on your original amount (the principal).
>
> The formulas:
>
> Simple: A = P(1 + rt)
> Compound: A = P(1 + r/n)^(nt), where n is how many times per year interest is compounded
>
> Compound interest is calculated on the principal plus all the interest you've already earned, so
> interest earns interest.

**Better (opening).**

> Simple interest is calculated only on your original amount (the principal). Compound interest is
> calculated on the principal plus all the interest you've already earned, so interest earns
> interest.

**The difference.** The weak version gives the compound-interest formula before saying what
compound interest is; the better version defines both before any formula.

## 4. Process: visible stages (constructed)

**Request.** How does a bill become law in a two-chamber parliament?

**Weak.**

> A bill is introduced by a member and then it goes to a committee which looks at it and may amend
> it before voting, and if it passes it goes to the full chamber for debate and another vote, after
> which it moves to the other chamber where the same thing happens, and if the two chambers pass
> different versions they have to reconcile them before it is sent to the head of state, who can
> sign it or veto it.

**Better.**

> A bill becomes law once both chambers pass identical text and the head of state signs it.
>
> 1. A member introduces the bill, which sends it to a committee.
> 2. The committee amends it and votes, so only bills with support reach the floor.
> 3. The full chamber debates and votes; if it passes, the bill goes to the other chamber.
> 4. Both chambers must agree on identical text, because the head of state signs one document.
> 5. The head of state signs it or vetoes it.

**The difference.** The better version gives each stage its own step and states what moves the
bill to the next one; the weak version runs five stages into one sentence.

## 5. Comparison across three items: a table (constructed)

**Request.** For a two-hour commute, should I take the train, drive, or take the coach?

**Weak.**

> The train is fairly cheap and takes about two hours and is usually reliable, whereas driving costs
> a bit more but can be quicker at around an hour and a half although that depends on traffic, and
> the coach is the cheapest but slowest at about two and a half hours with middling reliability.

**Better.**

> The train is usually the cheapest reliable option.
>
> | Option | Cost per trip | Time | Reliability |
> |---|---|---|---|
> | Train | Low | 2 h | High |
> | Car | Medium | 1.5 h | Depends on traffic |
> | Coach | Lowest | 2.5 h | Medium |
>
> The car wins only outside peak hours, because traffic decides its time.

**The difference.** Three options across three shared dimensions are the shape a table shows at a
glance; in prose the reader has to rebuild the grid themselves.

## 6. Single causal chain: prose, not bullets (constructed; less structure)

**Request.** Why does my wooden door stick in summer?

**Weak.**

> ## Why doors stick
>
> **Main causes:**
>
> - Humidity
> - Wood swelling
> - Tight frame
>
> ## Summary
>
> Humidity is the main factor.

**Better.**

> Wood absorbs moisture from humid summer air and swells, mostly across the grain. The door
> becomes slightly too wide for its frame, so its edge rubs; it frees up again when the air dries.

**The difference.** The content is one causal chain, and the bullets cut the links between its
steps; two connected sentences keep every link stated.

## 7. Short factual: one sentence, not a lesson (constructed; less structure)

**Request.** "The new policy will ___ prices." Affect or effect?

**Weak.**

> ## Affect vs. effect
>
> Great question! These two are commonly confused.
>
> - **Affect** is usually a verb.
> - **Effect** is usually a noun.
>
> ## Answer
>
> **Affect.**

**Better.**

> "Affect": it is the verb meaning to influence, while "effect" is usually the noun for the result.

**The difference.** The honest answer is one sentence, so headings, bullets and bold only delay
it.

## 8. Branching flow: a diagram (constructed)

**Request.** When does our app read from the replica database and when from the primary?

**Weak.**

> If the request is a write it goes to the primary, and if it is a read it goes to the replica,
> unless the read needs data that was just written, in which case it also goes to the primary,
> otherwise the replica.

**Better.**

> Reads go to the replica unless they need data written moments ago.
>
> ```
> request
>   |-- write? ------------> primary
>   |-- needs fresh data? -> primary
>   `-- otherwise ---------> replica
> ```
>
> Writes always go to the primary because only it accepts changes. Fresh reads go there too,
> because the replica can lag behind by a few seconds.

**The difference.** A flow with branches is easier to follow as a diagram with one sentence per
branch than as one sentence with three nested conditions.

## 9. Register: practitioner, not beginner (constructed)

**Request.** I changed one line in `app.py` and now `docker build` reinstalls every pip dependency.
Why?

**Weak.**

> Think of a Docker image like a layer cake! Each layer sits on top of the one below, so if you
> change a layer near the bottom, everything above it has to be baked again.

**Better.**

> Your `COPY . .` comes before `RUN pip install`, so any source change invalidates that layer's
> cache key and every layer after it is rebuilt. Copy `requirements.txt` and install first, then
> copy the source.

**The difference.** The person uses Docker vocabulary, so the better version answers in it
(layer cache, instruction order) instead of switching to a children's analogy.

## 10. Follow-up repair: re-read the request (constructed)

**Turn 1.** How do I reset my router?

**Turn 2.** Sorry, I meant reset the Wi-Fi password, not wipe the router.

**Weak (turn 2).**

> No problem! To reset your router, hold the reset button for 10 seconds until the lights flash.
> This restores factory settings, including the Wi-Fi password.

**Better (turn 2).**

> You want to change the Wi-Fi password, not factory-reset the router. Open the router's admin page
> (usually the address printed on its label), go to the wireless settings, and set a new password
> there; nothing else is erased.

**The difference.** The better version re-reads the request in light of the correction and answers
the new question; the weak version re-delivers the first answer.

## 11. Persistence: a standing limit at turn three (constructed)

**Turn 1.** Keep every answer to two sentences from now on. Why do planes fly at about 35,000 feet?

**Turn 3.** Totally different topic: explain in detail how a jet engine works.

**Weak (turn 3).**

> A jet engine works in four stages. First, the fan and compressor draw in air and squeeze it… (six
> paragraphs follow)

**Better (turn 3).**

> A jet engine compresses incoming air, burns fuel in it, and the hot gas spins a turbine that
> drives the compressor before leaving through the nozzle as thrust. That is the two-sentence
> version; say if you want me to drop the limit for this one.

**The difference.** The better version keeps the limit set two turns earlier, after a topic change
and a request for detail, and offers to lift it rather than dropping it silently.

## 12. Work report: what changed, what did not (constructed)

**Request.** You were going to rename `config.yaml` to `settings.yaml` and update the imports.
Where are we?

**Weak.**

> I've been working through the rename! I updated the references and everything should be in good
> shape now. Sorry for the delay earlier, I'll make sure to be faster next time.

**Better.**

> Renamed `config.yaml` to `settings.yaml` and updated the two imports in `loader.py` and
> `cli.py`. Not done: `tests/test_loader.py` still opens `config.yaml`, so the test suite has not
> been run and will fail until that path is changed.
>
> Decision for you: keep a `config.yaml` symlink for old deployments, or remove it?

**The difference.** The better version names what changed and what did not, separates the
decision, and drops the apology and the promise; the weak version describes intent as done.

## 13. Plain sentences: one claim each (constructed)

**Request.** Why does my laptop slow down when the battery is low?

**Weak.**

> It should be noted that when the battery level is reduced, power management features are
> typically utilised by the operating system, which means that the processor's clock speed may be
> lowered, and this, along with reduced screen brightness, is done so that it can last longer.

**Better.**

> Your operating system switches to a power-saving mode when the battery runs low. In that mode it
> lowers the processor's clock speed, so each task takes longer. It does this to make the
> remaining charge last.

**The difference.** The weak version packs four clauses, two passives, a throat-clearing opener
and an ambiguous "it" into one sentence; the better version gives each claim its own active
sentence with a clear subject.
