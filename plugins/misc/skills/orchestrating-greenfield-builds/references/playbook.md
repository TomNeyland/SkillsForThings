# Playbook — orchestrating greenfield builds

Expanded mechanics for each phase of SKILL.md's loop. Examples use generic
placeholder products (a rhythm game, a dashboard); adapt freely.

## 1. Pins

A **pin** is a user decision caught mid-conversation: audience, platform,
tone rules ("keep it public-friendly"), scope reversals, quality bars,
role assignments ("you're the manager; cheaper models may read code but
not write it"). Practice:

- Restate each pin in one line when caught; never re-ask a pinned thing.
- Pins override your process ceremony. "Get going quickly" + a new pin
  every minute means: engage, don't interview.
- Keep asked-questions to 2–3 per round, each with a recommended option
  and honest trade-offs. Previews (ASCII mockups) beat prose for
  visual-shape questions.
- Durable pins go in the repo docs the same hour (ethos/spec), not just
  chat history — sessions die; documents don't.

## 2. Prior-art fan-out

Launch 3–5 parallel read-only research agents before any stack/framework
decision. Useful angles: current-state-of-X ("has vNext gone stable? do
maintainers recommend it for new projects?"), head-to-head landscape
comparison (versions, adoption, activity, fitness table), the
tool-the-user-assumed ("is three-of-something actually used for this?"),
the heavyweight alternative (real payload/complexity costs). Require
sources with dates and a one-line verdict per agent. Decide adopt / adapt
/ build in a table the repo keeps (`docs/research/`). Record the risk and
the fallback ("if the new major disappoints, dropping to the previous
major is an afternoon — the API shape was preserved").

## 3. Predecessor mining

Two parallel read-only agents: an **asset/inventory mapper** (what exists,
what's licensed how, what was never used — unused inventory is free
content for v2) and a **knowledge miner** (tuning values, formulas,
progress-log lessons, known bugs). Then stamp the miner's report with an
**epistemic-status header** before anyone trusts it:

1. *Platform facts* — properties of the engine/framework, not of the old
   code. Verify against the current version, then rely on.
2. *Experience observations* — n=1 findings from a mediocre build.
   Re-test cheaply; never assume.
3. *Patches on wrong approaches* — the teleport-nudge, the cooldown
   masking a race. Symptoms, not solutions. If your clean architecture
   never produces the disease, never import the cure.

Corollaries: the predecessor's docs may lie about its own code (trust
code you read and behavior you measure); its unbuilt roadmap is brainstorm
residue, not validated design; and **provenance-blind evaluation** cuts
both ways — rejecting an idea *because* the predecessor touched it lets
the mediocre thing steer the successor exactly as much as copying it.

## 4. The document stack

- **ETHOS** (or similar sober name — not "bible"): sensibility, pillars in
  authority order, taste rules, epistemic discipline, working rules,
  definition of 1.0 ("every system rich and fully wired — a player
  completes real runs; no skeleton-ware"). It's how-to-think, not
  what-to-build. Do not reference the user by name in repo docs if asked.
- **SPEC**: the product — one-sentence spine, systems, architecture.
  Find the spine: the single quantity every system reads or writes (in a
  momentum game: speed; in a dashboard: trust in the numbers). Systems
  that don't touch the spine get asked why they exist.
- **docs/design/*.md**: one binding doc per system, authored by you,
  written before that system's implementation session. Status line,
  provenance of every contested decision, constants tables with units,
  event taxonomies, pre-registered A/B questions for the human gate,
  risks. An index README tracks authored/pending.
- **Read order for every spawned agent**: ethos → spec → its design doc.
  Tell agents NOT to read the predecessor archaeology unless their task
  demands it (old ideas are old).

## 5. Panels and judges

For make-or-break systems only (the feel core, the scoring economy — not
every doc). Shape:

- 2–3 designers, **rival lenses** chosen to fight: e.g. the purist
  (source-fantasy authenticity), the modern-craft specialist (named
  techniques, feel ceiling), the systems architect (interfaces,
  mutability, five-epics-later survival). Schema-forced structured
  output: philosophy, per-area design, event taxonomy, constants with
  units, architecture, risks.
- 2 judges with different mandates (the demanding player; the architect
  who must implement and then mutate it) scoring named axes 1–10 with
  harsh notes and explicit **grafts** ("steal X from the loser because…").
- You write the final doc. Name what won, what was rejected and *why*
  (rejections teach future sessions), and rule explicitly on any
  judge-split — "instrument first, legislate on evidence" is often the
  right ruling for speculative degeneracy fears.

## 6. Interface freezing

Before a system has any consumers, publish: an event taxonomy
(facts-only law: events carry facts and physically-grounded
classifications, never judgments a downstream system might re-decide),
an exported SCHEMA_VERSION per vocabulary, additive-only extension
reservations, a consumer contract enumerating who consumes what surface,
and anti-exploit laws ("consumers scale with payload values, never event
counts"). Make every tuning constant runtime-mutable table data with
**owner-tagged layers** (system-scoped pops; canonical application
order), so later systems (upgrades, per-level modifiers, temporary
effects) arrive as data. Validation throws on degenerate values at
layer-push — a config typo fails loud.

## 7. Dual mental playthroughs

- **Author pass**: walk one complete session of the product through every
  doc, boot to finish. Write the trace to `docs/design/` with numbered
  findings and resolutions.
- **Cold-reader pass**: a fresh agent (cheaper model fine — it's reading)
  plays from the docs alone, explicitly firewalled from your trace until
  its own round is written. It logs: **moments** (where design sings),
  **seams** (doc-vs-doc contradictions, cited), **inventions** (anything
  it made up to keep simulating = a doc gap), **exploits** (what its
  inner power-user finds). Then it diffs against your trace.
- Apply rulings as doc amendments with a commit essay. Expect the cold
  reader to find constant-stated-twice bugs, orphaned events nobody
  consumes, and contradictions your own narration stepped in.

## 8. Implementation sessions

One workflow per system: **Build** (one deep agent, full session, binding
doc, "API-level adaptation allowed, architectural deviation forbidden —
document any forced deviation"), **Review** (parallel: design-fidelity
clause-by-clause vs the doc; code-law vs the repo's structural rules — no
god files, engine-free core, listener hygiene, no debug leakage),
**Fix** (mandatory for blockers/majors; the design doc wins arguments),
**Gate** (typecheck/lint/build verbatim). Builders commit essay-style and
never push; you verify and push. Pausing a workflow kills in-flight
agents (completed ones cache) — prefer letting stages finish.

## 9. Instrumented feedback

If the product's core loop can be deterministic, make it so (seeded
forkable RNG streams; fixed timestep; no wall-clock in core), then:
always-on input/flight recorder, a **marker key** the human presses when
something feels off (feedback pre-pinned to the exact moment), one-key
export, and a headless replay CLI over the engine-free core that
regenerates full state around any marker. "It feels mushy" becomes a
frame range you analyze. Contract for all future systems: no new
nondeterminism without extending the recording.

## 10. Cadence and hygiene

- Commit essays: WHY + arc position, never diff summaries. `git log`
  should read as the design narrative.
- Epics/issues per phase; design-doc issues close as docs land.
- Human gates are for feelings (joy, feel, taste); agent gates are for
  facts (types, lint, determinism hashes, tripwire counters that must
  read zero).
- Definition-of-done lives in the ethos and is quoted in briefs; "we
  technically have the code" is the named enemy.
