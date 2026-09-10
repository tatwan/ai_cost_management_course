# Decisions

> **Purpose:** a short record of choices that weren't obvious and would be
> expensive to silently re-litigate — the "why is it built this way?" questions
> a new contributor (or an agent about to "helpfully" refactor something) would
> otherwise have to guess at or ask about again.
>
> **When to add an entry:** only when a decision was non-obvious, had a real
> alternative that was rejected, or would look like a mistake to someone
> reading the code cold. Don't log routine choices — this is not a diary of
> every function name debated. One entry per decision; keep them short.
>
> **Template for a new entry:**
> ```
> ## YYYY-MM-DD — <the decision, as a short title>
> **Context:** what problem forced a choice.
> **Decision:** what we chose.
> **Alternatives considered:** what we didn't pick, briefly.
> **Why:** the deciding factor.
> ```

---

## 2026-09-05 — Notebooks are generated, not hand-authored

**Context:** seven `.ipynb` files need to stay consistent in tone, structure
(About to happen / Watch for / Why it matters), and shared boilerplate
(`coursekit.boot()` cell at the top of each).

**Decision:** notebooks are build artifacts. All seven `.ipynb` files are
generated from `build_notebooks.py`; that script is the source of truth.

**Alternatives considered:** hand-editing each notebook directly in Jupyter.

**Why:** hand-editing seven notebooks in lockstep (e.g., changing the rate
card or a shared helper signature) doesn't scale and drifts silently. A build
script makes the shared structure enforceable and diffable.

**Implication for agents:** never hand-edit a `notebooks/*.ipynb` file's
content directly and expect it to stick — edit `build_notebooks.py` (or
`notebooks/coursekit.py` for shared helpers) and regenerate with
`uv run python build_notebooks.py`.

---

## 2026-09-05 — Vendor-neutral by default, Anthropic wins ties

**Context:** the course teaches cost concepts that apply to any provider; it
needs to run for students holding either an OpenAI or an Anthropic key without
forking the material.

**Decision:** `coursekit.boot()` auto-detects which key is present in `.env`
and picks that provider; if both are present, Anthropic is used by default
(its cache read/write usage is reported in separate buckets, which is easier
to explain live than OpenAI's cached-tokens-inside-prompt_tokens accounting).
Override with `LLM_PROVIDER=openai`.

**Why:** keeps one notebook set instead of two, and defaults to the clearer
teaching example without blocking OpenAI-only students.
