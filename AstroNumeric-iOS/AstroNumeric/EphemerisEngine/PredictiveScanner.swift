// PredictiveScanner.swift
// Future transit root-finder — steps forward through time to find exact partile (0°00') aspects.
// Uses EphemerisEngine to calculate ephemeris data for future dates.

import Foundation

actor PredictiveScanner {
    static let shared = PredictiveScanner()
    
    private init() {}
    
    // MARK: - Data Model
    
    struct FutureTransit: Codable {
        let transitPlanet: String
        let natalPlanet: String
        let aspectName: String
        let exactDate: Date
        let orb: Double            // degrees of orb at exactitude
        let isApplying: Bool       // approaching or separating
        let significance: String   // "major" or "minor"
    }
    
    // MARK: - Public API
    
    /// Find all exact transit-to-natal aspects within the next N days.
    /// Uses 3-pass refinement: daily → hourly → per-minute for sub-degree precision.
    func findExactTransits(profile: Profile, daysAhead: Int = 60) async throws -> [FutureTransit] {
        // Get natal planet positions (fixed)
        guard let natalChart = try? await EphemerisEngine.shared.calculateNatalChart(profile: profile) else {
            return []
        }
        
        let natalPlanets = natalChart.planets.compactMap { p -> (name: String, degree: Double)? in
            guard let deg = p.absoluteDegree else { return nil }
            return (p.name, deg)
        }
        
        let aspectDefs: [(name: String, angle: Double, significance: String)] = [
            ("conjunction", 0, "major"),
            ("opposition", 180, "major"),
            ("trine", 120, "major"),
            ("square", 90, "major"),
            ("sextile", 60, "minor"),
        ]
        
        // Only scan outer/slow planets (inner planets move too fast to be meaningful)
        let transitPlanetIDs: [(id: Int32, name: String)] = [
            (SE_MARS, "Mars"), (SE_JUPITER, "Jupiter"), (SE_SATURN, "Saturn"),
            (SE_URANUS, "Uranus"), (SE_NEPTUNE, "Neptune"), (SE_PLUTO, "Pluto")
        ]
        
        var results: [FutureTransit] = []
        let now = Date()
        
        // Pass 1: Step by day to find windows where aspects are forming
        for dayOffset in 0..<daysAhead {
            guard let scanDate = Calendar.current.date(byAdding: .day, value: dayOffset, to: now) else { continue }
            
            // CRITICAL: Yield to let UI transit calculations through the actor queue.
            // The Swiss Ephemeris C-library uses global buffers — the actor serializes all calls.
            // Without yield, a 60-day scan starves the UI for seconds.
            await Task.yield()
            
            let transitPositions = try calculatePositions(at: scanDate, planets: transitPlanetIDs)
            
            for transit in transitPositions {
                for natal in natalPlanets {
                    guard transit.name != natal.name else { continue }
                    
                    var diff = abs(transit.degree - natal.degree)
                    if diff > 180 { diff = 360 - diff }
                    
                    for aspect in aspectDefs {
                        let orb = abs(diff - aspect.angle)
                        if orb <= 1.5 {
                            // Pass 2: Refine to the hour
                            if let exactDate = try? await refineToExact(
                                transitPlanetID: transit.id,
                                transitPlanetName: transit.name,
                                natalDegree: natal.degree,
                                aspectAngle: aspect.angle,
                                startDate: scanDate,
                                hoursRange: 24
                            ) {
                                // Check for duplicate (same pair + same aspect + within 24h)
                                let isDuplicate = results.contains { existing in
                                    existing.transitPlanet == transit.name &&
                                    existing.natalPlanet == natal.name &&
                                    existing.aspectName == aspect.name &&
                                    abs(existing.exactDate.timeIntervalSince(exactDate)) < 86400
                                }
                                
                                if !isDuplicate {
                                    // Check if applying or separating
                                    let nextDay = Calendar.current.date(byAdding: .day, value: 1, to: exactDate)!
                                    let futurePositions = try calculatePositions(at: nextDay, planets: [(transit.id, transit.name)])
                                    let futureDiff = {
                                        var d = abs((futurePositions.first?.degree ?? 0) - natal.degree)
                                        if d > 180 { d = 360 - d }
                                        return abs(d - aspect.angle)
                                    }()
                                    
                                    results.append(FutureTransit(
                                        transitPlanet: transit.name,
                                        natalPlanet: natal.name,
                                        aspectName: aspect.name,
                                        exactDate: exactDate,
                                        orb: orb,
                                        isApplying: futureDiff > orb,
                                        significance: aspect.significance
                                    ))
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Sort by date
        return results.sorted { $0.exactDate < $1.exactDate }
    }
    
    // MARK: - Context Block for AI
    
    /// Format upcoming transits for AI system prompt injection.
    func contextBlock(profile: Profile, daysAhead: Int = 30) async -> String? {
        guard let transits = try? await findExactTransits(profile: profile, daysAhead: daysAhead),
              !transits.isEmpty else { return nil }
        
        let formatter = DateFormatter()
        formatter.dateFormat = "EEE, MMM d 'at' h:mm a"
        
        var lines: [String] = ["UPCOMING EXACT TRANSITS (next \(daysAhead) days):"]
        
        for transit in transits.prefix(10) {
            let arrow = transit.isApplying ? "→" : "←"
            let significance = transit.significance == "major" ? "⚡" : "·"
            lines.append("  \(significance) \(transit.transitPlanet) \(transit.aspectName) natal \(transit.natalPlanet) \(arrow) \(formatter.string(from: transit.exactDate))")
        }
        
        return lines.joined(separator: "\n")
    }
    
    // MARK: - Private
    
    private struct TransitPosition {
        let id: Int32
        let name: String
        let degree: Double
    }
    
    private func calculatePositions(at date: Date, planets: [(id: Int32, name: String)]) throws -> [TransitPosition] {
        let calendar = Calendar.current
        let components = calendar.dateComponents(in: TimeZone(identifier: "UTC")!, from: date)
        let jd = swe_julday(
            Int32(components.year ?? 2026),
            Int32(components.month ?? 1),
            Int32(components.day ?? 1),
            Double(components.hour ?? 12) + Double(components.minute ?? 0) / 60.0,
            SE_GREG_CAL
        )
        
        return planets.compactMap { planet in
            var xx = [Double](repeating: 0, count: 6)
            var serr = [CChar](repeating: 0, count: 256)
            let rc = swe_calc_ut(jd, planet.id, SEFLG_SWIEPH | SEFLG_SPEED, &xx, &serr)
            guard rc >= 0 else { return nil }
            return TransitPosition(id: planet.id, name: planet.name, degree: xx[0])
        }
    }
    
    /// Refine a transit aspect to the nearest minute by stepping through hours then minutes.
    /// IMPORTANT: This function yields periodically to prevent actor starvation.
    private func refineToExact(
        transitPlanetID: Int32,
        transitPlanetName: String,
        natalDegree: Double,
        aspectAngle: Double,
        startDate: Date,
        hoursRange: Int
    ) async throws -> Date? {
        var bestDate = startDate
        var bestOrb = 999.0
        
        // Step by hour
        for hourOffset in 0..<hoursRange {
            guard let checkDate = Calendar.current.date(byAdding: .hour, value: hourOffset, to: startDate) else { continue }
            let positions = try calculatePositions(at: checkDate, planets: [(transitPlanetID, transitPlanetName)])
            guard let pos = positions.first else { continue }
            
            var diff = abs(pos.degree - natalDegree)
            if diff > 180 { diff = 360 - diff }
            let orb = abs(diff - aspectAngle)
            
            if orb < bestOrb {
                bestOrb = orb
                bestDate = checkDate
            }
            
            // Yield every 6 hours to prevent actor starvation
            if hourOffset % 6 == 0 { await Task.yield() }
        }
        
        // Step by minute around the best hour
        let minuteStart = Calendar.current.date(byAdding: .minute, value: -30, to: bestDate) ?? bestDate
        for minOffset in 0..<60 {
            guard let checkDate = Calendar.current.date(byAdding: .minute, value: minOffset, to: minuteStart) else { continue }
            let positions = try calculatePositions(at: checkDate, planets: [(transitPlanetID, transitPlanetName)])
            guard let pos = positions.first else { continue }
            
            var diff = abs(pos.degree - natalDegree)
            if diff > 180 { diff = 360 - diff }
            let orb = abs(diff - aspectAngle)
            
            if orb < bestOrb {
                bestOrb = orb
                bestDate = checkDate
            }
            
            // Yield every 15 minutes to prevent actor starvation
            if minOffset % 15 == 0 { await Task.yield() }
        }
        
        return bestOrb < 1.0 ? bestDate : nil
    }
}
