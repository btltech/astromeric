"""
daily_features.py
-----------------
Daily features: lucky numbers, colors, planets, affirmations, tarot, manifestation prompts.
Adds entertainment value and reasons to return daily.
"""

from __future__ import annotations

import hashlib
import random
from datetime import date, datetime
from typing import Dict, List, Optional

from app.interpretation.translations import get_translation

# ========== INTERNAL HELPERS ==========


def _stable_seed(*parts: object) -> int:
    """Build a cross-process-stable integer seed from arbitrary input parts."""
    payload = "||".join("" if part is None else str(part) for part in parts)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _stable_rng(*parts: object) -> random.Random:
    """Return a local RNG so daily feature generation is deterministic and side-effect free."""
    return random.Random(_stable_seed(*parts))


# ========== LUCKY NUMBERS ==========


def calculate_lucky_numbers(dob: str, reference_date: date) -> List[int]:
    """
    Generate 5 daily lucky numbers — all derived from numerology, none random.

    Sources:
    1. Life path number          — core soul vibration
    2. Personal day number       — today's numerology energy
    3. Month + life path blend   — monthly cycle influence
    4. Expression number         — full name sum (approximated from DOB digits cross-sum)
    5. Universal day number      — today's date reduced (day + month + year)
    """
    digits = [int(d) for d in dob.replace("-", "")]

    # 1. Life path: reduce all DOB digits to single digit (or master number)
    lp_sum = sum(digits)
    life_path = lp_sum % 9 or 9

    # 2. Personal day: (life_path + personal_month) reduced
    personal_month_raw = life_path + reference_date.month
    personal_month = personal_month_raw % 9 or 9
    personal_day = (personal_month + reference_date.day) % 9 or 9

    # 3. Month + life path blend
    month_blend = (life_path + reference_date.month + reference_date.day) % 9 or 9

    # 4. Expression number proxy: birth year cross-sum
    birth_year_sum = sum(digits[:4]) if len(digits) >= 8 else life_path
    expression = (life_path + birth_year_sum) % 9 or 9

    # 5. Universal day number: reduce today's full date
    universal = (
        reference_date.day + reference_date.month + reference_date.year
    ) % 9 or 9

    lucky = list(
        dict.fromkeys([life_path, personal_day, month_blend, expression, universal])
    )

    # If any duplicates collapsed the list below 5, fill with compound numbers
    # derived from existing values (never random)
    extras = [
        (life_path * 2) % 9 or 9,
        (personal_day + universal) % 9 or 9,
        (month_blend + expression) % 9 or 9,
        (life_path + personal_day) % 9 or 9,
        (birth_year_sum + reference_date.month) % 9 or 9,
        (universal + reference_date.day) % 9 or 9,
    ]
    for e in extras:
        if len(lucky) >= 5:
            break
        if e not in lucky:
            lucky.append(e)

    # Guarantee five values even when several numerology factors collapse to duplicates.
    if len(lucky) < 5:
        for offset in range(1, 10):
            candidate = ((life_path + personal_day + offset - 1) % 9) + 1
            if candidate not in lucky:
                lucky.append(candidate)
            if len(lucky) >= 5:
                break

    return sorted(lucky[:5])


# ========== LUCKY COLORS ==========

ELEMENT_COLORS = {
    "Fire": {
        "primary": ["Ruby Red", "Sunset Orange", "Gold", "Crimson"],
        "accent": ["White", "Yellow", "Coral"],
        "hex": {
            "Ruby Red": "#E0115F",
            "Sunset Orange": "#FF4500",
            "Gold": "#FFD700",
            "Crimson": "#DC143C",
        },
    },
    "Earth": {
        "primary": ["Forest Green", "Terracotta", "Chocolate Brown", "Olive"],
        "accent": ["Cream", "Sage", "Tan"],
        "hex": {
            "Forest Green": "#228B22",
            "Terracotta": "#E2725B",
            "Chocolate Brown": "#7B3F00",
            "Olive": "#808000",
        },
    },
    "Air": {
        "primary": ["Sky Blue", "Lavender", "Mint", "Silver"],
        "accent": ["White", "Light Pink", "Pale Yellow"],
        "hex": {
            "Sky Blue": "#87CEEB",
            "Lavender": "#E6E6FA",
            "Mint": "#98FF98",
            "Silver": "#C0C0C0",
        },
    },
    "Water": {
        "primary": ["Ocean Blue", "Seafoam", "Deep Purple", "Teal"],
        "accent": ["Pearl", "Moonstone", "Aqua"],
        "hex": {
            "Ocean Blue": "#0077BE",
            "Seafoam": "#93E9BE",
            "Deep Purple": "#673AB7",
            "Teal": "#008080",
        },
    },
}

# Weekday planetary rulers: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
_WEEKDAY_RULER = {
    0: "Moon",
    1: "Mars",
    2: "Mercury",
    3: "Jupiter",
    4: "Venus",
    5: "Saturn",
    6: "Sun",
}

# Each planet maps to its traditional color per element affinity
_PLANET_COLOR_BOOST: Dict[str, Dict[str, int]] = {
    # planet -> {element -> index into that element's primary list}
    "Sun": {
        "Fire": 2,
        "Earth": 3,
        "Air": 3,
        "Water": 2,
    },  # Gold / Olive / Silver / Deep Purple
    "Moon": {
        "Fire": 0,
        "Earth": 1,
        "Air": 2,
        "Water": 1,
    },  # Ruby / Terracotta / Mint / Seafoam
    "Mars": {
        "Fire": 3,
        "Earth": 2,
        "Air": 0,
        "Water": 3,
    },  # Crimson / Choc Brown / Sky Blue / Teal
    "Mercury": {
        "Fire": 1,
        "Earth": 3,
        "Air": 1,
        "Water": 2,
    },  # Sunset Orange / Olive / Lavender / Deep Purple
    "Jupiter": {
        "Fire": 2,
        "Earth": 0,
        "Air": 3,
        "Water": 0,
    },  # Gold / Forest Green / Silver / Ocean Blue
    "Venus": {
        "Fire": 0,
        "Earth": 1,
        "Air": 1,
        "Water": 1,
    },  # Ruby / Terracotta / Lavender / Seafoam
    "Saturn": {
        "Fire": 3,
        "Earth": 2,
        "Air": 3,
        "Water": 3,
    },  # Crimson / Choc Brown / Silver / Teal
}

# Personal day modifies the accent index (mod len)
_PD_ACCENT_SHIFT = {1: 0, 2: 1, 3: 2, 4: 0, 5: 1, 6: 2, 7: 0, 8: 1, 9: 2}


def get_lucky_colors(
    element: str,
    reference_date: date,
    lang: str = "en",
    personal_day: Optional[int] = None,
) -> Dict:
    """
    Pick lucky colors using weekday planetary ruler × element affinity.

    Primary color: determined by today's planetary ruler and the user's element.
    Accent color:  cycled by personal day number.
    Both are fully deterministic — no randomness.
    """
    colors = ELEMENT_COLORS.get(element, ELEMENT_COLORS["Fire"])

    # Primary: weekday ruler picks the color index for this element
    weekday = reference_date.weekday()
    ruler = _WEEKDAY_RULER.get(weekday, "Sun")
    planet_boost = _PLANET_COLOR_BOOST.get(ruler, {})
    primary_idx = planet_boost.get(element, 0)
    primary_idx = min(primary_idx, len(colors["primary"]) - 1)
    primary = colors["primary"][primary_idx]

    # Accent: personal day number shifts through accent list.
    # Fall back to date-derived numerology if no personal day is supplied.
    if personal_day is None or personal_day not in _PD_ACCENT_SHIFT:
        digits_today = [int(d) for d in reference_date.isoformat().replace("-", "")]
        personal_day = sum(digits_today) % 9 or 9
    accent_idx = _PD_ACCENT_SHIFT.get(personal_day, 0) % len(colors["accent"])
    accent = colors["accent"][accent_idx]

    usage_lines = {
        "Sun": "Perfect for visibility and confidence today.",
        "Moon": "Ideal for emotional clarity and intuition.",
        "Mars": "Wear it to channel drive and bold action.",
        "Mercury": "Great for communication and mental sharpness.",
        "Jupiter": "Amplifies abundance and good fortune.",
        "Venus": "Enhances harmony, beauty, and connection.",
        "Saturn": "Grounds your energy and sharpens focus.",
    }
    usage = usage_lines.get(ruler, f"Wear {primary} to amplify your energy.")

    desc_trans = get_translation(lang, "lucky_color_desc")
    if desc_trans:
        description = desc_trans[0].format(primary=primary, accent=accent)
    else:
        description = f"{usage} Accent with {accent} for balance."

    return {
        "primary": primary,
        "primary_hex": colors["hex"].get(primary, "#4ECDC4"),
        "accent": accent,
        "description": description,
        "ruler": ruler,
    }


# ========== LUCKY PLANET ==========

PLANET_ENERGY = {
    "Sun": {
        "keywords": ["confidence", "visibility", "leadership", "vitality"],
        "activities": ["presenting", "self-promotion", "creative projects"],
        "avoid": ["hiding", "self-doubt", "dimming your light"],
    },
    "Moon": {
        "keywords": ["intuition", "emotion", "nurturing", "dreams"],
        "activities": ["self-care", "family time", "journaling"],
        "avoid": ["ignoring feelings", "overworking", "emotional suppression"],
    },
    "Mercury": {
        "keywords": ["communication", "learning", "commerce", "travel"],
        "activities": ["writing", "negotiations", "short trips"],
        "avoid": ["miscommunication", "hasty decisions", "information overload"],
    },
    "Venus": {
        "keywords": ["love", "beauty", "pleasure", "harmony"],
        "activities": ["dates", "art", "beautification", "socializing"],
        "avoid": ["conflict", "neglecting pleasure", "isolation"],
    },
    "Mars": {
        "keywords": ["action", "courage", "energy", "competition"],
        "activities": ["exercise", "starting projects", "asserting yourself"],
        "avoid": ["aggression", "recklessness", "passive behavior"],
    },
    "Jupiter": {
        "keywords": ["expansion", "luck", "wisdom", "adventure"],
        "activities": ["learning", "travel planning", "taking chances"],
        "avoid": ["pessimism", "playing small", "closed-mindedness"],
    },
    "Saturn": {
        "keywords": ["discipline", "structure", "mastery", "patience"],
        "activities": ["planning", "organizing", "long-term goals"],
        "avoid": ["shortcuts", "irresponsibility", "rigidity"],
    },
}

PLANET_DAY_RULERS = {
    0: "Moon",  # Monday
    1: "Mars",  # Tuesday
    2: "Mercury",  # Wednesday
    3: "Jupiter",  # Thursday
    4: "Venus",  # Friday
    5: "Saturn",  # Saturday
    6: "Sun",  # Sunday
}


