"""Extended numerology calculations: Expression, Soul Urge, Personality, Maturity, Cycles, Pinnacles, Challenges."""
from typing import Dict, List, Tuple
from datetime import datetime

# Pythagorean vowels for Soul Urge
VOWELS = set('aeiou')

LETTER_VALUES = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
    'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 6, 'p': 7, 'q': 8, 'r': 9,
    's': 1, 't': 2, 'u': 3, 'v': 4, 'w': 5, 'x': 6, 'y': 7, 'z': 8
}

NUMBER_MEANINGS = {
    1: {"keyword": "Leadership", "description": "Independent, pioneering, ambitious. Natural leader who forges their own path."},
    2: {"keyword": "Cooperation", "description": "Diplomatic, sensitive, partnership-oriented. Excels in collaboration."},
    3: {"keyword": "Expression", "description": "Creative, communicative, joyful. Natural entertainer and artist."},
    4: {"keyword": "Foundation", "description": "Practical, organized, disciplined. Builder of stable structures."},
    5: {"keyword": "Freedom", "description": "Adventurous, versatile, dynamic. Thrives on change and variety."},
    6: {"keyword": "Responsibility", "description": "Nurturing, harmonious, service-oriented. Natural caretaker."},
    7: {"keyword": "Analysis", "description": "Introspective, spiritual, analytical. Seeker of deeper truths."},
    8: {"keyword": "Power", "description": "Ambitious, authoritative, material success. Business-minded achiever."},
    9: {"keyword": "Humanitarianism", "description": "Compassionate, idealistic, global vision. Universal love and service."},
    11: {"keyword": "Illumination", "description": "Intuitive, inspiring, visionary. Master of spiritual insight."},
    22: {"keyword": "Master Builder", "description": "Powerful manifestor, practical visionary. Builds lasting legacies."},
    33: {"keyword": "Master Teacher", "description": "Selfless healer, spiritual guide. Uplifts humanity through love."},
}

def reduce_to_single(num: int, keep_master: bool = True) -> int:
    """Reduce number to single digit, optionally preserving master numbers."""
    master = {11, 22, 33} if keep_master else set()
    while num > 9 and num not in master:
        num = sum(int(d) for d in str(num))
    return num

def calculate_expression_number(full_name: str) -> int:
    """Expression/Destiny Number: Sum of all letters in birth name."""
    name = full_name.lower().replace(' ', '').replace('-', '')
    total = sum(LETTER_VALUES.get(c, 0) for c in name if c.isalpha())
    return reduce_to_single(total)

def calculate_soul_urge_number(full_name: str) -> int:
    """Soul Urge/Heart's Desire: Sum of vowels only."""
    name = full_name.lower()
    total = sum(LETTER_VALUES.get(c, 0) for c in name if c in VOWELS)
    return reduce_to_single(total)

def calculate_personality_number(full_name: str) -> int:
    """Personality Number: Sum of consonants only."""
    name = full_name.lower()
    total = sum(LETTER_VALUES.get(c, 0) for c in name if c.isalpha() and c not in VOWELS)
    return reduce_to_single(total)

def calculate_maturity_number(life_path: int, expression: int) -> int:
    """Maturity Number: Life Path + Expression, reduced."""
    return reduce_to_single(life_path + expression)

def calculate_personal_year(dob: str, year: int = None) -> int:
    """Personal Year: birth month + birth day + current year, reduced."""
    parts = dob.split('-')
    month, day = int(parts[1]), int(parts[2])
    if year is None:
        year = datetime.now().year
    return reduce_to_single(month + day + year, keep_master=False)

def calculate_personal_month(personal_year: int, month: int) -> int:
    """Personal Month: Personal Year + calendar month, reduced."""
    return reduce_to_single(personal_year + month, keep_master=False)

def calculate_personal_day(personal_month: int, day: int) -> int:
    """Personal Day: Personal Month + calendar day, reduced."""
    return reduce_to_single(personal_month + day, keep_master=False)

def calculate_pinnacles(dob: str) -> List[Dict]:
    """Calculate the 4 Pinnacles with their periods and numbers."""
    parts = dob.split('-')
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    
    # Reduce each component
    month_r = reduce_to_single(month, keep_master=False)
    day_r = reduce_to_single(day, keep_master=False)
    year_r = reduce_to_single(year, keep_master=False)
    
    # Life Path for timing
    life_path = reduce_to_single(month + day + year, keep_master=False)
    
    # Pinnacle numbers
    p1 = reduce_to_single(month_r + day_r)
    p2 = reduce_to_single(day_r + year_r)
    p3 = reduce_to_single(p1 + p2)
    p4 = reduce_to_single(month_r + year_r)
    
    # Pinnacle timing (36 - Life Path = end of first pinnacle)
    first_end = 36 - life_path
    birth_year = year
    
    return [
        {"number": p1, "period": f"Birth to age {first_end}", "start_year": birth_year, "end_year": birth_year + first_end},
        {"number": p2, "period": f"Age {first_end + 1} to {first_end + 9}", "start_year": birth_year + first_end + 1, "end_year": birth_year + first_end + 9},
        {"number": p3, "period": f"Age {first_end + 10} to {first_end + 18}", "start_year": birth_year + first_end + 10, "end_year": birth_year + first_end + 18},
        {"number": p4, "period": f"Age {first_end + 19} onwards", "start_year": birth_year + first_end + 19, "end_year": None},
    ]

def calculate_challenges(dob: str) -> List[Dict]:
    """Calculate the 3 Challenges."""
    parts = dob.split('-')
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    
    month_r = reduce_to_single(month, keep_master=False)
    day_r = reduce_to_single(day, keep_master=False)
    year_r = reduce_to_single(year, keep_master=False)
    
    c1 = abs(month_r - day_r)
    c2 = abs(day_r - year_r)
    c3 = abs(c1 - c2)
    
    return [
        {"number": c1, "label": "First Challenge", "description": "Early life lesson"},
        {"number": c2, "label": "Second Challenge", "description": "Middle life lesson"},
        {"number": c3, "label": "Main Challenge", "description": "Lifelong lesson"},
    ]

def get_number_meaning(num: int) -> Dict:
    """Get keyword and description for a number."""
    return NUMBER_MEANINGS.get(num, {"keyword": "Unknown", "description": "Unique energy."})

def get_full_numerology_profile(name: str, dob: str) -> Dict:
    """Generate complete numerology profile."""
    from .numerology import calculate_life_path_number, calculate_name_number
    
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
            "personal_year": {"number": personal_year, **get_number_meaning(personal_year)},
            "personal_month": {"number": personal_month, **get_number_meaning(personal_month)},
            "personal_day": {"number": personal_day, **get_number_meaning(personal_day)},
        },
        "pinnacles": [{"number": p["number"], "period": p["period"], **get_number_meaning(p["number"])} for p in pinnacles],
        "challenges": [{"number": c["number"], "label": c["label"], **get_number_meaning(c["number"])} for c in challenges],
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
