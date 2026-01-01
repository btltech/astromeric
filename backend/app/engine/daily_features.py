"""
daily_features.py
-----------------
Daily features: lucky numbers, colors, planets, affirmations, tarot, manifestation prompts.
Adds entertainment value and reasons to return daily.
"""

from __future__ import annotations

import random
from datetime import datetime, date
from typing import Dict, List, Optional
from app.interpretation.translations import get_translation

# ========== LUCKY NUMBERS ==========

def calculate_lucky_numbers(dob: str, reference_date: date) -> List[int]:
    """Generate daily lucky numbers based on DOB and date."""
    seed = hash(f"{dob}-{reference_date.isoformat()}")
    random.seed(seed)
    
    # Always include life path influenced number
    life_path = sum(int(d) for d in dob.replace("-", "")) % 9 or 9
    
    lucky = [life_path]
    lucky.append(reference_date.day % 9 or 9)
    lucky.append((life_path + reference_date.month) % 9 or 9)
    
    # Add 2-3 random lucky numbers
    while len(lucky) < 5:
        num = random.randint(1, 99)
        if num not in lucky:
            lucky.append(num)
    
    return sorted(set(lucky))[:5]


# ========== LUCKY COLORS ==========

ELEMENT_COLORS = {
    "Fire": {
        "primary": ["Ruby Red", "Sunset Orange", "Gold", "Crimson"],
        "accent": ["White", "Yellow", "Coral"],
        "hex": {"Ruby Red": "#E0115F", "Sunset Orange": "#FF4500", "Gold": "#FFD700", "Crimson": "#DC143C"},
    },
    "Earth": {
        "primary": ["Forest Green", "Terracotta", "Chocolate Brown", "Olive"],
        "accent": ["Cream", "Sage", "Tan"],
        "hex": {"Forest Green": "#228B22", "Terracotta": "#E2725B", "Chocolate Brown": "#7B3F00", "Olive": "#808000"},
    },
    "Air": {
        "primary": ["Sky Blue", "Lavender", "Mint", "Silver"],
        "accent": ["White", "Light Pink", "Pale Yellow"],
        "hex": {"Sky Blue": "#87CEEB", "Lavender": "#E6E6FA", "Mint": "#98FF98", "Silver": "#C0C0C0"},
    },
    "Water": {
        "primary": ["Ocean Blue", "Seafoam", "Deep Purple", "Teal"],
        "accent": ["Pearl", "Moonstone", "Aqua"],
        "hex": {"Ocean Blue": "#0077BE", "Seafoam": "#93E9BE", "Deep Purple": "#673AB7", "Teal": "#008080"},
    },
}

