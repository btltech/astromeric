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
    
    // MARK: - LocalJournalStore Tests
    
    func testLocalJournalStoreListEmptyByDefault() {
        let store = LocalJournalStore.shared
        // Use a profile ID unlikely to exist in real data
        let entries = store.list(profileId: -9999)
        XCTAssertTrue(entries.isEmpty)
    }
    
    func testLocalJournalStoreUpsertAndList() {
        let store = LocalJournalStore.shared
        let profileId = -8888
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "astromeric.local_journal.v1.profile.\(profileId)")
        
        store.upsert(profileId: profileId, id: 1, entry: "Test entry", outcome: "yes")
        let entries = store.list(profileId: profileId)
        
        XCTAssertEqual(entries.count, 1)
        XCTAssertEqual(entries.first?.entry, "Test entry")
        XCTAssertEqual(entries.first?.outcome, "yes")
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "astromeric.local_journal.v1.profile.\(profileId)")
    }
    
    func testLocalJournalStoreUpsertUpdatesExisting() {
        let store = LocalJournalStore.shared
        let profileId = -7777
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "astromeric.local_journal.v1.profile.\(profileId)")
        
        store.upsert(profileId: profileId, id: 1, entry: "Version 1", outcome: nil)
        store.upsert(profileId: profileId, id: 1, entry: "Version 2", outcome: "partial")
        
        let entries = store.list(profileId: profileId)
        XCTAssertEqual(entries.count, 1)
        XCTAssertEqual(entries.first?.entry, "Version 2")
        XCTAssertEqual(entries.first?.outcome, "partial")
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "astromeric.local_journal.v1.profile.\(profileId)")
    }
    
    func testLocalJournalStoreNextId() {
        let store = LocalJournalStore.shared
        let profileId = -6666
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "astromeric.local_journal.v1.profile.\(profileId)")
        
        XCTAssertEqual(store.nextId(profileId: profileId), 1)
        
        store.upsert(profileId: profileId, id: 1, entry: "Entry", outcome: nil)
        XCTAssertEqual(store.nextId(profileId: profileId), 2)
        
        store.upsert(profileId: profileId, id: 2, entry: "Entry 2", outcome: nil)
        XCTAssertEqual(store.nextId(profileId: profileId), 3)
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "astromeric.local_journal.v1.profile.\(profileId)")
    }
    
    // MARK: - JournalVM Local Draft Tests
    
    @MainActor
    func testMakeLocalDraftCreatesReading() {
        let vm = JournalVM()
        let profileId = -5555
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "astromeric.local_journal.v1.profile.\(profileId)")
        
        let draft = vm.makeLocalDraft(profileId: profileId)
        
        XCTAssertEqual(draft.scope, "local")
        XCTAssertEqual(draft.scopeLabel, "Journal Entry")
        XCTAssertNil(draft.journalFull)
        XCTAssertNotNil(draft.formattedDate)
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "astromeric.local_journal.v1.profile.\(profileId)")
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
