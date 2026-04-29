// ZodiacSign.swift
// Client-side zodiac sign derivation and birthstone data.
// No API call needed — all data is static and deterministic from date of birth.

import Foundation

// MARK: - Birthstone Info

struct BirthstoneInfo {
    let name: String
    let emoji: String
    let meaning: String
    let howToUse: String
}

// MARK: - Zodiac Sign

enum ZodiacSign: String, CaseIterable {
    case aries, taurus, gemini, cancer, leo, virgo
    case libra, scorpio, sagittarius, capricorn, aquarius, pisces

    // MARK: Display

    var displayName: String { rawValue.capitalized }

    var emoji: String {
        switch self {
        case .aries: return "♈️"
        case .taurus: return "♉️"
        case .gemini: return "♊️"
        case .cancer: return "♋️"
        case .leo: return "♌️"
        case .virgo: return "♍️"
        case .libra: return "♎️"
        case .scorpio: return "♏️"
        case .sagittarius: return "♐️"
        case .capricorn: return "♑️"
        case .aquarius: return "♒️"
        case .pisces: return "♓️"
        }
    }

    var element: String {
        switch self {
        case .aries, .leo, .sagittarius: return "Fire 🔥"
        case .taurus, .virgo, .capricorn: return "Earth 🌿"
        case .gemini, .libra, .aquarius: return "Air 💨"
        case .cancer, .scorpio, .pisces: return "Water 💧"
        }
    }

    var modality: String {
        switch self {
        case .aries, .cancer, .libra, .capricorn: return "Cardinal"
        case .taurus, .leo, .scorpio, .aquarius: return "Fixed"
        case .gemini, .virgo, .sagittarius, .pisces: return "Mutable"
        }
    }

    // MARK: Birthstones

