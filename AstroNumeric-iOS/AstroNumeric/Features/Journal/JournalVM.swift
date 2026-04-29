// JournalVM.swift
// Journal ViewModel, local store, and response models
// Extracted from JournalView.swift for maintainability

import SwiftUI

// MARK: - View Model

@Observable
final class JournalVM {
    var readings: [JournalReading] = []
    var prompts: [String] = []
    var isLoading = false
    var error: String?
    private(set) var isLocalMode: Bool = true
    
    private let api = APIClient.shared
    private let localStore = LocalJournalStore.shared
    private var currentProfileId: Int?
    
    @MainActor
    func load(profile: Profile?, isAuthenticated: Bool, forceRefresh: Bool = false) async {
        guard let profile else { return }
        currentProfileId = profile.id
        isLoading = true
        defer { isLoading = false }
        
        isLocalMode = AppConfig.personalMode || !isAuthenticated || profile.id <= 0
        if isLocalMode {
            readings = localStore.list(profileId: profile.id).map { mapLocalEntry($0) }
        } else {
            do {
                let cachePolicy: CachePolicy = forceRefresh ? .networkFirst : .cacheFirst
                let readingsResponse: V2ApiResponse<JournalReadingsResponse> = try await api.fetch(
                    .journalReadings(profileId: profile.id),
                    cachePolicy: cachePolicy
                )
                readings = readingsResponse.data.readings
            } catch {
                self.error = error.localizedDescription
            }
        }
        
        do {
            let promptsResponse: V2ApiResponse<JournalPromptsResponse> = try await api.fetch(.journalPrompts)
            prompts = promptsResponse.data.prompts
        } catch {
            // Prompts are optional
        }
    }
    
    @MainActor
    func saveEntry(readingId: Int, entry: String) async {
        if isLocalMode, let profileId = currentProfileId {
            let existing = localStore.list(profileId: profileId).first(where: { $0.id == readingId })
            localStore.upsert(profileId: profileId, id: readingId, entry: entry, outcome: existing?.outcome)
            readings = localStore.list(profileId: profileId).map { mapLocalEntry($0) }
            // Re-index for semantic search
            Task { await JournalEmbedder.shared.rebuildIndex(profileId: profileId) }
            return
        }
        do {
            let _: V2ApiResponse<JournalEntryResponse> = try await api.fetch(
                .journalEntry(body: JournalEntryRequest(readingId: readingId, entry: entry))
            )
        } catch {
            self.error = error.localizedDescription
        }
    }
    
    @MainActor
    func saveOutcome(readingId: Int, outcome: JournalOutcome) async {
        if isLocalMode, let profileId = currentProfileId {
            let existing = localStore.list(profileId: profileId).first(where: { $0.id == readingId })
            localStore.upsert(profileId: profileId, id: readingId, entry: existing?.entry ?? "", outcome: outcome.rawValue)
            readings = localStore.list(profileId: profileId).map { mapLocalEntry($0) }
            return
        }
        do {
            let _: V2ApiResponse<JournalOutcomeResponse> = try await api.fetch(
                .journalOutcome(body: JournalOutcomeRequest(readingId: readingId, outcome: outcome.rawValue, notes: nil))
            )
        } catch {
            self.error = error.localizedDescription
        }
    }
    
    func makeLocalDraft(profileId: Int) -> JournalReading {
        let id = localStore.nextId(profileId: profileId)
        return JournalReading(
            id: id,
            scope: "local",
            scopeLabel: "Journal Entry",
            date: nil,
            formattedDate: format(date: Date()),
            hasJournal: false,
            journalPreview: nil,
            journalFull: nil,
            feedback: nil,
            feedbackEmoji: nil,
            contentSummary: nil
        )
    }
    
    private func mapLocalEntry(_ e: LocalJournalEntry) -> JournalReading {
        let trimmed = e.entry.trimmingCharacters(in: .whitespacesAndNewlines)
        let preview = trimmed.isEmpty ? nil : String(trimmed.prefix(160))
        
        return JournalReading(
            id: e.id,
            scope: "local",
            scopeLabel: "Journal Entry",
            date: iso(date: e.createdAt),
            formattedDate: format(date: e.createdAt),
            hasJournal: !trimmed.isEmpty,
            journalPreview: preview,
            journalFull: trimmed,
            feedback: e.outcome,
            feedbackEmoji: outcomeEmoji(e.outcome),
            contentSummary: nil
        )
    }
    
    private func outcomeEmoji(_ value: String?) -> String? {
        switch JournalOutcome.from(value) {
        case .yes: return "✅"
        case .no: return "❌"
        case .partial: return "🔶"
        case .neutral: return "➖"
        }
    }
    
    private func iso(date: Date) -> String {
        ISO8601DateFormatter().string(from: date)
    }
    
