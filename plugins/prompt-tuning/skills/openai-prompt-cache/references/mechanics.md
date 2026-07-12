# OpenAI Prompt Cache: Mechanics

Reference for the `openai-prompt-cache` skill. Covers what gets hashed, how routing works, TTL, pricing, reporting, and known regressions.

## What gets hashed

The cache is a **prefix cache** that matches the longest exact byte-prefix of your request against an inference engine's in-memory KV state. The hash window for routing is the first ~256 tokens; actual cache reuse extends to the longest exact prefix shared with the engine.

**Wire prefix order on Chat Completions** (forced, not configurable):
1. `tools[]` — full JSON serialization
2. `response_format` schema
3. `messages[]` — developer/system first, then user/assistant turns

**On Responses API**: same general order with `tools` → `text.format` → `input` items. Note the `instructions` parameter is community-reported as NOT reliably entering the cached prefix — use a `developer` role item in `input` instead.

Everything in the prefix is hashed byte-for-byte after serialization: messages, tool definitions (name, description, parameters JSON), `response_format` JSON schema, image bytes/URLs, audio.

## Quantization

- **Minimum prefix: 1,024 tokens.** Below this floor, `cached_tokens: 0` always.
- **Beyond the floor: 128-token granularity.** A 1,500-token shared prefix yields `1024 + 3*128 = 1408` cached tokens, not 1500.

## TTL / retention

