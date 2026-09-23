# AI Cost Management and Token Utilization

**Unit prices collapsed. Bills went up. Both are true — and the gap between them is the subject of this course.**

This repository is a 4-hour masterclass plus eight runnable notebooks. You will learn how LLM inference is actually billed, which architectural choices move the bill by 10–100×, and how to measure, cap, and attribute spend so the saving survives the next invoice.

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
4. **Route routine work to a cheaper model** and judge the result on cost-per-successful-task, including cleanup, then run the same routing through a gateway with fallbacks.
5. **Tag, cap, and kill runaway spend** — the measurement layer most enterprises take six months to build.

The through-line: **never present a cost reduction without a quality number next to it.**

---

## The eight lessons

Work through these in order. They're written so you can study them on your own: each one starts with some background, explains a cell before you run it, and tells you how to read the output afterwards. Each lesson ends with a few **Check yourself** questions (answers are folded, so try first) and a small exercise to try on your own work. Notes marked **In class** are cues for when we run a lesson together. If you're working alone, treat them as a place to stop and think.

The notebooks are committed with the outputs from a real run, so you can read the whole course before you have a key. Your numbers will differ a little, because models aren't deterministic and prices change.

| # | Notebook | You will | Key? | Time |
|---|----------|----------|------|------|
| 1 | [`notebooks/01_token_economics.ipynb`](notebooks/01_token_economics.ipynb) | Count the same instruction five ways, compare a local token estimate with what the provider bills, price 1M identical calls (~107× spread), then toggle agent steps / cache / routing on a forecast | Optional | ~10 min |
| 2 | [`notebooks/02_prompt_caching.ipynb`](notebooks/02_prompt_caching.ipynb) | See a cache write, a cache hit, then a silent miss caused by one timestamp; work out when a cache pays for itself | Required | ~10 min |
| 3 | [`notebooks/03_context_compression.ipynb`](notebooks/03_context_compression.ipynb) | Cut a bloated system prompt by hand, then run a five-question eval (twice per question) on both versions before you ship it | Required for eval | ~10 min |
| 4 | [`notebooks/04_rag_cost.ipynb`](notebooks/04_rag_cost.ipynb) | Chunk a ~6K-token handbook three ways, sweep retrieval `k`, and compare RAG with putting the whole handbook in the prompt | Required for sweep | ~12 min |
| 5 | [`notebooks/05_semantic_cache.ipynb`](notebooks/05_semantic_cache.ipynb) | Stack exact + semantic cache, watch a negated question get a wrong cached answer, and see one customer's answer leak to another | Required for traffic | ~10 min |
| 6 | [`notebooks/06_routing_cascade.ipynb`](notebooks/06_routing_cascade.ipynb) | Build a three-tier cascade, then divide by success rate and add cleanup cost until the cheaper route is the expensive one | Required | ~15 min |
| 7 | [`notebooks/07_finops_telemetry.ipynb`](notebooks/07_finops_telemetry.ipynb) | Tag calls with OpenTelemetry-style spans, find the untagged spend, fire a budget, isolate tenants, kill a looping agent | Required | ~12 min |
| 8 | [`notebooks/08_litellm_gateway.ipynb`](notebooks/08_litellm_gateway.ipynb) | Do Lesson 6's routing through a LiteLLM gateway: one interface over three tiers, fallbacks when a model is down, quality-based escalation, rule-based routing, and an optional local model via Ollama | Required | ~15 min |

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
- **Lesson 1 runs without a key.** Lessons 2–8 need a live key for the cells that call a model. Without one, those cells print a clearly labelled placeholder and the notebook keeps going, so you can still follow the argument. The ledger won't count placeholders as money spent.
- **Lesson 8's local-model section is optional.** It uses [Ollama](https://ollama.com/) if it's running on your machine and skips itself if it isn't.
- Budget **about $2–5** to run everything once on the mid tier (Lessons 7 and 8 cost well under a cent each).
- Rate-card prices were last checked **5 September 2026**. They move. Re-check the provider pricing pages before you quote them.

---

## The argument, in five lines

1. **Token price is not the unit of consumption. The task is.** A chat turn and an agentic task are not the same product.
2. **Model tier is the largest single line.** Identical behaviour, ~107× spread on the verified rate card.
3. **Agent cost is input cost.** Agents re-read accumulated context at every step. Context engineering beats output tweaking.
4. **Divide by the success rate, then add cleanup.** A cheaper route that fails more can be the expensive one.
5. **FinOps is a practice, not a project.** Track → Attribute → Control → Optimize — in that order.

Honest ranges over headlines: a 90% input-cache discount does not take 90% off the bill. Output is never cached, so the saving depends on how much of your bill is input: roughly 30% for a chat-style workload and closer to 60% for a RAG-style one (Lesson 2 works both out). Routing papers quote 85–98%; a production cascade on real traffic (UCCI, 2026) was **31%** (95% CI 27–35%). Plan for the second; celebrate the first.



---

## Regenerating the notebooks

The `.ipynb` files are generated from [`build_notebooks.py`](build_notebooks.py):

```bash
uv run python build_notebooks.py                  # rebuild all eight, no outputs
uv run python build_notebooks.py 02 06            # rebuild selected lessons
uv run python build_notebooks.py --execute 08     # rebuild and run live, keeping the outputs
uv run pytest                                     # cost-math tests
```

Edit the build script, not the `.ipynb` files. Hand edits to a notebook are overwritten on the next build.
