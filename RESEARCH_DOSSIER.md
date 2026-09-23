# Research notes: the numbers behind the course

**AI Cost Management and Token Utilization · September 2026 · vendor-neutral**

This is the reference behind the slides and the notebooks: the rate card, the
statistics, the papers, and the arithmetic, with a source for each. Use it to
check a number before you quote it, or to follow a topic further than the
lessons go.

Two things to keep in mind:

- **Prices were checked against the providers' own pricing pages on
  5 September 2026.** They change often. Check the live page before you rely on
  any price here.
- **Some figures come from analyst reports and secondary write-ups, not
  primary studies.** The table or text says where each one comes from, and the
  section on [how sources were chosen](#7-how-sources-were-chosen) explains
  which ones deserve extra checking.

| Topic | Section | Lesson |
|---|---|---|
| Why bills go up while prices fall | §1 | Lesson 1 |
| Rate card, forecasting, cache break-even | §2 | Lessons 1, 2 |
| Prompt compression, RAG, caching layers | §3 | Lessons 3, 4, 5 |
| Model tiers, routing, cost per solved task, self-hosting | §4 | Lessons 6, 8 |
| FinOps, telemetry, budgets, circuit breakers | §5 | Lessons 7, 8 |
| A 90-day plan | §6 | — |

---

## 1. Prices fell, bills went up

Unit prices collapsed and bills went up. Both are true, and the gap between
them is what the course is about.

| Fact | Number | Source |
|---|---|---|
| GPT-3-class quality, price drop | $60/M → $0.06/M (2021→2024), ~1,000× | a16z, *LLMflation* (2024) |
| GPT-3.5-class quality, price drop | $20/M → $0.07/M, ~280× | Stanford HAI, *AI Index 2025* |
| Cross-benchmark price decline | Median ~50×/yr; 200×/yr since Jan 2024 | Epoch AI (2025) |
| Enterprise LLM API spend | $3.5B (late 2024) → $8.4B (mid-2025) | Menlo Ventures (2025) |
| Google monthly token throughput | 3.2 quadrillion tokens/mo, ~7× YoY | Google I/O (2026) |
| Share of builders whose workloads are majority inference | 48% → 74% | Menlo Ventures (2025) |
| Inference share of a model's lifetime cost | ≥70% | Gartner (2026) |

The explanation: price per token isn't what you consume. You consume *tasks*,
and a task now takes 5–30× more tokens than it used to, even as each token got
cheaper.

> "Agentic AI consumes 5 to 30 times more tokens per task than a standard
> chatbot exchange." (Gartner, 2026)

> "At least 50% of GenAI projects will exceed budgeted costs by 2028", driven
> by "poor architectural choices and lack of operational expertise" rather than
> list price. (Gartner, June 2026)

> 98% of FinOps practitioners now manage AI spend, up from 63% in 2025 and 31%
> in 2024. FinOps for AI is their top forward-looking priority, and AI value
> management is the biggest skill gap. (FinOps Foundation, *State of FinOps
> 2026*, n=1,192, $83B+ cloud spend)

---

## 2. Token economics and cost forecasting

### 2.1 Rate card (per 1M tokens, standard tier, checked 5 Sept 2026)

**Anthropic.** Source: `platform.claude.com/docs/en/about-claude/pricing`

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Batch in/out |
|---|---|---|---|---|---|---|
| Claude Fable 5.1 / Mythos 5.1 | $10 | $50 | $12.50 | $20 | $0.25 (0.025×) | $5 / $25 |
| Claude Fable 5 / Mythos 5 | $10 | $50 | $12.50 | $20 | $1.00 | $5 / $25 |
| Claude Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 | $5 | $25 | $6.25 | $10 | $0.50 | $2.50 / $12.50 |
| Claude Sonnet 5 | $2 | $10 | $2.50 | $4 | $0.20 | $1 / $5 |
| Claude Sonnet 4.6 / 4.5 | $3 | $15 | $3.75 | $6 | $0.30 | $1.50 / $7.50 |
| Claude Haiku 4.5 | $1 | $5 | $1.25 | $2 | $0.10 | $0.50 / $2.50 |

Anthropic has no long-context premium on Claude 4.6 and later: the full 1M
window is billed at standard rates. US data residency (`inference_geo: "us"`)
is 1.1× on all token types. Fast Mode (Opus 5 / 4.8 only) is $10/$50 and can't
be combined with Batch.

**OpenAI.** Source: `developers.openai.com/api/docs/pricing`. Each cell is
Input / Cached input / Cache writes / Output.

| Model | Short context | Long context |
|---|---|---|
| GPT-6 Astra | $10 / $1 / $12.50 / $50 | $20 / $2 / $25 / $75 |
| GPT-5.6 Sol *(promo until 21 Nov 2026)* | $4 / $0.40 / $5 / $20 | $8 / $0.80 / $10 / $30 |
| GPT-5.6 Terra | $2 / $0.20 / $2.50 / $12 | $4 / $0.40 / $5 / $18 |
| GPT-5.6 Luna | $0.20 / $0.02 / $0.25 / $1.20 | $0.40 / $0.04 / $0.50 / $1.80 |

Cached input is 90% off. It was 50% in the GPT-4o era, and a lot of older
write-ups still say 50%. Batch is 50% off, fast mode is 2×, regional endpoints
add 10%. Long context costs about 2× the short-context rate, the opposite of
Anthropic's current pricing.

**Open question on cache writes.** The table shows a cache-write price as
listed on the pricing page. OpenAI's prompt caching is automatic, and the
course's `coursekit.py` and Lesson 2 treat it as having no write premium
(cache writes billed at the normal input rate). These two don't agree. Check
the pricing page for when the write price applies before you rely on either.

**Google.** Source: `ai.google.dev/gemini-api/docs/pricing`

| Model | Input | Output | Cache | Notes |
|---|---|---|---|---|
| Gemini 3.8 / 3.7 / 3.6 Flash | $0.75 | $3.75 | $0.075 + $0.50/hr storage | Promo until 31 Dec 2026; doubles 1 Jan 2027 |
| Gemini 3.5 Flash | $1.50 | $9.00 | $0.15 | |
| Gemini 3.5 Flash-Lite | $0.30 | $2.50 | — | |
| Gemini 3.1 Pro (preview) | $2.00 ≤200K / $4.00 >200K | $12 / $18 | $0.20 / $0.40 | Price step at 200K |
| Gemini 2.5 Pro | $1.25 / $2.50 | $10 / $15 | $0.125 / $0.25 | Price step at 200K |

**DeepSeek.** Source: `deepseek.ai/pricing`

| Model | Cache miss in | Cache hit in | Output |
|---|---|---|---|
| DeepSeek V4-Flash | $0.14 | $0.0028 (98% off) | $0.28 |
| DeepSeek V4-Pro | $0.435 | $0.003625 | $0.87 |

### 2.2 Three things about the shape of prices

1. **Output costs 5–6× input, at every provider.** Output is generated one
   token at a time, and each token is a full pass through the model that is
   limited by memory bandwidth. Input is processed in parallel. So a verbose
   answer costs more than a clever one.
2. **Cache reads are 90–98% off input.** Anthropic 0.1× (0.025× on
   Fable/Mythos 5.1), OpenAI 0.1×, Gemini 0.1×, DeepSeek 0.02×.
3. **Long-context surcharges are a vendor choice, not an industry norm.**
   OpenAI and Google charge about 2× past a threshold; Anthropic 4.6+ doesn't.
   If your workload has long prompts, this belongs in the procurement
   conversation.

### 2.3 A forecast formula

```
Monthly $ = Requests
          × [ (T_in_fresh × P_in) + (T_in_cached × P_cache) + (T_out × P_out) ]
          / 1,000,000
          × M_agent          ← steps/tool calls per user-visible task
          × M_context        ← long-context price multiplier (1.0 or ~2.0)
          × (1 + R_retry)    ← retry and failure rate
```

The first line is what most business cases stop at. The last three
multipliers are where forecasts go wrong. Lesson 1 builds this as a function
you can play with.

### 2.4 Worked example: the same feature on nine models

1,000,000 requests a month, 800 input tokens and 200 output tokens each, same
product behaviour. Computed from the rate card above.

| Model | Monthly cost | vs. cheapest |
|---|---|---|
| DeepSeek V4-Flash | $168 | 1.0× |
| GPT-5.6 Luna | $400 | 2.4× |
| Gemini 3.5 Flash-Lite | $740 | 4.4× |
| Claude Haiku 4.5 | $1,800 | 10.7× |
| Claude Sonnet 5 | $3,600 | 21.4× |
| GPT-5.6 Terra / Gemini 3.1 Pro | $4,000 | 23.8× |
| GPT-5.6 Sol | $7,200 | 42.9× |
| Claude Opus 5 | $9,000 | 53.6× |
| GPT-6 Astra / Claude Fable 5.1 | $18,000 | 107× |

A 107× spread for the same feature. Model choice is the biggest single line on
the bill.

### 2.5 Worked example: the agent multiplier

The same user question, but answered by a 5-step agent that re-reads its
growing context at every step (3K → 6K → 9K → 12K → 15K = 45K input tokens,
plus 200 output tokens per step = 1,000 output). On Claude Sonnet 5:

- **Chat:** (800×$2 + 200×$10)/1M = $0.0036 per task
- **Agent, no caching:** (45,000×$2 + 1,000×$10)/1M = $0.100 per task, 28× the chat cost
- **Agent with prompt caching** (80% of the re-read context cached):
  (9,000×$2 + 36,000×$0.20 + 1,000×$10)/1M = $0.0352 per task. That's 65%
  saved, and still 10× the chat cost.

This arithmetic arrives at Gartner's 5–30× on its own, and it shows caching
is a partial fix, not a cure.

### 2.6 When does a prompt cache pay for itself?

`N_breakeven = 1 + (P_write − P_input) / (P_input − P_read)`

| Model / cache lifetime | Pays for itself on |
|---|---|
| Anthropic, 5-minute cache (any model above) | 2nd call |
| Anthropic, 1-hour cache | 3rd call |
| OpenAI, if cache writes carry no premium (see §2.1) | 1st call |

With a 1.25× write premium and a 0.1× read, caching is ahead from the second
call. For a workload with a stable prefix it's hard to lose money on caching.
The real risk is invalidating the cache by accident, usually by putting
something that changes (a timestamp, a session ID) near the start of the
prompt. That's the bug Lesson 2 reproduces.

A prefix also has to meet a minimum length before it's cached at all: about
1,024 tokens, more on some models (Claude Haiku 4.5 needs 4,096). Shorter
prefixes are silently not cached, with no error.

### 2.7 Where forecasts go wrong

1. **Forecasting per token instead of per task.** Researchers at the Stanford
   Digital Economy Lab found identical agents on identical tasks varied up to
   30× in cost between runs, and frontier models were poor at predicting their
   own token use.
2. **Costs outside the model invoice.** Retrieval, embeddings, reranking,
   observability, retries, and human review.
3. **Adoption curves.** Uber reportedly used its entire 2026 AI coding budget
   in four months across ~5,000 engineers ($150–$250 per engineer per month
   typical, $500–$2,000 for heavy users), then capped spend at $1,500 per
   employee per tool per month. Linear forecasts don't survive adoption.
   Model a best, base, and worst case with a wide spread between them.

---

## 3. Prompt and retrieval optimization

### 3.1 Where the input tokens actually are

A typical enterprise RAG or agent call, about 8,600 input tokens:

```
System prompt              500      6%
Tool / function schemas  2,500     29%   ← often the biggest single part
Retrieved context (5)    4,000     47%   ← often more than the answer needs
Conversation history     1,500     17%
User message               100      1%
```

Most people start by trimming the system prompt, which here is 6% of input.
Tool schemas and retrieved context are 76%.

### 3.2 Context engineering

Anthropic's *Effective context engineering for AI agents* treats context as a
limited attention budget rather than a container to fill. Recall gets worse
as the window grows, on every model (often called *context rot*). Their
stated goal:

> "Find the smallest possible set of high-signal tokens that maximize the
> likelihood of some desired outcome."

Four techniques, each of which helps quality and cost at once:

| Technique | What it does | Cost effect |
|---|---|---|
| Compaction | Summarise history near the context limit; keep decisions and open items, drop redundant tool output | Stops multi-turn input growing without limit |
| Structured note-taking | Keep memory *outside* the window (a notes file, a to-do list) | Removes history from every call |
| Just-in-time retrieval | Pass identifiers (paths, URLs, queries) and let the agent load what it needs | No pre-loaded corpus tokens |
| Sub-agents | Delegate to agents with clean windows that return short summaries | Parallel work with bounded context per agent |

On tools, the same article warns that a bloated tool set is a cost problem and
an accuracy problem: "If humans can't definitively identify which tool
applies, agents cannot perform better."

### 3.3 Compressing a prompt by hand

A five-step checklist typically cuts a system prompt by 20–40% with no quality
loss:

1. Remove repeated constraints (often 5–15% of tokens)
2. Turn prose into numbered lists
3. Use fewer, better examples (one strong example beats three average ones)
4. Delete stale or conflicting instructions (they cost tokens *and* accuracy)
5. Use compact delimiters (`###` rather than `===== SECTION =====`)

Always check the answers still hold on a fixed set of test questions before
you ship the shorter prompt. Lesson 3 does exactly this.

Ordering matters for caching too: stable content (system prompt, tool schemas,
policies) goes first, and anything that changes (timestamps, session IDs, the
user's message) goes last. One changing token near the front means the cached
prefix no longer matches, so a 0.1× cache read becomes a 1.25× cache write.

### 3.4 Automatic compression

| Method | How it works | Reported result |
|---|---|---|
| Selective Context | Prunes low-information words using a small auxiliary model | ~2× compression, small BERTScore loss |
| LLMLingua (Microsoft Research, EMNLP'23) | Coarse-to-fine pruning by perplexity, with a budget controller | Up to 20× compression, <2% quality loss |
| LLMLingua-2 (ACL'24) | Treats compression as token classification with an encoder | 2–5× compression, up to 2.9× faster than LLMLingua |
| LongLLMLingua | Question-aware compression for RAG | ~4× compression, +21.4% accuracy on long-context QA |

Compression works well on verbose instructions and retrieved prose. It goes
wrong on code, numbers, invoices, identifiers, and legal citations, where a
dropped token changes the meaning. Keep those out of the compressor.

### 3.5 Chunking is a cost decision

A 2026 synthesis of chunking benchmarks (FloTorch 2026 on 50 papers /
905,746 tokens; NVIDIA 2024; Chroma Research; Superlinked VectorHub):

| Strategy | End-to-end accuracy | Setup |
|---|---|---|
| Recursive character splitting | 69%, best overall | 512 tokens, 50–100 overlap |
| Fixed-size | 67% | 512 tokens |
| Page-level | 64.8% | paginated financial PDFs |
| Semantic | 91.9% *retrieval recall* but 54% end-to-end | chunks averaged 43 tokens |

Semantic chunking found the right passages more often but produced worse
answers. Its chunks averaged 43 tokens, which is very little context per
chunk. Recursive
splitting needs no model calls, runs in milliseconds, and beat the more
expensive options. Start there and move only if your own eval says so.

Rough sizes: 256–512 tokens for factual lookups, 512–1,024 for analytical
questions, 1,024 for financial documents (57.9%). Overlap of 10–25% of the
chunk size.

### 3.6 Long context vs. RAG

*The Token Tax of Epistemic Accuracy* (arXiv 2606.20898, 2026) tested 972
answers across 3 machines, 2 small models, and 3 retrieval/prompting
approaches on a manufacturing-safety benchmark:

- Putting everything in the prompt: 73.1% correct
- Semantic RAG: 65.4% correct
- Everything-in-the-prompt used 26× the tokens per query

That's 7.7 points of accuracy for 26× the cost. Whether it's worth it depends
on what a wrong answer costs you, so treat it as a business decision rather
than an architecture preference. Lesson 4 reproduces the shape of this on a
small handbook.

### 3.7 The caching layers

These three are often confused:

| Layer | Matches on | Latency | Saves | Main risk |
|---|---|---|---|---|
| L1 exact cache | Byte-identical query | <1 ms | The whole call | Low hit rate on its own |
| L2 semantic cache | Embedding similarity ≥ a threshold (0.88–0.95 is common) | 3–10 ms | The whole call | False hits |
| L3 provider prompt cache | Identical prompt *prefix* | 50–200 ms | 90–98% of the *cached input only* | Invalidation from prompt ordering |
| L4 model call | — | 500–2,000 ms | — | — |

*GPT Semantic Cache* (arXiv 2411.05276) reports hit rates of 61.6–68.8% and up
to 68.8% fewer API calls. Your hit rate depends entirely on how repetitive your
traffic is, so measure it rather than assuming it.

**What a prompt cache does to the whole bill.** A 90% discount on cached input
does not take 90% off the bill, because output is never cached. At an 80% hit
rate, it's roughly 31% off for a chat-style workload (short prompts, longer
answers) and roughly 58% for a RAG-style one (long prompts, short answers).
Lesson 2 works both out.

**False hits.** "Cancel the order" and "cancel the standing order" are very
similar as embeddings, but they ask for different things. So do "move my
delivery from Monday to Friday" and the same sentence with the days swapped.
A semantic cache can't tell. Decide which kinds of answer are safe to cache
before you celebrate a hit rate, keep account-specific answers out of shared
caches, and namespace the cache per tenant. Lesson 5 shows both failures.

---

## 4. Model selection and routing

### 4.1 Model tiers (vendor-neutral)

| Tier | Typical input $/M | Typical output $/M | Suited to |
|---|---|---|---|
| Floor | $0.14–$0.30 | $0.28–$2.50 | Classification, extraction, routing, reformatting |
| Volume | $0.75–$1.00 | $3.75–$5.00 | Summarisation, structured processing, routine Q&A |
| Near-frontier | $2–$5 | $10–$25 | Multi-step reasoning, code, grounded analysis |
| Frontier | $10–$20 | $50–$75 | Novel reasoning, high-stakes synthesis, unattended agents |

Production reports commonly put 60–80% of enterprise queries in the floor and
volume tiers, while by default they run on near-frontier or frontier models.
Treat that range as a planning prior, and measure your own traffic.

### 4.2 Routers and cascades

| Pattern | How it works | Latency cost | Best for |
|---|---|---|---|
| Router (decide before the call) | A classifier or rules pick the model up front | +10–20 ms | Known task types; latency-sensitive work |
| Cascade (escalate after the call) | Cheap model first; escalate if the answer fails a check | Sequential; can double latency | Open-ended queries; quality-critical work |
| Hybrid | Route known tasks, cascade the ambiguous 10–20% | Mixed | Most production systems |

What the research reports:

| Study | Result |
|---|---|
| FrugalGPT (Stanford, 2023) | 50–98% cost reduction with a confidence cascade at matched quality |
| RouteLLM (LMSYS / Berkeley / Anyscale) | Matrix-factorisation router kept 95% of GPT-4 quality on MT-Bench while sending only 14–26% of queries to the strong model, about an 85% cost cut. A BERT classifier router added <15 ms and cut cost 45% on MMLU |
| Cluster-Route-Escalate (arXiv 2606.27457, 2026) | Kept 97–99% of the strongest model's accuracy; adapts when the model pool changes; needs only task-correctness labels |
| UCCI (arXiv 2605.18796, 2026) | Calibrated uncertainty for escalation. 31% cost reduction (95% CI 27–35%) at micro-F1 0.91 on a 75K-query production NER workload. Beat entropy thresholds, conformal prediction, and FrugalGPT-style routing at the same accuracy. Calibration error fell from 0.12 to 0.03 |

The headline 85–98% figures come from academic benchmarks where the gap
between cheap and strong models is wide. UCCI measured a real production
workload and got 31%, with a confidence interval. Plan for something like the
second number. 31% of a real bill is still a lot of money.

On escalation signals: deterministic checks (does the output parse, does it
match the schema) are the most reliable; calibrated confidence scores come
next; asking the model to rate its own confidence is the weakest. Lesson 6
uses the first two.

### 4.3 Cost per solved task, not cost per token

DoiT's formula:

```
E[cost per solved task] = C_attempt / p_success  +  L × K_cleanup
```

`C_attempt` is the billed cost of the whole attempt, `p_success` the chance it
succeeds, `L` the share of wrong outputs that leak through to users, and
`K_cleanup` what it costs to clean one up.

Reported figures (Aug 2026):

| Workload | Model | Cost per *successful* task |
|---|---|---|
| Intelligence Index | GPT-5.6 Sol | $1.04 |
| Intelligence Index | Claude Opus 4.8 | $1.80 |
| Intelligence Index | Claude Opus 5 | $2.03 |
| SWE-bench Verified | GPT-5.6 Sol | ~$1.56 per solved issue (96.2% success) |
| SWE-bench Verified | Claude Opus 4.8 | ~$3.06 per solved issue (88.6% success) |
| τ-bench airline support | Claude Opus 4.8 | $1.47 per correct task (incl. $100 cleanup, 4 policy violations) |
| τ-bench airline support | GPT-5.5 | $2.63 per correct task (incl. $225 cleanup, 9 policy violations) |

Cleanup often costs more than the API bill. A cheaper model that fails more
often can end up the more expensive one, which makes reliability a cost lever
as well as a quality one. Lesson 6 finds the point where this flips.

### 4.4 Fine-tuning vs. few-shot examples

- **Few-shot:** nothing up front, but you pay for the examples on every call.
  Long example blocks cache well, which softens this a lot. Suits fewer than
  ~1,000 examples or tasks that change often.
- **Fine-tuning:** training and hosting cost up front; shorter prompts, and a
  smaller model can match a larger one on a narrow task. Suits more than
  ~5,000 good examples at steady volume.
- **Distillation** (a large model labels data, then you fine-tune a small
  model on it) is the common approach in 2026.
- The break-even is arithmetic: (few-shot tokens × price × monthly volume)
  against (training cost spread over its useful life + hosting + the change in
  per-call price).

### 4.5 Self-hosting vs. an API

A single H100, all in (2026): about $1,440/month cloud rental + $1,500/month
DevOps time + $300/month other infrastructure ≈ $3,240/month.

Monthly token volume needed to break even, at 60–70% utilisation:

| Replacing | Break-even |
|---|---|
| DeepSeek V4-Flash-class ($0.14/M) | ~5.7B tokens/month |
| Claude Sonnet-class ($3/M) | ~430M tokens/month |
| GPT-5-class ($5/M) | ~256M tokens/month |

Utilisation decides it. At about 10% utilisation the real cost per token is
about 10× the headline GPU rate ($0.013 becomes $0.13 per 1K tokens), which is
worse than premium API pricing. Engineering time typically multiplies raw GPU
rental cost by 3–5×.

A rough rule: self-host above 1–5B tokens a month with steady, high
utilisation, or when compliance forbids sending data to a third party. Use an
API below ~250M tokens a month or with bursty load. Common serving stacks are
vLLM (general throughput) and SGLang (prefix-heavy RAG and multi-turn); Text
Generation Inference went into maintenance mode in December 2025. Lesson 8 has
this break-even table next to a local model you can try.

---

## 5. Governance, FinOps, and measuring value

### 5.1 The state of practice (2026)

From the FinOps Foundation's *State of FinOps 2026* (n=1,192, $83B+ annual
cloud spend):

- 98% manage AI spend (63% in 2025, 31% in 2024)
- 90% manage SaaS, 64% licensing, 57% private cloud, 48% data centre, 28% labour
- 78% of FinOps teams report to the CTO or CIO (up 18 points since 2023)
- Teams with C-suite engagement have 2–4× more influence over technology choices
- The top AI-specific obstacles: seeing AI cost, allocating it to business
  units, and showing value or ROI
- Many organisations are asked to "self-fund AI investments through efficiency
  gains"

### 5.2 Track → Attribute → Control → Optimize

**Track.** Record usage from every provider response; that's the billing
record. Normalise it carefully. OpenAI counts cached tokens *inside*
`prompt_tokens`, while Anthropic reports `cache_read_input_tokens` in a
separate field. Add them up naively and you count cached tokens twice.

**Attribute.** Attach metadata to every call. A minimal tag set:

```yaml
business_unit:  sales-mktg          # who pays
use_case_id:    uc-12345            # stable per use case
environment:    dev | staging | prod
model_id:       <provider/model>
workload_type:  inference | embedding | fine-tuning | training
user_id:        u-789               # per-user attribution
session_id:     s-abc               # spotting agent loops
cost_tier:      1 | 2 | 3           # foundation / enablement / differentiation
```

Measure tag coverage, too. Untagged spend can't be allocated to anyone, and it
tends to grow quietly.

**Control.** Enforce limits at a gateway, not in each application. A common
three-step policy: at 50% of budget, notify and pause non-production traffic;
at 80%, review and require approval for new experiments; at 100%, hard stop on
non-critical traffic. A budget check before each call will always overshoot by
up to one call, because you only know the cost afterwards.

**Optimize.** Sort attributed spend by feature and difficulty, move routine
work to cheaper tiers, reorder prompts for cache hits, and trim retrieval.

### 5.3 OpenTelemetry GenAI semantic conventions

As of July 2026 these are still marked **Development**, not Stable; no
GenAI-specific span, metric, or attribute is Stable yet. Expect names to
change.

Key span attributes:

- `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` (v1.27+; many
  frameworks still also emit the older `prompt_tokens` / `completion_tokens`,
  so query both). Input tokens include cached tokens.
- `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.cache_creation.input_tokens`
- `gen_ai.provider.name` (renamed from `gen_ai.system` in v1.37.0, Aug 2025)
- `gen_ai.request.model`, `gen_ai.response.finish_reasons`
- `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`

Metrics: `gen_ai.client.token.usage` (a histogram, filterable by
`gen_ai.token.type`) and `gen_ai.client.operation.duration`. Duration is a
metric, not a span attribute.

Spans nest: `invoke_agent` → child `chat` spans → child `execute_tool` spans.
That nesting is what lets you add up the cost of a whole task instead of only
individual calls. Lesson 7's spans follow these names.

### 5.4 What a hard cap means in a gateway

The LiteLLM proxy can enforce budgets at several levels: the whole proxy,
team, internal user, virtual key, model, end user or customer, and tag or
project. Budgets reset on a duration you set (`30s`, `30m`, `30h`, `30d`); if
you don't set one, the budget never resets. Rate limits cover tokens per
minute, requests per minute, parallel requests, and per-model limits. When a
budget is exceeded, requests fail with `ExceededBudget`.

The LiteLLM docs say "Every budget is enforced against spend read from the
database." A deployment without a database can't enforce budgets, so
governance depends on the architecture.

Circuit breakers for agents (enforced outside the model):

- Max tool calls per task (50 is a reasonable default; beyond that it's
  probably a loop)
- Max tokens per session (e.g. 200K)
- Max wall-clock time per task (e.g. 5 minutes)
- Max spend per session or trace (e.g. $5.00)

### 5.5 Metrics worth reporting

| Metric | Formula | Why |
|---|---|---|
| Cost per completed task | `C_attempt / p_success` | The right unit for agents |
| Cost per business outcome | Total cost / tickets resolved, leads qualified, … | The number finance funds |
| Cost per inference | Total inference cost / requests | Unit price of the feature |
| Cache hit rate *and* false-hit rate | — | Hit rate alone rewards unsafe caching |
| Share of traffic on the cheapest tier | — | Early sign of whether routing is working |
| Tokens per task / per conversation | — | Catches loops early |
| Forecast vs. actual (weekly) | — | Shows how mature your forecasting is |
| Anomaly cost share | Spike cost / total spend | Surfaces runaway agents |

Cost per token hides problems: by the time it moves, a runaway agent has
already run. Cost per completed task, with a hard ceiling, shows them early.

### 5.6 Where this is heading

Gartner predicted in January 2026 that by 2030, GenAI cost per resolution in
customer service will exceed $3, more than many offshore human agents cost.

> "Full automation will be prohibitively expensive for most organizations;
> instead, leading organizations will use AI to drive customer engagement
> rather than to cut costs." (Patrick Quinlan, Senior Director Analyst, Gartner)

Gartner also expects regulation to increase assisted-service volume by 30% by
2028, as rules require easy access to a human agent.

The point for cost management: making tokens cheaper isn't enough if the unit
economics of the task don't work.

---

## 6. A 90-day plan

**Days 1–30: see the spend.** Put a gateway in front of every call. Tag every
call. Build one dashboard (spend by model, team, and use case) and one alert
(daily spend above a threshold). Find the five call sites that spend the most.
*Cost: $0–$200 a year on open-source tools. Outcome: visibility on all spend.*

**Days 31–60: stop the obvious waste.** Turn on provider prompt caching for
stable prefixes. Put stable content first in every prompt. Semantic-cache the
ten most repeated queries. Move floor and volume work to cheaper models. Cap
output length. *Typical result: 30–50% lower spend with no quality change,
checked against an eval.*

**Days 61–90: govern and forecast.** A tiered router with an eval gate.
Per-team and per-user hard caps. Circuit breakers for agents. Measure cost per
completed task. Publish a best/base/worst quarterly forecast and run the first
cost review with finance. *Typical cumulative result: 50–70% lower on the same
workload.*

The percentages are typical ranges from practitioner reports, not guarantees.
Measure your own before and after.

---

## 7. How sources were chosen

- **Prices** come from the providers' own pricing pages.
- **Headline statistics** in the lessons and slides come from primary
  research, peer-reviewed or preprint papers, or named analyst firms (Gartner,
  FinOps Foundation, Menlo Ventures, Stanford HAI, Epoch AI).
- **Some figures come from secondary write-ups** that collect other people's
  numbers (the chunking benchmark synthesis, the self-hosting guide, the
  agentic-cost and inference-statistics round-ups below). They're linked so you
  can trace them. Follow them back to the original before you quote one.
- **Two figures have no direct link here:** the Stanford Digital Economy Lab
  run-to-run variance (§2.7) and the Uber coding-budget story (§2.7). Treat them
  as illustrations and verify them before repeating them.
- Some widely repeated numbers were left out because they couldn't be traced
  to a primary source: a "$47,000 in 11 days" agent-loop story, "72% of AI
  cost sits outside the model invoice", and "31% of enterprise queries are
  semantically similar". The ideas behind them are real; the specific numbers
  aren't sourced.

---

## 8. Sources

**Pricing (checked 5 Sept 2026)**
- Anthropic: https://platform.claude.com/docs/en/about-claude/pricing
- OpenAI: https://developers.openai.com/api/docs/pricing
- Google: https://ai.google.dev/gemini-api/docs/pricing
- DeepSeek: https://deepseek.ai/pricing

**Research, standards, and frameworks**
- FinOps Foundation, *State of FinOps 2026*: https://data.finops.org/
- Linux Foundation press release on *State of FinOps 2026*: https://www.linuxfoundation.org/press/state-of-finops-survey-ai-value-and-skills-top-priorities-as-finops-matures-across-technology-value-98-manage-ai-90-saas-64-licensing-48-data-center-1
- FinOps for AI overview: https://www.finops.org/wg/finops-for-ai-overview/
- FinOps Framework, AI technology category: https://www.finops.org/framework/technology-categories/ai/
- Anthropic, *Effective context engineering for AI agents*: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- *The Token Tax of Epistemic Accuracy*: https://arxiv.org/abs/2606.20898
- *Cluster, Route, Escalate*: https://arxiv.org/abs/2606.27457
- *UCCI: Calibrated Uncertainty for Cost-Optimal LLM Cascade Routing*: https://arxiv.org/html/2605.18796
- LLMLingua (Microsoft Research): https://github.com/microsoft/LLMLingua · https://arxiv.org/abs/2310.05736
- *GPT Semantic Cache*: https://arxiv.org/html/2411.05276v2
- OpenTelemetry, GenAI observability: https://opentelemetry.io/blog/2026/genai-observability/
- LiteLLM, budgets and rate limits: https://docs.litellm.ai/docs/proxy/users
- Gartner, GenAI cost per resolution (Jan 2026): https://www.gartner.com/en/newsroom/press-releases/2026-01-26-gartner-predicts-genai-cost-per-resolution-for-customer-service-will-exceed-offshore-human-agent-costs-by-2030
- DoiT, *Cost per task vs cost per token*: https://www.doit.com/blog/cost-per-task-vs-cost-per-token
- Artificial Analysis (live cost-vs-intelligence comparison): https://artificialanalysis.ai/

**Secondary write-ups (check the original before quoting)**
- Gartner, 50% of GenAI projects over budget by 2028 (news report): https://thejournal.com/articles/2026/06/22/report-half-of-gen-ai-projects-could-exceed-budget-by-2028.aspx
- OTel GenAI semantic conventions status (July 2026, blog): https://john-hodge.com/blog/opentelemetry-genai-semantic-conventions/
- RAG chunking 2026 benchmark synthesis: https://www.premai.io/blog/rag-chunking-strategies-the-2026-benchmark-guide/
- Self-hosting open-weight LLMs, 2026 decision guide: https://www.digitalapplied.com/blog/self-hosting-open-weight-llms-2026-deployment-decision-guide
- Agentic inference cost (Gartner and Stanford figures collected): https://www.spheron.network/blog/agentic-ai-inference-cost-2026/
- AI inference cost statistics 2026 (a16z, Stanford HAI, Epoch, Menlo collected): https://voxbooster.com/blog/ai-inference-cost-statistics-2026/
