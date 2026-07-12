# SkillsForThings

![SkillsForThings package index: five packages covering multi-agent builds, prompt efficiency, cross-cutting project judgment, public skill maintenance, and memory visualization.](assets/skills-for-things.png)

A Claude Code skill marketplace for multi-agent builds, prompt engineering, research, plugin maintenance, and memory visualization.

## Install

In Claude Code:

```
/plugin marketplace add TomNeyland/SkillsForThings
/plugin install conductor@SkillsForThings
```

Or from a local clone:

```bash
claude plugin marketplace add /path/to/SkillsForThings
claude plugin install conductor@SkillsForThings
```

## Plugins

### `conductor`

Coordinate a fleet of subagents to do what one context can't — delegate owned units, review by blast radius, trace the seams, and integrate. Includes a standing enthusiast/critic pair and five ready-to-delegate subagents (`implementer`, `correctness-reviewer`, `integration-gap-auditor`, `scout`, `design-steward`).

| Skill | Use when |
|---|---|
| `coordinate-agents` | A task is large enough to split across multiple subagents you coordinate as the lead, rather than doing it all in one context |
| `fan-and-critic` | A long autonomous build needs two standing outside perspectives on repeated artifacts: an enthusiast identifying what genuinely lands and a harsh critic identifying what is weak |
| `autonomous-build` | Explicitly kicking off a long, autonomous product-building session by name |
| `autonomous-build-purpose-layers` | Deciding what to build next in a long session — advancing the product's arc of purpose, not polishing the last view |
| `autonomous-build-jealousy-ranking` | Ranking a backlog or filing issues — tool-vs-toy, red-team, kill-and-replace |
| `autonomous-build-session-pacing` | Running a long autonomous window — heartbeat, commit/push cadence, typecheck-before-commit, budget triage |
| `autonomous-build-commit-essays` | Writing a commit message that captures the WHY — audience and arc-position, not just what changed |

### `prompt-tuning`

Skills for optimizing LLM prompts across multiple axes — cache hit rate, latency, cost, structure.

| Skill | Use when |
|---|---|
| `openai-prompt-cache` | Designing or auditing OpenAI API prompts for cache hit rate; debugging cost spikes; building systems with large reused prefixes (RAG pipelines, agent loops, structured extraction, batch jobs) |

More skills are planned (`recency-reiteration`, `schema-vs-grammar`, others).

### `plugin-ops`

Skills for maintaining the marketplace itself — refreshing stale claims, validating manifests, auditing skills against current evidence.

| Skill | Use when |
|---|---|
| `refresh-skill` | A skill's content or references may have gone stale; a new SDK / model / API release may have invalidated specific recommendations; validating that measurements and version-pinned claims are still accurate |
| `admitting-a-skill` | A new or edited skill is about to enter a public marketplace, especially one ported or genericized from a private codebase — mechanical lint + a dual-model origin-leak and quality gate |
| `framing-skill-infographics` | Deciding which reader benefit, mechanism, proof, hook, and details belong in a shareable infographic for a skill in this marketplace |

### `memory-mood`

Replays staged cumulative snapshots of your assistant's memory files in formation order and asks a fresh judge at each selected timepoint, *how do you feel?* Renders a self-contained HTML page with an emotional-arc chart and timestamped reaction feed.

| Skill | Use when |
|---|---|
| `memory-mood` | Visualizing the mood/emotional arc of your assistant's accumulating memories; free-tier (Sonnet subagents, one reading per timepoint, no API key, stdlib only) |
| `memory-mood-openai` | Same, but via the OpenAI API — k independent readings per selected snapshot, averaged with visible ±1σ call-to-call spread (requires `OPENAI_API_KEY`) |

### `misc`

Assorted process skills that don't fit an existing plugin family.

| Skill | Use when |
|---|---|
| `prior-art` | Before hand-rolling a capability, choosing a library, technique, or data source, or designing a custom identifier, schema, algorithm, file format, or taxonomy |
| `align-terminology` | Reviewing or designing schema field / model / enum names, or auditing names against authoritative terminology |
| `cutting-internal-leaks-from-copy` | Reviewing or writing customer-facing prose an LLM produced, to catch material that leaks the machine's internals, the build process, the author's hedging, or copy narrating its own device |
| `orchestrating-greenfield-builds` | Prototype ancestor of `coordinate-agents`; use its specialized ten-stage workflow for showcase-grade greenfield or rebuild sessions that must preserve intent across agents and contexts |
| `creating-technical-infographics` | Turning technical explanations, workflows, failures, comparisons, or instructions into plain, editable 4:5 SVG and PNG infographics for mobile feeds |

See `CLAUDE.md` for contribution conventions.

## License

MIT (TBD — currently unlicensed pending decision).
