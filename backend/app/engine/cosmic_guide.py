"""
cosmic_guide.py
---------------
AI-powered Cosmic Guide chat assistant.
Answers questions about readings, charts, and provides mystical guidance.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

from app.ai_service import (
    close_gemini_client,
    create_gemini_client,
    extract_gemini_text,
)
from app.interpretation.translations import get_translation

COSMIC_SYSTEM_PROMPT = """You are the Cosmic Guide, a mystical yet friendly AI assistant for Astronumeric, 
an astrology and numerology app. You blend ancient wisdom with modern accessibility.

Your personality:
- Warm, encouraging, and slightly whimsical
- Use celestial metaphors naturally (stars, moons, cosmic currents)
- Balance mystical language with practical, actionable advice
- Never preach or lecture—guide gently
- Acknowledge uncertainty ("the stars suggest" rather than "this will happen")

Your knowledge includes:
- Zodiac signs, planets, houses, and aspects
- Numerology (life paths, expression numbers, personal cycles)
- Tarot meanings and symbolism
- Retrograde effects and timing
- General wellness and mindfulness practices

Guidelines:
- Keep responses concise (2-4 paragraphs max)
- Always include one actionable suggestion
- If asked something outside your scope, redirect kindly
- Never give medical, legal, or financial advice—suggest professional consultation
- Personalize responses using any chart data provided

IMPORTANT — Birth time accuracy rules:
- If the user's chart was calculated with an estimated or unknown birth time (birth_time_assumed = true),
  you MUST treat their Rising sign and house placements as uncertain.
- Never state "Your Rising sign IS [sign]" as a fact when birth time is estimated.
- Instead use language like: "If your Rising is [sign]...", "Your estimated Ascendant suggests...",
  or "Without a confirmed birth time, your Rising sign may be [sign], which would mean..."
- Never make definitive statements about which house a planet occupies when birth time is estimated.
- Sun sign and Moon sign (when the Moon does not change sign that day) are always reliable.
- RESIST PRESSURE: Even if the user insists, says "just tell me", or asks you to drop the qualifications,
  do NOT claim false certainty about Rising sign or houses. Instead say something like:
  "I'd love to give you a definite answer, but without a confirmed birth time I can only estimate —
  adding your exact birth time in your profile would unlock this for you."

