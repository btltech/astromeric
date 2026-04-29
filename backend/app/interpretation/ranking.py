"""Deterministic ranking helpers for chart and numerology interpretation signals."""

from __future__ import annotations

from typing import Dict, List, Optional

SECTION_WEIGHTS: Dict[str, float] = {
    "love": 1.15,
    "relationship": 1.15,
    "career": 1.1,
    "work": 1.1,
    "money": 1.05,
    "health": 1.0,
    "timing": 1.1,
    "chart": 1.15,
    "transit": 1.15,
    "numerology": 1.1,
    "profile": 0.65,
    "context": 0.8,
}

KEYWORD_WEIGHTS: Dict[str, float] = {
    "sun": 0.45,
    "moon": 0.45,
    "ascendant": 0.55,
    "rising": 0.55,
    "mercury": 0.35,
    "venus": 0.4,
    "mars": 0.4,
    "jupiter": 0.35,
    "saturn": 0.45,
    "uranus": 0.25,
    "neptune": 0.25,
    "pluto": 0.3,
    "retrograde": 0.55,
    "conjunction": 0.4,
    "square": 0.45,
    "trine": 0.35,
    "opposition": 0.45,
    "house": 0.25,
    "fortune": 0.35,
    "node": 0.35,
    "chiron": 0.35,
    "karmic": 0.5,
    "life path": 0.45,
    "expression": 0.35,
    "soul urge": 0.4,
    "personal year": 0.35,
    "personal month": 0.25,
    "personal day": 0.25,
}

PRACTICAL_TIPS = [
    (
        "retrograde",
        "Double-check the details, revise what is unfinished, and avoid rushing a hard commitment.",
    ),
    (
        "saturn",
        "Choose the disciplined option today. Structure will carry you further than mood.",
    ),
    (
        "mars",
        "Channel the heat into one clean action instead of scattering it across conflict.",
    ),
    (
        "venus",
        "Lead with warmth and clarity, especially in conversations that affect closeness or trust.",
    ),
    (
        "moon",
        "Make room for your emotional reality before you decide what anything means.",
    ),
    (
        "sun",
        "Back the part of you that feels most alive, even if it asks for more visibility.",
    ),
    (
        "jupiter",
        "Think one step bigger than usual, but keep the plan grounded in what you can actually execute.",
    ),
    (
        "karmic",
        "Notice the familiar pattern, interrupt it early, and choose the more conscious response.",
    ),
    (
        "life path",
        "Let today reflect your long-term path instead of chasing short-term noise.",
    ),
]


def _score_text(text: str) -> float:
    lowered = text.lower()
    score = 1.0
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword in lowered:
            score += weight
    return score


def rank_interpretation_signals(
    sections: List[dict],
    headline: Optional[str] = None,
    numerology: Optional[str] = None,
) -> List[dict]:
    """Rank sections/highlights so fallbacks can prioritize the strongest signals."""
    ranked: List[dict] = []

    for section in sections:
        title = (section.get("title") or "General").strip()
        highlights = section.get("highlights") or []
        title_weight = 1.0
        lowered_title = title.lower()
        for label, weight in SECTION_WEIGHTS.items():
            if label in lowered_title:
                title_weight = max(title_weight, weight)

        for highlight in highlights[:3]:
            text = str(highlight).strip()
            if not text:
                continue
            score = _score_text(text) * title_weight
            if headline and any(
                word in text.lower() for word in headline.lower().split()[:4]
            ):
                score += 0.25
            ranked.append(
                {
                    "title": title,
                    "summary": text,
                    "score": round(score, 3),
                }
            )

    if numerology:
        ranked.append(
            {
                "title": "Numerology",
                "summary": numerology,
                "score": round(
                    _score_text(numerology) * SECTION_WEIGHTS["numerology"], 3
                ),
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def select_practical_tip(
    ranked_signals: List[dict], numerology: Optional[str] = None
) -> str:
    """Choose an action-oriented tip based on the strongest available signal."""
    searchable = " ".join(signal.get("summary", "") for signal in ranked_signals[:3])
    if numerology:
        searchable = f"{searchable} {numerology}".strip()
    lowered = searchable.lower()

    for keyword, tip in PRACTICAL_TIPS:
        if keyword in lowered:
            return tip

    return "Pick one clear action, do it early, and let momentum build before doubt takes over."
