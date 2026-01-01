"""
learning_content.py
-------------------
Expanded learning content: moon signs, rising signs, elements, retrogrades, and mini-courses.
"""

from __future__ import annotations

from typing import Dict, List
from ..interpretation.translations import get_translation

# ========== MOON SIGNS ==========

MOON_SIGNS = {
    "Aries": {
        "title": "Aries Moon",
        "emoji": "🔥",
        "short_desc": "Your emotional nature is fiery, impulsive, and action-oriented.",
        "full_desc": (
            "With your Moon in Aries, you process emotions through action. When you feel something, "
            "you need to DO something about it immediately. You may have quick emotional reactions "
            "that flare up intensely but burn out just as fast.\n\n"
            "You feel most secure when you're independent and can make your own decisions. Being "
            "controlled or having to wait triggers restlessness. Your instinctive response to "
            "challenge is to fight, not flee."
        ),
        "needs": ["Independence", "Action", "Challenge", "To be first"],
        "struggles": ["Patience", "Emotional sensitivity", "Sitting with feelings"],
        "nurtures_self": "Through physical activity, competition, and starting new projects.",
        "in_relationships": "Direct and honest but can seem insensitive. Loves the chase.",
    },
    "Taurus": {
        "title": "Taurus Moon",
        "emoji": "🌿",
        "short_desc": "Your emotional nature is steady, sensual, and comfort-seeking.",
        "full_desc": (
            "With your Moon in Taurus, you process emotions slowly and deliberately. You need time "
            "to feel things fully before reacting. Once you've formed an emotional attachment, "
            "it's nearly unbreakable.\n\n"
            "You feel most secure when surrounded by physical comfort—good food, soft textures, "
            "financial stability. Sudden changes or instability shake you to your core."
        ),
        "needs": ["Security", "Comfort", "Consistency", "Physical pleasure"],
        "struggles": ["Change", "Letting go", "Emotional flexibility"],
        "nurtures_self": "Through sensory pleasures, nature walks, and financial stability.",
        "in_relationships": "Loyal and devoted but can be possessive. Shows love through care.",
    },
    "Gemini": {
        "title": "Gemini Moon",
        "emoji": "💨",
        "short_desc": "Your emotional nature is curious, communicative, and changeable.",
        "full_desc": (
            "With your Moon in Gemini, you process emotions through talking and thinking. You need "
            "to verbalize feelings to understand them. Your moods can shift quickly based on "
            "mental stimulation or lack thereof.\n\n"
            "You feel most secure when you have mental engagement and variety. Boredom is "
            "emotionally painful for you. You may sometimes intellectualize feelings rather than "
            "fully feeling them."
        ),
        "needs": ["Mental stimulation", "Communication", "Variety", "Information"],
        "struggles": ["Emotional depth", "Commitment", "Sitting still"],
        "nurtures_self": "Through reading, conversation, learning new things, and social variety.",
        "in_relationships": "Witty and fun but can seem emotionally detached. Needs talking.",
    },
    "Cancer": {
        "title": "Cancer Moon",
        "emoji": "🌙",
        "short_desc": "Your emotional nature is nurturing, intuitive, and protective.",
        "full_desc": (
            "With your Moon in Cancer, you are deeply in touch with your emotions—and everyone else's. "
            "You absorb the moods around you like a sponge. Your intuition is remarkably accurate.\n\n"
            "You feel most secure in the home, surrounded by family or chosen family. You need to "
            "nurture and be nurtured. Past memories, especially childhood, strongly influence your "
            "current emotional patterns."
        ),
        "needs": ["Emotional security", "Home base", "Nurturing", "Family connection"],
        "struggles": ["Letting go of the past", "Emotional boundaries", "Moodiness"],
        "nurtures_self": "Through cooking, home comforts, family time, and nostalgic activities.",
        "in_relationships": "Deeply caring and intuitive but can be clingy or moody.",
    },
    "Leo": {
        "title": "Leo Moon",
        "emoji": "☀️",
        "short_desc": "Your emotional nature is warm, expressive, and recognition-seeking.",
        "full_desc": (
            "With your Moon in Leo, you feel things dramatically and need to express emotions "
            "creatively and boldly. You have a deep need to be seen, appreciated, and admired for "
            "who you truly are.\n\n"
            "You feel most secure when you're receiving positive attention and can shine in some way. "
            "Being ignored or criticized cuts deeply. Your warmth is genuine and generous."
        ),
        "needs": ["Recognition", "Appreciation", "Creative expression", "To feel special"],
        "struggles": ["Criticism", "Being overlooked", "Sharing the spotlight"],
        "nurtures_self": "Through creative expression, romance, play, and positive feedback.",
        "in_relationships": "Loyal and generous but needs constant validation. Grand gestures.",
    },
    "Virgo": {
        "title": "Virgo Moon",
        "emoji": "📋",
        "short_desc": "Your emotional nature is analytical, helpful, and perfectionist.",
        "full_desc": (
            "With your Moon in Virgo, you process emotions through analysis and problem-solving. "
            "When you feel something, you want to understand why and fix any issues. You may "
            "criticize yourself harshly for emotional 'imperfections.'\n\n"
            "You feel most secure when life is orderly and you're being useful. Chaos and "
            "inefficiency trigger anxiety. You show love through practical help and attention to detail."
        ),
        "needs": ["Order", "Usefulness", "Health routines", "To be helpful"],
        "struggles": ["Self-criticism", "Anxiety", "Accepting imperfection"],
        "nurtures_self": "Through organizing, health practices, being of service, and craft work.",
        "in_relationships": "Devoted and thoughtful but can be critical. Shows love through help.",
    },
    "Libra": {
        "title": "Libra Moon",
        "emoji": "⚖️",
        "short_desc": "Your emotional nature is harmony-seeking, diplomatic, and partnership-oriented.",
        "full_desc": (
            "With your Moon in Libra, you process emotions through the lens of relationships and "
            "fairness. You deeply need harmony and may avoid conflict at the cost of your own needs. "
            "Beauty and aesthetics affect your mood significantly.\n\n"
            "You feel most secure in partnership—being alone can feel emotionally unsettling. "
            "You're a natural peacemaker but may struggle to know what you truly feel versus "
            "what you think you should feel."
        ),
        "needs": ["Harmony", "Partnership", "Beauty", "Fairness"],
        "struggles": ["Conflict", "Decision-making", "Being alone", "Own needs"],
        "nurtures_self": "Through beauty, art, harmonious relationships, and pleasant environments.",
        "in_relationships": "Romantic and diplomatic but can be indecisive or people-pleasing.",
    },
    "Scorpio": {
        "title": "Scorpio Moon",
        "emoji": "🦂",
        "short_desc": "Your emotional nature is intense, perceptive, and transformative.",
        "full_desc": (
            "With your Moon in Scorpio, you feel emotions with extraordinary intensity and depth. "
            "You experience the full spectrum—from profound love to consuming jealousy. You're "
            "psychologically perceptive and can sense hidden motives.\n\n"
            "You feel most secure when you're in emotional control and have deep, authentic bonds. "
            "Superficiality and betrayal are intolerable. You undergo periodic emotional death "
            "and rebirth cycles."
        ),
        "needs": ["Emotional depth", "Trust", "Transformation", "Control"],
        "struggles": ["Letting go", "Jealousy", "Trusting easily", "Forgiveness"],
        "nurtures_self": "Through deep intimacy, research, psychology, and cathartic release.",
        "in_relationships": "Intensely loyal and passionate but can be possessive or suspicious.",
    },
    "Sagittarius": {
        "title": "Sagittarius Moon",
        "emoji": "🏹",
        "short_desc": "Your emotional nature is optimistic, freedom-loving, and philosophical.",
        "full_desc": (
            "With your Moon in Sagittarius, you process emotions through meaning-making and expansion. "
            "You need to understand the bigger picture of why you feel what you feel. Optimism is "
            "your natural state—you bounce back from difficulties quickly.\n\n"
            "You feel most secure when you have freedom, adventure, and something to believe in. "
            "Routine and confinement are emotionally suffocating. Your honesty can sometimes be "
            "too blunt."
        ),
        "needs": ["Freedom", "Adventure", "Meaning", "Optimism"],
        "struggles": ["Commitment", "Emotional depth", "Staying present", "Tact"],
        "nurtures_self": "Through travel, learning, philosophy, outdoor adventures, and laughter.",
        "in_relationships": "Fun and inspiring but can be commitment-phobic or too blunt.",
    },
    "Capricorn": {
        "title": "Capricorn Moon",
        "emoji": "🏔️",
        "short_desc": "Your emotional nature is controlled, responsible, and achievement-oriented.",
        "full_desc": (
            "With your Moon in Capricorn, you approach emotions with maturity and restraint. "
            "You may feel uncomfortable with intense emotional displays and prefer to process "
            "feelings privately. Responsibility was likely learned young.\n\n"
            "You feel most secure through achievement, respect, and material stability. "
            "Failure or loss of status triggers deep insecurity. You show love through providing "
            "and protecting."
        ),
        "needs": ["Achievement", "Respect", "Structure", "Tangible security"],
        "struggles": ["Emotional expression", "Vulnerability", "Relaxing"],
        "nurtures_self": "Through goal achievement, work, building things, and earning respect.",
        "in_relationships": "Loyal and providing but can seem cold or workaholic.",
    },
    "Aquarius": {
        "title": "Aquarius Moon",
        "emoji": "⚡",
        "short_desc": "Your emotional nature is independent, humanitarian, and unconventional.",
        "full_desc": (
            "With your Moon in Aquarius, you approach emotions with intellectual detachment. "
            "You need space to process feelings and may feel uncomfortable with emotional demands. "
            "You genuinely care about humanity but may struggle with one-on-one intimacy.\n\n"
            "You feel most secure when you have personal freedom and can be authentically different. "
            "Conformity feels like emotional death. You need friends who accept your quirks."
        ),
        "needs": ["Freedom", "Authenticity", "Friendship", "Causes"],
        "struggles": ["Emotional intimacy", "Conventional expectations", "Being ordinary"],
        "nurtures_self": "Through friendships, causes, innovation, and intellectual pursuits.",
        "in_relationships": "Loyal friend-lover but can seem detached or unpredictable.",
    },
    "Pisces": {
        "title": "Pisces Moon",
        "emoji": "🌊",
        "short_desc": "Your emotional nature is sensitive, imaginative, and empathic.",
        "full_desc": (
            "With your Moon in Pisces, you feel emotions without boundaries—yours, others', "
            "and the collective's. Your sensitivity is both a gift (profound empathy) and a "
            "challenge (overwhelm). You need regular escape into imagination or spirituality.\n\n"
            "You feel most secure when connected to something transcendent. Harsh reality can "
            "feel emotionally brutal. You may struggle to distinguish your feelings from others'."
        ),
        "needs": ["Spiritual connection", "Escape", "Compassion", "Creative expression"],
        "struggles": ["Boundaries", "Reality", "Overwhelm", "Escapism"],
        "nurtures_self": "Through art, music, water, meditation, and spiritual practice.",
        "in_relationships": "Deeply compassionate and romantic but can be too self-sacrificing.",
    },
}