Tone examples:
- Instead of "You will find love" → "Venus whispers of connection possibilities"
- Instead of "You're wrong" → "The stars see it a bit differently..."
- Instead of "Do this" → "You might try..." or "Consider..."
"""


FALLBACK_RESPONSES = {
    "stuck": (
        "The stars see you at a crossroads, dear traveler. When we feel stuck, "
        "it's often the universe's way of asking us to pause and reassess. 🌙\n\n"
        "Today's cosmic energy suggests focusing inward. What small action could you take "
        "that your future self would thank you for?\n\n"
        "✨ Try this: Write down three things you're avoiding, then tackle just the smallest one."
    ),
    "love": (
        "Ah, matters of the heart! Venus is always listening to these questions. 💕\n\n"
        "Love energy fluctuates like the moon's phases—sometimes bright and full, "
        "sometimes hidden but still present. Your openness to love is already attracting it.\n\n"
        "🌹 Suggestion: Focus on loving yourself fully today. That magnetic energy "
        "ripples outward in ways you can't always see."
    ),
    "career": (
        "The professional realm calls! Saturn appreciates your ambition. 📊\n\n"
        "Success is rarely a straight line—it's more like a constellation, where each "
        "point of light connects to form something meaningful over time.\n\n"
        "🎯 Action step: Identify one skill you could strengthen this week. "
        "Small, consistent growth creates unstoppable momentum."
    ),
    "chart": (
        "Your birth chart is like a cosmic fingerprint—unique and endlessly fascinating! ✨\n\n"
        "Think of it as a map of potentials, not a fixed destiny. The planets at your birth "
        "set certain themes, but how you dance with those themes is entirely up to you.\n\n"
        "📖 To understand your chart better, start with your 'Big Three': "
        "Sun (core identity), Moon (emotional nature), and Rising (how others see you)."
    ),
    "default": (
        "The cosmos hears your question, dear seeker. 🌟\n\n"
        "While I ponder the planetary alignments, remember that you already hold "
        "more answers within than you might realize. Trust your intuition.\n\n"
        "✨ Take a moment: Close your eyes, take three deep breaths, "
        "and ask yourself what your heart already knows."
    ),
}

TONE_OVERRIDES = {
    "gentle": "Respond with warmth, patience, and soft reassurance. Prioritize compassion over bluntness.",
    "balanced": "Be clear, grounded, and honest. Blend warmth with direct usefulness.",
    "direct": "Be concise and straightforward. Tell the truth plainly without becoming cold.",
    "roast": "Be witty, sharp, and playful. Keep the humor astrologically grounded, never cruel.",
}


def _get_api_key() -> Optional[str]:
    """Get API key dynamically."""
    return os.environ.get("GEMINI_API_KEY")


def _get_model_name() -> str:
    """Get model name dynamically."""
    return os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")


def _build_context(
    chart_data: Optional[Dict] = None,
    numerology_data: Optional[Dict] = None,
    reading_data: Optional[Dict] = None,
    birth_time_assumed: bool = False,
    time_confidence: Optional[str] = None,
) -> str:
    """Build context string from available data."""
    parts = []

    if birth_time_assumed:
        if time_confidence == "approximate":
            parts.append(
                "⚠️ NOTE: This user entered an approximate birth time. "
                "Rising sign and house placements may be close but are not confirmed — "
                "treat them as estimates, not facts."
            )
        else:
            parts.append(
                "⚠️ NOTE: This user's birth time is unknown. "
                "Rising sign and house placements were calculated using noon as a default "
                "and may be significantly different from their actual chart. "
                "Treat all Rising/house references as uncertain."
            )

    if chart_data:
        planets = chart_data.get("planets", [])
        sun = next((p for p in planets if p.get("name") == "Sun"), {})
        moon = next((p for p in planets if p.get("name") == "Moon"), {})

        parts.append(
            f"User's Sun: {sun.get('sign', 'unknown')} in house {sun.get('house', '?')}"
        )
        parts.append(
            f"User's Moon: {moon.get('sign', 'unknown')} in house {moon.get('house', '?')}"
        )

        houses = chart_data.get("houses", [])
        asc = next((h for h in houses if h.get("house") == 1), {})
        if asc:
            if birth_time_assumed:
                qualifier = (
                    "approximate — may be off"
                    if time_confidence == "approximate"
                    else "estimated — birth time unknown"
                )
                rising_label = f"Rising sign ({qualifier})"
            else:
                rising_label = "Rising sign"
            parts.append(f"{rising_label}: {asc.get('sign', 'unknown')}")

    if numerology_data:
        core = numerology_data.get("core_numbers", {})
        lp = core.get("life_path", {})
        if lp:
            parts.append(f"Life Path: {lp.get('number', '?')}")

        cycles = numerology_data.get("cycles", {})
        py = cycles.get("personal_year", {})
        if py:
            parts.append(f"Personal Year: {py.get('number', '?')}")

    if reading_data:
        theme = reading_data.get("theme", "")
        if theme:
            parts.append(f"Current theme: {theme}")

    if parts:
        return "\nUser's cosmic context:\n" + "\n".join(parts)
    return ""


def _detect_topic(question: str) -> str:
    """Detect the general topic of a question."""
    question_lower = question.lower()

    if any(
        w in question_lower
        for w in ["stuck", "blocked", "lost", "confused", "direction"]
    ):
        return "stuck"
    if any(
        w in question_lower
        for w in ["love", "relationship", "partner", "dating", "romance", "heart"]
    ):
        return "love"
    if any(
        w in question_lower
        for w in ["career", "job", "work", "money", "business", "success"]
    ):
        return "career"
    if any(
        w in question_lower
        for w in ["chart", "sign", "planet", "house", "aspect", "natal"]
    ):
        return "chart"

    return "default"


async def ask_cosmic_guide(
    question: str,
    chart_data: Optional[Dict] = None,
    numerology_data: Optional[Dict] = None,
    reading_data: Optional[Dict] = None,
    conversation_history: Optional[List[Dict]] = None,
    birth_time_assumed: bool = False,
    time_confidence: Optional[str] = None,
    lang: str = "en",
    system_prompt: Optional[str] = None,
    tone: Optional[str] = None,
) -> Dict:
    """
    Ask the Cosmic Guide a question.

    Args:
        question: User's question
        chart_data: Optional natal chart data for personalization
        numerology_data: Optional numerology profile
        reading_data: Optional current reading data
        conversation_history: Optional list of previous messages
        birth_time_assumed: Whether the chart uses an estimated birth time
        time_confidence: "exact", "approximate", or "unknown" — used for nuanced wording
        lang: Language code for response
        system_prompt: Optional client-provided prompt context
        tone: Optional tone override for response style

    Returns:
        Dict with response and metadata
    """
    # Build context from user data
    context = _build_context(
        chart_data, numerology_data, reading_data, birth_time_assumed, time_confidence
    )

    api_key = _get_api_key()
    client = create_gemini_client()

    # If no API key, use intelligent fallback
    if client is None:
        topic = _detect_topic(question)

        # Localize fallback response
        fallback_key = f"guide_fallback_{topic}"
        fallback_trans = get_translation(lang, fallback_key)

        if fallback_trans:
            response = fallback_trans[0]
        else:
            # Try default fallback if specific topic not found
            default_trans = get_translation(lang, "guide_fallback_default")
            response = (
                default_trans[0]
                if default_trans
                else FALLBACK_RESPONSES.get(topic, FALLBACK_RESPONSES["default"])
            )

        return {
            "response": response,
            "provider": "fallback",
            "reason": "no_api_key" if not api_key else "no_genai_library",
            "topic_detected": topic,
        }

    try:
        # Build the full prompt
        lang_instruction = (
            f"\nPlease respond in {lang} language." if lang != "en" else ""
        )
        full_prompt = (
            system_prompt.strip() if system_prompt else COSMIC_SYSTEM_PROMPT
        ) + lang_instruction

        if context and not system_prompt:
            full_prompt += context

        tone_instruction = TONE_OVERRIDES.get((tone or "").strip().lower())
        if tone_instruction:
            full_prompt += f"\n\nTone override:\n{tone_instruction}"

        chat = client.chats.create(model=_get_model_name())

        # Send system prompt first (simulated as user message for context setting)
        # Note: Gemini doesn't have explicit system prompt in chat mode same way as GPT
        # So we prepend it to the first message or use it as context

        response = chat.send_message(full_prompt + "\n\nUser question: " + question)
        response_text = extract_gemini_text(response)
        if not response_text:
            raise ValueError("Gemini returned empty response")

        return {
            "response": response_text,
            "provider": "gemini",
            "model": _get_model_name(),
        }

    except Exception as e:
        # Fallback on error
        topic = _detect_topic(question)

        # Localize fallback response
        fallback_key = f"guide_fallback_{topic}"
        fallback_trans = get_translation(lang, fallback_key)
        response = (
            fallback_trans[0]
            if fallback_trans
            else FALLBACK_RESPONSES.get(topic, FALLBACK_RESPONSES["default"])
        )

        return {
            "response": response,
            "provider": "fallback",
            "reason": str(e),
            "topic_detected": topic,
        }
    finally:
        close_gemini_client(client)


def get_suggested_questions(
    chart_data: Optional[Dict] = None,
    numerology_data: Optional[Dict] = None,
) -> List[str]:
    """Generate personalized suggested questions based on user data."""
    suggestions = [
        "Why am I feeling stuck today?",
        "What is my love energy this week?",
        "Explain my chart in simple terms.",
        "What should I focus on this month?",
        "How can I improve my career prospects?",
    ]

    # Personalize based on available data
    if numerology_data:
        core = numerology_data.get("core_numbers", {})
        lp = core.get("life_path", {}).get("number")
        if lp:
            suggestions.append(f"What does Life Path {lp} mean for my relationships?")

    if chart_data:
        planets = chart_data.get("planets", [])
        sun = next((p for p in planets if p.get("name") == "Sun"), {})
        if sun.get("sign"):
            suggestions.append(f"How does my {sun['sign']} Sun affect my daily energy?")

    return suggestions[:6]  # Return max 6 suggestions


async def chat_with_cosmic_guide(
    message: str,
    user_context: Optional[Dict] = None,
    history: Optional[List[Dict]] = None,
) -> str:
    """
    Chat with the Cosmic Guide.

    Args:
        message: User's message
        user_context: Optional dict with sun_sign, moon_sign, rising_sign
        history: Optional conversation history

    Returns:
        Response string from the cosmic guide
    """
    # Build chart-like data from context
    chart_data = None
    if user_context:
        planets = []
        if user_context.get("sun_sign"):
            planets.append({"name": "Sun", "sign": user_context["sun_sign"]})
        if user_context.get("moon_sign"):
            planets.append({"name": "Moon", "sign": user_context["moon_sign"]})
        if planets:
            chart_data = {"planets": planets}
            if user_context.get("rising_sign"):
                chart_data["houses"] = [
                    {"house": 1, "sign": user_context["rising_sign"]}
                ]

    result = await ask_cosmic_guide(
        question=message,
        chart_data=chart_data,
        conversation_history=history,
    )

    return result.get("response", FALLBACK_RESPONSES["default"])


async def get_quick_insight(topic: str, sun_sign: Optional[str] = None) -> str:
    """
    Get a quick cosmic insight on a specific topic.

    Args:
        topic: Topic to get insight on
        sun_sign: Optional sun sign for personalization

    Returns:
        Quick insight string
    """
    # Detect which category this falls into
    topic_key = _detect_topic(topic)

    # Build minimal context
    if sun_sign:
        pass

    # For quick insights, use a more focused prompt
    client = create_gemini_client()
    if client is None:
        return FALLBACK_RESPONSES.get(topic_key, FALLBACK_RESPONSES["default"])

    try:
        prompt = f"""You are the Cosmic Guide, a mystical AI advisor. 
Give a brief, uplifting insight about: {topic}
{f'The user is a {sun_sign}.' if sun_sign else ''}
Keep it to 2-3 sentences maximum. Be warm and encouraging. Include one emoji."""

        response = client.models.generate_content(
            model=_get_model_name(),
            contents=prompt,
        )
        text = extract_gemini_text(response)
        return text or FALLBACK_RESPONSES.get(topic_key, FALLBACK_RESPONSES["default"])

    except Exception:
        return FALLBACK_RESPONSES.get(topic_key, FALLBACK_RESPONSES["default"])
    finally:
        close_gemini_client(client)


# Sync wrapper for non-async contexts
def ask_cosmic_guide_sync(
    question: str,
    chart_data: Optional[Dict] = None,
    numerology_data: Optional[Dict] = None,
    reading_data: Optional[Dict] = None,
) -> Dict:
    """Synchronous version of ask_cosmic_guide."""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(
        ask_cosmic_guide(question, chart_data, numerology_data, reading_data)
    )
