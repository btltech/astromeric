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


def _stable_seed(*parts: object) -> int:
    """Return a cross-process deterministic integer seed from the provided parts."""
    payload = "||".join(str(part) for part in parts)
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


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
    dob_parts = dob.split("-")

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
    birth_year_sum = (
        sum(int(d) for d in dob_parts[0]) if len(dob_parts) == 3 else life_path
    )
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
        (life_path + personal_day + month_blend) % 9 or 9,
        (expression + universal + reference_date.month) % 9 or 9,
        (life_path + reference_date.day) % 9 or 9,
        (birth_year_sum + universal) % 9 or 9,
    ]
    for e in extras:
        if len(lucky) >= 5:
            break
        if e not in lucky:
            lucky.append(e)

    if len(lucky) < 5:
        for candidate in range(1, 10):
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

    # Accent: personal day number shifts through accent list
    digits_today = [int(d) for d in reference_date.isoformat().replace("-", "")]
    pd_raw = personal_day or (sum(digits_today) % 9 or 9)
    accent_idx = _PD_ACCENT_SHIFT.get(pd_raw, 0) % len(colors["accent"])
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
    rng = random.Random(
        _stable_seed(
            "affirmation", element, life_path, reference_date.isoformat(), lang
        )
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
    rng = random.Random(_stable_seed("tarot", name, reference_date.isoformat(), lang))

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
    rng = random.Random(
        _stable_seed(
            "oracle",
            question.strip().lower(),
            reference_date.isoformat(),
            dob or "",
            lang,
        )
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
    rng = random.Random(
        _stable_seed(
            "manifestation", life_path, personal_day, reference_date.isoformat(), lang
        )
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
    rng = random.Random(
        _stable_seed(
            "mood",
            element,
            life_path,
            personal_day,
            reference_date.isoformat(),
            lang,
            personal_year,
        )
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


# ========== ASTRO CONTEXT GUIDANCE CONTRACT ==========

_PD_THEME_V2 = {
    1: "initiative",
    2: "connection",
    3: "expression",
    4: "stability",
    5: "change",
    6: "care",
    7: "reflection",
    8: "ambition",
    9: "completion",
}

_BIRTHSTONE_BY_SIGN = {
    "Aries": {"name": "Diamond", "color": "Clear", "keywords": ["clarity", "courage"]},
    "Taurus": {
        "name": "Emerald",
        "color": "Green",
        "keywords": ["growth", "steadiness"],
    },
    "Gemini": {
        "name": "Agate",
        "color": "Layered Blue",
        "keywords": ["language", "adaptability"],
    },
    "Cancer": {
        "name": "Moonstone",
        "color": "Pearl White",
        "keywords": ["intuition", "protection"],
    },
    "Leo": {
        "name": "Peridot",
        "color": "Solar Green",
        "keywords": ["warmth", "confidence"],
    },
    "Virgo": {
        "name": "Sapphire",
        "color": "Blue",
        "keywords": ["discernment", "craft"],
    },
    "Libra": {"name": "Opal", "color": "Iridescent", "keywords": ["balance", "beauty"]},
    "Scorpio": {"name": "Topaz", "color": "Amber", "keywords": ["depth", "renewal"]},
    "Sagittarius": {
        "name": "Turquoise",
        "color": "Blue Green",
        "keywords": ["vision", "truth"],
    },
    "Capricorn": {
        "name": "Garnet",
        "color": "Deep Red",
        "keywords": ["discipline", "endurance"],
    },
    "Aquarius": {
        "name": "Amethyst",
        "color": "Violet",
        "keywords": ["insight", "originality"],
    },
    "Pisces": {
        "name": "Aquamarine",
        "color": "Sea Blue",
        "keywords": ["compassion", "flow"],
    },
}

_SUPPORT_STONE_BY_RULER = {
    "Sun": {"name": "Citrine", "color": "Gold", "keywords": ["radiance", "visibility"]},
    "Moon": {
        "name": "Pearl",
        "color": "White",
        "keywords": ["softness", "receptivity"],
    },
    "Mars": {
        "name": "Carnelian",
        "color": "Orange Red",
        "keywords": ["drive", "action"],
    },
    "Mercury": {
        "name": "Fluorite",
        "color": "Green Purple",
        "keywords": ["clarity", "learning"],
    },
    "Jupiter": {
        "name": "Lapis Lazuli",
        "color": "Royal Blue",
        "keywords": ["wisdom", "expansion"],
    },
    "Venus": {
        "name": "Rose Quartz",
        "color": "Pink",
        "keywords": ["harmony", "affection"],
    },
    "Saturn": {
        "name": "Smoky Quartz",
        "color": "Smoky Brown",
        "keywords": ["focus", "boundaries"],
    },
}

_TAROT_TRANSIT_THEME = {
    "Fire": "act with purpose",
    "Earth": "build something tangible",
    "Air": "name the pattern clearly",
    "Water": "trust the emotional signal",
}

_PLANET_NUMBER_MAP = {
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


def _reason_factor(factor_type: str, value: str, note: str) -> Dict:
    return {"type": factor_type, "value": value, "note": note}


def _unique_numbers(*groups: List[int]) -> List[int]:
    seen = set()
    ordered: List[int] = []
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                ordered.append(value)
    return ordered


def get_lucky_number_guidance(ctx: Dict) -> Dict:
    life_path = ctx["life_path"]
    personal_day = ctx["personal_day"]
    support = _unique_numbers(
        [
            ctx["personal_month"],
            ctx["universal_day"],
            ctx["calendar_reduction"],
        ]
    )
    support = [num for num in support if num != life_path][:2]

    ruler_num = _PLANET_NUMBER_MAP.get(ctx["day_ruler"], 1)
    resonance = _unique_numbers([ruler_num, ctx["personal_year"], personal_day])
    resonance = [num for num in resonance if num not in {life_path, *support}][:2]

    return {
        "headline": f"Lucky Number Focus: {life_path}",
        "selection": {
            "core": life_path,
            "support": support,
            "resonance": resonance,
        },
        "why_it_matches": f"Life Path {life_path} is your core numerology anchor, while today's supporting numbers echo your personal day and calendar rhythm.",
        "how_to_use": "Use the core number for your main decision or intention, and treat the support and resonance numbers as secondary timing cues.",
        "basis": "numerology-based",
        "trust_level": "high",
        "reason_factors": [
            _reason_factor("life_path", str(life_path), "Primary soul-pattern number."),
            _reason_factor(
                "personal_day", str(personal_day), "Today's active numerology current."
            ),
            _reason_factor(
                "day_ruler", ctx["day_ruler"], "Planetary day resonance number."
            ),
        ],
    }


def get_lucky_color_guidance(ctx: Dict, lang: str = "en") -> Dict:
    colors = get_lucky_colors(
        ctx["dominant_element"],
        ctx["reference_date"],
        lang=lang,
        personal_day=ctx["personal_day"],
    )
    return {
        "headline": f"Color Current: {colors['primary']}",
        "selection": {
            "power_color": colors["primary"],
            "power_hex": colors["primary_hex"],
            "accent_color": colors["accent"],
            "accent_hex": ELEMENT_COLORS.get(
                ctx["dominant_element"], ELEMENT_COLORS["Fire"]
            )["hex"].get(colors["primary"], colors["primary_hex"]),
        },
        "why_it_matches": f"{colors['primary']} tracks the {ctx['day_ruler']} day ruler through your {ctx['dominant_element']} element, while {colors['accent']} supports the tone of your Moon in {ctx['moon_sign']}.",
        "how_to_use": "Wear the power color close to the body, then use the accent in accessories, notes, or your digital workspace.",
        "basis": "astro-symbolic",
        "trust_level": "medium",
        "reason_factors": [
            _reason_factor(
                "day_ruler",
                ctx["day_ruler"],
                "Planetary ruler of the day picks the lead color.",
            ),
            _reason_factor(
                "dominant_element",
                ctx["dominant_element"],
                "Element palette anchors the recommendation.",
            ),
            _reason_factor(
                "moon_sign", ctx["moon_sign"], "Moon sign shapes the emotional accent."
            ),
        ],
    }


def get_affirmation_guidance(ctx: Dict) -> Dict:
    theme = _PD_THEME_V2.get(ctx["personal_day"], "balance")
    anchors = {
        "initiative": "I begin clearly and act without second-guessing.",
        "connection": "I listen well and choose responses that build trust.",
        "expression": "My voice is useful, timely, and honest today.",
        "stability": "I strengthen what matters through steady attention.",
        "change": "I move with change and keep my center.",
        "care": "I give care without abandoning my own needs.",
        "reflection": "Silence helps me hear the truth beneath the noise.",
        "ambition": "I handle power responsibly and follow through.",
        "completion": "I release what is finished and make room for what is next.",
    }
    anchor = anchors[theme]
    return {
        "headline": f"Affirmation Theme: {theme.title()}",
        "selection": {"anchor": anchor, "theme": theme},
        "why_it_matches": f"Your personal day {ctx['personal_day']} points to {theme}, and your {ctx['dominant_element']} emphasis suggests this line is most useful when spoken plainly rather than dramatically.",
        "how_to_use": "Repeat it three times before the first important task of the day, then once again when your attention scatters.",
        "basis": "numerology-led",
        "trust_level": "medium",
        "reason_factors": [
            _reason_factor(
                "personal_day",
                str(ctx["personal_day"]),
                "Sets the daily affirmation theme.",
            ),
            _reason_factor(
                "dominant_element",
                ctx["dominant_element"],
                "Shapes the tone of the wording.",
            ),
            _reason_factor(
                "moon_sign", ctx["moon_sign"], "Adds emotional texture to the anchor."
            ),
        ],
    }


def get_tarot_guidance(ctx: Dict, lang: str = "en") -> Dict:
    tarot = get_daily_tarot(ctx["reference_date"], str(ctx["life_path"]), lang=lang)
    transit_theme = _TAROT_TRANSIT_THEME.get(
        ctx["dominant_element"], "follow the clearest signal"
    )
    return {
        "headline": f"Tarot Card: {tarot['card']}",
        "selection": {
            "card": tarot["card"],
            "reversed": tarot["reversed"],
            "message": tarot["message"],
        },
        "why_it_matches": f"With the Moon in {ctx['moon_sign']}, this card reads through an emotional lens of {transit_theme}; the interpretation adapts to that atmosphere rather than claiming the sky chose the card itself.",
        "how_to_use": "Use the message as a reflection prompt, not a literal prediction. Notice where it mirrors the day's emotional weather.",
        "basis": "date-seeded symbolic reflection",
        "trust_level": "medium",
        "reason_factors": [
            _reason_factor(
                "reference_date",
                ctx["reference_date"].isoformat(),
                "Deterministic seed for the draw.",
            ),
            _reason_factor(
                "moon_sign", ctx["moon_sign"], "Shapes the interpretation tone."
            ),
            _reason_factor(
                "dominant_element",
                ctx["dominant_element"],
                "Adds a transit theme to the reflection.",
            ),
        ],
        "reflect_on": tarot["daily_advice"],
        "avoid": "Treating the card as proof that astrology literally selected it.",
        "transit_theme": transit_theme,
        "honesty_note": "This is a date-seeded tarot draw: deterministic for consistency, then interpreted through the current context.",
    }


def get_birthstone_guidance(ctx: Dict) -> Dict:
    primary = dict(
        _BIRTHSTONE_BY_SIGN.get(ctx["natal_sun"], _BIRTHSTONE_BY_SIGN["Aries"])
    )
    if ctx.get("birth_time_trusted") and ctx.get("chart_ruler"):
        primary["basis"] = "chart-informed"
    else:
        primary["basis"] = "sun-sign"

    support = dict(
        _SUPPORT_STONE_BY_RULER.get(ctx["day_ruler"], _SUPPORT_STONE_BY_RULER["Sun"])
    )
    if support["name"] == primary["name"]:
        support = dict(
            _SUPPORT_STONE_BY_RULER.get(
                ctx["chart_ruler"] or "Moon", _SUPPORT_STONE_BY_RULER["Moon"]
            )
        )
    support["basis"] = "day-ruler"

    result = {
        "headline": f"Stone Pairing: {primary['name']} + {support['name']}",
        "selection": {
            "primary": primary,
            "support": support,
        },
        "why_it_matches": f"{primary['name']} stays constant because it reflects your natal signature, while {support['name']} adjusts to the {ctx['day_ruler']} day ruler to support today's tone.",
        "how_to_use": "Keep the primary stone as your steady anchor and use the support stone when you need a small behavioral nudge during the day.",
        "basis": "symbolic correspondence",
        "trust_level": "medium",
        "reason_factors": [
            _reason_factor("natal_sun", ctx["natal_sun"], "Sets the primary stone."),
            _reason_factor("day_ruler", ctx["day_ruler"], "Shapes the support stone."),
            _reason_factor(
                "birth_time_trusted",
                str(ctx.get("birth_time_trusted")),
                "Controls whether chart-based logic is allowed.",
            ),
        ],
    }
    if not ctx.get("birth_time_trusted"):
        result[
            "trust_note"
        ] = "Birth time is not trusted, so this pairing avoids Ascendant or chart-ruler claims."
    return result


def get_all_guidance(ctx: Dict, lang: str = "en") -> Dict:
    return {
        "lucky_number": get_lucky_number_guidance(ctx),
        "lucky_color": get_lucky_color_guidance(ctx, lang=lang),
        "affirmation": get_affirmation_guidance(ctx),
        "tarot": get_tarot_guidance(ctx, lang=lang),
        "birthstone": get_birthstone_guidance(ctx),
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
        "lucky_colors": get_lucky_colors(element, today),
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
    seed = hash(
        f"{question or 'daily'}-{today.isoformat()}-{datetime.now().microsecond}"
    )
    random.seed(seed)

    card_num = random.randint(0, 21)
    is_reversed = random.random() < 0.3

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
    seed = hash(f"{question}-{today.isoformat()}-{birth_date or ''}")
    random.seed(seed)

    # Determine answer with cosmic reasoning
    answers = [
        {
            "answer": "Yes",
            "emoji": "✨",
            "confidence": random.randint(70, 95),
            "message": "The stars align in favor. Move forward with confidence.",
            "reasoning": "The cosmic energies support this path. Trust the universe's guidance.",
            "timing": "The timing feels right. Act within the next few days.",
        },
        {
            "answer": "Yes",
            "emoji": "🌟",
            "confidence": random.randint(55, 75),
            "message": "A soft yes. Proceed with awareness and intention.",
            "reasoning": "The energy is favorable but requires your conscious effort.",
            "timing": "Consider waiting until after the new moon for best results.",
        },
        {
            "answer": "No",
            "emoji": "🌑",
            "confidence": random.randint(70, 95),
            "message": "The cosmos advises against this path right now.",
            "reasoning": "There are unseen obstacles. This isn't a permanent no, just not now.",
            "timing": "Revisit this question in a lunar cycle.",
        },
        {
            "answer": "No",
            "emoji": "🌒",
            "confidence": random.randint(55, 75),
            "message": "Not at this moment. Patience may change the answer.",
            "reasoning": "The universe is redirecting you toward something better.",
            "timing": "Give it more time. The path will become clearer.",
        },
        {
            "answer": "Maybe",
            "emoji": "🔮",
            "confidence": random.randint(40, 60),
            "message": "The outcome depends on your actions. You have power here.",
            "reasoning": "This is a crossroads moment. Your choice shapes the outcome.",
            "timing": "Take action within 3 days to influence the outcome.",
        },
        {
            "answer": "Wait",
            "emoji": "⏳",
            "confidence": random.randint(50, 70),
            "message": "The timing isn't clear. Ask again when the moon shifts.",
            "reasoning": "More information needs to emerge before this can be answered.",
            "timing": "Ask again after the next major lunar phase.",
        },
    ]

    result = random.choice(answers)
    result["question"] = question
    result["asked_at"] = datetime.now().isoformat()

    return result


def get_mood_forecast(sun_sign: str, moon_sign: Optional[str] = None) -> Dict:
    """Get today's mood forecast based on astrological influences."""
    today = date.today()
    element = SIGN_ELEMENTS.get(sun_sign, "Fire")

    # Simple life path and personal day for forecasting
    seed = hash(f"{sun_sign}-{moon_sign or ''}-{today.isoformat()}")
    random.seed(seed)

    random.randint(1, 9)
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
    mood = random.choices(moods, weights=list(weights.values()))[0]
    forecast = MOOD_FORECASTS[mood]

    # Calculate energy score (1-10)
    base_score = random.randint(5, 8)
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
