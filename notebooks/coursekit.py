"""Shared helpers for the AI Cost Management live demos.

Import with::

    from coursekit import boot
    cfg = boot()

``boot()`` loads ``.env``, picks OpenAI or Anthropic from the keys you have,
prints a one-line banner, and returns a ``Config`` you can ignore if you like
the module-level shortcuts (``complete``, ``cost``, ``ledger``, ``MODELS``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Rate card — illustrative, verified 5 September 2026. Re-check before class.
# USD per 1,000,000 tokens.  cw = cache write, cr = cache read.
# OpenAI, Gemini (implicit) and DeepSeek charge no cache-write premium, so their
# cw equals inp. Anthropic charges 1.25x input for a 5-minute cache write.
# ---------------------------------------------------------------------------
PRICES: dict[str, dict[str, float]] = {
    "deepseek-v4-flash": dict(inp=0.14, out=0.28, cw=0.14, cr=0.0028),
    "gpt-5.6-luna": dict(inp=0.20, out=1.20, cw=0.20, cr=0.02),
    "gemini-3.5-flash-lite": dict(inp=0.30, out=2.50, cw=0.30, cr=0.03),
    "gemini-3.8-flash": dict(inp=0.75, out=3.75, cw=0.75, cr=0.075),
    "claude-haiku-4-5": dict(inp=1.00, out=5.00, cw=1.25, cr=0.10),
    "claude-sonnet-5": dict(inp=2.00, out=10.00, cw=2.50, cr=0.20),
    "gpt-5.6-terra": dict(inp=2.00, out=12.00, cw=2.00, cr=0.20),
    "gpt-5.6-sol": dict(inp=4.00, out=20.00, cw=4.00, cr=0.40),
    "claude-opus-5": dict(inp=5.00, out=25.00, cw=6.25, cr=0.50),
    "gpt-6-astra": dict(inp=10.00, out=50.00, cw=10.00, cr=1.00),
    "claude-fable-5-1": dict(inp=10.00, out=50.00, cw=12.50, cr=0.25),
}

DEFAULT_TIERS = {
    "anthropic": {
        "floor": "claude-haiku-4-5",
        "mid": "claude-sonnet-5",
        "frontier": "claude-opus-5",
    },
    "openai": {
        "floor": "gpt-5.6-luna",
        "mid": "gpt-5.6-terra",
        "frontier": "gpt-5.6-sol",
    },
}

LEDGER: list[dict[str, Any]] = []
_NO_THINKING_OFF: set[str] = set()          # Anthropic models that reject thinking=disabled
_OPENAI_OPTS: dict[str, dict[str, Any]] = {}  # per-model request options that worked
PROVIDER: str | None = None
MODELS = type("Models", (), {"floor": "", "mid": "", "frontier": ""})()
_CLIENT = None
_BOOTED = False


@dataclass
class UsageNorm:
    fresh_input: int
    output: int
    cache_write: int = 0
    cache_read: int = 0


@dataclass
class Result:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    fresh_input: int
    cache_write: int = 0
    cache_read: int = 0
    usd: float = 0.0
    reasoning_tokens: int = 0
    raw: Any = None
    fallback: bool = False


@dataclass
class Config:
    provider: str
    models: Any
    live: bool
    prices_note: str = "Rate card last checked 5 September 2026 — re-verify before presenting."


# ---------------------------------------------------------------------------
# Money
# ---------------------------------------------------------------------------
def usd(x: float) -> str:
    if x < 0.01:
        return f"${x:,.6f}"
    if x < 1:
        return f"${x:,.4f}"
    return f"${x:,.2f}"


def _price_row(model: str) -> dict[str, float]:
    if model in PRICES:
        return PRICES[model]
    # Unknown id: bill at mid-tier so the ledger still prints something.
    print(f"  (no rate-card row for {model!r}; costing as claude-sonnet-5)")
    return PRICES["claude-sonnet-5"]


def cost(model: str, inp: int = 0, out: int = 0, cache_w: int = 0, cache_r: int = 0) -> float:
    """USD for one call from already-normalised token buckets."""
    p = _price_row(model)
    return (inp * p["inp"] + out * p["out"] + cache_w * p["cw"] + cache_r * p["cr"]) / 1e6


def cost_usage(model: str, usage: UsageNorm) -> float:
    return cost(
        model,
        inp=usage.fresh_input,
        out=usage.output,
        cache_w=usage.cache_write,
        cache_r=usage.cache_read,
    )


def normalize_usage(
    provider: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_creation: int = 0,
    cache_read: int = 0,
) -> UsageNorm:
    """Put both vendors onto the same four buckets.

    Anthropic: input / cache_creation / cache_read are *disjoint*.
    OpenAI:    cached_tokens is a *subset* of prompt_tokens — subtract it
               or you double-count. There is no cache-write premium.
    """
    if provider == "openai":
        cached = cache_read or 0
        return UsageNorm(
            fresh_input=max(0, (input_tokens or 0) - cached),
            output=output_tokens or 0,
            cache_write=0,
            cache_read=cached,
        )
    return UsageNorm(
        fresh_input=input_tokens or 0,
        output=output_tokens or 0,
        cache_write=cache_creation or 0,
        cache_read=cache_read or 0,
    )


def cache_breakeven(model: str) -> float:
    p = _price_row(model)
    denom = p["inp"] - p["cr"]
    if denom <= 0:
        return float("inf")
    return 1 + (p["cw"] - p["inp"]) / denom


def forecast(
    model: str,
    requests_per_month: int,
    tokens_in: int,
    tokens_out: int,
    agent_steps: int = 1,
    cache_hit_rate: float = 0.0,
    context_multiplier: float = 1.0,
    retry_rate: float = 0.0,
    verbose: bool = True,
) -> tuple[float, float]:
    """Monthly cost. agent_steps>1 re-reads growing context (triangular)."""
    step_factor = agent_steps * (agent_steps + 1) / 2 if agent_steps > 1 else 1
    total_in = tokens_in * step_factor
    total_out = tokens_out * agent_steps
    cached_in = total_in * cache_hit_rate
    fresh_in = total_in - cached_in
    per_task = cost(model, inp=fresh_in, out=total_out, cache_r=cached_in)
    per_task *= context_multiplier * (1 + retry_rate)
    monthly = per_task * requests_per_month
    if verbose:
        print(f"  model            {model}")
        print(f"  input tokens     {total_in:,.0f}  ({fresh_in:,.0f} fresh / {cached_in:,.0f} cached)")
        print(f"  output tokens    {total_out:,.0f}")
        print(f"  cost per task    {usd(per_task)}")
        print(f"  MONTHLY          {usd(monthly)}")
    return monthly, per_task


def log_call(
    label: str,
    model: str,
    inp: int = 0,
    out: int = 0,
    cache_w: int = 0,
    cache_r: int = 0,
    note: str = "",
) -> float:
    c = cost(model, inp, out, cache_w, cache_r)
    LEDGER.append(
        dict(
            label=label,
            model=model,
            input=inp,
            output=out,
            cache_write=cache_w,
            cache_read=cache_r,
            usd=c,
            note=note,
        )
    )
    print(
        f"{label:<42} {usd(c):>12}   "
        f"in={inp:<7} out={out:<6} cw={cache_w:<7} cr={cache_r:<7} {note}"
    )
    return c


def ledger() -> pd.DataFrame:
    df = pd.DataFrame(LEDGER)
    if df.empty:
        print("no calls yet")
        return df
    offline = df.note.astype(str).str.contains("placeholder")
    print(f"\nTOTAL SPENT IN THIS NOTEBOOK: {usd(df.usd[~offline].sum())}")
    if offline.any():
        print(f"({offline.sum()} placeholder rows are estimates only, "
              f"{usd(df.usd[offline].sum())} that was never actually spent)")
    return df


def reset_ledger() -> None:
    LEDGER.clear()


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------
def ntok(text: str) -> int:
    import tiktoken

    enc = tiktoken.get_encoding("o200k_base")
    return len(enc.encode(text))


def vendor_tokens(text: str, model: str | None = None) -> tuple[int | None, str]:
    """Count tokens the way the live provider will bill them.

    Anthropic has a free count_tokens endpoint; tiktoken is OpenAI's own
    tokenizer, so for OpenAI it is already the right answer. Offline we
    return (None, reason) rather than pretend.
    """
    _ensure_boot()
    if PROVIDER == "anthropic" and _CLIENT is not None:
        try:
            r = _CLIENT.messages.count_tokens(
                model=model or MODELS.mid,
                messages=[{"role": "user", "content": text}],
            )
            # count_tokens includes a few tokens of message framing.
            return int(r.input_tokens), "anthropic count_tokens (includes message framing)"
        except Exception as exc:  # noqa: BLE001
            return None, f"count_tokens failed: {type(exc).__name__}"
    if PROVIDER == "openai":
        return ntok(text), "tiktoken o200k_base (OpenAI's own encoding)"
    return None, "offline: no provider to ask"


def token_pieces(text: str) -> list[str]:
    import tiktoken

    enc = tiktoken.get_encoding("o200k_base")
    return [enc.decode([t]) for t in enc.encode(text)]


# ---------------------------------------------------------------------------
# Provider / env
# ---------------------------------------------------------------------------
def _load_env() -> None:
    here = Path(__file__).resolve().parent
    for candidate in (here / ".env", here.parent / ".env", Path.cwd() / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=False)


def _key(name: str) -> str:
    return (os.environ.get(name) or "").strip()


def detect_provider() -> str | None:
    """Return 'openai', 'anthropic', or None when no key is configured.

    None is a valid teaching mode: tokenizer and forecast cells still run.
    """
    explicit = (_key("LLM_PROVIDER") or "").lower()
    has_ant = bool(_key("ANTHROPIC_API_KEY"))
    has_oai = bool(_key("OPENAI_API_KEY"))
    if explicit in {"openai", "anthropic"}:
        if explicit == "openai" and not has_oai:
            print("LLM_PROVIDER=openai but OPENAI_API_KEY is empty — offline mode.")
            return None
        if explicit == "anthropic" and not has_ant:
            print("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is empty — offline mode.")
            return None
        return explicit
    if has_ant:
        return "anthropic"
    if has_oai:
        return "openai"
    return None


def _tier_models(provider: str) -> Any:
    defaults = DEFAULT_TIERS[provider]
    return type(
        "Models",
        (),
        {
            "floor": _key("MODEL_FLOOR") or defaults["floor"],
            "mid": _key("MODEL_MID") or defaults["mid"],
            "frontier": _key("MODEL_FRONTIER") or defaults["frontier"],
        },
    )()


def parse_openai_response(raw: Any, model: str) -> Result:
    u = raw.usage
    details = getattr(u, "prompt_tokens_details", None)
    cached = int(getattr(details, "cached_tokens", 0) or 0) if details else 0
    cdet = getattr(u, "completion_tokens_details", None)
    reasoning = int(getattr(cdet, "reasoning_tokens", 0) or 0) if cdet else 0
    text = raw.choices[0].message.content or ""
    norm = normalize_usage(
        "openai",
        input_tokens=int(u.prompt_tokens or 0),
        output_tokens=int(u.completion_tokens or 0),
        cache_read=cached,
    )
    return Result(
        text=text,
        model=model,
        input_tokens=int(u.prompt_tokens or 0),
        output_tokens=norm.output,
        fresh_input=norm.fresh_input,
        cache_write=0,
        cache_read=norm.cache_read,
        usd=cost_usage(model, norm),
        reasoning_tokens=reasoning,
        raw=raw,
    )


def parse_anthropic_response(raw: Any, model: str) -> Result:
    u = raw.usage
    # Newer Claude models can return a thinking block before the text, so
    # never assume content[0] is the answer.
    text = "".join(
        getattr(b, "text", "") for b in raw.content if getattr(b, "type", "") == "text"
    )
    cw = int(getattr(u, "cache_creation_input_tokens", 0) or 0)
    cr = int(getattr(u, "cache_read_input_tokens", 0) or 0)
    norm = normalize_usage(
        "anthropic",
        input_tokens=int(u.input_tokens or 0),
        output_tokens=int(u.output_tokens or 0),
        cache_creation=cw,
        cache_read=cr,
    )
    return Result(
        text=text,
        model=model,
        input_tokens=int(u.input_tokens or 0),
        output_tokens=norm.output,
        fresh_input=norm.fresh_input,
        cache_write=norm.cache_write,
        cache_read=norm.cache_read,
        usd=cost_usage(model, norm),
        raw=raw,
    )


def _make_client(provider: str):
    if provider == "anthropic":
        import anthropic

        return anthropic.Anthropic()
    import openai

    return openai.OpenAI()


def boot(*, reset: bool = True) -> Config:
    """Call once at the top of every notebook."""
    global PROVIDER, MODELS, _CLIENT, _BOOTED
    _load_env()
    if reset:
        reset_ledger()
    PROVIDER = detect_provider()
    live = PROVIDER is not None
    # Default the rate-card / forecast labels even in offline mode.
    tiers = _tier_models(PROVIDER or "anthropic")
    # Mutate in place so `from coursekit import MODELS` keeps working after boot.
    MODELS.floor, MODELS.mid, MODELS.frontier = tiers.floor, tiers.mid, tiers.frontier
    _CLIENT = _make_client(PROVIDER) if live else None
    _BOOTED = True

    # Make pandas tables readable from the back row.
    pd.set_option("display.max_colwidth", 88)
    pd.set_option("display.width", 120)

    print("=" * 64)
    if live:
        print(f"  Provider : {PROVIDER}")
        print(f"  floor    : {MODELS.floor}")
        print(f"  mid      : {MODELS.mid}")
        print(f"  frontier : {MODELS.frontier}")
        if PROVIDER == "anthropic":
            print("  Cache    : explicit cache_control; read/write are separate buckets.")
        else:
            print("  Cache    : automatic prefix cache; cached_tokens ⊂ prompt_tokens.")
        print("Switch with LLM_PROVIDER=openai or LLM_PROVIDER=anthropic in .env")
    else:
        print("  Provider : none (offline)")
        print("  Arithmetic cells still run. Cells that need a model print a placeholder.")
        print("  Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env for live calls.")
    print("  Rate card: verified 5 Sep 2026 — re-check before presenting.")
    print("=" * 64)
    return Config(provider=PROVIDER or "offline", models=MODELS, live=live)


def _ensure_boot() -> None:
    if not _BOOTED:
        boot()


def _anthropic_complete(
    prompt: str,
    *,
    system: str | None,
    model: str,
    max_tokens: int,
    cache: bool,
) -> Result:
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        if cache:
            kwargs["system"] = [
                {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}
            ]
        else:
            kwargs["system"] = system
    # Sonnet 5 and Opus 5 think by default. Thinking is billed as output and eats
    # into max_tokens, which makes the small, cheap calls in these labs come back
    # truncated. Switch it off where the model allows; remember models that refuse.
    if model not in _NO_THINKING_OFF:
        try:
            raw = _CLIENT.messages.create(**kwargs, thinking={"type": "disabled"})
            return parse_anthropic_response(raw, model)
        except Exception as exc:  # noqa: BLE001
            if "thinking" not in str(exc).lower():
                raise
            _NO_THINKING_OFF.add(model)
    raw = _CLIENT.messages.create(**kwargs)
    return parse_anthropic_response(raw, model)


def _openai_complete(
    prompt: str,
    *,
    system: str | None,
    model: str,
    max_tokens: int,
    cache: bool,
) -> Result:
    # cache=True is a no-op on OpenAI: prefix caching is automatic above ~1024 tokens.
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Current OpenAI models want max_completion_tokens; older ones want max_tokens.
    # Reasoning models also spend hidden reasoning tokens out of that same budget,
    # so we ask for the lowest reasoning effort the model accepts. Whatever works
    # is remembered per model so we only pay for the discovery once.
    opts = _OPENAI_OPTS.get(model)
    candidates = [opts] if opts else [
        {"limit": "max_completion_tokens", "reasoning_effort": "none"},
        {"limit": "max_completion_tokens", "reasoning_effort": "minimal"},
        {"limit": "max_completion_tokens", "reasoning_effort": None},
        {"limit": "max_tokens", "reasoning_effort": None},
    ]
    last_exc: Exception | None = None
    for c in candidates:
        kwargs: dict[str, Any] = {"model": model, "messages": messages, c["limit"]: max_tokens}
        if c["reasoning_effort"]:
            kwargs["reasoning_effort"] = c["reasoning_effort"]
        try:
            raw = _CLIENT.chat.completions.create(**kwargs)
        except Exception as exc:  # noqa: BLE001
            msg = str(exc).lower()
            if "unsupported" in msg or "reasoning_effort" in msg or "max_tokens" in msg:
                last_exc = exc
                continue
            raise
        _OPENAI_OPTS[model] = c
        result = parse_openai_response(raw, model)
        if not result.text and result.reasoning_tokens:
            print(f"  (note: {result.reasoning_tokens} hidden reasoning tokens used the whole "
                  f"max_tokens={max_tokens} budget, so the visible answer is empty)")
        return result
    assert last_exc is not None
    raise last_exc


def _fallback_result(prompt: str, model: str, system: str | None) -> Result:
    approx_in = ntok((system or "") + prompt)
    approx_out = 80
    return Result(
        text="[offline placeholder: no model was called, so there is no real answer here]",
        model=model,
        input_tokens=approx_in,
        output_tokens=approx_out,
        fresh_input=approx_in,
        usd=cost(model, inp=approx_in, out=approx_out),
        fallback=True,
    )


def complete(
    prompt: str,
    *,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 150,
    cache: bool = False,
    label: str | None = None,
    note: str = "",
) -> Result:
    """One chat turn. Logs to the ledger when ``label`` is set.

    On API failure the notebook keeps going with a placeholder result unless
    ``DEMO_STRICT=1`` is set — so a 401 in the room does not kill the arc.
    """
    _ensure_boot()
    model = model or MODELS.mid
    if PROVIDER is None or _CLIENT is None:
        print("(offline: no API key, so this is a placeholder, not a model answer)")
        result = _fallback_result(prompt, model, system)
        if label:
            log_call(label, result.model, inp=result.fresh_input, out=result.output_tokens,
                     note="offline placeholder")
        return result
    try:
        if PROVIDER == "anthropic":
            result = _anthropic_complete(
                prompt, system=system, model=model, max_tokens=max_tokens, cache=cache
            )
        else:
            result = _openai_complete(
                prompt, system=system, model=model, max_tokens=max_tokens, cache=cache
            )
    except Exception as exc:
        # Print the type and status only: provider error text can echo part of the key.
        status = getattr(exc, "status_code", None)
        print(f"⚠ API call failed: {type(exc).__name__}" + (f" (HTTP {status})" if status else ""))
        if os.environ.get("DEMO_STRICT"):
            raise
        print("  Continuing with a placeholder so the rest of the notebook still runs.")
        result = _fallback_result(prompt, model, system)

    if label:
        if result.fallback:
            note = "failed-call placeholder"
        hit = "CACHE HIT" if result.cache_read else note
        log_call(
            label,
            result.model,
            inp=result.fresh_input,
            out=result.output_tokens,
            cache_w=result.cache_write,
            cache_r=result.cache_read,
            note=hit or note,
        )
    return result


def show(obj: Any) -> None:
    try:
        from IPython.display import display

        display(obj)
    except Exception:
        print(obj)


# Keep notebooks importable even when run as `python coursekit.py` for a sanity check.
if __name__ == "__main__":
    print("coursekit ok")
    print("models in rate card:", len(PRICES))
    print("107x check:", round(cost("gpt-6-astra", 800_000_000, 200_000_000) / cost("deepseek-v4-flash", 800_000_000, 200_000_000), 1))
