// LearnVM.swift
// ViewModel for learning content - serves the lessons bundled in the app

import SwiftUI
import Observation

@Observable
final class LearnVM {
    // MARK: - State
    
    var modules: [LearningModule] = []
    var selectedCategory: String = "astrology"
    
    // MARK: - Actions
    
    @MainActor
    func fetchModules() async {
        // Lessons are static, long-form reference content bundled in the app.
        // Render ONLY the local content so the full lessons always show — never
        // overwritten by thin/stale server data or a cache.
        modules = fallbackModules(for: selectedCategory)
        HapticManager.impact(.light)
    }
    
    @MainActor
    func switchCategory(_ category: String) {
        selectedCategory = category
        Task {
            await fetchModules()
        }
    }
    
    // MARK: - Fallback Content
    
    private func fallbackModules(for category: String) -> [LearningModule] {
        switch category.lowercased() {
        case "astrology":
            return [
                LearningModule(
                    id: "astro-1",
                    title: "What is Astrology?",
                    description: "Understanding the cosmic language",
                    category: "astrology",
                    difficulty: "beginner",
                    durationMinutes: 5,
                    content: "Astrology is the study of how the positions of the Sun, Moon, planets, and stars correspond to personality, events, and timing here on Earth. It is not about the stars 'controlling' you — it is a symbolic language for describing patterns in character, relationships, and timing.\n\nThe core idea is simple: the sky at the moment you were born forms a map. Where each planet sat, which zodiac sign it occupied, and the angles the planets made to one another all become symbols an astrologer reads together, like words in a sentence.\n\nNearly every culture — Babylonian, Egyptian, Greek, Indian, Chinese, Mayan — built its own astrology, because watching the sky was humanity's first calendar and compass. Western astrology, which this app uses, traces back to Hellenistic Greece and organizes the sky into twelve signs and twelve houses.\n\nHold two things at once: astrology is a tool for self-reflection, not fortune-telling, and its value comes from how thoughtfully you apply it. Treat each placement as a tendency to explore, not a fixed fate. The next lessons break the map into its pieces — the birth chart, the planets, the signs, and the houses — so you can start reading it yourself.",
                    keywords: ["astrology", "basics", "introduction"],
                    relatedModules: ["astro-2", "astro-3"]
                ),
                LearningModule(
                    id: "astro-2",
                    title: "The Birth Chart",
                    description: "Your cosmic blueprint",
                    category: "astrology",
                    difficulty: "beginner",
                    durationMinutes: 8,
                    content: "Your birth chart (or natal chart) is a 360-degree snapshot of the sky at the exact date, time, and place you were born. It is the foundation of everything in astrology — every reading, forecast, and compatibility report starts here.\n\nThink of the chart as four layers that work together:\n• Signs describe style — the 'how'. There are twelve, from Aries to Pisces.\n• Planets describe what — the functions of the psyche, like identity (Sun), emotion (Moon), or drive (Mars).\n• Houses describe where — the twelve areas of life a planet shows up in, from self and money to career and relationships.\n• Aspects describe relationships — the angles between planets that show where energies cooperate or clash.\n\nMeaning comes from combining these. 'Mars in Aries in the 10th house' reads as: drive (Mars), expressed boldly and directly (Aries), focused on career and public life (10th house).\n\nAccuracy matters. Your Sun sign needs only your birth date, but your Moon sign, rising sign, and houses need your exact birth time and place — even a few hours' difference can change them. Without a birth time the chart still works for sign-level insight; it just can't place the houses precisely.\n\nDon't try to absorb everything at once. Start with your 'big three' — Sun, Moon, and Rising — then add one planet at a time.",
                    keywords: ["birth chart", "natal chart", "blueprint"],
                    relatedModules: ["astro-1", "astro-3"]
                ),
                LearningModule(
                    id: "astro-3",
                    title: "Planets & Their Meanings",
                    description: "Celestial influences",
                    category: "astrology",
                    difficulty: "intermediate",
                    durationMinutes: 10,
                    content: "In astrology each planet represents a different function of the personality — a distinct voice inside you. Reading a chart gets far easier once each planet keeps a clear job.\n\nThe personal planets shape day-to-day character:\n• Sun — your core identity, ego, and what energizes you.\n• Moon — your emotions, instincts, and what makes you feel safe.\n• Mercury — how you think, learn, and communicate.\n• Venus — how you love, what you value, and your sense of beauty.\n• Mars — your drive, anger, and how you take action.\n\nThe social planets describe how you grow and connect to the wider world:\n• Jupiter — expansion, luck, beliefs, and where you seek meaning.\n• Saturn — discipline, limits, responsibility, and hard-won lessons.\n\nThe outer planets move slowly and color whole generations:\n• Uranus — change, rebellion, and sudden insight.\n• Neptune — dreams, intuition, spirituality, and illusion.\n• Pluto — power, transformation, and deep renewal.\n\nTo interpret any planet, combine three things: the planet (what), its sign (how it expresses), and its house (where it plays out). For example, Venus (love) in Capricorn (cautious, committed) in the 7th house (partnership) suggests someone who takes relationships seriously and is loyal once committed.\n\nStart with the Sun, Moon, and Mercury — identity, feeling, and mind — and you'll already understand most of what drives someone.",
                    keywords: ["planets", "meanings", "celestial"],
                    relatedModules: ["astro-2", "astro-4"]
                ),
                LearningModule(
                    id: "astro-4",
                    title: "Houses in Astrology",
                    description: "Life areas and experiences",
                    category: "astrology",
                    difficulty: "intermediate",
                    durationMinutes: 12,
                    content: "If signs are 'how' and planets are 'what', the twelve houses are 'where' — the areas of life where a planet's energy actually shows up. The houses are set by the horizon and your birth time, which is why an accurate time matters so much.\n\nHere is the quick tour:\n• 1st — self, body, first impressions, how you start things.\n• 2nd — money, possessions, values, self-worth.\n• 3rd — communication, siblings, learning, short trips.\n• 4th — home, family, roots, your private world.\n• 5th — creativity, romance, play, children.\n• 6th — work, health, daily routines, service.\n• 7th — partnerships, marriage, close one-to-one relationships.\n• 8th — intimacy, shared resources, transformation, the taboo.\n• 9th — travel, higher education, philosophy, belief.\n• 10th — career, reputation, public role, ambition.\n• 11th — friends, groups, hopes, networks.\n• 12th — the unconscious, solitude, spirituality, what's hidden.\n\nA planet 'lights up' the house it sits in. Several planets in one house show where much of your energy concentrates; an empty house simply means that area runs quietly in the background — it isn't a problem.\n\nTo read a placement, ask: which planet, in which sign, in which house? 'Moon (emotion) in Cancer (nurturing) in the 4th house (home)' points to someone deeply tied to family and a sense of belonging.",
                    keywords: ["houses", "life areas", "domains"],
                    relatedModules: ["astro-3"]
                )
            ]
        case "numerology":
            return [
                LearningModule(
                    id: "num-1",
                    title: "Introduction to Numerology",
                    description: "The power of numbers",
                    category: "numerology",
                    difficulty: "beginner",
                    durationMinutes: 5,
                    content: "Numerology is the study of the meaning behind numbers and how they relate to your character and timing. Like astrology, it is a symbolic system: each number from 1 to 9 carries a distinct personality, plus the 'master numbers' 11, 22, and 33.\n\nThe practice has roots in Pythagorean Greece, where it was taught that numbers are the building blocks of reality. Modern Western numerology turns your name and birth date into a small set of core numbers that describe who you are and the cycles you move through.\n\nThe headline numbers are:\n• Life Path — from your birth date; your overall direction and life lessons (the most important number).\n• Expression / Destiny — from the letters of your full birth name; your natural talents.\n• Soul Urge — from the vowels in your name; your inner desires and motivations.\n• Personality — from the consonants; how others first experience you.\n\nNumbers are reduced by adding their digits until you reach a single digit (or a master number). Numerology shines as a practical tool: pair your core numbers with your current cycle (the Personal Year) and you get a simple read on what to focus on now. The next lessons cover the Life Path and the yearly cycles.",
                    keywords: ["numerology", "numbers", "introduction"],
                    relatedModules: ["num-2"]
                ),
                LearningModule(
                    id: "num-2",
                    title: "Your Life Path Number",
                    description: "Your soul's purpose",
                    category: "numerology",
                    difficulty: "beginner",
                    durationMinutes: 7,
                    content: "The Life Path is the single most important number in numerology. Calculated from your full birth date, it describes your main direction in life — the themes, strengths, and lessons that repeat for you across the years.\n\nYou find it by reducing your birth date to a single digit (keeping 11, 22, and 33 as master numbers). Each result has a clear flavor:\n• 1 — the Leader: independence, initiative, drive.\n• 2 — the Diplomat: partnership, sensitivity, balance.\n• 3 — the Communicator: creativity, expression, joy.\n• 4 — the Builder: structure, discipline, stability.\n• 5 — the Explorer: freedom, change, adventure.\n• 6 — the Nurturer: responsibility, care, harmony.\n• 7 — the Seeker: analysis, intuition, depth.\n• 8 — the Powerhouse: ambition, authority, abundance.\n• 9 — the Humanitarian: compassion, completion, wisdom.\n• 11 / 22 / 33 — master numbers: heightened intuition (11), large-scale building (22), compassionate teaching (33).\n\nYour Life Path isn't a limit — it's the lens through which your choices play out. A '5' will keep meeting themes of freedom and change; the growth is in handling that energy wisely rather than restlessly.\n\nLife Path is most useful paired with your Personal Year (next lesson), which tells you when its themes are most active.",
                    keywords: ["life path", "purpose", "destiny"],
                    relatedModules: ["num-1", "num-3"]
                ),
                LearningModule(
                    id: "num-3",
                    title: "Personal Year Cycles",
                    description: "Annual energy themes",
                    category: "numerology",
                    difficulty: "intermediate",
                    durationMinutes: 8,
                    content: "Numerology describes not just who you are but when — and the Personal Year is the most practical timing tool. Your life moves through repeating nine-year cycles, and each year within the cycle carries a distinct theme.\n\nYou calculate it by adding your birth month and day to the current year, then reducing to a single digit. The nine years tend to flow like this:\n• Year 1 — fresh starts, new projects, planting seeds.\n• Year 2 — patience, partnerships, slow development.\n• Year 3 — creativity, socializing, self-expression.\n• Year 4 — hard work, structure, laying foundations.\n• Year 5 — change, freedom, the unexpected.\n• Year 6 — home, family, responsibility, relationships.\n• Year 7 — reflection, study, rest, inner growth.\n• Year 8 — ambition, money, recognition, power.\n• Year 9 — completion, release, letting go to make room.\n\nThe skill is to work with the year rather than against it. A Year 1 rewards bold beginnings; a Year 9 rewards finishing and releasing — pushing to start something brand-new in a 9 often feels like swimming upstream.\n\nTreat the cycle as a posture, then test it against what's actually happening in your life. Combined with your Life Path, it turns numerology into a simple, usable planning lens.",
                    keywords: ["cycles", "personal year", "themes"],
                    relatedModules: ["num-2"]
                )
            ]
        case "zodiac":
            return [
                LearningModule(
                    id: "zodiac-1",
                    title: "The 12 Signs",
                    description: "Overview of the zodiac",
                    category: "zodiac",
                    difficulty: "beginner",
                    durationMinutes: 10,
                    content: "The twelve zodiac signs are the 'styles' of astrology — twelve distinct ways energy expresses itself. Every planet in a chart wears the costume of the sign it occupies.\n\nEach sign blends an element and a modality. The four elements describe temperament: Fire (passion, action), Earth (practicality, stability), Air (intellect, connection), and Water (emotion, intuition). The three modalities describe approach: Cardinal signs initiate, Fixed signs sustain, Mutable signs adapt.\n\nIn order:\n• Aries — bold initiator (Fire, Cardinal).\n• Taurus — steady builder (Earth, Fixed).\n• Gemini — curious connector (Air, Mutable).\n• Cancer — nurturing protector (Water, Cardinal).\n• Leo — radiant performer (Fire, Fixed).\n• Virgo — careful improver (Earth, Mutable).\n• Libra — harmonizing diplomat (Air, Cardinal).\n• Scorpio — intense investigator (Water, Fixed).\n• Sagittarius — adventurous seeker (Fire, Mutable).\n• Capricorn — disciplined achiever (Earth, Cardinal).\n• Aquarius — original reformer (Air, Fixed).\n• Pisces — compassionate dreamer (Water, Mutable).\n\nSigns are styles, not whole identities — you are not 'just' your Sun sign. A full chart mixes many signs across its planets. Knowing the element and modality of a sign is often enough to grasp how it behaves.",
                    keywords: ["zodiac", "signs", "overview"],
                    relatedModules: ["zodiac-2"]
                ),
                LearningModule(
                    id: "zodiac-2",
                    title: "Sun, Moon & Rising",
                    description: "Your cosmic trinity",
                    category: "zodiac",
                    difficulty: "intermediate",
                    durationMinutes: 8,
                    content: "Before diving into a whole chart, learn your 'big three': Sun, Moon, and Rising sign. Together they give a fast, surprisingly complete sketch of a person.\n\n• Sun sign — your core identity, ego, and what lights you up. It's the sign most people know, set by your birth date. It answers 'who am I at my center?'\n• Moon sign — your emotional nature, instincts, and what you need to feel safe. More private than the Sun and often only visible to those close to you; it needs your birth date and, ideally, time.\n• Rising sign (Ascendant) — the sign that was rising on the eastern horizon at your birth. It shapes your first impression and your instinctive approach to life, and it needs an accurate birth time.\n\nA helpful metaphor: the Rising is the book cover, the Sun is the main character, and the Moon is the inner emotional world revealed as you read on.\n\nWhen two people seem to embody their sign very differently, the big three usually explain why. A Capricorn Sun with a Leo Rising and Pisces Moon is a very different person from a Capricorn with Virgo Rising and Scorpio Moon. Start here before adding the other planets.",
                    keywords: ["sun", "moon", "rising", "trinity"],
                    relatedModules: ["zodiac-1", "zodiac-3"]
                ),
                LearningModule(
                    id: "zodiac-3",
                    title: "Sign Compatibility",
                    description: "Cosmic connections",
                    category: "zodiac",
                    difficulty: "intermediate",
                    durationMinutes: 10,
                    content: "Sign compatibility is a quick way to sense how two people might mesh — useful as a first scan, not a final verdict. Real compatibility lives in the full charts (synastry), but signs give a fast, intuitive starting point.\n\nThe most reliable shortcut is elements:\n• Same element (e.g., two Fire signs) — easy, instinctive understanding, but can lack contrast.\n• Complementary elements — Fire + Air feed each other (air fuels fire); Earth + Water nourish each other (water shapes earth).\n• Challenging mixes — Fire + Water or Earth + Air can clash without effort, but also balance each other beautifully when both make room for difference.\n\nModality matters too: two Cardinal signs may both want to lead; two Fixed signs may both refuse to budge; two Mutable signs may both struggle to commit.\n\nUse sign compatibility to notice the texture of a connection — where it flows and where it needs patience. But never write off a pairing on Sun signs alone. Two 'incompatible' Suns can be deeply bonded once you look at their Moons, Venus, Mars, and the angles between their charts. Signs open the conversation; the full chart finishes it.",
                    keywords: ["compatibility", "relationships", "harmony"],
                    relatedModules: ["zodiac-2"]
                )
            ]
        case "elements":
            return [
                LearningModule(
                    id: "elem-1",
                    title: "Fire Signs",
                    description: "Aries, Leo, Sagittarius",
                    category: "elements",
                    difficulty: "beginner",
                    durationMinutes: 6,
                    content: "Fire signs — Aries, Leo, and Sagittarius — are the zodiac's spark. They move by desire, courage, and momentum, bringing warmth, enthusiasm, and a sense of possibility wherever they go.\n\nFire is the element of spirit and action. These signs tend to act first and reflect later, lead rather than follow, and inspire others with their confidence. At their best they're brave, generous, and motivating; under stress they can be impatient, blunt, or burn out by overcommitting.\n\nEach Fire sign expresses the flame differently:\n• Aries (Cardinal Fire) — the spark of initiation: direct, competitive, pioneering. Aries starts things.\n• Leo (Fixed Fire) — the steady flame: warm, proud, creative, loyal. Leo sustains and radiates.\n• Sagittarius (Mutable Fire) — the wandering flame: optimistic, philosophical, freedom-loving. Sagittarius expands and explores.\n\nIf you have strong Fire in your chart, you likely need movement, challenge, and room to express yourself; routine and micromanagement drain you. The growth edge for Fire is patience — pairing that natural drive with follow-through and sensitivity to others. Fire works beautifully with Air (which fuels it) and is balanced by Earth and Water.",
                    keywords: ["fire", "aries", "leo", "sagittarius"],
                    relatedModules: ["elem-2", "elem-3", "elem-4"]
                ),
                LearningModule(
                    id: "elem-2",
                    title: "Earth Signs",
                    description: "Taurus, Virgo, Capricorn",
                    category: "elements",
                    difficulty: "beginner",
                    durationMinutes: 6,
                    content: "Earth signs — Taurus, Virgo, and Capricorn — are the zodiac's foundation. Grounded, practical, and reliable, they turn ideas into tangible results and value stability, security, and things that last.\n\nEarth is the element of the material world: the body, money, work, and nature. These signs trust what they can see, touch, and build. At their best they're dependable, patient, and productive; under stress they can become rigid, overly cautious, or stuck in materialism.\n\nEach Earth sign builds differently:\n• Taurus (Fixed Earth) — patient and sensual: values comfort, loyalty, and steady progress. Taurus sustains.\n• Virgo (Mutable Earth) — precise and improving: analytical, helpful, detail-oriented. Virgo refines.\n• Capricorn (Cardinal Earth) — ambitious and structured: disciplined, strategic, built for the long climb. Capricorn achieves.\n\nIf Earth is strong in your chart, you likely crave security and tangible accomplishment, and you're the person others rely on to get things done. The growth edge for Earth is flexibility — staying open to change and to feelings, not just facts and plans. Earth pairs naturally with Water (which nourishes it) and is energized by Fire and Air.",
                    keywords: ["earth", "taurus", "virgo", "capricorn"],
                    relatedModules: ["elem-1", "elem-3", "elem-4"]
                ),
                LearningModule(
                    id: "elem-3",
                    title: "Air Signs",
                    description: "Gemini, Libra, Aquarius",
                    category: "elements",
                    difficulty: "beginner",
                    durationMinutes: 6,
                    content: "Air signs — Gemini, Libra, and Aquarius — are the zodiac's thinkers and connectors. They live in the realm of ideas, language, and relationships, thriving on conversation, perspective, and mental stimulation.\n\nAir is the element of the mind. These signs gather information, weigh options, and connect people and concepts. At their best they're communicative, fair-minded, and socially gifted; under stress they can overthink, detach from their emotions, or struggle to decide.\n\nEach Air sign moves differently:\n• Gemini (Mutable Air) — curious and quick: versatile, talkative, endlessly interested. Gemini connects ideas.\n• Libra (Cardinal Air) — balanced and relational: diplomatic, aesthetic, partnership-focused. Libra harmonizes.\n• Aquarius (Fixed Air) — original and principled: inventive, independent, future-minded. Aquarius reforms.\n\nIf Air is strong in your chart, you likely need conversation, variety, and intellectual freedom, and you process life by talking and thinking it through. The growth edge for Air is grounding — landing all those ideas in the body and the heart, not just the head. Air feeds Fire and is balanced by Earth and Water.",
                    keywords: ["air", "gemini", "libra", "aquarius"],
                    relatedModules: ["elem-1", "elem-2", "elem-4"]
                ),
                LearningModule(
                    id: "elem-4",
                    title: "Water Signs",
                    description: "Cancer, Scorpio, Pisces",
                    category: "elements",
                    difficulty: "beginner",
                    durationMinutes: 6,
                    content: "Water signs — Cancer, Scorpio, and Pisces — are the zodiac's emotional depth. Intuitive, sensitive, and deeply feeling, they navigate life through emotion and connection rather than logic alone.\n\nWater is the element of feeling and the unconscious. These signs absorb the moods around them, form deep bonds, and often sense things before they can explain them. At their best they're empathic, nurturing, and creative; under stress they can become moody, over-absorbent of others' pain, or escapist.\n\nEach Water sign flows differently:\n• Cancer (Cardinal Water) — nurturing and protective: caring, home-loving, emotionally intelligent. Cancer shelters.\n• Scorpio (Fixed Water) — intense and transformative: passionate, loyal, unafraid of depth. Scorpio investigates.\n• Pisces (Mutable Water) — compassionate and imaginative: dreamy, artistic, spiritually attuned. Pisces dissolves boundaries.\n\nIf Water is strong in your chart, you likely feel everything deeply and need emotional safety, creative outlets, and time to retreat and recharge. The growth edge for Water is boundaries — staying open without absorbing everyone else's storms. Water nourishes Earth and is balanced by Fire and Air.",
                    keywords: ["water", "cancer", "scorpio", "pisces"],
                    relatedModules: ["elem-1", "elem-2", "elem-3"]
                )
            ]
        default:
            return []
        }
    }
    
    // MARK: - Categories
    
    var categories: [(id: String, title: String, icon: String)] {
        [
            ("astrology", "Astrology", "sparkles"),
            ("numerology", "Numerology", "number.circle"),
            ("zodiac", "Zodiac", "sun.max"),
            ("elements", "Elements", "leaf.fill")
        ]
    }
}
