// JournalVM.swift
// Journal ViewModel and response models
// Local persistence + remote API access live behind JournalRepository.

import SwiftUI

// MARK: - View Model

@Observable
@MainActor
final class JournalVM {
    var readings: [JournalReading] = []
    var prompts: [String] = []
    var isLoading = false
    var error: String?
    private(set) var isLocalMode: Bool = true

    private let repository: JournalRepository
    private var currentProfileId: Int?
    private var pendingEmbedderRebuild: Task<Void, Never>?

    init(repository: JournalRepository = DefaultJournalRepository.shared) {
        self.repository = repository
    }

    func load(profile: Profile?, isAuthenticated: Bool, forceRefresh: Bool = false) async {
        guard let profile else { return }
        currentProfileId = profile.id
        isLoading = true
        defer { isLoading = false }

        isLocalMode = AppConfig.personalMode || !isAuthenticated || profile.id <= 0
        if isLocalMode {
            let entries = await repository.loadLocalEntries(profileId: profile.id)
            readings = entries.map { mapLocalEntry($0) }
        } else {
            do {
                let cachePolicy: CachePolicy = forceRefresh ? .networkFirst : .cacheFirst
                readings = try await repository.fetchRemoteReadings(
                    profileId: profile.id,
                    cachePolicy: cachePolicy
                )
            } catch {
                self.error = error.localizedDescription
            }
        }

        do {
            prompts = try await repository.fetchPrompts()
        } catch {
            // Prompts are optional
        }
    }

    func saveEntry(readingId: Int, entry: String) async {
        if isLocalMode, let profileId = currentProfileId {
            let entries = await repository.saveLocalEntryText(
                profileId: profileId,
                id: readingId,
                entry: entry
            )
            readings = entries.map { mapLocalEntry($0) }
            scheduleEmbedderRebuild(profileId: profileId, entries: entries)
            return
        }
        do {
            try await repository.saveRemoteEntry(readingId: readingId, entry: entry)
        } catch {
            self.error = error.localizedDescription
        }
    }

    func saveOutcome(readingId: Int, outcome: JournalOutcome) async {
        if isLocalMode, let profileId = currentProfileId {
            let entries = await repository.saveLocalEntryOutcome(
                profileId: profileId,
                id: readingId,
                outcome: outcome.rawValue
            )
            readings = entries.map { mapLocalEntry($0) }
            return
        }
        do {
            try await repository.saveRemoteOutcome(readingId: readingId, outcome: outcome.rawValue)
        } catch {
            self.error = error.localizedDescription
        }
    }

    func makeLocalDraft(profileId: Int) async -> JournalReading {
        let id = await repository.nextLocalId(profileId: profileId)
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

    /// Coalesce embedder rebuilds: postpone work briefly so a burst of saves
    /// produces a single re-index pass instead of one per keystroke/save.
    private func scheduleEmbedderRebuild(profileId: Int, entries: [LocalJournalEntry]) {
        pendingEmbedderRebuild?.cancel()
        pendingEmbedderRebuild = Task { @MainActor [weak self] in
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            if Task.isCancelled { return }
            await JournalEmbedder.shared.rebuildIndex(profileId: profileId, entries: entries)
            self?.pendingEmbedderRebuild = nil
        }
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

// MARK: - Local Journal Entry (used by repository + embedder)

struct LocalJournalEntry: Codable, Identifiable, Hashable {
    let id: Int
    let profileId: Int
    var createdAt: Date
    var updatedAt: Date
    var entry: String
    var outcome: String? // yes|no|partial|neutral
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
