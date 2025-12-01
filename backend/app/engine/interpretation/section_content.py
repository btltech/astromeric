"""
section_content.py
------------------
Rich, unique content generators for each reading section.
Each section gets different metaphors, examples, scenarios, and actionable tips.
No repetition across sections - each has its own voice and focus.
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Dict, List, Optional

# ========== OVERVIEW SECTION ==========

OVERVIEW_OPENERS = [
    "The cosmic stage is set: {theme}. Picture yourself standing at a crossroads where {metaphor}.",
    "Today's stellar canvas reveals {theme}. Imagine {metaphor}—this is your energy right now.",
    "The universe whispers of {theme}. Think of it like {metaphor}.",
    "Celestial currents carry {theme}. It's as if {metaphor}.",
    "The stars align around {theme}. Envision {metaphor}.",
]

OVERVIEW_METAPHORS = {
    "Fire": [
        "a spark catching on dry tinder, ready to blaze",
        "the first rays of dawn breaking over mountains",
        "a phoenix preparing for its next magnificent flight",
    ],
    "Earth": [
        "deep roots drinking from an underground spring",
        "a master craftsperson shaping raw materials into art",
        "a garden slowly revealing its hidden treasures",
    ],
    "Air": [
        "wind carrying seeds to new fertile ground",
        "a message in a bottle finally reaching shore",
        "clouds shifting to reveal unexpected vistas",
    ],
    "Water": [
        "a tide turning under the moon's gentle pull",
        "still waters reflecting truths you've been avoiding",
        "a river finding its way around ancient stones",
    ],
}

OVERVIEW_SCENARIOS = [
    "Whether you're tackling a project or simply navigating daily routines, {action}.",
    "From morning coffee to evening wind-down, {action}.",
    "In conversations, decisions, and quiet moments alike, {action}.",
    "As you move through your day, {action}.",
]

OVERVIEW_ACTIONS = {
    "confident": [
        "trust your instincts—they're particularly sharp now",
        "lean into opportunities without second-guessing",
        "let your natural authority guide you forward",
    ],
    "reflective": [
        "pause before reacting and let wisdom surface",
        "notice what patterns keep appearing",
        "give yourself permission to process slowly",
    ],
    "social": [
        "connections made today carry extra significance",
        "be open to unexpected allies appearing",
        "your words have power—use them intentionally",
    ],
    "creative": [
        "unconventional solutions are favored",
        "let your imagination lead even in practical matters",
        "color outside the lines today",
    ],
}

OVERVIEW_TIPS = [
    "🌟 Try this: {tip}",
    "💡 Quick action: {tip}",
    "✨ Cosmic suggestion: {tip}",
]

OVERVIEW_TIP_CONTENT = [
    "Set one intention before checking your phone this morning",
    "Take three deep breaths before any important interaction",
    "Write down one thing you're grateful for before bed",
    "Move your body for at least 10 minutes today",
    "Tell one person something you appreciate about them",
    "Step outside and look at the sky for 60 seconds",
    "Drink an extra glass of water with intention",
    "Put one item back in its proper place with mindfulness",
]

# ========== LOVE SECTION ==========

LOVE_OPENERS = [
    "💕 Heart weather report: {theme}. Romantically speaking, {metaphor}.",
    "💗 The love forecast shows {theme}. In matters of the heart, {metaphor}.",
    "💖 Venus energy brings {theme}. Your relating style today is like {metaphor}.",
    "❤️ Emotional currents reveal {theme}. Connection-wise, think of {metaphor}.",
]

LOVE_METAPHORS = {
    "passionate": [
        "a dance where both partners know exactly when to lead",
        "magnets finally finding their perfect alignment",
        "two flames merging into something brighter",
    ],
    "gentle": [
        "morning mist softening all the hard edges",
        "a warm blanket on a cold night",
        "two streams quietly joining into one river",
    ],
    "communicative": [
        "finally finding the right words for a song",
        "a conversation that flows like music",
        "messages written in starlight suddenly becoming clear",
    ],
    "introspective": [
        "a mirror revealing your true reflection",
        "a letter to yourself finally getting opened",
        "discovering a hidden room in a familiar house",
    ],
}

LOVE_SCENARIOS = [
    "If you're partnered: {partnered}. If single: {single}.",
    "For those in relationships: {partnered}. Flying solo? {single}.",
    "Coupled up? {partnered}. On your own? {single}.",
]

LOVE_PARTNERED = [
    "small gestures speak louder than grand declarations today",
    "revisit a conversation that got cut short",
    "physical presence matters more than perfect words",
    "share something you've been holding back",
    "notice what your partner needs without them asking",
]

LOVE_SINGLE = [
    "chance encounters have extra potential now",
    "self-love practices are your secret weapon",
    "the universe is taking notes on what you truly desire",
    "authenticity is more magnetic than strategy",
    "focus on becoming what you want to attract",
]

LOVE_TIPS = [
    "💝 Relationship booster: {tip}",
    "💌 Connection upgrade: {tip}",
    "🌹 Love action: {tip}",
]

LOVE_TIP_CONTENT = [
    "Send an unexpected appreciation text (no special occasion needed)",
    "Put your phone away during your next conversation",
    "Ask a question you've never asked before",
    "Offer a 6-second hug instead of a quick squeeze",
    "Cook or order their favorite comfort food",
    "Listen without trying to fix or advise",
    "Share a vulnerability you've been guarding",
    "Plan something for next week together",
]

# ========== CAREER SECTION ==========

CAREER_OPENERS = [
    "💼 Professional weather: {theme}. Your work energy is like {metaphor}.",
    "📊 Career currents show {theme}. Think of your professional path as {metaphor}.",
    "🎯 Ambition forecast reveals {theme}. Your momentum resembles {metaphor}.",
    "⚡ Success signals indicate {theme}. Picture your career as {metaphor}.",
]

CAREER_METAPHORS = {
    "ambitious": [
        "a rocket on the launchpad, systems go",
        "a chess player three moves ahead",
        "an architect seeing the completed building in their mind",
    ],
    "steady": [
        "a skilled gardener tending proven crops",
        "a carpenter measuring twice, cutting once",
        "a marathon runner finding their sustainable pace",
    ],
    "innovative": [
        "an inventor with a breakthrough on the whiteboard",
        "a musician discovering an unexpected chord progression",
        "a scout finding an uncharted path",
    ],
    "collaborative": [
        "an orchestra where every section knows its part",
        "a basketball team in perfect flow state",
        "a hive buzzing with coordinated purpose",
    ],
}

CAREER_SCENARIOS = [
    "In meetings and negotiations: {meeting}. For solo work: {solo}.",
    "When collaborating: {meeting}. During focused time: {solo}.",
    "With colleagues: {meeting}. At your desk: {solo}.",
]

CAREER_MEETING = [
    "your ideas will land better than you expect",
    "listen for the subtext beneath what's said",
    "position yourself as a bridge-builder",
    "let others speak first, then synthesize",
    "propose solutions, not just problems",
]

CAREER_SOLO = [
    "tackle the hardest task while energy is fresh",
    "batch similar tasks for better flow",
    "take breaks before you need them",
    "document your wins, however small",
    "clear one thing from your backlog completely",
]

CAREER_TIPS = [
    "💰 Money move: {tip}",
    "🚀 Career boost: {tip}",
    "📈 Growth action: {tip}",
]

CAREER_TIP_CONTENT = [
    "Review one financial statement you've been avoiding",
    "Reach out to someone in your field you admire",
    "Update one line on your resume or portfolio",
    "Set a 25-minute timer and do one deep work session",
    "Archive or delete 10 old emails or files",
    "Schedule a meeting you've been putting off",
    "Learn one new shortcut for a tool you use daily",
    "Thank someone who helped your career recently",
]

# ========== EMOTIONAL / SPIRITUAL SECTION ==========

EMOTIONAL_OPENERS = [
    "🌙 Soul weather: {theme}. Your inner landscape resembles {metaphor}.",
    "🔮 Spiritual currents carry {theme}. Within you, it's like {metaphor}.",
    "🕊️ The emotional forecast shows {theme}. Your spirit is like {metaphor}.",
    "💫 Inner world report: {theme}. Deep down, imagine {metaphor}.",
]

EMOTIONAL_METAPHORS = {
    "transformative": [
        "a chrysalis right before the breakthrough",
        "a snake approaching its shedding time",
        "old maps being redrawn with new territories",
    ],
    "peaceful": [
        "a lake so still it mirrors the sky perfectly",
        "a meditation bell's tone fading into silence",
        "morning light filling a quiet room",
    ],
    "seeking": [
        "a compass needle swinging toward true north",
        "an astronomer training their telescope on a new star",
        "roots reaching deeper for hidden water",
    ],
    "processing": [
        "a library reorganizing its shelves",
        "a river depositing silt before joining the sea",
        "a wound finally being allowed to breathe",
    ],
}

EMOTIONAL_SCENARIOS = [
    "For your mental health: {mental}. For spiritual practice: {spiritual}.",
    "Emotionally: {mental}. On a soul level: {spiritual}.",
    "In your inner world: {mental}. For deeper meaning: {spiritual}.",
]

EMOTIONAL_MENTAL = [
    "feelings that surface today carry important data",
    "what drains you is asking to be released",
    "your intuition is unusually accurate now",
    "old triggers may appear for final healing",
    "rest is not laziness—it's integration time",
]

EMOTIONAL_SPIRITUAL = [
    "signs and synchronicities are worth noting",
    "meditation or stillness practices are extra potent",
    "ancestors or guides may feel closer",
    "dreams tonight may carry messages",
    "creative expression becomes a spiritual act",
]

EMOTIONAL_TIPS = [
    "🧘 Soul practice: {tip}",
    "🌿 Wellness ritual: {tip}",
    "✨ Inner work: {tip}",
]

EMOTIONAL_TIP_CONTENT = [
    "Do a 5-minute body scan and notice where you hold tension",
    "Journal three sentences about how you really feel",
    "Light a candle and set one intention for inner peace",
    "Take a walk without your phone or music",
    "Give yourself permission to feel whatever arises",
    "Practice saying 'no' to one energy-draining thing",
    "Spend 2 minutes in gratitude for your body",
    "Create a small altar or sacred space corner",
]


def get_element_from_sign(sign: str) -> str:
    """Get element for a zodiac sign."""
    elements = {
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
    }
    return elements.get(sign, "Fire")


def get_energy_mode(blocks: List[Dict], topic: str) -> str:
    """Determine dominant energy mode from blocks."""
    modes = {
        "overview": ["confident", "reflective", "social", "creative"],
        "love": ["passionate", "gentle", "communicative", "introspective"],
        "career": ["ambitious", "steady", "innovative", "collaborative"],
        "emotional": ["transformative", "peaceful", "seeking", "processing"],
    }
    
    # Score based on block tags and weights
    scores = {mode: 0 for mode in modes.get(topic, ["default"])}
    
    tag_mappings = {
        "confident": ["action", "assertion", "leadership", "fire"],
        "reflective": ["insight", "wisdom", "contemplation", "water"],
        "social": ["connection", "communication", "partnership", "air"],
        "creative": ["creativity", "innovation", "expression", "art"],
        "passionate": ["love", "desire", "attraction", "intensity"],
        "gentle": ["nurturing", "care", "softness", "support"],
        "communicative": ["communication", "expression", "dialogue"],
        "introspective": ["self", "inner", "reflection", "alone"],
        "ambitious": ["career", "success", "achievement", "status"],
        "steady": ["stability", "consistency", "routine", "grounding"],
        "innovative": ["change", "novelty", "innovation", "breakthrough"],
        "collaborative": ["teamwork", "partnership", "cooperation"],
        "transformative": ["transformation", "change", "rebirth", "power"],
        "peaceful": ["peace", "calm", "serenity", "rest"],
        "seeking": ["seeking", "purpose", "meaning", "spiritual"],
        "processing": ["emotional", "healing", "processing", "release"],
    }
    
    for block in blocks:
        block_tags = block.get("tags", [])
        for mode, keywords in tag_mappings.items():
            if mode in scores:
                for tag in block_tags:
                    if tag.lower() in keywords:
                        scores[mode] += 1
    
    if not scores or max(scores.values()) == 0:
        return random.choice(list(scores.keys())) if scores else "default"
    
    return max(scores, key=scores.get)


def generate_overview_content(
    blocks: List[Dict],
    element: str,
    theme: str,
    seed: str,
) -> Dict:
    """Generate unique overview section content."""
    random.seed(hash(seed + "overview"))
    
    mode = get_energy_mode(blocks, "overview")
    metaphor = random.choice(OVERVIEW_METAPHORS.get(element, OVERVIEW_METAPHORS["Fire"]))
    opener = random.choice(OVERVIEW_OPENERS).format(theme=theme, metaphor=metaphor)
    
    scenario = random.choice(OVERVIEW_SCENARIOS).format(
        action=random.choice(OVERVIEW_ACTIONS.get(mode, OVERVIEW_ACTIONS["confident"]))
    )
    
    tip_template = random.choice(OVERVIEW_TIPS)
    tip = tip_template.format(tip=random.choice(OVERVIEW_TIP_CONTENT))
    
    highlights = [opener, scenario]
    for block in blocks[:2]:
        highlights.append(f"{block.get('source', 'Stars')}: {block.get('text', '')}")
    highlights.append(tip)
    
    return {
        "title": "Overview",
        "highlights": highlights,
        "affirmation": f"Today, I embrace {theme.lower()} with confidence and grace.",
        "energy_mode": mode,
    }


def generate_love_content(
    blocks: List[Dict],
    theme: str,
    seed: str,
) -> Dict:
    """Generate unique love & relationships content."""
    random.seed(hash(seed + "love"))
    
    mode = get_energy_mode(blocks, "love")
    metaphor = random.choice(LOVE_METAPHORS.get(mode, LOVE_METAPHORS["gentle"]))
    opener = random.choice(LOVE_OPENERS).format(theme=theme, metaphor=metaphor)
    
    scenario = random.choice(LOVE_SCENARIOS).format(
        partnered=random.choice(LOVE_PARTNERED),
        single=random.choice(LOVE_SINGLE)
    )
    
    tip_template = random.choice(LOVE_TIPS)
    tip = tip_template.format(tip=random.choice(LOVE_TIP_CONTENT))
    
    highlights = [opener, scenario]
    for block in blocks[:2]:
        if "love" in block.get("tags", []) or block.get("weights", {}).get("love", 0) > 0.3:
            highlights.append(f"{block.get('source', 'Venus')}: {block.get('text', '')}")
    highlights.append(tip)
    
    return {
        "title": "Love & Relationships",
        "highlights": highlights,
        "affirmation": "I am worthy of deep, authentic connection.",
        "energy_mode": mode,
    }


def generate_career_content(
    blocks: List[Dict],
    theme: str,
    seed: str,
) -> Dict:
    """Generate unique career & money content."""
    random.seed(hash(seed + "career"))
    
    mode = get_energy_mode(blocks, "career")
    metaphor = random.choice(CAREER_METAPHORS.get(mode, CAREER_METAPHORS["steady"]))
    opener = random.choice(CAREER_OPENERS).format(theme=theme, metaphor=metaphor)
    
    scenario = random.choice(CAREER_SCENARIOS).format(
        meeting=random.choice(CAREER_MEETING),
        solo=random.choice(CAREER_SOLO)
    )
    
    tip_template = random.choice(CAREER_TIPS)
    tip = tip_template.format(tip=random.choice(CAREER_TIP_CONTENT))
    
    highlights = [opener, scenario]
    for block in blocks[:2]:
        if "career" in block.get("tags", []) or block.get("weights", {}).get("career", 0) > 0.3:
            highlights.append(f"{block.get('source', 'Saturn')}: {block.get('text', '')}")
    highlights.append(tip)
    
    return {
        "title": "Career & Money",
        "highlights": highlights,
        "affirmation": "I create value and receive abundance in return.",
        "energy_mode": mode,
    }


def generate_emotional_content(
    blocks: List[Dict],
    theme: str,
    seed: str,
) -> Dict:
    """Generate unique emotional & spiritual content."""
    random.seed(hash(seed + "emotional"))
    
    mode = get_energy_mode(blocks, "emotional")
    metaphor = random.choice(EMOTIONAL_METAPHORS.get(mode, EMOTIONAL_METAPHORS["peaceful"]))
    opener = random.choice(EMOTIONAL_OPENERS).format(theme=theme, metaphor=metaphor)
    
    scenario = random.choice(EMOTIONAL_SCENARIOS).format(
        mental=random.choice(EMOTIONAL_MENTAL),
        spiritual=random.choice(EMOTIONAL_SPIRITUAL)
    )
    
    tip_template = random.choice(EMOTIONAL_TIPS)
    tip = tip_template.format(tip=random.choice(EMOTIONAL_TIP_CONTENT))
    
    highlights = [opener, scenario]
    for block in blocks[:2]:
        if "emotional" in block.get("tags", []) or block.get("weights", {}).get("emotional", 0) > 0.3:
            highlights.append(f"{block.get('source', 'Moon')}: {block.get('text', '')}")
    highlights.append(tip)
    
    return {
        "title": "Emotional & Spiritual",
        "highlights": highlights,
        "affirmation": "I honor my inner world and trust my spiritual journey.",
        "energy_mode": mode,
    }


def generate_all_sections(
    blocks: List[Dict],
    element: str,
    overall_theme: str,
    numerology: Dict,
    seed: str,
) -> List[Dict]:
    """Generate all four sections with unique, non-repeating content."""
    
    # Derive topic-specific themes
    overview_theme = overall_theme
    love_theme = _derive_love_theme(blocks, numerology)
    career_theme = _derive_career_theme(blocks, numerology)
    emotional_theme = _derive_emotional_theme(blocks, numerology)
    
    sections = [
        generate_overview_content(blocks, element, overview_theme, seed),
        generate_love_content(blocks, love_theme, seed),
        generate_career_content(blocks, career_theme, seed),
        generate_emotional_content(blocks, emotional_theme, seed),
    ]
    
    return sections


def _derive_love_theme(blocks: List[Dict], numerology: Dict) -> str:
    """Create a love-specific theme from blocks and numerology."""
    love_blocks = [b for b in blocks if "love" in b.get("tags", [])]
    if love_blocks:
        return love_blocks[0].get("text", "connection energy")[:50]
    
    pd = numerology.get("cycles", {}).get("personal_day", {}).get("number", 1)
    love_themes = {
        1: "new beginnings in connection",
        2: "partnership harmony",
        3: "playful expression",
        4: "building trust",
        5: "unexpected chemistry",
        6: "nurturing bonds",
        7: "deep understanding",
        8: "powerful attraction",
        9: "compassionate love",
    }
    return love_themes.get(pd, "heart-centered energy")


def _derive_career_theme(blocks: List[Dict], numerology: Dict) -> str:
    """Create a career-specific theme from blocks and numerology."""
    career_blocks = [b for b in blocks if "career" in b.get("tags", [])]
    if career_blocks:
        return career_blocks[0].get("text", "professional momentum")[:50]
    
    py = numerology.get("cycles", {}).get("personal_year", {}).get("number", 1)
    career_themes = {
        1: "initiative and leadership",
        2: "collaborative success",
        3: "creative expression at work",
        4: "solid foundations",
        5: "career pivots",
        6: "service and responsibility",
        7: "strategic planning",
        8: "financial growth",
        9: "completion and harvest",
    }
    return career_themes.get(py, "professional growth")


def _derive_emotional_theme(blocks: List[Dict], numerology: Dict) -> str:
    """Create an emotional-specific theme from blocks and numerology."""
    emotional_blocks = [b for b in blocks if "emotional" in b.get("tags", [])]
    if emotional_blocks:
        return emotional_blocks[0].get("text", "inner transformation")[:50]
    
    pm = numerology.get("cycles", {}).get("personal_month", {}).get("number", 1)
    emotional_themes = {
        1: "self-discovery",
        2: "emotional balance",
        3: "joyful expression",
        4: "grounding stability",
        5: "liberating change",
        6: "healing and care",
        7: "spiritual deepening",
        8: "personal power",
        9: "release and renewal",
    }
    return emotional_themes.get(pm, "inner growth")
