// JournalModels.swift
// Journal entry and reflection models

import Foundation

// MARK: - Journal Requests

struct JournalEntryRequest: Encodable {
    let readingId: Int
    let entry: String
    
    enum CodingKeys: String, CodingKey {
        case readingId = "reading_id"
        case entry
    }
}

struct JournalReportRequest: Encodable {
    let profileId: Int
    let period: String
    
    enum CodingKeys: String, CodingKey {
        case profileId = "profile_id"
        case period
    }
}

struct JournalOutcomeRequest: Encodable {
    let readingId: Int
    let outcome: String
    let notes: String?
    
    enum CodingKeys: String, CodingKey {
        case readingId = "reading_id"
        case outcome
        case notes
    }
}
