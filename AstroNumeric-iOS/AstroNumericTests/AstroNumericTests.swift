import XCTest
@testable import AstroNumeric

final class AstroNumericTests: XCTestCase {
    private func makeProfile() -> Profile {
        Profile(
            id: 42,
            name: "Jane Example",
            dateOfBirth: "1991-04-03",
            timeOfBirth: "14:30:00",
            timeConfidence: "exact",
            placeOfBirth: "London, UK",
            latitude: 51.5072,
            longitude: -0.1276,
            timezone: "Europe/London",
            houseSystem: "Placidus"
        )
    }

    private func makeHabitResponse(id: String, lastCompleted: String?) -> HabitResponse {
        HabitResponse(
            id: id,
            name: "Habit \(id)",
            description: "Test habit",
            category: "exercise",
            createdDate: "2026-04-01",
            entries: [],
            summary: HabitSummary(
                habitId: id,
                habitName: "Habit \(id)",
                totalDays: 7,
                completedDays: lastCompleted == nil ? 0 : 1,
                currentStreak: lastCompleted == nil ? 0 : 1,
                longestStreak: lastCompleted == nil ? 0 : 1,
                completionRate: lastCompleted == nil ? 0 : 0.14,
                lastCompleted: lastCompleted
            )
        )
    }
    
    func testExample() throws {
        // Test placeholder
        XCTAssertTrue(true)
    }
    
    func testRetryPolicyDelay() throws {
        let policy = RetryPolicy.default
        
        // First attempt delay should be around 0.5s (with jitter)
        let delay1 = policy.delay(for: 1)
        XCTAssertGreaterThanOrEqual(delay1, 0.5)
        XCTAssertLessThanOrEqual(delay1, 0.65)
        
        // Second attempt should be around 1.0s (with jitter)
        let delay2 = policy.delay(for: 2)
        XCTAssertGreaterThanOrEqual(delay2, 1.0)
        XCTAssertLessThanOrEqual(delay2, 1.3)
    }
    
    func testReadingScopeDisplayName() throws {
        XCTAssertEqual(ReadingScope.daily.displayName, "Daily")
        XCTAssertEqual(ReadingScope.weekly.displayName, "Weekly")
        XCTAssertEqual(ReadingScope.monthly.displayName, "Monthly")
    }

    func testPrivacyRedactionMasksDisplayAndPayload() throws {
        let profile = makeProfile()

        XCTAssertEqual(profile.displayName(hideSensitive: true, role: .activeUser), "You")
        XCTAssertEqual(profile.displayName(hideSensitive: true, role: .genericProfile, index: 1), "Profile 2")
        XCTAssertEqual(profile.maskedDateOfBirth(hideSensitive: true), PrivacyRedaction.maskedDate)
        XCTAssertEqual(profile.maskedBirthTime(hideSensitive: true), PrivacyRedaction.hiddenValue)
        XCTAssertEqual(profile.maskedBirthplace(hideSensitive: true), PrivacyRedaction.hiddenValue)

        let payload = profile.privacySafePayload(hideSensitive: true)
        XCTAssertEqual(payload.name, PrivacyRedaction.privateUser)
        XCTAssertEqual(payload.dateOfBirth, profile.dateOfBirth)
        XCTAssertNil(payload.placeOfBirth)
        XCTAssertEqual(payload.latitude, profile.latitude)
        XCTAssertEqual(payload.longitude, profile.longitude)
    }

    func testReadingToneMapsSliderRangesToStableRequestValues() throws {
        let previousTone = AppStore.shared.tonePreference
        defer { AppStore.shared.tonePreference = previousTone }

        AppStore.shared.tonePreference = 10
        XCTAssertEqual(AppStore.shared.readingTone, .veryPractical)

        AppStore.shared.tonePreference = 30
        XCTAssertEqual(AppStore.shared.readingTone, .balancedPractical)

        AppStore.shared.tonePreference = 60
        XCTAssertEqual(AppStore.shared.readingTone, .balancedMystical)

        AppStore.shared.tonePreference = 90
        XCTAssertEqual(AppStore.shared.readingTone, .veryMystical)
    }

