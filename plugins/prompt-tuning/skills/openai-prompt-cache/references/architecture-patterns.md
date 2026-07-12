# Cache-Aware Prompt Architectures

Reference for the `openai-prompt-cache` skill. Covers structured-output vs unstructured cache implications, multi-turn conversation patterns, the canonical [stable prefix + variable tail] pattern, and what happens when you switch models with a shared schema.

## Structured output vs unstructured

| Aspect | Unstructured | Structured (JSON Schema or Lark) |
|---|---|---|
| Cache surfaces to manage | One (prompt prefix) | **Two** (prompt prefix + schema-compile cache) |
| Schema bytes in prefix | N/A | **Yes** — appended ahead of system message |
| First-call latency penalty | None | 10–60s schema compile (JSON Schema), ~9.5s overhead per call (Lark) |
| Cache miss cost | Full prefix re-bill | Full prefix re-bill **PLUS** potential schema recompile |
| Stability constraint | Just message bytes | Schema bytes also must be byte-stable |
| CI test recommended | No | **Yes** — assert serialized schema bytes match snapshot |

**Net:** structured output is cache-friendly *only if* you treat the schema as immutable bytes. Snapshot to disk, fail CI on drift, pin Pydantic + openai SDK versions. Bigger schemas = bigger absolute savings on hit AND bigger absolute penalty on miss.

## Pattern A: Long appending conversation

The "chatbot" pattern. Each turn extends the prefix; prior turns stay in the prefix and continue caching.

**Cache-correctness:** good. Append-only is structurally cache-friendly.

**Costs scale linearly:** at turn N you re-bill all N-1 prior turns (at cached rate, but still billed). A 50-turn conversation pays 50× the system prompt cost across its lifetime even with 90% discount.

**Footguns:**
- Mid-conversation summarization breaks the cache from the summarization point onward. If you must compact, do it on a stable cadence (every N turns) so the new compressed prefix amortizes.
- Editing prior turns to "fix" something invalidates everything downstream.
- On Responses API, `previous_response_id` does NOT compress server-side — it just expands into the same prefix tokens you'd send manually. Same cost shape.

**When to use:** when conversation history is genuinely semantically load-bearing (multi-turn reasoning, agentic workflows that need state continuity).

**When to avoid:** when each "task" is independent. The pattern below is far more economical.

## Pattern B: [stable prefix] + [uncached variable tail] (RECOMMENDED for repeated tasks)

The dominant production pattern. Structure:

```
┌─────────────────────────────────────────────┐
│ [CACHED]  Tools / response_format / schema  │  ← byte-stable, in prefix
│ [CACHED]  System instructions               │  ← byte-stable, in prefix
│ [CACHED]  Payload (corpus / KB / config)    │  ← byte-stable, in prefix
│ [CACHED]  Tail reminders (optional)         │  ← byte-stable, in prefix
├─────────────────────────────────────────────┤  ← cache boundary
│ [UNCACHED] User message / analysis task     │  ← varies per call
└─────────────────────────────────────────────┘
```

**Why it works:** the first ~99% of every call is identical bytes → prefix-cache hit at near-90% discount. Only the variable tail is fresh-billed.

### Sub-pattern: payload in system message

Putting a large shared payload (knowledge base, config dump, corpus excerpt) into the **system message** is correct *iff* the payload is genuinely shared across calls. Considerations:

- **If the payload is shared** (same corpus across all users/sessions): system-message placement is correct. It caches. Some models (community-reported) weight system content slightly heavier than user content for instruction-following.
- **If the payload is per-user/per-session**: it won't cache regardless of which role you put it in. Choose role for attention-weight reasons, not cache reasons.
- **If the payload is per-batch**: shard `prompt_cache_key` per batch so each batch warms its own cache (e.g., `prompt_cache_key=f"batch-{batch_id}"`).

### Sub-pattern: static reminder at the cache tail (Pareto move)

A short, **static** reminder block placed as the **last item before the user message** is the dominant pattern for combining cache hit rate with recency-bias mitigation:

- **Cached** because it's static bytes inside the prefix → ~90% discount on every call after the first.
- **Recency-positioned** because it sits at position N immediately before the user message at position N+1 → captures the tail of the U-shaped attention curve.
- **Zero per-call cost** beyond the one-time cache write.

