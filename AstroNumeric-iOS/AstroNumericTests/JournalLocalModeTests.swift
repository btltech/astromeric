import XCTest
@testable import AstroNumeric

/// The iOS app has no accounts, and the journal's remote endpoints require one:
/// `/v2/journal/readings/{id}` answers 401 without a session. Journal work must
/// therefore stay on the device — these tests pin that, so a future change that
/// routes journal writes through the network fails here rather than silently
/// dropping someone's entries.
///
/// `/v2/journal/prompts` is deliberately unauthenticated and is the one journal
/// call that may run for everyone.
@MainActor
final class JournalLocalModeTests: XCTestCase {

    /// Records which side of the repository the view model reached for.
    private actor CallLog {
        private(set) var remoteCalls: [String] = []
        private(set) var localCalls: [String] = []
        func remote(_ name: String) { remoteCalls.append(name) }
        func local(_ name: String) { localCalls.append(name) }
    }

    private struct SpyRepository: JournalRepository {
        let log: CallLog

        func fetchRemoteReadings(profileId: Int, cachePolicy: CachePolicy) async throws -> [JournalReading] {
            await log.remote("fetchRemoteReadings")
            return []
        }
        func fetchPrompts() async throws -> [String] {
            await log.remote("fetchPrompts")
            return ["What stood out today?"]
        }
        func saveRemoteEntry(readingId: Int, entry: String) async throws {
            await log.remote("saveRemoteEntry")
        }
        func saveRemoteOutcome(readingId: Int, outcome: String) async throws {
            await log.remote("saveRemoteOutcome")
        }
        func loadLocalEntries(profileId: Int) async -> [LocalJournalEntry] {
            await log.local("loadLocalEntries")
            return []
        }
        func nextLocalId(profileId: Int) async -> Int {
            await log.local("nextLocalId")
            return 1
        }
        func saveLocalEntryText(profileId: Int, id: Int, entry: String) async -> [LocalJournalEntry] {
            await log.local("saveLocalEntryText")
            return []
        }
        func saveLocalEntryOutcome(profileId: Int, id: Int, outcome: String?) async -> [LocalJournalEntry] {
            await log.local("saveLocalEntryOutcome")
            return []
        }
        func removeAllLocalEntries(profileId: Int) async {
            await log.local("removeAllLocalEntries")
        }
    }

    private func makeProfile() -> Profile {
        Profile(
            id: 7,
            name: "Local Only",
            dateOfBirth: "1990-05-15",
            timeOfBirth: nil,
            timeConfidence: "unknown",
            placeOfBirth: "London, UK",
            latitude: 51.5072,
            longitude: -0.1276,
            timezone: "Europe/London",
            houseSystem: "Placidus"
        )
    }

    func testUnauthenticatedLoadReadsLocallyAndOnlyFetchesPrompts() async {
        let log = CallLog()
        let vm = JournalVM(repository: SpyRepository(log: log))

        await vm.load(profile: makeProfile(), isAuthenticated: false)

        XCTAssertTrue(vm.isLocalMode)
        let remote = await log.remoteCalls
        let local = await log.localCalls
        // Prompts need no account; readings would 401.
        XCTAssertEqual(remote, ["fetchPrompts"])
        XCTAssertEqual(local, ["loadLocalEntries"])
    }

    func testUnauthenticatedWritesNeverGoToTheNetwork() async {
        let log = CallLog()
        let vm = JournalVM(repository: SpyRepository(log: log))
        await vm.load(profile: makeProfile(), isAuthenticated: false)

        await vm.saveEntry(readingId: 1, entry: "Wrote something down.")
        await vm.saveOutcome(readingId: 1, outcome: .yes)

        let remote = await log.remoteCalls
        XCTAssertFalse(remote.contains("saveRemoteEntry"))
        XCTAssertFalse(remote.contains("saveRemoteOutcome"))
        let local = await log.localCalls
        XCTAssertTrue(local.contains("saveLocalEntryText"))
        XCTAssertTrue(local.contains("saveLocalEntryOutcome"))
    }
}
