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
    """
    Calculate Life Path Number from date of birth (YYYY-MM-DD).
    Uses standard Pythagorean method: reduce each component first, then sum.
    Example: 1990-12-15 → month(12→3) + day(15→6) + year(1990→19→10→1) = 10 → 1
    """
    parts = dob.split("-")
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    
    # Reduce each component individually (standard Pythagorean method)
    month_reduced = reduce_number(month, keep_master=False)
    day_reduced = reduce_number(day, keep_master=False)
    year_reduced = reduce_number(year, keep_master=False)
    
    # Sum the reduced components and reduce again (preserving master numbers)
    total = month_reduced + day_reduced + year_reduced
    return reduce_number(total, keep_master=True)


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


# ──────────────────────────────────────────────────────────────────────────────
# CHALDEAN NUMEROLOGY
# ──────────────────────────────────────────────────────────────────────────────

from .constants import CHALDEAN_LETTER_VALUES


def calculate_life_path_number_chaldean(dob: str) -> int:
    """
    Calculate Life Path Number using the Chaldean method.

    Chaldean uses a different reduction strategy:
    all digits in the full DOB (YYYYMMDD) are summed, then reduced to 1–8.
    (9 is sacred in Chaldean and only emerges if that is the exact sum.)
    """
    digits = "".join(dob.split("-"))  # YYYYMMDD
    total = sum(int(d) for d in digits)

    # Reduce to single digit, but preserve 9 if it arises naturally
    while total > 9:
        total = sum(int(d) for d in str(total))

    return total


def calculate_name_number_chaldean(name: str) -> int:
    """Calculate Expression (Name) Number using Chaldean letter values."""
    name = name.lower().replace(" ", "").replace("-", "")
    total = sum(CHALDEAN_LETTER_VALUES.get(char, 0) for char in name)
    # Chaldean: reduce but preserve compound numbers (≥10) as double digits
    # Final single-digit reduction
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total


# ──────────────────────────────────────────────────────────────────────────────
# UNIFIED DISPATCHER
# ──────────────────────────────────────────────────────────────────────────────

def calculate_core_numbers(
    dob: str,
    name: str,
    method: str = "pythagorean",
) -> Dict:
    """
    Calculate Life Path and Name numbers using the requested method.

    Args:
        dob: Date of birth (YYYY-MM-DD)
        name: Full name
        method: 'pythagorean' (default) or 'chaldean'

    Returns:
        dict with life_path, name_number, method, and meaning.
    """
    use_chaldean = method.lower() == "chaldean"

    life_path = (
        calculate_life_path_number_chaldean(dob)
        if use_chaldean
        else calculate_life_path_number(dob)
    )
    name_number = (
        calculate_name_number_chaldean(name)
        if use_chaldean
        else calculate_name_number(name)
    )

    life_path_info = get_life_path_data(life_path)

    return {
        "method": "chaldean" if use_chaldean else "pythagorean",
        "life_path": life_path,
        "name_number": name_number,
        "life_path_meaning": life_path_info.get("meaning", ""),
        "life_path_advice": life_path_info.get("advice", []),
    }
