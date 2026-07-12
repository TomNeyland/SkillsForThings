# Cache-Aware Prompt Architectures

Current source of truth: OpenAI's [Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching).

## Choose the model generation first

| Model generation | Cache boundary | Lifetime control | Write cost |
|---|---|---|---|
| GPT-5.6 and later families | Implicit latest-message breakpoint plus optional explicit breakpoints, or explicit-only mode | `prompt_cache_options.ttl="30m"` sets a minimum lifetime | `cache_write_tokens` billed at 1.25× uncached input rate |
| Earlier supported models | Automatic exact-prefix caching | `prompt_cache_retention` where supported (`in_memory` or `24h`) | No additional cache-write fee |

Do not send GPT-5.6 breakpoint fields to earlier models. Do not use `prompt_cache_retention` as the design model for GPT-5.6+.

## Pattern A: one stable prefix, one variable tail

Use this for repeated independent tasks.

```text
[stable instructions]
[stable tools and output schema]
[stable examples or shared reference material]
---------------- cache boundary ----------------
[request-specific user data and task]
```

Rules:

1. The stable rendered prefix must contain at least 1,024 tokens.
2. Reuse an exact `prompt_cache_key` for the workload.
3. On GPT-5.6+, place an explicit breakpoint after the last stable block when you need a durable boundary.
4. Put IDs, timestamps, per-user content, and request-specific retrieval after the boundary.
5. Log cache reads and writes.

This is usually the simplest architecture because one prefix is warmed and reused across many tasks.

## Pattern B: several reusable stages

Use multiple explicit breakpoints on GPT-5.6+ when a conversation has nested stable regions with different reuse frequency.

```text
[base instructions]                 breakpoint A
[large stable file or knowledge]    breakpoint B
[stable task examples]              breakpoint C
[current question]                  variable tail
```

OpenAI reads the longest matching prefix. A request can create at most four new cache writes. In implicit mode, the latest-message breakpoint consumes one write slot; in explicit mode, four explicit writes are available.

Good reasons for multiple breakpoints:

- many requests share the base instructions, but only one cohort shares the file;
- a long conversation can reuse an earlier stable turn when the newest prefix changed;
- different task families reuse different depths of the same prompt.

Bad reason: marking every block “just in case.” GPT-5.6+ writes are billable. Each breakpoint must earn its write through later reads.

## Pattern C: explicit-only cost control

Set `prompt_cache_options.mode="explicit"` when only selected stable prefixes may be cached.

```python
prompt_cache_options={"mode": "explicit", "ttl": "30m"}
```

With no marker, the request performs no prompt-cache read or write and incurs no cache-write charge. This makes the write policy visible in code and prevents the implicit latest-message breakpoint from writing a prefix that is unlikely to be reused.

Use explicit-only mode for sparse workloads, prompts with large one-off tails, or jobs where cache-write cost needs tight attribution.

## Pattern D: appending conversation

An append-only conversation naturally preserves earlier prefixes. On GPT-5.6+, implicit mode marks the latest message and may also read earlier explicit breakpoints. On earlier models, automatic prefix caching can reuse the unchanged history.

Costs still grow with the input history. Prompt caching discounts reused input; it does not remove prior turns from input accounting. Compaction or editing an earlier turn creates a new rendered prefix.

Use this pattern when conversation history is semantically necessary. Prefer Pattern A for independent tasks.

## Stable tail reminders

A short static reminder immediately before the variable task can improve prompt salience while remaining part of a reusable prefix. On GPT-5.6+, place the breakpoint after the reminder if it should be cached. Any request-specific value inside the reminder turns it into changing content and reduces reuse.

Do not call the reminder “free.” GPT-5.6+ bills the write; the reminder earns its place only when later cache reads amortize that write.

## Keys and traffic partitioning

Choose keys by **shared prefix**, not by individual request:

```python
prompt_cache_key = f"tenant:{tenant_id}:knowledge-base-v3"
```

Keep total traffic per key near the documented approximately 15 requests per minute. For more volume, partition with a stable mapping:

```python
prompt_cache_key = f"tenant:{tenant_id}:knowledge-base-v3:shard-{stable_shard}"
```

Random per-call keys destroy routing reuse. One global hot key spills traffic to other machines.

Do not assume caches transfer across model families. If a workflow changes models, measure each model/key/prefix path independently.

## Write/read break-even on GPT-5.6+

For a prefix of `W` written tokens:

```text
write cost = W × 1.25 × uncached input rate
savings per cached read = W × (uncached input rate − cached input rate)
```

The prefix pays off only after accumulated read savings exceed its write cost. Use actual `cache_write_tokens` and `cached_tokens`; do not assume the entire prompt was written or read.

Earlier models have no additional cache-write fee, but still require enough repeated reads to make the prompt architecture worth its complexity.

## Measurement loop

For each workload key:

1. Log total input tokens, `cache_write_tokens`, and `cached_tokens` per request.
2. Attribute writes and reads to the breakpoint/prefix version.
3. Compare write cost with later read savings.
4. Move the breakpoint earlier when one-off content is being written.
5. Move it later only when the additional stable content is repeatedly read.
6. Split a hot key when its total traffic exceeds the documented routing guidance.

The completion condition is economic, not aesthetic: stable prefixes are read often enough to repay their writes, and variable content never sits before the intended boundary.
