import Foundation

protocol ChartRepository {
    func natalChart(for profile: Profile) async throws -> ChartData
    func synastryChart(personA: Profile, personB: ProfilePayload) async throws -> SynastryChartResponse
}

struct DefaultChartRepository: ChartRepository {
    private let api: APIService
    private let ephemeris: EphemerisService

    init(api: APIService = LiveAPIService(), ephemeris: EphemerisService = LiveEphemerisService()) {
        self.api = api
        self.ephemeris = ephemeris
    }

    func natalChart(for profile: Profile) async throws -> ChartData {
        do {
            let response: V2ApiResponse<ChartData> = try await api.fetch(
                .natalChart(profile: profile),
                cachePolicy: .networkFirst
            )
            return response.data
        } catch {
            DebugLog.log("API chart fetch failed, falling back to local ephemeris: \(error)")
            return try await ephemeris.calculateNatalChart(profile: profile)
        }
    }

    func synastryChart(personA: Profile, personB: ProfilePayload) async throws -> SynastryChartResponse {
        let response: V2ApiResponse<SynastryChartResponse> = try await api.fetch(
            .synastryChart(personA: personA, personB: personB),
            cachePolicy: .networkFirst
        )
        return response.data
    }
}

protocol DailyContentRepository {
    func reading(profile: Profile, scope: ReadingScope, date: Date?, cachePolicy: CachePolicy) async throws -> PredictionData
    func dailyFeatures(profile: Profile, date: Date?, cachePolicy: CachePolicy) async throws -> DailyFeaturesData
    func currentMoon(cachePolicy: CachePolicy) async throws -> MoonPhaseData
}

struct DefaultDailyContentRepository: DailyContentRepository {
    private let api: APIService

    init(api: APIService = LiveAPIService()) {
        self.api = api
    }

    func reading(profile: Profile, scope: ReadingScope, date: Date? = nil, cachePolicy: CachePolicy = .networkFirst) async throws -> PredictionData {
        let response: V2ApiResponse<PredictionData> = try await api.fetch(
            .reading(profile: profile, scope: scope, date: date),
            cachePolicy: cachePolicy
        )
        return response.data
    }

    func dailyFeatures(profile: Profile, date: Date? = nil, cachePolicy: CachePolicy = .cacheFirst) async throws -> DailyFeaturesData {
        let response: V2ApiResponse<DailyFeaturesData> = try await api.fetch(
            .dailyFeatures(profile: profile, date: date),
            cachePolicy: cachePolicy
        )
        return response.data
    }

    func currentMoon(cachePolicy: CachePolicy = .cacheFirst) async throws -> MoonPhaseData {
        let response: V2ApiResponse<MoonPhaseData> = try await api.fetch(.currentMoon, cachePolicy: cachePolicy)
        return response.data
    }
}

// MARK: - Journal

protocol JournalRepository: Sendable {
    func fetchRemoteReadings(profileId: Int, cachePolicy: CachePolicy) async throws -> [JournalReading]
    func fetchPrompts() async throws -> [String]
    func saveRemoteEntry(readingId: Int, entry: String) async throws
    func saveRemoteOutcome(readingId: Int, outcome: String) async throws

    func loadLocalEntries(profileId: Int) async -> [LocalJournalEntry]
    func nextLocalId(profileId: Int) async -> Int
    func saveLocalEntryText(profileId: Int, id: Int, entry: String) async -> [LocalJournalEntry]
    func saveLocalEntryOutcome(profileId: Int, id: Int, outcome: String?) async -> [LocalJournalEntry]
    func removeAllLocalEntries(profileId: Int) async
}

