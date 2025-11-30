"""Glossary and learning content for astrology and numerology."""

from typing import Dict, List

ZODIAC_GLOSSARY = {
    "Aries": {
        "dates": "March 21 - April 19",
        "element": "Fire",
        "modality": "Cardinal",
        "ruler": "Mars",
        "symbol": "The Ram",
        "traits": ["Bold", "Pioneering", "Competitive", "Energetic"],
        "description": "Aries is the first sign of the zodiac, representing new beginnings and raw energy. Aries individuals are natural leaders who thrive on challenge and adventure.",
    },
    "Taurus": {
        "dates": "April 20 - May 20",
        "element": "Earth",
        "modality": "Fixed",
        "ruler": "Venus",
        "symbol": "The Bull",
        "traits": ["Reliable", "Patient", "Sensual", "Determined"],
        "description": "Taurus grounds us in the material world. Known for stability and appreciation of beauty, Taureans build lasting foundations.",
    },
    "Gemini": {
        "dates": "May 21 - June 20",
        "element": "Air",
        "modality": "Mutable",
        "ruler": "Mercury",
        "symbol": "The Twins",
        "traits": ["Curious", "Adaptable", "Communicative", "Witty"],
        "description": "Gemini represents the mind's duality and love of learning. Quick-witted and sociable, Geminis excel at communication.",
    },
    "Cancer": {
        "dates": "June 21 - July 22",
        "element": "Water",
        "modality": "Cardinal",
        "ruler": "Moon",
        "symbol": "The Crab",
        "traits": ["Nurturing", "Intuitive", "Protective", "Emotional"],
        "description": "Cancer embodies home and emotional security. Deeply intuitive, Cancers are the caregivers of the zodiac.",
    },
    "Leo": {
        "dates": "July 23 - August 22",
        "element": "Fire",
        "modality": "Fixed",
        "ruler": "Sun",
        "symbol": "The Lion",
        "traits": ["Confident", "Creative", "Generous", "Dramatic"],
        "description": "Leo radiates warmth and creativity. Natural performers, Leos seek recognition and lead with heart.",
    },
    "Virgo": {
        "dates": "August 23 - September 22",
        "element": "Earth",
        "modality": "Mutable",
        "ruler": "Mercury",
        "symbol": "The Virgin",
        "traits": ["Analytical", "Helpful", "Practical", "Perfectionist"],
        "description": "Virgo brings order and service. Detail-oriented and health-conscious, Virgos improve everything they touch.",
    },
    "Libra": {
        "dates": "September 23 - October 22",
        "element": "Air",
        "modality": "Cardinal",
        "ruler": "Venus",
        "symbol": "The Scales",
        "traits": ["Diplomatic", "Harmonious", "Artistic", "Indecisive"],
        "description": "Libra seeks balance and beauty. Natural mediators, Libras value partnership and fairness above all.",
    },
    "Scorpio": {
        "dates": "October 23 - November 21",
        "element": "Water",
        "modality": "Fixed",
        "ruler": "Pluto/Mars",
        "symbol": "The Scorpion",
        "traits": ["Intense", "Transformative", "Passionate", "Secretive"],
        "description": "Scorpio dives into life's depths. Masters of transformation, Scorpios possess incredible emotional power.",
    },
    "Sagittarius": {
        "dates": "November 22 - December 21",
        "element": "Fire",
        "modality": "Mutable",
        "ruler": "Jupiter",
        "symbol": "The Archer",
        "traits": ["Adventurous", "Philosophical", "Optimistic", "Freedom-loving"],
        "description": "Sagittarius explores both physical and mental horizons. Seekers of truth, they inspire with their vision.",
    },
    "Capricorn": {
        "dates": "December 22 - January 19",
        "element": "Earth",
        "modality": "Cardinal",
        "ruler": "Saturn",
        "symbol": "The Goat",
        "traits": ["Ambitious", "Disciplined", "Patient", "Strategic"],
        "description": "Capricorn climbs toward achievement. Masters of long-term planning, they build empires through persistence.",
    },
    "Aquarius": {
        "dates": "January 20 - February 18",
        "element": "Air",
        "modality": "Fixed",
        "ruler": "Uranus/Saturn",
        "symbol": "The Water Bearer",
        "traits": ["Innovative", "Humanitarian", "Independent", "Eccentric"],
        "description": "Aquarius envisions the future. Revolutionaries and humanitarians, they challenge norms for collective good.",
    },
    "Pisces": {
        "dates": "February 19 - March 20",
        "element": "Water",
        "modality": "Mutable",
        "ruler": "Neptune/Jupiter",
        "symbol": "The Fish",
        "traits": ["Intuitive", "Compassionate", "Artistic", "Dreamy"],
        "description": "Pisces dissolves boundaries between self and universe. Mystics and artists, they channel the collective unconscious.",
    },
}