    func testForecastRequestIncludesResolvedReadingTone() throws {
        let previousTone = AppStore.shared.tonePreference
        defer { AppStore.shared.tonePreference = previousTone }

        AppStore.shared.tonePreference = 10
        let practicalRequest = V2ForecastRequest(profile: makeProfile(), scope: "daily")
        XCTAssertEqual(practicalRequest.tone, ReadingTone.veryPractical.rawValue)

        AppStore.shared.tonePreference = 90
        let mysticalRequest = V2ForecastRequest(profile: makeProfile(), scope: "daily")
        XCTAssertEqual(mysticalRequest.tone, ReadingTone.veryMystical.rawValue)
    }

    func testDailyFeaturePresentationNormalizesLuckPercentage() throws {
        XCTAssertEqual(DailyFeaturePresentation.normalizedLuckPercentage(72.34), 72.34, accuracy: 0.001)
        XCTAssertEqual(DailyFeaturePresentation.normalizedLuckPercentage(0.7234), 72.34, accuracy: 0.01)
        XCTAssertEqual(DailyFeaturePresentation.normalizedLuckPercentage(150.0), 100.0, accuracy: 0.001)
    }

    func testDailyFeaturePresentationRecognizesBackendColorNames() throws {
        XCTAssertEqual(DailyFeaturePresentation.usageHint(for: "Sunset Orange"), "Activate for energy and enthusiasm")
        XCTAssertEqual(DailyFeaturePresentation.usageHint(for: "Forest Green"), "Carry for abundance and fresh starts")
        XCTAssertEqual(DailyFeaturePresentation.usageHint(for: "Deep Purple"), "Channel for intuition and spiritual insight")
    }

    func testProfileLifePathNumberUsesBirthDateInsteadOfPersonalDayPlaceholder() throws {
        let profile = makeProfile()

        XCTAssertEqual(profile.lifePathNumber(useChaldean: false), 9)
        XCTAssertEqual(HomeView.cosmicIDLifePathText(profile: profile, useChaldean: false), "9")
        XCTAssertEqual(HomeView.cosmicIDLifePathText(profile: nil, useChaldean: false), "?")
    }

    func testForecastDayParsesIsoDateTimeUsingCivilDatePortion() throws {
        let day = ForecastDay(
            date: "2026-04-08T00:15:00Z",
            score: 84,
            vibe: "Powerful",
            icon: "🌟",
            recommendation: "Take action."
        )

        XCTAssertEqual(day.dayNumber, 8)
        XCTAssertEqual(day.weekday, "Wed")
        XCTAssertNotNil(day.dateObject)
    }

    @MainActor
    func testHomeVMHabitSummaryCountsTodayEntries() throws {
        // Use the current UTC date so the test doesn't go stale
        let formatter = ISO8601DateFormatter()
        let todayISO = formatter.string(from: Date())

        let habits = [
            makeHabitResponse(id: "1", lastCompleted: todayISO),
            makeHabitResponse(id: "2", lastCompleted: nil),
        ]

        let summary = HomeVM.habitSummary(from: habits, timezoneID: "UTC")
        XCTAssertEqual(summary.completed, 1)
        XCTAssertEqual(summary.total, 2)
    }

    func testHabitRepositoryPersistsLocalHabits() async throws {
        let repository = DefaultHabitRepository()
        await repository.saveLocalHabits([])
        defer { Task { await repository.saveLocalHabits([]) } }

        let habit = LocalHabit(
            id: "local-test",
            name: "Morning walk",
            category: "exercise",
            emoji: "🏃",
            currentStreak: 3,
            longestStreak: 5,
            completionRate: 0.75,
            isCompletedToday: true,
            lastCompleted: Date(timeIntervalSince1970: 1_777_000_000)
        )

        await repository.saveLocalHabits([habit])
        let loadedHabits = await repository.loadLocalHabits()
        let loaded = try XCTUnwrap(loadedHabits)

        XCTAssertEqual(loaded.count, 1)
        XCTAssertEqual(loaded.first?.id, habit.id)
        XCTAssertEqual(loaded.first?.name, habit.name)
        XCTAssertEqual(loaded.first?.isCompletedToday, true)
    }

