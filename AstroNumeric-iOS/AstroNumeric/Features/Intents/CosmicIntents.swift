import AppIntents
import Foundation
import CoreLocation

// MARK: - Planetary Hour Intent

struct PlanetaryHourIntent: AppIntent {
    static var title: LocalizedStringResource = "Current Planetary Hour"
    static var description: IntentDescription = "Returns which planet rules the current hour based on the Chaldean order and real sunrise/sunset."
    
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let result = await computePlanetaryHour()
        return .result(dialog: "\(result.emoji) The current planetary hour is ruled by \(result.planet). \(result.meaning)")
    }
    
    static var openAppWhenRun: Bool = false
    
    /// Chaldean order of planets (traditional 7)
    private static let chaldeanOrder = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    
    /// Day rulers (Sunday=Sun, Monday=Moon, etc.)
    private static let dayRulers = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    private func computePlanetaryHour() async -> (planet: String, emoji: String, meaning: String) {
        let now = Date()
        let calendar = Calendar.current
        
        // Get the day of week (1=Sunday, 7=Saturday)
        let weekday = calendar.component(.weekday, from: now)
        let dayRuler = Self.dayRulers[weekday - 1]
        
        guard let dayRulerIndex = Self.chaldeanOrder.firstIndex(of: dayRuler) else {
            return ("Unknown", "❓", "")
        }
        
        // Try to get real sunrise/sunset from user's location
        var sunriseDate: Date?
        var sunsetDate: Date?
        var daylightMins = 720.0  // fallback: 12 hours
        var nighttimeMins = 720.0
        
        if let location = await getCurrentLocation() {
            do {
                let solar = try await EphemerisEngine.shared.calculateSunriseSunset(
                    latitude: location.coordinate.latitude,
                    longitude: location.coordinate.longitude,
                    date: now
                )
                sunriseDate = solar.sunrise
                sunsetDate = solar.sunset
                daylightMins = solar.daylightMinutes
                nighttimeMins = solar.nighttimeMinutes
            } catch {
                // Fall through to fixed times
            }
        }
        
        // Determine if daytime or nighttime using real or fallback sunrise/sunset
        let sunrise = sunriseDate ?? calendar.date(bySettingHour: 6, minute: 0, second: 0, of: now)!
        let sunset = sunsetDate ?? calendar.date(bySettingHour: 18, minute: 0, second: 0, of: now)!
        
        let isDaytime = now >= sunrise && now < sunset
        
        // Calculate which planetary hour we're in
        let minutesSinceEvent: Double
        let hourDuration: Double
        
        if isDaytime {
            minutesSinceEvent = now.timeIntervalSince(sunrise) / 60.0
            hourDuration = daylightMins / 12.0  // each daytime hour
        } else {
            if now >= sunset {
                minutesSinceEvent = now.timeIntervalSince(sunset) / 60.0
            } else {
                // Before sunrise — calculate from previous sunset (approx)
                let prevSunset = calendar.date(byAdding: .day, value: -1, to: sunset) ?? sunset
                minutesSinceEvent = now.timeIntervalSince(prevSunset) / 60.0
            }
            hourDuration = nighttimeMins / 12.0  // each nighttime hour
        }
        
        let planetaryHourNumber = min(Int(minutesSinceEvent / hourDuration), 11)
        
        // Offset into Chaldean sequence
        let offset = isDaytime ? planetaryHourNumber : planetaryHourNumber + 12
        let planetIndex = (dayRulerIndex + offset) % 7
        let planet = Self.chaldeanOrder[planetIndex]
        
        let emojis: [String: String] = [
            "Sun": "☀️", "Moon": "🌙", "Mars": "♂️", "Mercury": "☿️",
            "Jupiter": "♃", "Venus": "♀️", "Saturn": "♄"
        ]
        
        let meanings: [String: String] = [
            "Sun": "Good for leadership, vitality, and creative projects.",
            "Moon": "Good for intuition, emotions, and nurturing.",
            "Mars": "Good for action, courage, and physical activity.",
            "Mercury": "Good for communication, learning, and travel.",
            "Jupiter": "Good for expansion, luck, and generosity.",
            "Venus": "Good for love, beauty, and artistic pursuits.",
            "Saturn": "Good for discipline, structure, and long-term planning."
        ]
        
        return (planet, emojis[planet] ?? "🌟", meanings[planet] ?? "")
    }
    
    /// Get user's current location (one-shot).
    private func getCurrentLocation() async -> CLLocation? {
        let manager = CLLocationManager()
        guard manager.authorizationStatus == .authorizedWhenInUse || manager.authorizationStatus == .authorizedAlways else {
            return nil
        }
        return manager.location  // last known location (fast, no prompt)
    }
}

// MARK: - Void of Course Moon Intent

