#!/usr/bin/env python3
"""Stage cumulative judging tasks for the memory-mood skill.

For each cumulative timepoint (1 memory, then 2, ... then all N) writes a
self-contained judging prompt to <work-dir>/tasks/step_NNN.txt. A fresh Sonnet
subagent reads each task and writes its JSON answer to <work-dir>/results/step_NNN.json.

Usage:
  python collect.py --memory-dir DIR --work-dir DIR [--max-timepoints 30]

Stdlib only.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import moodviz  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--memory-dir", required=True, help="Claude memory dir for this session (holds *.md + MEMORY.md)")
    ap.add_argument("--work-dir", required=True, help="scratch dir for tasks/ + results/ + index.html")
    ap.add_argument("--max-timepoints", type=int, default=30,
                    help="cap on judged timepoints; if memories exceed this, sample evenly (default 30)")
    args = ap.parse_args()

    mems = moodviz.collect_memories(args.memory_dir)
    counts = moodviz.select_counts(len(mems), args.max_timepoints)

    work = Path(args.work_dir).expanduser()
    tasks = work / "tasks"
    tasks.mkdir(parents=True, exist_ok=True)
    (work / "results").mkdir(parents=True, exist_ok=True)

    manifest = {"memory_dir": str(Path(args.memory_dir).expanduser()),
                "memories": [{"name": m["name"], "date": m["date"]} for m in mems],
                "timepoints": []}
    for c in counts:
        sub = mems[:c]
        step = f"{c:03d}"
        (tasks / f"step_{step}.txt").write_text(moodviz.build_task_prompt(sub))
        manifest["timepoints"].append({
            "step": step, "n_memories": c,
            "date": sub[-1]["date"], "newest_memory": sub[-1]["name"],
            "task": str(tasks / f"step_{step}.txt"),
            "result": str(work / "results" / f"step_{step}.json"),
        })
    (work / "manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"{len(mems)} memories → {len(counts)} timepoints staged in {tasks}")
    print(f"Each subagent: read tasks/step_NNN.txt, write JSON to results/step_NNN.json")
    print("Steps:", " ".join(t["step"] for t in manifest["timepoints"]))


if __name__ == "__main__":
    main()
