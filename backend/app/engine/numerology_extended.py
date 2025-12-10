"""Extended numerology calculations: Expression, Soul Urge, Personality, Maturity, Cycles, Pinnacles, Challenges."""

from datetime import datetime
from typing import Dict, List

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


def calculate_pinnacles(dob: str) -> List[Dict]:
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

    return [
        {
            "number": p1,
            "period": f"Birth to age {first_end}",
            "start_year": birth_year,
            "end_year": birth_year + first_end,
        },
        {
            "number": p2,
            "period": f"Age {first_end + 1} to {first_end + 9}",
            "start_year": birth_year + first_end + 1,
            "end_year": birth_year + first_end + 9,
        },
        {
            "number": p3,
            "period": f"Age {first_end + 10} to {first_end + 18}",
            "start_year": birth_year + first_end + 10,
            "end_year": birth_year + first_end + 18,
        },
        {
            "number": p4,
            "period": f"Age {first_end + 19} onwards",
            "start_year": birth_year + first_end + 19,
            "end_year": None,
        },
    ]


def calculate_challenges(dob: str) -> List[Dict]:
    """Calculate the 3 Challenges."""
    parts = dob.split("-")
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

    month_r = reduce_number(month, keep_master=False)
    day_r = reduce_number(day, keep_master=False)
    year_r = reduce_number(year, keep_master=False)

    c1 = abs(month_r - day_r)
    c2 = abs(day_r - year_r)
    c3 = abs(c1 - c2)

    return [
        {"number": c1, "label": "First Challenge", "description": "Early life lesson"},
        {
            "number": c2,
            "label": "Second Challenge",
            "description": "Middle life lesson",
        },
        {"number": c3, "label": "Main Challenge", "description": "Lifelong lesson"},
    ]


def get_number_meaning(num: int) -> Dict:
    """Get keyword and description for a number."""
    return NUMBER_MEANINGS.get(
        num, {"keyword": "Unknown", "description": "Unique energy."}
    )


def get_full_numerology_profile(name: str, dob: str) -> Dict:
    """Generate complete numerology profile."""
    from .numerology import calculate_life_path_number

    life_path = calculate_life_path_number(dob)
    expression = calculate_expression_number(name)
    soul_urge = calculate_soul_urge_number(name)
    personality = calculate_personality_number(name)
    maturity = calculate_maturity_number(life_path, expression)

    now = datetime.now()
    personal_year = calculate_personal_year(dob, now.year)
    personal_month = calculate_personal_month(personal_year, now.month)
    personal_day = calculate_personal_day(personal_month, now.day)

    pinnacles = calculate_pinnacles(dob)
    challenges = calculate_challenges(dob)

    return {
        "core_numbers": {
            "life_path": {"number": life_path, **get_number_meaning(life_path)},
            "expression": {"number": expression, **get_number_meaning(expression)},
            "soul_urge": {"number": soul_urge, **get_number_meaning(soul_urge)},
            "personality": {"number": personality, **get_number_meaning(personality)},
            "maturity": {"number": maturity, **get_number_meaning(maturity)},
        },
        "cycles": {
            "personal_year": {
                "number": personal_year,
                **get_number_meaning(personal_year),
            },
            "personal_month": {
                "number": personal_month,
                **get_number_meaning(personal_month),
            },
            "personal_day": {
                "number": personal_day,
                **get_number_meaning(personal_day),
            },
        },
        "pinnacles": [
            {
                "number": p["number"],
                "period": p["period"],
                **get_number_meaning(p["number"]),
            }
            for p in pinnacles
        ],
        "challenges": [
            {
                "number": c["number"],
                "label": c["label"],
                **get_number_meaning(c["number"]),
            }
            for c in challenges
        ],
    }


def analyze_name(name: str) -> Dict:
    """Analyze any name for numerology numbers."""
    expression = calculate_expression_number(name)
    soul_urge = calculate_soul_urge_number(name)
    personality = calculate_personality_number(name)

    return {
        "name": name,
        "expression": {"number": expression, **get_number_meaning(expression)},
        "soul_urge": {"number": soul_urge, **get_number_meaning(soul_urge)},
        "personality": {"number": personality, **get_number_meaning(personality)},
    }
