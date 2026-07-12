# Skill Source-Integrity Repair Plan

## Goal

Repair every SkillsForThings skill and infographic that was derived from a name, a partial reading, or the wrong workflow instead of the canonical source skill.

## Global constraints

- The canonical local skill is authoritative for meaning. Read it completely before judging or editing the repository port.
- Preserve the canonical trigger, roles, inputs, operations, decision rules, output, and completion condition. Genericize private context only; never substitute a different public workflow.
- A repository-native skill with no external canonical file is checked against its full live `SKILL.md` and creation history.
- The infographic must teach the verified mechanism. It cannot promote one subroutine as the whole skill.
- `README.md` references the PNG immediately after its H1. `SKILL.md` contains no image embed.
- SVG is editable, 1600×2000, plain technical-document style, and renders deterministically to the committed PNG.
- Do not edit shared manifests, root/package indexes, or files outside the assigned skill directories. Report shared-file corrections to the root agent.
- Do not commit; the root agent integrates and verifies the complete repository.

## Confirmed corruption

`fan-and-critic` currently redefines **fan** as “fan out.” The canonical `autonomous-build-fan-and-critic` uses **fan** in the ordinary sense: an enthusiast who identifies what genuinely lands, opposed by a harsh critic. The lead weighs convergence and divergence between the two. Repair both the skill and its infographic accordingly.

## Work units

### Conductor — 7 skills

- `autonomous-build`
- `autonomous-build-commit-essays`
- `autonomous-build-jealousy-ranking`
- `autonomous-build-purpose-layers`
- `autonomous-build-session-pacing`
- `fan-and-critic` → canonical `autonomous-build-fan-and-critic`
- `coordinate-agents` (discover and verify its actual source; do not infer from the name)

### Misc + prompt-tuning — 6 skills

- `prior-art`
- `align-terminology`
- `orchestrating-greenfield-builds`
- `cutting-internal-leaks-from-copy`
- `creating-technical-infographics`
- `openai-prompt-cache`

### Plugin operations + memory — 5 skills

- `admitting-a-skill`
- `refresh-skill`
- `framing-skill-infographics`
- `memory-mood`
- `memory-mood-openai`

## Per-skill gate

1. Record the authoritative source path or `repo-native` provenance.
2. Compare the trigger, roles/nouns, ordered method, branches, output, and completion check.
3. Classify the current port as faithful, materially incomplete, or semantically corrupted.
4. Repair every material mismatch in the owned skill directory.
5. Render and inspect the PNG at full size and 400×500.
6. Verify XML, 1600×2000 sRGB, deterministic SVG→PNG equality, README-only embed, and a caption-free method trace.
7. Report the verdict, source, repairs, and any shared index/catalog changes the root agent must make.

## Completed verdicts

| Skill | Source-integrity verdict | Repair |
|---|---|---|
| `autonomous-build` | Faithful genericization | None |
| `autonomous-build-commit-essays` | Faithful genericization | None |
| `autonomous-build-jealousy-ranking` | Faithful genericization | None |
| `autonomous-build-purpose-layers` | Faithful genericization | None |
| `autonomous-build-session-pacing` | Faithful genericization | None |
| `coordinate-agents` | Core workflow faithful; false composition reference | Removed the incorrect dependency on `fan-and-critic`; marked as current successor to the greenfield prototype |
| `fan-and-critic` | Semantically corrupted: “fan” had been redefined as fan-out | Restored standing enthusiast fan versus harsh critic, separate feedback, convergence/divergence judgment, README, and infographic |
| `prior-art` | Workflow faithful; numeric decision gate used undefined “coverage” and overlapped at exactly 50% | Defined weighted must-have fit before scoring, made the cutoffs an explicit default heuristic, gave disqualifying gaps precedence, and removed the overlap |
| `align-terminology` | Workflow faithful; example falsely treated an ISO 8601 value-format standard as authority for a field name | Replaced it with an RFC 6838 media-type example and corrected package-index output wording |
| `orchestrating-greenfield-builds` | Faithful active specialized workflow; prototype-ancestor status was missing and image was incomplete | Marked prototype ancestor of `coordinate-agents`; retained its active greenfield trigger; rebuilt full ten-stage image and routing copy |
| `cutting-internal-leaks-from-copy` | Skill faithful; image narrowed the method to one leak class | Rebuilt image around both sweeps, all eight classes, editing branches, and completion gate |
| `creating-technical-infographics` | Faithful repo-native skill and image | None |
| `openai-prompt-cache` | Port matched its old source but had become materially stale and internally contradictory | Refreshed from current official OpenAI documentation; separated GPT-5.6+ explicit breakpoints and 30-minute minimum lifetime from earlier-model retention; added read/write accounting; rebuilt the image |
| `admitting-a-skill` | Workflow faithful; false composition reference | Removed incorrect dependency on `fan-and-critic`; retained its direct two-run admission critic gate |
| `refresh-skill` | Canonical skill exact; image omitted research-agent clustering and synthesis | Rebuilt end-to-end refresh workflow and completion gate |
| `framing-skill-infographics` | Skill faithful; image incorrectly forced skill, plugin, and repository surfaces through one explainer flow | Rebuilt the image around surface-specific briefs and corrected the shared archetype catalog |
| `memory-mood` | Wording falsely implied every memory was always a rendered timepoint; image omitted named staging/render roles | Corrected sampled/staged timepoints, named Sonnet judges and scripts, rebuilt image and shared index copy |
| `memory-mood-openai` | Statistically corrupted terminology and claims | Replaced “confidence band” with call-to-call spread; removed unsupported ±0.1 and tightening claims; rebuilt image and shared copy |
