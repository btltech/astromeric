"""Utility helpers for Gemini Flash explanations."""

from __future__ import annotations

import os
from typing import Any, List, Optional

from .interpretation import rank_interpretation_signals, select_practical_tip

try:
    from google import genai
except ImportError:  # pragma: no cover - handled gracefully at runtime
    genai = None  # type: ignore


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
            "You are Gemini Flash, a friendly astrology helper.",
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
            "You are Gemini Flash, helping explain an astrology + numerology reading in upbeat, plain language.",
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


def explain_with_gemini(
    scope: str,
    headline: Optional[str],
    theme: Optional[str],
    sections: List[dict],
    numerology: Optional[str],
    simple_language: bool = True,
) -> Optional[str]:
    client = create_gemini_client()
    if client is None:
        return None

    import logging

    _log = logging.getLogger(__name__)

    prompt = build_prompt(scope, headline, theme, sections, numerology, simple_language)
    try:
        response = client.models.generate_content(
            model=_get_model_name(),
            contents=prompt,
        )
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
        return result
    except Exception as e:
        _log.warning("Gemini call failed: %s: %s", type(e).__name__, str(e))
        return None
    finally:
        close_gemini_client(client)


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
