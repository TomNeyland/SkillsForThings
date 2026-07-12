# Cache Behavior By API Surface

Reference for the `openai-prompt-cache` skill. Cache mechanics differ across API surfaces in load-bearing ways.

## Chat Completions API (`/v1/chat/completions`)

**Cache-hit field:** `usage.prompt_tokens_details.cached_tokens`

**Wire prefix order (forced):** `tools[]` → `response_format` → `messages[]` (developer/system first).

**Stateless** — every call re-sends full conversation. Cache is your only deduplication mechanism for shared prefix.

**`stream_options={"include_usage": true}`** required to get usage in streaming responses (delivered in final chunk).

**`n>1`** — prefix shared across n samples, billed once. `cached_tokens` reflects the (single) prompt.

**Quirks:**
- The `user` field used to be a cache-routing hint. That role has since **split**: `prompt_cache_key` for routing, `safety_identifier` for abuse signals. The "July 31, 2025" date is community-sourced ([thread 1267103](https://community.openai.com/t/prompt-cache-routing-the-user-parameter/1267103)), not confirmed on an official changelog — the parameter split itself is documented, the exact date is not.
- `parallel_tool_calls=true|false` is part of the request body — keep stable.

## Responses API (`/v1/responses`)

**Cache-hit field:** `usage.input_tokens_details.cached_tokens` (NOT `prompt_tokens_details` — different from Chat Completions). Cost-tracking code that hardcodes the Chat Completions path will silently report 0 cached tokens against Responses.

**Stateful via `previous_response_id`** — server expands the chain into the same prefix tokens you would have sent yourself. The cache key is the rendered prefix; `previous_response_id` is not a "cache pointer."

**Critical quirk: `instructions` parameter does NOT reliably enter cache.** Despite docs implying it's part of the prompt, community testing reports it's treated as ephemeral and doesn't persist into the cached prefix even at ~2k tokens ([thread 1346849](https://community.openai.com/t/problem-caching-system-prompt/1346849), opened Aug 2025; a user there: "The instructions parameter is only valid for one request"). No OpenAI staff acknowledgment or fix found, so the behavior appears current — but the verifiable evidence is Aug 2025, not the later month-stamps earlier drafts of this skill claimed.

**Workaround:**
```python
client.responses.create(
    model="gpt-5.1",
    input=[
        {"role": "developer", "content": SYSTEM_PROMPT},  # caches
        {"role": "user", "content": user_msg},
    ],
    # do NOT use instructions=SYSTEM_PROMPT
)
```

**Reasoning models + `store=false`** require explicit reasoning replay: set `include=["reasoning.encrypted_content"]`, capture the encrypted blob from each response, pass back in next call's `input`. Otherwise the prefix shifts every turn.

**Cookbook reports cache utilization rising "from 40% to 80%"** switching Chat Completions → Responses for reasoning workloads ([reasoning_items cookbook](https://developers.openai.com/cookbook/examples/responses_api/reasoning_items), verbatim: "switching from the Completions API to the Responses API boosted cache utilization from 40% to 80%"). Those are absolute utilization levels in their internal test — *not* "40–80% better." The mechanism is real: persisted chain-of-thought between turns via `previous_response_id`/reasoning items, which Chat Completions drops.

**`store=true` vs `store=false`** is independent of caching in principle. `store` controls 30-day response-object retention; cache is its own KV mechanism. ZDR orgs are forced `store=false`. **Note:** `prompt_cache_retention="24h"` is **permitted under ZDR** — current docs say extended-retention requests "are not blocked if Zero Data Retention is enabled" (it stores derived KV tensors, not content). Earlier drafts of this skill called 24h "incompatible with ZDR"; that is refuted.

**`previous_response_id` cost trap:** every prior token re-billed as input on every call. Cache hits are what make multi-turn economical.

**Migration trap from Chat Completions:** the lazy port is `messages=[…]` → `instructions=system_text, input=user_text`. That's the worst possible setup for cache (because of the `instructions` quirk). Correct port:
```python
input=[
    {"role": "developer", "content": system_text},
    {"role": "user", "content": user_text}
],
# instructions=None
```

**`conversation` API object (newer than `previous_response_id`):** state-management feature, **NOT a cache-warming feature**. Same prefix-hash mechanism for cache lookup. The difference is durability — Conversation items don't expire after 30 days the way response objects do. Don't assume Conversation objects help cache hits.

**gpt-5.4 introduced "native Compaction"** as a built-in conversation-management feature (released Mar 5, 2026), with a dedicated [compaction guide](https://developers.openai.com/api/docs/guides/compaction) and a `/responses/compact` endpoint — it summarizes earlier turns server-side (also on gpt-5.4-mini/-nano). Cache implications are not documented; assume a compacted prefix is a NEW prefix until measured otherwise.

**gpt-5.5 / gpt-5.5-pro:** only `24h` retention is supported (guide: "For `gpt-5.5`, `gpt-5.5-pro`, and future models, only `24h` is supported"); `in_memory` is no longer available. All future models follow this pattern. (Secondary sources say passing `in_memory` errors; the doc only states 24h is the sole supported value.)

## JSON Schema enforcement (`response_format={"type":"json_schema",...}` / `text.format=...`)

**The schema participates in prompt caching** and changing it can break cache hits — but the exact ordering is **disputed**. The "appended as a prefix to the system message" line attributed to Microsoft Foundry docs is **not in the current Foundry doc** (misattribution), and a [community test](https://community.openai.com/t/does-structured-output-schema-come-before-after-system-message-for-prompt-caching/1332152) found editing the schema tail did *not* break caching while editing the system-message tail did — implying the schema sits *after* the system message, not strictly before it. Keep the schema byte-stable regardless; don't over-claim its prefix position.

**Independent compile cache:**
- Idle TTL: **undocumented** — [Sophia Willows](https://sophiabits.com/blog/openai-structured-outputs-deep-dive) (canonical deep-dive) explicitly flags warm duration as an open question. (Earlier drafts said "~120s"; that figure has no source.)
- Scope: Sophia Willows's "global" observation is consistent with OpenAI pre-warming their own published example schemas — does not generalize to your schemas
- Cross-model crossover within an org: **unmeasured publicly** — pre-warm each (model, schema) pair explicitly
- First-call latency: 10–60s typical (Willows saw ~12s simple / up to a minute complex), up to a minute on complex schemas
- Not billed (wall-clock only)
- No pre-warm endpoint — fire one cheap call per (model, schema) pair before batches

**`strict: true` requires:**
- `additionalProperties: false` on every object
- Every property in `required` (no truly-optional keys; "optional" must be a `["type","null"]` union with the field still required)
- Documented limits: **up to 100 object properties total and up to 5 levels of nesting** ($defs and recursion supported; root cannot be `anyOf`)

**The OpenAI SDK's `parse()` helper** runs `Model.model_json_schema()` then transforms via `openai.lib._pydantic.to_strict_json_schema` (drops unsupported keys, hoists `$defs` to `definitions`, forces `additionalProperties: false`, marks every field `required`, wraps Optional). Output is stable for a given (Pydantic, openai SDK) version pair — bumps change bytes.

**Stability checklist:**
- Snapshot serialized schema bytes to disk
- CI test: `assert current_schema == snapshot`
- Pin `pydantic` and `openai` versions
- No dynamic content in `Field(description=...)`
- Don't reorder model fields casually

## Lark grammar enforcement (custom tools)

**API surface (Responses or Chat Completions):**
```python
tools=[{
    "type": "custom",
    "name": "...",
    "format": {
        "type": "grammar",
        "syntax": "lark",
        "definition": grammar_string,
    },
}]
```

**Supported models:** gpt-5, gpt-5-mini, gpt-5-nano and the gpt-5.x family. Not gpt-4.1 or earlier. (Don't enumerate exact point releases — the lineup churns; the cookbook lists gpt-5/mini/nano and live examples use gpt-5.5.)

**Cannot use with `parallel_tool_calls=True`.**

**Grammar is in cached prefix**, byte-for-byte. Same rules as schema: any change invalidates.

**No documented compile cache** (unlike JSON Schema). Engine is **llguidance** ([guidance-ai/llguidance](https://github.com/guidance-ai/llguidance), "shipped in OpenAI for JSON Schema" 2025-05-20) — lazy automaton construction, ~50µs/token mask compute. Empirically, CFG-enabled calls show a large per-call latency penalty: **~8–10× is one anecdotal figure, but community reports vary widely (sometimes far worse)**, attributed to the constrained generation loop rather than the 50µs mask. Also note CFG outputs are **not always guaranteed to conform** to the grammar ([thread 1337673](https://community.openai.com/t/gpt-5-custom-lark-tool-outputs-are-not-guaranteed-to-conform-to-the-cfg/1337673)) — validate post-hoc.

**Lark dialect (subset):**
- Supported: terminals, rules, `|`, `+`, `*`, `?`, `()`, recursion, character classes, regex inside terminals (Rust regex), `%import common.WS`, `%ignore WS`.
- NOT supported: lookaround (`(?=...)`, `(?!...)`), lazy quantifiers (`*?`, `+?`, `??`), terminal priorities (`.N` suffix), templates, `%declare`.
- Validate offline: `pip install llguidance` and parse before shipping.

**Output:** model emits `custom_tool_call` item; `input` field is plain text (not JSON-wrapped).

## Schema vs Grammar decision

| Axis | JSON Schema | Lark grammar |
|---|---|---|
| First-call latency | 10–60s compile, then fast | ~9.5s overhead per call, no compile cache |
| Steady-state latency | Fast post-warmup | Slow (~10× without CFG) |
| Cache stability | Bytes in prefix + separate compile cache | Bytes in prefix only |
| Output flexibility | JSON only | Arbitrary text format |
| Reliability | Higher (more mature) | Lower — model drift + occasional Rust panics |
| Best fit | Structured records | DSLs, SQL, custom mini-languages |

**Default to JSON Schema. Use Lark only when output genuinely isn't JSON-shaped** (mini-languages, freeform text + structure, planner DSLs).

## Service tier interactions

| Tier | Cache discount | Cache hit rate | Latency |
|---|---|---|---|
| `standard` | Yes (full discount) | Baseline | Baseline |
| `priority` | Yes (same 90% discount; ~2.5× base input) | Baseline | Lower |
| `flex` | Yes (applied to flex base rate) | **+8.5% vs batch** (cookbook-author anecdote) | Higher |
| `batch` | Caches for **GPT-5-and-newer**; pre-GPT-5 (o3, o4-mini) NOT cached | N/A | Highest |

**For cache-heavy workloads where latency tolerance is moderate**, `flex` on Responses is the recommended path: cheaper than standard, full cache discount, and a cookbook author's head-to-head test showed a better hit rate than batch.
