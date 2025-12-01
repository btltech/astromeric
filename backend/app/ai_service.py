"""Utility helpers for Gemini Flash explanations."""

from __future__ import annotations

import os
from typing import List, Optional

try:
    import google.generativeai as genai
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
    api_key = _get_api_key()
    if not genai or not api_key:
        return False
    # Configure once per process; repeated calls are harmless.
    genai.configure(api_key=api_key)
    return True


def build_prompt(
    scope: str,
    headline: Optional[str],
    theme: Optional[str],
    sections: List[dict],
    numerology: Optional[str],
) -> str:
    parts = [
        "You are Gemini Flash, helping explain an astrology + numerology reading in upbeat, plain language.",
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
    parts.append(
        "Produce 2-3 friendly sentences plus one practical tip. Avoid repeating raw data."
    )
    return "\n".join(parts)


def explain_with_gemini(
    scope: str,
    headline: Optional[str],
    theme: Optional[str],
    sections: List[dict],
    numerology: Optional[str],
) -> Optional[str]:
    if not _configure_client():
        return None

    prompt = build_prompt(scope, headline, theme, sections, numerology)
    model = genai.GenerativeModel(_get_model_name())
    response = model.generate_content(prompt)
    text = getattr(response, "text", None)
    if text:
        return text.strip()

    if response.candidates:
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    maybe = getattr(part, "text", None)
                    if maybe:
                        return maybe.strip()
    return None


def fallback_summary(
    headline: Optional[str], sections: List[dict], numerology: Optional[str]
) -> str:
    opening = headline or "Fresh opportunities are unfolding."
    section_bits: List[str] = []
    for section in sections[:2]:
        highlights = section.get("highlights") or []
        if not highlights:
            continue
        title = section.get("title") or "This area"
        section_bits.append(f"{title} focus: {highlights[0]}")

    if not section_bits:
        section_bits.append("Trust your instincts and keep plans flexible.")

    numerology_line = numerology or "Lean into cooperation energy today."
    return f"{opening} {' '.join(section_bits)} Numerology insight: {numerology_line}."
