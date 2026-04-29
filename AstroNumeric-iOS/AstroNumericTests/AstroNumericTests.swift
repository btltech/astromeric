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
        XCTAssertTrue(text.contains("Sensitive details were hidden because privacy mode is enabled."))

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
