# Cache Behavior By API Surface

Current source of truth: OpenAI's [Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching).

## Shared rules

Both Responses and Chat Completions cache exact rendered prefixes of at least 1,024 tokens. Stable messages, tools, images, files, and structured-output schemas belong before changing content. Reuse a stable `prompt_cache_key` for requests that share a prefix.

GPT-5.6+ supports explicit breakpoints and `prompt_cache_options`; earlier models reject those fields and retain their automatic-caching behavior.

## Responses API (`/v1/responses`)

Read cache usage from:

```text
usage.input_tokens_details.cached_tokens
```

On GPT-5.6+, cache writes are reported at:

```text
usage.input_tokens_details.cache_write_tokens
```

Responses supports explicit breakpoints on `input_text`, `input_image`, and `input_file` content blocks.

### GPT-5.6+ implicit example

The request keeps the default implicit latest-message breakpoint and adds an explicit breakpoint after a stable file:

```python
response = client.responses.create(
    model="gpt-5.6",
    prompt_cache_key="tenant:acme:knowledge-base-v1",
    prompt_cache_options={"ttl": "30m"},
    input=[{
        "type": "message",
        "role": "user",
        "content": [
            {
                "type": "input_file",
                "file_id": "file_123",
                "prompt_cache_breakpoint": {"mode": "explicit"},
            },
            {"type": "input_text", "text": user_question},
        ],
    }],
)
```

The rendered prefix ending at the file must contain at least 1,024 tokens. The question after the breakpoint may vary.

### Community caveat: top-level `instructions`

Users have reported that a long top-level `instructions` value did not produce the same reliable reuse as placing the same text in a leading `developer` input item ([community thread 1346849](https://community.openai.com/t/problem-caching-system-prompt/1346849), Aug 2025). OpenAI's current prompt-caching guide does not document this distinction.

Treat it as a compatibility test, not a universal rule: if the workload misses, move stable instructions into the rendered `input` prefix and compare `cached_tokens` over repeated calls.

### Stateful response chains

Conversation state and prompt caching solve different problems. A stateful Responses chain does not remove the need to monitor cache reads and, on GPT-5.6+, cache writes. When compaction or an earlier item changes the rendered prefix, expect a new cache write or miss until measurement proves otherwise.

## Chat Completions API (`/v1/chat/completions`)

Read cache usage from:

```text
usage.prompt_tokens_details.cached_tokens
```

On GPT-5.6+, cache writes are reported at:

```text
usage.prompt_tokens_details.cache_write_tokens
```

Chat Completions supports explicit breakpoints on `text`, `image_url`, `input_audio`, `file`, and `refusal` content blocks.

### GPT-5.6+ explicit-only example

```python
response = client.chat.completions.create(
    model="gpt-5.6",
    prompt_cache_key="tenant:acme:support-v1",
    prompt_cache_options={"mode": "explicit", "ttl": "30m"},
    messages=[
        {
            "role": "system",
            "content": [{
                "type": "text",
                "text": stable_system_prompt,
                "prompt_cache_breakpoint": {"mode": "explicit"},
            }],
        },
        {"role": "user", "content": user_question},
    ],
)
```

In explicit mode, omitting every explicit marker disables prompt-cache reads and writes for that request. This is useful when you need deterministic control over which prefixes may incur write charges.

For streamed Chat Completions, request usage in the stream if your client would otherwise omit the final usage object.

## Earlier models on either API

Do not send `prompt_cache_options` or `prompt_cache_breakpoint`; earlier models reject them. Use exact-prefix automatic caching and, when supported, set `prompt_cache_retention` explicitly to `in_memory` or `24h`.

`gpt-5.5` and `gpt-5.5-pro` accept only `24h` through the older retention field. Other earlier models vary; check the current official model list rather than copying a family-wide default.

## Structured outputs

OpenAI documents the structured-output schema as cacheable prompt-prefix content. Changing the schema can therefore change the reusable prefix.

Stability rules:

- generate and serialize the schema deterministically;
- keep field order and descriptions stable;
- move dates, tenant IDs, and other runtime values out of schema descriptions;
- snapshot schema bytes in CI when a stable prefix matters.

Structured-output grammar compilation is a separate concern from prompt caching. OpenAI's prompt-caching guide does not specify compile-cache lifetime, cross-model scope, or a pre-warm contract. Do not mix undocumented compile-cache timings into prompt-cache retention guidance.

## Tools and custom grammars

Tool definitions participate in the prompt prefix. Keep the entire tool list and its serialized bytes stable. For a custom grammar, do not interpolate per-request values into the grammar definition; put changing values after the cache breakpoint and validate the output separately.

## Images, audio, and files

- Images may be cached when their links or base64 data match; `detail` must also match.
- GPT-5.6+ explicit markers are allowed only on the block types listed above.
- A marker on an unsupported or non-cacheable block returns `400 invalid_request_error`.
- A file or image placed before a breakpoint is part of the exact prefix; replacing it creates a different prefix.