def get_lucky_planet(reference_date: date, life_path: int, lang: str = "en") -> Dict:
    """Get the day's ruling planet and its guidance."""
    day_ruler = PLANET_DAY_RULERS.get(reference_date.weekday(), "Sun")
    energy = PLANET_ENERGY.get(day_ruler, PLANET_ENERGY["Sun"])

    # Localize
    planet_key_base = f"planet_{day_ruler.lower()}"

    keywords_trans = get_translation(lang, f"{planet_key_base}_keywords")
    keywords = keywords_trans if keywords_trans else energy["keywords"]

    activities_trans = get_translation(lang, f"{planet_key_base}_activities")
    activities = activities_trans if activities_trans else energy["activities"]

    avoid_trans = get_translation(lang, f"{planet_key_base}_avoid")
    avoid = avoid_trans if avoid_trans else energy["avoid"]

    msg_trans = get_translation(lang, f"{planet_key_base}_message")
    if msg_trans:
        message = msg_trans[0]
    else:
        message = f"{day_ruler} rules today. Embrace {keywords[0]} and {keywords[1]}."

    return {
        "planet": day_ruler,
        "keywords": keywords,
        "best_for": activities,
        "avoid": avoid,
        "message": message,
    }


# ========== DAILY AFFIRMATIONS ==========

AFFIRMATION_TEMPLATES = {
    "confidence": [
        "I trust my unique path and honor my inner wisdom.",
        "My confidence grows stronger with each breath.",
        "I am exactly where I need to be right now.",
        "I release self-doubt and embrace my power.",
    ],
    "love": [
        "Love flows to me and through me effortlessly.",
        "I am worthy of deep, authentic connection.",
        "My heart is open to giving and receiving love.",
        "I attract relationships that support my highest good.",
    ],
    "abundance": [
        "Abundance finds me in expected and unexpected ways.",
        "I am a magnet for prosperity and success.",
        "Money flows to me easily and consistently.",
        "I deserve the abundance that is coming to me.",
    ],
    "peace": [
        "I choose peace over chaos in every moment.",
        "My mind is calm, my heart is steady.",
        "I release what I cannot control.",
        "Serenity is my natural state.",
    ],
    "growth": [
        "Every challenge is an opportunity for growth.",
        "I am constantly evolving into my best self.",
        "I embrace change as a pathway to expansion.",
        "My potential is limitless.",
    ],
}


def get_daily_affirmation(
    element: str,
    life_path: int,
    reference_date: date,
    lang: str = "en",
) -> Dict:
    """Generate a personalized daily affirmation."""
    rng = _stable_rng(
        "affirmation", element, life_path, reference_date.isoformat(), lang
    )

    # Map elements and life paths to affirmation categories
    if element == "Fire" or life_path in [1, 3, 5]:
        category = rng.choice(["confidence", "growth"])
    elif element == "Earth" or life_path in [4, 8]:
        category = rng.choice(["abundance", "growth"])
    elif element == "Water" or life_path in [2, 6]:
        category = rng.choice(["love", "peace"])
    else:
        category = rng.choice(["peace", "growth"])

    # Try to get localized affirmations
    affirmations = get_translation(lang, f"affirmation_{category}")
    if not affirmations:
        affirmations = AFFIRMATION_TEMPLATES.get(
            category, AFFIRMATION_TEMPLATES["confidence"]
        )

    affirmation = rng.choice(affirmations)

    instr_trans = get_translation(lang, "affirmation_instruction")
    instruction = (
        instr_trans[0]
        if instr_trans
        else "Repeat this 3 times each morning, feeling the words as truth."
    )

    return {
        "text": affirmation,
        "category": category,
        "instruction": instruction,
    }


# ========== TAROT DAILY CARD ==========

MAJOR_ARCANA = {
    0: {
        "name": "The Fool",
        "keywords": ["beginnings", "innocence", "spontaneity", "leap of faith"],
        "upright": "Take a leap! New adventures await. Trust the journey.",
        "reversed": "Pause before jumping. Consider the risks.",
        "advice": "Embrace beginner's mind today. What would you do if you couldn't fail?",
    },
    1: {
        "name": "The Magician",
        "keywords": ["manifestation", "resourcefulness", "power", "action"],
        "upright": "You have everything you need. Manifest your vision now.",
        "reversed": "Check for scattered energy. Focus your intentions.",
        "advice": "Take one concrete action toward your biggest goal today.",
    },
    2: {
        "name": "The High Priestess",
        "keywords": ["intuition", "sacred knowledge", "divine feminine", "mystery"],
        "upright": "Trust your gut. Hidden truths are surfacing.",
        "reversed": "Don't ignore your inner voice. Listen deeper.",
        "advice": "Spend 5 minutes in silence. What does your intuition whisper?",
    },
    3: {
        "name": "The Empress",
        "keywords": ["abundance", "nature", "nurturing", "sensuality"],
        "upright": "Abundance surrounds you. Nurture what matters.",
        "reversed": "Self-care isn't selfish. Fill your cup first.",
        "advice": "Connect with nature or beauty today, even briefly.",
    },
    4: {
        "name": "The Emperor",
        "keywords": ["authority", "structure", "stability", "leadership"],
        "upright": "Take charge. Your leadership is needed.",
        "reversed": "Flexibility is strength. Loosen rigid structures.",
        "advice": "Create one new system or boundary that serves you.",
    },
    5: {
        "name": "The Hierophant",
        "keywords": ["tradition", "spirituality", "guidance", "institutions"],
        "upright": "Seek wisdom from trusted sources. Honor traditions.",
        "reversed": "Question conventional wisdom. Find your own path.",
        "advice": "What wisdom from your past still serves you?",
    },
    6: {
        "name": "The Lovers",
        "keywords": ["love", "harmony", "relationships", "values"],
        "upright": "Heart connections deepen. Align with your values.",
        "reversed": "Examine a relationship imbalance. Seek harmony.",
        "advice": "Make a choice today that aligns with your authentic self.",
    },
    7: {
        "name": "The Chariot",
        "keywords": ["willpower", "determination", "success", "direction"],
        "upright": "Victory through focus. Drive forward with determination.",
        "reversed": "Check your direction. Are you fighting the current?",
        "advice": "Set your intention clearly and move with purpose.",
    },
    8: {
        "name": "Strength",
        "keywords": ["courage", "patience", "compassion", "inner strength"],
        "upright": "Gentle persistence wins. Lead with heart, not force.",
        "reversed": "Don't suppress emotions. Find healthy expression.",
        "advice": "Where can you apply gentle strength instead of force?",
    },
    9: {
        "name": "The Hermit",
        "keywords": ["introspection", "solitude", "guidance", "soul-searching"],
        "upright": "Wisdom awaits within. Seek solitude to find answers.",
        "reversed": "Don't isolate too long. Seek balance.",
        "advice": "Schedule 15 minutes of quiet reflection today.",
    },
    10: {
        "name": "Wheel of Fortune",
        "keywords": ["change", "cycles", "destiny", "turning point"],
        "upright": "Change is coming—welcome it. The wheel turns in your favor.",
        "reversed": "Resist stagnation. Accept what cannot be controlled.",
        "advice": "What cycle in your life is asking to complete?",
    },
    11: {
        "name": "Justice",
        "keywords": ["fairness", "truth", "cause and effect", "accountability"],
        "upright": "Truth prevails. Balanced decisions bring results.",
        "reversed": "Check for bias. Seek fairness in all dealings.",
        "advice": "Where in your life do you need more balance?",
    },
    12: {
        "name": "The Hanged Man",
        "keywords": ["pause", "surrender", "new perspective", "letting go"],
        "upright": "Pause brings insight. Surrender to gain perspective.",
        "reversed": "Stop resisting the pause. What are you avoiding?",
        "advice": "What would change if you looked at a problem upside-down?",
    },
    13: {
        "name": "Death",
        "keywords": ["endings", "transformation", "transition", "release"],
        "upright": "Something ends so something new can begin. Embrace transformation.",
        "reversed": "Stop clinging. Release what no longer serves.",
        "advice": "What must you let die so new life can emerge?",
    },
    14: {
        "name": "Temperance",
        "keywords": ["balance", "moderation", "patience", "purpose"],
        "upright": "Blend extremes. Patience and moderation bring harmony.",
        "reversed": "Restore balance. Avoid excess in any direction.",
        "advice": "Where can you bring more moderation to your life?",
    },
    15: {
        "name": "The Devil",
        "keywords": ["shadow self", "attachment", "bondage", "materialism"],
        "upright": "Examine attachments. What chains can you release?",
        "reversed": "Breaking free! Liberation from old patterns.",
        "advice": "Name one habit or thought pattern that limits you.",
    },
    16: {
        "name": "The Tower",
        "keywords": ["sudden change", "revelation", "upheaval", "awakening"],
        "upright": "Shakeups lead to breakthroughs. Embrace necessary destruction.",
        "reversed": "Delaying the inevitable? Let go before you're pushed.",
        "advice": "What structure in your life needs honest examination?",
    },
    17: {
        "name": "The Star",
        "keywords": ["hope", "faith", "renewal", "inspiration"],
        "upright": "Hope renewed. Trust in the universe's plan.",
        "reversed": "Reconnect with faith. Don't give up on dreams.",
        "advice": "What dream have you neglected that deserves revival?",
    },
    18: {
        "name": "The Moon",
        "keywords": ["intuition", "illusion", "fear", "subconscious"],
        "upright": "Trust intuition over logic today. Navigate uncertainty.",
        "reversed": "Clarity emerging. Confusion lifting.",
        "advice": "What does your subconscious know that your conscious mind denies?",
    },
    19: {
        "name": "The Sun",
        "keywords": ["joy", "success", "vitality", "positivity"],
        "upright": "Radiant success! Joy and vitality are yours.",
        "reversed": "Let your light shine. Don't dim yourself.",
        "advice": "What brings you genuine, uncomplicated joy?",
    },
    20: {
        "name": "Judgement",
        "keywords": ["reflection", "reckoning", "awakening", "rebirth"],
        "upright": "A calling! Reflect on your life's purpose.",
        "reversed": "Self-forgiveness needed. Release old guilt.",
        "advice": "What life chapter is calling for closure or celebration?",
    },
    21: {
        "name": "The World",
        "keywords": ["completion", "integration", "accomplishment", "travel"],
        "upright": "A cycle completes. Celebrate your journey!",
        "reversed": "Almost there. Don't quit before the finish.",
        "advice": "Acknowledge one accomplishment you haven't celebrated.",
    },
}


def get_daily_tarot(reference_date: date, name: str, lang: str = "en") -> Dict:
    """Draw a daily tarot card based on date and name."""
    rng = _stable_rng(
        "daily_tarot", name.strip().lower(), reference_date.isoformat(), lang
    )

    card_num = rng.randint(0, 21)
    is_reversed = rng.random() < 0.3  # 30% chance reversed

    card = MAJOR_ARCANA[card_num]

    # Localize card details
    card_key_base = f"tarot_{card_num}"

    name_trans = get_translation(lang, f"{card_key_base}_name")
    card_name = name_trans[0] if name_trans else card["name"]

    upright_trans = get_translation(lang, f"{card_key_base}_upright")
    upright_msg = upright_trans[0] if upright_trans else card["upright"]

    reversed_trans = get_translation(lang, f"{card_key_base}_reversed")
    reversed_msg = reversed_trans[0] if reversed_trans else card["reversed"]

    advice_trans = get_translation(lang, f"{card_key_base}_advice")
    advice_msg = advice_trans[0] if advice_trans else card["advice"]

    # Keywords might be tricky if not translated individually, but let's assume we keep English or add a key
    # For now, keeping English keywords as they are often universal or simple enough

    return {
        "card": card_name,
        "card_number": card_num,
        "keywords": card["keywords"],
        "message": reversed_msg if is_reversed else upright_msg,
        "reversed": is_reversed,
        "daily_advice": advice_msg,
    }


