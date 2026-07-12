# OpenAI Prompt Cache: Footgun Catalog

Current source of truth: OpenAI's [Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching). Each entry names the cause, visible symptom, and direct fix.

## Prefix-shape failures

### Changing data before the stable boundary

- **Cause:** timestamps, request IDs, tenant values, retrieved chunks, or user state appear before reusable instructions and examples.
- **Symptom:** `cached_tokens` is zero or far below the expected stable prefix.
- **Fix:** move changing content to the tail. On GPT-5.6+, place an explicit breakpoint immediately after the reusable stable region.

### Prefix below 1,024 tokens

- **Cause:** the rendered prefix ending at the implicit or explicit breakpoint is too short.
- **Symptom:** `cached_tokens: 0` even though every byte matches.
- **Fix:** combine genuinely reusable content before the breakpoint or accept that the request is not cacheable. Do not add meaningless padding.

### Tool or schema byte drift

- **Cause:** per-call regeneration changes key order, field order, descriptions, or the tool list.
- **Symptom:** logically identical requests miss after a deploy or dependency update.
- **Fix:** serialize deterministically, snapshot the result, and fail CI when stable tool or schema bytes drift.

### RAG chunks arrive in a different order

- **Cause:** retrieval returns the same shared documents in nondeterministic order.
- **Symptom:** the reusable prefix ends at the first reordered chunk.
- **Fix:** sort genuinely shared chunks by a stable identifier before the breakpoint. Keep request-specific retrieval after the stable boundary.

### Image settings change

- **Cause:** image data, URL, ordering, or `detail` changes.
- **Symptom:** otherwise identical multimodal requests miss.
- **Fix:** keep all image inputs before the breakpoint identical, including `detail`; put changing images after the reusable boundary.

## GPT-5.6+ control failures

### Omitting `prompt_cache_key`

- **Cause:** relying on automatic routing without a workload key.
- **Symptom:** occasional automatic hits but inconsistent matching across repeated requests.
- **Fix:** set and consistently reuse `prompt_cache_key`. GPT-5.6+ requires it for the more reliable matching path.

### One key receives too much traffic

- **Cause:** total traffic for a key substantially exceeds approximately 15 requests per minute.
- **Symptom:** requests spill to other machines and some miss.
- **Fix:** partition into more stable keys. Requests that should share a prefix must continue to map to the same key.

### Explicit mode without a breakpoint

- **Cause:** `prompt_cache_options.mode="explicit"` but no content block has `prompt_cache_breakpoint`.
- **Symptom:** no cache read, no cache write, and both usage fields remain zero.
- **Fix:** add a marker after the stable content, or use implicit mode intentionally.

### Marker on the wrong block

- **Cause:** applying a breakpoint to an unsupported content type or using a mode other than `explicit` on the marker.
- **Symptom:** `400 invalid_request_error`.
- **Fix:** use only documented blocks: Responses `input_text`/`input_image`/`input_file`; Chat Completions `text`/`image_url`/`input_audio`/`file`/`refusal`.

### Too many new write candidates

- **Cause:** expecting every marker in a long conversation to be written again.
- **Symptom:** only the latest eligible breakpoints become new cache writes.
- **Fix:** design around the four-new-writes-per-request limit. Implicit mode reserves one slot for the latest message; explicit mode can use four explicit writes. Earlier-turn breakpoints are read-only.

### Treating `ttl` as a maximum or storage policy

- **Cause:** reading `prompt_cache_options.ttl="30m"` as “delete at 30 minutes” or as the replacement name for `in_memory`/`24h`.
- **Symptom:** incorrect eviction and compliance assumptions.
- **Fix:** treat `30m` as the minimum eligible lifetime for GPT-5.6+ breakpoints. It is the only supported value and the default; OpenAI may retain the prefix longer.

### Ignoring cache-write billing

- **Cause:** optimizing only for `cached_tokens` as if writes were free.
- **Symptom:** a workload repeatedly pays cache writes at 1.25× uncached input cost without enough later reads to recover the charge.
- **Fix:** log `cache_write_tokens` and `cached_tokens`; move or remove breakpoints whose writes are not amortized.

## Earlier-model control failures

### Sending GPT-5.6 fields to an earlier model

- **Cause:** using `prompt_cache_options` or `prompt_cache_breakpoint` on a pre-GPT-5.6 model.
- **Symptom:** the request is rejected.
- **Fix:** use that model's automatic prompt caching and `prompt_cache_retention` where supported.

### Reusing obsolete retention guidance

- **Cause:** assuming every GPT-5-era model has the same default or supports the same policies.
- **Symptom:** invalid parameters or a cache lifetime different from the workload design.
- **Fix:** check the official support list and set `prompt_cache_retention` explicitly when available. `gpt-5.5` and `gpt-5.5-pro` accept only `24h`; GPT-5.6+ uses `prompt_cache_options.ttl` instead.

## Measurement failures

### Reading the wrong usage path

- **Cause:** using the Chat Completions path on a Responses object or vice versa.
- **Symptom:** dashboards report zero even when the API returned cache activity.
- **Fix:** read `usage.prompt_tokens_details` on Chat Completions and `usage.input_tokens_details` on Responses. Log both `cached_tokens` and, on GPT-5.6+, `cache_write_tokens`.

### Testing with one request

- **Cause:** treating a cold call as proof of broken caching.
- **Symptom:** false diagnosis before any reusable prefix has been written and routed.
- **Fix:** test a representative sequence with the same key and exact prefix; compare writes and later reads.

### Forecasting from discounts without measuring writes

- **Cause:** multiplying input tokens by a cached-input price while assuming every eligible token is read from cache.
- **Symptom:** real cost exceeds the forecast.
- **Fix:** calculate from observed uncached input, `cache_write_tokens`, and `cached_tokens` separately.

## Community-reported compatibility checks

These are useful diagnostics, not official contracts:

- **Responses `instructions`:** users reported weaker reuse than placing the same text in a leading `developer` input item ([thread 1346849](https://community.openai.com/t/problem-caching-system-prompt/1346849)). If a workload misses, compare both shapes and inspect `cached_tokens`.
- **Some pre-GPT-5.6 model paths:** user measurements reported inconsistent caching on mini, nano, GPT-5.4, and GPT-5.5 variants ([thread 1368208](https://community.openai.com/t/possible-cache-issue-on-gpt-5-mini-and-gpt-5-nano/1368208), [thread 1384129](https://community.openai.com/t/prompt-cache-documented-byte-prefix-matching-does-not-occur-on-gpt-5-4-gpt-5-5-when-trailing-user-content-exceeds-500-tokens/1384129)). Instrument the selected model rather than applying those reports as universal rates.

Do not carry those older-model anecdotes forward as claims about GPT-5.6+. The official guide documents a different matching and breakpoint system for GPT-5.6 and later families.