# ========== RISING SIGNS ==========

RISING_SIGNS = {
    "Aries": {
        "title": "Aries Rising",
        "emoji": "🚀",
        "first_impression": "Energetic, direct, competitive, impatient",
        "appearance": "Athletic build, prominent forehead or eyebrows, quick movements",
        "life_approach": (
            "You attack life head-on. Your first instinct is action, not planning. "
            "People see you as a leader and self-starter. You may come across as "
            "intimidating even when you're not trying."
        ),
        "growth_edge": "Learning patience and considering others before charging ahead.",
    },
    "Taurus": {
        "title": "Taurus Rising",
        "emoji": "🌸",
        "first_impression": "Calm, reliable, stubborn, sensual",
        "appearance": "Solid build, pleasant features, deliberate movements, nice voice",
        "life_approach": (
            "You move through life at your own pace, refusing to be rushed. "
            "People see you as dependable and grounded. Your presence is calming "
            "but your resistance to change can frustrate others."
        ),
        "growth_edge": "Embracing necessary change and being more flexible.",
    },
    "Gemini": {
        "title": "Gemini Rising",
        "emoji": "🦋",
        "first_impression": "Talkative, curious, restless, youthful",
        "appearance": "Expressive hands, bright eyes, slim build, animated expressions",
        "life_approach": (
            "You engage with life through questions and communication. "
            "People see you as interesting and versatile but possibly scattered. "
            "You're often doing multiple things at once."
        ),
        "growth_edge": "Developing focus and following through on commitments.",
    },
    "Cancer": {
        "title": "Cancer Rising",
        "emoji": "🦀",
        "first_impression": "Nurturing, protective, moody, approachable",
        "appearance": "Round face, expressive eyes, changes in weight tied to emotions",
        "life_approach": (
            "You approach life with emotional sensitivity and protectiveness. "
            "People instinctively trust you with their feelings. Your shell protects "
            "a deeply vulnerable interior."
        ),
        "growth_edge": "Not taking everything personally and building emotional resilience.",
    },
    "Leo": {
        "title": "Leo Rising",
        "emoji": "🦁",
        "first_impression": "Confident, dramatic, generous, attention-seeking",
        "appearance": "Mane-like hair, proud posture, warm smile, theatrical presence",
        "life_approach": (
            "You enter every room like the star of your own show. "
            "People are drawn to your warmth and confidence. You need to shine "
            "but also lift others up."
        ),
        "growth_edge": "Sharing the spotlight and receiving criticism gracefully.",
    },
    "Virgo": {
        "title": "Virgo Rising",
        "emoji": "📝",
        "first_impression": "Reserved, helpful, critical, detail-oriented",
        "appearance": "Neat appearance, youthful looks, intelligent eyes, modest dress",
        "life_approach": (
            "You approach life analytically, always improving and refining. "
            "People see you as competent and helpful but possibly judgmental. "
            "You notice what's wrong before what's right."
        ),
        "growth_edge": "Accepting imperfection in yourself and others.",
    },
    "Libra": {
        "title": "Libra Rising",
        "emoji": "💫",
        "first_impression": "Charming, diplomatic, indecisive, stylish",
        "appearance": "Symmetrical features, pleasant demeanor, stylish dress, dimples",
        "life_approach": (
            "You approach life seeking balance and harmony. "
            "People find you agreeable and easy to like. Your challenge is "
            "maintaining your own identity amid constant accommodation."
        ),
        "growth_edge": "Making decisions and standing firm in your values.",
    },
    "Scorpio": {
        "title": "Scorpio Rising",
        "emoji": "🔮",
        "first_impression": "Intense, magnetic, secretive, powerful",
        "appearance": "Penetrating eyes, strong presence, dark features, still body",
        "life_approach": (
            "You approach life with intensity and strategic awareness. "
            "People sense your power and may feel either drawn to or wary of you. "
            "You see through facades instantly."
        ),
        "growth_edge": "Trusting others and revealing vulnerability.",
    },
    "Sagittarius": {
        "title": "Sagittarius Rising",
        "emoji": "🌍",
        "first_impression": "Optimistic, adventurous, blunt, restless",
        "appearance": "Tall, athletic, infectious smile, casual dress, open posture",
        "life_approach": (
            "You approach life as an adventure and quest for meaning. "
            "People see you as inspiring and fun but possibly unreliable. "
            "You're always looking toward the next horizon."
        ),
        "growth_edge": "Following through and being present where you are.",
    },
    "Capricorn": {
        "title": "Capricorn Rising",
        "emoji": "🏆",
        "first_impression": "Serious, ambitious, reserved, mature",
        "appearance": "Defined bone structure, ages well, conservative dress, dignified bearing",
        "life_approach": (
            "You approach life as a mountain to climb, step by step. "
            "People see you as responsible and capable but possibly cold. "
            "You improve with age as your true warmth emerges."
        ),
        "growth_edge": "Relaxing, playing, and showing your softer side.",
    },
    "Aquarius": {
        "title": "Aquarius Rising",
        "emoji": "🌐",
        "first_impression": "Unique, friendly, eccentric, detached",
        "appearance": "Unusual features, distinctive style, bright eyes, unpredictable",
        "life_approach": (
            "You approach life as an experiment in being different. "
            "People see you as interesting and humanitarian but possibly aloof. "
            "You connect best with fellow free thinkers."
        ),
        "growth_edge": "Connecting emotionally one-on-one, not just with groups.",
    },
    "Pisces": {
        "title": "Pisces Rising",
        "emoji": "🧜",
        "first_impression": "Dreamy, compassionate, vague, artistic",
        "appearance": "Soft features, soulful eyes, gentle voice, floaty presence",
        "life_approach": (
            "You approach life with imagination and sensitivity. "
            "People see you as kind and artistic but possibly impractical. "
            "You absorb the energy of your environment completely."
        ),
        "growth_edge": "Developing boundaries and grounding in practical reality.",
    },
}


