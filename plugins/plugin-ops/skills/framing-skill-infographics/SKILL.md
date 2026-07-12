---
name: framing-skill-infographics
description: Use when creating or revising a shareable infographic for a skill in the SkillsForThings marketplace; when deciding which benefit, mechanism, proof, hook, or workflow detail from a SKILL.md deserves visual space; or when a skill image feels product-first, feature-led, generic, overstuffed, or forced into an inappropriate pain story.
---

# Framing Skill Infographics

## Overview

Turn a repository skill into a self-contained explanation of the job it performs and how it performs it. The image may open with a recognizable problem, but comprehension of the working method is the primary job; persuasion is secondary.

The image must explain itself after it is separated from this repository, its post caption, and the skill name. Default audience: a technically literate stranger encountering it in a general programming or AI feed.

If the request includes a finished image, **REQUIRED SUB-SKILL:** Use `creating-technical-infographics` after producing the editorial brief. That skill owns SVG style, research-backed visual choices, Reddit geometry, and raster QA. If the request asks only for framing or a brief, stop after the brief.

Read [references/repo-skill-archetypes.md](references/repo-skill-archetypes.md) for the current marketplace catalog and framing precedents. Verify every catalog entry against the live target skill; the source file wins.

## Choose the surface before the story

The repository has two different information architectures. Do not use the skill-card formula at every directory level.

| Surface | Reader job | Required image structure |
|---|---|---|
| Individual skill | Decide whether one capability solves the situation | One self-contained explainer: situation, useful change, mechanism, proof |
| Plugin package README | Choose among the skills in this package | Visual index: package job, one row per live skill, public trigger, useful output, selection rule |
| Repository README | Understand the marketplace and choose a package | Marketplace index: repository job, one row per live package, package scope, choose-if cue, child count |

Directory images are **reference / orientation** artifacts, not teaser posters. Their headline names the collection's shared job. Their dominant visual is the live child index. A package image must not borrow one child's pain story and present it as the whole package.

Keep directory titles literal: **Package index** at repository root and **Skill index** inside a plugin. Do not add a hook, pain opener, promise, CTA, or closing slogan. The index itself is the artifact: names, scope or use-when, and output. Prefer the visual register of technical reference documentation over a landing page.

Build directory indexes from the filesystem, manifests, and live descriptions—not from a remembered catalog. When a child is added, renamed, moved, or removed, its parent index is stale until regenerated.

For every directory row, translate names into a recognizable choice:

```text
child name  →  choose when this is happening  →  artifact or decision produced
```

Keep names visible because the image is navigation. Unlike a skill teaser, a directory index may lead with package and child names; those labels are the handles the reader needs next.

## Cold-reader contract

Before selecting a headline, write this sentence in ordinary reader language:

> For a developer who **[recognizable situation]**, this image shows **[useful change]** by **[plain-language mechanism]**.

The finished image must let a stranger answer, without a caption:

1. What situation or problem is this about?
2. Why does it matter?
3. What should I understand or do differently?

Name the concrete object being acted on: code change, prompt, schema, copy, backlog, design document, memory file, or other familiar artifact. A framework diagram without a concrete object fails this contract.

For a directory index, replace the single-skill questions with:

1. What collection is this?
2. Which child should I choose for my situation?
3. What will that child help me produce or decide?

A stranger must be able to select the right row without opening every child README. The adjacent Markdown supplies installation and full descriptions; it must not repair an index whose rows are indistinguishable.

Treat terminology from the target skill as source material, not public copy. For every coined or repository-specific term, choose exactly one treatment:

- replace it with ordinary programming/AI language;
- define it inline before using the short label; or
- remove it and show one concrete example instead.

If understanding the image requires a glossary, choose a narrower example. The image is not a compressed manual.

## Read the source completely

Read the target `SKILL.md` and every reference it requires. Extract:

- the triggering moment in the description;
- the reader's desired change;
- the mechanism unique to this skill;
- the observable proof or decision it produces;
- the detail most likely to be misunderstood;
- claims requiring a source, measurement, or real artifact.

Do not frame from the skill name or headings alone.

## Explain the solution, not only the stakes

An individual skill card must expose a complete solution trace. A before/after example or contrarian headline can prove the problem, but it does not explain the skill by itself.

Extract and show:

1. **Input** — the concrete artifact or state the skill receives.
2. **Operations** — three to six causal steps the skill actually performs, in order.
3. **Decision criteria** — classifications, branches, stop conditions, or source hierarchy that determine the next step.
4. **Output** — the report, patch, brief, ranked list, model, decision, or other artifact produced.
5. **Success check** — how the reader knows the job is complete.

At least half of an individual skill image should explain operations, decision criteria, and output. The opener and problem proof together should not dominate the canvas. If a fresh reader can repeat the headline but cannot describe what happens after invoking the skill, the card is marketing copy and fails.

## Choose one primary archetype

| Observable predicate | Primary archetype | Opening |
|---|---|---|
| Reader is already losing time, money, trust, or correctness | Struggling moment | Lived problem → mechanism → fix |
| Value depends on replacing a common but wrong model | Contrarian reframe | Assumption → counterexample → better model |
| Reader wants an ambitious new capability or outcome | Transformation | Desired future → path → evidence |
| Skill makes work more rigorous, repeatable, or trustworthy | Method / quality multiplier | Quality gap → method → observable improvement |
| The experience, reveal, or artifact is itself the appeal | Curiosity / experience | Intriguing question → reveal → implication |
| Reader must choose between editions, methods, or tradeoffs | Comparison / upgrade | Decision criterion → decisive differences → rule |
| Skill mainly organizes a field or lookup space | Reference / orientation | Orientation question → map → use rule |

