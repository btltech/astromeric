import XCTest
@testable import AstroNumeric

/// Canary test for the Swiss Ephemeris C-bridge.
/// If an iOS update, Xcode migration, or bridging header change
/// breaks the engine, this test will catch it instantly.
final class EphemerisEngineTests: XCTestCase {

    private func makeExactProfile() -> Profile {
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

    private func makeNoTimeProfile() -> Profile {
        Profile(
            id: 43,
            name: "No Time Example",
            dateOfBirth: "1991-04-03",
            timeOfBirth: nil,
            timeConfidence: nil,
            placeOfBirth: "London, UK",
            latitude: 51.5072,
            longitude: -0.1276,
            timezone: "Europe/London",
            houseSystem: "Placidus"
        )
    }

    /// July 20, 1969 20:17 UTC — Apollo 11 Moon Landing.
    /// Known tropical positions from Astro-Databank / Astro.com:
    ///   Sun  ≈ 27°55' Cancer
    ///   Moon ≈ 7°53' Libra
    func testMoonLandingPositions() async throws {
        // Build the date: 1969-07-20 20:17:00 UTC
        var components = DateComponents()
        components.year = 1969
        components.month = 7
        components.day = 20
        components.hour = 20
        components.minute = 17
        components.second = 0
        components.timeZone = TimeZone(identifier: "UTC")

        let calendar = Calendar(identifier: .gregorian)
        let moonLandingDate = try XCTUnwrap(calendar.date(from: components))

        // Calculate transits for that moment
        let transits = try await EphemerisEngine.shared.calculateCurrentTransits(date: moonLandingDate)

        // --- Sun ---
        let sun = try XCTUnwrap(transits.first(where: { $0.name == "Sun" }), "Sun not found in transits")
        XCTAssertEqual(sun.sign, "Cancer", "Sun should be in Cancer on July 20, 1969")
        // Sun should be around 27° Cancer
        XCTAssertGreaterThan(sun.degree, 25.0, "Sun degree should be ~27° Cancer")
        XCTAssertLessThan(sun.degree, 29.0, "Sun degree should be ~27° Cancer")

        // --- Moon ---
        let moon = try XCTUnwrap(transits.first(where: { $0.name == "Moon" }), "Moon not found in transits")
        XCTAssertEqual(moon.sign, "Libra", "Moon should be in Libra during the Moon Landing")
        // Moon should be around 7-9° Libra
        XCTAssertGreaterThan(moon.degree, 7.0, "Moon degree should be ~8° Libra")
        XCTAssertLessThan(moon.degree, 9.0, "Moon degree should be ~8° Libra")

        // --- Validate we got all expected planets ---
        let expectedPlanets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        for name in expectedPlanets {
            XCTAssertTrue(transits.contains(where: { $0.name == name }), "\(name) missing from transits")
        }
    }

    /// Sanity check: degrees are in valid range (0-360)
    func testTransitDegreesInRange() async throws {
        let transits = try await EphemerisEngine.shared.calculateCurrentTransits()

        for planet in transits {
            if let absDeg = planet.absoluteDegree {
                XCTAssertGreaterThanOrEqual(absDeg, 0.0, "\(planet.name) absoluteDegree should be >= 0")
                XCTAssertLessThan(absDeg, 360.0, "\(planet.name) absoluteDegree should be < 360")
            }
            XCTAssertGreaterThanOrEqual(planet.degree, 0.0, "\(planet.name) degree should be >= 0")
            XCTAssertLessThan(planet.degree, 30.0, "\(planet.name) degree should be < 30 (within sign)")
        }
    }

    func testNatalChartMatchesBackendGoldenProfileForExactBirthTime() async throws {
        let chart = try await EphemerisEngine.shared.calculateNatalChart(profile: makeExactProfile())

        XCTAssertEqual(chart.metadata?.birthTimeAssumed, false)
        XCTAssertEqual(chart.metadata?.dataQuality, "full")

        let sun = try XCTUnwrap(chart.planets.first(where: { $0.name == "Sun" }))
        XCTAssertEqual(sun.sign, "Aries")
        XCTAssertEqual(sun.dignity, "exaltation")
        XCTAssertEqual(sun.house, 9)
        XCTAssertEqual(sun.absoluteDegree ?? 0, 13.2934, accuracy: 0.2)

        let venus = try XCTUnwrap(chart.planets.first(where: { $0.name == "Venus" }))
        XCTAssertEqual(venus.sign, "Taurus")
        XCTAssertEqual(venus.dignity, "domicile")
        XCTAssertEqual(venus.house, 10)
        XCTAssertEqual(venus.absoluteDegree ?? 0, 48.8143, accuracy: 0.25)

        let pointNames = Set((chart.points ?? []).map(\ .name))
        XCTAssertEqual(pointNames, Set(["North Node", "South Node", "Chiron", "Part of Fortune"]))

        let northNode = try XCTUnwrap(chart.points?.first(where: { $0.name == "North Node" }))
        XCTAssertEqual(northNode.sign, "Capricorn")
        XCTAssertEqual(northNode.house, 6)
        XCTAssertEqual(northNode.absoluteDegree ?? 0, 294.2327, accuracy: 0.35)

        let fortune = try XCTUnwrap(chart.points?.first(where: { $0.name == "Part of Fortune" }))
        XCTAssertEqual(fortune.sign, "Aries")
        XCTAssertEqual(fortune.house, 9)
        XCTAssertEqual(fortune.chartType, "day")
        XCTAssertEqual(fortune.absoluteDegree ?? 0, 10.0314, accuracy: 0.35)
    }

    func testNatalChartMatchesBackendGoldenProfileWhenBirthTimeIsUnknown() async throws {
        let chart = try await EphemerisEngine.shared.calculateNatalChart(profile: makeNoTimeProfile())

        XCTAssertEqual(chart.metadata?.birthTimeAssumed, true)
        XCTAssertEqual(chart.metadata?.dataQuality, "date_and_place")

        let sun = try XCTUnwrap(chart.planets.first(where: { $0.name == "Sun" }))
        XCTAssertEqual(sun.sign, "Aries")
        XCTAssertEqual(sun.dignity, "exaltation")
        XCTAssertEqual(sun.house, 10)
        XCTAssertEqual(sun.absoluteDegree ?? 0, 13.1907, accuracy: 0.2)

        let fortune = try XCTUnwrap(chart.points?.first(where: { $0.name == "Part of Fortune" }))
        XCTAssertEqual(fortune.sign, "Pisces")
        XCTAssertEqual(fortune.house, 9)
        XCTAssertEqual(fortune.chartType, "day")
        XCTAssertEqual(fortune.absoluteDegree ?? 0, 342.0683, accuracy: 0.4)

        let northNode = try XCTUnwrap(chart.points?.first(where: { $0.name == "North Node" }))
        XCTAssertEqual(northNode.sign, "Capricorn")
        XCTAssertEqual(northNode.house, 7)
        XCTAssertEqual(northNode.absoluteDegree ?? 0, 294.2382, accuracy: 0.35)
    }
}