**Empirical support:**
- Anthropic's own measurement: query-at-end of a multi-doc prompt improves response quality by **up to 30%** (a ceiling "in tests," not a mean) vs query-at-head ([Anthropic prompting best practices → "Long context prompting"](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompt-best-practices); the old standalone `/long-context-tips` page was merged here).
- **"Drift No More? Context Equilibria in Multi-Turn LLM Interactions"** (Dongre et al., Adobe Research/UIUC, [arXiv 2510.07777](https://arxiv.org/abs/2510.07777), Oct 2025): goal reminders injected mid-conversation cut turn-wise KL divergence **6–12%** (Qwen-2-7B 6.45% → LLaMA-3.1-70B 11.81%) and improved o1-judge quality **16–27%** across LLaMA-3.1 (8B/70B) and Qwen-2-7B (used as user simulators).
- "Lost in the Middle" (Liu et al. 2023, [arXiv 2307.03172](https://arxiv.org/abs/2307.03172)), with the mechanism analyzed in **"On the Emergence of Position Bias in Transformers"** (Wu, Wang, Jegelka, Jadbabaie, MIT, ICML 2025; [MIT News, 2025-06-17](https://news.mit.edu/2025/unpacking-large-language-model-bias-0617)): **causal masking induces a primacy bias**; relative/rotary positional encodings (RoPE) partially *modulate* it rather than causing "long-term decay." Net: start-and-end-of-prefix tokens get more attention than the middle. (Don't conflate with the later "Lost in the Middle at Birth," arXiv 2603.10123.)

**Anti-pattern (the only thing to avoid):** reminders that interpolate per-call values (timestamps, user IDs, session state). These invalidate the cache for everything below them. Either keep the reminder fully static, or move dynamic content into the user message.

**When the static-tail-reminder isn't enough:** if your task is a hard compliance constraint and the reminder must include per-request context, accept the cost of placing it AFTER the user message. The Drift No More result (16–27%) suggests the adherence ROI more than offsets a few hundred uncached tokens for high-stakes calls. For background batch workloads, the static cached reminder almost always wins.

**SCAN pattern for very long contexts (>100K tokens):** instead of a static reminder, place short *generative* checkpoints at the cache tail. In the original ([community thread 1375139](https://community.openai.com/t/solving-agent-system-prompt-drift-in-long-sessions-a-300-token-fix/1375139)) these are `@@SCAN` markers — numbered questions at section ends that the agent must answer before acting — which force the model to spend reasoning tokens on the rules within the recent attention window. The author reports ~300 tokens total (vs 2,000+ for full prompt repetition), <0.5% overhead, stable across 100K+ contexts (11 agents, 7 markers). This is a **single forum anecdote**, self-reported — weaker evidence than the peer-reviewed results above; treat as a pattern to try, not a measured guarantee.

### Sub-pattern: user message at the tail

Always uncached, always per-call. This is the right place for:
- The actual question or task
- Per-user context (their goals, their history)
- Per-session state (current document, current selection)
- Anything that varies per call

**Don't try to make the user message cache.** It defeats the architecture.

## Multi-model with shared schema

You have one JSON Schema (or grammar) and call it against multiple sibling models — e.g., a draft-then-polish workflow, a model bake-off, a tiered routing strategy.

This involves **two independent cache layers** with different cross-model behaviors:

### Layer 1: Prefix routing cache — possibly shared across siblings [single unverified report]

One HN post ([46070749](https://news.ycombinator.com/item?id=46070749), harsharanga, 2025-11-27, **5 points, 0 comments**) reports a cache hit on the *first* call to gpt-5-mini after warming a 1,400-token prefix on gpt-4o-mini, with no per-model warmup. The author's own words: *"prefix-processing cache sharing, not KV-cache sharing. Models share tokenization and prefix hashing, not attention states."*

This is **a single self-report with zero corroboration**, and the test used the Chat Completions `cached_tokens` field. Contemporaneous threads report cache being model-specific and flaky, which cuts against a clean cross-sibling-sharing story. Treat the whole "share the prefix cache across siblings" idea as an **untested hypothesis**, not a documented mechanism — useful only if your own `cached_tokens` measurements confirm it.

### Layer 2: Schema-compile cache — scope disputed, cross-model behavior unmeasured

The compile cache is keyed on schema-bytes hash. Scope is **not firmly established**: the documented "not shared between organizations" line is about the *prompt* cache, while [Sophia Willows](https://sophiabits.com/blog/openai-structured-outputs-deep-dive) observed the *schema-compile* cache behaving as if **global** (zero compile latency reusing OpenAI's published example schema) — most likely because OpenAI pre-warms its own published schemas, which doesn't generalize to yours. Cross-model crossover within an org is **not empirically measured** in public research.

Theoretically a CFG is model-independent (depends on tokenizer, not weights). If a model family shares a tokenizer the compile artifact *could* transfer. But the gpt-5-mini/nano prompt-cache regressions ([community thread #1359574](https://community.openai.com/t/caching-is-borked-for-gpt-5-models/1359574)) suggest the cache infrastructure is not uniform across the family — don't assume the schema cache transfers cleanly.

### Strategies for multi-model workloads

**1. Consider the SAME `prompt_cache_key` across sibling models in a workload.** Fragmenting by model name *might* defeat the (unconfirmed, single-report) cross-model routing benefit from HN 46070749 — but it's cheap to try and measure:
```python
# RIGHT
prompt_cache_key = workload_id  # same across model variants

# WRONG (defeats cross-model effect)
prompt_cache_key = f"{model_snapshot}:{workload_id}"
```

**2. Warm the cheaper model first.** A draft-then-polish pipeline that warms with gpt-5-mini before hitting gpt-5 lands the polish call on a routed-hot machine.

**3. Pre-warm each (model, schema) pair explicitly with one synthetic call** before a batch starts. Insurance against the schema-compile cache being cold for that model. ~$0.0001 per warmup call.

**4. Pin model per workload phase when possible.** Instead of round-robin per call, batch by model:
- Phase 1: 1000 calls to gpt-5-mini (cache warms, hit rate climbs)
- Phase 2: 1000 calls to gpt-5 (cache warms, hit rate climbs)

Round-robin A/B (alternating models call-by-call) maximizes cache thrash. Batching minimizes it.

**5. Family failure-rate awareness.** Independent measurement of cache miss rates by family ([DavidDev, 120 tests/model, thread 1368208](https://community.openai.com/t/possible-cache-issue-on-gpt-5-mini-and-gpt-5-nano/1368208), Dec 2025) — reported **without → with `prompt_cache_key`**:

| Model | Cache miss rate (no key → with key) |
|---|---|
| GPT-5.1 | **19% → 6%** (best) |
| GPT-5-nano | 25% → 28% |
| GPT-5.2 | 45% → 30% |
| GPT-5-mini | **72% → 76%** (worst) |

Separately, gpt-5.4-nano has been reported at a **0% hit rate** ([thread 1379973](https://community.openai.com/t/switching-to-gpt5-4-nano-results-in-0-cache-hit-rate/1379973), Apr 2026), and gpt-5.4/5.5 lose cache when trailing user content exceeds ~500 tokens on chat.completions ([thread 1384129](https://community.openai.com/t/prompt-cache-documented-byte-prefix-matching-does-not-occur-on-gpt-5-4-gpt-5-5-when-trailing-user-content-exceeds-500-tokens/1384129), Jun 2026). For cost-tier routing, **gpt-5.1 is the only consistently-caching small model** in current data. Adding `prompt_cache_key` reportedly made gpt-5-mini/nano *worse* — the routing layer treats those families differently for reasons OpenAI hasn't acknowledged.

**6. `reasoning.effort` is part of the request signature.** Switching effort levels mid-workload busts cache even on the same model snapshot. If you need both low and high effort, treat them as separate cache pools.

## Decision tree

```
Is this prompt called > 10 times within ~1 hour?
├─ No  → Cache won't pay off. Skip this skill, focus on token count + latency.
└─ Yes → Proceed.
   │
   Is the stable content ≥ 1024 tokens?
   ├─ No  → Pad it deliberately, OR accept zero cache and skip the rest.
   └─ Yes → Proceed.
      │
      Are you switching models per call (sibling models, same family)?
      ├─ Yes → Use SAME prompt_cache_key across siblings (don't shard by model).
      │        Warm cheaper sibling first. Pre-warm each (model, schema) pair.
      │        Avoid gpt-5-mini and *-nano for cache-sensitive paths
      │        (DavidDev measurements show 70%+ miss on gpt-5-mini).
      └─ No  → Pin one model snapshot. Apply Pattern B.
         │
         Is your prompt structured output?
         ├─ Yes → Snapshot the schema, CI test for byte stability, pin SDK versions.
         │        Pre-warm the schema-compile cache with one synthetic call.
         └─ No  → Apply Pattern B without schema-cache concerns.
```
