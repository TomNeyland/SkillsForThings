---
name: refresh-skill
description: Use when refreshing or auditing a skill's content for stale claims, when a new SDK / model / API release may have invalidated specific recommendations, or when validating that a skill's measurements and version-pinned claims are still accurate. Triggers on "refresh the X skill", "is this still accurate", "audit X for stale claims", or after any release in the skill's domain.
---

# Refresh Skill

![After an external release, audit a reusable AI instruction file by inventorying volatile claims, checking current sources, assigning statuses, editing, and versioning by impact; output an updated cited guide and change log, complete when every claim is statused and local reinstall passes.](assets/refresh-skill.png)

Systematically refresh a skill's content and references against current evidence.

## When to use

- A skill addresses a fast-moving subject (LLM APIs, framework versions, model behavior) and time has passed since last update
- A new release in the skill's domain may have invalidated specific claims
- A user asks "is this still accurate?" or "are these numbers current?"
- Routine audit pass across the marketplace

## When NOT to use

- Greenfield skill creation (different flow)
- Mechanical fixes (typos, formatting) — just edit
- Structural changes (renaming, moving) — just refactor

## Workflow

1. **Inventory time-sensitive claims.** Read SKILL.md and every file under `references/`. Mark every claim that includes:
   - Dates, version numbers, "as of X"
   - Measurement numbers (latency, hit rates, token counts, percentages)
   - Model names or specific snapshot dates
   - `[community-reported]`, `[unconfirmed]`, `[unmeasured]` tags
   - Per-source citations
   Group claims into research clusters that can be researched in parallel.

2. **Spawn one focused research agent per cluster, in parallel.** Use the prompt template below. Cap at 4–6 concurrent (context budget). Run in background.

3. **Synthesize findings.** For each cluster: did anything change? Which is the highest-confidence updated claim? Reconcile contradictions (often two cache layers / mechanisms get conflated). Surface new open questions.

4. **Apply updates.** Edit the relevant files. Bump version per semver:
   - **PATCH** (0.0.Y): typo fixes, citation refresh, no guidance change
   - **MINOR** (0.Y.0): new evidence, recommendations refined or expanded
   - **MAJOR** (X.0.0): a recommendation was reversed
   Update both `marketplace.json` and `plugin.json` versions.

5. **Commit with a detailed log.** List substantive changes (not file diffs). Cite new evidence URLs. If a recommendation reversed, say so explicitly in the commit message.

6. **Reinstall locally to verify.**
   ```bash
   claude plugin marketplace update <name>          # OR remove + re-add for local-path marketplaces
   claude plugin update <plugin>@<marketplace>
   # then /reload-plugins
   ```

## Research agent prompt template

```
Subject: <topic name>

Background:
- Skill currently claims: "<verbatim claim from SKILL.md or references/*.md>"
- Cited sources: <urls>
- Last known status: <date> "<status>"

Open questions:
1. <specific question>
2. ...

Sources to prioritize:
- <official docs>
- <community channels>
- <recent threads filtered by date>

Deliverable (~500-1000 words, dense, no padding):
- For each open question: [confirmed | refuted | updated | no change | still unknown]
- Cite URLs inline
- Distinguish official docs / staff statements / community measurement
```

## Anti-patterns

| Don't | Why |
|---|---|
| Refresh from memory without spawning research agents | Stale recommendations are the failure mode being fixed; the model's training data IS the stale source |
| Apply findings without citing the new source URL inline | Future audit can't verify the chain |
| Bump MAJOR for additive changes | Only a reversal is MAJOR; new evidence supporting an existing recommendation is PATCH/MINOR |
| Skip the version bump | Users who installed the plugin won't get the update |
| Edit the skill before the research agents return | Premature; let evidence drive the change |
| Spawn 10+ agents for parallel research | Context blows up on synthesis; 4–6 max |

## When to add a new reference file vs editing existing

- **New reference file** when: research surfaces a coherent new topic too large for an existing reference
- **Edit existing reference** when: change is content refinement within an existing topic
- **Add to SKILL.md** when: the change updates the high-level guidance (rare — most updates land in references)

## Trigger phrases

- "Refresh the X skill"
- "Are the cache mechanics still accurate?"
- "Audit prompt-tuning for stale claims"
- "OpenAI just shipped GPT-5.6 — update the skill"
- "Has anything changed about Y recently?"
