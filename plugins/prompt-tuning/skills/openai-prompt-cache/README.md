# OpenAI Prompt Cache

![For repeated OpenAI API requests, keep at least 1,024 stable tokens—tools, schemas, developer or system instructions, and examples—before variable content. On GPT-5.6 and later, use a workload prompt_cache_key, an explicit breakpoint after the stable prefix when needed, and the 30-minute minimum TTL; earlier models use automatic prefix caching and their supported retention policy. Verify reuse and cost from cached_tokens and cache_write_tokens.](assets/openai-prompt-cache.png)
