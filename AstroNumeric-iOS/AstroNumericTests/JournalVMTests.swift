import XCTest
@testable import AstroNumeric

final class JournalVMTests: XCTestCase {
    
    // MARK: - JournalOutcome Tests
    
    func testJournalOutcomeLabels() {
        XCTAssertEqual(JournalOutcome.yes.label, "✅ Yes")
        XCTAssertEqual(JournalOutcome.no.label, "❌ No")
        XCTAssertEqual(JournalOutcome.partial.label, "🔶 Partial")
        XCTAssertEqual(JournalOutcome.neutral.label, "➖ Neutral")
    }
    
    func testJournalOutcomeFromValidValue() {
        XCTAssertEqual(JournalOutcome.from("yes"), .yes)
        XCTAssertEqual(JournalOutcome.from("no"), .no)
        XCTAssertEqual(JournalOutcome.from("partial"), .partial)
        XCTAssertEqual(JournalOutcome.from("neutral"), .neutral)
    }
    
    func testJournalOutcomeFromNilReturnsNeutral() {
        XCTAssertEqual(JournalOutcome.from(nil), .neutral)
    }
    
    func testJournalOutcomeFromInvalidReturnsNeutral() {
        XCTAssertEqual(JournalOutcome.from("unknown"), .neutral)
        XCTAssertEqual(JournalOutcome.from(""), .neutral)
    }
    
    // MARK: - JournalRepository (local persistence) Tests

    func testJournalRepositoryListEmptyByDefault() async {
        let repository = DefaultJournalRepository()
        let profileId = -9999
        await repository.removeAllLocalEntries(profileId: profileId)
        let entries = await repository.loadLocalEntries(profileId: profileId)
        XCTAssertTrue(entries.isEmpty)
    }

    func testJournalRepositoryUpsertAndList() async {
        let repository = DefaultJournalRepository()
        let profileId = -8888
        await repository.removeAllLocalEntries(profileId: profileId)
        defer { Task { await repository.removeAllLocalEntries(profileId: profileId) } }

        _ = await repository.saveLocalEntryText(profileId: profileId, id: 1, entry: "Test entry")
        _ = await repository.saveLocalEntryOutcome(profileId: profileId, id: 1, outcome: "yes")

        let entries = await repository.loadLocalEntries(profileId: profileId)
        XCTAssertEqual(entries.count, 1)
        XCTAssertEqual(entries.first?.entry, "Test entry")
        XCTAssertEqual(entries.first?.outcome, "yes")
    }

    func testJournalRepositoryUpsertUpdatesExisting() async {
        let repository = DefaultJournalRepository()
        let profileId = -7777
        await repository.removeAllLocalEntries(profileId: profileId)
        defer { Task { await repository.removeAllLocalEntries(profileId: profileId) } }

        _ = await repository.saveLocalEntryText(profileId: profileId, id: 1, entry: "Version 1")
        _ = await repository.saveLocalEntryText(profileId: profileId, id: 1, entry: "Version 2")
        _ = await repository.saveLocalEntryOutcome(profileId: profileId, id: 1, outcome: "partial")

        let entries = await repository.loadLocalEntries(profileId: profileId)
        XCTAssertEqual(entries.count, 1)
        XCTAssertEqual(entries.first?.entry, "Version 2")
        XCTAssertEqual(entries.first?.outcome, "partial")
    }

    func testJournalRepositoryNextLocalId() async {
        let repository = DefaultJournalRepository()
        let profileId = -6666
        await repository.removeAllLocalEntries(profileId: profileId)
        defer { Task { await repository.removeAllLocalEntries(profileId: profileId) } }

        var next = await repository.nextLocalId(profileId: profileId)
        XCTAssertEqual(next, 1)

        _ = await repository.saveLocalEntryText(profileId: profileId, id: 1, entry: "Entry")
        next = await repository.nextLocalId(profileId: profileId)
        XCTAssertEqual(next, 2)

        _ = await repository.saveLocalEntryText(profileId: profileId, id: 2, entry: "Entry 2")
        next = await repository.nextLocalId(profileId: profileId)
        XCTAssertEqual(next, 3)
    }

    func testJournalRepositoryMigratesLegacyUserDefaults() async throws {
        let repository = DefaultJournalRepository()
        let profileId = -5050
        let legacyKey = "astromeric.local_journal.v1.profile.\(profileId)"

        // Clean state
        await repository.removeAllLocalEntries(profileId: profileId)
        defer {
            UserDefaults.standard.removeObject(forKey: legacyKey)
            Task { await repository.removeAllLocalEntries(profileId: profileId) }
        }

        // Seed legacy UserDefaults blob (encoded with .iso8601, matching old store).
        let legacyEntry = LocalJournalEntry(
            id: 7,
            profileId: profileId,
            createdAt: Date(timeIntervalSince1970: 1_700_000_000),
            updatedAt: Date(timeIntervalSince1970: 1_700_000_000),
            entry: "Legacy entry",
            outcome: "yes"
        )
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode([legacyEntry])
        UserDefaults.standard.set(data, forKey: legacyKey)

        // First load should migrate, return content, and clear the legacy key.
        let migrated = await repository.loadLocalEntries(profileId: profileId)
        XCTAssertEqual(migrated.count, 1)
        XCTAssertEqual(migrated.first?.entry, "Legacy entry")
        XCTAssertEqual(migrated.first?.outcome, "yes")
        XCTAssertNil(UserDefaults.standard.data(forKey: legacyKey))
    }

    // MARK: - JournalVM Local Draft Tests

    @MainActor
    func testMakeLocalDraftCreatesReading() async {
        let repository = DefaultJournalRepository()
        let profileId = -5555
        await repository.removeAllLocalEntries(profileId: profileId)
        defer { Task { await repository.removeAllLocalEntries(profileId: profileId) } }

        let vm = JournalVM(repository: repository)
        let draft = await vm.makeLocalDraft(profileId: profileId)

        XCTAssertEqual(draft.scope, "local")
        XCTAssertEqual(draft.scopeLabel, "Journal Entry")
        XCTAssertNil(draft.journalFull)
        XCTAssertNotNil(draft.formattedDate)
    }
    
    // MARK: - JournalReading Model Tests
    
    func testJournalReadingDecoding() throws {
        let json = """
        {
            "id": 42,
            "scope": "daily",
            "scope_label": "Daily Reading",
            "date": "2026-01-15T10:00:00Z",
            "formatted_date": "Jan 15, 2026",
            "has_journal": true,
            "journal_preview": "Today was...",
            "journal_full": "Today was a great day for reflection.",
            "feedback": "yes",
            "feedback_emoji": "✅",
            "content_summary": "A positive day"
        }
        """.data(using: .utf8)!
        
        let reading = try JSONDecoder().decode(JournalReading.self, from: json)
        XCTAssertEqual(reading.id, 42)
        XCTAssertEqual(reading.scope, "daily")
        XCTAssertEqual(reading.scopeLabel, "Daily Reading")
        XCTAssertEqual(reading.hasJournal, true)
        XCTAssertEqual(reading.journalFull, "Today was a great day for reflection.")
        XCTAssertEqual(reading.feedback, "yes")
    }
}
