# Current State

> **Purpose:** the fastest way for a human *or* an agent to answer "where does this
> project actually stand right now?" without reading the git log or re-deriving it
> from the code. Read this file **first**, before `log.md` — `log.md` tells you how
> we got here, this file tells you where "here" is.
>
> **Rule of thumb:** this file describes *the present*. If a sentence starts with
> "we used to..." or "next we will...", it belongs in `log.md` or `next_steps.md`
> instead. Keep this file overwritten in place — don't append to it.

_Last updated: 2026-09-10_

## One-line summary

Seven runnable notebooks teaching LLM cost management are built and passing tests;
labs were just run successfully and the repo is in a stable, teachable state.

## What's working

- All 7 lessons (`notebooks/01_token_economics.ipynb` → `07_finops_telemetry.ipynb`)
  build cleanly from `build_notebooks.py` and run top to bottom.
- `coursekit.py` (shared helper: `boot()`, `complete()`, `cost()`, `ledger()`) has
  a verified rate card (`PRICES`) and a `.env`-driven provider switch
  (Anthropic default, OpenAI via `LLM_PROVIDER=openai`).
- `tests/test_coursekit.py` covers the cost-accounting arithmetic and the
  Anthropic-vs-OpenAI cache-bucket normalization — the two bugs most likely to
  embarrass a live demo. Run with `uv run pytest`.
- Course materials (slides, instructor guide, quiz, feedback notes) live under
  `AI Cost Management/` and are up to date with the notebooks.

## Known gaps / rough edges

- Rate-card prices in `coursekit.py` are "verified 5 September 2026" — they will
  drift. Re-check provider pricing pages before each cohort.
- Lesson 3's LLMLingua compression cell is optional and not installed by default
  (`uv sync --extra compress` the night before if you plan to run it live).
- `.env` currently holds a real key locally (gitignored) — fine for solo dev, but
  remind students never to commit `.env`, only `.env.example`.

## Environment / how to get this running

```bash
uv sync
cp .env.example .env      # add OPENAI_API_KEY or ANTHROPIC_API_KEY
uv run pytest              # sanity-check the cost math before touching notebooks
uv run jupyter lab notebooks/
```

## Where to look next

See [`next_steps.md`](next_steps.md) for the open backlog and
[`decisions.md`](decisions.md) for why the repo is shaped the way it is.
