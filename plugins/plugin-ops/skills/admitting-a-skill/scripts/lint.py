#!/usr/bin/env python3
"""Mechanical pre-flight checks for a skill before it goes public.

Deterministic only — the judgment call (origin leaks, quality, redundancy) is a
separate dual-model critic pass. This script exists to catch what a human/agent
reading skims past: a stray absolute path, a missing frontmatter field, a
cross-reference to a skill that doesn't exist, a body that's 3x over budget.

Usage:
    python3 lint.py <marketplace-root>              # every SKILL.md in the repo
    python3 lint.py <marketplace-root> --skill NAME  # just one skill by dir name
"""
import argparse
import pathlib
import re
import sys

WORD_BUDGET_SOFT = 700
WORD_BUDGET_HARD = 1100

# Real local paths, not the documented generic placeholder.
PATH_RE = re.compile(r"/(Users|home)/[A-Za-z0-9_.-]+")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
DESC_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)
# A `backtick-name` that looks like a skill reference (kebab-case, 2+ words).
SKILL_REF_RE = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+){1,})`")
INTERNAL_ARTIFACT_RE = re.compile(
    r"\b(HANDOVER|worktree|scratchpad|session_[a-f0-9]{6,})\b", re.IGNORECASE
)
ISSUE_REF_RE = re.compile(r"#\d{2,}")


def find_skills(root: pathlib.Path):
    return sorted(root.glob("plugins/*/skills/*/SKILL.md"))


def all_skill_names(root: pathlib.Path) -> set[str]:
    names = {p.parent.name for p in find_skills(root)}
    # Agents are a valid cross-reference target too (`conducting` names its
    # delegatable subagents by filename stem).
    names |= {p.stem for p in root.glob("plugins/*/agents/*.md")}
    return names


def lint_one(path: pathlib.Path, known_skills: set[str]) -> list[tuple[str, str]]:
    """Returns list of (severity, message). severity is FAIL or WARN."""
    findings = []
    text = path.read_text()
    dir_name = path.parent.name

    m = FRONTMATTER_RE.match(text)
    if not m:
        findings.append(("FAIL", "missing or malformed frontmatter block"))
        return findings
    frontmatter, body = m.group(1), text[m.end():]

    name_m = NAME_RE.search(frontmatter)
    if not name_m:
        findings.append(("FAIL", "frontmatter missing `name`"))
    elif name_m.group(1).strip() != dir_name:
        findings.append(
            ("FAIL", f"frontmatter name `{name_m.group(1).strip()}` != directory `{dir_name}`")
        )

    desc_m = DESC_RE.search(frontmatter)
    if not desc_m or not desc_m.group(1).strip():
        findings.append(("FAIL", "frontmatter missing or empty `description`"))

    for m in PATH_RE.finditer(text):
        findings.append(("FAIL", f"real local filesystem path: `{m.group(0)}`"))

    for m in ISSUE_REF_RE.finditer(text):
        findings.append(("WARN", f"issue-ref-shaped token `{m.group(0)}` — confirm it's a public reference, not a private tracker"))

    for m in INTERNAL_ARTIFACT_RE.finditer(text):
        findings.append(("WARN", f"internal-artifact-shaped token `{m.group(0)}` — verify it's not a session/build artifact"))

    word_count = len(body.split())
    if word_count > WORD_BUDGET_HARD:
        findings.append(("WARN", f"body is {word_count} words (hard budget {WORD_BUDGET_HARD}) — move detail to references/"))
    elif word_count > WORD_BUDGET_SOFT:
        findings.append(("WARN", f"body is {word_count} words (soft budget {WORD_BUDGET_SOFT})"))

    for m in SKILL_REF_RE.finditer(body):
        ref = m.group(1)
        if ref == dir_name:
            continue
        if ref not in known_skills and not (path.parent / ref).exists():
            findings.append(("WARN", f"cross-reference `{ref}` doesn't match any skill in the marketplace — dangling or a false positive (e.g. a code identifier)"))

    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=pathlib.Path)
    ap.add_argument("--skill", help="lint only this skill (directory name)")
    args = ap.parse_args()

    root = args.root.resolve()
    skills = find_skills(root)
    if args.skill:
        skills = [p for p in skills if p.parent.name == args.skill]
        if not skills:
            print(f"no skill named {args.skill!r} under {root}", file=sys.stderr)
            sys.exit(2)

    known = all_skill_names(root)
    any_fail = False
    for path in skills:
        findings = lint_one(path, known)
        rel = path.relative_to(root)
        if not findings:
            print(f"CLEAN  {rel}")
            continue
        for severity, msg in findings:
            print(f"{severity:5s}  {rel}: {msg}")
            if severity == "FAIL":
                any_fail = True

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
