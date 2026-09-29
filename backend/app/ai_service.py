"""AI text generation for readings and the Cosmic Guide.

NVIDIA's hosted API is tried first; Gemini is the fallback when NVIDIA is not
configured or fails. Callers get ``None`` when neither answers and then use their
own built-in fallback text.
"""

from __future__ import annotations

import hmac
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, List, Optional

import httpx
from fastapi import Request

from .interpretation import rank_interpretation_signals, select_practical_tip


def _get_ai_access_code() -> str | None:
    code = os.getenv("AI_ACCESS_CODE", "").strip()
    return code or None


def has_ai_access(request: Request) -> bool:
    """Return True only for callers holding the private AI access code.

    Gemini runs on an unpaid key whose prompts Google may use to improve its
    products, so it is reserved for the owner's own device: the code is typed in
    once there and is never shipped in the app. Every other caller falls back to
    the built-in responses, and their questions and chart data never leave us.
    """
    expected = _get_ai_access_code()
    if not expected:
        return False
    return hmac.compare_digest(request.headers.get("x-ai-access", ""), expected)


def is_native_ios(request: Request) -> bool:
    """Return True only for requests originating from the native iOS app.

    Two signals are checked (either is sufficient):
    - ``X-Client-Platform: ios`` header set by APIClient.swift
    - ``CFNetwork`` in the User-Agent (URLSession fingerprint, browsers cannot spoof this)
    """
    if request.headers.get("x-client-platform", "").lower() == "ios":
        return True
    ua = request.headers.get("user-agent", "")
    return "CFNetwork" in ua


def is_native_android(request: Request) -> bool:
    """Return True only for requests originating from the native Android app.

    Checks for the ``X-Client-Platform: android`` header injected by the
    OkHttpClient platform interceptor in AstroRemoteData.
    """
    return request.headers.get("x-client-platform", "").lower() == "android"


def is_native_app(request: Request) -> bool:
    """Return True for any native mobile app (iOS or Android)."""
    return is_native_ios(request) or is_native_android(request)


try:
    from google import genai
except ImportError:  # pragma: no cover - handled gracefully at runtime
    genai = None  # type: ignore


_log = logging.getLogger(__name__)


def _get_model_name() -> str:
    """Get model name, stripping any 'models/' prefix."""
    name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    # Gemini SDK adds 'models/' prefix, so strip if provided
    return name.removeprefix("models/")


def _get_api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY")


def _configure_client() -> bool:
    return bool(genai and _get_api_key())


def create_gemini_client() -> Any | None:
    if not _configure_client():
        return None
    return genai.Client(api_key=_get_api_key())


def close_gemini_client(client: Any) -> None:
    close = getattr(client, "close", None)
    if callable(close):
        close()


def extract_gemini_text(response: Any) -> Optional[str]:
    text = getattr(response, "text", None)
    if text:
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            maybe = getattr(part, "text", None)
            if maybe:
                return maybe.strip()

    return None


def build_prompt(
    scope: str,
    headline: Optional[str],
    theme: Optional[str],
    sections: List[dict],
    numerology: Optional[str],
    simple_language: bool = True,
) -> str:
    if simple_language:
        # Ultra-simple mode: 5th grade reading level, everyday words
        parts = [
            "You are a friendly astrology helper.",
            "Explain this reading like you're talking to a friend who knows nothing about astrology.",
            "Use only simple, everyday words. No astrology terms.",
            "Keep sentences short. One idea per sentence.",
            "Output MUST be Markdown.",
            "Keep it short (100-150 words max).",
            "Use this structure:",
            "### What This Means\n1-2 simple sentences.",
            "### Good Things Coming\n- 2-3 bullets (each <= 10 words, very simple).",
            "### One Thing To Do\n- 1 bullet, super practical and easy.",
            "Do not use words like: transit, conjunction, aspect, retrograde, house, rising, ascendant.",
            "Instead say things like: 'good energy for love' or 'great day to start projects'.",
            f"Scope: {scope}.",
        ]
    else:
        # Original mode: still plain language but allows some astrology context
        parts = [
            "You are a friendly astrology helper explaining an astrology + numerology reading in upbeat, plain language.",
            "Write for a normal person (no jargon).",
            "Output MUST be Markdown.",
            "Keep it short (120-180 words max).",
            "Use this structure:",
            "### TL;DR\n1 sentence.",
            "### Key takeaways\n- 2-4 bullets (each <= 12 words).",
            "### One practical tip\n- 1 bullet, actionable.",
            "### Numerology insight\n- 1 bullet (only if numerology provided).",
            "Do not mention APIs, providers, or that you're an AI.",
            f"Scope: {scope}.",
        ]
    if headline:
        parts.append(f"Headline: {headline}.")
    if theme:
        parts.append(f"Theme: {theme}.")
    for section in sections[:4]:
        title = section.get("title") or "General"
        highlights = "; ".join(section.get("highlights", [])[:3])
        if highlights:
            parts.append(f"Section {title}: {highlights}.")
    if numerology:
        parts.append(f"Numerology insight: {numerology}.")
    parts.append("Avoid repeating raw data verbatim; synthesize it.")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# NVIDIA (OpenAI-compatible chat completions)
