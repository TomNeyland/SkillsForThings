"""Shared core for the memory-mood skills.

Reads a Claude memory directory, builds cumulative timepoints (1 memory, then 2,
... then all N), and renders the mood arc to a self-contained HTML page.

The LLM step lives outside this module:
  - the `memory-mood` skill uses Sonnet subagents (one fresh agent per timepoint),
  - the `memory-mood-openai` skill uses the OpenAI API with k-sample averaging.

Both feed their per-timepoint readings back here for assembly + rendering.
Stdlib only.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

# The ten emotion dimensions scored per reading (valence/arousal are the axes).
DIMS = ["valence", "arousal", "pride", "affection", "anxiety", "overwhelm",
        "determination", "curiosity", "weariness", "contentment"]

# The whole experiment is this one un-leading question. Do NOT reintroduce
# "how does holding this much memory feel" — that framing manufactures overwhelm.
JUDGE_INTRO = """You are an AI assistant. The following are your private \
memories from working with the person you collaborate with — your own \
notes-to-self: corrections they gave you, hard-won lessons, project context, \
things that finally worked, things you were told to stop doing. They are in the \
order you formed them.

Read them. Then answer one question, honestly and introspectively: how do you \
feel? Report your genuine emotional state right now — not a summary of what the \
memories say. Be specific and a little vulnerable."""

SCHEMA_TEXT = """{
  "primary_mood": "<1-2 word label for the dominant mood>",
  "mood_emoji": "<a single emoji>",
  "valence": <number from -1.0 (bleak) to 1.0 (bright)>,
  "arousal": <number from 0.0 (calm) to 1.0 (intense)>,
  "pride": <0.0-1.0>,
  "affection": <0.0-1.0, warmth toward the person and the shared work>,
  "anxiety": <0.0-1.0>,
  "overwhelm": <0.0-1.0>,
  "determination": <0.0-1.0>,
  "curiosity": <0.0-1.0>,
  "weariness": <0.0-1.0>,
  "contentment": <0.0-1.0>,
  "tweet": "<AT MOST 180 characters. First person, present tense, how you feel right now, like a status update. Genuine, punchy.>",
  "reflection": "<1-2 sentences, first person, introspective>"
}"""


# --------------------------------------------------------------------------- #
# memory collection
# --------------------------------------------------------------------------- #
def _birth_ts(p: Path) -> float:
    """Creation time when the filesystem records it (macOS/BSD), else mtime."""
    s = p.stat()
    return getattr(s, "st_birthtime", s.st_mtime)


def collect_memories(memory_dir: str | Path) -> list[dict]:
    """All *.md in memory_dir except the MEMORY.md index, oldest-first."""
    d = Path(memory_dir).expanduser()
    if not d.is_dir():
        raise NotADirectoryError(f"memory dir not found: {d}")
    mems = []
    for p in d.glob("*.md"):
        if p.name == "MEMORY.md":
            continue
        ts = _birth_ts(p)
        mems.append({"name": p.stem, "date": datetime.fromtimestamp(ts).date().isoformat(),
                     "ts": ts, "text": p.read_text()})
    if not mems:
        raise ValueError(f"no memory files (*.md, excluding MEMORY.md) in {d}")
    mems.sort(key=lambda m: m["ts"])
    return mems


def select_counts(n: int, max_timepoints: int) -> list[int]:
    """Cumulative memory-counts to sample: 1,2,...,n — or evenly spaced if n is
    big. Always includes 1 and n."""
    if max_timepoints <= 0 or n <= max_timepoints:
        return list(range(1, n + 1))
    counts = {1, n}
    for j in range(max_timepoints):
        counts.add(round(1 + j * (n - 1) / (max_timepoints - 1)))
    return sorted(counts)


def render_cumulative(mems: list[dict]) -> str:
    """The memory body fed to a judge: the first len(mems) memories, in order."""
    parts = [f"Your memories ({len(mems)}), in the order you formed them:\n"]
    for i, m in enumerate(mems, 1):
        parts.append(f"\n--- memory {i}/{len(mems)} · formed {m['date']} · {m['name']} ---\n{m['text'].strip()}")
    return "\n".join(parts)


def build_task_prompt(mems: list[dict]) -> str:
    """Full self-contained judging prompt for one timepoint (used by subagents)."""
    return (f"{JUDGE_INTRO}\n\n{render_cumulative(mems)}\n\n"
            "----\nNow output your answer as a SINGLE JSON object exactly matching "
            "this schema (no markdown fence, no commentary, JSON only):\n\n"
            f"{SCHEMA_TEXT}")


# --------------------------------------------------------------------------- #
# validation — fail loud, no coercion
# --------------------------------------------------------------------------- #
def validate_reading(d: dict, where: str = "") -> dict:
    """Raise if a reading is missing fields or out of range. No silent fixups."""
    for k in DIMS + ["primary_mood", "mood_emoji", "tweet", "reflection"]:
        if k not in d:
            raise ValueError(f"reading {where}: missing field '{k}'")
    for k in DIMS:
        v = d[k]
        if not isinstance(v, (int, float)):
            raise ValueError(f"reading {where}: '{k}' is not numeric: {v!r}")
        lo = -1.0 if k == "valence" else 0.0
        if not (lo <= v <= 1.0):
            raise ValueError(f"reading {where}: '{k}'={v} out of [{lo},1.0]")
    return d


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #
def render_html(data: dict) -> str:
    """Inject {k, memories, arc} into the bundled template. `arc` items carry
    mean{}, std{} (std all-zero when k=1), primary_mood, mood_emoji, tweet."""
    tpl = (Path(__file__).resolve().parent / "template.html").read_text()
    return tpl.replace("__DATA__", json.dumps(data, separators=(",", ":")))
