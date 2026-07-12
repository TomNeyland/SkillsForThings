# OpenAI Prompt Cache: Mechanics

Current source of truth: OpenAI's [Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching). This reference separates GPT-5.6-and-later behavior from earlier models because the controls and billing differ.

## Universal mechanics

Prompt caching is available on recent models (`gpt-4o` and newer) and is automatic for eligible prompts.

- A cache hit requires an **exact prompt-prefix match**. Put stable instructions, examples, images, files, and tools first; put changing content last.
- The rendered cacheable prefix must contain at least **1,024 tokens**. Requests below the floor still report `cached_tokens`, but it is zero.
- Routing normally hashes an initial prefix, typically the first **256 tokens**; the exact length varies by model.
- `prompt_cache_key` is combined with that prefix hash. Reuse one stable key for requests that share a long common prefix.
- Keep traffic for a key at approximately **15 requests per minute**. Use more keys with a stable partitioning rule when traffic is higher.
- A hit reduces latency and bills the reused tokens at the model's cached-input rate. It does not reuse an old response; output generation still runs normally.

OpenAI can cache messages, images, files, tools, and structured-output schemas. Images and tools must remain identical between matching requests; image `detail` changes tokenization.

## GPT-5.6 and later model families

GPT-5.6+ adds reliable matching, explicit breakpoints, a new TTL control, and cache-write billing.

### Key requirement

Set `prompt_cache_key` to use the more reliable matching path for both implicit and explicit caching. Requests without a key may still receive automatic hits, but do not use the improved matching.

### Implicit and explicit breakpoints

`prompt_cache_options.mode` controls request-wide behavior:

- `implicit` (default): OpenAI places a breakpoint on the latest message and also uses explicit breakpoints supplied by the request.
- `explicit`: only supplied breakpoints are used. With no explicit breakpoint, the request performs no prompt-cache read or write and incurs no cache-write charge.

Mark a supported content block with:

```json
"prompt_cache_breakpoint": {"mode": "explicit"}
```

The marker includes that block and everything rendered before it in the cacheable prefix. Content after the marker may change without invalidating that prefix. Only `explicit` is valid as a breakpoint mode; an unsupported block returns `400 invalid_request_error`.

Breakpoint limits:

- At most **four new cache writes** per request.
- In implicit mode, the latest-message breakpoint consumes one write slot, leaving up to three new explicit writes.
- In explicit mode, up to four new explicit writes can be created.
- Breakpoints from earlier conversation turns may be read but are not written again.
- Cache lookup considers up to the latest **50 breakpoints** and uses the longest matching prefix.
- Every marked prefix still needs at least 1,024 rendered tokens.

Supported breakpoint blocks:

| API | Blocks |
|---|---|
| Responses | `input_text`, `input_image`, `input_file` |
| Chat Completions | `text`, `image_url`, `input_audio`, `file`, `refusal` |

### TTL and retention

`prompt_cache_options.ttl` sets a **minimum lifetime** for all breakpoints written by the request. The only supported value is `30m`, which is also the default. A prefix remains eligible for at least 30 minutes and may be retained longer.

This field is not a storage-policy selector and does not set a maximum retention period. `prompt_cache_retention` is deprecated for GPT-5.6+.

### Write billing and reporting

Cache writes are billed at **1.25× the uncached input-token rate**. Reads remain billed at the model's cached-input rate.

- `cache_write_tokens`: prompt tokens written to cache.
- `cached_tokens`: prompt tokens read from cache.

Log both. A high write count with few later reads can cost more than leaving the prefix uncached.

## Models before GPT-5.6

Earlier models reject `prompt_cache_options` and `prompt_cache_breakpoint`. Continue using automatic prefix caching and `prompt_cache_retention` where the model supports it.

- `in_memory`: usually 5–10 minutes of inactivity, up to one hour.
- `24h`: extended retention, up to 24 hours, on the models listed in the current OpenAI guide.
- `gpt-5.5` and `gpt-5.5-pro` accept only `24h` through `prompt_cache_retention`.

Do not generalize one retention default across all earlier models or organization policies. Set `prompt_cache_retention` explicitly when the chosen model supports the policy you need, and confirm current support in the official guide.

Cache writes on models before GPT-5.6 have **no additional fee**. These models report cache reads through `cached_tokens`; they do not use the GPT-5.6+ explicit-breakpoint write model.

## Usage fields

| API | Read field | GPT-5.6+ write field |
|---|---|---|
| Chat Completions | `usage.prompt_tokens_details.cached_tokens` | `usage.prompt_tokens_details.cache_write_tokens` |
| Responses | `usage.input_tokens_details.cached_tokens` | `usage.input_tokens_details.cache_write_tokens` |

`cached_tokens` is part of total input tokens, not an additional token bucket. No HTTP header is required to identify a hit.

## What invalidates reuse

Any change before a matched breakpoint can shorten or eliminate the hit:

- changing or reordering tools;
- changing a structured-output schema;
- editing earlier messages or examples;
- reshuffling shared retrieval content;
- injecting timestamps or request IDs into the stable prefix;
- changing image content or `detail`;
- changing serialization bytes for logically equivalent JSON.

For GPT-5.6+, put explicit breakpoints immediately after reusable stable regions so later request-specific content cannot invalidate them.

## Privacy and cache clearing

Prompt caches are not shared between organizations. Cache data handling depends on model and retention policy; consult OpenAI's data-controls documentation for ZDR and residency requirements.

There is no manual cache-clear endpoint.

## Community evidence: older-model reliability

Community reports from 2025–2026 documented low or inconsistent hit rates on some pre-GPT-5.6 mini, nano, GPT-5.4, and GPT-5.5 paths, including [thread 1368208](https://community.openai.com/t/possible-cache-issue-on-gpt-5-mini-and-gpt-5-nano/1368208) and [thread 1384129](https://community.openai.com/t/prompt-cache-documented-byte-prefix-matching-does-not-occur-on-gpt-5-4-gpt-5-5-when-trailing-user-content-exceeds-500-tokens/1384129). These are user measurements, not an official model contract. They do not override the official GPT-5.6+ behavior described above.

When an earlier-model workload depends on caching, log `cached_tokens` over a representative run instead of forecasting from list pricing alone.
