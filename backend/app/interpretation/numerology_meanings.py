"""
numerology_meanings.py
Meaning blocks for core and cycle numerology numbers.
"""

NUMEROLOGY_MEANINGS = {
    "life_path": {"text": "Core trajectory and repeated lessons.", "tags": ["purpose"], "weights": {"general": 0.6, "career": 0.5}},
    "expression": {"text": "How talents express outwardly.", "tags": ["talent"], "weights": {"career": 0.5, "general": 0.4}},
    "soul_urge": {"text": "Deepest heart desires and attraction style.", "tags": ["love", "emotional"], "weights": {"love": 0.6, "emotional": 0.5}},
    "personality": {"text": "Outer mask and first impression.", "tags": ["social"], "weights": {"general": 0.3}},
    "personal_year": {"text": "Theme of the year—macro timing.", "tags": ["timing"], "weights": {"general": 0.3, "career": 0.3}},
    "personal_month": {"text": "Month flavor—micro timing.", "tags": ["timing"], "weights": {"general": 0.2}},
    "personal_day": {"text": "Day tone—fine timing.", "tags": ["timing"], "weights": {"general": 0.1}},
    # Number-specific sample meanings (extendable)
    "number_1": {"text": "Initiation, independence, first moves.", "tags": ["start"], "weights": {"general": 0.3, "career": 0.3}},
    "number_2": {"text": "Cooperation, diplomacy, pairing.", "tags": ["partnership"], "weights": {"love": 0.3, "general": 0.2}},
    "number_3": {"text": "Expression, creativity, visibility.", "tags": ["expression"], "weights": {"general": 0.3, "career": 0.2}},
    "number_4": {"text": "Foundation, structure, steady building.", "tags": ["structure"], "weights": {"career": 0.3}},
    "number_5": {"text": "Change, freedom, adaptability.", "tags": ["change"], "weights": {"general": 0.3}},
    "number_6": {"text": "Care, responsibility, service.", "tags": ["care"], "weights": {"love": 0.3, "general": 0.2}},
    "number_7": {"text": "Insight, reflection, analysis.", "tags": ["insight"], "weights": {"spiritual": 0.3, "general": 0.2}},
    "number_8": {"text": "Power, material mastery, influence.", "tags": ["power"], "weights": {"career": 0.3}},
    "number_9": {"text": "Completion, compassion, release.", "tags": ["closure"], "weights": {"spiritual": 0.3, "emotional": 0.2}},
}
