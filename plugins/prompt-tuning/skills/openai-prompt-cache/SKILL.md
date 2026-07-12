---
name: openai-prompt-cache
description: Use when designing or auditing OpenAI API prompts for cache hit rate. Triggers on debugging cost spikes from cache misses, slow first-token latency on repeated prompts, schema/grammar/tool regeneration silently killing cache, or building systems with large reused prefixes (RAG pipelines, agent loops, structured extraction, batch jobs). Applies to Chat Completions and Responses API, JSON Schema and Lark grammar enforcement.
---

# OpenAI Prompt Cache Optimization

## Overview

OpenAI's prompt cache can reduce the cost and latency of repeated prompt prefixes. The cache is a
**prefix cache**: it reuses the longest exact prefix available on the routed inference engine.
Anything that changes the rendered prefix ends reuse at that point. Rates, write charges, retention
controls, and breakpoint support vary by model family; verify them against the current official
[prompt-caching guide](https://developers.openai.com/api/docs/guides/prompt-caching).

The skill is the discipline of:
1. Getting stable content above the **1,024-token minimum**
2. Putting it at the **head of the rendered prefix**, byte-stable
3. Putting all dynamic content in the **tail**
4. Choosing the **automatic or explicit-breakpoint path** for the target model
5. **Measuring** cache reads and writes to verify

## When to use

- Designing a prompt that will be called repeatedly (>10×/hour, or any reused-system-prompt pattern)
- Cost has spiked unexpectedly on a workload that should be cache-friendly
- First-token latency is high on calls that share most of their input
- Migrating between Chat Completions and Responses API and needing to preserve a cacheable prefix
- Adding/changing a `response_format` JSON schema or Lark grammar
- Auditing a tool-using agent loop where every turn re-sends large state

## When NOT to use

- One-shot prompts under 1,024 tokens (cache literally cannot hit)
- Prompts where every byte legitimately varies per call (no shared prefix to optimize)
- Prototypes / exploratory eval where total cost and latency don't matter

## Universal laws (apply regardless of API surface)

| Property | Value |
|---|---|
| Minimum cacheable prefix | **1,024 tokens** |
| Routing hash window | First **~256 tokens** (varies by model) + `prompt_cache_key` |
| GPT-5.6+ retention control | `prompt_cache_options.ttl`; current default and only value is **`30m` minimum lifetime**; OpenAI may retain longer |
| Earlier-model retention control | `prompt_cache_retention`; `in_memory` is typically 5–10 min idle (up to 1 hr), while supported extended policies retain up to 24 hr |
| GPT-5.6+ write accounting | Cache writes cost **1.25× uncached input** and appear in `cache_write_tokens`; reads appear in `cached_tokens` |
| Throughput per (prefix, key) bucket | **~15 RPM** before overflow to cold engines (OpenAI cookbook) |
| Isolation | Caches are not shared between organizations |

## The optimization workflow

1. **AUDIT.** Identify genuinely reusable content. Is the rendered reusable prefix at least 1,024
   tokens? If not, accept zero cache or consolidate real shared context; never add meaningless padding.

2. **STRUCTURE.** Order content so dynamic stuff lands at the tail. Wire prefix sequence is forced:
   ```
   tools / schema → developer or system content → few-shots → changing user input
   ```

3. **STABILIZE.** Make the prefix byte-identical across calls.
   - Tool definitions: `json.dumps(..., sort_keys=True)`, snapshot at startup, never re-generate per call
   - JSON schemas: snapshot serialized bytes to disk, fail CI on drift
   - Lark grammars: snapshot the `definition` string, hash-log per call
   - RAG chunks: sort by stable doc id BEFORE splicing
   - Few-shots: fixed order, no shuffling

4. **ROUTE.** Set `prompt_cache_key` per logical workload. GPT-5.6+ requires it for the more reliable
   cache-matching path. Shard the key with a stable mapping to keep each key around 15 RPM.

5. **CHOOSE THE MODEL-FAMILY PATH.**
   - **GPT-5.6 and later:** automatic caching still works, but explicit breakpoints make the write
     boundary controllable. Put `prompt_cache_breakpoint: {"mode":"explicit"}` after stable content;
     set `prompt_cache_options.mode="explicit"` only when every write must be explicit. The current
     `prompt_cache_options.ttl` default/only value is `30m`.
   - **Earlier models:** continue using automatic prefix caching and, where supported, configure
     `prompt_cache_retention` (`in_memory` or `24h`). Do not send GPT-5.6 breakpoint fields to older
     models; they reject them.

6. **MEASURE.** Read `cached_tokens` after every call. On GPT-5.6+, also read
   `cache_write_tokens` and compare billed writes with later reads. Field paths differ by API surface.

## Quick reference: API surface differences

| Surface | Cache usage fields | Notable quirk |
|---|---|---|
| Chat Completions | `usage.prompt_tokens_details.cached_tokens`; GPT-5.6+ `cache_write_tokens` is its sibling | Wire prefix order forced (tools → schema → messages) |
| Responses | `usage.input_tokens_details.cached_tokens`; GPT-5.6+ `cache_write_tokens` is its sibling | GPT-5.6+ breakpoints can mark `input_text`, `input_image`, and `input_file` blocks |
| JSON Schema | (same as host API) | Structured-output schemas are part of the cacheable prefix |
| Lark grammar | (same as host API) | Stabilize the exact grammar definition and verify reads on the host API |

## Common mistakes (highest-impact first)

| Mistake | Fix |
|---|---|
| Timestamps in system prompt | Move to `metadata` (out-of-band, doesn't enter prefix) |
| Regenerating Pydantic schemas per call | Snapshot to disk; fail CI when bytes drift |
| Reordering RAG chunks per call | Sort by stable doc id before splicing |
| Tool JSON without `sort_keys=True` | Pin canonical serialization once at startup |
| Mutating `tools` array to gate availability | Use `tool_choice={"type":"allowed_tools",...}` |
| Reading `prompt_tokens_details.cached_tokens` on Responses | Path is `input_tokens_details.cached_tokens` on Responses |
| Assuming the advertised cached-input rate guarantees hits | Measure the chosen model and API directly; log reads and, on GPT-5.6+, billed writes before forecasting savings |
| Dynamic `Field(description=f"As of {today}...")` | Strip dynamic content from descriptions; move to user message |

## Cost tradeoff

On GPT-5.6+, a cache write is billable. Place explicit breakpoints only after stable content that is
likely to be reused, then compare `cache_write_tokens` on the writing request with `cached_tokens`
on subsequent requests. A breakpoint that is continually rewritten but rarely read is not saving
money.

## Validation: confirm the cache is hitting

```python
# Chat Completions
resp = client.chat.completions.create(...)
print(resp.usage.prompt_tokens_details.cached_tokens, "/", resp.usage.prompt_tokens)

# Responses API
resp = client.responses.create(...)
print(resp.usage.input_tokens_details.cached_tokens, "/", resp.usage.input_tokens)

# GPT-5.6+ write accounting (same detail object on either API)
resp = client.responses.create(...)
print(resp.usage.input_tokens_details.cache_write_tokens)
```

Run repeated identical-prefix calls. On GPT-5.6+, confirm the first eligible request reports a write
and later requests report reads. Do not conclude from a single request or from pricing tables alone.

## Deep reference

- `references/mechanics.md` — how the cache actually works (routing, hashing, TTL, eviction)
- `references/footguns.md` — exhaustive catalog of cache killers
- `references/by-surface.md` — Chat Completions, Responses, JSON Schema, Lark grammar specifics
- `references/architecture-patterns.md` — structured-vs-unstructured tradeoffs, long-conversation vs [stable prefix + variable tail], multi-model with shared schema
