// AIModels.swift
// AI chat and explanation models

import Foundation

// MARK: - Chat Message Role

enum ChatMessageRole: String, Codable {
    case user
    case assistant
    case system
}

// MARK: - Chat

struct ChatMessage: Codable, Identifiable {
    let id: String
    let role: ChatMessageRole
    let content: String
    let timestamp: Date?
    
    init(id: String = UUID().uuidString, role: ChatMessageRole, content: String, timestamp: Date? = nil) {
        self.id = id
        self.role = role
        self.content = content
        self.timestamp = timestamp
    }
}

struct ChatContext: Codable {
    let sunSign: String?
    let moonSign: String?
    let risingSign: String?
    let birthTimeAssumed: Bool?
    let timeConfidence: String?
    let history: [ChatMessage]?

    enum CodingKeys: String, CodingKey {
        case sunSign = "sun_sign"
        case moonSign = "moon_sign"
        case risingSign = "rising_sign"
        case birthTimeAssumed = "birth_time_assumed"
        case timeConfidence = "time_confidence"
        case history
    }
}

struct ChatRequest: Encodable {
    let message: String
    let history: [ChatMessage]?
    let profile: ProfilePayload?
    let context: ChatContext?
}

struct ChatResponse: Codable {
    let response: String
    let message: String?
    let model: String?
    let tokensUsed: Int?
    
    enum CodingKeys: String, CodingKey {
        case response, message, model
        case tokensUsed = "tokens_used"
    }
}

// MARK: - V2 Cosmic Guide Chat

struct V2CosmicGuideChatRequest: Encodable {
    let message: String
    let sunSign: String?
    let moonSign: String?
    let risingSign: String?
    let birthTimeAssumed: Bool?
    let timeConfidence: String?
    let history: [ChatMessage]?
    let systemPrompt: String?
    let tone: String?

    enum CodingKeys: String, CodingKey {
        case message
        case sunSign = "sun_sign"
        case moonSign = "moon_sign"
        case risingSign = "rising_sign"
        case birthTimeAssumed = "birth_time_assumed"
        case timeConfidence = "time_confidence"
        case history
        case systemPrompt = "system_prompt"
        case tone
    }
}

// MARK: - Guide Tone

enum GuideTone: String, CaseIterable, Identifiable {
    case gentle = "gentle"
    case balanced = "balanced"
    case direct = "direct"
    case roast = "roast"
    
    var id: String { rawValue }
    
    var label: String {
        switch self {
        case .gentle: return "Gentle"
        case .balanced: return "Balanced"
        case .direct: return "Direct"
        case .roast: return "Roast"
        }
    }
    
    var emoji: String {
        switch self {
        case .gentle: return "🌸"
        case .balanced: return "⚖️"
        case .direct: return "🎯"
        case .roast: return "🔥"
        }
    }
    
    var prompt: String {
        switch self {
        case .gentle:
            return "Speak with warmth and compassion. Be encouraging and supportive. Soften harsh aspects."
        case .balanced:
            return "Be informative and balanced. Mix encouragement with honest observations."
        case .direct:
            return "Be blunt and straightforward. No sugar-coating. Give it to me straight."
        case .roast:
            return "Roast me based on my chart. Be savage but astrologically accurate. Make it funny."
        }
    }
}

// MARK: - AI Explain

struct AIExplainRequest: Encodable {
    let scope: String?
    let headline: String?
    let theme: String?
    let sections: [SectionSummary]?
    let numerologySummary: String?
    let simpleLanguage: Bool
    
    init(scope: String?, headline: String?, theme: String?, sections: [SectionSummary]?, numerologySummary: String?, simpleLanguage: Bool = true) {
        self.scope = scope
        self.headline = headline
        self.theme = theme
        self.sections = sections
        self.numerologySummary = numerologySummary
        self.simpleLanguage = simpleLanguage
    }
    
    enum CodingKeys: String, CodingKey {
        case scope, headline, theme, sections
        case numerologySummary = "numerology_summary"
        case simpleLanguage = "simple_language"
    }
}

struct SectionSummary: Encodable {
    let title: String
    let highlights: [String]?
}

struct AIExplainResponse: Codable {
    let summary: String
}