# ========== YES/NO ORACLE ==========


def get_yes_no_oracle(
    question: str,
    reference_date: date,
    dob: Optional[str] = None,
    lang: str = "en",
) -> Dict:
    """
    Cosmic yes/no oracle weighted by moon phase and personal day energy.

    Weighting logic:
    - Full Moon / Waxing Gibbous  → strong yes bias
    - New Moon / Waxing Crescent  → gentle yes / maybe (seeds need time)
    - Void-of-course proxy (Waning Crescent / late waning) → wait bias
    - Waning Gibbous / Last Quarter → no / release bias
    - Personal day 7 or 4          → introspective → wait/maybe boost
    - Personal day 1, 3, 5         → action → yes bias
    """
    base_answers = [
        {
            "key": "yes_strong",
            "answer": "Yes",
            "confidence": "strong",
            "default": "The stars align in favor. Move forward with confidence.",
        },
        {
            "key": "yes_gentle",
            "answer": "Yes",
            "confidence": "gentle",
            "default": "A soft yes. Proceed with awareness and intention.",
        },
        {
            "key": "no_strong",
            "answer": "No",
            "confidence": "strong",
            "default": "The cosmos advises against this path right now.",
        },
        {
            "key": "no_gentle",
            "answer": "No",
            "confidence": "gentle",
            "default": "Not at this moment. Patience may change the answer.",
        },
        {
            "key": "wait",
            "answer": "Wait",
            "confidence": "neutral",
            "default": "The timing isn't clear. Ask again when the moon shifts.",
        },
        {
            "key": "maybe",
            "answer": "Maybe",
            "confidence": "neutral",
            "default": "The outcome depends on your actions. You have power here.",
        },
    ]

    # Build weights: start at 1 for each answer
    weights = {a["key"]: 1.0 for a in base_answers}

    # Moon phase influence
    try:
        from .moon_phases import calculate_moon_phase

        ref_dt = datetime(
            reference_date.year, reference_date.month, reference_date.day, 12, 0
        )
        moon = calculate_moon_phase(ref_dt)
        phase = moon.get("phase", "").lower()

        if "full moon" in phase:
            weights["yes_strong"] += 3
            weights["yes_gentle"] += 1
        elif "waxing gibbous" in phase:
            weights["yes_strong"] += 2
            weights["yes_gentle"] += 2
        elif "waxing crescent" in phase or "first quarter" in phase:
            weights["yes_gentle"] += 2
            weights["maybe"] += 1
        elif "new moon" in phase:
            weights["yes_gentle"] += 1
            weights["maybe"] += 2
            weights["wait"] += 1
        elif "waning crescent" in phase:
            weights["wait"] += 3
            weights["no_gentle"] += 1
        elif "last quarter" in phase:
            weights["no_gentle"] += 2
            weights["wait"] += 2
        elif "waning gibbous" in phase:
            weights["no_gentle"] += 1
            weights["maybe"] += 1
    except Exception:
        pass

    # Personal day influence
    if dob:
        try:
            digits = [int(d) for d in reference_date.isoformat().replace("-", "")]
            pd = sum(digits) % 9 or 9
            if pd in (1, 3, 5):
                weights["yes_strong"] += 2
                weights["yes_gentle"] += 1
            elif pd in (4, 7):
                weights["wait"] += 2
                weights["maybe"] += 1
            elif pd == 9:
                weights["no_gentle"] += 1
                weights["wait"] += 1  # endings, release
            elif pd in (2, 6):
                weights["yes_gentle"] += 1
                weights["maybe"] += 1  # cooperation
        except Exception:
            pass

    # Use question + date as seed for deterministic selection within the weighted pool
    rng = _stable_rng(
        "yes_no_oracle",
        question.strip().lower(),
        reference_date.isoformat(),
        dob or "",
        lang,
    )
    keys = list(weights.keys())
    wvals = [weights[k] for k in keys]
    selected_key = rng.choices(keys, weights=wvals)[0]
    selected = next(a for a in base_answers if a["key"] == selected_key)

    msg_key = f"oracle_{selected['key']}_msg"
    msg_trans = get_translation(lang, msg_key)
    message = msg_trans[0] if msg_trans else selected["default"]

    ans_key = f"oracle_{selected['key']}_ans"
    ans_trans = get_translation(lang, ans_key)
    answer = ans_trans[0] if ans_trans else selected["answer"]

    return {
        "answer": answer,
        "confidence": selected["confidence"],
        "message": message,
    }


# ========== MANIFESTATION PROMPT ==========

MANIFESTATION_PROMPTS = [
    "I am attracting {desire} into my life right now.",
    "The universe is conspiring to bring me {desire}.",
    "I am ready and open to receive {desire}.",
    "Every day, I move closer to {desire}.",
    "I release all blocks to {desire} and welcome it fully.",
]

MANIFESTATION_DESIRES = {
    1: ["independence", "new opportunities", "leadership", "fresh starts"],
    2: ["harmony", "partnership", "peace", "deep connection"],
    3: ["creative success", "joy", "recognition", "self-expression"],
    4: ["stability", "security", "solid foundations", "tangible results"],
    5: ["adventure", "freedom", "positive change", "new experiences"],
    6: ["love", "family harmony", "beautiful spaces", "responsibility fulfillment"],
    7: ["wisdom", "spiritual insight", "inner peace", "understanding"],
    8: ["abundance", "success", "recognition", "material prosperity"],
    9: ["completion", "humanitarian impact", "release", "universal love"],
}


def get_manifestation_prompt(
    life_path: int, personal_day: int, reference_date: date, lang: str = "en"
) -> Dict:
    """Generate a personalized manifestation prompt."""
    rng = _stable_rng(
        "manifestation", life_path, personal_day, reference_date.isoformat(), lang
    )

    # Get desires
    desires_trans = get_translation(lang, f"manifestation_desires_{life_path}")
    if desires_trans:
        desires = desires_trans
    else:
        desires = MANIFESTATION_DESIRES.get(life_path, MANIFESTATION_DESIRES[1])

    desire = rng.choice(desires)

    # Get templates
    prompts_trans = get_translation(lang, "manifestation_prompts")
    if prompts_trans:
        template = rng.choice(prompts_trans)
    else:
        template = rng.choice(MANIFESTATION_PROMPTS)

    return {
        "prompt": template.format(desire=desire),
        "focus": desire,
        "practice": get_translation(lang, "manifestation_practice")[0]
        if get_translation(lang, "manifestation_practice")
        else "Write this 3 times in present tense, feeling it as already true.",
        "visualization": (
            get_translation(lang, "manifestation_viz")[0]
            if get_translation(lang, "manifestation_viz")
            else "Close your eyes and picture yourself fully experiencing {desire}."
        ).format(desire=desire),
    }


# ========== MOOD FORECAST ==========

MOOD_FORECASTS = {
    "energetic": {
        "emoji": "⚡",
        "description": "High energy day! Channel this into productive action.",
        "tips": ["Exercise early", "Tackle big tasks", "Avoid caffeine after 2pm"],
    },
    "reflective": {
        "emoji": "🌙",
        "description": "Contemplative mood. Insights come from within.",
        "tips": ["Journal", "Meditate", "Avoid major decisions"],
    },
    "social": {
        "emoji": "🌟",
        "description": "Connection-oriented. Relationships benefit from attention.",
        "tips": ["Reach out to friends", "Network", "Collaborate"],
    },
    "creative": {
        "emoji": "🎨",
        "description": "Imagination runs high. Creative solutions abound.",
        "tips": ["Brainstorm freely", "Try something artistic", "Think outside boxes"],
    },
    "grounded": {
        "emoji": "🌿",
        "description": "Stable and practical. Good for concrete progress.",
        "tips": ["Handle finances", "Organize spaces", "Complete lingering tasks"],
    },
    "transformative": {
        "emoji": "🦋",
        "description": "Change energy is strong. Release what doesn't serve.",
        "tips": ["Let go of old stuff", "Have honest conversations", "Embrace endings"],
    },
}


def _calculate_daily_luck_score(
    element: str,
    life_path: int,
    personal_day: int,
    personal_year: int,
    reference_date: date,
) -> float:
    """
    Calculate a deterministic daily luck score (0.0–100.0) from five weighted factors.

    Factors & weights
    -----------------
    1. Personal Day energy     30% — numerology energy of today's personal day number
    2. Moon phase              25% — lunar cycle position (new/full = high, balsamic = low)
    3. Void-of-course penalty  15% — late-degree moon with no applying aspects = -15 pts
    4. Personal Year cycle     15% — expansion years (1,3,5,9) vs contraction (4,7)
    5. Weekday × element       15% — planetary ruler of weekday resonance with element
    """
    # ── 1. Personal Day energy (0–100) ──────────────────────────────────────
    PD_ENERGY: Dict[int, float] = {
        1: 85,  # New beginnings, high initiative
        2: 60,  # Cooperation, patience required
        3: 90,  # Creativity, self-expression, social
        4: 45,  # Hard work, discipline, restriction
        5: 80,  # Change, freedom, adventure
        6: 75,  # Harmony, nurturing, balance
        7: 40,  # Introspection, rest, inner work
        8: 70,  # Ambition, power, material focus
        9: 65,  # Completion, release, compassion
    }
    pd_score = PD_ENERGY.get(personal_day, 60)

    # ── 2. Moon phase score (0–100) ──────────────────────────────────────────
    try:
        from .moon_phases import calculate_moon_phase

        ref_dt = datetime(
            reference_date.year, reference_date.month, reference_date.day, 12, 0
        )
        moon = calculate_moon_phase(ref_dt)
        phase_name = (moon.get("phase_name") or moon.get("phase") or "").lower()
        illumination = moon.get("illumination", 50)

        PHASE_SCORES: Dict[str, float] = {
            "new moon": 85,  # Fresh start, plant seeds
            "waxing crescent": 75,  # Building momentum
            "first quarter": 70,  # Decision point, push forward
            "waxing gibbous": 80,  # Refinement, nearly full power
            "full moon": 90,  # Peak energy, maximum clarity
            "waning gibbous": 65,  # Harvest, gratitude
            "last quarter": 50,  # Release, let go
            "waning crescent": 40,  # Rest, prepare, balsamic
        }
        moon_score = next(
            (v for k, v in PHASE_SCORES.items() if k in phase_name),
            50 + (illumination - 50) * 0.4,  # fallback: scale on illumination
        )
    except Exception:
        moon_score = 60.0

    # ── 3. Void-of-course moon penalty (0 or –15 pts applied at end) ─────────
    voc_penalty = 0.0
    try:
        from .moon_phases import calculate_moon_phase

        ref_dt = datetime(
            reference_date.year, reference_date.month, reference_date.day, 12, 0
        )
        moon_data = calculate_moon_phase(ref_dt)
        # VOC proxy: moon in late degrees (≥27°) of sign and waning
        moon_deg = moon_data.get("degrees_in_sign", 0)
        moon_phase_name = (
            moon_data.get("phase_name") or moon_data.get("phase") or ""
        ).lower()
        is_waning = (
            "waning" in moon_phase_name or moon_data.get("illumination", 50) < 50
        )
        if moon_deg >= 27 and is_waning:
            voc_penalty = 15.0
    except Exception:
        pass

    # ── 4. Personal Year cycle energy (0–100) ────────────────────────────────
    PY_ENERGY: Dict[int, float] = {
        1: 85,  # Year of new beginnings
        2: 60,
        3: 80,
        4: 45,  # Year of foundation — slow but necessary
        5: 85,
        6: 70,
        7: 40,  # Year of introspection
        8: 75,
        9: 65,  # Year of endings & release
    }
    py_score = PY_ENERGY.get(personal_year % 9 or 9, 60)

    # ── 5. Weekday × element resonance (0–100) ────────────────────────────────
    # Each weekday is ruled by a planet; elements resonate with those rulers
    WEEKDAY_RULERS = {
        0: "Moon",  # Monday
        1: "Mars",  # Tuesday
        2: "Mercury",  # Wednesday
        3: "Jupiter",  # Thursday
        4: "Venus",  # Friday
        5: "Saturn",  # Saturday
        6: "Sun",  # Sunday
    }
    ELEMENT_RESONANCE: Dict[str, Dict[str, float]] = {
        "Fire": {
            "Sun": 90,
            "Mars": 85,
            "Jupiter": 75,
            "Venus": 60,
            "Mercury": 65,
            "Moon": 55,
            "Saturn": 40,
        },
        "Earth": {
            "Saturn": 85,
            "Venus": 80,
            "Mercury": 70,
            "Moon": 65,
            "Jupiter": 60,
            "Mars": 50,
            "Sun": 55,
        },
        "Air": {
            "Mercury": 90,
            "Venus": 80,
            "Jupiter": 75,
            "Sun": 70,
            "Moon": 60,
            "Mars": 55,
            "Saturn": 45,
        },
        "Water": {
            "Moon": 90,
            "Venus": 75,
            "Jupiter": 70,
            "Saturn": 60,
            "Mercury": 55,
            "Mars": 50,
            "Sun": 65,
        },
    }
    weekday = reference_date.weekday()
    ruler = WEEKDAY_RULERS.get(weekday, "Sun")
    element_scores = ELEMENT_RESONANCE.get(element, {})
    weekday_score = element_scores.get(ruler, 60)

    # ── Weighted composite ────────────────────────────────────────────────────
    raw = (
        pd_score * 0.30
        + moon_score * 0.25
        + py_score * 0.15
        + weekday_score * 0.15
        + 60 * 0.15  # base contribution for the VOC slot (penalty applied below)
    ) - voc_penalty

    return round(max(5.0, min(100.0, raw)), 1)


