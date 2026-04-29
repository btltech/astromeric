"""
do_dont.py
----------
Generates personalized daily Do's and Don'ts based on:
- Current transit aspects to natal chart
- Personal day numerology
- Moon phase
- Venus/Mercury retrograde status
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ──────────────────────────────────────────────────────────────
#  Transit-aware Do / Don't libraries
# ──────────────────────────────────────────────────────────────

_ASPECT_DOS: Dict[str, List[str]] = {
    "Sun_conjunction": [
        "Set bold intentions",
        "Take centre stage",
        "Announce big decisions",
    ],
    "Sun_trine": [
        "Trust your instincts",
        "Start creative projects",
        "Share your ideas freely",
    ],
    "Sun_square": [
        "Channel frustration into focus",
        "Double-check before acting",
        "Seek outside perspective",
    ],
    "Sun_opposition": [
        "Listen before speaking",
        "Find the middle ground",
        "Collaborate rather than compete",
    ],
    "Moon_conjunction": [
        "Honour your feelings",
        "Spend time with close ones",
        "Journal your inner world",
    ],
    "Moon_trine": [
        "Make intuitive decisions",
        "Nurture relationships",
        "Practise self-care",
    ],
    "Moon_square": [
        "Pause before reacting emotionally",
        "Breathe before big conversations",
        "Set healthy limits",
    ],
    "Moon_opposition": [
        "Acknowledge both sides of how you feel",
        "Talk it out with a trusted friend",
    ],
    "Mercury_conjunction": [
        "Sign agreements",
        "Have important conversations",
        "Study or learn something new",
    ],
    "Mercury_trine": [
        "Write, pitch, or present your ideas",
        "Network and reach out",
        "Read and research",
    ],
    "Mercury_square": [
        "Re-read messages before sending",
        "Confirm appointments in advance",
        "Back up your data",
    ],
    "Mercury_opposition": [
        "Listen more than you speak",
        "Seek clarity before concluding",
    ],
    "Venus_conjunction": [
        "Schedule date nights",
        "Buy something beautiful",
        "Express affection openly",
    ],
    "Venus_trine": [
        "Smooth over old tensions",
        "Enjoy art or music",
        "Tell people you appreciate them",
    ],
    "Venus_square": ["Avoid impulse purchases", "Address relationship friction calmly"],
    "Mars_conjunction": [
        "Start new fitness routines",
        "Tackle the hardest task first",
        "Assert your needs clearly",
    ],
    "Mars_trine": [
        "Push towards ambitious goals",
        "Move your body",
        "Take decisive action",
    ],
    "Mars_square": [
        "Avoid confrontations",
        "Redirect aggression into exercise",
        "Take short breaks to release tension",
    ],
    "Jupiter_trine": [
        "Think bigger",
        "Apply for opportunities",
        "Be generous with your time",
    ],
    "Saturn_trine": [
        "Make long-term plans",
        "Commit to new disciplines",
        "Review your progress",
    ],
    "Saturn_square": [
        "Be patient with delays",
        "Strengthen your structures",
        "Accept reality as a teacher",
    ],
}

_ASPECT_DONTS: Dict[str, List[str]] = {
    "Sun_square": [
        "Force outcomes",
        "Skip steps to gain speed",
        "Make solo decisions that affect others",
    ],
    "Sun_opposition": ["Go it alone", "Dismiss other people's needs", "Over-promise"],
    "Moon_square": [
        "Make major choices when upset",
        "Suppress what you're feeling",
        "Isolate yourself",
    ],
    "Moon_opposition": [
        "Project emotions onto others",
        "Avoid the conversation you need to have",
    ],
    "Mercury_square": [
        "Sign documents without reading",
        "Assume you were understood",
        "Spread unverified rumours",
    ],
    "Mercury_opposition": ["Argue just to win", "Send that heated email"],
    "Venus_square": [
        "Spend to fill an emotional gap",
        "Issue ultimatums in relationships",
    ],
    "Mars_square": [
        "React impulsively",
        "Start fights you can't finish",
        "Push through injury or exhaustion",
    ],
    "Saturn_square": [
        "Cut corners on important commitments",
        "Resist helpful feedback",
        "Rush milestones",
    ],
}

# Personal-day mapped guidance
_PERSONAL_DAY_DOS: Dict[int, str] = {
    1: "Launch the project you've been postponing",
    2: "Collaborate — two heads beat one today",
    3: "Express yourself creatively — write, draw, speak",
    4: "Organise your workspace and make a concrete plan",
    5: "Try something outside your routine",
    6: "Give your time to someone who needs support",
    7: "Meditate, rest, or spend time in nature",
    8: "Make the bold financial or career move",
    9: "Reflect on what you're ready to release",
}

_PERSONAL_DAY_DONTS: Dict[int, str] = {
    1: "Wait for permission — you already have it",
    2: "Make solo decisions that affect shared outcomes",
    3: "Overthink — your first creative instinct is right",
    4: "Procrastinate — the work builds your future",
    5: "Stay rigidly in comfort; the day wants movement",
    6: "Neglect your own needs while caring for others",
    7: "Make major external decisions — this is inner time",
    8: "Undersell yourself or settle for less",
    9: "Cling to what's already ended",
}

# Moon-phase guidance
_MOON_PHASE_DOS: Dict[str, str] = {
    "New Moon": "Set your intentions for the next 28 days",
    "Waxing Crescent": "Take one small action toward your goal",
    "First Quarter": "Push past resistance — momentum is building",
    "Waxing Gibbous": "Refine and perfect what you've been building",
    "Full Moon": "Celebrate progress and release what no longer serves you",
    "Waning Gibbous": "Share your wisdom and express gratitude",
    "Last Quarter": "Forgive, let go, and make space for the new",
    "Waning Crescent": "Rest, reflect, and prepare for the cycle to begin again",
}

_MOON_PHASE_DONTS: Dict[str, str] = {
    "New Moon": "Start big projects without clear intention",
    "Full Moon": "Make permanent decisions in a highly emotional state",
    "Last Quarter": "Begin major new ventures — this is completion energy",
    "Waning Crescent": "Overextend yourself — conserve your energy",
}


def build_do_dont(
    natal_chart: Optional[Dict] = None,
    transit_chart: Optional[Dict] = None,
    personal_day: int = 5,
    moon_phase: str = "Waxing Crescent",
    is_mercury_retrograde: bool = False,
    is_venus_retrograde: bool = False,
    lang: str = "en",
) -> Dict[str, Any]:
    """
    Generate 3 Do's and 3 Don'ts for the day.

    Priority order:
    1. Tight transit aspects to natal chart (orb ≤ 2°)
    2. Retrograde warnings (Mercury/Venus)
    3. Personal day numerology
    4. Moon phase

    Returns at least 3 dos and 3 don'ts regardless of transit data availability.
    """
    dos: List[str] = []
    donts: List[str] = []

    # 1. Transit aspects
    if natal_chart and transit_chart:
        try:
            from ..transit_alerts import find_transit_aspects

            aspects = find_transit_aspects(natal_chart, transit_chart)
            tight_aspects = [a for a in aspects if a["orb"] <= 2.0][:6]
            for asp in tight_aspects:
                key = f"{asp['transit_planet']}_{asp['aspect']}"
                if key in _ASPECT_DOS and len(dos) < 4:
                    dos.extend(_ASPECT_DOS[key][:1])
                if key in _ASPECT_DONTS and len(donts) < 4:
                    donts.extend(_ASPECT_DONTS[key][:1])
        except Exception:
            pass  # Graceful degradation

    # 2. Retrograde warnings
    if is_mercury_retrograde:
        if len(donts) < 4:
            donts.append("Sign contracts or make major communications decisions")
        if len(dos) < 4:
            dos.append("Revisit unfinished projects from the past")

    if is_venus_retrograde:
        if len(donts) < 4:
            donts.append("Start significant new relationships or make big purchases")
        if len(dos) < 4:
            dos.append("Reconnect with an old friend or creative passion")

    # 3. Personal day numerology
    if len(dos) < 3 and personal_day in _PERSONAL_DAY_DOS:
        dos.append(_PERSONAL_DAY_DOS[personal_day])
    if len(donts) < 3 and personal_day in _PERSONAL_DAY_DONTS:
        donts.append(_PERSONAL_DAY_DONTS[personal_day])

    # 4. Moon phase
    if len(dos) < 3 and moon_phase in _MOON_PHASE_DOS:
        dos.append(_MOON_PHASE_DOS[moon_phase])
    if len(donts) < 3 and moon_phase in _MOON_PHASE_DONTS:
        donts.append(_MOON_PHASE_DONTS[moon_phase])

    # 5. Always-on fallback pool to guarantee we return exactly 3+3
    _fallback_dos = [
        "Take one mindful breath before each task",
        "Drink water and move your body",
        "Notice three things you're grateful for",
        "Respond rather than react today",
        "Focus on progress, not perfection",
    ]
    _fallback_donts = [
        "Scroll social media first thing in the morning",
        "Judge yourself for feeling what you feel",
        "Compare your chapter 1 to someone else's chapter 20",
        "Put off a conversation that needs to happen",
        "Skip your midday break",
    ]

    fallback_do_idx = 0
    while len(dos) < 3 and fallback_do_idx < len(_fallback_dos):
        candidate = _fallback_dos[fallback_do_idx]
        if candidate not in dos:
            dos.append(candidate)
        fallback_do_idx += 1

    fallback_dont_idx = 0
    while len(donts) < 3 and fallback_dont_idx < len(_fallback_donts):
        candidate = _fallback_donts[fallback_dont_idx]
        if candidate not in donts:
            donts.append(candidate)
        fallback_dont_idx += 1

    return {
        "dos": dos[:3],
        "donts": donts[:3],
        "personal_day": personal_day,
        "moon_phase": moon_phase,
        "mercury_retrograde": is_mercury_retrograde,
        "venus_retrograde": is_venus_retrograde,
    }
