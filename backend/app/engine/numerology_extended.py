"""Extended numerology calculations: Expression, Soul Urge, Personality, Maturity, Cycles, Pinnacles, Challenges."""

from datetime import datetime
from typing import Dict, List
from app.interpretation.translations import get_translation

from .constants import LETTER_VALUES, VOWELS, reduce_number

NUMBER_MEANINGS = {
    1: {
        "keyword": "Leadership",
        "description": "Independent pioneer. Forge your own path.",
    },
    2: {
        "keyword": "Cooperation",
        "description": "Diplomatic partner. Excel through collaboration.",
    },
    3: {
        "keyword": "Expression",
        "description": "Creative communicator. Let your artistry shine.",
    },
    4: {
        "keyword": "Foundation",
        "description": "Practical builder. Create lasting structures.",
    },
    5: {
        "keyword": "Freedom",
        "description": "Adventurous spirit. Embrace change and variety.",
    },
    6: {
        "keyword": "Responsibility",
        "description": "Nurturing caretaker. Serve through love.",
    },
    7: {
        "keyword": "Analysis",
        "description": "Spiritual seeker. Trust deeper truths.",
    },
    8: {
        "keyword": "Power",
        "description": "Ambitious achiever. Master material success.",
    },
    9: {
        "keyword": "Humanitarianism",
        "description": "Compassionate visionary. Serve the greater good.",
    },
    11: {
        "keyword": "Illumination",
        "description": "Intuitive visionary. Trust your inner light.",
    },
    22: {
        "keyword": "Master Builder",
        "description": "Powerful manifestor. Build a lasting legacy.",
    },
    33: {
        "keyword": "Master Teacher",
        "description": "Spiritual healer. Uplift through love.",
    },
}


def calculate_expression_number(full_name: str) -> int:
    """Expression/Destiny Number: Sum of all letters in birth name."""
    name = full_name.lower().replace(" ", "").replace("-", "")
    total = sum(LETTER_VALUES.get(c, 0) for c in name if c.isalpha())
    return reduce_number(total)


def calculate_soul_urge_number(full_name: str) -> int:
    """Soul Urge/Heart's Desire: Sum of vowels only."""
    name = full_name.lower()
    total = sum(LETTER_VALUES.get(c, 0) for c in name if c in VOWELS)
    return reduce_number(total)


def calculate_personality_number(full_name: str) -> int:
    """Personality Number: Sum of consonants only."""
    name = full_name.lower()
    total = sum(
        LETTER_VALUES.get(c, 0) for c in name if c.isalpha() and c not in VOWELS
    )
    return reduce_number(total)


def calculate_maturity_number(life_path: int, expression: int) -> int:
    """Maturity Number: Life Path + Expression, reduced."""
    return reduce_number(life_path + expression)


def calculate_personal_year(dob: str, year: int = None) -> int:
    """Personal Year: birth month + birth day + current year, reduced."""
    parts = dob.split("-")
    month, day = int(parts[1]), int(parts[2])
    if year is None:
        year = datetime.now().year
    return reduce_number(month + day + year, keep_master=False)


def calculate_personal_month(personal_year: int, month: int) -> int:
    """Personal Month: Personal Year + calendar month, reduced."""
    return reduce_number(personal_year + month, keep_master=False)


def calculate_personal_day(personal_month: int, day: int) -> int:
    """Personal Day: Personal Month + calendar day, reduced."""
    return reduce_number(personal_month + day, keep_master=False)


def calculate_pinnacles(dob: str, lang: str = "en") -> List[Dict]:
    """Calculate the 4 Pinnacles with their periods and numbers."""
    parts = dob.split("-")
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

    # Reduce each component
    month_r = reduce_number(month, keep_master=False)
    day_r = reduce_number(day, keep_master=False)
    year_r = reduce_number(year, keep_master=False)

    # Life Path for timing
    life_path = reduce_number(month + day + year, keep_master=False)

    # Pinnacle numbers
    p1 = reduce_number(month_r + day_r)
    p2 = reduce_number(day_r + year_r)
    p3 = reduce_number(p1 + p2)
    p4 = reduce_number(month_r + year_r)

    # Pinnacle timing (36 - Life Path = end of first pinnacle)
    first_end = 36 - life_path
    birth_year = year
    
    # Localize period strings
    if lang == "en":
        period1 = f"Birth to age {first_end}"
        period2 = f"Age {first_end + 1} to {first_end + 9}"
        period3 = f"Age {first_end + 10} to {first_end + 18}"
        period4 = f"Age {first_end + 19} onwards"
    else:
        # Templates
        t_birth = get_translation(lang, "numerology_periods", "birth_to_age") or "Birth to age {age}"
        t_range = get_translation(lang, "numerology_periods", "age_range") or "Age {start} to {end}"
        t_onwards = get_translation(lang, "numerology_periods", "age_onwards") or "Age {start} onwards"
        
        period1 = t_birth.format(age=first_end)
        period2 = t_range.format(start=first_end + 1, end=first_end + 9)
        period3 = t_range.format(start=first_end + 10, end=first_end + 18)
        period4 = t_onwards.format(start=first_end + 19)

    return [
        {
            "number": p1,
            "period": period1,
            "start_year": birth_year,
            "end_year": birth_year + first_end,
        },
        {
            "number": p2,
            "period": period2,
            "start_year": birth_year + first_end + 1,
            "end_year": birth_year + first_end + 9,
        },
        {
            "number": p3,
            "period": period3,
            "start_year": birth_year + first_end + 10,
            "end_year": birth_year + first_end + 18,
        },
        {
            "number": p4,
            "period": period4,
            "start_year": birth_year + first_end + 19,
            "end_year": None,
        },
    ]