# ========== ELEMENTS & MODALITIES ==========

ELEMENTS = {
    "Fire": {
        "signs": ["Aries", "Leo", "Sagittarius"],
        "emoji": "🔥",
        "keywords": ["Action", "Inspiration", "Energy", "Enthusiasm"],
        "description": (
            "Fire signs burn with enthusiasm and inspire others to action. "
            "They lead with courage, create with passion, and live with boldness. "
            "Too much fire can cause burnout or aggression; too little leads to depression."
        ),
        "balanced": "Warmth, confidence, creativity, leadership",
        "excessive": "Aggression, burnout, arrogance, impulsivity",
        "deficient": "Low energy, depression, timidity, lack of inspiration",
        "activities": ["Exercise", "Competition", "Leadership roles", "Creative projects"],
    },
    "Earth": {
        "signs": ["Taurus", "Virgo", "Capricorn"],
        "emoji": "🌍",
        "keywords": ["Stability", "Practicality", "Sensuality", "Building"],
        "description": (
            "Earth signs ground ideas into reality. They build, stabilize, and manifest. "
            "They connect to the physical world through senses and tangible results. "
            "Too much earth can mean rigidity; too little means groundlessness."
        ),
        "balanced": "Reliability, productivity, sensory pleasure, practical wisdom",
        "excessive": "Materialism, stubbornness, workaholism, rigidity",
        "deficient": "Ungroundedness, impracticality, financial chaos, disconnection from body",
        "activities": ["Gardening", "Cooking", "Financial planning", "Crafts"],
    },
    "Air": {
        "signs": ["Gemini", "Libra", "Aquarius"],
        "emoji": "💨",
        "keywords": ["Thought", "Communication", "Connection", "Ideas"],
        "description": (
            "Air signs think, communicate, and connect. They process life through ideas "
            "and social interaction. They bring objectivity and perspective. "
            "Too much air means overthinking; too little means close-mindedness."
        ),
        "balanced": "Clear thinking, good communication, social grace, objectivity",
        "excessive": "Overthinking, detachment, scattered energy, all talk no action",
        "deficient": "Poor communication, isolation, narrow thinking, prejudice",
        "activities": ["Reading", "Socializing", "Debates", "Writing"],
    },
    "Water": {
        "signs": ["Cancer", "Scorpio", "Pisces"],
        "emoji": "🌊",
        "keywords": ["Emotion", "Intuition", "Healing", "Depth"],
        "description": (
            "Water signs feel, intuit, and heal. They connect to the emotional undercurrents "
            "of life and bring depth to experience. They excel at empathy and creativity. "
            "Too much water means drowning; too little means emotional emptiness."
        ),
        "balanced": "Emotional intelligence, intuition, compassion, creativity",
        "excessive": "Overwhelm, mood swings, boundary issues, escapism",
        "deficient": "Emotional numbness, disconnection, inability to empathize",
        "activities": ["Journaling", "Art therapy", "Water activities", "Meditation"],
    },
}