NUMEROLOGY_GLOSSARY = {
    "Life Path": {
        "calculation": "Sum of birth date digits, reduced to single digit or master number",
        "meaning": "Your core life purpose and the lessons you're here to learn. The most important number in your chart.",
        "example": "Born 1990-03-15: 1+9+9+0+0+3+1+5 = 28 → 2+8 = 10 → 1+0 = 1",
    },
    "Expression": {
        "calculation": "Sum of all letters in full birth name using Pythagorean values",
        "meaning": "Your natural talents, abilities, and the gifts you bring to the world. How you express yourself.",
        "example": "JOHN DOE: J(1)+O(6)+H(8)+N(5)+D(4)+O(6)+E(5) = 35 → 3+5 = 8",
    },
    "Soul Urge": {
        "calculation": "Sum of vowels only in birth name",
        "meaning": "Your innermost desires, motivations, and what truly drives you. Your heart's deepest wish.",
        "example": "JOHN DOE: O(6)+O(6)+E(5) = 17 → 1+7 = 8",
    },
    "Personality": {
        "calculation": "Sum of consonants only in birth name",
        "meaning": "How others perceive you. Your outer mask and first impression.",
        "example": "JOHN DOE: J(1)+H(8)+N(5)+D(4) = 18 → 1+8 = 9",
    },
    "Maturity": {
        "calculation": "Life Path + Expression, reduced",
        "meaning": "Your true self that emerges after age 40-50. The integration of purpose and expression.",
        "example": "Life Path 1 + Expression 8 = 9",
    },
    "Personal Year": {
        "calculation": "Birth month + Birth day + Current year, reduced",
        "meaning": "The theme and opportunities of your current year. Runs from birthday to birthday.",
        "example": "March 15, year 2025: 3+1+5+2+0+2+5 = 18 → 1+8 = 9",
    },
    "Pinnacles": {
        "calculation": "Four life phases based on birth date components",
        "meaning": "Major life phases with specific themes and opportunities. Each pinnacle shapes your experiences.",
        "example": "First Pinnacle: Month + Day reduced",
    },
    "Challenges": {
        "calculation": "Differences between birth date components",
        "meaning": "Life lessons you're working through. Areas requiring growth and mastery.",
        "example": "First Challenge: |Month - Day|",
    },
}

MASTER_NUMBERS = {
    11: {
        "title": "The Intuitive Master",
        "keywords": ["Illumination", "Inspiration", "Spiritual insight"],
        "description": "11 is the channel between the conscious and unconscious. Those with 11 are highly intuitive, inspiring, and often experience life on a heightened plane.",
        "challenges": ["Nervous energy", "Self-doubt", "Impracticality"],
        "gifts": ["Spiritual awareness", "Artistic vision", "Healing abilities"],
    },
    22: {
        "title": "The Master Builder",
        "keywords": ["Manifestation", "Large-scale achievement", "Practical vision"],
        "description": "22 combines the intuition of 11 with the practical power of 4. These individuals can turn the grandest visions into reality.",
        "challenges": ["Overwhelm", "Workaholic tendencies", "Self-pressure"],
        "gifts": ["Organizational genius", "Leadership", "Legacy building"],
    },
    33: {
        "title": "The Master Teacher",
        "keywords": ["Selfless service", "Healing", "Cosmic consciousness"],
        "description": "33 is the rarest master number, embodying pure love and spiritual upliftment. These souls teach through their presence.",
        "challenges": ["Self-sacrifice", "Martyrdom", "Unrealistic expectations"],
        "gifts": ["Unconditional love", "Healing presence", "Spiritual guidance"],
    },
}

ELEMENTS_GLOSSARY = {
    "Fire": {
        "signs": ["Aries", "Leo", "Sagittarius"],
        "qualities": ["Passionate", "Energetic", "Spontaneous", "Confident"],
        "description": "Fire signs burn bright with enthusiasm and action. They inspire others and lead with courage.",
    },
    "Earth": {
        "signs": ["Taurus", "Virgo", "Capricorn"],
        "qualities": ["Practical", "Grounded", "Reliable", "Sensual"],
        "description": "Earth signs build and stabilize. They manifest ideas into reality through patience and persistence.",
    },
    "Air": {
        "signs": ["Gemini", "Libra", "Aquarius"],
        "qualities": ["Intellectual", "Social", "Communicative", "Objective"],
        "description": "Air signs think and connect. They process life through ideas and relationships.",
    },
    "Water": {
        "signs": ["Cancer", "Scorpio", "Pisces"],
        "qualities": ["Emotional", "Intuitive", "Nurturing", "Transformative"],
        "description": "Water signs feel and flow. They navigate life through emotion and intuition.",
    },
}


def get_sign_info(sign: str) -> Dict:
    """Get full information about a zodiac sign."""
    return ZODIAC_GLOSSARY.get(sign, {})


def get_number_explanation(number_type: str) -> Dict:
    """Get explanation of a numerology number type."""
    return NUMEROLOGY_GLOSSARY.get(number_type, {})


def get_master_number_info(number: int) -> Dict:
    """Get information about a master number."""
    return MASTER_NUMBERS.get(number, {})


def get_element_info(element: str) -> Dict:
    """Get information about an element."""
    return ELEMENTS_GLOSSARY.get(element, {})


def search_glossary(query: str) -> List[Dict]:
    """Search all glossaries for a term."""
    results = []
    query = query.lower()

    for sign, data in ZODIAC_GLOSSARY.items():
        if query in sign.lower() or query in data.get("description", "").lower():
            results.append({"type": "zodiac", "key": sign, "data": data})

    for term, data in NUMEROLOGY_GLOSSARY.items():
        if query in term.lower() or query in data.get("meaning", "").lower():
            results.append({"type": "numerology", "key": term, "data": data})

    for element, data in ELEMENTS_GLOSSARY.items():
        if query in element.lower() or query in data.get("description", "").lower():
            results.append({"type": "element", "key": element, "data": data})

    return results
