// CompatibilityModels.swift
// Compatibility and relationship models

import Foundation

// MARK: - Compatibility Requests

struct CompatibilityRequest: Encodable {
    let personA: ProfilePayload
    let personB: ProfilePayload
    let relationshipType: String
    
    init(personA: Profile, personB: Profile, relationshipType: String = "romantic") {
        let hideSensitive = AppStore.shared.hideSensitiveDetailsEnabled
        self.personA = personA.privacySafePayload(hideSensitive: hideSensitive)
        self.personB = personB.privacySafePayload(hideSensitive: hideSensitive)
        self.relationshipType = relationshipType
    }
    
    enum CodingKeys: String, CodingKey {
        case personA = "person_a"
        case personB = "person_b"
        case relationshipType = "relationship_type"
    }
}

struct RomanticCompatibilityRequest: Encodable {
    let personA: ProfilePayload
    let personB: ProfilePayload
    
    init(personA: Profile, personB: ProfilePayload) {
        self.personA = personA.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        self.personB = personB
    }
    
    enum CodingKeys: String, CodingKey {
        case personA = "person_a"
        case personB = "person_b"
    }
}

struct FriendshipCompatibilityRequest: Encodable {
    let personA: ProfilePayload
    let personB: ProfilePayload
    
    init(personA: Profile, personB: ProfilePayload) {
        self.personA = personA.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        self.personB = personB
    }
    
    enum CodingKeys: String, CodingKey {
        case personA = "person_a"
        case personB = "person_b"
    }
}

// MARK: - Compatibility Results

struct DataConfidence: Codable {
    let score: Double
    let note: String?
}

struct CompatibilityResult: Codable {
    // Legacy fields
    let score: Int?
    let rating: String?
    let summary: String?
    let topics: [CompatibilityTopic]?
    
    // V2 API fields
    let overallScore: Double?
    let dimensions: [CompatibilityDimension]?
    let strengths: [String]?
    let challenges: [String]?
    let recommendations: [String]?
    let personA: CompatibilityPerson?
    let personB: CompatibilityPerson?
    let generatedAt: String?
    let dataConfidence: DataConfidence?
    
    enum CodingKeys: String, CodingKey {
        case score, rating, summary, topics, dimensions, strengths, challenges, recommendations
        case overallScore = "overall_score"
        case personA = "person_a"
        case personB = "person_b"
        case generatedAt = "generated_at"
        case dataConfidence = "data_confidence"
    }
    
    var displayScore: Double {
        overallScore ?? Double(score ?? 0)
    }
    
    var categories: [CompatibilityCategory] {
        dimensions?.map { CompatibilityCategory(name: $0.name, score: $0.score, description: $0.insight) } ?? []
    }
    
    var advice: [String] {
        (recommendations ?? []) + (strengths ?? [])
    }
}

struct CompatibilityTopic: Codable, Identifiable {
    var id: String { name }
    let name: String
    let score: Int
    let description: String?
}

struct CompatibilityDimension: Codable {
    let name: String
    let score: Double
    let interpretation: String?
    
    var insight: String? { interpretation }
    
    enum CodingKeys: String, CodingKey {
        case name, score, interpretation
    }
}

struct CompatibilityPerson: Codable {
    let name: String
}

struct CompatibilityCategory: Codable {
    let name: String
    let score: Double
    let description: String?
}

// MARK: - Relationship Models

struct RelationshipTimelineRequest: Encodable {
    let sunSign: String
    let partnerSign: String?
    let monthsAhead: Int
    
    enum CodingKeys: String, CodingKey {
        case sunSign = "sun_sign"
        case partnerSign = "partner_sign"
        case monthsAhead = "months_ahead"
    }
}

struct RelationshipTimingRequest: Encodable {
    let sunSign: String
    let partnerSign: String?
    let date: String?
    
    enum CodingKeys: String, CodingKey {
        case sunSign = "sun_sign"
        case partnerSign = "partner_sign"
        case date
    }
}