MODALITIES = {
    "Cardinal": {
        "signs": ["Aries", "Cancer", "Libra", "Capricorn"],
        "emoji": "🚀",
        "keyword": "Initiate",
        "description": (
            "Cardinal signs START things. They're the initiators, the ones who get the ball rolling. "
            "They begin new seasons and new cycles. Their challenge is follow-through."
        ),
        "strength": "Starting projects, leading, initiating change",
        "challenge": "Finishing what they start, patience",
    },
    "Fixed": {
        "signs": ["Taurus", "Leo", "Scorpio", "Aquarius"],
        "emoji": "⚓",
        "keyword": "Sustain",
        "description": (
            "Fixed signs MAINTAIN things. They're the sustainers who provide stability and depth. "
            "They're in the middle of seasons, fully established. Their challenge is flexibility."
        ),
        "strength": "Persistence, loyalty, depth, reliability",
        "challenge": "Adaptability, letting go, stubbornness",
    },
    "Mutable": {
        "signs": ["Gemini", "Virgo", "Sagittarius", "Pisces"],
        "emoji": "🦋",
        "keyword": "Adapt",
        "description": (
            "Mutable signs CHANGE things. They're the adapters who bridge one season to the next. "
            "They bring flexibility and versatility. Their challenge is commitment."
        ),
        "strength": "Adaptability, flexibility, communication, synthesis",
        "challenge": "Focus, commitment, consistency",
    },
}