def _calculate_mood_forecast(
    element: str,
    life_path: int,
    personal_day: int,
    reference_date: date,
    lang: str = "en",
    personal_year: int = 5,
) -> Dict:
    """Generate daily mood forecast with a real weighted luck score."""
    rng = _stable_rng(
        "mood_forecast",
        element,
        life_path,
        personal_day,
        personal_year,
        reference_date.isoformat(),
        lang,
    )

    # Weight moods based on element and personal day
    weights = {
        "energetic": 1 if element in ["Fire", "Air"] else 0.5,
        "reflective": 1 if personal_day in [7, 9] else 0.5,
        "social": 1 if element in ["Air", "Fire"] or personal_day in [2, 3, 6] else 0.5,
        "creative": 1 if personal_day in [3, 5] else 0.5,
        "grounded": 1 if element == "Earth" or personal_day in [4, 8] else 0.5,
        "transformative": 1 if element == "Water" or personal_day == 9 else 0.3,
    }

    moods = list(weights.keys())
    mood = rng.choices(moods, weights=list(weights.values()))[0]
    forecast = MOOD_FORECASTS[mood]

    desc_trans = get_translation(lang, f"mood_{mood}_desc")
    description = desc_trans[0] if desc_trans else forecast["description"]

    tips_trans = get_translation(lang, f"mood_{mood}_tips")
    tips = tips_trans if tips_trans else forecast["tips"]

    # Real weighted score (1–10 scale for backward compat, full score on separate key)
    luck_100 = _calculate_daily_luck_score(
        element, life_path, personal_day, personal_year, reference_date
    )
    score_10 = round(luck_100 / 10, 1)

    return {
        "mood": mood,
        "emoji": forecast["emoji"],
        "score": score_10,
        "luck_score": luck_100,  # full 0–100 value used by daily_luck field
        "description": description,
        "tips": tips,
        "peak_hours": f"{10 + (personal_day % 3)}am - {2 + (personal_day % 4)}pm",
    }


# ========== RETROGRADE ALERTS ==========

# Approximate Mercury retrograde dates for 2024-2026
MERCURY_RETROGRADES = [
    ("2024-04-01", "2024-04-25"),
    ("2024-08-04", "2024-08-28"),
    ("2024-11-25", "2024-12-15"),
    ("2025-03-15", "2025-04-07"),
    ("2025-07-18", "2025-08-11"),
    ("2025-11-09", "2025-11-29"),
    ("2026-02-26", "2026-03-20"),
    ("2026-06-29", "2026-07-23"),
    ("2026-10-24", "2026-11-13"),
]


def check_retrograde_alerts(reference_date: date, lang: str = "en") -> List[Dict]:
    """Check for active retrogrades and return alerts."""
    alerts = []
    date_str = reference_date.isoformat()

    for start, end in MERCURY_RETROGRADES:
        if start <= date_str <= end:
            days_in = (reference_date - date.fromisoformat(start)).days
            days_left = (date.fromisoformat(end) - reference_date).days

            msg_trans = get_translation(lang, "retro_mercury_msg")
            if msg_trans:
                message = msg_trans[0].format(days_in=days_in + 1, days_left=days_left)
            else:
                message = f"Mercury is retrograde! Day {days_in + 1}, {days_left} days remaining."

            advice_trans = get_translation(lang, "retro_mercury_advice")
            advice = (
                advice_trans
                if advice_trans
                else [
                    "Double-check all communications",
                    "Back up important files",
                    "Avoid signing contracts if possible",
                    "Reconnect with old friends",
                    "Review rather than start new projects",
                ]
            )

            alerts.append(
                {
                    "planet": "Mercury",
                    "status": "retrograde",
                    "message": message,
                    "advice": advice,
                }
            )
            break

    return alerts


# ========== COMPLETE DAILY FEATURES ==========


def get_all_daily_features(
    name: str,
    dob: str,
    element: str,
    life_path: int,
    personal_day: int,
    reference_date: Optional[date] = None,
    lang: str = "en",
    personal_year: int = 5,
) -> Dict:
    """Get all daily features in one call."""
    if reference_date is None:
        reference_date = date.today()

    return {
        "date": reference_date.isoformat(),
        "lucky_numbers": calculate_lucky_numbers(dob, reference_date),
        "lucky_colors": get_lucky_colors(
            element, reference_date, lang=lang, personal_day=personal_day
        ),
        "lucky_planet": get_lucky_planet(reference_date, life_path, lang=lang),
        "affirmation": get_daily_affirmation(
            element, life_path, reference_date, lang=lang
        ),
        "tarot": get_daily_tarot(reference_date, name, lang=lang),
        "manifestation": get_manifestation_prompt(
            life_path, personal_day, reference_date, lang=lang
        ),
        "mood_forecast": _calculate_mood_forecast(
            element,
            life_path,
            personal_day,
            reference_date,
            lang=lang,
            personal_year=personal_year,
        ),
        "retrograde_alerts": check_retrograde_alerts(reference_date, lang=lang),
    }


# ========== API-FACING FUNCTIONS ==========

SIGN_ELEMENTS = {
    "Aries": "Fire",
    "Leo": "Fire",
    "Sagittarius": "Fire",
    "Taurus": "Earth",
    "Virgo": "Earth",
    "Capricorn": "Earth",
    "Gemini": "Air",
    "Libra": "Air",
    "Aquarius": "Air",
    "Cancer": "Water",
    "Scorpio": "Water",
    "Pisces": "Water",
}


def get_daily_features(birth_date: str, sun_sign: Optional[str] = None) -> Dict:
    """Get daily features for the API endpoint."""
    today = date.today()

    # Calculate life path from birth date
    life_path = sum(int(d) for d in birth_date.replace("-", "")) % 9 or 9

    # Calculate personal day
    personal_day = (today.day + today.month + life_path) % 9 or 9

    # Determine element from sun sign
    element = SIGN_ELEMENTS.get(sun_sign, "Fire") if sun_sign else "Fire"

    # Generate a name seed from birth date
    name_seed = f"cosmic_{birth_date}"

    return {
        "date": today.isoformat(),
        "lucky_numbers": calculate_lucky_numbers(birth_date, today),
        "lucky_colors": get_lucky_colors(element, today, personal_day=personal_day),
        "lucky_planet": get_lucky_planet(today, life_path),
        "affirmation": get_daily_affirmation(element, life_path, today),
        "tarot": get_daily_tarot(today, name_seed),
        "manifestation": get_manifestation_prompt(life_path, personal_day, today),
        "mood_forecast": _calculate_mood_forecast(
            element, life_path, personal_day, today
        ),
        "retrograde_alerts": check_retrograde_alerts(today),
        "personal_day": personal_day,
        "life_path": life_path,
    }


def get_tarot_card(question: Optional[str] = None) -> Dict:
    """Draw a single tarot card."""
    today = date.today()
    draw_nonce = datetime.now().isoformat(timespec="microseconds")
    rng = _stable_rng("tarot_card", question or "daily", today.isoformat(), draw_nonce)

    card_num = rng.randint(0, 21)
    is_reversed = rng.random() < 0.3

    card = MAJOR_ARCANA[card_num]

    return {
        "card": card["name"],
        "card_number": card_num,
        "keywords": card["keywords"],
        "message": card["reversed"] if is_reversed else card["upright"],
        "reversed": is_reversed,
        "daily_advice": card["advice"],
        "drawn_at": datetime.now().isoformat(),
    }


def get_yes_no_reading(question: str, birth_date: Optional[str] = None) -> Dict:
    """Get a cosmic yes/no reading."""
    today = date.today()
    rng = _stable_rng(
        "yes_no_reading", question.strip().lower(), today.isoformat(), birth_date or ""
    )

    # Determine answer with cosmic reasoning
    answers = [
        {
            "answer": "Yes",
            "emoji": "✨",
            "confidence": rng.randint(70, 95),
            "message": "The stars align in favor. Move forward with confidence.",
            "reasoning": "The cosmic energies support this path. Trust the universe's guidance.",
            "timing": "The timing feels right. Act within the next few days.",
        },
        {
            "answer": "Yes",
            "emoji": "🌟",
            "confidence": rng.randint(55, 75),
            "message": "A soft yes. Proceed with awareness and intention.",
            "reasoning": "The energy is favorable but requires your conscious effort.",
            "timing": "Consider waiting until after the new moon for best results.",
        },
        {
            "answer": "No",
            "emoji": "🌑",
            "confidence": rng.randint(70, 95),
            "message": "The cosmos advises against this path right now.",
            "reasoning": "There are unseen obstacles. This isn't a permanent no, just not now.",
            "timing": "Revisit this question in a lunar cycle.",
        },
        {
            "answer": "No",
            "emoji": "🌒",
            "confidence": rng.randint(55, 75),
            "message": "Not at this moment. Patience may change the answer.",
            "reasoning": "The universe is redirecting you toward something better.",
            "timing": "Give it more time. The path will become clearer.",
        },
        {
            "answer": "Maybe",
            "emoji": "🔮",
            "confidence": rng.randint(40, 60),
            "message": "The outcome depends on your actions. You have power here.",
            "reasoning": "This is a crossroads moment. Your choice shapes the outcome.",
            "timing": "Take action within 3 days to influence the outcome.",
        },
        {
            "answer": "Wait",
            "emoji": "⏳",
            "confidence": rng.randint(50, 70),
            "message": "The timing isn't clear. Ask again when the moon shifts.",
            "reasoning": "More information needs to emerge before this can be answered.",
            "timing": "Ask again after the next major lunar phase.",
        },
    ]

    result = rng.choice(answers)
    result["question"] = question
    result["asked_at"] = datetime.now().isoformat()

    return result