def calculate_challenges(dob: str, lang: str = "en") -> List[Dict]:
    """Calculate the 3 Challenges."""
    parts = dob.split("-")
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

    month_r = reduce_number(month, keep_master=False)
    day_r = reduce_number(day, keep_master=False)
    year_r = reduce_number(year, keep_master=False)

    c1 = abs(month_r - day_r)
    c2 = abs(day_r - year_r)
    c3 = abs(c1 - c2)
    
    # Localize labels and descriptions
    if lang == "en":
        l1, d1 = "First Challenge", "Early life lesson"
        l2, d2 = "Second Challenge", "Middle life lesson"
        l3, d3 = "Main Challenge", "Lifelong lesson"
    else:
        l1 = get_translation(lang, "numerology_challenges", "first_label") or "First Challenge"
        d1 = get_translation(lang, "numerology_challenges", "first_desc") or "Early life lesson"
        l2 = get_translation(lang, "numerology_challenges", "second_label") or "Second Challenge"
        d2 = get_translation(lang, "numerology_challenges", "second_desc") or "Middle life lesson"
        l3 = get_translation(lang, "numerology_challenges", "main_label") or "Main Challenge"
        d3 = get_translation(lang, "numerology_challenges", "main_desc") or "Lifelong lesson"

    return [
        {"number": c1, "label": l1, "description": d1},
        {
            "number": c2,
            "label": l2,
            "description": d2,
        },
        {"number": c3, "label": l3, "description": d3},
    ]


def get_number_meaning(num: int, lang: str = "en") -> Dict:
    """Get keyword and description for a number."""
    base_data = NUMBER_MEANINGS.get(
        num, {"keyword": "Unknown", "description": "Unique energy."}
    )
    
    if lang == "en":
        return base_data
        
    keyword_key = f"numerology_number_{num}_keyword"
    description_key = f"numerology_number_{num}_description"
    
    keyword = get_translation(lang, "numerology_meanings", keyword_key)
    description = get_translation(lang, "numerology_meanings", description_key)
    
    return {
        "keyword": keyword if keyword else base_data["keyword"],
        "description": description if description else base_data["description"]
    }


def get_full_numerology_profile(name: str, dob: str, lang: str = "en") -> Dict:
    """Generate complete numerology profile."""
    from .numerology import calculate_life_path_number, get_life_path_data

    life_path = calculate_life_path_number(dob)
    expression = calculate_expression_number(name)
    soul_urge = calculate_soul_urge_number(name)
    personality = calculate_personality_number(name)
    maturity = calculate_maturity_number(life_path, expression)

    now = datetime.now()
    personal_year = calculate_personal_year(dob, now.year)
    personal_month = calculate_personal_month(personal_year, now.month)
    personal_day = calculate_personal_day(personal_month, now.day)

    pinnacles = calculate_pinnacles(dob, lang=lang)
    challenges = calculate_challenges(dob, lang=lang)

    return {
        "core_numbers": {
            "life_path": {"number": life_path, **get_number_meaning(life_path, lang=lang)},
            "expression": {"number": expression, **get_number_meaning(expression, lang=lang)},
            "soul_urge": {"number": soul_urge, **get_number_meaning(soul_urge, lang=lang)},
            "personality": {"number": personality, **get_number_meaning(personality, lang=lang)},
            "maturity": {"number": maturity, **get_number_meaning(maturity, lang=lang)},
        },
        "cycles": {
            "personal_year": {
                "number": personal_year,
                **get_number_meaning(personal_year, lang=lang),
            },
            "personal_month": {
                "number": personal_month,
                **get_number_meaning(personal_month, lang=lang),
            },
            "personal_day": {
                "number": personal_day,
                **get_number_meaning(personal_day, lang=lang),
            },
        },
        "pinnacles": [
            {
                "number": p["number"],
                "period": p["period"],
                **get_number_meaning(p["number"], lang=lang),
            }
            for p in pinnacles
        ],
        "challenges": [
            {
                "number": c["number"],
                "label": c["label"],
                **get_number_meaning(c["number"], lang=lang),
            }
            for c in challenges
        ],
    }


def analyze_name(name: str, lang: str = "en") -> Dict:
    """Analyze any name for numerology numbers."""
    expression = calculate_expression_number(name)
    soul_urge = calculate_soul_urge_number(name)
    personality = calculate_personality_number(name)

    return {
        "name": name,
        "expression": {"number": expression, **get_number_meaning(expression, lang=lang)},
        "soul_urge": {"number": soul_urge, **get_number_meaning(soul_urge, lang=lang)},
        "personality": {"number": personality, **get_number_meaning(personality, lang=lang)},
    }
