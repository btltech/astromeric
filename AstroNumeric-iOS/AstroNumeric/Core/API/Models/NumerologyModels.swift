// NumerologyModels.swift
// Numerology calculation and analysis models

import Foundation

// MARK: - Numerology Requests

struct NumerologyRequest: Encodable {
    let name: String
    let dateOfBirth: String
    
    enum CodingKeys: String, CodingKey {
        case name
        case dateOfBirth = "date_of_birth"
    }
}

struct NameAnalysisRequest: Encodable {
    let name: String
}

/// Request for v2 numerology analysis
struct V2NumerologyRequest: Encodable {
    let profile: ProfilePayload
    let language: String
    let method: String  // 'pythagorean' or 'chaldean'

    enum CodingKeys: String, CodingKey {
        case profile
        case language
        case method
    }

    init(profile: Profile, method: String = "pythagorean") {
        self.profile = profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        self.language = "en"
        self.method = method
    }

    init(name: String, dateOfBirth: String, method: String = "pythagorean") {
        self.profile = ProfilePayload(
            name: name,
            dateOfBirth: dateOfBirth,
            timeOfBirth: nil,
            latitude: nil,
            longitude: nil,
            timezone: nil
        )
        self.language = "en"
        self.method = method
    }
}

/// Request for numerology compatibility
struct NumerologyCompatibilityRequest: Encodable {
    let profile: ProfilePayload
    let personB: ProfilePayload
    let language: String
    
    enum CodingKeys: String, CodingKey {
        case profile
        case personB = "person_b"
        case language
    }
    
    init(profile1: Profile, profile2: Profile) {
        let hideSensitive = AppStore.shared.hideSensitiveDetailsEnabled
        self.profile = profile1.privacySafePayload(hideSensitive: hideSensitive)
        self.personB = profile2.privacySafePayload(hideSensitive: hideSensitive)
        self.language = "en"
    }
}

// MARK: - Numerology Data

struct NumerologyData: Codable {
    let profile: ProfilePayload?
    let lifePath: LifePathData?
    let destinyNumber: Int?
    let destinyInterpretation: String?
    let personalYear: PersonalYearData?
    let compatibilityNumber: Int?
    let compatibilityInterpretation: String?
    let luckyNumbers: [Int]?
    let auspiciousDays: [Int]?
    let numerologyInsights: [String: String]?
    let pinnacles: [Pinnacle]?
    let challenges: [Challenge]?
    let karmicDebts: [KarmicDebt]?
    let synthesis: NumerologySynthesis?
    let generatedAt: String?
    
    enum CodingKeys: String, CodingKey {
        case profile
        case lifePath = "life_path"
        case destinyNumber = "destiny_number"
        case destinyInterpretation = "destiny_interpretation"
        case personalYear = "personal_year"
        case compatibilityNumber = "compatibility_number"
        case compatibilityInterpretation = "compatibility_interpretation"
        case luckyNumbers = "lucky_numbers"
        case auspiciousDays = "auspicious_days"
        case numerologyInsights = "numerology_insights"
        case pinnacles
        case challenges
        case karmicDebts = "karmic_debts"
        case synthesis
        case generatedAt = "generated_at"
    }
    
    // Computed properties for UI compatibility
    var coreNumbers: CoreNumbers? {
        guard let lp = lifePath else { return nil }
        let profileName = profile?.name ?? ""
        
        let expressionDetail: NumberDetail? = destinyNumber.map {
            NumberDetail(number: $0, meaning: destinyInterpretation, keywords: nil)
        }
        
        let soulUrgeDetail: NumberDetail? = numerologyInsights?["soul_urge"].map {
            NumberDetail(number: Self.soulUrgeNumber(for: profileName), meaning: $0, keywords: nil)
        }
        
        let personalityDetail: NumberDetail? = numerologyInsights?["personality"].map {
            NumberDetail(number: Self.personalityNumber(for: profileName), meaning: $0, keywords: nil)
        }
        
        return CoreNumbers(
            lifePath: NumberDetail(number: lp.number, meaning: lp.meaning, keywords: lp.traits),
            expression: expressionDetail,
            soulUrge: soulUrgeDetail,
            personality: personalityDetail,
            birthday: nil
        )
    }
    
    var cycles: NumerologyCycles? {
        guard let py = personalYear else { return nil }

        let personalMonthNumber = numerologyInsights?["personal_month"].map { _ in
            Self.personalMonthNumber(personalYear: py.cycleNumber)
        }
        let personalDayNumber = numerologyInsights?["personal_day"].map { _ in
            Self.personalDayNumber(personalMonth: personalMonthNumber ?? 0)
        }
        
        let monthDetail: CycleDetail? = numerologyInsights?["personal_month"].map {
            CycleDetail(number: personalMonthNumber ?? 0, meaning: $0)
        }
        
        let dayDetail: CycleDetail? = numerologyInsights?["personal_day"].map {
            CycleDetail(number: personalDayNumber ?? 0, meaning: $0)
        }
        
        return NumerologyCycles(
            personalYear: CycleDetail(number: py.cycleNumber, meaning: py.interpretation),
            personalMonth: monthDetail,
            personalDay: dayDetail
        )
    }
    
    // MARK: - Local fallback calculations (match backend v2 rules)