# ---------------------------------------------------------------------------

NVIDIA_DEFAULT_URL = "https://integrate.api.nvidia.com/v1"
# The 120B Super model answers in 1-4s; the 550B Ultra took 11-15s, too slow for
# requests a person is waiting on.
NVIDIA_DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b"
NVIDIA_TIMEOUT_SECONDS = 20.0
# NVIDIA's free tier often answers "busy" with a 5xx; one retry usually lands.
NVIDIA_RETRY_STATUSES = frozenset({500, 502, 503, 504})
NVIDIA_RETRY_DELAY_SECONDS = 2.0
DEFAULT_MAX_TOKENS = 1024

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_THINK_CLOSE = re.compile(r"</think>", re.IGNORECASE)


@dataclass(frozen=True)
class AIText:
    """Text from a hosted model, with which provider and model produced it."""

    text: str
    provider: str  # "nvidia" or "gemini"
    model: str


def _get_nvidia_api_key() -> str | None:
    key = os.getenv("NVIDIA_API_KEY", "").strip()
    return key or None


def _get_nvidia_model() -> str:
    return os.getenv("NVIDIA_MODEL", "").strip() or NVIDIA_DEFAULT_MODEL


def _get_nvidia_url() -> str:
    base = os.getenv("NVIDIA_API_URL", "").strip() or NVIDIA_DEFAULT_URL
    return base.rstrip("/") + "/chat/completions"


def strip_thinking(text: Optional[str]) -> Optional[str]:
    """Drop any reasoning the model wrote into its answer.

    Removes whole ``<think>...</think>`` blocks, then anything before a stray
    closing ``</think>`` (the opening tag is sometimes left out).
    """
    if not text:
        return None
    cleaned = _THINK_BLOCK.sub("", text)
    parts = _THINK_CLOSE.split(cleaned)
    cleaned = parts[-1].strip()
    return cleaned or None


def ai_configured() -> bool:
    """True when at least one hosted provider could be tried."""
    return bool(_get_nvidia_api_key()) or _configure_client()


def _nvidia_generate(
    prompt: str, system: Optional[str], max_tokens: int
) -> Optional[AIText]:
    api_key = _get_nvidia_api_key()
    if not api_key:
        return None

    model = _get_nvidia_model()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": False,
        # Without this Nemotron writes its reasoning into the answer.
        "chat_template_kwargs": {"enable_thinking": False},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        with httpx.Client(timeout=NVIDIA_TIMEOUT_SECONDS) as client:
            response = client.post(_get_nvidia_url(), json=body, headers=headers)
            if response.status_code in NVIDIA_RETRY_STATUSES:
                _log.info("NVIDIA answered %s; retrying once", response.status_code)
                time.sleep(NVIDIA_RETRY_DELAY_SECONDS)
                response = client.post(_get_nvidia_url(), json=body, headers=headers)
            if response.status_code != 200:
                _log.warning("NVIDIA call failed with HTTP %s", response.status_code)
                return None
            data = response.json()
        content = data["choices"][0]["message"].get("content")
    except Exception as e:
        _log.warning("NVIDIA call failed: %s: %s", type(e).__name__, str(e))
        return None

    text = strip_thinking(content if isinstance(content, str) else None)
    if not text:
        _log.warning("NVIDIA returned no usable text")
        return None
    return AIText(text=text, provider="nvidia", model=model)


