# Current SkillsForThings Skill Archetypes

This is a starting map for consistent marketplace storytelling, not authority over the live files. Re-read the target skill before producing a brief. Reclassify when its trigger, promise, or mechanism changes. Catalog language is analysis shorthand; translate it before putting it in a public image.

## Catalog

| Skill | Primary archetype | Reader conversation / hook territory | Proof visual |
|---|---|---|---|
| `openai-prompt-cache` | Struggling moment | “Why did the repeated prompt cost full price again?” | Two byte prefixes diverge at one changing value; stable-first/variable-last repair |
| `cutting-internal-leaks-from-copy` | Struggling moment | “Why does accurate copy still sound AI-written?” | Reader-facing sentence with backstage material highlighted, then clean reader-language |
| `autonomous-build-session-pacing` | Struggling moment | “Why did the long autonomous session stall, rush, or leave work unshipped?” | Time budget across heartbeat, feature-sized commit/push cadence, and re-triage |
| `align-terminology` | Contrarian reframe | “A field name can be syntactically clear and still wrong to every expert.” | Invented name → expert question → authoritative term recognized without explanation |
| `prior-art` | Contrarian reframe | “Before this custom design becomes load-bearing, is the real problem already standardized?” | Surface solution Y versus root problem X; adopt/adapt/build gate |
| `autonomous-build-purpose-layers` | Contrarian reframe | “More features do not necessarily make a deeper product.” | Horizontal parity/polish path versus vertical sequence of new user questions answered |
| `autonomous-build-jealousy-ranking` | Contrarian reframe | “Easy-to-build is not the same as worth building.” | Candidate backlog filtered by named audience, tool/toy value, red-team, kill-and-replace |
| `autonomous-build-commit-essays` | Contrarian reframe | “A git log can preserve product intent, not merely diffs.” | Thin commit subject versus narrative commit tied to audience and purpose layer |
| `creating-technical-infographics` | Method / quality multiplier | “Why did ‘restrained’ still turn into a tiny dashboard?” | Card-grid baseline versus one-path technical-document page; rendered collision check |
| `fan-and-critic` | Method / quality multiplier | “Several plausible agent answers still do not tell you which result is safe to use.” | Independent attempts broaden coverage; separate reviewers try to find faults in the combined real artifact; every concrete finding is kept |
| `coordinate-agents` | Method / quality multiplier | “Parallel agents can each finish their part while the combined system still fails at the boundaries.” | Split owned work, review each result, connect real producers to consumers, then inspect the assembled whole for missing connections |
| `orchestrating-greenfield-builds` | Transformation | “How does a long AI-assisted build preserve the same product direction when agents and context keep changing?” | Record product constraints in durable design documents, test those documents with an independent reader, then build and review against them |
| `autonomous-build` | Transformation | “Give an autonomous session a product arc before it gets a scaffold.” | Audience/arc/budget pins becoming a layered build system rather than an unaimed feature pile |
| `memory-mood` | Curiosity / experience | “Your assistant remembers you. What mood did that accumulation create?” | Growing memory snapshots → fresh isolated judges → emotional arc and feelings feed |
| `memory-mood-openai` | Comparison / upgrade | “Is that mood change signal or one model draw wobbling?” | Single reading variance versus k independent samples, mean curve, and ±1σ band |
| `refresh-skill` | Struggling moment | “The file did not change, but the advice may already be stale.” | New release → time-sensitive claim inventory → evidence status → semver update |
| `admitting-a-skill` | Method / quality multiplier | “A clean grep can still miss a private project leak.” | Deterministic lint → two independent full reads → reconcile all concrete findings → release gate |
| `framing-skill-infographics` | Reference / orientation | “Which part of a skill deserves the image?” | Trigger/promise/mechanism inventory routed through archetype selection to one brief |

## Archetype-specific content tests

### Struggling moment

The source description must contain an observable symptom or costly moment. Use the reader's language, not invented drama. Show why the problem persists even when the request “works.” The feature or command proves the repair.

### Contrarian reframe

Name the belief precisely enough that a skeptical reader might hold it. The proof must distinguish the two models. Avoid empty “you are doing X wrong” provocation.

### Transformation

Make the destination concrete: which new question can the reader answer, which artifact exists, or which responsibility becomes manageable? A feature montage is not a transformation.

### Method / quality multiplier

Show the input and the observable quality change. The method's steps matter only where they causally produce the improvement. Do not promise certainty; show how blind spots, variance, or seams become visible.

### Curiosity / experience

The reveal must come from a real run or a clearly labeled schematic. Protect the premise from overclaiming: an emotional visualization is an experiment in model readings, not proof of sentience.

### Comparison / upgrade

Name the decision criteria before rating options. Use shared dimensions, consistent definitions, and a selection rule. Do not make the more expensive or complex edition automatically win.

### Reference / orientation

Expose the organizing system and the question it helps answer. The image should be a map with a use rule, not a compressed table of contents.

For repository and plugin-package READMEs, reference / orientation is mandatory. Show every live direct child as a routing row: public name, recognizable choose-if cue, and output or decision. The root routes to packages; a package routes to skills. A directory image is successful when a stranger can choose where to go next, not when one child sounds exciting.

## Public-copy translations

Use these as examples of the translation pass, not mandatory phrasing:

| Repository shorthand | Public-language starting point |
|---|---|
| fan | multiple independent attempts or task owners |
| critic | separate reviewers trying to find faults |
| union coverage | combine the distinct useful results |
| union findings | keep every concrete issue either reviewer found |
| user pins | recorded product constraints: audience, platform, tone, scope |
| ethos → spec → system doc | product principles and durable design documents |
| author trace / cold-reader trace | author walks through the design; an independent reader tries it from the documents alone |
| code-law review | check implementation against repository rules |
| seam trace | verify each component has a real producer, consumer, and exit |
| purpose layer | a feature that answers a new user question |
| jealousy ranking | rank ideas by differentiation for a named audience |
| commit essay | a commit message that preserves why the feature exists |
| XY problem | the proposed solution may differ from the underlying need |

A short label may follow its plain-language definition. It may not substitute for that definition.

## Cross-skill boundaries

- The framing skill decides **what to say and show**.
- `creating-technical-infographics` decides **how the artifact looks, renders, and verifies**.
- The target `SKILL.md` and its references decide **what is factually true**.
- The surrounding Markdown carries the workflow and detail that the image intentionally omits.

Do not let one layer silently take over another. A beautiful graphic cannot repair a weak promise; persuasive framing cannot invent a claim; a complete workflow does not belong inside the image.
