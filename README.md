# AI Cost Management and Token Utilization — Course Package
**4-hour masterclass · vendor-neutral · September 2026**

Built against the approved Pluralsight outline. Audience: IT leadership and finance managers alongside AI engineers, architects and product managers.

---

## What is in here

| File | What it is |
|---|---|
| `AI_Cost_Management_and_Token_Utilization.pptx` | **The deck.** 61 slides, full speaker notes on every slide, timing, exercises and demo cues. |
| `RESEARCH_DOSSIER.md` | **The factual backbone.** Every number on every slide, with its primary source — plus a correction table for the agent-research files. |
| `DEMO_GUIDE.md` | **Instructor run-sheets.** Exact click-paths for the 8 website demos, run order for the 7 notebooks, pre-flight checklist and a fallback matrix. |
| `notebooks/*.ipynb` | **7 runnable demos.** Live API calls, cost ledger printed by every cell, Colab-ready. |
| `build_deck.js` | The deck generator, if you want to change content and rebuild. |
| `build_notebooks.py` | The notebook generator. |

---

## The deck at a glance

61 slides across the approved four-module structure, built to the wow-factor archetypes — sourced big-number slides, framework grids, semantic decision cards, comparison tables, and a synthesis band closing every dense slide with its "so what".

| | Module | Slides | Demos |
|---|---|---|---|
| 0:00 | Opening — the paradox | 7 | — |
| 0:12 | **M1** Token economics & forecasting | 15 | W1, W3, W4, W5 · N1 |
| 1:10 | **M2** Prompt & retrieval optimization | 18 | N2, N3, N4, N5 |
| 2:10 | **M3** Model selection & routing | 12 | W3 · N6 |
| 3:10 | **M4** Governance, FinOps & ROI | 14 | W6, W7, W8 · N7 |
| 3:52 | Close — 30-60-90 and the commitment | 4 | — |

**Speaker notes are on every slide.** They carry the delivery guidance, the discussion prompts, the expected workshop answers, and the "say this out loud" moments — not a restatement of the slide.

Four slides are built as take-home artefacts people will photograph: the verified rate card, the tagging schema, the 30-60-90 plan, and the savings-by-lever reference.

---

## The argument the course makes

> **Unit prices collapsed. Bills went up. Both are true — and the gap between them is the entire subject.**

1. **Token price is not the unit of consumption.** The task is. Agentic tasks consume 5–30× the tokens of a chat turn (Gartner 2026) — and the deck *derives* that number from arithmetic rather than quoting it.
2. **Model tier is the biggest single line.** 107× spread for identical behaviour, computed from the verified rate card.
3. **Agent cost is input cost.** Agents re-read accumulated context at every step, which is why context engineering — not output tuning — is where agent bills are won.
4. **Divide by the success rate.** Cost per completed task, including cleanup. Cleanup frequently exceeds the API bill, which makes reliability a cost lever.
5. **FinOps is a practice, not a project.** Track → Attribute → Control → Optimize, in that order.

---

## Editorial standards applied

- **Every number on a slide has a primary or peer-reviewed source.** Vendor-blog percentages appear only as speaker-note colour, never as a headline stat.
- **All pricing was read from the provider's own documentation on 5 September 2026** — Anthropic, OpenAI, Google and DeepSeek — not from secondary summaries.
- **Honest ranges over headline numbers.** The routing module shows both the 85–98% benchmark results *and* UCCI's 31% (95% CI 27–35%) on a real production workload, and explains why they differ.
- **The caching caveat is said out loud**: a 90% input discount lands as roughly 30% off the total bill, because output is never cached.
- **Every cost claim is paired with a quality gate.** Cost reduction without an eval score is an unverified regression, and the notebooks enforce that pattern.

`RESEARCH_DOSSIER.md` §9 lists what the agent-research files got wrong, including two claims that verification directly contradicted. Worth reading before reusing any of those files.

---

## Rebuilding

```bash
# Deck
npm install pptxgenjs        # if not present
node build_deck.js

# Notebooks
python3 build_notebooks.py
```

---

## Before you teach

**Re-verify the rate card.** It is the deck's credibility anchor and prices move. Open the four pricing pages, check the numbers on the rate-card slide and in notebook cell 2, and update both if anything has changed. `DEMO_GUIDE.md` has the full pre-flight checklist.

One known dated item: **Gemini 3.x Flash promotional pricing ends 31 December 2026 and doubles on 1 January 2027.** If you teach near that date, the slide needs a one-line update — and it is worth calling out live as an example of a forecast risk that belongs in a budget rather than a footnote.
