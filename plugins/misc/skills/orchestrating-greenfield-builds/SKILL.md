---
name: orchestrating-greenfield-builds
description: Use when a user brings a product idea for a long autonomous multi-agent build session — greenfield or rebuilding a mediocre predecessor — and expects showcase-grade quality ("this will be public", "make it excellent", "unbounded time"). Also when a build will span many sessions/context windows and future agents must inherit intent, or when a predecessor codebase exists and you're tempted to inherit its stack, fixes, or roadmap.
---

# Orchestrating Greenfield Builds

## Overview

You are the product's **continuity of intent**. Delegate everything except
judgment: capturing decisions, making rulings, and authoring design docs.
Untested agents default to code-in-45-minutes, stack-by-fluency, design as
a private scratch note, self-only validation, and patch-guessing on vague
feedback. This process replaces each of those with a mechanism.

Full phase detail, prompts, and templates: `references/playbook.md`.

## The loop

1. **Pins, not interviews.** Users fire decisions mid-flight ("make it a
   roguelite", "keep it PG"). Catch each pin, confirm in one line, keep
   moving. Ask only questions whose answer changes what you build; give a
   recommendation with every question.
2. **Prior-art before stack.** Fan out parallel research agents (current
   landscape, the tool the user assumed, the heavyweight option). Decide
   from a comparison table: adopt / adapt / build. Never pick by fluency;
   never inherit the predecessor's stack because it's there.
3. **Predecessors are negative space.** Mine them with epistemic triage:
   *platform facts* (verify, then trust), *experience observations*
   (re-test cheaply, never assume), *patches on wrong approaches*
   (symptoms — never import the cure). Unbuilt promises are wishes.
   Then be provenance-blind: nothing adopted because v1 promised it,
   nothing rejected in protest because v1 touched it.
4. **Write the ethos, then the spec, then per-system design docs.** The
   ethos is sensibility (taste, epistemics, working rules, definition of
   done) — the thing that survives context loss. Every agent's read order
   starts there. Design-before-code is an epic with issues.
5. **Panels pitch; judges score; you author.** For make-or-break systems,
   spawn 2–3 designers with *rival lenses* plus adversarial judges — then
   write the doc yourself: rulings with provenance, rejections named,
   judge-splits decided by you. Panels critique; they never ghostwrite.
6. **Freeze interfaces before consumers exist.** Event taxonomies with
   schema versions, consumer contracts ("consumers scale with payload
   values, never event counts"), every constant as runtime-mutable data.
   Downstream systems then arrive as data, not refactors.
7. **Play the product in your head — twice.** Author playthrough first;
   then an independent cold-reader agent, firewalled from your trace,
   plays from the docs alone and logs moments / seams / inventions
   (each invention = a doc gap) / exploits. Diff the two. Author
   blindness is real: expect the cold reader to catch contradictions
   your own narration walked into.
8. **One deep builder per system,** executing its binding doc — then a
   design-fidelity reviewer and a code-law reviewer in parallel, a fix
   pass, and mechanical gates. API-level adaptation allowed;
   architectural deviation forbidden unless documented.
9. **Make feedback data-addressable.** Deterministic core + always-on
   input recorder + a marker key during human playtests: "feels off"
   arrives pinned to a replayable moment, and you analyze instead of
   guess.
10. **Humans judge joy; agents measure.** Quality gates that are feelings
    belong to human hands. Commit essays, not diffs described.

## Common mistakes

- Authoring docs by committee (synthesis is your job; panels are input)
- One mental playthrough (yours) counted as validation
- Freezing nothing, then rewiring every system when the next one lands
- Treating the predecessor's TODO list as a roadmap
- Shipping "technically exists" — the bar is rich and fully wired
