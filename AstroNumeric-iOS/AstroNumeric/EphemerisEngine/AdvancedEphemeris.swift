// AdvancedEphemeris.swift
// Secondary Progressions & Solar Returns — macro life-chapter calculations.
// Uses the ancient "1 day = 1 year" formula via Swiss Ephemeris.

import Foundation

actor AdvancedEphemeris {
    static let shared = AdvancedEphemeris()
    
    private init() {}
    
    // MARK: - Data Models
    
    struct ProgressedChart {
        let progressedDate: Date     // The actual "progressed" date (birth + age-in-days)
        let ageYears: Double
        let planets: [ProgressedPlanet]
    }
    
    struct ProgressedPlanet {
        let name: String
        let sign: String
        let degree: Double
        let absoluteDegree: Double
        let retrograde: Bool
    }
    
    // MARK: - Secondary Progressions
    
    /// Calculate secondary progressions for a profile.
    /// Formula: age in years → same number of days after birth.
    /// e.g. 30.5 years old → planet positions 30.5 days after birth.
    func calculateProgressions(profile: Profile) async throws -> ProgressedChart {
        guard let dobString = Optional(profile.dateOfBirth),
              let _ = profile.latitude, let _ = profile.longitude,
              let tz = profile.timezone else {
            throw EphemerisError.missingLocation
        }
        
        // Parse birth date
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        guard let birthDate = formatter.date(from: dobString) else {
            throw EphemerisError.invalidDate
        }
        
        // Calculate exact age in years (fractional)
        let now = Date()
        let ageSeconds = now.timeIntervalSince(birthDate)
        let ageYears = ageSeconds / (365.25 * 24 * 3600)
        
        // The progressed date = birth date + age-in-days
        // 1 year of life = 1 day of progression
        let progressedSeconds = ageYears * 24 * 3600  // age-in-years → days in seconds
        guard let progressedDate = Calendar.current.date(byAdding: .second, value: Int(progressedSeconds), to: birthDate) else {
            throw EphemerisError.invalidDate
        }
        
        // Parse birth time
        let timeParts = (profile.timeOfBirth ?? "12:00:00").split(separator: ":")
        let birthHour = Double(timeParts[safe: 0] ?? "12") ?? 12.0
        let birthMinute = Double(timeParts[safe: 1] ?? "0") ?? 0.0
        let birthSecond = Double(timeParts[safe: 2] ?? "0") ?? 0.0
        let localHour = birthHour + birthMinute / 60.0 + birthSecond / 3600.0
        
        // Convert to UT
        let utHour: Double
        if let timezone = TimeZone(identifier: tz) {
            let offsetHours = Double(timezone.secondsFromGMT()) / 3600.0
            utHour = localHour - offsetHours
        } else {
            utHour = localHour
        }
        
        // Get calendar components for the progressed date
        let calendar = Calendar.current
        let progComponents = calendar.dateComponents([.year, .month, .day], from: progressedDate)
        
        // Calculate Julian Day for progressed date (using birth time)
        let jd = swe_julday(
            Int32(progComponents.year ?? 2026),
            Int32(progComponents.month ?? 1),
            Int32(progComponents.day ?? 1),
            utHour,
            SE_GREG_CAL
        )
        
        // Calculate planet positions at progressed JD
        let planets = calculateProgressedPlanets(julianDay: jd)
        
        return ProgressedChart(
            progressedDate: progressedDate,
            ageYears: ageYears,
            planets: planets
        )
    }
    
    // MARK: - Context Block for AI
    
    /// Generate a context block describing the user's secondary progressions.
    func contextBlock(profile: Profile) async -> String? {
        guard let chart = try? await calculateProgressions(profile: profile) else { return nil }
        
        var lines: [String] = ["SECONDARY PROGRESSIONS (Life Era Context):"]
        lines.append("  Age: \(String(format: "%.1f", chart.ageYears)) years")
        
        // Focus on the most important progressed bodies
        let keyPlanets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Ascendant"]
        
        for planet in chart.planets where keyPlanets.contains(planet.name) {
            var line = "  - Progressed \(planet.name): \(planet.sign) \(String(format: "%.1f", planet.degree))°"
            if planet.retrograde { line += " (Rx)" }
            lines.append(line)
        }
        
        // Special note for Progressed Moon (changes signs ~every 2.5 years)
        if let pMoon = chart.planets.first(where: { $0.name == "Moon" }) {
            lines.append("  → Progressed Moon in \(pMoon.sign) defines your current emotional era.")
        }
        
        // Special note for Progressed Sun (changes signs ~every 30 years)
        if let pSun = chart.planets.first(where: { $0.name == "Sun" }) {
            lines.append("  → Progressed Sun in \(pSun.sign) shapes your evolving identity.")
        }
        
        return lines.joined(separator: "\n")
    }
    
    // MARK: - Private
    
    private static let signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    private static let planets: [(id: Int32, name: String)] = [
        (SE_SUN, "Sun"), (SE_MOON, "Moon"), (SE_MERCURY, "Mercury"),
        (SE_VENUS, "Venus"), (SE_MARS, "Mars"), (SE_JUPITER, "Jupiter"),
        (SE_SATURN, "Saturn"), (SE_URANUS, "Uranus"), (SE_NEPTUNE, "Neptune"),
        (SE_PLUTO, "Pluto")
    ]
    
    private func calculateProgressedPlanets(julianDay jd: Double) -> [ProgressedPlanet] {
        let iflag = SEFLG_SWIEPH | SEFLG_SPEED
        var results: [ProgressedPlanet] = []
        
        for planet in Self.planets {
            var xx = [Double](repeating: 0, count: 6)
            var serr = [CChar](repeating: 0, count: 256)
            
            let rc = swe_calc_ut(jd, planet.id, iflag, &xx, &serr)
            if rc >= 0 {
                let longitude = xx[0]
                let speed = xx[3]
                let signIndex = Int(longitude / 30.0) % 12
                let degree = longitude.truncatingRemainder(dividingBy: 30.0)
                
                results.append(ProgressedPlanet(
                    name: planet.name,
                    sign: Self.signs[signIndex],
                    degree: degree,
                    absoluteDegree: longitude,
                    retrograde: speed < 0
                ))
            }
        }
        
        return results
    }
}

// MARK: - Safe Array Access

private extension Array {
    subscript(safe index: Int) -> Element? {
        return indices.contains(index) ? self[index] : nil
    }
}

private extension Array where Element == Substring {
    subscript(safe index: Int) -> Substring? {
        return indices.contains(index) ? self[index] : nil
    }
}