def get_mood_forecast(sun_sign: str, moon_sign: Optional[str] = None) -> Dict:
    """Get today's mood forecast based on astrological influences."""
    today = date.today()
    element = SIGN_ELEMENTS.get(sun_sign, "Fire")

    # Simple life path and personal day for forecasting
    rng = _stable_rng(
        "public_mood_forecast", sun_sign, moon_sign or "", today.isoformat()
    )

    life_path = rng.randint(1, 9)
    personal_day = (today.day + today.month) % 9 or 9

    # Weight moods based on element and day
    weights = {
        "energetic": 1.5 if element in ["Fire", "Air"] else 0.8,
        "reflective": 1.2 if personal_day in [7, 9] else 0.6,
        "social": 1.5
        if element in ["Air", "Fire"] or personal_day in [2, 3, 6]
        else 0.7,
        "creative": 1.3 if personal_day in [3, 5] else 0.6,
        "grounded": 1.5 if element == "Earth" or personal_day in [4, 8] else 0.7,
        "transformative": 1.2 if element == "Water" or personal_day == 9 else 0.5,
    }

    moods = list(weights.keys())
    mood = rng.choices(moods, weights=list(weights.values()))[0]
    forecast = MOOD_FORECASTS[mood]

    # Calculate energy score (1-10)
    base_score = rng.randint(5, 8)
    modifier = 1 if personal_day in [3, 5, 6] else -1 if personal_day in [4, 7] else 0
    score = max(1, min(10, base_score + modifier))

    return {
        "date": today.isoformat(),
        "sun_sign": sun_sign,
        "moon_sign": moon_sign,
        "mood": mood,
        "emoji": forecast["emoji"],
        "energy_score": score,
        "description": forecast["description"],
        "tips": forecast["tips"],
        "peak_hours": f"{10 + (personal_day % 3)}:00 AM - {2 + (personal_day % 4)}:00 PM",
        "element_influence": f"{element} energy shapes your day",
    }


# =============================================================================
# ASTROLOGY-INFORMED GUIDANCE FUNCTIONS (v2 — consume AstroContext)
#
# These five functions are the upgraded replacements.  They accept an
# AstroContext dict (produced by astro_context.build_astro_context) and
# return the standard output contract:
#   headline, selection, why_it_matches, how_to_use,
#   basis, trust_level, reason_factors
#
# All old functions remain untouched for backward compatibility.
# =============================================================================


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _rf(type_: str, value) -> Dict:
    """Build a reason_factor entry."""
    return {"type": type_, "value": value}


def _trust_level_from_ctx(context: Dict) -> str:
    """Return 'limited' if either trust gate is False, else 'full'."""
    if not context.get("birth_time_trusted") or not context.get("location_trusted"):
        return "limited"
    return "full"


# ---------------------------------------------------------------------------
# FEATURE 1 — Lucky Number (3-tier, numerology-based)
# ---------------------------------------------------------------------------

_PLANET_NUM_MAP: Dict[str, int] = {
    "Sun": 1,
    "Moon": 2,
    "Jupiter": 3,
    "Uranus": 4,
    "Mercury": 5,
    "Venus": 6,
    "Neptune": 7,
    "Saturn": 8,
    "Mars": 9,
}

_PD_DESCRIPTORS_V2: Dict[int, str] = {
    1: "self-direction and new beginnings",
    2: "cooperation and patience",
    3: "creative expression",
    4: "structured, practical effort",
    5: "change and freedom",
    6: "nurturing and harmony",
    7: "inner reflection and rest",
    8: "ambition and material focus",
    9: "completion and release",
}

_PM_DESCRIPTORS_V2: Dict[int, str] = {
    1: "fresh starts",
    2: "patience",
    3: "creativity",
    4: "discipline",
    5: "adventure",
    6: "harmony",
    7: "reflection",
    8: "material focus",
    9: "release",
}


