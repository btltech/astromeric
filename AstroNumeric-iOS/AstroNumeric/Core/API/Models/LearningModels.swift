// LearningModels.swift
// Learning, glossary, and educational content models

import Foundation

// MARK: - Lessons

struct Lesson: Codable, Identifiable {
    let id: String
    let title: String
    let category: String
    let content: String
    let order: Int?
}

struct GlossaryTerm: Codable, Identifiable {
    let id: String
    let term: String
    let definition: String
    let category: String?
}

// MARK: - Learning Modules

struct LearningModule: Codable, Identifiable {
    let id: String
    let title: String
    let description: String
    let category: String
    let difficulty: String
    let durationMinutes: Int
    let content: String
    let keywords: [String]
    let relatedModules: [String]?
    
    enum CodingKeys: String, CodingKey {
        case id, title, description, category, difficulty, content, keywords
        case durationMinutes = "duration_minutes"
        case relatedModules = "related_modules"
    }
    
    var formattedDuration: String {
        "\(durationMinutes) min"
    }
    
    var icon: String {
        switch category.lowercased() {
        case "astrology": return "sparkles"
        case "numerology": return "number.circle"
        case "tarot": return "rectangle.stack"
        case "zodiac": return "sun.max"
        default: return "book"
        }
    }
}

struct PaginatedLearningModules: Codable {
    let data: [LearningModule]
    let page: Int
    let pageSize: Int
    let total: Int
    let pages: Int
    
    enum CodingKeys: String, CodingKey {
        case data, page, total, pages
        case pageSize = "page_size"
    }
}

// MARK: - Zodiac Guidance

struct ZodiacGuidanceResult: Codable {
    let sign: String
    let dateRange: String
    let element: String
    let rulingPlanet: String
    let characteristics: [String]
    let compatibility: [String: Double]
    let guidance: String
    
    enum CodingKeys: String, CodingKey {
        case sign, element, characteristics, compatibility, guidance
        case dateRange = "date_range"
        case rulingPlanet = "ruling_planet"
    }
}

// MARK: - Glossary

struct GlossaryEntry: Codable, Identifiable {
    var id: String { term }
    let term: String
    let definition: String
    let category: String
    let usageExample: String
    let relatedTerms: [String]?
    
    enum CodingKeys: String, CodingKey {
        case term, definition, category
        case usageExample = "usage_example"
        case relatedTerms = "related_terms"
    }
}

struct PaginatedGlossaryEntries: Codable {
    let data: [GlossaryEntry]
    let page: Int
    let pageSize: Int
    let total: Int
    let pages: Int

    enum CodingKeys: String, CodingKey {
        case data, page, total, pages
        case pageSize = "page_size"
    }
}
