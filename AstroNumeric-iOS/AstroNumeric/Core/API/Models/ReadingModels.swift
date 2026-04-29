// ReadingModels.swift
// Daily/weekly/monthly reading and forecast models

import Foundation

// MARK: - Reading Scope

enum ReadingScope: String, CaseIterable, Codable {
    case daily
    case weekly
    case monthly
    
    var displayName: String {
        rawValue.capitalized
    }
}

// MARK: - Forecast Requests

struct ForecastRequest: Encodable {
    let profileId: Int
    let scope: String
    
    enum CodingKeys: String, CodingKey {
        case profileId = "profile_id"
        case scope
    }
}

struct ReadingRequest: Encodable {
    let name: String
    let dateOfBirth: String
    let timeOfBirth: String?
    let placeOfBirth: String?
    let latitude: Double?
    let longitude: Double?
    let timezone: String?
    let scope: String
    
    enum CodingKeys: String, CodingKey {
        case name
        case dateOfBirth = "date_of_birth"
        case timeOfBirth = "time_of_birth"
        case placeOfBirth = "place_of_birth"
        case latitude
        case longitude
        case timezone
        case scope
    }
}

/// Request for v2 forecasts using full profile data (for session/guest profiles)
struct V2ForecastRequest: Encodable {
    let profile: ProfilePayload
    let scope: String
    let date: String?
    let includeDetails: Bool
    let tone: String
    
    enum CodingKeys: String, CodingKey {
        case profile
        case scope
        case date
        case includeDetails = "include_details"
        case tone
    }
    
    init(profile: Profile, scope: String, date: String? = nil) {
        self.profile = profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        self.scope = scope
        self.date = date
        self.includeDetails = true
        self.tone = AppStore.shared.readingTone.rawValue
    }
}

/// Request for v2 forecasts using saved profile ID
struct ForecastByIdRequest: Encodable {
    let profileId: Int
    let scope: String
    let date: String?
    let includeDetails: Bool
    
    enum CodingKeys: String, CodingKey {
        case profileId = "profile_id"
        case scope
        case date
        case includeDetails = "include_details"
    }
    
    init(profileId: Int, scope: String, date: String? = nil) {
        self.profileId = profileId
        self.scope = scope
        self.date = date
        self.includeDetails = true
    }
}

// MARK: - Prediction/Forecast Data

struct PredictionData: Codable {
    let profile: ProfilePayload?
    let scope: String
    let date: String
    let sections: [ForecastSection]
    let overallScore: Float
    let generatedAt: String
    
    enum CodingKeys: String, CodingKey {
        case profile
        case scope
        case date
        case sections
        case overallScore = "overall_score"
        case generatedAt = "generated_at"
    }
}

struct ForecastSection: Codable, Identifiable {
    var id: String { title }
    let title: String
    let summary: String
    let topics: [String: Float]
    let avoid: [String]
    let embrace: [String]
}

struct ReadingSummary: Codable {
    let headline: String?
    let topFactors: [TopFactor]?
    
    enum CodingKeys: String, CodingKey {
        case headline
        case topFactors = "top_factors"
    }
}

struct TopFactor: Codable {
    let aspect: String?
    let impact: String?
    let description: String?
}

struct ReadingSection: Codable, Identifiable {
    var id: String { title }
    let title: String
    let icon: String?
    let highlights: [String]?
    let text: String?
}

// MARK: - Daily Guidance

struct DailyGuidance: Codable {
    let luckyNumbers: [Int]?
    let luckyColor: String?
    let affirmation: String?
    let advice: String?
    let moonPhase: String?
    let moonSign: String?
    let power: Int?
    
    enum CodingKeys: String, CodingKey {
        case luckyNumbers = "lucky_numbers"
        case luckyColor = "lucky_color"
        case affirmation
        case advice
        case moonPhase = "moon_phase"
        case moonSign = "moon_sign"
        case power
    }
}

// MARK: - Weekly Forecast

struct ForecastDay: Codable, Identifiable {
    var id: String { date }
    let date: String
    let score: Int
    let vibe: String
    let icon: String
    let recommendation: String

    private var canonicalDateString: String {
        String(date.prefix(10))
    }

    var weekday: String {
        guard let dateObj = dateObject else { return "" }
        let formatter = DateFormatter()
        formatter.dateFormat = "EEE"
        return formatter.string(from: dateObj)
    }
    
    var dayNumber: Int {
        guard let components = dateComponents else { return 0 }
        return components.day ?? 0
    }

    var dateObject: Date? {
        guard let components = dateComponents else { return nil }
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = .current
        var localComponents = DateComponents()
        localComponents.year = components.year
        localComponents.month = components.month
        localComponents.day = components.day
        // Use noon to keep the civil day stable across time zones.
        localComponents.hour = 12
        return calendar.date(from: localComponents)
    }

    var isToday: Bool {
        guard let dateObj = dateObject else { return false }
        return Calendar.current.isDateInToday(dateObj)
    }
    
    var scoreColor: String {
        if score >= 80 { return "gold" }
        if score >= 60 { return "purple" }
        return "red"
    }

    private var dateComponents: DateComponents? {
        let parts = canonicalDateString.split(separator: "-")
        guard parts.count == 3,
              let year = Int(parts[0]),
              let month = Int(parts[1]),
              let day = Int(parts[2]) else {
            return nil
        }

        var components = DateComponents()
        components.year = year
        components.month = month
        components.day = day
        return components
    }
}

struct WeeklyForecastResponse: Codable {
    let days: [ForecastDay]
}

// MARK: - Year Ahead

struct YearAheadRequest: Encodable {
    let profile: ProfilePayload
    let year: Int?
}