    func testRelationshipRepositoryPersistsSavedRelationships() async throws {
        let repository = DefaultRelationshipRepository()
        await repository.saveRelationships([])
        defer { Task { await repository.saveRelationships([]) } }

        let relationship = SavedRelationship(
            personAName: "Jane",
            personBName: "Alex",
            personADOB: "1991-04-03",
            personBDOB: "1990-02-01",
            type: .romantic,
            overallScore: 82,
            categories: [CompatibilityCategorySummary(name: "Communication", score: 80, emoji: "💬")],
            strengths: ["Easy rapport"],
            challenges: ["Timing"],
            createdAt: Date(timeIntervalSince1970: 1_777_000_000),
            lastUpdated: Date(timeIntervalSince1970: 1_777_000_100)
        )

        await repository.saveRelationships([relationship])
        let loaded = await repository.loadRelationships()

        XCTAssertEqual(loaded.count, 1)
        XCTAssertEqual(loaded.first?.personAName, "Jane")
        XCTAssertEqual(loaded.first?.personBName, "Alex")
        XCTAssertEqual(loaded.first?.overallScore, 82)
    }

    @MainActor
    func testPrivacyModeExportUsesAnonymousFilenameAndRedactedText() throws {
        let previousValue = AppStore.shared.hideSensitiveDetailsEnabled
        AppStore.shared.hideSensitiveDetailsEnabled = true
        defer { AppStore.shared.hideSensitiveDetailsEnabled = previousValue }

        let profile = makeProfile()
        let exporter = ProfileExporter()

        XCTAssertEqual(exporter.exportFileName(for: profile), "private_profile.json")

        let text = exporter.exportAsText(profile)
        XCTAssertFalse(text.contains(profile.name))
        XCTAssertFalse(text.contains(profile.dateOfBirth))
        XCTAssertTrue(text.contains(PrivacyRedaction.privateProfile))
        XCTAssertTrue(text.contains(PrivacyRedaction.maskedDate))
        XCTAssertTrue(text.contains("Sensitive details were hidden in this text export because privacy mode is enabled."))
        XCTAssertTrue(text.contains("The backup JSON export can still include full birth details for restore."))

        let url = try XCTUnwrap(exporter.exportAsFile(profile))
        defer { try? FileManager.default.removeItem(at: url) }
        XCTAssertEqual(url.lastPathComponent, "private_profile.json")

        let data = try XCTUnwrap(exporter.exportProfile(profile))
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let decoded = try decoder.decode(ProfileExport.self, from: data)
        XCTAssertEqual(decoded.profile.name, profile.name)
        XCTAssertEqual(decoded.profile.dateOfBirth, profile.dateOfBirth)
        XCTAssertEqual(decoded.isRedacted, false)
    }
}

/// The backend sends timestamps with microseconds. JSONDecoder's built-in
/// .iso8601 rejects those before iOS 26, which blanked Home's daily features
/// and the morning brief on iOS 17 and 18. Run these on an iOS 18 simulator to
/// exercise the old parser.
final class APIDateDecodingTests: XCTestCase {

    private func decoder() -> JSONDecoder {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601WithOptionalFractionalSeconds
        return decoder
    }

    private func decodeDate(_ string: String) throws -> Date {
        try decoder().decode([Date].self, from: Data("[\"\(string)\"]".utf8))[0]
    }

    func testAcceptsFractionalSecondsWholeSecondsAndOffsets() throws {
        let whole = try decodeDate("2026-09-28T18:24:33Z")
        XCTAssertEqual(try decodeDate("2026-09-28T18:24:33.258095Z").timeIntervalSince(whole), 0.258, accuracy: 0.001)
        XCTAssertEqual(try decodeDate("2026-09-28T19:24:33+01:00"), whole)
    }

    func testRejectsTextThatIsNotADate() {
        XCTAssertThrowsError(try decodeDate("yesterday"))
    }

