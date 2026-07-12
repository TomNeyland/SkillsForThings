---
name: memory-mood-openai
description: Use when someone wants a high-fidelity mood visualization of their AI assistant's accumulating memories using the OpenAI API — averaged emotional arc with confidence bands, many samples per timepoint. Triggers on "memory mood with openai", "averaged mood arc", "mood of my memories with confidence bands", "high fidelity memory feelings". Requires OPENAI_API_KEY.
---

# Memory Mood (OpenAI edition)

Same idea as the `memory-mood` skill — replay your assistant's memory files in formation order and ask *how do you feel?* after each — but judged by the **OpenAI API with k independent samples per timepoint, averaged**. A single reading wobbles by ~±0.1; averaging k of them (default 8) collapses the noise and lets the page draw **±1σ confidence bands**. Use this when you want the smooth, defensible version and have an API key. Otherwise use the dependency-free `memory-mood` (Sonnet subagent) skill.

## Why averaging

Adjacent timepoints differ by exactly one memory, so a real mood signal should move slowly. A single LLM draw swings far more than that — that swing is sampling noise, not signal. Drawing **k samples and averaging** separates the two; the shaded band shows how much one call would have wobbled.

## Independence

Every call is a clean read of the memory set alone — calls never see each other or their own prior answers. The only shared context is the growing memory. Do not thread prior answers forward; that reintroduces self-priming and breaks the average.

## Workflow

`$DIR` is this skill's directory. `$WORK` is any scratch dir.

**1 — Find the memory directory** for this session (where your `MEMORY.md` + `*.md` files live, typically `~/.claude/projects/<project>/memory/`).

**2 — Build it** (uv handles deps with no install; needs `OPENAI_API_KEY` set):
```bash
uv run --with openai --with pydantic python "$DIR/build.py" \
    --memory-dir <memory-dir> --work-dir "$WORK" --k 8 --model gpt-5.4-nano
open "$WORK/index.html"   # macOS; xdg-open on Linux
```
No uv? `pip install openai pydantic` then `python "$DIR/build.py" ...`.

**3 — Read the page.** Emotions chart (mean lines + ±1σ ribbons) is the hero; the timestamped tweet feed follows. Each surfaced tweet is the one sample, of k, whose full mood vector sat closest to that timepoint's average.

## Knobs

| Flag | Default | Effect |
|---|---|---|
| `--k` | 8 | samples per timepoint to average; higher = tighter bands, more cost |
| `--max-timepoints` | 0 (every memory) | cap timepoints; samples evenly if memories exceed it |
| `--model` | `gpt-5.4-nano` | any responses-API model with structured output |
| `--concurrency` | 60 | max in-flight calls |

## Cost

Cost scales with timepoints × k and grows as the cumulative prompt lengthens. Order-of-magnitude: ~$0.003/call on a nano-class model — e.g. 80 memories × k=8 ≈ 640 calls ≈ a couple dollars. Drop `--k` or set `--max-timepoints` to spend less.

## Common mistakes

- **Threading prior answers** into later calls — breaks independence and the average. Each call is standalone.
- **Re-asking "how does holding this much memory feel"** — that framing manufactures overwhelm. The neutral "how do you feel?" is deliberate (see `lib/moodviz.py` `JUDGE_INTRO`).
- **k=1** — defeats the point of this edition; use the `memory-mood` skill instead.