`prompt_cache_retention` takes two policies: `in_memory` and `24h`. **As of 2026-05-29 the default flipped** — non-ZDR orgs on the GPT-5 series now default to **`24h`**, not `in_memory` ([prompt-caching guide](https://developers.openai.com/api/docs/guides/prompt-caching); corroborated [TheRouter, 2026-05-29](https://therouter.ai/news/openai-extended-prompt-cache-24h-default-gpt5-operator-routing/)).

- **`in_memory` policy:** 5–10 min idle, 1 hour hard cap. Activity refreshes the idle clock until cap.
- **`24h` (Extended Prompt Caching):** retains KV state up to 24h. **Permitted under Zero Data Retention** — the guide states extended-retention requests "are not blocked if Zero Data Retention is enabled" (it stores derived KV tensors, not content, expiring ≤24h). ZDR orgs still *default* to `in_memory`, but `24h` is allowed. *(Correction: earlier versions of this skill said 24h was "incompatible with ZDR" — that is refuted by current docs.)*
- **gpt-5.5 / gpt-5.5-pro and future models:** only `24h` is supported (guide: "For `gpt-5.5`, `gpt-5.5-pro`, and future models, only `24h` is supported"). Secondary sources report passing `in_memory` errors; the doc only asserts 24h is the sole supported value.
- **No manual purge endpoint.**

## Routing & `prompt_cache_key`

Engines are sharded; the routing key is `hash(first ~256 tokens) + prompt_cache_key + model_snapshot`. `prompt_cache_key` makes routing sticky — it does NOT change cache key composition, just makes hits more likely by pinning related requests to the same engine.

**Per-bucket throughput cap: ~15 RPM.** Above that, requests overflow to additional engines that haven't seen the prefix → cache miss. Shard `prompt_cache_key` (e.g., `f"workflow-v3-shard-{i%N}"`) to scale wide. This figure is **OpenAI-documented** ([Prompt Caching 201 cookbook](https://developers.openai.com/cookbook/examples/prompt_caching_201)), not community-inferred.

OpenAI's [Prompt Caching 201 cookbook](https://developers.openai.com/cookbook/examples/prompt_caching_201) reports an (unnamed) coding customer's hit rate improving from **60% → 87%** after adopting `prompt_cache_key`.

## Isolation

- **Per organization** — caches not shared cross-org (docs: "Prompt caches are not shared between organizations").
- **Per model snapshot** — `gpt-5.1` (alias) and `gpt-5.1-2026-XX-XX` (dated) are different cache scopes; alias rotations create cache misses.
- **Per region** — Regional Inference data stays in-region; default routing's region partitioning is undocumented.
- **Per inference instance RAM** — single-engine-local; not a shared key-value store.
- **Possibly shared across sibling models — but evidence is thin.** A **single unverified HN self-report** ([46070749](https://news.ycombinator.com/item?id=46070749), harsharanga, 2025-11-27, 5 points, **0 comments**) primed a 1,400-token prefix on gpt-4o-mini, then got a cache hit on the *first* call to gpt-5-mini with the identical prefix. The author's own framing: *"prefix-processing cache sharing, not KV-cache sharing. Models share tokenization and prefix hashing, not attention states."* The test used the **Chat Completions** `cached_tokens` field. This is one anecdote with no corroboration, and contemporaneous threads report cache being *model-specific and flaky* — treat "share the key across siblings" as an untested hypothesis, not a rule. **If you try it:** use one `prompt_cache_key` across siblings and measure `cached_tokens` before depending on it.

## Pricing (June 2026 snapshot)

Source: [OpenAI pricing](https://developers.openai.com/api/docs/pricing) + [Prompt Caching 201](https://developers.openai.com/cookbook/examples/prompt_caching_201), observed 2026-06-28. The lineup moved two releases past the old "May 2026" snapshot: **gpt-5.5 is the flagship**, **gpt-5.4** is the production tier, and gpt-5.1 / gpt-5 are now **legacy** (still sold, no longer flagship). Pin a dated snapshot in production regardless.

| Model | Standard input ($/1M) | Cached input ($/1M) | Discount |
|---|---|---|---|
| gpt-5.5 (flagship) | $5.00 | $0.50 | **90%** |
| gpt-5.5-pro | $30.00 | (no cache) | — |
| gpt-5.4 | $2.50 | $0.25 | **90%** |
| gpt-5.4-mini | $0.75 | $0.075 | 90% |
| gpt-5.4-nano | $0.20 | $0.02 | 90% |
| gpt-5.2 (legacy) | $1.75 | $0.175 | 90% |
| gpt-5.1, gpt-5 (legacy) | $1.25 | $0.125 | **90%** |
| gpt-5-mini | $0.25 | $0.025 | 90% |
| gpt-5-nano | $0.05 | $0.005 | 90% |
| gpt-4.1 | $2.00 | $0.50 | **75%** |
| gpt-4o | $2.50 | $1.25 | **50%** |
| gpt-realtime (audio) | $32.00 | $0.40 | **98.75%** |

The o-series (o3, o4-mini), o1, and gpt-4o-mini rows from the old snapshot **no longer appear on the live pricing page** (older-models section or removed) — treat their cached rates as unverified. The discount *structure* still holds: 90% for all gpt-5.x, 75% for o-series and gpt-4.1, 50% for gpt-4o/o1. The cookbook's rationale, verbatim: "as our inference stack has become more efficient, our newest models have been able to offer steeper cache discounts."

**New cache-write billing on GPT-5.6+.** For **GPT-5.6 and later models** (previewed 2026-06-26), cache *writes* are billed at **1.25× the uncached input rate** (they were previously free); cache *reads* keep the 90% discount ([Simon Willison, 2026-06-26](https://simonwillison.net/2026/Jun/26/openai/)). This mirrors Anthropic's cache-write surcharge and changes the break-even math: a prefix must now be re-read enough times to amortize a 1.25× write, not just any reuse. Doesn't apply to ≤gpt-5.5.

**Service tier interaction:** cached pricing on `flex` and `batch` applies the same discount percentage to those tiers' cheaper base rates. The cookbook author reports a head-to-head test (10,000 identical requests) where **flex showed ~8.5% higher cache hit rate than batch** — an OpenAI-published-author anecdote, not a formal OpenAI benchmark. (Batch scheduling defeats routing stickiness — jobs go to whichever engine is free.) Note **Batch now supports caching for GPT-5-and-newer**; pre-GPT-5 models (o3, o4-mini) get no Batch cache.

## Reporting

| API | Field |
|---|---|
| Chat Completions | `usage.prompt_tokens_details.cached_tokens` |
| Responses | `usage.input_tokens_details.cached_tokens` |

`cached_tokens` is a subset of total input tokens, not a separate bucket. Present on every response (including those below the 1,024-token floor, where it's always 0). No HTTP header confirms a cache hit.

## What invalidates the cache

Any byte change in the prefix: model snapshot drift, tool definition reorder/rename, schema field rename, system prompt edit, RAG chunk reshuffle, timestamp injection, JSON serialization key-order drift, image `detail` parameter changes.

**Sampling parameters** (`temperature`, `top_p`, `seed`, `n`) do NOT invalidate (community-inferred — undocumented, but consistent with cache being prompt-only and KV-state being deterministic per prefix).

**`service_tier` switching** — *unverified.* No doc or thread ties `service_tier` to cache-pool routing; the hypothesis that switching tiers lands you on a different pool is plausible (it changes scheduling) but unsourced. Pin tier per workload as a precaution, but don't treat the cache penalty as established.

**`reasoning.effort` changes** — *unverified inference.* No source documents this busting the cache; it's plausible because effort is part of the request signature, but treat as inference, not fact.

## Schema-compile cache (independent mechanism)

When using `response_format={"type":"json_schema",...}` with `strict: true`, OpenAI compiles the schema into a constrained-decoding state machine. This compile result is cached **independently** of the prompt cache:

- **TTL:** *unknown.* The "~120s idle" figure has **no source** — [Sophia Willows](https://sophiabits.com/blog/openai-structured-outputs-deep-dive) (the author of the canonical deep-dive) explicitly writes the warm duration is undocumented and an open question. Treat 120s as an unverified guess; the only documented retention numbers are for the *token* prompt cache (5–10 min / 24h), a different mechanism.
- **Scope:** the documented "not shared between organizations" line is about the *prompt* cache. Sophia Willows's observational "global" claim (zero compile latency on OpenAI's published `MathResponse` schema) is about the *schema-compile* cache and is consistent with OpenAI internally pre-warming their own published example schemas — does not generalize to your schemas.
- **Cross-model behavior within an org:** **NOT empirically measured in public research.** Theoretically a CFG is model-independent (depends on tokenizer, not weights), so if a model family shares a tokenizer the compile artifact *could* transfer — but with the gpt-5-mini/nano cache regressions (see below), don't assume the schema cache transfers cleanly across siblings.
- **First-call latency:** 10–60s typical, up to minutes on complex enums (docs language has narrowed since the older "10s–10min" claim).
- **Not billed** (wall-clock only)
- **No pre-warm endpoint** — fire one cheap call per (model, schema) pair before a batch starts.
- **Fine-tuned models:** docs say only FT models incur first-call delay, but community measurements show 10s delays on stock gpt-4.1-nano too. Treat every (model, schema) pair as potentially incurring 10–60s when the org-wide cache is cold.

Lark grammars do NOT have a documented compile cache, but exhibit ~8–10× per-call latency overhead with CFG enabled. Origin opaque (compile, mask integration, or API plumbing). Don't extrapolate the JSON-schema cache story to custom-tool grammars.

## Cache warmup behavior

A new prefix takes **2–10 calls** and **17–450 sec** to reach steady-state hits (community-measured). Single-call repros for cache health are noise. Run 20+ identical-prefix calls before concluding the cache is broken or working.

## Known model regressions (open as of 2026-06-27)

The mini and nano families have systematically lower cache hit rates than the full models. Independent measurement — DavidDev, 120 tests/model, reported **without → with `prompt_cache_key`** — lives in [community thread 1368208](https://community.openai.com/t/possible-cache-issue-on-gpt-5-mini-and-gpt-5-nano/1368208) (Dec 2025), *not* the "caching is borked" thread sometimes cited:

| Model | Cache miss rate (no key → with key) |
|---|---|
| **GPT-5.1** | **19% → 6%** (best — recommended for cost-tier routing) |
| GPT-5-nano | 25% → 28% |
| GPT-5.2 | 45% → 30% |
| **GPT-5-mini** | **72% → 76%** (worst) |

**Adding `prompt_cache_key` made gpt-5-mini and gpt-5-nano *worse*** in DavidDev's tests (verbatim: "using prompt_cache_key doesn't have any effect at all in mini and nano, making them even slightly worse") — signal the routing layer treats those families differently. For cost-sensitive paths needing reliable cache, **gpt-5.1 is the only consistently-caching small-class model** in current data.

**The issue is unresolved and broadening — still live as of 2026-06-27.** It now affects the flagship tier:
- gpt-5.4-nano returns a **0% hit rate** on prompts that hit >90% on gpt-5.4-mini ([thread 1379973, OP 2026-04-28](https://community.openai.com/t/switching-to-gpt5-4-nano-results-in-0-cache-hit-rate/1379973)).
- gpt-5.5 / gpt-5.4: **persistent 0% hits** with large stable prefixes — `cached_tokens` reported as 0 when ~180K should be cached ([thread 1383838, OP 2026-06-16](https://community.openai.com/t/persistent-0-prompt-cache-hits-on-gpt-5-5-with-auckland-nz-cloudflare-520s-complicating-every-workaround/1383838)).
- On gpt-5.4 / gpt-5.5, byte-prefix matching **fails when trailing user content exceeds ~500 tokens** — ~99% hit below, ~0% above ([thread 1384129, OP 2026-06-19](https://community.openai.com/t/prompt-cache-documented-byte-prefix-matching-does-not-occur-on-gpt-5-4-gpt-5-5-when-trailing-user-content-exceeds-500-tokens/1384129)). The ~500-token cutoff is single-sourced (OP shubh49); the *direction* is corroborated (dreamer_93: "for 5.4, only the system instructions are cached"). The OP reports the **Responses API is unaffected** while chat.completions breaks — but that escape hatch is **uncorroborated and partly contradicted** (thread 1383838's OP saw 0% on *both* APIs). Verify with your own `cached_tokens` before relying on a Responses fallback.

**No official acknowledgment.** Status page and changelog show nothing on gpt-5 caching. A staff "this issue has since been resolved" reply exists ([thread 1383465, OpenAI_Support, 2026-06-12](https://community.openai.com/t/prompt-caching-broken-for-gpt-5-4-and-5-5/1383465)) but refers to a separate June 12–13 error incident, not the byte-prefix regression — and that OP still had an open case the next day. No confirmed fix or `prompt_cache_retention` workaround for the existing models.

**The claimed fix lands in GPT-5.6, not the current models.** GPT-5.6 (Sol/Terra/Luna, previewed 2026-06-26, gated to ~20 partners) announces "**more predictable prompt caching, including support for explicit cache breakpoints and a 30-minute minimum cache life**." Billing changes with it: **cache *writes* are billed at 1.25× the uncached input rate** (previously free) while cache *reads* keep the 90% discount — for "GPT-5.6 and later models" ([Simon Willison, 2026-06-26](https://simonwillison.net/2026/Jun/26/openai/); [OpenAI Help Center](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna)). This is OpenAI's marketing claim, **unverified by independent users** (access is gated). Net: shipping models (5.4/5.5/mini/nano) have **no relief yet** as of 2026-06-28.

If you depend on these for cost-tier routing, instrument `cached_tokens` and don't trust the discount line in your forecast.

## Stateful billing trap (Responses API)

When using `previous_response_id`, every prior input token is **re-billed as input on every call** — the conversation chain doesn't get "compressed" server-side. Caching is what makes this affordable. Without cache hits, multi-turn `previous_response_id` is strictly more expensive than a single-shot prompt.