Choose the archetype that supplies both the opener and the proof. Record secondary archetypes only as supporting context. Do not combine multiple opening formulas.

PAS and Jobs-to-be-Done apply when the trigger contains a real struggling moment. Agitation is the mechanism that explains the cost; it is not theatrical language. If the skill is exploratory, aspirational, comparative, or referential, use its matching archetype instead.

## Decide what earns visual space

An individual skill image contains:

1. **The skill/job label** as a navigation handle.
2. **The triggering situation** in ordinary reader language.
3. **The concrete input** the workflow acts on.
4. **The solution trace**: operations and decision criteria in public language.
5. **The output and completion check**.
6. **One proof example** only where it clarifies the method.

A hook is optional. When used, it occupies no more than the opening quarter of the page and cannot displace the solution trace.

The adjacent Markdown contains installation, the full workflow, edge cases, detailed citations, long examples, model/provider knobs, and complete API or command syntax. It must not supply a premise missing from the image.

Use exact repository facts. Performance numbers require the skill's cited evidence or a real measurement. Example outputs must come from a real run or be visibly schematic. Preserve legitimate negative outcomes: if research can conclude “build custom,” or review can conclude “clean,” the graphic must not manufacture a guaranteed win.

## Write the editorial brief

For an individual skill, use the explainer brief below. For a plugin or repository directory, use an index brief with: **collection job**, **live children**, **row mapping (name / choose when / output)**, **selection rule**, **omit from image**, **provenance**, and **five-second routing test**. Do not force directory work into a hook/promise/proof brief.

Produce exactly these sections:

```markdown
# Infographic brief: <skill-name>

## Audience conversation
Who the reader is; the sentence already in their head; what changes after reading.

## Cold-reader premise
Complete: “For a developer who ..., this image shows ... by ... .” Name the concrete object.

## Primary archetype
One archetype, the observable predicate that selected it, and why alternatives are secondary.

## Takeaway
One sentence the reader should remember tomorrow.

## Headline
One final headline. Product/skill name excluded unless recognition of that name is itself the value.

## Proof visual
The single relationship, sequence, comparison, or artifact to draw. Include exact labels and source facts.

## Solution trace
Exact input, ordered operations, decision criteria or branches, output artifact, and success check the image must expose.

## Public-language mapping
List every source term that could require repository context and its exact in-image replacement or inline definition.

## Supporting points
One to three concise points.

## Omit from image
Specific source material that belongs in Markdown instead.

## Skill-name role
Exact closing label or invocation after the value is established.

## Provenance
Source paths, citations, measurements, and whether examples are real or schematic.

## Five-second test
Write the expected cold reader's answers to: situation, importance, and changed behavior.
```

## Integrate the finished artifact

Write both files beside the target skill:

```text
plugins/<plugin>/skills/<skill>/assets/<skill>.svg
plugins/<plugin>/skills/<skill>/assets/<skill>.png
```

Add the PNG with useful alt text immediately after the skill `README.md` H1. Do not embed the image in `SKILL.md`; that file remains instruction-only.

The SVG remains the editable source; the README references the PNG for reliable rendering. Update the plugin and marketplace versions when publishing the asset.

## Review gate

- Hook describes the reader's world, not the skill's feature list.
- Headline and premise identify the domain, concrete object, and stakes without a caption.
- Archetype matches the trigger; pain was not invented.
- The visual proves the mechanism instead of decorating the copy.
- A fresh reader can describe what the skill actually does after invocation: input, operations, decisions, and output.
- Method coverage occupies at least as much visual weight as the opener and problem proof combined.
- Every coined term is translated, defined inline, or removed.
- Arrow inputs and outputs are recognizable without the target SKILL.md.
- No internal orchestration detail appears unless it is causal proof.
- No unsupported number, fabricated output, or apologetic limitation copy appears.
- The name arrives after the value.
- Asset paths and Markdown reference are exact.
- The README references the PNG immediately after its H1; SKILL.md contains no image embed.
- The rendered artifact passes `creating-technical-infographics` verification.
- A directory card is an index, includes every live direct child, and gives each row a distinct choose-if cue.
- A package or repository index was checked against the current filesystem and manifests after the final edit.

## Mandatory cold-reader test

Give the final PNG—without its filename, caption, README, target skill, or repository context—to a fresh reader. Ask for:

1. the situation/problem;
2. the method in their own words;
3. what they would do differently;
4. every unclear term or relationship;
5. a 0–5 self-contained comprehension score;
6. whether they would share it without adding a caption.
7. the exact workflow they believe runs after invocation, including input and output.

Pass only when the first three answers and workflow trace match the brief, the score is at least 4, no unclear term blocks the method, and the reader would share it without explanatory caption. A failure triggers reframing and a new PNG—not a glossary appended to the same crowded image.

For a directory index, also name two reader situations and ask the fresh reader which row they would choose. Both routes must match the brief. A directory image that explains the collection but cannot route a reader fails.
