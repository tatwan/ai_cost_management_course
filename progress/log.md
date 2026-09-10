# Work Log

> **Purpose:** an append-only, chronological record of what actually happened —
> newest entry on top. This is the project's memory across sessions: when you
> (human or agent) come back after a break, read the last few entries here to
> reload context before doing anything else.
>
> **How to write an entry:** date it, say what you did and why in a sentence or
> two, and note anything a future session needs to know (a decision, a blocker,
> a thing you deliberately left broken). Don't just log "what" — the code diff
> already shows that. Log the *why* and anything not obvious from the diff.
>
> **Log vs. current_state.md:** this file is a *timeline*; `current_state.md` is
> a *snapshot*. Every entry here should eventually be reflected in an update to
> `current_state.md` if it changes where the project stands.

---

## 2026-09-10 — Labs run, template files added

Ran the full lab sequence with students; went well end to end. Added an
`AGENTS.md` at the repo root plus this `progress/` folder as a worked example
students can copy into their own repos — the goal is to show a minimal,
concrete pattern for keeping an AI coding agent (and collaborators) oriented
across sessions, not just tell them about it abstractly.

**Why now:** a few students asked specifically for an `AGENTS.md` template
after seeing it referenced in tooling docs; better to hand them a real,
populated example from a repo they already know than a blank one.

---

## 2026-09-08 — Initial commit → "updated labs"

Course repo brought in with seven notebooks, `coursekit.py` helper, and the
pytest suite for cost-accounting correctness. See `git log` for the literal
diff; this line just marks that history predates the `progress/` folder.
