from typing import Dict
from app.interpretation.translations import get_translation

from .constants import LETTER_VALUES, reduce_number

# Life Path meanings and advice pools
LIFE_PATH_DATA = {
    1: {
        "meaning": "Leadership and independence",
        "advice": ["Take initiative", "Trust your instincts", "Lead by example"],
    },
    2: {
        "meaning": "Cooperation and balance",
        "advice": ["Seek harmony", "Collaborate effectively", "Listen carefully"],
    },
    3: {
        "meaning": "Creativity and expression",
        "advice": ["Express yourself", "Embrace joy", "Share your talents"],
    },
    4: {
        "meaning": "Stability and hard work",
        "advice": ["Build foundations", "Be diligent", "Organize your life"],
    },
    5: {
        "meaning": "Freedom and adventure",
        "advice": ["Embrace change", "Seek new experiences", "Stay flexible"],
    },
    6: {
        "meaning": "Responsibility and service",
        "advice": ["Help others", "Nurture relationships", "Maintain balance"],
    },
    7: {
        "meaning": "Analysis and spirituality",
        "advice": ["Seek knowledge", "Reflect deeply", "Trust intuition"],
    },
    8: {
        "meaning": "Power and abundance",
        "advice": ["Build wealth", "Take control", "Be ambitious"],
    },
    9: {
        "meaning": "Humanitarianism and completion",
        "advice": ["Give generously", "Complete cycles", "Help humanity"],
    },
    11: {
        "meaning": "Inspiration and enlightenment",
        "advice": ["Inspire others", "Follow visions", "Seek higher purpose"],
    },
    22: {
        "meaning": "Master builder and practicality",
        "advice": ["Plan big", "Build structures", "Manifest dreams"],
    },
    33: {
        "meaning": "Master teacher and compassion",
        "advice": ["Teach wisdom", "Show compassion", "Heal others"],
    },
}


def calculate_life_path_number(dob: str) -> int:
    """Calculate Life Path Number from date of birth (YYYY-MM-DD)."""
    parts = dob.split("-")
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    total = year + month + day
    return reduce_number(total)


def calculate_name_number(name: str) -> int:
    """Calculate Name Number using Pythagorean numerology."""
    name = name.lower().replace(" ", "").replace("-", "")
    total = sum(LETTER_VALUES.get(char, 0) for char in name)
    return reduce_number(total)


def get_life_path_data(number: int, lang: str = "en") -> Dict[str, any]:
    """Get meaning and advice pool for Life Path number."""
    base_data = LIFE_PATH_DATA.get(
        number,
        {
            "meaning": "Unknown path",
            "advice": ["Seek guidance", "Explore possibilities"],
        },
    )
    
    if lang == "en":
        return base_data
        
    # Localize meaning
    meaning_key = f"numerology_life_path_{number}_meaning"
    meaning = get_translation(lang, "numerology_life_path", meaning_key)
    if not meaning:
        meaning = base_data["meaning"]
        
    # Localize advice
    advice = []
    for i, item in enumerate(base_data["advice"]):
        advice_key = f"numerology_life_path_{number}_advice_{i}"
        translated_item = get_translation(lang, "numerology_life_path", advice_key)
        advice.append(translated_item if translated_item else item)
        
    return {
        "meaning": meaning,
        "advice": advice
    }
