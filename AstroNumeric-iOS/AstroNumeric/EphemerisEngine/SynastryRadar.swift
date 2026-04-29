// SynastryRadar.swift
// Scans today's transits against saved contacts' natal charts.
// Provides "Social Weather" alerts for volatile interpersonal energy.

import Foundation

actor SynastryRadar {
    static let shared = SynastryRadar()
    
    private init() {}
    
    // MARK: - Data Model
    
    struct SocialAlert {
        let personName: String
        let relationshipType: String
        let transitPlanet: String
        let aspectName: String
        let natalPlanet: String
        let severity: Severity
        let advice: String
        
        enum Severity: String {
            case calm = "calm"
            case moderate = "moderate"
            case volatile = "volatile"
        }
    }
    
    // MARK: - Public API
    
    /// Scan today's transits against all saved relationships.
    /// Uses noon charts (12:00 UTC) for contacts without birth times.
    func scanSocialWeather() async -> [SocialAlert] {
        // Load saved relationships
        let relationships = loadRelationships()
        guard !relationships.isEmpty else { return [] }
        
        // Get today's transits
        guard let todayTransits = try? await EphemerisEngine.shared.calculateCurrentTransits() else {
            return []
        }
        
        var alerts: [SocialAlert] = []
        
        for rel in relationships {
            // Calculate noon chart for the contact's DOB
            guard let natalPlanets = noonChartPlanets(dob: rel.personBDOB) else { continue }
            
            // Check volatile transits against their natal chart
            let volatilePlanets = ["Mars", "Saturn", "Uranus", "Pluto"]
            let hardAspects: [(name: String, angle: Double, orb: Double)] = [
                ("conjunction", 0, 6),
                ("opposition", 180, 6),
                ("square", 90, 5),
            ]
            
            for transit in todayTransits {
                guard volatilePlanets.contains(transit.name) else { continue }
                guard let transitDeg = transit.absoluteDegree else { continue }
                
                for natal in natalPlanets {
                    var diff = abs(transitDeg - natal.degree)
                    if diff > 180 { diff = 360 - diff }
                    
                    for aspect in hardAspects {
                        let orb = abs(diff - aspect.angle)
                        if orb <= aspect.orb {
                            let severity = classifySeverity(
                                transitPlanet: transit.name,
                                aspectName: aspect.name,
                                natalPlanet: natal.name,
                                orb: orb
                            )
                            
                            let advice = generateAdvice(
                                personName: rel.personBName,
                                transitPlanet: transit.name,
                                aspectName: aspect.name,
                                natalPlanet: natal.name,
                                severity: severity,
                                relType: rel.type.rawValue
                            )
                            
                            alerts.append(SocialAlert(
                                personName: rel.personBName,
                                relationshipType: rel.type.rawValue,
                                transitPlanet: transit.name,
                                aspectName: aspect.name,
                                natalPlanet: natal.name,
                                severity: severity,
                                advice: advice
                            ))
                        }
                    }
                }
            }
        }
        
        // Sort volatile first
        return alerts.sorted { a, b in
            let order: [SocialAlert.Severity] = [.volatile, .moderate, .calm]
            let aIdx = order.firstIndex(of: a.severity) ?? 2
            let bIdx = order.firstIndex(of: b.severity) ?? 2
            return aIdx < bIdx
        }
    }
    
    // MARK: - Context Block for AI
    
    /// Format social weather for AI system prompt injection.
    func contextBlock() async -> String? {
        let alerts = await scanSocialWeather()
        guard !alerts.isEmpty else { return nil }
        
        var lines: [String] = ["SOCIAL WEATHER (contacts' cosmic stress):"]
        
        for alert in alerts.prefix(6) {
            let icon: String
            switch alert.severity {
            case .volatile: icon = "🚨"
            case .moderate: icon = "⚡"
            case .calm: icon = "·"
            }
            lines.append("  \(icon) \(alert.personName) (\(alert.relationshipType)): Transit \(alert.transitPlanet) \(alert.aspectName) their natal \(alert.natalPlanet)")
            lines.append("    → \(alert.advice)")
        }
        
        return lines.joined(separator: "\n")
    }
    
    // MARK: - Noon Chart Calculation
    
    private static let signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    private func noonChartPlanets(dob: String) -> [(name: String, degree: Double)]? {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        guard let date = formatter.date(from: dob) else { return nil }
        
        let calendar = Calendar.current
        let components = calendar.dateComponents([.year, .month, .day], from: date)
        
        // Noon UTC
        let jd = swe_julday(
            Int32(components.year ?? 2000),
            Int32(components.month ?? 1),
            Int32(components.day ?? 1),
            12.0,
            SE_GREG_CAL
        )
        
        let planetIDs: [(id: Int32, name: String)] = [
            (SE_SUN, "Sun"), (SE_MOON, "Moon"), (SE_MERCURY, "Mercury"),
            (SE_VENUS, "Venus"), (SE_MARS, "Mars"), (SE_JUPITER, "Jupiter"),
            (SE_SATURN, "Saturn"), (SE_URANUS, "Uranus"), (SE_NEPTUNE, "Neptune"),
            (SE_PLUTO, "Pluto")
        ]
        
        let iflag = SEFLG_SWIEPH | SEFLG_SPEED
        var results: [(name: String, degree: Double)] = []
        
        for planet in planetIDs {
            var xx = [Double](repeating: 0, count: 6)
            var serr = [CChar](repeating: 0, count: 256)
            let rc = swe_calc_ut(jd, planet.id, iflag, &xx, &serr)
            if rc >= 0 {
                results.append((planet.name, xx[0]))
            }
        }
        
        return results.isEmpty ? nil : results
    }
    
    // MARK: - Severity Classification
    
    private func classifySeverity(transitPlanet: String, aspectName: String, natalPlanet: String, orb: Double) -> SocialAlert.Severity {
        // Volatile: Mars or Uranus in hard aspect to personal planets with tight orb
        let personalPlanets = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
        let isPersonal = personalPlanets.contains(natalPlanet)
        let isTight = orb < 2.0
        
        if (transitPlanet == "Uranus" || transitPlanet == "Mars") && isPersonal && isTight {
            return .volatile
        }
        if transitPlanet == "Saturn" && isPersonal && isTight {
            return .moderate
        }
        if aspectName == "square" || aspectName == "opposition" {
            return orb < 3.0 ? .moderate : .calm
        }
        return .calm
    }
    
    // MARK: - Advice Generator
    
    private func generateAdvice(personName: String, transitPlanet: String, aspectName: String, natalPlanet: String, severity: SocialAlert.Severity, relType: String) -> String {
        switch (transitPlanet, severity) {
        case ("Mars", .volatile):
            return "\(personName) may be unusually aggressive or impatient. Avoid confrontation."
        case ("Uranus", .volatile):
            return "\(personName) is prone to erratic decisions. Don't rely on commitments made today."
        case ("Saturn", .moderate):
            return "\(personName) may feel burdened or pessimistic. Offer support, not pressure."
        case ("Pluto", _):
            return "\(personName) may be dealing with intense power dynamics. Tread carefully."
        case (_, .volatile):
            return "High-tension energy around \(personName). Keep interactions minimal."
        case (_, .moderate):
            return "Some stress around \(personName). Be patient and diplomatic."
        default:
            return "Minor cosmic tension. Normal interactions should be fine."
        }
    }
    
    // MARK: - Load Relationships
    
    private func loadRelationships() -> [SavedRelationship] {
        guard let data = UserDefaults.standard.data(forKey: "savedRelationships"),
              let relationships = try? JSONDecoder().decode([SavedRelationship].self, from: data) else {
            return []
        }
        return relationships
    }
}
