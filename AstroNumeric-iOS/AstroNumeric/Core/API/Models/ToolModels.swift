// ToolModels.swift
// Tool feature models (Timing, Habits, Moon, Tarot, Oracle, Affirmation, etc.)

import Foundation

// MARK: - Timing

struct TimingRequest: Encodable {
    let activity: String
    let profile: ProfilePayload?
    let latitude: Double
    let longitude: Double
    let tz: String
    
    init(activity: String, profile: Profile?) {
        self.activity = activity
        self.latitude = profile?.latitude ?? 40.7128
        self.longitude = profile?.longitude ?? -74.006
        self.tz = profile?.timezone ?? "UTC"
        
        self.profile = profile.map { p in
            p.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        }
    }
}

struct TimingProfileData: Encodable {
    let name: String
    let dateOfBirth: String
    let timeOfBirth: String
    let location: LocationData
    
    enum CodingKeys: String, CodingKey {
        case name
        case dateOfBirth = "date_of_birth"
        case timeOfBirth = "time_of_birth"
        case location
    }
}

// MARK: - Best Days

struct BestDaysRequest: Encodable {
    let activity: String
    let daysAhead: Int
    
    enum CodingKeys: String, CodingKey {
        case activity
        case daysAhead = "days_ahead"
    }
}

// MARK: - Habits

struct CreateHabitRequest: Encodable {
    let name: String
    let category: String
    let frequency: String
    let targetCount: Int?
    let description: String?
    
    init(name: String, category: String, frequency: String, targetCount: Int? = nil, description: String? = nil) {
        self.name = name
        self.category = category
        self.frequency = frequency
        self.targetCount = targetCount
        self.description = description
    }
    
    enum CodingKeys: String, CodingKey {
        case name
        case category
        case frequency
        case targetCount = "target_count"
        case description
    }
}

struct HabitLogRequest: Encodable {
    let habitId: Int
    let completed: Bool
    let note: String?
    
    enum CodingKeys: String, CodingKey {
        case habitId = "habit_id"
        case completed
        case note
    }
}

struct HabitCategory: Codable, Identifiable {
    let id: String
    let name: String
    let emoji: String
    let description: String?
    let bestPhases: [String]
    
    enum CodingKeys: String, CodingKey {
        case id, name, emoji, description
        case bestPhases = "best_phases"
    }
}

struct Habit: Codable, Identifiable {
    let id: Int
    let name: String
    let category: String
    let frequency: String
    let targetCount: Int?
    let description: String?
    let createdAt: String?
    let isActive: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, name, category, frequency, description
        case targetCount = "target_count"
        case createdAt = "created_at"
        case isActive = "is_active"
    }
}

struct HabitCompletion: Codable {
    let habitId: Int
    let completedAt: String
    let date: String
    let weekday: String
    let moonPhase: String?
    
    enum CodingKeys: String, CodingKey {
        case habitId = "habit_id"
        case completedAt = "completed_at"
        case date, weekday
        case moonPhase = "moon_phase"
    }
}

// MARK: - Moon

struct MoonData: Codable {
    let phaseName: String?
    let illumination: Double?
    let emoji: String?
    let daysUntilNextPhase: Double?
    let isWaxing: Bool?
    let isWaning: Bool?
    
    enum CodingKeys: String, CodingKey {
        case phaseName = "phase_name"
        case illumination, emoji
        case daysUntilNextPhase = "days_until_next_phase"
        case isWaxing = "is_waxing"
        case isWaning = "is_waning"
    }
}

struct MoonPhaseData: Codable {
    let phaseName: String
    let emoji: String
    let guidance: String?
    let illumination: Double?
    let daysUntilNextPhase: Double?
    
    enum CodingKeys: String, CodingKey {
        case phaseName = "phase_name"
        case emoji, guidance, illumination
        case daysUntilNextPhase = "days_until_next_phase"
    }
}

struct MoonRitualRequest: Encodable {
    let profile: ProfilePayload?
}

// MARK: - Tarot

struct TarotCard: Codable {
    let name: String
    let suit: String
    let number: Int
    let upright: Bool
    let meaning: String
    let interpretation: String
}

struct TarotRequest: Encodable {
    let profile: ProfilePayload
}

// MARK: - Yes/No Oracle

struct YesNoAnswer: Codable {
    let question: String
    let answer: String
    let confidence: Double
    let reasoning: String
    let guidance: [String]
}

struct YesNoRequest: Encodable {
    let question: String
    let profile: ProfilePayload
}

// MARK: - Daily Affirmation

struct AffirmationResponse: Codable {
    let affirmation: String
}

struct AffirmationRequest: Encodable {
    let profile: ProfilePayload?
}

// MARK: - Cosmic Guide

struct CosmicGuidanceRequest: Encodable {
    let topic: String
    let profile: ProfilePayload?
    let context: String?
}

struct CosmicInterpretRequest: Encodable {
    let chartData: String?
    let readingData: String?
    let question: String?
    
    enum CodingKeys: String, CodingKey {
        case chartData = "chart_data"
        case readingData = "reading_data"
        case question
    }
}

// MARK: - Feedback

struct SectionFeedbackRequest: Encodable {
    let section: String
    let rating: Int
    let comment: String?
    let profileId: Int?
    
    enum CodingKeys: String, CodingKey {
        case section, rating, comment
        case profileId = "profile_id"
    }
}