    func testMorningBriefFromTheServerDecodes() throws {
        let json = """
        {"date":"2026-09-28T18:24:33.427594Z","greeting":"Good evening","bullets":[{"emoji":"🌕","text":"Full Moon"}],
         "moon_phase":"Full Moon","personal_day":5,"vibe":"Adventurous"}
        """
        let brief = try decoder().decode(MorningBriefData.self, from: Data(json.utf8))
        XCTAssertEqual(brief.personalDay, 5)
    }
}

/// The Numerology screen shows server text beside a number. The app used to
/// compute that number itself (Pythagorean only, master numbers dropped), so a
/// Chaldean user or an 11 day could see one number beside another's meaning.
final class NumerologyNumbersTests: XCTestCase {

    private func decode(numbers: String?) throws -> NumerologyData {
        let numbersField = numbers.map { #","numerology_numbers":\#($0)"# } ?? ""
        let json = """
        {"profile":{"name":"Maria Yolanda Brown","date_of_birth":"1985-11-29"},
         "life_path":{"number":9,"meaning":"m"},
         "personal_year":{"year":2026,"cycle_number":5,"interpretation":"i"},
         "numerology_insights":{"soul_urge":"su","personality":"pe","personal_month":"pm","personal_day":"pd"}\(numbersField)}
        """
        return try JSONDecoder().decode(NumerologyData.self, from: Data(json.utf8))
    }

    func testShowsTheNumberTheServerWroteTheTextFor() throws {
        let data = try decode(numbers: #"{"soul_urge":7,"personality":22,"personal_month":3,"personal_day":11}"#)
        XCTAssertEqual(data.coreNumbers?.soulUrge?.number, 7)
        XCTAssertEqual(data.coreNumbers?.personality?.number, 22)
        XCTAssertEqual(data.cycles?.personalMonth?.number, 3)
        // A master-number day: the local fallback would have reduced this to 2.
        XCTAssertEqual(data.cycles?.personalDay?.number, 11)
        XCTAssertEqual(data.cycles?.personalDay?.meaning, "pd")
    }

    func testDecodesTodaysFullReading() throws {
        let json = """
        {"life_path":{"number":9},"daily_reading":{"text":"A full passage.","lens":"work","personal_day":33,"personal_month":5}}
        """
        let data = try JSONDecoder().decode(NumerologyData.self, from: Data(json.utf8))
        XCTAssertEqual(data.dailyReading?.text, "A full passage.")
        XCTAssertEqual(data.dailyReading?.personalDay, 33)
    }

    func testOlderResponsesWithoutNumbersStillShowANumber() throws {
        let data = try decode(numbers: nil)
        XCTAssertNotNil(data.coreNumbers?.soulUrge?.number)
        XCTAssertNotNil(data.cycles?.personalDay?.number)
    }

    func testEachYIsAVowelOrAConsonantNeverBoth() {
        // "Lynn": Y is the only vowel sound. "Maya": Y sits between vowels.
        let lynn = NumerologyData.vowelAndConsonantValues(for: "Lynn")
        XCTAssertEqual(lynn.vowels, [7])
        XCTAssertEqual(lynn.consonants, [3, 5, 5])
        let maya = NumerologyData.vowelAndConsonantValues(for: "Maya Lynn")
        XCTAssertEqual(maya.vowels, [1, 1, 7])
        XCTAssertEqual(maya.vowels.count + maya.consonants.count, 8)
    }
}

final class DisplayFormattingTests: XCTestCase {

    func testHomeHeadlineIsTheReadingsFirstSentence() {
        // The reading's "headline" is a paragraph; Home shows its first sentence.
        XCTAssertEqual(
            HomeView.firstSentence(of: "Your warmth gives you an edge — use it. Mercury is busy. More."),
            "Your warmth gives you an edge — use it."
        )
        XCTAssertEqual(HomeView.firstSentence(of: "Big day! Then rest."), "Big day!")
        XCTAssertEqual(HomeView.firstSentence(of: "No full stop at all"), "No full stop at all")
        // A decimal point is not a sentence end.
        XCTAssertEqual(HomeView.firstSentence(of: "Energy is 7.7 today. Rest."), "Energy is 7.7 today.")
    }

    func testAspectKeysReadAsWords() {
        XCTAssertEqual("semi_square".aspectDisplayName, "Semi-square")
        XCTAssertEqual("conjunction".aspectDisplayName, "Conjunction")
    }
}


final class HoraryOracleTests: XCTestCase {

    private func body(_ name: String, _ sign: String, _ absolute: Double,
                      retrograde: Bool = false, dignity: String? = nil) -> PlanetPlacement {
        PlanetPlacement(name: name, sign: sign, degree: absolute.truncatingRemainder(dividingBy: 30),
                        absoluteDegree: absolute, house: nil, retrograde: retrograde, dignity: dignity)
    }

    /// Hour of Venus; Venus strong in Taurus; Mercury retrograde and in fall
    /// in Pisces; a waning Moon well away from both.
    private func sky(voidOfCourse: Bool = false) -> CalendarOracle.HorarySnapshot {
        CalendarOracle.HorarySnapshot(
            timestamp: Date(timeIntervalSince1970: 1_790_000_000),
            planetaryHour: "Venus",
            moonSign: "Leo",
            moonDegree: 10,
            moonPhase: "Waning Gibbous",
            isVoidOfCourse: voidOfCourse,
            keyTransits: [],
            bodies: [
                body("Venus", "Taurus", 45, dignity: "domicile"),
                body("Mercury", "Pisces", 340, retrograde: true, dignity: "fall"),
                body("Moon", "Leo", 130),
                body("Saturn", "Aries", 5),
            ]
        )
    }

    func testDetectsTheQuestionsTopic() {
        XCTAssertEqual(OracleTopic.detect(in: "Should I text my ex?"), .love)
        XCTAssertEqual(OracleTopic.detect(in: "Should I invest in crypto this month?"), .money)
        XCTAssertEqual(OracleTopic.detect(in: "Should I take the job offer?"), .career)
        XCTAssertEqual(OracleTopic.detect(in: "Should I sign the contract?"), .communication)
        XCTAssertEqual(OracleTopic.detect(in: "Should I stop my medication?"), .wellbeing)
        XCTAssertEqual(OracleTopic.detect(in: "Is today a good day?"), .general)
        // "exam" must not read as "ex".
        XCTAssertEqual(OracleTopic.detect(in: "Will I pass the exam?"), .career)
    }

    func testTheSameSkyAnswersDifferentQuestionsDifferently() {
        let love = HoraryOracle.read(question: "Should I ask her on a date?", snapshot: sky())
        XCTAssertEqual(love.answer, "Yes")
        XCTAssertTrue(love.reasoning.contains("Venus"))

        let contract = HoraryOracle.read(question: "Should I sign the contract today?", snapshot: sky())
        XCTAssertEqual(contract.answer, "No")
        XCTAssertTrue(contract.factors?.contains { !$0.helps && $0.text.contains("Mercury is retrograde") } == true)
        // Every point is explained, and the summary says how they balanced out.
        XCTAssertTrue(contract.reasoning.contains("so the answer is no"))
        XCTAssertTrue(love.factors?.contains { $0.helps && $0.text.contains("home signs") } == true)
    }

    func testVoidOfCourseMoonMeansNo() {
        let answer = HoraryOracle.read(question: "Should I ask her on a date?", snapshot: sky(voidOfCourse: true))
        XCTAssertEqual(answer.answer, "No")
        XCTAssertEqual(answer.confidence, 0.85, accuracy: 0.001)
    }

    func testSameQuestionAndSkyAlwaysGiveTheSameAnswer() {
        let first = HoraryOracle.read(question: "Should I launch now?", snapshot: sky())
        let second = HoraryOracle.read(question: "Should I launch now?", snapshot: sky())
        XCTAssertEqual(first.answer, second.answer)
        XCTAssertEqual(first.reasoning, second.reasoning)
    }

    func testHealthAndMoneyQuestionsPointToAProfessional() {
        let health = HoraryOracle.read(question: "Should I stop my medication?", snapshot: sky())
        XCTAssertTrue(health.guidance.contains { $0.contains("doctor") })
        let money = HoraryOracle.read(question: "Should I invest my savings?", snapshot: sky())
        XCTAssertTrue(money.guidance.contains { $0.contains("adviser") })
    }
}
