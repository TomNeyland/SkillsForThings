# Repository Infographic Pass

## Goal

Give every skill, plugin package, and the repository root a plain 1600×2000 infographic in the approved technical-document style, referenced from Markdown.

## Required skills

Every skill-card worker must read and apply both:

- `plugins/plugin-ops/skills/framing-skill-infographics/SKILL.md`
- `plugins/misc/skills/creating-technical-infographics/SKILL.md`

Read every reference those skills require plus the complete target `SKILL.md` and its required references.

## Skill deliverable

For target `plugins/<plugin>/skills/<skill>/`:

1. Create `assets/<skill>.svg` and `assets/<skill>.png`.
2. Create `README.md` containing an H1 and the PNG reference.
3. Add the same PNG immediately after the H1 in `SKILL.md`.
4. Render at 1600×2000, validate XML, inspect full-size and 400×500 previews, and re-render deterministically.
5. Keep essential content inside `y=200..1800`; use 120 px side margins.
6. Make the PNG self-contained for a technically literate stranger in a general programming or AI feed. Translate every repository-specific term, name a concrete object, and establish situation, importance, and changed behavior inside the image.
7. Cross-test the PNG without caption, filename, README, repository, or target skill context. It passes only if the reader correctly explains situation/method/action, scores comprehension at least 4/5, and would share it without an explanatory caption.
8. Do not modify manifests, marketplace files, package READMEs, or files outside the owned skill directory.

## Worker rotation

### Batch 1

- `misc/align-terminology`
- `misc/cutting-internal-leaks-from-copy`
- `misc/prior-art`

### Batch 2

- `misc/orchestrating-greenfield-builds`
- `plugin-ops/refresh-skill`
- `conductor/fan-and-critic`

### Batch 3

- `conductor/coordinate-agents`
- `conductor/autonomous-build`
- `conductor/autonomous-build-session-pacing`

### Batch 4

- `conductor/autonomous-build-purpose-layers`
- `conductor/autonomous-build-jealousy-ranking`
- `conductor/autonomous-build-commit-essays`

### Batch 5

- `memory-mood/memory-mood`
- `memory-mood/memory-mood-openai`

## Lead-owned targets

- Finish the two meta-skill images and READMEs.
- Add the existing `openai-prompt-cache` image to a skill README.
- Create package images and READMEs for `conductor`, `memory-mood`, `misc`, `plugin-ops`, and `prompt-tuning`.
- Create the repository image and add it to the root `README.md`.
- Bump versions once after the full pass.
- Validate every SVG, PNG, Markdown reference, skill, plugin, and marketplace manifest.