def _reduce_num(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def get_lucky_number_guidance(context: Dict) -> Dict:
    """
    Tiered lucky-number guidance from AstroContext.

    Tier 1 — core   : life_path
    Tier 2 — support: personal_day + personal_month (deduped)
    Tier 3 — resonance: universal_day + calendar_reduction + day-ruler correspondence
    """
    lp = context["life_path"]
    pd = context["personal_day"]
    pm = context["personal_month"]
    ud = context["universal_day"]
    cr = context["calendar_reduction"]
    ruler = context["day_ruler"]

    core = lp

    seen: set = {core}
    support: List[int] = []
    for n in [pd, pm]:
        if n not in seen:
            support.append(n)
            seen.add(n)
    if len(support) < 2:
        extra = _reduce_num(pd + pm)
        if extra not in seen:
            support.append(extra)
            seen.add(extra)
    if len(support) < 2:
        extra2 = _reduce_num(pm + 1)
        if extra2 not in seen:
            support.append(extra2)
    support = support[:2]

    planet_num = _PLANET_NUM_MAP.get(ruler)
    resonance_candidates = [ud, cr]
    if planet_num:
        resonance_candidates.append(planet_num)
    resonance: List[int] = []
    for n in resonance_candidates:
        if n not in seen and n not in resonance:
            resonance.append(n)
            seen.add(n)
    resonance = resonance[:2]

    pd_desc = _PD_DESCRIPTORS_V2.get(pd, "personal focus")
    pm_desc = _PM_DESCRIPTORS_V2.get(pm, "monthly cycle")

    # Deterministic opener variation: rotate by (lp % 3)
    _openers = [
        f"Life Path {lp} is your numerological constant — it grounds every reading.",
        f"Every day you carry Life Path {lp} as your baseline vibration.",
        f"Your Life Path of {lp} doesn't shift with the calendar — it's the stable root here.",
    ]
    opener = _openers[lp % 3]

    why = (
        f"{opener} "
        f"Personal Day {pd} adds the quality of {pd_desc}. "
        f"Personal Month {pm} sets the wider current of {pm_desc}. "
        f"The universal day number ({ud}) reflects the shared vibration of today's date."
    )
    if planet_num:
        why += (
            f" {ruler}'s traditional correspondence is {planet_num} — "
            f"it lands in the resonance tier as a planetary echo for today."
        )

    # Deterministic how_to_use variation by pd parity
    if pd % 2 == 1:
        how = (
            f"Keep {core} front of mind as a quiet reference point today — "
            f"in timing, choices, or setting an intention before you start work. "
            f"The support numbers ({', '.join(str(n) for n in support)}) are useful when deciding between two paths."
        )
    else:
        how = (
            f"Anchor to {core} for anything that needs a clear decision today. "
            f"Lean on {support[0] if support else core} when collaborating or weighing input from others. "
            f"The resonance numbers sit in the background — notice if they show up."
        )

    return {
        "headline": "Today's resonance numbers",
        "selection": {"core": core, "support": support, "resonance": resonance},
        "why_it_matches": why,
        "how_to_use": how,
        "basis": "numerology-based",
        "trust_level": "full",
        "reason_factors": [
            _rf("life_path", lp),
            _rf("personal_day", pd),
            _rf("personal_month", pm),
            _rf("universal_day", ud),
            _rf("calendar_reduction", cr),
            _rf("day_ruler", ruler),
        ],
    }


# ---------------------------------------------------------------------------
# FEATURE 2 — Lucky Color (planet × element × moon-sign tone)
# ---------------------------------------------------------------------------

_COLOR_PALETTE_V2: Dict[str, Dict[str, tuple]] = {
    "Sun": {
        "Fire": ("Gold", "#FFD700", "Amber", "#FFBF00"),
        "Earth": ("Warm Gold", "#C9A84C", "Olive", "#808000"),
        "Air": ("Pale Gold", "#FAD02C", "Ivory", "#FFFFF0"),
        "Water": ("Champagne", "#F7E7CE", "Teal", "#008080"),
    },
    "Moon": {
        "Fire": ("Pearl", "#F8F6F0", "Coral", "#FF7F50"),
        "Earth": ("Moonstone", "#C6D4E1", "Sage", "#9CAF88"),
        "Air": ("Silver", "#C0C0C0", "Lavender", "#E6E6FA"),
        "Water": ("Seafoam", "#93E9BE", "Deep Purple", "#673AB7"),
    },
    "Mars": {
        "Fire": ("Crimson", "#DC143C", "Rust", "#B7410E"),
        "Earth": ("Terracotta", "#E2725B", "Chocolate", "#7B3F00"),
        "Air": ("Ruby Red", "#E0115F", "Sky Blue", "#87CEEB"),
        "Water": ("Deep Red", "#8B0000", "Teal", "#008080"),
    },
    "Mercury": {
        "Fire": ("Sunset Orange", "#FF4500", "Yellow", "#FFFF00"),
        "Earth": ("Olive", "#808000", "Tan", "#D2B48C"),
        "Air": ("Sky Blue", "#87CEEB", "Mint", "#98FF98"),
        "Water": ("Aqua", "#00FFFF", "Lavender", "#E6E6FA"),
    },
    "Jupiter": {
        "Fire": ("Royal Blue", "#4169E1", "Gold", "#FFD700"),
        "Earth": ("Forest Green", "#228B22", "Royal Blue", "#4169E1"),
        "Air": ("Indigo", "#4B0082", "Silver", "#C0C0C0"),
        "Water": ("Ocean Blue", "#0077BE", "Deep Purple", "#673AB7"),
    },
    "Venus": {
        "Fire": ("Rose", "#FF007F", "Ruby Red", "#E0115F"),
        "Earth": ("Rose Gold", "#B76E79", "Forest Green", "#228B22"),
        "Air": ("Lavender", "#E6E6FA", "Light Pink", "#FFB6C1"),
        "Water": ("Seafoam", "#93E9BE", "Rose", "#FF007F"),
    },
    "Saturn": {
        "Fire": ("Charcoal", "#36454F", "Crimson", "#DC143C"),
        "Earth": ("Slate", "#708090", "Chocolate", "#7B3F00"),
        "Air": ("Indigo", "#4B0082", "Silver", "#C0C0C0"),
        "Water": ("Dark Blue", "#00008B", "Teal", "#008080"),
    },
}

_MOON_ELEM_TONE: Dict[str, str] = {
    "Fire": "vibrant and action-forward tones",
    "Earth": "grounded, rich, and tactile tones",
    "Air": "lighter, airy, and communicative tones",
    "Water": "cool, fluid, and emotionally resonant tones",
}

_RULER_ADJ: Dict[str, str] = {
    "Sun": "solar and radiant",
    "Moon": "lunar and reflective",
    "Mars": "dynamic and assertive",
    "Mercury": "communicative and quick",
    "Jupiter": "expansive and generous",
    "Venus": "harmonious and sensory",
    "Saturn": "structured and grounding",
}

_SIGN_ELEM: Dict[str, str] = {
    "Aries": "Fire",
    "Leo": "Fire",
    "Sagittarius": "Fire",
    "Taurus": "Earth",
    "Virgo": "Earth",
    "Capricorn": "Earth",
    "Gemini": "Air",
    "Libra": "Air",
    "Aquarius": "Air",
    "Cancer": "Water",
    "Scorpio": "Water",
    "Pisces": "Water",
}


def get_lucky_color_guidance(context: Dict) -> Dict:
    """
    Lucky-color guidance: day ruler × dominant element, toned by Moon sign element.
    """
    ruler = context["day_ruler"]
    element = context["dominant_element"]
    moon_sign = context["moon_sign"]

    row = _COLOR_PALETTE_V2.get(ruler, _COLOR_PALETTE_V2["Sun"])
    palette = row.get(element, row.get("Fire"))
    power_color, power_hex, accent, accent_hex = palette

    moon_element = _SIGN_ELEM.get(moon_sign, "Water")
    moon_tone = _MOON_ELEM_TONE.get(moon_element, "balanced tones")
    ruler_adj = _RULER_ADJ.get(ruler, "planetary")

    if moon_element == element:
        blend = (
            f"The Moon is in {moon_sign} — same element as yours, "
            f"so today's palette runs deeper and more coherent than usual."
        )
    else:
        blend = (
            f"The Moon is currently in {moon_sign}, bringing {moon_tone} "
            f"alongside the primary palette — a complementary layer rather than a clash."
        )

    # Water opener: avoid repeating ruler_adj since "and receptive" is already implied
    # Earth+Sun: "measured, solar and radiant" contradicts — use neutral for Sun on Earth
    if element == "Earth" and ruler == "Sun":
        _water_or_earth_sun = (
            f"{ruler} brings its direct quality to the day — clear and present."
        )
    else:
        _water_or_earth_sun = (
            f"{ruler} holds today's atmosphere — quiet and receptive in register."
            if ruler in ("Moon", "Saturn", "Venus")
            else f"{ruler} shapes today's tone — {ruler_adj}, with a receptive undertone."
        )
    _elem_openers = {
        "Fire": f"{ruler} rules today, favouring bold, dynamic energy.",
        "Earth": (
            f"{ruler} brings its direct quality to the day — clear and present."
            if ruler == "Sun"
            else f"{ruler} sets today's tone — measured, {ruler_adj} in quality."
        ),
        "Air": f"{ruler} governs the day, lending it a {ruler_adj} character.",
        "Water": _water_or_earth_sun,
    }
    opener = _elem_openers.get(
        element, f"{ruler} rules today, favouring {ruler_adj} energy."
    )

    why = (
        f"{opener} "
        f"Your {element} chart signature narrows that to a specific shade within the family. "
        f"{blend}"
    )

    # Deterministic how_to_use by ruler
    _color_how = {
        "Sun": f"Lead with {power_color} — make it your most visible colour today.",
        "Moon": f"Bring {power_color} close to your skin or workspace; {accent} works for the periphery.",
        "Mars": f"Wear {power_color} where it can be seen — it reinforces decisive action.",
        "Mercury": f"{power_color} near your workspace or on what you carry sharpens the signal today.",
        "Jupiter": f"Use {power_color} as a statement — it aligns with today's expansive register.",
        "Venus": f"{power_color} anywhere it touches your direct environment. {accent} as a quiet accent.",
        "Saturn": f"{power_color} works best in grounded details — a bag, notebook, or what you wear closest.",
    }
    how = _color_how.get(
        ruler,
        f"Wear {power_color} as your dominant tone today; use {accent} in details.",
    )

    return {
        "headline": "Today's colours",
        "selection": {
            "power_color": power_color,
            "power_hex": power_hex,
            "support_accent": accent,
            "accent_hex": accent_hex,
        },
        "why_it_matches": why,
        "how_to_use": how,
        "basis": "astro-symbolic blend",
        "trust_level": "full",
        "reason_factors": [
            _rf("day_ruler", ruler),
            _rf("dominant_element", element),
            _rf("moon_sign", moon_sign),
            _rf("moon_element", moon_element),
        ],
    }


# ---------------------------------------------------------------------------
# FEATURE 3 — Affirmation (structured templates)
# ---------------------------------------------------------------------------

_PD_THEME_V2: Dict[int, str] = {
    1: "action",
    2: "emotional_grounding",
    3: "expression",
    4: "structure",
    5: "freedom",
    6: "connection",
    7: "rest",
    8: "focus",
    9: "completion",
}

_MOON_MOOD_V2: Dict[str, str] = {
    "Aries": "active",
    "Leo": "warm",
    "Sagittarius": "bold",
    "Taurus": "steady",
    "Virgo": "precise",
    "Capricorn": "disciplined",
    "Gemini": "curious",
    "Libra": "harmonious",
    "Aquarius": "independent",
    "Cancer": "nurturing",
    "Scorpio": "intense",
    "Pisces": "intuitive",
}

_AFFIRMATION_ANCHORS_V2: Dict[tuple, str] = {
    ("action", "Fire"): "I move forward with intention and trust my instincts.",
    ("action", "Earth"): "I take grounded, deliberate steps toward what matters.",
    ("action", "Air"): "I act on my ideas before overthinking takes over.",
    ("action", "Water"): "I let my values move me into clear, purposeful action.",
    ("expression", "Fire"): "I speak and create from my most authentic self today.",
    ("expression", "Earth"): "I express myself with honesty and quiet confidence.",
    ("expression", "Air"): "My words and ideas flow freely and land with clarity.",
    ("expression", "Water"): "I share what I feel, without apology or restraint.",
    (
        "emotional_grounding",
        "Fire",
    ): "I feel deeply and channel emotion into forward movement.",
    (
        "emotional_grounding",
        "Earth",
    ): "I am steady in my feelings and patient with myself.",
    (
        "emotional_grounding",
        "Air",
    ): "I observe my emotions without being swept away by them.",
    (
        "emotional_grounding",
        "Water",
    ): "I honour what I feel and let it move through me gently.",
    ("structure", "Fire"): "I channel my energy into systems that sustain my vision.",
    ("structure", "Earth"): "I build with care, consistency, and long-term thinking.",
    ("structure", "Air"): "I organise my ideas into plans that actually work.",
    (
        "structure",
        "Water",
    ): "I create gentle structures that hold my inner world steady.",
    ("freedom", "Fire"): "I embrace change as fuel, not as threat.",
    (
        "freedom",
        "Earth",
    ): "I release what no longer serves and make room for what does.",
    ("freedom", "Air"): "I explore with curiosity and stay open to new directions.",
    (
        "freedom",
        "Water",
    ): "I flow with the current and trust where change is taking me.",
    ("connection", "Fire"): "I show up boldly and generously in my relationships.",
    (
        "connection",
        "Earth",
    ): "I nurture the people and bonds that ground and sustain me.",
    (
        "connection",
        "Air",
    ): "I listen as much as I speak, and meet others with openness.",
    ("connection", "Water"): "I give and receive care with an open, aware heart.",
    ("rest", "Fire"): "I pause and restore so my fire burns steady, not frantic.",
    ("rest", "Earth"): "I allow myself to be still — stillness is not stagnation.",
    ("rest", "Air"): "I quiet my mind and let clarity arrive on its own.",
    ("rest", "Water"): "I rest deeply, trusting the process even when I cannot see it.",
    ("focus", "Fire"): "I direct my full energy at one thing today and let it matter.",
    ("focus", "Earth"): "I hold my focus through consistency, not force.",
    (
        "focus",
        "Air",
    ): "I choose one thread to follow rather than scattering in many directions.",
    ("focus", "Water"): "I tune into what truly calls me and let the rest recede.",
    ("completion", "Fire"): "I honour what I have built and release it with pride.",
    (
        "completion",
        "Earth",
    ): "I close what I have opened with care, and clear space for what's next.",
    (
        "completion",
        "Air",
    ): "I acknowledge the cycle ending and choose what to carry forward.",
    (
        "completion",
        "Water",
    ): "I release with gratitude and trust the space this creates.",
}

_PD_THEME_LABELS_V2: Dict[int, str] = {
    1: "initiation and self-direction",
    2: "cooperation and emotional sensitivity",
    3: "creative expression",
    4: "structure and disciplined effort",
    5: "flexibility and change",
    6: "nurturing and relational care",
    7: "inner reflection and rest",
    8: "focus and material ambition",
    9: "completion and release",
}


def get_affirmation_guidance(context: Dict) -> Dict:
    """
    Affirmation guidance from element + moon mood + personal-day theme.
    No random selection — (theme, element) pair is deterministic.
    """
    element = context["dominant_element"]
    moon_sign = context["moon_sign"]
    pd = context["personal_day"]

    theme = _PD_THEME_V2.get(pd, "focus")
    mood = _MOON_MOOD_V2.get(moon_sign, "steady")
    anchor = _AFFIRMATION_ANCHORS_V2.get(
        (theme, element), "I am present, grounded, and clear today."
    )

    pd_label = _PD_THEME_LABELS_V2.get(pd, "intentional living")
    moon_element = _SIGN_ELEM.get(moon_sign, "Water")

    # Deterministic sentence rhythm varies by (pd % 2) to avoid repetition across days
    _art = lambda w: "an" if w and w[0].lower() in "aeiou" else "a"
    if pd % 2 == 1:
        why = (
            f"Personal Day {pd} leans toward {pd_label}. "
            f"The Moon in {moon_sign} brings {_art(mood)} {mood} quality to the day's texture, "
            f"and your {element} nature shapes how both of those register for you."
        )
    else:
        why = (
            f"Today is {_art(pd_label)} {pd_label} kind of day numerologically — Personal Day {pd}. "
            f"{_art(mood).capitalize()} {mood} {moon_sign} Moon gives that its particular feeling, "
            f"filtered through your {element} way of moving through the world."
        )
    if moon_element == element:
        why += f" The Moon's {moon_element} quality matches yours today — the energy is unusually aligned."

    # Deterministic how_to_use variant by theme
    _aff_how = {
        "action": "Say it once before you start — then act. Don't return to it mid-task.",
        "emotional_grounding": "Write it by hand in the morning. Let it settle before your day begins.",
        "expression": "Say it aloud. The voice matters for this theme — not just reading it silently.",
        "structure": "Write it at the top of your task list. It works as an intention, not decoration.",
        "freedom": "Read it when you feel stuck or boxed in. That's exactly when it's meant to land.",
        "connection": "Hold it in mind before any significant conversation today.",
        "rest": "Return to it when the day pulls you into doing mode. It's a permission slip.",
        "focus": "Write it once and put it somewhere you'll see it during work — not on your phone.",
        "completion": "Read it at the end of the day, not the start. It's meant to close, not open.",
    }
    how = _aff_how.get(
        theme, "Say it once at the start of your day as a quiet orienting statement."
    )

    return {
        "headline": "Today's affirmation",
        "selection": {"anchor": anchor, "theme": theme},
        "why_it_matches": why,
        "how_to_use": how,
        "basis": "astro-symbolic blend",
        "trust_level": "full",
        "reason_factors": [
            _rf("personal_day", pd),
            _rf("personal_day_theme", theme),
            _rf("moon_sign", moon_sign),
            _rf("moon_mood", mood),
            _rf("dominant_element", element),
        ],
    }


# ---------------------------------------------------------------------------
# FEATURE 4 — Tarot (deterministic draw + astro-informed interpretation)
# ---------------------------------------------------------------------------

_PD_TRANSIT: Dict[int, str] = {
    1: "initiation",
    2: "connection",
    3: "expression",
    4: "structure",
    5: "transformation",
    6: "restoration",
    7: "reflection",
    8: "expression",
    9: "transformation",
}

_MOON_TRANSIT: Dict[str, str] = {
    "Aries": "initiation",
    "Leo": "expression",
    "Sagittarius": "transformation",
    "Taurus": "restoration",
    "Virgo": "structure",
    "Capricorn": "structure",
    "Gemini": "expression",
    "Libra": "connection",
    "Aquarius": "initiation",
    "Cancer": "restoration",
    "Scorpio": "transformation",
    "Pisces": "reflection",
}

_RULER_TRANSIT: Dict[str, str] = {
    "Sun": "expression",
    "Moon": "reflection",
    "Mars": "initiation",
    "Mercury": "expression",
    "Jupiter": "restoration",
    "Venus": "restoration",
    "Saturn": "structure",
}

_CARD_THEME_MAP: Dict[int, tuple] = {
    0: ("initiation", "restoration"),
    1: ("expression", "initiation"),
    2: ("reflection", "structure"),
    3: ("restoration", "expression"),
    4: ("structure", "initiation"),
    5: ("structure", "reflection"),
    6: ("connection", "restoration"),
    7: ("initiation", "expression"),
    8: ("restoration", "connection"),
    9: ("reflection", "structure"),
    10: ("transformation", "initiation"),
    11: ("structure", "reflection"),
    12: ("reflection", "transformation"),
    13: ("transformation", "initiation"),
    14: ("restoration", "structure"),
    15: ("reflection", "transformation"),
    16: ("transformation", "initiation"),
    17: ("restoration", "connection"),
    18: ("reflection", "transformation"),
    19: ("expression", "restoration"),
    20: ("transformation", "reflection"),
    21: ("restoration", "expression"),
}

_CARD_REFLECT_AVOID: Dict[int, tuple] = {
    0: (
        "What new chapter is quietly calling you?",
        "Pretending certainty you don't yet have.",
    ),
    1: (
        "What tool or resource have you been overlooking?",
        "Scattering effort across too many fronts.",
    ),
    2: (
        "What are you sensing but not yet saying aloud?",
        "Pushing for answers before they are ready.",
    ),
    3: (
        "Where can you invite more ease and nourishment today?",
        "Self-denial disguised as discipline.",
    ),
    4: (
        "What structure would make your day more grounded?",
        "Controlling through rigidity instead of clarity.",
    ),
    5: (
        "What teaching still genuinely serves you?",
        "Discarding wisdom just because it is old.",
    ),
    6: (
        "What choice today aligns with your deepest values?",
        "Making decisions against what you truly believe.",
    ),
    7: (
        "What goal deserves your focused, sustained momentum?",
        "Starting strong then allowing distraction to take over.",
    ),
    8: (
        "Where can patience serve you better than force today?",
        "Using pressure where presence would work better.",
    ),
    9: (
        "What inner answer are you ready to receive?",
        "Seeking external validation for something only you can know.",
    ),
    10: (
        "What cycle in your life is completing or beginning?",
        "Resisting movement already in motion.",
    ),
    11: (
        "Where in your life do you need more honest balance?",
        "Justifying imbalance by framing it as fairness.",
    ),
    12: (
        "What would change if you looked at this differently?",
        "Forcing resolution before perspective has shifted.",
    ),
    13: (
        "What must release so new life can come through?",
        "Clinging to a form the situation has already outgrown.",
    ),
    14: (
        "Where can you bring moderation without losing vitality?",
        "Swinging between extremes instead of finding middle ground.",
    ),
    15: (
        "What pattern is quietly limiting you?",
        "Avoiding an honest look at what holds you back.",
    ),
    16: (
        "What structure needs honest examination?",
        "Delaying necessary change until it becomes unavoidable.",
    ),
    17: (
        "What hope deserves quiet attention today?",
        "Dismissing hope as naïve without giving it a chance.",
    ),
    18: (
        "What does your instinct know that logic is ignoring?",
        "Over-analysing until clarity disappears.",
    ),
    19: (
        "What brings you genuine, uncomplicated joy right now?",
        "Dimming your energy to avoid being visible.",
    ),
    20: (
        "What chapter requests closure or honest recognition?",
        "Letting old guilt block forward movement.",
    ),
    21: (
        "What accomplishment have you not fully celebrated?",
        "Rushing to the next start before honouring the finish.",
    ),
}

_TRANSIT_LABEL_V2: Dict[str, str] = {
    "initiation": "starting or moving something new",
    "reflection": "introspection and inner knowing",
    "connection": "relating and heart-centred energy",
    "transformation": "release and significant change",
    "structure": "discipline and long-term building",
    "expression": "creativity and self-expression",
    "restoration": "healing and bringing things to harmony",
}

_MOON_PHASE_TONES: Dict[str, str] = {
    "New Moon": "new beginnings and planting intentions",
    "Waxing Crescent": "building momentum",
    "First Quarter": "decision and commitment",
    "Waxing Gibbous": "refinement and perseverance",
    "Full Moon": "culmination and heightened clarity",
    "Waning Gibbous": "reflection and sharing",
    "Last Quarter": "release and letting go",
    "Waning Crescent": "rest and renewal",
}


def _derive_transit_theme_v2(pd: int, moon_sign: str, ruler: str) -> str:
    from collections import Counter

    themes = [
        _PD_TRANSIT.get(pd, "reflection"),
        _MOON_TRANSIT.get(moon_sign, "reflection"),
        _RULER_TRANSIT.get(ruler, "expression"),
    ]
    count = Counter(themes)
    top, top_n = count.most_common(1)[0]
    return top if top_n >= 2 else _PD_TRANSIT.get(pd, "reflection")


def _moon_phase_tone_v2(phase: str) -> str:
    for key, tone in _MOON_PHASE_TONES.items():
        if key.lower() in phase.lower():
            return tone
    return "cyclical transition"


def get_tarot_guidance(context: Dict) -> Dict:
    """
    Tarot: deterministic card draw + astro-informed interpretation layer.

    The card is seeded by natal_sun + reference_date (deterministic).
    Only the interpretation adapts to today's astrological context.

    Honesty: the card is NOT astrologically selected.
    The reading is interpreted *through* the day's symbolic context.
    """
    pd = context["personal_day"]
    moon_sign = context["moon_sign"]
    ruler = context["day_ruler"]
    moon_phase = context.get("moon_phase", "")
    birth_time_trusted = context.get("birth_time_trusted", False)
    ref_date = context["reference_date"]
    name_seed = context.get("natal_sun", "cosmic")

    rng = _stable_rng("daily_tarot_v2", str(name_seed), str(ref_date))
    card_num = rng.randint(0, 21)
    is_reversed = rng.random() < 0.3

    card = MAJOR_ARCANA[card_num]
    card_name = card["name"]
    message = card["reversed"] if is_reversed else card["upright"]

    transit_theme = _derive_transit_theme_v2(pd, moon_sign, ruler)
    transit_label = _TRANSIT_LABEL_V2.get(transit_theme, "today's energy")

    primary_theme, secondary_theme = _CARD_THEME_MAP.get(
        card_num, ("reflection", "structure")
    )
    if transit_theme == primary_theme:
        frame = "This card and today's pattern are in direct conversation."
        alignment = "amplified"
    elif transit_theme == secondary_theme:
        frame = (
            "This card has a quieter but real connection to what today is emphasising."
        )
        alignment = "resonant"
    else:
        frame = "Today's energy pulls in a different direction to this card — worth holding both."
        alignment = "contrasting"

    orientation = "reversed" if is_reversed else "upright"
    mood = _MOON_MOOD_V2.get(moon_sign, "steady")

    _art = lambda w: "an" if w and w[0].lower() in "aeiou" else "a"
    why_parts = [frame]
    why_parts.append(
        f"Personal Day {pd} carries {_art(transit_theme)} {transit_theme} quality today."
    )
    why_parts.append(
        f"The Moon is in {moon_sign}, giving the day {_art(mood)} {mood} undercurrent "
        f"that colours how this card's energy shows up."
    )
    if moon_phase:
        phase_tone = _moon_phase_tone_v2(moon_phase)
        why_parts.append(f"The {moon_phase} adds a background of {phase_tone}.")
    if is_reversed:
        why_parts.append(
            "The card comes reversed — its subtler or more challenging dimension is present today."
        )
    else:
        why_parts.append("The card is upright — its more direct meaning is available.")
    why = " ".join(why_parts)

    reflect_on, avoid = _CARD_REFLECT_AVOID.get(
        card_num, (card["advice"], "Ignoring what this card surfaces.")
    )
    if alignment == "contrasting":
        reflect_on = (
            f"That tension can be clarifying — {reflect_on[0].lower()}{reflect_on[1:]}"
        )

    reason_factors = [
        _rf("personal_day", pd),
        _rf("transit_theme", transit_theme),
        _rf("moon_sign", moon_sign),
        _rf("day_ruler", ruler),
        _rf("card_number", card_num),
        _rf("reversed", is_reversed),
        _rf("card_alignment", alignment),
    ]
    if not birth_time_trusted:
        reason_factors.append(
            _rf("note", "birth_time not trusted — house context excluded")
        )

    return {
        "headline": "Today's card",
        "selection": {
            "card": card_name,
            "card_number": card_num,
            "reversed": is_reversed,
        },
        "keywords": card["keywords"],
        "message": message,
        "why_it_matches": why,
        "honesty_note": (
            "The card is drawn through a date-seeded process — not chosen astrologically. "
            "What the astrological context adds is a lens for reading it, not a selection mechanism."
        ),
        "how_to_use": (
            "Sit with the image for a moment before you read anything into it. "
            "Treat the reflection question as the main event — the card is context, not conclusion."
        ),
        "reflect_on": reflect_on,
        "avoid": avoid,
        "transit_theme": transit_theme,
        "basis": "symbolic guidance",
        "trust_level": _trust_level_from_ctx(context),
        "reason_factors": reason_factors,
    }


# ---------------------------------------------------------------------------
# FEATURE 5 — Birthstone (chart-informed ranking)
# ---------------------------------------------------------------------------

_RULER_STONE_V2: Dict[str, tuple] = {
    "Sun": ("Sunstone", "☀️", "Channels solar confidence and vitality."),
    "Moon": ("Moonstone", "🌙", "Supports lunar intuition and emotional depth."),
    "Mercury": ("Agate", "🔵", "Sharpens clarity and communication."),
    "Venus": ("Rose Quartz", "🌸", "Opens the heart to harmony and self-love."),
    "Mars": ("Carnelian", "🟠", "Fuels courage, drive, and decisive action."),
    "Jupiter": ("Citrine", "🌟", "Attracts abundance and expands possibility."),
    "Saturn": ("Obsidian", "⚫️", "Grounds, protects, and clarifies."),
}

_ELEMENT_STONE_V2: Dict[str, tuple] = {
    "Fire": ("Carnelian", "🟠", "Sustains Fire's bold, initiating energy."),
    "Earth": ("Moss Agate", "🍃", "Anchors Earth's patient, sustaining nature."),
    "Air": ("Citrine", "🌟", "Brightens Air's mental clarity and optimism."),
    "Water": ("Aquamarine", "🩵", "Supports Water's emotional flow and intuition."),
}

_NATAL_MOON_STONE_V2: Dict[str, tuple] = {
    "Aries": ("Bloodstone", "🟢", "Grounds Aries Moon courage and initiative."),
    "Taurus": ("Rose Quartz", "🌸", "Deepens Taurus Moon's love of comfort."),
    "Gemini": ("Tiger's Eye", "🐯", "Focuses Gemini Moon's quicksilver energy."),
    "Cancer": ("Moonstone", "🌙", "Resonates with Cancer Moon's emotional nature."),
    "Leo": ("Peridot", "💛", "Amplifies Leo Moon's warmth and generosity."),
    "Virgo": ("Amazonite", "🩵", "Soothes Virgo Moon's self-critical edge."),
    "Libra": ("Lapis Lazuli", "🔵", "Supports Libra Moon's search for balance."),
    "Scorpio": ("Obsidian", "⚫️", "Protects Scorpio Moon's psychic depth."),
    "Sagittarius": ("Turquoise", "🩵", "Expands Sagittarius Moon's adventurous spirit."),
    "Capricorn": ("Garnet", "❤️", "Sustains Capricorn Moon's steady ambition."),
    "Aquarius": ("Amethyst", "💜", "Heightens Aquarius Moon's visionary intuition."),
    "Pisces": ("Fluorite", "💚", "Brings clarity to Pisces Moon's dreamy receptivity."),
}

_LIFE_PATH_STONE_V2: Dict[int, tuple] = {
    1: ("Ruby", "🔴", "Amplifies Life Path 1's courage and self-leadership."),
    2: ("Moonstone", "🌙", "Supports Life Path 2's sensitivity and cooperation."),
    3: ("Citrine", "🌟", "Fuels Life Path 3's creative joy."),
    4: ("Smoky Quartz", "🤎", "Grounds Life Path 4's need for stability."),
    5: ("Turquoise", "🩵", "Supports Life Path 5's adventurous freedom."),
    6: ("Emerald", "💚", "Strengthens Life Path 6's nurturing nature."),
    7: ("Amethyst", "💜", "Deepens Life Path 7's spiritual inquiry."),
    8: ("Onyx", "⚫️", "Steadies Life Path 8's ambitious drive."),
    9: ("Opal", "🌈", "Reflects Life Path 9's compassionate universality."),
    11: ("Selenite", "🤍", "Amplifies Life Path 11's intuitive illumination."),
    22: ("Malachite", "🌿", "Supports Life Path 22's master-building vision."),
    33: ("Clear Quartz", "⚪️", "Holds Life Path 33's devoted service energy."),
}

_DAY_SUPPORT_STONE_V2: Dict[str, tuple] = {
    "Sun": (
        "Sunstone",
        "☀️",
        "Today's solar energy supports confident, visible action.",
    ),
    "Moon": (
        "Selenite",
        "🤍",
        "Today's lunar tone supports emotional clarity and calm.",
    ),
    "Mars": (
        "Red Jasper",
        "🔴",
        "Today's Martian tone supports sustained, grounded effort.",
    ),
    "Mercury": (
        "Agate",
        "🔵",
        "Today's Mercurial tone sharpens communication and thought.",
    ),
    "Jupiter": (
        "Lapis Lazuli",
        "🔵",
        "Today's Jupiterian energy supports expansion and optimism.",
    ),
    "Venus": (
        "Rose Quartz",
        "🌸",
        "Today's Venusian tone supports openness in relationships.",
    ),
    "Saturn": (
        "Smoky Quartz",
        "🤎",
        "Today's Saturnian energy supports focus and groundedness.",
    ),
}


def get_birthstone_guidance(context: Dict) -> Dict:
    """
    Chart-informed birthstone guidance.

    Primary stone ranking (priority):
      1. Chart ruler (only if birth_time_trusted)
      2. Natal Moon sign
      3. Dominant element
      4. Life path

    Support stone: day-ruler correspondence (today only), deduped from primary.
    Primary is intentionally stable for the same user.
    """
    birth_time_trusted = context.get("birth_time_trusted", False)
    chart_ruler = context.get("chart_ruler")
    natal_asc = context.get("natal_ascendant")
    natal_moon = context.get("natal_moon")
    element = context["dominant_element"]
    lp = context["life_path"]
    ruler = context["day_ruler"]

    # ── Primary stone ────────────────────────────────────────────────────
    primary_stone = None
    primary_basis = "element-supported"
    primary_detail = ""

    if birth_time_trusted and chart_ruler and chart_ruler in _RULER_STONE_V2:
        s = _RULER_STONE_V2[chart_ruler]
        primary_stone = s
        primary_basis = "chart-informed"
        asc_note = f" (via {natal_asc})" if natal_asc else ""
        primary_detail = (
            f"Your chart ruler is {chart_ruler}{asc_note}. "
            f"{s[0]} is a strong long-term resonance stone for this placement."
        )
    elif natal_moon and natal_moon in _NATAL_MOON_STONE_V2:
        s = _NATAL_MOON_STONE_V2[natal_moon]
        primary_stone = s
        primary_basis = "natal-moon-informed"
        primary_detail = f"Your natal Moon in {natal_moon} gives {s[0]} a lasting personal resonance."
    elif element in _ELEMENT_STONE_V2:
        s = _ELEMENT_STONE_V2[element]
        primary_stone = s
        primary_basis = "element-supported"
        primary_detail = (
            f"Your dominant {element} element aligns naturally with {s[0]}."
        )
    else:
        lp_key = lp if lp in _LIFE_PATH_STONE_V2 else (lp % 9 or 9)
        s = _LIFE_PATH_STONE_V2.get(
            lp_key, ("Moonstone", "🌙", "Supports your energetic pattern.")
        )
        primary_stone = s
        primary_basis = "numerology-supported"
        primary_detail = f"Your Life Path {lp} provides the anchor for {s[0]}."

    # ── Support stone: today's day ruler ────────────────────────────────
    support_data = _DAY_SUPPORT_STONE_V2.get(ruler, _DAY_SUPPORT_STONE_V2["Moon"])
    if support_data[0] == primary_stone[0]:
        for candidate in [
            _NATAL_MOON_STONE_V2.get(natal_moon or "Cancer"),
            _ELEMENT_STONE_V2.get(element),
            _LIFE_PATH_STONE_V2.get(lp % 9 or 9),
        ]:
            if candidate and candidate[0] != primary_stone[0]:
                support_data = (
                    candidate[0],
                    candidate[1],
                    f"Supports today's overall energy alongside {primary_stone[0]}.",
                )
                break

    trust_level = "full" if birth_time_trusted else "limited"
    trust_note = (
        None
        if birth_time_trusted
        else "Without a confirmed birth time, Ascendant-based logic isn't used here. "
        "The stone selection draws on your natal Moon and element — "
        "inputs that hold regardless of birth time."
    )

    # Deterministic why — opener sets context, primary_detail adds specifics without repeating the opener
    _why_openers = {
        "chart-informed": f"Your primary stone comes from your chart ruler, {chart_ruler} — a placement that doesn't change with the calendar.",
        "natal-moon-informed": f"For stone resonance, your natal Moon sign carries more weight than your Sun sign.",
        "element-supported": f"Without a time-confirmed chart, your {element} element is the clearest stable anchor.",
        "numerology-supported": f"Life Path {lp} is the stable numerological ground this selection builds from.",
    }
    why_opener = _why_openers.get(
        primary_basis,
        f"Your primary stone reflects your chart's dominant signature ({primary_basis}).",
    )

    why = (
        f"{why_opener} "
        f"{primary_detail} "
        f"The support stone is keyed to {ruler}'s influence today — it shifts with the calendar."
    )

    reason_factors = [
        _rf("dominant_element", element),
        _rf("natal_moon", natal_moon),
        _rf("life_path", lp),
        _rf("day_ruler", ruler),
        _rf("birth_time_trusted", birth_time_trusted),
        _rf("primary_basis", primary_basis),
    ]
    if birth_time_trusted and chart_ruler:
        reason_factors.insert(0, _rf("chart_ruler", chart_ruler))

    # Deterministic how_to_use varies by primary_basis
    _stone_how = {
        "chart-informed": (
            f"Keep {primary_stone[0]} as your regular stone — it reflects something stable in your chart, "
            f"not just today. Reach for {support_data[0]} when today's {ruler} quality asks for it."
        ),
        "natal-moon-informed": (
            f"{primary_stone[0]} is anchored to your natal Moon in {natal_moon or 'its sign'} — "
            f"carry it for the long term, not just today. "
            f"{support_data[0]} is the addition specific to this {ruler}-ruled day."
        ),
        "element-supported": (
            f"Your {element} element makes {primary_stone[0]} a reliable companion across seasons, "
            f"not just today. Use {support_data[0]} for the particular tone this {ruler}-ruled day brings."
        ),
        "numerology-supported": (
            f"{primary_stone[0]} works with your Life Path {lp} pattern — carry it consistently. "
            f"{support_data[0]} is a lighter, daily addition for today's specific energy."
        ),
    }
    how = _stone_how.get(
        primary_basis,
        f"Keep {primary_stone[0]} nearby as your regular anchor. Use {support_data[0]} for today's particular atmosphere.",
    )

    result = {
        "headline": "Today's stones",
        "selection": {
            "primary": {
                "name": primary_stone[0],
                "emoji": primary_stone[1],
                "why_chosen": primary_detail,
                "when_to_use": "Your regular, ongoing stone — not just for today.",
                "basis": primary_basis,
            },
            "support": {
                "name": support_data[0],
                "emoji": support_data[1],
                "why_chosen": support_data[2],
                "when_to_use": f"Specific to today — especially around {ruler.lower()}-quality moments.",
                "basis": "astro-symbolic blend",
            },
        },
        "why_it_matches": why,
        "how_to_use": how,
        "basis": primary_basis,
        "trust_level": trust_level,
        "reason_factors": reason_factors,
    }
    if trust_note:
        result["trust_note"] = trust_note
    return result


# ---------------------------------------------------------------------------
# Convenience — all five from one AstroContext call
# ---------------------------------------------------------------------------


def get_all_guidance(context: Dict) -> Dict:
    """
    Return all five astrology-informed guidance outputs in one call.

    Parameters
    ----------
    context : dict
        AstroContext dict from astro_context.build_astro_context().
    """
    return {
        "lucky_number": get_lucky_number_guidance(context),
        "lucky_color": get_lucky_color_guidance(context),
        "affirmation": get_affirmation_guidance(context),
        "tarot": get_tarot_guidance(context),
        "birthstone": get_birthstone_guidance(context),
    }
