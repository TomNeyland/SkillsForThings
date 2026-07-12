# OpenAI Prompt Cache: Footgun Catalog

Reference for the `openai-prompt-cache` skill. Each entry: cause, symptom, fix.

## High-impact (silent cache annihilators)

### Timestamps in the system prompt
- **Cause:** `f"You are a helpful assistant. Today is {datetime.now()}."` at prefix head.
- **Symptom:** `cached_tokens: 0` on every call despite a massive shared prefix.
- **Fix:** Move time to `metadata` (out-of-band, doesn't enter prefix). If the model genuinely needs the date, put it in the user message (post-prefix).

### Regenerating Pydantic schemas per call
- **Cause:** `client.beta.chat.completions.parse(response_format=Model)` re-serializes the schema each call. Field-definition order, `$defs` ordering, V1↔V2 Optional representation, auto-generated `title` from field names — all sources of byte drift.
- **Symptom:** Cache hits randomly; correlates with code changes that "shouldn't matter."
- **Fix:** Snapshot the serialized schema to disk at build time. Load the cached bytes per call. Add a CI test:
  ```python
  assert json.dumps(to_strict_json_schema(Model)) == open("schema.json").read()
  ```

### Dynamic `description=` in Pydantic Field
- **Cause:** `Field(description=f"As of {today}, ...")` — daily byte drift.
- **Symptom:** Cache hits work for one day, fail the next.
- **Fix:** Strip dynamic content from descriptions. Move runtime context to user messages.

### RAG chunk reshuffling
- **Cause:** Vector DB returns same chunks in different order each call.
- **Symptom:** Hit rate ~30–50% instead of ~90%.
- **Fix:** Sort retrieved chunks by stable doc id before splicing. OR put RAG content AFTER the cached system block (in user-message position).

### Tool JSON serialization order drift
- **Cause:** `json.dumps(tools)` with default `sort_keys=False` against a Python dict whose order isn't pinned (set→list conversions, dict comprehensions, conditional inclusion).
- **Symptom:** Same logical tools array; different bytes per call.
- **Fix:** `json.dumps(tools, sort_keys=True)` once at startup; cache the bytes; reuse forever.

### Mutating `tools` to gate availability
- **Cause:** Removing a tool per-call to restrict what the model can call.
- **Symptom:** Cache misses every time you change which tools are available.
- **Fix:** Keep `tools[]` constant. Use `tool_choice={"type":"allowed_tools","mode":"auto","tools":[...]}` to restrict per call without mutating the array.

### Few-shot examples shuffled "for diversity"
- **Cause:** Prompt template that randomizes example order.
- **Symptom:** Cache hit rate inversely correlates with shuffle frequency.
- **Fix:** Pin the order. If you need diversity, pin per-cohort and shard `prompt_cache_key` accordingly.

### Sharding `prompt_cache_key` by model name in multi-model workloads
- **Cause:** `prompt_cache_key=f"{model}:{workload}"` — fragments the cache pool per sibling model.
- **Symptom:** Cache miss when alternating sibling models on a shared prefix (draft/polish, model bake-off, tiered routing).
- **Fix (tentative):** Try the SAME `prompt_cache_key` across sibling models. The "prefix cache is shared across siblings" claim rests on a **single unverified HN self-report** (46070749, Nov 2025, 0 comments) — not corroborated. Measure `cached_tokens` before relying on it; if it doesn't help, this footgun doesn't apply to your setup.

## Medium-impact

### Model alias (`gpt-5.1`) in production
- **Cause:** Alias resolves to different dated snapshots over time; each snapshot has its own KV cache.
- **Symptom:** Cache hit rate craters on a date you didn't deploy anything.
- **Fix:** Pin dated snapshot in production: `gpt-5.1-2026-XX-XX`. Plan an explicit migration when bumping.

### `instructions` parameter on Responses API
- **Cause:** Putting your system prompt in the `instructions` top-level parameter on Responses.
- **Symptom:** No cache hit despite >1,024 tokens of stable content.
- **Fix:** Put system prompt as a `developer` role item at head of `input` instead.
- **Status:** Reported since Aug 2025 ([thread 1346849](https://community.openai.com/t/problem-caching-system-prompt/1346849)); no OpenAI acknowledgment or fix found, so apparently still current. (Earlier drafts gave precise "Feb 2026 / May 2026" datestamps that aren't sourced — the verifiable evidence is Aug 2025.)

### Image `detail` parameter changes
- **Cause:** Flipping image `detail` between `low`/`high`/`auto` retokenizes the image.
- **Symptom:** Cache misses on otherwise-identical prompts containing images.
- **Fix:** Pin `detail` per workload.

### Reasoning effort changes between calls
- **Cause:** `reasoning.effort` is part of the request signature.
- **Symptom:** Cache miss when toggling effort.
- **Fix:** Pin effort per workload chain. If you need both low and high effort, treat them as separate cache pools.

### Service tier switching
- **Cause:** `service_tier="standard"` vs `"flex"` vs `"priority"` *may* route to different pools — **unverified**, no doc or thread ties `service_tier` to cache-pool routing.
- **Symptom:** Reported anecdotally; not confirmed.
- **Fix:** Pin tier per workload as a cheap precaution, but don't assume switching busts cache as established fact.

### Forgetting `prompt_cache_retention="24h"` on slow workloads
- **Cause:** `in_memory` retention's 5–10 min TTL evicts before the next call in a low-cadence batch.
- **Symptom:** Cache hits within a burst; miss between bursts.
- **Fix:** Mostly already handled — GPT-5-series non-ZDR orgs **default to `24h` since 2026-05-29**, and gpt-5.5+ only allows `24h`. You only need to set it explicitly on `in_memory`-default paths (pre-GPT-5, or ZDR orgs, where `24h` is still permitted).

### Exceeding 15 RPM per (prefix, key) bucket
- **Cause:** One workload generates >15 requests/min sharing the same prefix and key.
- **Symptom:** Hit rate plateaus around 60–70% even with stable prefix.
- **Fix:** Shard the key: `prompt_cache_key=f"workflow-v3-shard-{i%N}"` for N workers/buckets.

## Low-impact / subtle

### Lark grammar with interpolated values
- **Cause:** Grammar terminal like `ID: "12345" | "67890"` with per-call values.
- **Symptom:** Cache miss every call on the entire tools array.
- **Fix:** Don't interpolate. Define a generic terminal (`ID: /\d+/`) and validate post-hoc.

### Lark grammar regenerated by `lark.Lark(...).source`
- **Cause:** Lark library output not byte-stable across versions.
- **Symptom:** Cache hits work locally but break in CI / new env.
- **Fix:** Snapshot the grammar string to disk; ship the snapshot, not the regenerated value.

### Planner→executor with grammar interpolation
- **Cause:** Planner emits a value that gets interpolated into executor's grammar definition.
- **Symptom:** Executor cache hit rate ~0%.
- **Fix:** Pre-define a fixed executor grammar that admits all valid planner outputs, OR pass planner output as text in the user message and validate post-hoc.

### Comments / whitespace drift in grammars
- **Cause:** Auto-formatter re-flows whitespace; revision header `# rev: 2026-05-02` updates per deploy.
- **Symptom:** Cache miss after innocuous "cleanup" PR.
- **Fix:** Strip comments and normalize whitespace before snapshotting.

### Conversation compaction breaking multi-turn cache
- **Cause:** Summarizing earlier turns mid-conversation changes the prefix.
- **Symptom:** Cache hits within compaction boundaries; miss at boundaries.
- **Fix:** Append-only between compactions. If compaction is necessary, do it on a stable cadence (every N turns) so the new compressed prefix amortizes for the next N.

### `previous_response_id` cost trap (Responses)
- **Cause:** Assuming `previous_response_id` is server-side compression. It's not — every prior token is re-billed as input on every call.
- **Symptom:** Token usage grows linearly with conversation length even with `previous_response_id`.
- **Fix:** Cache hits are what make `previous_response_id` economical. If your hit rate isn't high, manual resend is no worse.

### Pydantic / OpenAI SDK version bumps
- **Cause:** `pydantic` or `openai` minor bump changes the strict-transform pipeline output bytes.
- **Symptom:** Cache misses after `pip install --upgrade`.
- **Fix:** Pin both library versions. Treat upgrades as schema migrations: regenerate snapshot, commit, deploy.

### Fine-tuned model has its own compile cache
- **Cause:** Schema-compilation cache is per-FT-deployment.
- **Symptom:** First call to each FT model has full compile-latency penalty.
- **Fix:** Warmup call per FT deployment at process start.

### `user` field used for cache routing (deprecated)
- **Cause:** Old guidance recommended `user` for cache bucketing.
- **Symptom:** Routing-stickiness benefits no longer come from `user`.
- **Fix:** Use `prompt_cache_key` for routing and `safety_identifier` for abuse signals — these split off the `user` field's old roles (the split is documented; the often-cited "July 31, 2025" date is community-sourced, not an official changelog entry).