    private func format(date: Date) -> String {
        let f = DateFormatter()
        f.dateStyle = .medium
        f.timeStyle = .short
        return f.string(from: date)
    }
}

// MARK: - Local Journal (Personal Mode)

struct LocalJournalEntry: Codable, Identifiable, Hashable {
    let id: Int
    let profileId: Int
    var createdAt: Date
    var updatedAt: Date
    var entry: String
    var outcome: String? // yes|no|partial|neutral
}

final class LocalJournalStore {
    static let shared = LocalJournalStore()
    private init() {}
    
    private let encoder: JSONEncoder = {
        let e = JSONEncoder()
        e.dateEncodingStrategy = .iso8601
        return e
    }()
    
    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .iso8601
        return d
    }()
    
    private func key(profileId: Int) -> String {
        "astromeric.local_journal.v1.profile.\(profileId)"
    }
    
    func list(profileId: Int) -> [LocalJournalEntry] {
        guard let data = UserDefaults.standard.data(forKey: key(profileId: profileId)),
              let entries = try? decoder.decode([LocalJournalEntry].self, from: data) else {
            return []
        }
        return entries.sorted(by: { $0.createdAt > $1.createdAt })
    }
    
    func nextId(profileId: Int) -> Int {
        let entries = list(profileId: profileId)
        return (entries.map(\.id).max() ?? 0) + 1
    }
    
    func upsert(profileId: Int, id: Int, entry: String, outcome: String?) {
        var entries = list(profileId: profileId)
        let now = Date()
        
        if let idx = entries.firstIndex(where: { $0.id == id }) {
            entries[idx].entry = entry
            entries[idx].outcome = outcome
            entries[idx].updatedAt = now
        } else {
            entries.append(
                LocalJournalEntry(
                    id: id,
                    profileId: profileId,
                    createdAt: now,
                    updatedAt: now,
                    entry: entry,
                    outcome: outcome
                )
            )
        }
        
        entries.sort(by: { $0.createdAt > $1.createdAt })
        if let data = try? encoder.encode(entries) {
            UserDefaults.standard.set(data, forKey: key(profileId: profileId))
        }
    }
}

// MARK: - Response Models

struct JournalReadingsResponse: Codable {
    let profileId: Int
    let total: Int
    let limit: Int
    let offset: Int
    let readings: [JournalReading]
    
    enum CodingKeys: String, CodingKey {
        case profileId = "profile_id"
        case total, limit, offset, readings
    }
}

struct JournalReading: Codable, Identifiable {
    let id: Int
    let scope: String?
    let scopeLabel: String?
    let date: String?
    let formattedDate: String?
    let hasJournal: Bool?
    let journalPreview: String?
    let journalFull: String?
    let feedback: String?
    let feedbackEmoji: String?
    let contentSummary: String?
    
    enum CodingKeys: String, CodingKey {
        case id, scope, date
        case scopeLabel = "scope_label"
        case formattedDate = "formatted_date"
        case hasJournal = "has_journal"
        case journalPreview = "journal_preview"
        case journalFull = "journal_full"
        case feedback
        case feedbackEmoji = "feedback_emoji"
        case contentSummary = "content_summary"
    }
}

struct JournalPromptsResponse: Codable {
    let scope: String
    let prompts: [String]
}

struct JournalEntryResponse: Codable {
    let message: String
    let entry: JournalEntryData
}

struct JournalEntryData: Codable {
    let readingId: Int
    let entry: String
    let timestamp: String
    let wordCount: Int
    let characterCount: Int
    
    enum CodingKeys: String, CodingKey {
        case readingId = "reading_id"
        case entry, timestamp
        case wordCount = "word_count"
        case characterCount = "character_count"
    }
}

struct JournalOutcomeResponse: Codable {
    let message: String
    let outcome: JournalOutcomeData
}

struct JournalOutcomeData: Codable {
    let readingId: Int
    let outcome: String
    let outcomeEmoji: String
    let categories: [String]
    let notes: String
    let recordedAt: String
    
    enum CodingKeys: String, CodingKey {
        case readingId = "reading_id"
        case outcome
        case outcomeEmoji = "outcome_emoji"
        case categories, notes
        case recordedAt = "recorded_at"
    }
}

enum JournalOutcome: String, CaseIterable {
    case yes
    case no
    case partial
    case neutral
    
    var label: String {
        switch self {
        case .yes: return "✅ Yes"
        case .no: return "❌ No"
        case .partial: return "🔶 Partial"
        case .neutral: return "➖ Neutral"
        }
    }
    
    static func from(_ value: String?) -> JournalOutcome {
        guard let value else { return .neutral }
        return JournalOutcome(rawValue: value) ?? .neutral
    }
}
