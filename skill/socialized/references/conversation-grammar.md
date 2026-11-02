# Conversation grammar

This file supports the conversational operation in `SKILL.md`. It shows the
implied-second-voice move in worked form, a register ladder for pitching it, and
weak and better pairs for direct address and contractions. The better versions
illustrate the move; they are not templates, and a question belongs on the page
only when the content then answers it.

## Contents

1. The reader's-question move, worked
2. A register ladder for the same move
3. Direct address: weak and better
4. Contractions: weak and better
5. What the second voice may not do

<!-- op:conversational -->
## 1. The reader's-question move, worked

Each pair shows a flat assertion, then the same content with the reader's next
question surfaced and answered. The question earns its place because the sentences
under it resolve it.

### Caching: why not write to memory every time

**Weak:**
> Write-back caching defers the write to main memory until the cache line is
> evicted, which improves throughput at the cost of durability.

**Better:**
> Write-back caching holds the new value in the cache and writes it to main memory
> later, when the line is evicted.
>
> > 🙋 **So why not just write to memory every time?**
>
> Because every write would then wait on memory, and memory is roughly a hundred
> times slower than the cache. You would pay that cost on every single write.

**What changed:**
- The objection a reader forms at "writes it later" is stated, not left implicit.
- The answer is the cost comparison, not a restatement of the definition.

### Indexes: why a read speed-up can slow writes

**Weak:**
> Adding an index improves read performance but introduces write overhead and
> additional storage requirements.

**Better:**
> An index is a sorted copy of one column, kept beside the table, so a lookup on
> that column jumps straight to the rows instead of scanning every one.
>
> > 🙋 **If it only helps, why not index every column?**
>
> Because the database has to update each index on every insert and update. Five
> indexes mean five extra writes per row, so you add an index where reads are hot
> and writes are not.

**What changed:**
- The question turns a bare "write overhead" into the reason: one extra write per
  index per row.
- The reader leaves with a rule they can apply, not a tradeoff they must weigh
  unaided.

### Hashing: why average, not worst, case

**Weak:**
> Hash lookups are O(1) on average and O(n) in the worst case due to collisions.

**Better:**
> A hash turns the key into a slot number, and you read that slot directly, so the
> work does not grow with the number of stored items.
>
> > 🙋 **Then where does the O(n) worst case come from?**
>
> From collisions: when many keys land in the same slot, that slot holds a list
> you must scan one entry at a time. A good hash and timely resizing keep each
> slot's list short, so lookups stay constant on average.

**What changed:**
- The worst case is introduced as the answer to a question, so it reads as a
  consequence rather than a disclaimer.

### Retries: why they can make an outage worse

**Weak:**
> Naive retry logic can amplify load during partial outages, so backoff is
> recommended.

**Better:**
> A retry resends a request that failed, on the assumption the failure was
> temporary.
>
> > 🙋 **How could retrying make things worse?**
>
> When a service is already overloaded, every client retrying at once multiplies
> the traffic hitting it, which keeps it overloaded. Exponential backoff spreads
> the retries out in time so the service gets room to recover.
<!-- /op:conversational -->

## 2. A register ladder for the same move

The move is the same at every level; only the assumed background changes. For one
reader asking why a connection pool helps:

- **Beginner:** "**So what's wrong with opening a connection each time?** Opening
  one is slow — the client and server negotiate and authenticate first — and doing
  that on every request costs more than the query itself."
- **Practitioner:** "**Why not open per request?** Connection setup (TCP, TLS,
  auth, backend session allocation) dominates a short query, so you amortise it by
  reusing a pooled connection."
- **Expert:** stated, not asked. "Setup amortises across requests; the pool size
  caps concurrency and becomes the saturation point under load." An expert does
  not need the question staged.

The ladder's lesson: surface the question for a beginner or practitioner who would
actually ask it, and drop the staging for an expert who would find it slow.

## 3. Direct address: weak and better

**Weak:**
> One configures the pool size according to one's workload.

**Better:**
> You set the pool size to match your workload.

**What changed:** "one" becomes "you", and the reader sees their own action rather
than an impersonal rule. Address the reader as "you" and name what they do.

## 4. Contractions: weak and better

**Weak:**
> It is not that the query is slow; it is that the connection setup is slow.

**Better:**
> It's not that the query is slow; it's that the connection setup is slow.

**What changed:** the contractions match how the sentence would be said aloud. Use
them unless the register is formal or the person asked otherwise.

## 5. What the second voice may not do

The move fails when the question is decoration. Keep these out:

- A question the text does not then answer.
- A question asked to sound lively ("Ever wondered how this works?").
- Praise or reassurance as an opener ("Great question", "simple, right?").
- A staged dialogue between named speakers, or an invented persona.

The test is in `SKILL.md` Step 3: a surfaced question counts only when the content
answers it.