    var birthstones: [BirthstoneInfo] {
        switch self {
        case .aries:
            return [
                BirthstoneInfo(name: "Diamond", emoji: "💎", meaning: "Clarity and invincibility — amplifies Aries courage and willpower.", howToUse: "Wear or carry diamond when taking bold action or starting something new."),
                BirthstoneInfo(name: "Bloodstone", emoji: "🟢", meaning: "Grounds fiery Aries energy and promotes courage without recklessness.", howToUse: "Hold bloodstone during stressful moments to stay grounded and decisive."),
                BirthstoneInfo(name: "Jasper", emoji: "🔴", meaning: "A nurturing stone that promotes patience and stamina — balancing Aries impulsivity.", howToUse: "Keep jasper nearby during long projects to sustain motivation.")
            ]
        case .taurus:
            return [
                BirthstoneInfo(name: "Emerald", emoji: "💚", meaning: "Stone of prosperity and loyalty — resonates deeply with Taurus' love of abundance.", howToUse: "Wear emerald to attract stability and strengthen bonds in relationships."),
                BirthstoneInfo(name: "Rose Quartz", emoji: "🌸", meaning: "Opens the heart to self-love and harmony — softens Taurus stubbornness with compassion.", howToUse: "Place rose quartz in your bedroom or carry it to invite warmth into relationships."),
                BirthstoneInfo(name: "Malachite", emoji: "🌿", meaning: "Transformation stone that helps Taurus release what no longer serves them.", howToUse: "Meditate with malachite when you're resisting necessary change.")
            ]
        case .gemini:
            return [
                BirthstoneInfo(name: "Agate", emoji: "🔵", meaning: "Brings mental clarity and helps Gemini articulate thoughts with precision.", howToUse: "Hold agate before important conversations or presentations."),
                BirthstoneInfo(name: "Citrine", emoji: "🌟", meaning: "Sunny and uplifting — enhances Gemini's natural wit and optimism.", howToUse: "Keep citrine on your desk to spark creativity and clear mental fog."),
                BirthstoneInfo(name: "Tiger's Eye", emoji: "🐯", meaning: "Grounds scattered Gemini energy into focused, practical action.", howToUse: "Carry tiger's eye when you need to follow through on ideas.")
            ]
        case .cancer:
            return [
                BirthstoneInfo(name: "Ruby", emoji: "🔴", meaning: "A stone of passion and confidence. Helps Cancer step forward boldly and say what they truly feel.", howToUse: "Wear or visualize ruby when trying new things or having courageous conversations."),
                BirthstoneInfo(name: "Moonstone", emoji: "🌙", meaning: "Enhances intuition and emotional balance — Cancer's natural domain. Supports deep reflection.", howToUse: "Carry moonstone when feelings deepen or when navigating emotional complexity."),
                BirthstoneInfo(name: "Pearl", emoji: "🤍", meaning: "A calming gemstone that soothes stress and promotes inner harmony and emotional resilience.", howToUse: "Wear pearl jewelry or place a pearl under your pillow to calm emotional turbulence.")
            ]
        case .leo:
            return [
                BirthstoneInfo(name: "Peridot", emoji: "💛", meaning: "Awakens Leo's warmth and generosity, while dispelling jealousy and resentment.", howToUse: "Wear peridot to radiate positive energy and attract loyal people."),
                BirthstoneInfo(name: "Carnelian", emoji: "🟠", meaning: "Fuels Leo's creative fire and boldness — a stone of action and self-expression.", howToUse: "Hold carnelian before performing, presenting, or creating anything artistic."),
                BirthstoneInfo(name: "Amber", emoji: "🟡", meaning: "Warm and sunny like Leo — promotes vitality, self-confidence, and joy.", howToUse: "Keep amber nearby to maintain high energy and enthusiasm throughout the day.")
            ]
        case .virgo:
            return [
                BirthstoneInfo(name: "Sapphire", emoji: "💙", meaning: "Stone of wisdom and clarity — sharpens Virgo's analytical mind.", howToUse: "Wear sapphire when tackling complex problems or making important decisions."),
                BirthstoneInfo(name: "Amazonite", emoji: "🩵", meaning: "Soothes Virgo's tendency toward worry and self-criticism with calm clarity.", howToUse: "Hold amazonite when overthinking, or keep it on your desk as a reminder to be kind to yourself."),
                BirthstoneInfo(name: "Moss Agate", emoji: "🍃", meaning: "Connects Virgo to nature's rhythms and promotes stability and healing.", howToUse: "Keep moss agate near plants or in your workspace to foster calm productivity.")
            ]
        case .libra:
            return [
                BirthstoneInfo(name: "Opal", emoji: "🌈", meaning: "Stone of inspiration and creativity — magnifies Libra's love of beauty and harmony.", howToUse: "Wear opal when seeking creative inspiration or artistic breakthroughs."),
                BirthstoneInfo(name: "Lapis Lazuli", emoji: "🔵", meaning: "Promotes honest communication and inner truth — helps Libra speak up decisively.", howToUse: "Hold lapis lazuli when you need to voice your opinion or make a difficult decision."),
                BirthstoneInfo(name: "Rose Quartz", emoji: "🌸", meaning: "Enhances Libra's deep need for connection and harmonious relationships.", howToUse: "Place rose quartz in shared spaces to nurture loving, balanced energy.")
            ]
        case .scorpio:
            return [
                BirthstoneInfo(name: "Topaz", emoji: "🟤", meaning: "Amplifies Scorpio's intensity and psychic perception — a stone of manifestation.", howToUse: "Meditate with topaz when setting intentions or working through transformation."),
                BirthstoneInfo(name: "Obsidian", emoji: "⚫️", meaning: "Powerful protective stone — shields Scorpio from psychic drain and negative energy.", howToUse: "Keep obsidian near your entryway or carry it as a shield in draining environments."),
                BirthstoneInfo(name: "Malachite", emoji: "🌿", meaning: "Accelerates Scorpio's natural transformation and releases deep emotional patterns.", howToUse: "Use malachite in journaling or shadow work practices.")
            ]
        case .sagittarius:
            return [
                BirthstoneInfo(name: "Turquoise", emoji: "🩵", meaning: "Stone of travel and wisdom — perfectly aligned with Sagittarius' adventurous spirit.", howToUse: "Wear turquoise when traveling or seeking new wisdom and experiences."),
                BirthstoneInfo(name: "Tanzanite", emoji: "💜", meaning: "Deepens Sagittarius' spiritual awareness and visionary thinking.", howToUse: "Meditate with tanzanite to connect to higher purpose and spiritual insight."),
                BirthstoneInfo(name: "Citrine", emoji: "🌟", meaning: "Amplifies optimism and attracts abundance — Sagittarius at their best.", howToUse: "Keep citrine in your wallet or space to attract luck and opportunities.")
            ]
        case .capricorn:
            return [
                BirthstoneInfo(name: "Garnet", emoji: "❤️", meaning: "Stone of commitment and perseverance — fuels Capricorn's drive toward long-term goals.", howToUse: "Wear garnet when starting an ambitious project or needing sustained motivation."),
                BirthstoneInfo(name: "Onyx", emoji: "⚫️", meaning: "Strengthens Capricorn's discipline and resilience, especially during hardship.", howToUse: "Carry onyx during stressful periods to maintain strength and focus."),
                BirthstoneInfo(name: "Smoky Quartz", emoji: "🤎", meaning: "Grounds ambition into practical steps — prevents Capricorn from burning out.", howToUse: "Keep smoky quartz in your workspace to stay grounded and realistic.")
            ]
        case .aquarius:
            return [
                BirthstoneInfo(name: "Amethyst", emoji: "💜", meaning: "Heightens Aquarius' intuition and visionary thinking — a stone of spiritual insight.", howToUse: "Meditate with amethyst when working on innovative ideas or future planning."),
                BirthstoneInfo(name: "Aquamarine", emoji: "🩵", meaning: "Aligns with Aquarius' humanitarian spirit — promotes clear, compassionate communication.", howToUse: "Wear aquamarine when speaking for a cause or facilitating group conversations."),
                BirthstoneInfo(name: "Labradorite", emoji: "🔮", meaning: "Stone of magic and transformation — awakens Aquarius' genius and originality.", howToUse: "Keep labradorite nearby during creative or inventive work.")
            ]
        case .pisces:
            return [
                BirthstoneInfo(name: "Aquamarine", emoji: "🩵", meaning: "Supports Pisces' empathic nature and emotional clarity — like the ocean depths.", howToUse: "Wear aquamarine to stay emotionally clear and avoid absorbing others' energies."),
                BirthstoneInfo(name: "Amethyst", emoji: "💜", meaning: "Amplifies Pisces' spiritual intuition and protects against psychic overwhelm.", howToUse: "Place amethyst near your bed to enhance intuitive dreams and restful sleep."),
                BirthstoneInfo(name: "Fluorite", emoji: "💚", meaning: "Brings mental clarity and focus to dreamy Pisces — organizes creative visions.", howToUse: "Keep fluorite on your desk when you need to translate inspiration into action.")
            ]
        }
    }