actor DefaultJournalRepository: JournalRepository {
    static let shared = DefaultJournalRepository()

    private let api: APIService
    private let domain = "journal"

    private func key(profileId: Int) -> String { "entries.v1.profile.\(profileId)" }
    private func legacyKey(profileId: Int) -> String { "astromeric.local_journal.v1.profile.\(profileId)" }

    init(api: APIService = LiveAPIService()) {
        self.api = api
    }

    // MARK: Remote

    func fetchRemoteReadings(profileId: Int, cachePolicy: CachePolicy) async throws -> [JournalReading] {
        let response: V2ApiResponse<JournalReadingsResponse> = try await api.fetch(
            .journalReadings(profileId: profileId),
            cachePolicy: cachePolicy
        )
        return response.data.readings
    }

    func fetchPrompts() async throws -> [String] {
        let response: V2ApiResponse<JournalPromptsResponse> = try await api.fetch(
            .journalPrompts,
            cachePolicy: .cacheFirst
        )
        return response.data.prompts
    }

    func saveRemoteEntry(readingId: Int, entry: String) async throws {
        let _: V2ApiResponse<JournalEntryResponse> = try await api.fetch(
            .journalEntry(body: JournalEntryRequest(readingId: readingId, entry: entry)),
            cachePolicy: .networkFirst
        )
    }

    func saveRemoteOutcome(readingId: Int, outcome: String) async throws {
        let _: V2ApiResponse<JournalOutcomeResponse> = try await api.fetch(
            .journalOutcome(body: JournalOutcomeRequest(readingId: readingId, outcome: outcome, notes: nil)),
            cachePolicy: .networkFirst
        )
    }

    // MARK: Local

    func loadLocalEntries(profileId: Int) async -> [LocalJournalEntry] {
        if let entries = await LocalDomainDatabase.shared.load(
            [LocalJournalEntry].self,
            domain: domain,
            key: key(profileId: profileId)
        ) {
            return entries.sorted { $0.createdAt > $1.createdAt }
        }
        // Migrate legacy UserDefaults blob (encoded with .iso8601)
        let legacy = legacyKey(profileId: profileId)
        if let data = UserDefaults.standard.data(forKey: legacy) {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            if let entries = try? decoder.decode([LocalJournalEntry].self, from: data) {
                let sorted = entries.sorted { $0.createdAt > $1.createdAt }
                await LocalDomainDatabase.shared.save(sorted, domain: domain, key: key(profileId: profileId))
                UserDefaults.standard.removeObject(forKey: legacy)
                return sorted
            }
        }
        return []
    }

    func nextLocalId(profileId: Int) async -> Int {
        let entries = await loadLocalEntries(profileId: profileId)
        return (entries.map(\.id).max() ?? 0) + 1
    }

    func saveLocalEntryText(profileId: Int, id: Int, entry: String) async -> [LocalJournalEntry] {
        var entries = await loadLocalEntries(profileId: profileId)
        let now = Date()
        if let idx = entries.firstIndex(where: { $0.id == id }) {
            entries[idx].entry = entry
            entries[idx].updatedAt = now
        } else {
            entries.append(LocalJournalEntry(
                id: id,
                profileId: profileId,
                createdAt: now,
                updatedAt: now,
                entry: entry,
                outcome: nil
            ))
        }
        entries.sort { $0.createdAt > $1.createdAt }
        await LocalDomainDatabase.shared.save(entries, domain: domain, key: key(profileId: profileId))
        return entries
    }

    func saveLocalEntryOutcome(profileId: Int, id: Int, outcome: String?) async -> [LocalJournalEntry] {
        var entries = await loadLocalEntries(profileId: profileId)
        let now = Date()
        if let idx = entries.firstIndex(where: { $0.id == id }) {
            entries[idx].outcome = outcome
            entries[idx].updatedAt = now
        } else {
            entries.append(LocalJournalEntry(
                id: id,
                profileId: profileId,
                createdAt: now,
                updatedAt: now,
                entry: "",
                outcome: outcome
            ))
        }
        entries.sort { $0.createdAt > $1.createdAt }
        await LocalDomainDatabase.shared.save(entries, domain: domain, key: key(profileId: profileId))
        return entries
    }

    func removeAllLocalEntries(profileId: Int) async {
        await LocalDomainDatabase.shared.remove(domain: domain, key: key(profileId: profileId))
        UserDefaults.standard.removeObject(forKey: legacyKey(profileId: profileId))
    }
}

// MARK: - Cosmic Guide

protocol CosmicGuideRepository: Sendable {
    func chat(
        message: String,
        context: ChatContext,
        systemPrompt: String?,
        tone: String?
    ) async throws -> ChatResponse
}

struct DefaultCosmicGuideRepository: CosmicGuideRepository {
    private let api: APIService

    init(api: APIService = LiveAPIService()) {
        self.api = api
    }

    func chat(
        message: String,
        context: ChatContext,
        systemPrompt: String? = nil,
        tone: String? = nil
    ) async throws -> ChatResponse {
        let response: V2ApiResponse<ChatResponse> = try await api.fetch(
            .cosmicGuideChat(
                message: message,
                context: context,
                systemPrompt: systemPrompt,
                tone: tone
            ),
            cachePolicy: .networkFirst
        )
        return response.data
    }
}

// MARK: - Alert Preferences

protocol AlertPreferencesRepository: Sendable {
    func loadPreferences() async throws -> AlertPreferencesResponse
    func updatePreferences(_ request: AlertPreferencesRequest) async throws -> AlertPreferencesResponse
    func upcomingMoonEvents() async throws -> [UpcomingMoonEvent]
}

struct DefaultAlertPreferencesRepository: AlertPreferencesRepository {
    private let api: APIService

    init(api: APIService = LiveAPIService()) {
        self.api = api
    }

    func loadPreferences() async throws -> AlertPreferencesResponse {
        try await api.fetch(.alertPreferences, cachePolicy: .networkFirst)
    }

    func updatePreferences(_ request: AlertPreferencesRequest) async throws -> AlertPreferencesResponse {
        try await api.fetch(.updateAlertPreferences(request), cachePolicy: .networkFirst)
    }

    func upcomingMoonEvents() async throws -> [UpcomingMoonEvent] {
        let response: V2ApiResponse<UpcomingMoonEventsResponse> = try await api.fetch(
            .upcomingMoonEvents,
            cachePolicy: .cacheFirst
        )
        return response.data.events
    }
}