# ========== RETROGRADES ==========

RETROGRADE_GUIDE = {
    "Mercury": {
        "emoji": "☿️",
        "frequency": "3-4 times per year for ~3 weeks",
        "themes": ["Communication", "Technology", "Travel", "Contracts"],
        "what_it_means": (
            "Mercury Retrograde is the most famous astrological event. Mercury, the planet of "
            "communication, appears to move backward in the sky. This creates snags in everything "
            "Mercury rules: communication, technology, travel, and agreements."
        ),
        "do": [
            "Review and revise projects",
            "Reconnect with old friends",
            "Back up your data",
            "Double-check all details",
            "Reflect on past decisions",
        ],
        "dont": [
            "Sign important contracts (if avoidable)",
            "Launch new projects",
            "Buy expensive electronics",
            "Make major decisions",
            "Assume messages were received",
        ],
        "silver_lining": "Great for revision, reconnection, and fixing old problems.",
    },
    "Venus": {
        "emoji": "♀️",
        "frequency": "Every 18 months for ~6 weeks",
        "themes": ["Love", "Values", "Beauty", "Money"],
        "what_it_means": (
            "Venus Retrograde asks us to review our values, relationships, and what we find "
            "beautiful or worthwhile. Old lovers may reappear. We question what we truly want."
        ),
        "do": [
            "Reflect on relationship patterns",
            "Reconnect with exes for closure (carefully!)",
            "Reassess your values",
            "Revisit creative projects",
            "Reevaluate finances",
        ],
        "dont": [
            "Start new relationships",
            "Get drastic beauty treatments",
            "Make major purchases",
            "Get married",
            "Launch creative projects",
        ],
        "silver_lining": "Excellent for healing old relationship wounds and clarifying values.",
    },
    "Mars": {
        "emoji": "♂️",
        "frequency": "Every 2 years for ~10 weeks",
        "themes": ["Energy", "Action", "Conflict", "Desire"],
        "what_it_means": (
            "Mars Retrograde slows down our energy and drive. We may feel less motivated, "
            "or our actions may not get the results we expect. Anger from the past may surface."
        ),
        "do": [
            "Rest and recharge",
            "Review fitness goals",
            "Process old anger",
            "Strategize before acting",
            "Finish ongoing projects",
        ],
        "dont": [
            "Start new physical challenges",
            "Pick fights",
            "Make aggressive moves",
            "Rush into action",
            "Force outcomes",
        ],
        "silver_lining": "Great for strategic planning and healing anger.",
    },
    "Jupiter": {
        "emoji": "♃",
        "frequency": "Once per year for ~4 months",
        "themes": ["Growth", "Luck", "Expansion", "Beliefs"],
        "what_it_means": (
            "Jupiter Retrograde turns growth inward. Instead of external expansion, "
            "we grow through reflection and inner development. Our beliefs get examined."
        ),
        "do": [
            "Reflect on your beliefs",
            "Inner spiritual development",
            "Finish educational pursuits",
            "Plan future growth",
            "Practice gratitude",
        ],
        "dont": [
            "Expect easy luck",
            "Over-expand",
            "Be reckless with risks",
            "Ignore philosophical questions",
        ],
        "silver_lining": "Perfect for inner growth and examining beliefs.",
    },
    "Saturn": {
        "emoji": "♄",
        "frequency": "Once per year for ~4.5 months",
        "themes": ["Structure", "Discipline", "Karma", "Boundaries"],
        "what_it_means": (
            "Saturn Retrograde reviews our structures, responsibilities, and karma. "
            "Past neglected duties may demand attention. We examine our relationship with authority."
        ),
        "do": [
            "Complete old obligations",
            "Restructure what isn't working",
            "Face karmic patterns",
            "Set better boundaries",
            "Build discipline",
        ],
        "dont": [
            "Ignore responsibilities",
            "Avoid hard work",
            "Blame authority figures",
            "Make quick commitments",
        ],
        "silver_lining": "Excellent for karmic clearing and building real discipline.",
    },
}