def _gemini_generate(prompt: str, system: Optional[str]) -> Optional[AIText]:
    client = create_gemini_client()
    if client is None:
        return None

    # Gemini keeps the original single-message shape: the guide prompt is
    # prepended to the question rather than sent as a separate system turn.
    contents = f"{system}\n\nUser question: {prompt}" if system else prompt
    model = _get_model_name()
    try:
        response = client.models.generate_content(model=model, contents=contents)
        result = extract_gemini_text(response)
        if result is None:
            text_attr = getattr(response, "text", "NO_TEXT_ATTR")
            candidates = getattr(response, "candidates", [])
            finish_reasons = [
                getattr(c, "finish_reason", "?") for c in (candidates or [])
            ]
            _log.warning(
                "Gemini returned None text. text=%r, candidates=%d, finish_reasons=%s",
                text_attr,
                len(candidates or []),
                finish_reasons,
            )
            return None
        return AIText(text=result, provider="gemini", model=model)
    except Exception as e:
        _log.warning("Gemini call failed: %s: %s", type(e).__name__, str(e))
        return None
    finally:
        close_gemini_client(client)


def generate_ai_text(
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> Optional[AIText]:
    """Try NVIDIA, then Gemini. Return None when neither answers."""
    return _nvidia_generate(prompt, system, max_tokens) or _gemini_generate(
        prompt, system
    )


def generate_text(
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> Optional[str]:
    """Text-only form of :func:`generate_ai_text`."""
    result = generate_ai_text(prompt, system=system, max_tokens=max_tokens)
    return result.text if result else None


def explain_reading(
    scope: str,
    headline: Optional[str],
    theme: Optional[str],
    sections: List[dict],
    numerology: Optional[str],
    simple_language: bool = True,
) -> Optional[AIText]:
    prompt = build_prompt(scope, headline, theme, sections, numerology, simple_language)
    return generate_ai_text(prompt, max_tokens=512)


def explain_with_gemini(
    scope: str,
    headline: Optional[str],
    theme: Optional[str],
    sections: List[dict],
    numerology: Optional[str],
    simple_language: bool = True,
) -> Optional[str]:
    """Explain a reading with whichever provider answers (NVIDIA, then Gemini).

    The name is kept for existing callers.
    """
    result = explain_reading(
        scope, headline, theme, sections, numerology, simple_language
    )
    return result.text if result else None


def fallback_summary(
    headline: Optional[str], sections: List[dict], numerology: Optional[str]
) -> str:
    ranked = rank_interpretation_signals(
        sections, headline=headline, numerology=numerology
    )
    opening = headline or "Fresh opportunities are unfolding."

    bullets: List[str] = []
    seen_titles = set()
    for signal in ranked:
        title = signal.get("title") or "This area"
        if title in seen_titles and title != "Numerology":
            continue
        bullets.append(f"- {title} focus: {signal.get('summary')}")
        seen_titles.add(title)
        if len(bullets) == 2:
            break

    if not bullets:
        # Keep this exact phrase for existing tests.
        bullets.append("- Trust your instincts and keep plans flexible.")

    numerology_line = numerology or next(
        (
            signal.get("summary")
            for signal in ranked
            if signal.get("title") == "Numerology"
        ),
        "Lean into cooperation energy today.",
    )
    practical_tip = select_practical_tip(ranked, numerology)

    # Keep the exact substring "Numerology insight:" for existing tests.
    md = [
        "### TL;DR",
        opening,
        "",
        "### Key takeaways",
        *bullets,
        "",
        "### One practical tip",
        f"- {practical_tip}",
        "",
        "### Numerology insight:",
        f"- {numerology_line}",
    ]
    return "\n".join(md).strip()