struct VoidOfCourseMoonIntent: AppIntent {
    static var title: LocalizedStringResource = "Is the Moon Void of Course?"
    static var description: IntentDescription = "Checks if the Moon is currently void-of-course (no major aspects before changing signs)."
    
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let result = try await checkVoidOfCourse()
        if result.isVoid {
            return .result(dialog: "🌑 The Moon IS void-of-course right now in \(result.moonSign). \(result.advice)")
        } else {
            return .result(dialog: "🌕 The Moon is NOT void-of-course. It's active in \(result.moonSign) with aspects still to make. Proceed with plans normally.")
        }
    }
    
    static var openAppWhenRun: Bool = false
    
    private func checkVoidOfCourse() async throws -> (isVoid: Bool, moonSign: String, advice: String) {
        let transits = try await EphemerisEngine.shared.calculateCurrentTransits()
        
        guard let moon = transits.first(where: { $0.name == "Moon" }) else {
            return (false, "unknown", "")
        }
        
        let moonSign = moon.sign
        let moonDegree = moon.degree
        
        // Check if the Moon makes any major aspects to other planets
        // within the remaining degrees of its current sign
        let remainingDegrees = 30.0 - moonDegree
        
        // Major aspect angles
        let aspectAngles: [Double] = [0, 60, 90, 120, 150, 180]
        let orb = 8.0
        
        guard let moonAbsDeg = moon.absoluteDegree else {
            return (false, moonSign, "")
        }
        
        var hasUpcomingAspect = false
        
        for planet in transits where planet.name != "Moon" {
            guard let planetAbsDeg = planet.absoluteDegree else { continue }
            
            // Check future positions of the Moon (scan ahead in 1° increments)
            for offset in stride(from: 0.0, through: remainingDegrees, by: 1.0) {
                let futureMoonDeg = moonAbsDeg + offset
                var diff = abs(futureMoonDeg - planetAbsDeg)
                if diff > 180 { diff = 360 - diff }
                
                for angle in aspectAngles {
                    if abs(diff - angle) <= orb {
                        if offset > 0.5 { // Must be an upcoming aspect, not a separating one
                            hasUpcomingAspect = true
                            break
                        }
                    }
                }
                if hasUpcomingAspect { break }
            }
            if hasUpcomingAspect { break }
        }
        
        let isVoid = !hasUpcomingAspect
        let advice = isVoid
            ? "Avoid starting new projects, signing contracts, or making major purchases. Great for rest, meditation, and routine tasks."
            : ""
        
        return (isVoid, moonSign, advice)
    }
}

// MARK: - Moon Phase Intent

struct MoonPhaseIntent: AppIntent {
    static var title: LocalizedStringResource = "Current Moon Phase"
    static var description: IntentDescription = "Returns the current moon phase, illumination percentage, and sign."
    
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let result = try await computeMoonPhase()
        return .result(dialog: "\(result.emoji) \(result.phase) (\(result.illumination)% illuminated) — Moon in \(result.sign). \(result.meaning)")
    }
    
    static var openAppWhenRun: Bool = false
    
    private func computeMoonPhase() async throws -> (phase: String, emoji: String, illumination: Int, sign: String, meaning: String) {
        let transits = try await EphemerisEngine.shared.calculateCurrentTransits()
        
        guard let sun = transits.first(where: { $0.name == "Sun" }),
              let moon = transits.first(where: { $0.name == "Moon" }),
              let sunDeg = sun.absoluteDegree,
              let moonDeg = moon.absoluteDegree else {
            return ("Unknown", "❓", 0, "unknown", "")
        }
        
        // Calculate the elongation (angular distance Moon - Sun)
        var elongation = moonDeg - sunDeg
        if elongation < 0 { elongation += 360 }
        
        // Illumination (approximate)
        let illumination = Int((1 - cos(elongation * .pi / 180)) / 2 * 100)
        
        // Determine phase name
        let (phase, emoji, meaning) = phaseInfo(elongation: elongation)
        
        return (phase, emoji, illumination, moon.sign, meaning)
    }
    
    private func phaseInfo(elongation: Double) -> (String, String, String) {
        switch elongation {
        case 0..<11.25:
            return ("New Moon", "🌑", "Time for new beginnings, setting intentions, and planting seeds.")
        case 11.25..<78.75:
            return ("Waxing Crescent", "🌒", "Build momentum. Take small steps toward your goals.")
        case 78.75..<101.25:
            return ("First Quarter", "🌓", "Decision time. Overcome obstacles and commit to action.")
        case 101.25..<168.75:
            return ("Waxing Gibbous", "🌔", "Refine and adjust. Almost there — stay focused.")
        case 168.75..<191.25:
            return ("Full Moon", "🌕", "Peak energy. Manifestation, celebration, and revelation.")
        case 191.25..<258.75:
            return ("Waning Gibbous", "🌖", "Gratitude and sharing. Distribute what you've gained.")
        case 258.75..<281.25:
            return ("Last Quarter", "🌗", "Release and let go. Clear what no longer serves you.")
        case 281.25..<360:
            return ("Waning Crescent", "🌘", "Rest, reflect, and prepare for the next cycle.")
        default:
            return ("Unknown", "🌑", "")
        }
    }
}

// MARK: - App Shortcuts Provider

struct CosmicShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: PlanetaryHourIntent(),
            phrases: [
                "What's the current planetary hour in \(.applicationName)?",
                "Planetary hour \(.applicationName)",
                "Which planet rules this hour in \(.applicationName)?"
            ],
            shortTitle: "Planetary Hour",
            systemImageName: "clock.badge.questionmark"
        )
        AppShortcut(
            intent: VoidOfCourseMoonIntent(),
            phrases: [
                "Is the moon void of course in \(.applicationName)?",
                "Void of course \(.applicationName)",
                "Can I sign a contract right now \(.applicationName)?"
            ],
            shortTitle: "Void of Course",
            systemImageName: "moon.zzz"
        )
        AppShortcut(
            intent: MoonPhaseIntent(),
            phrases: [
                "What's the moon phase in \(.applicationName)?",
                "Moon phase \(.applicationName)",
                "What moon are we in \(.applicationName)?"
            ],
            shortTitle: "Moon Phase",
            systemImageName: "moon.stars"
        )
    }
}