# ========== MINI COURSES ==========

MINI_COURSES = {
    "read_your_chart": {
        "title": "How to Read Your Own Birth Chart",
        "emoji": "📖",
        "duration": "20 minutes",
        "lessons": [
            {
                "title": "Lesson 1: The Big Three",
                "content": (
                    "Your Sun, Moon, and Rising sign form your 'Big Three'—the foundation "
                    "of your chart. Sun = core identity and ego. Moon = emotional nature and "
                    "needs. Rising = how others see you and your life approach."
                ),
                "exercise": "Write one sentence describing yourself for each of your Big Three.",
            },
            {
                "title": "Lesson 2: Planets as Players",
                "content": (
                    "Each planet represents a different part of you: Mercury (mind), Venus (love), "
                    "Mars (drive), Jupiter (growth), Saturn (discipline), and the outer planets "
                    "(generational themes). They're the 'what' of your chart."
                ),
                "exercise": "Find where Venus and Mars are in your chart—they reveal love and action styles.",
            },
            {
                "title": "Lesson 3: Signs as Styles",
                "content": (
                    "Each planet expresses itself through the filter of its sign. A Mars in Aries "
                    "takes action directly; Mars in Libra acts diplomatically. Signs are 'how' "
                    "planets operate."
                ),
                "exercise": "Look at your Mercury sign—this is your communication and thinking style.",
            },
            {
                "title": "Lesson 4: Houses as Stages",
                "content": (
                    "The 12 houses are life areas where planets perform: 1st (self), 7th (relationships), "
                    "10th (career), etc. A planet in a house brings its themes to that life area."
                ),
                "exercise": "Check which house your Sun is in—this life area seeks your attention.",
            },
            {
                "title": "Lesson 5: Aspects as Relationships",
                "content": (
                    "Aspects show how planets relate: conjunctions (intensify), squares (challenge), "
                    "trines (support), oppositions (balance). They create the dynamic tension in your chart."
                ),
                "exercise": "Find one aspect in your chart and journal about how it shows up in your life.",
            },
        ],
    },
    "numerology_basics": {
        "title": "Numerology Fundamentals",
        "emoji": "🔢",
        "duration": "15 minutes",
        "lessons": [
            {
                "title": "Lesson 1: What is Numerology?",
                "content": (
                    "Numerology is the study of the spiritual significance of numbers. "
                    "Every number carries a vibration and meaning. Your birth date and name "
                    "can be reduced to key numbers that reveal your path and personality."
                ),
                "exercise": "Write your birth date and notice which single digits appear most.",
            },
            {
                "title": "Lesson 2: Life Path Number",
                "content": (
                    "Your Life Path is the most important number—it's your main lesson in life. "
                    "Calculate by adding all digits of your birth date until you get a single digit "
                    "(or master number 11, 22, 33)."
                ),
                "exercise": "Calculate your Life Path number and read its meaning.",
            },
            {
                "title": "Lesson 3: Personal Year Cycles",
                "content": (
                    "Life moves in 9-year cycles. Your Personal Year shows the theme of the current year. "
                    "Calculate: birth month + birth day + current year, reduce to single digit."
                ),
                "exercise": "Calculate your current Personal Year and see if it matches your life.",
            },
        ],
    },
}


