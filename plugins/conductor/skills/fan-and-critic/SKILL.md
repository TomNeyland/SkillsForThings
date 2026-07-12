---
name: fan-and-critic
description: Use when one pass isn't enough to trust a result — you need breadth (multiple options, perspectives, or parallel coverage), an adversarial check of an artifact before you act on it, or both. Not for a single-fact lookup or a trivial low-stakes change.
---

# Fan and critic

![Given a candidate patch, surrounding repository code, and one identical review prompt, two independent reviewers return ranked failure scenarios with locations and severity; keep every concrete issue, record a clean result when none remain, and send ship-blocking or substantively fixed code to two new reviewers.](assets/fan-and-critic.png)

Two halves of one move. **Fan** diverges — generate options, perspectives, or coverage in parallel.
**Critic** converges — judge them hard, trying to refute. Neither works alone: fanning without a
critic leaves you N unjudged outputs (noise); critiquing without fanning is one perspective on one
artifact. The power is the pairing.

The **dual-model review is the two fused**: fan out two independent reviewers, critic-frame both
(refute, not confirm), converge their union. Reach for the whole duality when the stakes are real;
reach for one half when you only need breadth (fan) or only need to verify one existing artifact
(critic).

## FAN — diverge

Split one task into independent units, one agent each, run concurrently.

- **When:** a work-list of similar items; breadth beyond one context; independent perspectives that
  must form without seeing each other's; separate subsystems covered in parallel.
- **When NOT:** a serial dependency (B needs A's result → sequence it); a single-fact lookup (just do
  it); one coherent voice needed (fan the research that *feeds* it, write it yourself).
- **Slice into units:** owned (has all it needs), non-overlapping (no shared file/record/decision),
  sized to complexity (mechanical → cheap agent, judgment → strongest), self-contained brief (goal,
  boundaries, what "done" is, where to report).
- **Barrier vs pipeline:** a barrier (wait for every unit before the next stage) ONLY when that stage
  needs every result *together* — dedup across the set, an early-exit on the total, one synthesis
  pass. Otherwise pipeline — a barrier when nothing needs the full set idles your fastest agent on
  your slowest.
- **Reconcile:** dedup + union; log dropped coverage (top-N, a sample) — silent truncation reads as
  "covered everything," which is false.

## CRITIC — converge

Dispatch reviewers to **refute** an artifact, not confirm it.

- **Core procedure:** two reviewers, the verbatim **same** prompt — a stronger model + a cheaper one,
  or two runs of one. Don't split lenses for a routine review; the model variance itself is the
  diversity. Each catches ship-blockers the other passes — the disagreement, and the union of what
  either flags, is the signal (not the average, not the more-confident voice).
- **Adversarial framing:** refute not confirm; fault on uncertainty (an unverifiable claim is a
  finding, not a pass); verify against the **real artifact** — the code / document / data — never the
  diff's own comments, the commit message, or the author's summary.
- **Output:** ranked findings, each a concrete failure scenario + location + severity; a verified
  "clean" is a first-class result.
- **Auto-re-review:** if any finding was blocks-severity OR the fix added substantive new code, the
  fixed unit goes back through a **fresh** pair (new agents, same prompt, carrying the prior
  findings) — verify each fix, hunt regressions. Loop until clean or minor-only.
- **Perspective-diverse variant:** when a claim can fail along genuinely different axes (wrong /
  exploitable / doesn't reproduce), give each reviewer a distinct lens instead of identical prompts.
  Reserve it for that case; a routine review wants identical prompts — the point is catching one
  model's blind spot, not covering more ground per reviewer.

## Composes with

`coordinate-agents` — the full run that fans work out, critics it back, and integrates the results.
