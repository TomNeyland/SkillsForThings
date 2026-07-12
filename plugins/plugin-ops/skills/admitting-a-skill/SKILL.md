---
name: admitting-a-skill
description: Use before a new or edited skill enters a public marketplace — especially one ported, distilled, or genericized from a private codebase or internal playbook. Triggers on "is this ready to publish", "check this skill for leaks", "prep this for the public repo", "genericize this skill", or after porting a skill from a private project.
---

# Admitting a Skill

![A clean grep can still miss a private project leak. Run deterministic machine checks, give the complete reusable AI instruction package to two independent readers, keep every concrete issue either reader finds, and repeat after substantive fixes until all three checks are clean.](assets/admitting-a-skill.png)

A skill written inside a private project absorbs that project's vocabulary, catchphrases, and
examples without anyone deciding to put them there — the author is fluent in the origin and doesn't
notice it leaking through. Publishing is the one-way door: once a leak ships, it's public forever.
Two gates, always both, in this order.

## Gate 1 — mechanical lint (fast, deterministic)

```bash
python3 scripts/lint.py <marketplace-root>                  # every skill
python3 scripts/lint.py <marketplace-root> --skill <name>    # one skill
```

Catches: missing/malformed frontmatter, a `name` that doesn't match its directory, a real local
filesystem path (`/Users/…`, `/home/…`), a body far over the word budget (SKILL.md stays under ~700
words; heavy material goes in `references/`), and a `` `<some-skill>` `` cross-reference that
doesn't resolve to any skill in the marketplace. `FAIL` blocks; `WARN` needs a human/agent glance —
issue-ref-shaped and internal-artifact-shaped tokens are common false positives (a skill *about*
GitHub workflows will legitimately say `#123`), so don't auto-reject on `WARN`.

This step is cheap and catches nothing subtle — it exists so the judgment pass isn't spent on typos.

## Gate 2 — dual-model critic (judgment)

Grep-based scanning misses the leaks that matter most: a coined phrase reused from elsewhere, an
example arc that only makes sense for one real product, device narration with no keyword to search
for. Dispatch **two independent reviewers, the verbatim same prompt**, each using the
`skill-admission-critic` subagent (this plugin's `agents/skill-admission-critic.md`) — a stronger
model plus a cheaper one, or two runs of one. Point each at the exact file set changed or added; for
a whole-plugin admission, the entire plugin directory. The model disagreement is signal: what one
flags and the other clears is exactly where a second look pays off.

**Reconcile the union**, not the intersection — a finding either reviewer raises is real until
checked, not dismissed because only one saw it. Verify each finding against the actual source you
have access to before acting (a name may be a legitimate public citation, not a leak — see the
critic's own "do NOT flag" list); don't accept a claim of provenance ("this looks copied from X")
without confirming it against a real X you can read. Apply fixes, then **re-run both critics** on
whatever changed if any finding was leak-severity or the fix was substantive — loop until clean.

## When both gates are clean

The skill is admitted. `FAIL`-free lint + a `SHIP-CLEAN` verdict (or all findings resolved) from both
critics is the bar — not "looks fine on a skim." A verified-clean report is the expected outcome for
most skills, not a rare pass; don't manufacture findings to look thorough.

## Common mistakes

| Mistake | Reality |
|---|---|
| Grep for known bad words and call it swept | The worst leaks share no keyword — a real reader end-to-end is what catches them |
| Scrub every real person's name as a precaution | A named public source is what makes a claim verifiable; only the author's own private catchphrase is a leak |
| Run only one critic | One model's blind spot is the other's catch — that's the whole point of the pair |
| Treat the mechanical lint as sufficient | It catches typos and paths, not "this arc only makes sense for one real product" |
| Skip re-review after a substantive fix | A fix can introduce a new leak (an "invented" replacement that's still specific to the origin) |

## Composes with

The dual-model mechanism itself: `fan-and-critic` (conductor plugin). For refreshing a skill's
*content* against current evidence (a different problem — staleness, not origin leaks): `refresh-skill`.