    // MARK: - Derivation from Date of Birth

    static func from(dateOfBirth: String) -> ZodiacSign? {
        // dateOfBirth is "yyyy-MM-dd"
        let parts = dateOfBirth.split(separator: "-")
        guard parts.count >= 2,
              let month = Int(parts[1]),
              let day = Int(parts[2]) else { return nil }
        return from(month: month, day: day)
    }

    static func from(month: Int, day: Int) -> ZodiacSign? {
        switch (month, day) {
        case (3, 21...), (4, 1...19): return .aries
        case (4, 20...), (5, 1...20): return .taurus
        case (5, 21...), (6, 1...20): return .gemini
        case (6, 21...), (7, 1...22): return .cancer
        case (7, 23...), (8, 1...22): return .leo
        case (8, 23...), (9, 1...22): return .virgo
        case (9, 23...), (10, 1...22): return .libra
        case (10, 23...), (11, 1...21): return .scorpio
        case (11, 22...), (12, 1...21): return .sagittarius
        case (12, 22...), (1, 1...19): return .capricorn
        case (1, 20...), (2, 1...18): return .aquarius
        case (2, 19...), (3, 1...20): return .pisces
        default: return nil
        }
    }

    // MARK: - Monthly Lucky Numbers

    /// Numerology-based lucky numbers for a given birth day + calendar month.
    /// Uses pythagorean reduction: birth day + current month reduced to single digit, then spread.
    static func monthlyLuckyNumbers(dateOfBirth: String, month: Int, year: Int) -> [Int] {
        let parts = dateOfBirth.split(separator: "-")
        guard parts.count == 3,
              let birthDay = Int(parts[2]),
              let birthMonth = Int(parts[1]) else {
            return [3, 6, 9, 12, 21]
        }

        // Personal month number (standard numerology)
        let lifePathBase = reduce(birthDay) + reduce(birthMonth)
        let personalMonth = reduce(lifePathBase + reduce(month))

        // Generate 5 distinct lucky numbers from the personal month seed
        var numbers: [Int] = []
        numbers.append(personalMonth)
        numbers.append(reduce(personalMonth + reduce(year % 100)) + birthDay % 10)
        numbers.append(personalMonth * 3)
        numbers.append(birthDay)
        numbers.append(reduce(birthDay + month))

        // Normalize: keep in 1–99 range and deduplicate
        var seen = Set<Int>()
        return numbers
            .map { max(1, abs($0) % 99 == 0 ? 9 : abs($0) % 99) }
            .filter { seen.insert($0).inserted }
    }

    private static func reduce(_ n: Int) -> Int {
        guard n > 9 else { return n }
        let sum = String(n).compactMap { $0.wholeNumberValue }.reduce(0, +)
        return reduce(sum)
    }
}
