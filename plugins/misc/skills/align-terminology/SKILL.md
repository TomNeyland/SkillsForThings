---
name: align-terminology
description: Use when reviewing or designing schema field names, model names, or enum names, or auditing names against authoritative terminology. Triggers on "would an expert recognize this name", "align terminology", "standard field names", "canonical term for this". Also use proactively during schema design or review.
---

# Align Terminology

![The invented boolean is_critical makes an expert ask what critical means; RFC 5424's recognized severity field and eight-level scale show why authoritative names carry their definitions.](assets/align-terminology.png)

For every field, model, and enum value: **would someone who works with this data daily recognize the name without explanation?**

## The Expert Test

> If a specialist in this data's domain looked at field `Y`, would I have to explain what it means — or would they already know from the name?

If you'd explain it, you named it wrong. The name is an instruction — to the LLM, the developer, and the expert reading it. A name that carries its definition from an established standard beats one you invented.

## Why This Matters

1. **LLMs already know standard terms.** `status_code: 404` triggers HTTP semantics from training; `error_num: 404` forces the model to guess your convention.
2. **Experts validate faster.** The standard term reads instantly; a home-rolled synonym forces "is this the same as X?"
3. **Invented names drift.** `quality_score` sounds clear until someone asks "by what measure?" — a standard name would have disambiguated it.

## Process

### 1. Identify the authority

Most concepts already have a name somewhere:

| Kind of concept | Where authority lives |
|---|---|
| Cross-domain primitives (time, money, geography, identity) or data-interchange shapes | International or de facto standards (ISO, IETF/RFC, IANA, format specs) |
| Domain-specific concepts | The field's own standards body or reference vocabulary |
| Genuinely internal concepts | No authority exists — fine, if true (see Invented) |

### 2. Apply the Expert Test

```
Field: is_critical: bool
Authority: Syslog severity (RFC 5424) — an 8-level scale, not a flag
Expert test: "critical compared to what — 'error'? 'emergency'?"
Verdict: RENAME → severity: Literal["emergency", ..., "debug"]
```

### 3. Classify each field

| Status | Meaning | Example |
|---|---|---|
| **Aligned** | Matches the authority's term | `created_at` (ISO 8601) |
| **Misnamed** | Authority uses a different term | `is_critical` → RFC 5424's `severity` |
| **Conflated** | Standard's name, different concept | `content_type` used for "topic" |
| **Oversimplified** | Standard is richer than the field | `is_authenticated`, alone |
| **Ambiguous** | Different standards disagree | `status` — HTTP code, or workflow stage? |
| **Invented** | No standard covers this concept | `quality_score` — if truly novel, document why |

### 4. Propose the standard name

```
❌ content_type: "faq"            → RFC 6838 already owns this name (media type)
✅ topic: "faq"

❌ is_authenticated: bool (alone) → OAuth/OIDC separate authN from authZ
✅ is_authenticated: bool
✅ granted_scopes: list[str]
```

## Output Format

```
[STATUS] field_name → Authority: term | Action
```
```
[ALIGNED] created_at → ISO 8601 | None
[MISNAMED] is_critical → RFC 5424: severity | Rename to severity
[INVENTED] quality_score → No standard found | Keep, document why
```

## Red Flags

| Thought | What's wrong |
|---|---|
| "Our name is clearer" | Clearer to whom? The LLM knows the standard term from training. You're the only one it's clear to. |
| "Nobody reads field names" | The LLM reads them as instructions; a recognized name extracts better. |
| "It means the same thing" | Near-synonyms often aren't — check if the standard treats them as independent before merging. |
