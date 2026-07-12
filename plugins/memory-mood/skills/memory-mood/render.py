#!/usr/bin/env python3
"""Assemble subagent mood readings into the memory-mood visualization.

Reads <work-dir>/manifest.json + <work-dir>/results/step_NNN.json (one per
timepoint, written by the judging subagents) and renders <work-dir>/index.html.

Single reading per timepoint (k=1) → no ±1σ bands. Fails loud on any missing
or malformed result; no silent skipping.

Usage:
  python render.py --work-dir DIR

Stdlib only.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import moodviz  # noqa: E402


def _load_result(path: Path, step: str) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"missing result for step {step}: {path} "
                                "(did every judging subagent finish and write its JSON?)")
    raw = path.read_text().strip()
    # tolerate a ```json fence if a subagent added one
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return moodviz.validate_reading(json.loads(raw), where=f"step {step}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-dir", required=True)
    args = ap.parse_args()
    work = Path(args.work_dir).expanduser()

    manifest = json.loads((work / "manifest.json").read_text())
    arc = []
    for tp in manifest["timepoints"]:
        r = _load_result(Path(tp["result"]), tp["step"])
        arc.append({
            "step": int(tp["step"]), "n_memories": tp["n_memories"],
            "date": tp["date"], "newest_memory": tp["newest_memory"],
            "mean": {d: float(r[d]) for d in moodviz.DIMS},
            "std": {d: 0.0 for d in moodviz.DIMS},
            "primary_mood": r["primary_mood"], "mood_emoji": r["mood_emoji"],
            "tweet": r["tweet"],
        })
    arc.sort(key=lambda a: a["step"])

    data = {"k": 1, "memories": manifest["memories"], "arc": arc}
    out = work / "index.html"
    out.write_text(moodviz.render_html(data))
    print(f"Wrote {out} ({len(arc)} timepoints, k=1)")


if __name__ == "__main__":
    main()
