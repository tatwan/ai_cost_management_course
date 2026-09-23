# Lessons — how to run them

Eight notebooks. Run them **top to bottom, in order**. Each code cell has a short explanation before it, and the important ones have a note after them on how to read the output. They're committed with outputs from a real run, so you can read ahead before you have a key.

If you landed here from the course repo, start at the [root README](../README.md) for the argument and the lesson table, then come back here for setup.

| # | File | Key needed? | ~Time |
|---|------|-------------|-------|
| 1 | `01_token_economics.ipynb` | Optional (last section only) | 10 min |
| 2 | `02_prompt_caching.ipynb` | Yes | 10 min |
| 3 | `03_context_compression.ipynb` | Yes (eval cells; compression runs offline) | 10 min |
| 4 | `04_rag_cost.ipynb` | Yes (k sweep; chunking and retrieval run offline) | 12 min |
| 5 | `05_semantic_cache.ipynb` | Yes (traffic cell; false-hit and tenant demos run offline) | 10 min |
| 6 | `06_routing_cascade.ipynb` | Yes | 15 min |
| 7 | `07_finops_telemetry.ipynb` | Yes (cheapest tier, well under a cent) | 12 min |
| 8 | `08_litellm_gateway.ipynb` | Yes; Ollama optional | 15 min |

## Setup

From the **repo root** (not this folder):

```bash
uv sync
cp .env.example .env
```

Put **one** key in `.env`:

```
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
```

If both are set, Anthropic is used (its cache read/write buckets are easier to read on screen). Force a vendor with `LLM_PROVIDER=openai`.

```bash
uv run jupyter lab notebooks/
```

The first code cell of every notebook prints which provider and which three model tiers it will call. Re-run that cell after changing `.env`.

Budget about **$2–5** to work through all eight once on the mid tier. Lessons 7 and 8 cost well under a cent each.

## How to read a lesson

Each lesson opens with a line giving its module, rough time, and whether it needs a key, followed by some background. After that it alternates: a paragraph on what the next cell does, the cell, then (for the ones that matter) a short note on how to read what came out. The notes describe what to look for, not exact values, because your numbers will differ from the committed run.

| Section | What it's for |
|---|---|
| **In class** notes | Cues for when we run the lesson together. On your own, stop and think about the question. |
| **What to take away** | The few points worth remembering from the lesson |
| **Check yourself** | Short questions. The answers are folded, so try them first. |
| **Try it on your own work** | A small exercise to repeat the lesson on your own prompts, traffic, or bill |

A **cost ledger** prints at the end of every notebook that spends money.

## Model ids

Defaults, overridable in `.env`:

| Tier | Anthropic | OpenAI |
|------|-----------|--------|
| floor | `claude-haiku-4-5` | `gpt-5.6-luna` |
| mid | `claude-sonnet-5` | `gpt-5.6-terra` |
| frontier | `claude-opus-5` | `gpt-5.6-sol` |

```
MODEL_FLOOR=...
MODEL_MID=...
MODEL_FRONTIER=...
```

Lessons 6 and 8 use all three tiers. If your key can only call one model, set all three variables to it. The cost-per-solved-task arithmetic still works; you just won't see a price gap between tiers.

## If a live call fails

`complete()` catches 401 / 429 / unknown-model errors and returns a placeholder labelled as such, so the rest of the notebook still runs. Placeholders are never counted as money spent in the ledger, and the lessons don't print a conclusion from placeholder answers. If you'd rather it stop on the error, set `DEMO_STRICT=1` in `.env`.

Error messages show the error type and status code only. Some providers echo part of your key in the full message, so it isn't printed.

Lesson 3's LLMLingua cell is optional and **not** installed by default. You can skip it: the lesson is the checklist and the eval. To run it, `uv sync --extra compress` the night before, since the first run downloads a model of about 2 GB.

Lesson 8's local-model section looks for Ollama at its default address and skips itself if it isn't running. The committed run used `qwen2.5:0.5b`.