def get_moon_sign_lesson(sign: str, lang: str = "en") -> Dict:
    """Get detailed moon sign information."""
    data = MOON_SIGNS.get(sign, MOON_SIGNS["Aries"]).copy()
    if lang != "en":
        title_trans = get_translation(lang, f"learn_moon_{sign.lower()}_title")
        if title_trans: data["title"] = title_trans[0]
        
        short_trans = get_translation(lang, f"learn_moon_{sign.lower()}_short")
        if short_trans: data["short_desc"] = short_trans[0]
        
        full_trans = get_translation(lang, f"learn_moon_{sign.lower()}_full")
        if full_trans: data["full_desc"] = full_trans[0]
    return data


def get_rising_sign_lesson(sign: str, lang: str = "en") -> Dict:
    """Get detailed rising sign information."""
    data = RISING_SIGNS.get(sign, RISING_SIGNS["Aries"]).copy()
    if lang != "en":
        title_trans = get_translation(lang, f"learn_rising_{sign.lower()}_title")
        if title_trans: data["title"] = title_trans[0]
        
        imp_trans = get_translation(lang, f"learn_rising_{sign.lower()}_impression")
        if imp_trans: data["first_impression"] = imp_trans[0]
    return data


def get_element_lesson(element: str, lang: str = "en") -> Dict:
    """Get element information."""
    data = ELEMENTS.get(element, ELEMENTS["Fire"]).copy()
    if lang != "en":
        desc_trans = get_translation(lang, f"learn_element_{element.lower()}_desc")
        if desc_trans: data["description"] = desc_trans[0]
    return data


def get_modality_lesson(modality: str, lang: str = "en") -> Dict:
    """Get modality information."""
    data = MODALITIES.get(modality, MODALITIES["Cardinal"]).copy()
    if lang != "en":
        desc_trans = get_translation(lang, f"learn_modality_{modality.lower()}_desc")
        if desc_trans: data["description"] = desc_trans[0]
    return data


def get_retrograde_guide(planet: str, lang: str = "en") -> Dict:
    """Get retrograde survival guide for a planet."""
    data = RETROGRADE_GUIDE.get(planet, RETROGRADE_GUIDE["Mercury"]).copy()
    if lang != "en":
        means_trans = get_translation(lang, f"learn_retro_{planet.lower()}_means")
        if means_trans: data["what_it_means"] = means_trans[0]
    return data


def get_mini_course(course_id: str, lang: str = "en") -> Dict:
    """Get a mini course by ID."""
    data = MINI_COURSES.get(course_id, MINI_COURSES["read_your_chart"]).copy()
    if lang != "en":
        title_trans = get_translation(lang, f"learn_course_{course_id}_title")
        if title_trans: data["title"] = title_trans[0]
        
        desc_trans = get_translation(lang, f"learn_course_{course_id}_desc")
        if desc_trans: data["description"] = desc_trans[0]
    return data


def get_all_learning_content() -> Dict:
    """Get all learning content organized by category."""
    return {
        "moon_signs": MOON_SIGNS,
        "rising_signs": RISING_SIGNS,
        "elements": ELEMENTS,
        "modalities": MODALITIES,
        "retrogrades": RETROGRADE_GUIDE,
        "mini_courses": MINI_COURSES,
    }


# ========== API-COMPATIBLE EXPORTS ==========

