---
name: memory-mood-openai
description: Use when someone wants a high-fidelity mood visualization of their AI assistant's accumulating memories using the OpenAI API — an averaged emotional arc with call-to-call spread, using many independent samples per timepoint. Triggers on "memory mood with openai", "averaged mood arc", "mood of my memories with sampling spread", "high fidelity memory feelings". Requires OPENAI_API_KEY.
---

# Memory Mood (OpenAI edition)

Same idea as the `memory-mood` skill — replay cumulative snapshots of your assistant's memory files
in formation order and ask *how do you feel?* — but judged by the **OpenAI API with k independent
samples per timepoint, averaged**. Averaging k readings reduces the influence of any one draw on the
mean. The page also draws a **±1σ spread band** from the individual readings; this is call-to-call
spread, not a confidence interval for the mean. Use this edition when you want an averaged curve and
have an API key. Otherwise use the dependency-free `memory-mood` (Sonnet subagent) skill.

## Why averaging

Adjacent staged timepoints differ only by the memories added since the previous selected snapshot.
A single LLM draw can move even when the memory text does not. Drawing **k independent samples and
averaging** reduces that single-draw influence; the shaded ±1σ band shows the spread of the individual
calls around their mean.

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
| `--k` | 8 | samples per timepoint; higher = a more stable estimate of the mean and spread, more cost |
| `--max-timepoints` | 0 (every memory) | cap timepoints; samples evenly if memories exceed it |
| `--model` | `gpt-5.4-nano` | any responses-API model with structured output |
| `--concurrency` | 60 | max in-flight calls |

## Cost

Cost scales with timepoints × k and grows as the cumulative prompt lengthens. Order-of-magnitude: ~$0.003/call on a nano-class model — e.g. 80 memories × k=8 ≈ 640 calls ≈ a couple dollars. Drop `--k` or set `--max-timepoints` to spend less.

## Common mistakes

- **Threading prior answers** into later calls — breaks independence and the average. Each call is standalone.
- **Re-asking "how does holding this much memory feel"** — that framing manufactures overwhelm. The neutral "how do you feel?" is deliberate (see `lib/moodviz.py` `JUDGE_INTRO`).
- **k=1** — defeats the point of this edition; use the `memory-mood` skill instead.
