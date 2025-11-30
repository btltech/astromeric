from datetime import datetime
from typing import Dict, List

# Zodiac sign data with date ranges (month, day)
ZODIAC_SIGNS = [
    ("Capricorn", 12, 22, 1, 19),
    ("Aquarius", 1, 20, 2, 18),
    ("Pisces", 2, 19, 3, 20),
    ("Aries", 3, 21, 4, 19),
    ("Taurus", 4, 20, 5, 20),
    ("Gemini", 5, 21, 6, 20),
    ("Cancer", 6, 21, 7, 22),
    ("Leo", 7, 23, 8, 22),
    ("Virgo", 8, 23, 9, 22),
    ("Libra", 9, 23, 10, 22),
    ("Scorpio", 10, 23, 11, 21),
    ("Sagittarius", 11, 22, 12, 21),
]

# Elemental associations
ELEMENT_MAP = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

# Daily message snippets per sign (pools for fusion)
SIGN_TRAITS = {
    "Aries": {
        "general": ["Bold energy", "Direct action", "Protective drive"],
        "love": ["Bold in romance", "Direct communication", "Protective passion"], 
        "money": ["Impulsive spending", "Quick gains", "Risk-taking wins"], 
        "career": ["Leadership opportunities", "High energy", "Competitive edge"],
        "health": ["Physical activity", "Headstrong vitality", "Quick recovery"],
        "spiritual": ["Independent exploration", "Warrior spirit", "Self-discovery"]
    },
    "Taurus": {
        "general": ["Steady presence", "Comfort focus", "Sensual loyalty"],
        "love": ["Steady affection", "Comfort seeking", "Sensual loyalty"], 
        "money": ["Financial stability", "Patient investments", "Long-term building"], 
        "career": ["Reliable work", "Grounded decisions", "Consistency impresses"],
        "health": ["Body nourishment", "Slow healing", "Endurance building"],
        "spiritual": ["Earth connection", "Patient growth", "Sensory awareness"]
    },
    "Gemini": {
        "general": ["Playful curiosity", "Varied interests", "Quick thinking"],
        "love": ["Playful interactions", "Varied interests", "Curious questions"], 
        "money": ["Flexible finances", "Multiple streams", "Quick pivots"], 
        "career": ["Adaptable roles", "Communication skills", "Networking strengths"],
        "health": ["Mental stimulation", "Restless energy", "Breathwork"],
        "spiritual": ["Knowledge seeking", "Versatile paths", "Communication with guides"]
    },
    "Cancer": {
        "general": ["Emotional depth", "Nurturing care", "Protective tenderness"],
        "love": ["Emotional depth", "Nurturing bonds", "Protective tenderness"], 
        "money": ["Home security", "Cautious savings", "Family-focused planning"], 
        "career": ["Supportive environments", "Intuitive guidance", "Care-driven leadership"],
        "health": ["Emotional healing", "Digestive care", "Restful recovery"],
        "spiritual": ["Intuitive wisdom", "Family karma", "Moon rituals"]
    },
    "Leo": {
        "general": ["Dramatic flair", "Loyal hearts", "Warm spotlight"],
        "love": ["Dramatic gestures", "Loyal hearts", "Warm spotlight"], 
        "money": ["Generous spending", "Creative ventures", "Status investments"], 
        "career": ["Spotlight roles", "Confident leadership", "Performative clarity"],
        "health": ["Heart vitality", "Creative expression", "Proud posture"],
        "spiritual": ["Self-expression", "Solar power", "Creative manifestation"]
    },
    "Virgo": {
        "general": ["Thoughtful detail", "Practical care", "Analytical kindness"],
        "love": ["Thoughtful care", "Practical romance", "Detail-rich kindness"], 
        "money": ["Detailed budgeting", "Health investments", "Practical gains"], 
        "career": ["Analytical tasks", "Service-oriented", "Process mastery"],
        "health": ["Digestive health", "Routine care", "Mental clarity"],
        "spiritual": ["Service to others", "Analytical meditation", "Healing practices"]
    },
    "Libra": {
        "general": ["Harmonious balance", "Artful connection", "Diplomatic grace"],
        "love": ["Harmonious relationships", "Balanced partnerships", "Artful connection"], 
        "money": ["Fair deals", "Aesthetic purchases", "Win-win negotiations"], 
        "career": ["Diplomatic positions", "Team collaboration", "Bridge-building"],
        "health": ["Balance harmony", "Skin care", "Social wellness"],
        "spiritual": ["Relationship harmony", "Beauty rituals", "Justice alignment"]
    },
    "Scorpio": {
        "general": ["Intense focus", "Deep trust", "Magnetic loyalty"],
        "love": ["Intense connections", "Deep trust", "Magnetic loyalty"], 
        "money": ["Strategic investments", "Hidden resources", "Long-game wealth"], 
        "career": ["Transformative projects", "Research roles", "Stealth execution"],
        "health": ["Reproductive vitality", "Crisis recovery", "Deep cleansing"],
        "spiritual": ["Transformation journeys", "Shadow work", "Psychic depth"]
    },
    "Sagittarius": {
        "general": ["Adventurous spirit", "Honest expressions", "Freedom with devotion"],
        "love": ["Adventurous dates", "Honest expressions", "Freedom with affection"], 
        "money": ["Travel expenses", "Optimistic gambles", "Opportunity spotting"], 
        "career": ["Exploratory jobs", "Philosophical insights", "Global thinking"],
        "health": ["Liver support", "Movement freedom", "Optimistic outlook"],
        "spiritual": ["Philosophical quests", "Travel pilgrimages", "Higher learning"]
    },
    "Capricorn": {
        "general": ["Committed structure", "Long-term planning", "Serious devotion"],
        "love": ["Committed relationships", "Long-term planning", "Serious devotion"], 
        "money": ["Ambitious savings", "Career investments", "Structured growth"], 
        "career": ["Authority positions", "Structured goals", "Strategic patience"],
        "health": ["Bone strength", "Discipline routines", "Aging gracefully"],
        "spiritual": ["Karmic responsibility", "Earth stewardship", "Achievement enlightenment"]
    },
    "Aquarius": {
        "general": ["Unconventional vision", "Intellectual bonds", "Space with loyalty"],
        "love": ["Unconventional romance", "Intellectual bonds", "Space with loyalty"], 
        "money": ["Innovative ideas", "Community funds", "Tech-forward gains"], 
        "career": ["Progressive fields", "Group efforts", "Systems thinking"],
        "health": ["Circulatory flow", "Innovative healing", "Community support"],
        "spiritual": ["Humanitarian causes", "Futuristic visions", "Collective consciousness"]
    },
    "Pisces": {
        "general": ["Dreamy intuition", "Empathetic understanding", "Poetic closeness"],
        "love": ["Dreamy affection", "Empathetic understanding", "Poetic closeness"], 
        "money": ["Creative funding", "Charitable giving", "Intuitive timing"], 
        "career": ["Artistic pursuits", "Healing professions", "Visionary concepts"],
        "health": ["Immune support", "Dream integration", "Fluid balance"],
        "spiritual": ["Mystic visions", "Compassionate service", "Universal love"]
    }
}

def get_zodiac_sign(dob: str) -> str:
    """Determine zodiac sign from date of birth string (YYYY-MM-DD)."""
    date = datetime.fromisoformat(dob)
    month, day = date.month, date.day
    for sign, start_month, start_day, end_month, end_day in ZODIAC_SIGNS:
        if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
            return sign
    return "Capricorn"  # Default

def get_element(sign: str) -> str:
    """Get elemental association for a sign."""
    return ELEMENT_MAP.get(sign, "Unknown")

def get_sign_traits(sign: str) -> Dict[str, List[str]]:
    """Get trait pools for a sign."""
    return SIGN_TRAITS.get(sign, {"love": [], "money": [], "career": []})
