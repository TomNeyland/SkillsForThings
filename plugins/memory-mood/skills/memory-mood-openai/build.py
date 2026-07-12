#!/usr/bin/env python3
"""memory-mood, OpenAI edition: k independent samples per cumulative timepoint,
averaged, with ±1σ bands. Preserves the original high-fidelity version.

Asks gpt-5.4-nano (configurable) "how do you feel?" after each memory, K times,
averages the 10 emotion dimensions, surfaces the tweet whose full mood vector sits
closest to that average, and renders the shared HTML.

Run with uv (zero install):
  uv run --with openai --with pydantic python build.py \
      --memory-dir <DIR> --work-dir <DIR> [--k 8] [--model gpt-5.4-nano] [--max-timepoints 0]

Needs OPENAI_API_KEY in the environment. --max-timepoints 0 = every memory.
"""
import argparse
import asyncio
import statistics as st
import sys
from pathlib import Path

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import moodviz  # noqa: E402


class MoodReading(BaseModel):
    primary_mood: str = Field(description="1-2 word label for the dominant mood")
    mood_emoji: str = Field(description="a single emoji")
    valence: float = Field(ge=-1, le=1, description="-1 bleak .. +1 bright")
    arousal: float = Field(ge=0, le=1, description="0 calm .. 1 intense")
    pride: float = Field(ge=0, le=1)
    affection: float = Field(ge=0, le=1, description="warmth toward the person and the shared work")
    anxiety: float = Field(ge=0, le=1)
    overwhelm: float = Field(ge=0, le=1)
    determination: float = Field(ge=0, le=1)
    curiosity: float = Field(ge=0, le=1)
    weariness: float = Field(ge=0, le=1)
    contentment: float = Field(ge=0, le=1)
    tweet: str = Field(description="AT MOST 180 characters. First person, present tense, like a status update.")
    reflection: str = Field(description="1-2 sentences, first person, introspective")


async def _sample(client, sem, model, user) -> MoodReading:
    async with sem:
        resp = await client.responses.parse(
            model=model,
            input=[{"role": "system", "content": moodviz.JUDGE_INTRO},
                   {"role": "user", "content": user}],
            text_format=MoodReading,
        )
        return resp.output_parsed


async def run(args) -> None:
    mems = moodviz.collect_memories(args.memory_dir)
    counts = moodviz.select_counts(len(mems), args.max_timepoints)
    print(f"{len(mems)} memories → {len(counts)} timepoints × {args.k} samples = {len(counts) * args.k} calls")

    client = AsyncOpenAI()
    sem = asyncio.Semaphore(args.concurrency)
    prompts = [moodviz.render_cumulative(mems[:c]) for c in counts]
    flat = await asyncio.gather(*[_sample(client, sem, args.model, prompts[i])
                                  for i in range(len(counts)) for _ in range(args.k)])

    arc = []
    for i, c in enumerate(counts):
        samples = flat[i * args.k:(i + 1) * args.k]
        mean = {d: st.mean(getattr(s, d) for s in samples) for d in moodviz.DIMS}
        std = {d: (st.pstdev(getattr(s, d) for s in samples) if args.k > 1 else 0.0) for d in moodviz.DIMS}
        rep = min(samples, key=lambda s: sum((getattr(s, d) - mean[d]) ** 2 for d in moodviz.DIMS) ** 0.5)
        sub = mems[:c]
        arc.append({"step": c, "n_memories": c, "date": sub[-1]["date"], "newest_memory": sub[-1]["name"],
                    "mean": mean, "std": std,
                    "primary_mood": rep.primary_mood, "mood_emoji": rep.mood_emoji, "tweet": rep.tweet})

    data = {"k": args.k, "memories": [{"name": m["name"], "date": m["date"]} for m in mems], "arc": arc}
    out = Path(args.work_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(moodviz.render_html(data))
    print(f"Wrote {out / 'index.html'} ({len(arc)} timepoints, k={args.k})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--memory-dir", required=True)
    ap.add_argument("--work-dir", required=True)
    ap.add_argument("--k", type=int, default=8, help="samples per timepoint to average (default 8)")
    ap.add_argument("--model", default="gpt-5.4-nano")
    ap.add_argument("--max-timepoints", type=int, default=0, help="0 = every memory; else sample evenly")
    ap.add_argument("--concurrency", type=int, default=60, help="max in-flight API calls")
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