def get_lucky_colors(element: str, reference_date: date, lang: str = "en") -> Dict:
    """Get daily lucky colors based on element and date."""
    seed = hash(f"{element}-{reference_date.isoformat()}")
    random.seed(seed)
    
    colors = ELEMENT_COLORS.get(element, ELEMENT_COLORS["Fire"])
    primary = random.choice(colors["primary"])
    accent = random.choice(colors["accent"])
    
    desc_trans = get_translation(lang, "lucky_color_desc")
    if desc_trans:
        description = desc_trans[0].format(primary=primary, accent=accent)
    else:
        description = f"Wear {primary} to amplify your energy, with touches of {accent} for balance."
    
    return {
        "primary": primary,
        "primary_hex": colors["hex"].get(primary, "#4ECDC4"),
        "accent": accent,
        "description": description,
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
    0: "Moon",     # Monday
    1: "Mars",     # Tuesday
    2: "Mercury",  # Wednesday
    3: "Jupiter",  # Thursday
    4: "Venus",    # Friday
    5: "Saturn",   # Saturday
    6: "Sun",      # Sunday
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
    seed = hash(f"{element}-{life_path}-{reference_date.isoformat()}")
    random.seed(seed)
    
    # Map elements and life paths to affirmation categories
    if element == "Fire" or life_path in [1, 3, 5]:
        category = random.choice(["confidence", "growth"])
    elif element == "Earth" or life_path in [4, 8]:
        category = random.choice(["abundance", "growth"])
    elif element == "Water" or life_path in [2, 6]:
        category = random.choice(["love", "peace"])
    else:
        category = random.choice(["peace", "growth"])
    
    # Try to get localized affirmations
    affirmations = get_translation(lang, f"affirmation_{category}")
    if not affirmations:
        affirmations = AFFIRMATION_TEMPLATES.get(category, AFFIRMATION_TEMPLATES["confidence"])
        
    affirmation = random.choice(affirmations)
    
    instr_trans = get_translation(lang, "affirmation_instruction")
    instruction = instr_trans[0] if instr_trans else "Repeat this 3 times each morning, feeling the words as truth."
    
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
    seed = hash(f"{name}-{reference_date.isoformat()}")
    random.seed(seed)
    
    card_num = random.randint(0, 21)
    is_reversed = random.random() < 0.3  # 30% chance reversed
    
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

def get_yes_no_oracle(question: str, reference_date: date, lang: str = "en") -> Dict:
    """Cosmic yes/no oracle for decision-making."""
    seed = hash(f"{question}-{reference_date.isoformat()}")
    random.seed(seed)
    
    # Define base answers
    base_answers = [
        {"key": "yes_strong", "answer": "Yes", "confidence": "strong", "default": "The stars align in favor. Move forward with confidence."},
        {"key": "yes_gentle", "answer": "Yes", "confidence": "gentle", "default": "A soft yes. Proceed with awareness and intention."},
        {"key": "no_strong", "answer": "No", "confidence": "strong", "default": "The cosmos advises against this path right now."},
        {"key": "no_gentle", "answer": "No", "confidence": "gentle", "default": "Not at this moment. Patience may change the answer."},
        {"key": "wait", "answer": "Wait", "confidence": "neutral", "default": "The timing isn't clear. Ask again when the moon shifts."},
        {"key": "maybe", "answer": "Maybe", "confidence": "neutral", "default": "The outcome depends on your actions. You have power here."},
    ]
    
    selected = random.choice(base_answers)
    
    # Localize
    msg_key = f"oracle_{selected['key']}_msg"
    msg_trans = get_translation(lang, msg_key)
    message = msg_trans[0] if msg_trans else selected["default"]
    
    ans_key = f"oracle_{selected['key']}_ans"
    ans_trans = get_translation(lang, ans_key)
    answer = ans_trans[0] if ans_trans else selected["answer"]
    
    return {
        "answer": answer,
        "confidence": selected["confidence"],
        "message": message
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

def get_manifestation_prompt(life_path: int, personal_day: int, reference_date: date, lang: str = "en") -> Dict:
    """Generate a personalized manifestation prompt."""
    seed = hash(f"{life_path}-{personal_day}-{reference_date.isoformat()}")
    random.seed(seed)
    
    # Get desires
    desires_trans = get_translation(lang, f"manifestation_desires_{life_path}")
    if desires_trans:
        desires = desires_trans
    else:
        desires = MANIFESTATION_DESIRES.get(life_path, MANIFESTATION_DESIRES[1])
    
    desire = random.choice(desires)
    
    # Get templates
    prompts_trans = get_translation(lang, "manifestation_prompts")
    if prompts_trans:
        template = random.choice(prompts_trans)
    else:
        template = random.choice(MANIFESTATION_PROMPTS)
    
    return {
        "prompt": template.format(desire=desire),
        "focus": desire,
        "practice": get_translation(lang, "manifestation_practice")[0] if get_translation(lang, "manifestation_practice") else "Write this 3 times in present tense, feeling it as already true.",
        "visualization": (get_translation(lang, "manifestation_viz")[0] if get_translation(lang, "manifestation_viz") else "Close your eyes and picture yourself fully experiencing {desire}.").format(desire=desire),
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

def _calculate_mood_forecast(
    element: str,
    life_path: int,
    personal_day: int,
    reference_date: date,
    lang: str = "en",
) -> Dict:
    """Generate daily mood forecast."""
    seed = hash(f"{element}-{life_path}-{personal_day}-{reference_date.isoformat()}")
    random.seed(seed)
    
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
    mood = random.choices(moods, weights=list(weights.values()))[0]
    forecast = MOOD_FORECASTS[mood]
    
    # Localize
    desc_trans = get_translation(lang, f"mood_{mood}_desc")
    description = desc_trans[0] if desc_trans else forecast["description"]
    
    tips_trans = get_translation(lang, f"mood_{mood}_tips")
    tips = tips_trans if tips_trans else forecast["tips"]
    
    # Calculate mood score (1-10)
    base_score = random.randint(5, 8)
    modifier = 1 if personal_day in [3, 5, 6] else -1 if personal_day in [4, 7] else 0
    score = max(1, min(10, base_score + modifier))
    
    return {
        "mood": mood,
        "emoji": forecast["emoji"],
        "score": score,
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
            advice = advice_trans if advice_trans else [
                "Double-check all communications",
                "Back up important files",
                "Avoid signing contracts if possible",
                "Reconnect with old friends",
                "Review rather than start new projects",
            ]
            
            alerts.append({
                "planet": "Mercury",
                "status": "retrograde",
                "message": message,
                "advice": advice,
            })
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
) -> Dict:
    """Get all daily features in one call."""
    if reference_date is None:
        reference_date = date.today()
    
    return {
        "date": reference_date.isoformat(),
        "lucky_numbers": calculate_lucky_numbers(dob, reference_date),
        "lucky_colors": get_lucky_colors(element, reference_date, lang=lang),
        "lucky_planet": get_lucky_planet(reference_date, life_path, lang=lang),
        "affirmation": get_daily_affirmation(element, life_path, reference_date, lang=lang),
        "tarot": get_daily_tarot(reference_date, name, lang=lang),
        "manifestation": get_manifestation_prompt(life_path, personal_day, reference_date, lang=lang),
        "mood_forecast": _calculate_mood_forecast(element, life_path, personal_day, reference_date, lang=lang),
        "retrograde_alerts": check_retrograde_alerts(reference_date, lang=lang),
    }


# ========== API-FACING FUNCTIONS ==========

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
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
        "mood_forecast": _calculate_mood_forecast(element, life_path, personal_day, today),
        "retrograde_alerts": check_retrograde_alerts(today),
        "personal_day": personal_day,
        "life_path": life_path,
    }


def get_tarot_card(question: Optional[str] = None) -> Dict:
    """Draw a single tarot card."""
    today = date.today()
    seed = hash(f"{question or 'daily'}-{today.isoformat()}-{datetime.now().microsecond}")
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
    
    life_path = random.randint(1, 9)
    personal_day = (today.day + today.month) % 9 or 9
    
    # Weight moods based on element and day
    weights = {
        "energetic": 1.5 if element in ["Fire", "Air"] else 0.8,
        "reflective": 1.2 if personal_day in [7, 9] else 0.6,
        "social": 1.5 if element in ["Air", "Fire"] or personal_day in [2, 3, 6] else 0.7,
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
