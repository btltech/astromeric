// CalendarOracle.swift
// Reads the user's iOS Calendar (EventKit) and calculates cosmic weather for upcoming events.
// Provides context blocks for the AI to proactively advise on scheduled events.

import Foundation
import EventKit

actor CalendarOracle {
    static let shared = CalendarOracle()

    private let eventStore = EKEventStore()
    private var isAuthorized = false

    private init() {}

    // MARK: - Horary Snapshot

    /// A point-in-time cosmic state for Horary Astrology queries.
    struct HorarySnapshot {
        let timestamp: Date
        let planetaryHour: String
        let moonSign: String
        let moonDegree: Double
        let moonPhase: String
        let isVoidOfCourse: Bool
        let keyTransits: [String]

        /// Compact telemetry string for UI display.
        var citation: String {
            let planetSymbols: [String: String] = [
                "Saturn": "♄", "Jupiter": "♃", "Mars": "♂",
                "Sun": "☉", "Venus": "♀", "Mercury": "☿", "Moon": "☽"
            ]
            let hourSymbol = planetSymbols[planetaryHour] ?? planetaryHour
            var parts = [
                "\(hourSymbol) Hour of \(planetaryHour)",
                "☽ \(String(format: "%.0f", moonDegree))° \(moonSign) (\(moonPhase))"
            ]
            if isVoidOfCourse {
                parts.append("⚠️ VOC")
            }
            for transit in keyTransits.prefix(2) {
                var t = transit
                for (name, sym) in planetSymbols {
                    t = t.replacingOccurrences(of: name, with: sym)
                }
                parts.append(t)
            }
            return "[\(parts.joined(separator: " | "))]"
        }

        /// Threat level: green (favorable), yellow (neutral), red (caution).
        var threatLevel: ThreatLevel {
            let cautionPlanets = ["Saturn", "Mars"]
            let favorablePlanets = ["Venus", "Jupiter"]
            if isVoidOfCourse || cautionPlanets.contains(planetaryHour) {
                return .red
            } else if favorablePlanets.contains(planetaryHour) {
                return .green
            }
            return .yellow
        }

        enum ThreatLevel {
            case green, yellow, red

            var label: String {
                switch self {
                case .green: return "🟢"
                case .yellow: return "🟡"
                case .red: return "🔴"
                }
            }
        }
    }

    /// Capture the cosmic state at a given moment for Horary analysis.
    func snapshot(at date: Date = Date(), latitude: Double? = nil, longitude: Double? = nil) async -> HorarySnapshot {
        var planetaryHour = "Unknown"
        var moonSign = "Unknown"
        var moonDegree: Double = 0
        var moonPhase = "Unknown"
        var isVoid = false
        var keyTransits: [String] = []

        if let transits = try? await EphemerisEngine.shared.calculateCurrentTransits(date: date) {
            if let moon = transits.first(where: { $0.name == "Moon" }) {
                moonSign = moon.sign
                moonDegree = moon.degree
            }
            if let sun = transits.first(where: { $0.name == "Sun" }),
               let moon = transits.first(where: { $0.name == "Moon" }),
               let sunDeg = sun.absoluteDegree,
               let moonDeg = moon.absoluteDegree {
                var elongation = moonDeg - sunDeg
                if elongation < 0 { elongation += 360 }
                moonPhase = phaseName(elongation: elongation)
            }
            let slowPlanets = ["Saturn", "Jupiter", "Uranus", "Neptune", "Pluto", "Mars"]
            for idx in 0..<transits.count {
                for jdx in (idx+1)..<transits.count {
                    let bodyA = transits[idx]
                    let bodyB = transits[jdx]
                    guard slowPlanets.contains(bodyA.name) || slowPlanets.contains(bodyB.name) else { continue }
                    guard let aDeg = bodyA.absoluteDegree, let bDeg = bodyB.absoluteDegree else { continue }
                    var diff = abs(aDeg - bDeg)
                    if diff > 180 { diff = 360 - diff }
                    if diff < 3 { keyTransits.append("\(bodyA.name) conjunct \(bodyB.name)") }
                    else if abs(diff - 90) < 3 { keyTransits.append("\(bodyA.name) square \(bodyB.name)") }
                    else if abs(diff - 180) < 3 { keyTransits.append("\(bodyA.name) opposite \(bodyB.name)") }
                }
            }
            isVoid = checkVoidOfCourse(transits: transits)
        }

        planetaryHour = await chaldeanPlanetaryHour(at: date, latitude: latitude, longitude: longitude)

        return HorarySnapshot(
            timestamp: date,
            planetaryHour: planetaryHour,
            moonSign: moonSign,
            moonDegree: moonDegree,
            moonPhase: moonPhase,
            isVoidOfCourse: isVoid,
            keyTransits: keyTransits
        )
    }

    // MARK: - Data Model

    struct CosmicEvent {
        let title: String
        let startDate: Date
        let endDate: Date
        let location: String?
        let planetaryHour: String
        let moonPhase: String
        let moonSign: String
        let isVoidOfCourse: Bool
        let keyTransits: [String]  // e.g. "Mars square Saturn (exact)"
    }

    // MARK: - Authorization

    func requestAccess() async -> Bool {
        guard !hasFullAccess() else {
            isAuthorized = true
            return true
        }

        do {
            let granted = try await eventStore.requestFullAccessToEvents()
            isAuthorized = granted
            return granted
        } catch {
            return false
        }
    }

    func hasFullAccess() -> Bool {
        let status = EKEventStore.authorizationStatus(for: .event)
        if #available(iOS 17.0, *) {
            return status == .fullAccess
        } else {
            return status == .authorized
        }
    }

    // MARK: - Event Scanning

    /// Scan the user's calendar for the next N days.
    func scanUpcomingEvents(days: Int = 7) async -> [CosmicEvent] {
        guard await requestAccess() else { return [] }
        let ekEvents = upcomingEvents(days: days)

        var cosmicEvents: [CosmicEvent] = []

        for event in ekEvents {
            // Skip all-day events (less precise cosmic timing)
            guard !event.isAllDay else { continue }

            let cosmic = await analyzeEvent(title: event.title ?? "Untitled",
                                            start: event.startDate,
                                            end: event.endDate,
                                            location: event.location)
            cosmicEvents.append(cosmic)
        }

        return cosmicEvents
    }

    // MARK: - Cosmic Analysis per Event

    private func analyzeEvent(title: String, start: Date, end: Date, location: String?) async -> CosmicEvent {
        // Calculate planetary positions at event time
        var planetaryHour = "Unknown"
        var moonPhase = "Unknown"
        var moonSign = "Unknown"
        var isVoid = false
        var keyTransits: [String] = []

        if let transits = try? await EphemerisEngine.shared.calculateCurrentTransits(date: start) {
            // Moon sign
            if let moon = transits.first(where: { $0.name == "Moon" }) {
                moonSign = moon.sign
            }

            // Moon phase (Sun-Moon elongation)
            if let sun = transits.first(where: { $0.name == "Sun" }),
               let moon = transits.first(where: { $0.name == "Moon" }),
               let sunDeg = sun.absoluteDegree,
               let moonDeg = moon.absoluteDegree {
                var elongation = moonDeg - sunDeg
                if elongation < 0 { elongation += 360 }
                moonPhase = phaseName(elongation: elongation)
            }

            // Key transits (hard aspects between slow planets)
            let slowPlanets = ["Saturn", "Jupiter", "Uranus", "Neptune", "Pluto", "Mars"]
            for idx in 0..<transits.count {
                for jdx in (idx+1)..<transits.count {
                    let bodyA = transits[idx]
                    let bodyB = transits[jdx]
                    guard slowPlanets.contains(bodyA.name) || slowPlanets.contains(bodyB.name) else { continue }
                    guard let aDeg = bodyA.absoluteDegree, let bDeg = bodyB.absoluteDegree else { continue }

                    var diff = abs(aDeg - bDeg)
                    if diff > 180 { diff = 360 - diff }

                    if diff < 3 { keyTransits.append("\(bodyA.name) conjunct \(bodyB.name)") }
                    else if abs(diff - 90) < 3 { keyTransits.append("\(bodyA.name) square \(bodyB.name)") }
                    else if abs(diff - 180) < 3 { keyTransits.append("\(bodyA.name) opposite \(bodyB.name)") }
                }
            }

            // Void of course check (simplified: Moon has no applying aspects within remaining sign degrees)
            isVoid = checkVoidOfCourse(transits: transits)
        }

        // Planetary hour — uses real sunrise/sunset when location available
        planetaryHour = await chaldeanPlanetaryHour(at: start, latitude: nil, longitude: nil)

        return CosmicEvent(
            title: title,
            startDate: start,
            endDate: end,
            location: location,
            planetaryHour: planetaryHour,
            moonPhase: moonPhase,
            moonSign: moonSign,
            isVoidOfCourse: isVoid,
            keyTransits: keyTransits
        )
    }

    // MARK: - Location-Aware Scanning

    /// Scan with location for accurate planetary hours.
    func scanUpcomingEvents(days: Int = 7, latitude: Double?, longitude: Double?) async -> [CosmicEvent] {
        guard await requestAccess() else { return [] }
        let ekEvents = upcomingEvents(days: days)

        var cosmicEvents: [CosmicEvent] = []

        for event in ekEvents {
            guard !event.isAllDay else { continue }
            let cosmic = await analyzeEvent(title: event.title ?? "Untitled",
                                            start: event.startDate,
                                            end: event.endDate,
                                            location: event.location,
                                            latitude: latitude,
                                            longitude: longitude)
            cosmicEvents.append(cosmic)
        }

        return cosmicEvents
    }

    /// Analyze a single event with location-aware planetary hours.
    private func analyzeEvent(title: String, start: Date, end: Date, location: String?,
                              latitude: Double?, longitude: Double?) async -> CosmicEvent {
        // Re-analyze with location-aware planetary hour
        var planetaryHour = "Unknown"
        var moonPhase = "Unknown"
        var moonSign = "Unknown"
        var isVoid = false
        var keyTransits: [String] = []

        if let transits = try? await EphemerisEngine.shared.calculateCurrentTransits(date: start) {
            if let moon = transits.first(where: { $0.name == "Moon" }) {
                moonSign = moon.sign
            }
            if let sun = transits.first(where: { $0.name == "Sun" }),
               let moon = transits.first(where: { $0.name == "Moon" }),
               let sunDeg = sun.absoluteDegree,
               let moonDeg = moon.absoluteDegree {
                var elongation = moonDeg - sunDeg
                if elongation < 0 { elongation += 360 }
                moonPhase = phaseName(elongation: elongation)
            }
            let slowPlanets = ["Saturn", "Jupiter", "Uranus", "Neptune", "Pluto", "Mars"]
            for idx in 0..<transits.count {
                for jdx in (idx+1)..<transits.count {
                    let bodyA = transits[idx]
                    let bodyB = transits[jdx]
                    guard slowPlanets.contains(bodyA.name) || slowPlanets.contains(bodyB.name) else { continue }
                    guard let aDeg = bodyA.absoluteDegree, let bDeg = bodyB.absoluteDegree else { continue }
                    var diff = abs(aDeg - bDeg)
                    if diff > 180 { diff = 360 - diff }
                    if diff < 3 { keyTransits.append("\(bodyA.name) conjunct \(bodyB.name)") }
                    else if abs(diff - 90) < 3 { keyTransits.append("\(bodyA.name) square \(bodyB.name)") }
                    else if abs(diff - 180) < 3 { keyTransits.append("\(bodyA.name) opposite \(bodyB.name)") }
                }
            }
            isVoid = checkVoidOfCourse(transits: transits)
        }

        planetaryHour = await chaldeanPlanetaryHour(at: start, latitude: latitude, longitude: longitude)

        return CosmicEvent(
            title: title,
            startDate: start,
            endDate: end,
            location: location,
            planetaryHour: planetaryHour,
            moonPhase: moonPhase,
            moonSign: moonSign,
            isVoidOfCourse: isVoid,
            keyTransits: keyTransits
        )
    }

    // MARK: - Context Block for AI

    /// Format upcoming cosmic events for AI system prompt injection.
    func contextBlock(
        days: Int = 7,
        requestIfNeeded: Bool = true,
        includeSensitiveDetails: Bool = true
    ) async -> String? {
        let events: [CosmicEvent]
        if requestIfNeeded {
            events = await scanUpcomingEvents(days: days)
        } else {
            guard hasFullAccess() else { return nil }
            let ekEvents = upcomingEvents(days: days)
            var cosmicEvents: [CosmicEvent] = []

            for event in ekEvents {
                guard !event.isAllDay else { continue }
                let cosmic = await analyzeEvent(
                    title: event.title ?? "Untitled",
                    start: event.startDate,
                    end: event.endDate,
                    location: event.location
                )
                cosmicEvents.append(cosmic)
            }
            events = cosmicEvents
        }

        guard !events.isEmpty else { return nil }

        let formatter = DateFormatter()
        formatter.dateFormat = "EEE MMM d, h:mm a"

        let dayFormatter = DateFormatter()
        dayFormatter.dateFormat = "EEE MMM d"

        var lines: [String] = ["UPCOMING CALENDAR — COSMIC WEATHER:"]

        for event in events.prefix(5) {
            var detail: String
            if includeSensitiveDetails {
                detail = "• \(formatter.string(from: event.startDate)): \"\(event.title)\""
            } else {
                let window = timeBucket(for: event.startDate)
                detail = "• \(dayFormatter.string(from: event.startDate)) (\(window)): upcoming event"
            }
            detail += "\n  Moon in \(event.moonSign) (\(event.moonPhase)), Planetary Hour of \(event.planetaryHour)"
            if event.isVoidOfCourse {
                detail += "\n  ⚠️ VOID-OF-COURSE MOON — avoid initiating new agreements"
            }
            if !event.keyTransits.isEmpty {
                detail += "\n  Active: \(event.keyTransits.joined(separator: ", "))"
            }
            lines.append(detail)
        }

        return lines.joined(separator: "\n")
    }

    // MARK: - Helpers

    private func phaseName(elongation: Double) -> String {
        switch elongation {
        case 0..<45: return "New Moon"
        case 45..<90: return "Waxing Crescent"
        case 90..<135: return "First Quarter"
        case 135..<180: return "Waxing Gibbous"
        case 180..<225: return "Full Moon"
        case 225..<270: return "Waning Gibbous"
        case 270..<315: return "Last Quarter"
        case 315..<360: return "Waning Crescent"
        default: return "Unknown"
        }
    }

    private func checkVoidOfCourse(transits: [PlanetPlacement]) -> Bool {
        guard let moon = transits.first(where: { $0.name == "Moon" }),
              let moonDeg = moon.absoluteDegree else { return false }

        let remainingDegrees = 30.0 - moon.degree
        let aspectAngles: [Double] = [0, 60, 90, 120, 180]

        for planet in transits where planet.name != "Moon" {
            guard let pDeg = planet.absoluteDegree else { continue }
            for offset in stride(from: 0.5, through: remainingDegrees, by: 1.0) {
                let futureMoon = moonDeg + offset
                var diff = abs(futureMoon - pDeg)
                if diff > 180 { diff = 360 - diff }
                for angle in aspectAngles {
                    if abs(diff - angle) <= 8 { return false }
                }
            }
        }
        return true
    }

    private func upcomingEvents(days: Int) -> [EKEvent] {
        let now = Date()
        let calendar = Calendar.current
        guard let endDate = calendar.date(byAdding: .day, value: days, to: now) else { return [] }

        let predicate = eventStore.predicateForEvents(withStart: now, end: endDate, calendars: nil)
        return eventStore.events(matching: predicate)
    }

    private func timeBucket(for date: Date) -> String {
        let hour = Calendar.current.component(.hour, from: date)
        switch hour {
        case 5..<12:
            return "morning"
        case 12..<17:
            return "afternoon"
        case 17..<22:
            return "evening"
        default:
            return "night"
        }
    }

    /// Chaldean planetary hour using real sunrise/sunset when coordinates available.
    /// The astrological day begins at SUNRISE, not midnight.
    /// Each "hour" = 1/12 of daylight (day hours) or 1/12 of night (night hours).
    private func chaldeanPlanetaryHour(at date: Date, latitude: Double?, longitude: Double?) async -> String {
        let calendar = Calendar.current
        let weekday = calendar.component(.weekday, from: date)

        let chaldean = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        let dayRulers = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        let dayRuler = dayRulers[weekday - 1]
        guard let startIdx = chaldean.firstIndex(of: dayRuler) else { return "Unknown" }

        // Try to use real sunrise/sunset from Swiss Ephemeris
        if let lat = latitude, let lon = longitude,
           let solar = try? await EphemerisEngine.shared.calculateSunriseSunset(
               latitude: lat, longitude: lon, date: date
           ) {
            let sunrise = solar.sunrise
            let sunset = solar.sunset

            let isDaytime = date >= sunrise && date < sunset
            let periodStart = isDaytime ? sunrise : sunset
            let periodDuration = isDaytime ? solar.daylightMinutes : solar.nighttimeMinutes
            let hourDuration = periodDuration / 12.0

            let minutesIntoPeriod = date.timeIntervalSince(periodStart) / 60.0
            let hourNum = max(0, min(11, Int(minutesIntoPeriod / hourDuration)))
            let offset = isDaytime ? hourNum : hourNum + 12

            return chaldean[(startIdx + offset) % 7]
        }

        // Fallback: fixed 6 AM / 6 PM (only when no location data)
        let hour = calendar.component(.hour, from: date)
        let minute = calendar.component(.minute, from: date)
        let totalMins = hour * 60 + minute
        let isDaytime = totalMins >= 360 && totalMins < 1080
        let minsIntoPeriod = isDaytime ? totalMins - 360 : (totalMins >= 1080 ? totalMins - 1080 : totalMins + 360)
        let hourNum = minsIntoPeriod / 60
        let offset = isDaytime ? hourNum : hourNum + 12

        return chaldean[(startIdx + offset) % 7]
    }
}
