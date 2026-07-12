# SkillsForThings

A Claude Code plugin marketplace.

## 🔥 GOLDEN RULE: Domain-Agnostic

Skills in this marketplace must work for **any** LLM-prompting use case — chat agents, RAG systems, structured extraction, code generation, content moderation, anything.

**Never reference:**
- Specific industries (healthcare, finance, legal, biomedical research)
- Specific datasets, products, internal company projects, or proprietary business logic
- Specific examples that only make sense in one domain

If an example clarifies a concept, use a generic placeholder domain (e.g., "a customer support agent", "a code review tool", "a structured-extraction pipeline") — not a real product.

## Layout

```
.claude-plugin/marketplace.json    Marketplace manifest
plugins/<plugin-name>/
  .claude-plugin/plugin.json       Plugin manifest (optional)
  skills/<skill-name>/SKILL.md     Skill content
  skills/<skill-name>/references/  Heavy reference material (>100 lines)
```

## Adding a new skill

1. Create directory under an existing plugin: `plugins/<plugin>/skills/<new-skill>/`
2. Write `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: <kebab-case-name>
   description: Use when <triggering conditions only — NOT a workflow summary>
   ---
   ```
3. **Description = triggers/symptoms only.** Do NOT summarize what the skill does or its workflow. See `superpowers:writing-skills` for the full guidance.
4. `references/*.md` is for genuinely optional depth a reader would deliberately seek out (an API reference table, a heavy spec) — not a length-management escape valve. Agents skim/skip reference files, so load-bearing technique content stays inline in SKILL.md even if that makes it long. A skill teaching several real, distinct scenarios can run well past ~1800 words — that's fine; length alone isn't a quality problem if every part earns its place.
5. Bump `version` in marketplace.json (and plugin.json if present).
6. Test locally: see "Test locally" below.
7. Commit and push.

## Adding a new plugin

1. Create `plugins/<new-plugin>/.claude-plugin/plugin.json`
2. Create `plugins/<new-plugin>/skills/` (and `commands/`, `agents/`, `hooks/` as needed)
3. Add an entry to `.claude-plugin/marketplace.json` under `plugins[]`
4. Update README.md plugin index

## Test locally

```bash
# Add this repo as a marketplace from the local path
claude plugin marketplace add /path/to/SkillsForThings

# Install the plugin
claude plugin install <plugin-name>@SkillsForThings

# Restart Claude Code or run /reload-plugins
```

## Style

- Specific symptoms in descriptions, not abstract categories
- Concrete numbers (token counts, TTLs, percentages) over vague claims
- Reference original sources for any non-obvious technical claim
- Code examples: pick ONE language (Python by default), make it complete and runnable
- One excellent example beats five mediocre ones across languages
