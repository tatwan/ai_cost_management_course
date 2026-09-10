# AGENTS.md

> **What this file is:** `AGENTS.md` is a plain-Markdown convention (used by
> Claude Code, Cursor, Codex, and other AI coding tools) for briefing an AI
> agent on a repo — the same way a `README.md` briefs a human. It sits at the
> repo root, and a good agent reads it before touching anything.
>
> **This particular copy does double duty:** it's the real instructions for
> this course repo, *and* a worked template. If you're a student building your
> own project, copy this file, gut the "Project overview" section, and keep the
> shape — especially the **`progress/` tracking system** below, which is the
> part most worth stealing.

---

## Project overview

This is the repo for **"AI Cost Management and Token Utilization"** — a
4-hour masterclass plus seven runnable Jupyter notebooks teaching how LLM
inference is billed and how to control the bill. It is vendor-neutral: the
notebooks run against either OpenAI or Anthropic depending on which API key is
present in `.env`.

Full argument and lesson table: [`README.md`](README.md). Setup and
troubleshooting for the notebooks specifically: [`notebooks/README.md`](notebooks/README.md).

## Repo map

| Path | What it is |
|---|---|
| `notebooks/01_*.ipynb` … `07_*.ipynb` | The seven lessons. **Generated files — see below.** |
| `notebooks/coursekit.py` | Shared helper module: `boot()`, `complete()`, `cost()`, `ledger()`, the `PRICES` rate card. Source of truth for all cost math. |
| `notebooks/README.md` | Student-facing setup + "how to read a lesson" reference. |
| `build_notebooks.py` | Generates every `notebooks/*.ipynb` from Python. **Edit this, not the notebooks.** |
| `tests/test_coursekit.py` | Pytest suite for the cost-accounting arithmetic and OpenAI/Anthropic cache-bucket normalization. |
| `AI Cost Management/` | Slide decks, instructor guide, quiz, feedback notes — the classroom-facing materials. |
| `.env.example` | Template for local secrets. `.env` itself is gitignored — never commit it. |
| `progress/` | Session-to-session memory for this project. See the mapping below. |

## Working conventions

- **Package manager is `uv`.** Setup is `uv sync`; run anything with
  `uv run <cmd>` (e.g. `uv run pytest`, `uv run jupyter lab notebooks/`).
- **Notebooks are build artifacts, not source.** Never hand-edit a
  `notebooks/*.ipynb` file's cells directly and expect the change to stick —
  edit `build_notebooks.py` (structure/content) or `notebooks/coursekit.py`
  (shared helpers, pricing), then regenerate:
  ```bash
  uv run python build_notebooks.py
  ```
- **Run the tests before claiming cost-math changes work.** `uv run pytest`
  covers the two bugs most likely to embarrass a live demo: OpenAI counting
  cached tokens *inside* `prompt_tokens` vs. Anthropic reporting cache
  read/write in separate buckets. If you touch `coursekit.py`'s pricing or
  usage-normalization logic, this suite must pass.
- **Secrets never get committed.** Only `.env.example` is tracked; `.env`
  holds the real key and is gitignored.
- **Rate-card prices decay.** `coursekit.PRICES` is dated in a comment at the
  top of the file — re-check it against provider pricing pages rather than
  trusting it's current. See `progress/current_state.md` for the last-checked
  date.

## The `progress/` tracking system

The single biggest failure mode in multi-session AI-assisted work is context
loss: a new session (or a human returning after a week) has to re-derive
"what's going on here?" from scratch — usually by re-reading the whole repo or
the whole git log. `progress/` exists to make that answerable in 30 seconds
instead.

**Read order when starting a session:** `current_state.md` → `next_steps.md`
→ the top few entries of `log.md`. Read `decisions.md` only when you're about
to change something that might have been deliberate.

| File | What it holds | Read it when… | Update it when… |
|---|---|---|---|
| [`progress/current_state.md`](progress/current_state.md) | A **snapshot** (overwritten in place, not appended) of what's working, what's rough, and how to get the project running right now. | You're starting a session and need "where do things stand?" in one read. | Something changes that would make the existing snapshot wrong or stale. |
| [`progress/log.md`](progress/log.md) | An append-only **timeline**, newest entry on top: what happened, when, and *why* — not just what the diff already shows. | You need history: "why does this exist / what did the last session actually do?" | At the end of any session that changed something worth remembering. |
| [`progress/decisions.md`](progress/decisions.md) | Short, non-obvious **"why is it built this way"** records — decisions with a real rejected alternative. | Before changing something that looks like it could be a mistake but might be deliberate. | You make a choice a future session (or teammate) would otherwise re-litigate or "fix" by accident. |
| [`progress/next_steps.md`](progress/next_steps.md) | The open **backlog**, roughly prioritized. | You're picking up work and want to know what's next. | You think of something worth doing but aren't doing it now; check items off and move them to `log.md` once done. |

The rule that keeps this system from rotting: **`current_state.md` describes
the present tense only.** If a sentence wants to start with "we used to..." it
belongs in `log.md`; if it wants to start with "next we should..." it belongs
in `next_steps.md`. Keeping that boundary is what makes `current_state.md`
trustworthy to skim instead of something people stop updating.

## For students copying this template

1. Keep the four `progress/` files and their division of labor — it's small
   enough to maintain by hand and covers the questions that actually cause
   re-work: *where are we, what happened, why is it like this, what's next.*
2. Trim the "Repo map" and "Working conventions" sections down to your own
   project's real structure and commands — don't leave this course's notebook
   details in your copy.
3. Populate `progress/current_state.md` and one `progress/log.md` entry as
   soon as you start, even before there's much to say. An empty tracking
   system never gets filled in; a started one usually does.