    private static let pythagoreanLetterValues: [UInt32: Int] = [
        97: 1, 98: 2, 99: 3, 100: 4, 101: 5, 102: 6, 103: 7, 104: 8, 105: 9, // a-i
        106: 1, 107: 2, 108: 3, 109: 4, 110: 5, 111: 6, 112: 7, 113: 8, 114: 9, // j-r
        115: 1, 116: 2, 117: 3, 118: 4, 119: 5, 120: 6, 121: 7, 122: 8, // s-z
    ]

    private static let vowels: Set<UInt32> = [97, 101, 105, 111, 117] // a, e, i, o, u
    private static let masterNumbers: Set<Int> = [11, 22, 33]

    private static func reduceNumber(_ num: Int, keepMaster: Bool = true) -> Int {
        var current = num
        let masters: Set<Int> = keepMaster ? masterNumbers : []
        while current > 9, !masters.contains(current) {
            current = String(current).compactMap { Int(String($0)) }.reduce(0, +)
        }
        return current
    }

    private static func soulUrgeNumber(for name: String) -> Int {
        let lowercased = name.lowercased()
        var total = 0
        for scalar in lowercased.unicodeScalars {
            guard vowels.contains(scalar.value),
                  let value = pythagoreanLetterValues[scalar.value] else { continue }
            total += value
        }
        return reduceNumber(total, keepMaster: true)
    }

    private static func personalityNumber(for name: String) -> Int {
        let lowercased = name.lowercased()
        var total = 0
        for scalar in lowercased.unicodeScalars {
            guard let value = pythagoreanLetterValues[scalar.value],
                  !vowels.contains(scalar.value) else { continue }
            total += value
        }
        return reduceNumber(total, keepMaster: true)
    }

    private static func personalMonthNumber(personalYear: Int) -> Int {
        let utcCalendar = Calendar(identifier: .gregorian)
        var calendar = utcCalendar
        calendar.timeZone = TimeZone(secondsFromGMT: 0) ?? (TimeZone(abbreviation: "UTC") ?? TimeZone.current)

        let month = calendar.component(.month, from: Date())
        return reduceNumber(personalYear + month, keepMaster: false)
    }

    private static func personalDayNumber(personalMonth: Int) -> Int {
        let utcCalendar = Calendar(identifier: .gregorian)
        var calendar = utcCalendar
        calendar.timeZone = TimeZone(secondsFromGMT: 0) ?? (TimeZone(abbreviation: "UTC") ?? TimeZone.current)

        let day = calendar.component(.day, from: Date())
        return reduceNumber(personalMonth + day, keepMaster: false)
    }
}

struct LifePathData: Codable {
    let number: Int
    let meaning: String?
    let traits: [String]?
    let lifePurpose: String?
    
    enum CodingKeys: String, CodingKey {
        case number, meaning, traits
        case lifePurpose = "life_purpose"
    }
}

struct PersonalYearData: Codable {
    let year: Int
    let cycleNumber: Int
    let interpretation: String?
    let focusAreas: [String]?
    
    enum CodingKeys: String, CodingKey {
        case year
        case cycleNumber = "cycle_number"
        case interpretation
        case focusAreas = "focus_areas"
    }
}

struct CoreNumbers: Codable {
    let lifePath: NumberDetail?
    let expression: NumberDetail?
    let soulUrge: NumberDetail?
    let personality: NumberDetail?
    let birthday: NumberDetail?
    
    enum CodingKeys: String, CodingKey {
        case lifePath = "life_path"
        case expression
        case soulUrge = "soul_urge"
        case personality
        case birthday
    }
}

struct NumberDetail: Codable {
    let number: Int
    let meaning: String?
    let keywords: [String]?
}

struct NumerologyCycles: Codable {
    let personalYear: CycleDetail?
    let personalMonth: CycleDetail?
    let personalDay: CycleDetail?
    
    enum CodingKeys: String, CodingKey {
        case personalYear = "personal_year"
        case personalMonth = "personal_month"
        case personalDay = "personal_day"
    }
}

struct CycleDetail: Codable {
    let number: Int
    let meaning: String?
}

struct Pinnacle: Codable, Identifiable {
    var id: Int { number }
    let number: Int
    let ages: String?
    let meaning: String?
}

struct Challenge: Codable, Identifiable {
    var id: Int { number }
    let number: Int
    let ages: String?
    let meaning: String?
}

struct KarmicDebt: Codable, Identifiable {
    var id: Int { raw }
    /// Pre-reduction number that triggered the karmic debt (13, 14, 16, or 19)
    let raw: Int
    /// Which core numbers carry this debt (e.g. ["life_path", "soul_urge"])
    let sources: [String]
    /// Short label e.g. "Karmic Debt 13/4"
    let label: String
    /// One-line theme e.g. "Laziness redeemed through discipline"
    let theme: String
    /// Full description of the karmic lesson
    let description: String
}

struct NumerologySynthesis: Codable {
    let summary: String
    let strengths: [String]
    let growthEdges: [String]
    let currentFocus: String
    let affirmation: String
    let dominantNumbers: [NumerologyHighlight]

    enum CodingKeys: String, CodingKey {
        case summary
        case strengths
        case growthEdges = "growth_edges"
        case currentFocus = "current_focus"
        case affirmation
        case dominantNumbers = "dominant_numbers"
    }
}

struct NumerologyHighlight: Codable, Identifiable {
    var id: String { key }
    let key: String
    let label: String
    let number: Int
    let meaning: String
}
