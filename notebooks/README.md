# Lessons — how to run them

Seven notebooks. Run them **top to bottom, in order**. Each section tells you what is about to happen, what number to watch, and why it matters *before* you execute the cell.

If you landed here from the course repo, start at the [root README](../README.md) for the argument and the lesson table, then come back here for setup.

| # | File | Key needed? | ~Time |
|---|------|-------------|-------|
| 1 | `01_token_economics.ipynb` | Optional (last cell only) | 8 min |
| 2 | `02_prompt_caching.ipynb` | Yes | 8 min |
| 3 | `03_context_compression.ipynb` | Yes (eval cells) | 10 min |
| 4 | `04_rag_cost.ipynb` | Yes (k-sweep) | 12 min |
| 5 | `05_semantic_cache.ipynb` | Yes (traffic cell) | 8 min |
| 6 | `06_routing_cascade.ipynb` | Yes | 15 min |
| 7 | `07_finops_telemetry.ipynb` | Yes | 12 min |

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

Budget about **$2–5** to work through all seven once on the mid tier. Lesson 7 uses the cheap tier on purpose.

## How to read a lesson

| Marker in the notebook | Meaning |
|---|---|
| **About to happen** | What the next cell will do |
| **Watch for** | The number or field that makes the point — pause on it |
| **Why it matters** | The Monday-morning decision this should change |
| **Presenting:** | Live-demo cue. Studying solo? That is the takeaway. |
| **Try on Monday** | A small action at the end of each lesson |

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

Lesson 6 needs three tiers. If your key can only call one model, set all three variables to it — the cost-per-solved-task reframe still works.

## If a live call fails

`complete()` catches 401 / 429 / unknown-model errors and continues with a rehearsal result so the argument still reads. Set `DEMO_STRICT=1` in `.env` if you would rather it raise.

Lesson 3's LLMLingua cell is optional and **not** installed by default. Skip it; the five-point checklist plus the eval set is the lesson. Night-before only: `uv sync --extra compress`.