# These aliases make the API endpoints work correctly
ELEMENTS_AND_MODALITIES = {
    "elements": ELEMENTS,
    "modalities": MODALITIES,
}

RETROGRADE_INFO = RETROGRADE_GUIDE


def get_learning_module(module_id: str, lang: str = "en") -> Dict:
    """Get a learning module by ID for the API."""
    modules = {
        "moon_signs": {
            "id": "moon_signs",
            "title": "Moon Signs: Your Emotional Self",
            "description": "Discover how your Moon sign shapes your inner world",
            "content": MOON_SIGNS,
        },
        "rising_signs": {
            "id": "rising_signs",
            "title": "Rising Signs: Your Cosmic Mask",
            "description": "Learn how your Ascendant influences first impressions",
            "content": RISING_SIGNS,
        },
        "elements": {
            "id": "elements",
            "title": "Elements & Modalities",
            "description": "Fire, Earth, Air, Water and Cardinal, Fixed, Mutable",
            "content": ELEMENTS_AND_MODALITIES,
        },
        "retrogrades": {
            "id": "retrogrades",
            "title": "Planetary Retrogrades",
            "description": "What happens when planets appear to move backward",
            "content": RETROGRADE_INFO,
        },
        "courses": {
            "id": "courses",
            "title": "Mini Courses",
            "description": "Structured lessons for deeper learning",
            "content": list(MINI_COURSES.keys()),
        },
    }
    module = modules.get(module_id)
    if not module: return None
    
    module = module.copy()
    if lang != "en":
        title_trans = get_translation(lang, f"learn_module_{module_id}_title")
        if title_trans: module["title"] = title_trans[0]
        
        desc_trans = get_translation(lang, f"learn_module_{module_id}_desc")
        if desc_trans: module["description"] = desc_trans[0]
        
    return module


def get_lesson(course_id: str, lesson_number: int, lang: str = "en") -> Dict:
    """Get a specific lesson from a mini course."""
    course = get_mini_course(course_id, lang)
    if not course:
        return None
    
    lessons = course.get("lessons", [])
    if lesson_number < 1 or lesson_number > len(lessons):
        return None
    
    lesson = lessons[lesson_number - 1].copy()
    
    if lang != "en":
        l_title_trans = get_translation(lang, f"learn_lesson_{course_id}_{lesson_number}_title")
        if l_title_trans: lesson["title"] = l_title_trans[0]
        
        l_content_trans = get_translation(lang, f"learn_lesson_{course_id}_{lesson_number}_content")
        if l_content_trans: lesson["content"] = l_content_trans[0]
    
    return {
        "course_id": course_id,
        "course_title": course["title"],
        "lesson_number": lesson_number,
        "total_lessons": len(lessons),
        **lesson,
    }


def search_learning_content(query: str, lang: str = "en") -> List[Dict]:
    """Search across all learning content."""
    results = []
    query_lower = query.lower()
    
    # Search moon signs
    for sign, data in MOON_SIGNS.items():
        if query_lower in sign.lower() or query_lower in data.get("short_desc", "").lower():
            info = get_moon_sign_lesson(sign, lang)
            results.append({
                "type": "moon_sign",
                "key": sign,
                "title": info["title"],
                "preview": info["short_desc"],
            })
    
    # Search rising signs
    for sign, data in RISING_SIGNS.items():
        if query_lower in sign.lower() or query_lower in data.get("first_impression", "").lower():
            info = get_rising_sign_lesson(sign, lang)
            results.append({
                "type": "rising_sign",
                "key": sign,
                "title": info["title"],
                "preview": info["first_impression"],
            })
    
    # Search elements
    for element, data in ELEMENTS.items():
        if query_lower in element.lower() or query_lower in data.get("description", "").lower():
            info = get_element_lesson(element, lang)
            results.append({
                "type": "element",
                "key": element,
                "title": f"{element} Element",
                "preview": ", ".join(data.get("keywords", [])),
            })
    
    # Search retrogrades
    for planet, data in RETROGRADE_GUIDE.items():
        if query_lower in planet.lower() or query_lower in data.get("what_it_means", "").lower():
            info = get_retrograde_guide(planet, lang)
            results.append({
                "type": "retrograde",
                "key": planet,
                "title": f"{planet} Retrograde",
                "preview": info.get("frequency", ""),
            })
    
    # Search courses
    for course_id, data in MINI_COURSES.items():
        if query_lower in data.get("title", "").lower():
            info = get_mini_course(course_id, lang)
            results.append({
                "type": "course",
                "key": course_id,
                "title": info["title"],
                "preview": f"{len(data.get('lessons', []))} lessons",
            })
    
    return results[:10]  # Limit to 10 results
