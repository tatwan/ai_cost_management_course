# AI Cost Management and Token Utilization

**Unit prices collapsed. Bills went up. Both are true — and the gap between them is the subject of this course.**

This repository is a 4-hour masterclass plus seven runnable notebooks. You will learn how LLM inference is actually billed, which architectural choices move the bill by 10–100×, and how to measure, cap, and attribute spend so the saving survives the next invoice.

It is vendor-neutral. The notebooks run against **OpenAI or Anthropic** — you only need one API key.

---

## Who this is for

- Engineers and architects shipping LLM features who just saw the first production bill
- Product managers who need a cost model that survives “we added an agent”
- Finance, FinOps, and IT leadership who are asked to approve a number they cannot yet forecast

You should be comfortable with APIs and cloud bills. You do not need to have trained a model.

---

## What you will walk away able to do

1. **Forecast per completed task**, not per million tokens — including agent steps, cache hits, and retries.
2. **Turn on prompt caching without silently invalidating it** (the timestamp-in-the-prefix bug).
3. **Cut context and RAG input** and prove quality held on a fixed eval set.
4. **Route routine work to a cheaper model** and judge the result on cost-per-successful-task, including cleanup.
5. **Tag, cap, and kill runaway spend** — the measurement layer most enterprises take six months to build.

The through-line: **never present a cost reduction without a quality number next to it.**

---

## The seven lessons

Work through these in order. Each notebook tells you what is about to happen, what to watch for, and why it matters *before* you run the cell. Blockquotes marked **Presenting:** are live-demo cues; if you are studying solo, treat them as the takeaway.

| # | Notebook | You will | Key? | Time |
|---|----------|----------|------|------|
| 1 | [`notebooks/01_token_economics.ipynb`](notebooks/01_token_economics.ipynb) | Count the same instruction five ways, price 1M identical calls (~107× spread), then toggle agent steps / cache / routing on a forecast | Optional | ~8 min |
| 2 | [`notebooks/02_prompt_caching.ipynb`](notebooks/02_prompt_caching.ipynb) | See a cache write, a cache hit, then a silent miss caused by one timestamp | Required | ~8 min |
| 3 | [`notebooks/03_context_compression.ipynb`](notebooks/03_context_compression.ipynb) | Compress a bloated system prompt 20–40% and run a 5-question eval on both versions | Required for eval | ~10 min |
| 4 | [`notebooks/04_rag_cost.ipynb`](notebooks/04_rag_cost.ipynb) | Sweep retrieval `k`, find the smallest k that still answers, compare to stuffing the whole corpus | Required for sweep | ~12 min |
| 5 | [`notebooks/05_semantic_cache.ipynb`](notebooks/05_semantic_cache.ipynb) | Stack exact + semantic cache, then watch two “similar” cancel-order queries collide | Required for traffic | ~8 min |
| 6 | [`notebooks/06_routing_cascade.ipynb`](notebooks/06_routing_cascade.ipynb) | Build a three-tier cascade, then divide by success rate until the cheaper route is the expensive one | Required | ~15 min |
| 7 | [`notebooks/07_finops_telemetry.ipynb`](notebooks/07_finops_telemetry.ipynb) | Tag calls, fire a hard budget, isolate tenants, kill a looping agent | Required | ~12 min |

Setup, model overrides, and what to do when a live call fails: **[notebooks/README.md](notebooks/README.md)**.

---

## Run the notebooks

You need [uv](https://docs.astral.sh/uv/) and one API key (OpenAI or Anthropic).

```bash
uv sync
cp .env.example .env          # add OPENAI_API_KEY or ANTHROPIC_API_KEY
uv run jupyter lab notebooks/
```

- **One key is enough.** If both are set, Anthropic is the default (clearer cache metadata). Force a vendor with `LLM_PROVIDER=openai`.
- **Lesson 1 runs without a key.** Lessons 2–7 need a live key for the cells that call a model; if a call fails, the notebook continues with a rehearsal fallback so you can still read the argument.
- Budget **about $2–5** to run everything once on the mid tier (lesson 7 uses the cheap tier on purpose).
- Rate-card prices were last checked **5 September 2026**. They move. Re-check the provider pricing pages before you quote them.

---

## The argument, in five lines

1. **Token price is not the unit of consumption. The task is.** A chat turn and an agentic task are not the same product.
2. **Model tier is the largest single line.** Identical behaviour, ~107× spread on the verified rate card.
3. **Agent cost is input cost.** Agents re-read accumulated context at every step. Context engineering beats output tweaking.
4. **Divide by the success rate, then add cleanup.** A cheaper route that fails more can be the expensive one.
5. **FinOps is a practice, not a project.** Track → Attribute → Control → Optimize — in that order.

Honest ranges over headlines: a 90% input-cache discount is ~30% off the **total** bill (output is never cached). Routing papers quote 85–98%; a production cascade on real traffic (UCCI, 2026) was **31%** (95% CI 27–35%). Plan for the second; celebrate the first.



---

## Regenerating the notebooks

The `.ipynb` files are generated from [`build_notebooks.py`](build_notebooks.py):

```bash
uv run python build_notebooks.py
```
