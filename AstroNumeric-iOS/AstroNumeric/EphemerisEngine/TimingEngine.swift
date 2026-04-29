// TimingEngine.swift
// On-device timing advisor — calculates cosmic timing scores using Swiss Ephemeris.
// Replaces the API-dependent timing calculation with fully local math.
// Scores activities using 5 factors: planetary hour, moon phase, VoC, transit-natal aspects, and moon sign element.

import Foundation

actor TimingEngine {
    static let shared = TimingEngine()
    
    private init() {}
    
    // MARK: - Activity–Planet Rulership Map
    
    /// Each activity is ruled by specific planets. A matching planetary hour boosts the score.
    private static let activityRulers: [String: [String]] = [
        "business_meeting":     ["Mercury", "Jupiter"],
        "romance_date":         ["Venus", "Moon"],
        "job_interview":        ["Mercury", "Mars"],
        "creative_work":        ["Venus", "Neptune"],
        "financial_decision":   ["Jupiter", "Saturn"],
        "travel":               ["Mercury", "Jupiter"],
        "signing_contracts":    ["Saturn", "Mercury"],
        "starting_project":     ["Mars", "Jupiter", "Sun"],
        "meditation_spiritual": ["Neptune", "Moon"],
    ]
    
    /// Moon sign elements and their affinity to activities
    private static let signElements: [String: String] = [
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
    ]
    
    /// Activity element affinities (which element favors which activity)
    private static let activityElements: [String: [String]] = [
        "business_meeting":     ["Air", "Earth"],
        "romance_date":         ["Water", "Fire"],
        "job_interview":        ["Air", "Fire"],
        "creative_work":        ["Water", "Fire"],
        "financial_decision":   ["Earth"],
        "travel":               ["Air", "Fire"],
        "signing_contracts":    ["Earth", "Air"],
        "starting_project":     ["Fire"],
        "meditation_spiritual": ["Water"],
    ]
    
    // MARK: - Benefic / Malefic Classification
    
    /// Benefic planets boost transit-natal aspect scores
    private static let beneficPlanets: Set<String> = ["Venus", "Jupiter"]
    /// Malefic planets penalize hard aspects
    private static let maleficPlanets: Set<String> = ["Saturn", "Mars", "Pluto"]
    
    // MARK: - Public API
    
    /// Calculate a cosmic timing score for an activity across multiple days.
    /// Returns a TimingResult matching the UI's expected data model.
    func calculateTiming(activity: String, profile: Profile, daysToScan: Int = 3) async -> TimingResult {
        // Get natal chart for transit-natal aspect scoring
        let natalPlanets = (try? await EphemerisEngine.shared.calculateNatalChart(profile: profile))?.planets ?? []
        
        // Calculate solar times for accurate planetary hours (if location available)
        let solarTimes = try? await EphemerisEngine.shared.calculateSunriseSunset(
            latitude: profile.latitude ?? 0,
            longitude: profile.longitude ?? 0
        )
        
        let calendar = Calendar.current
        let now = Date()
        
        // Scan windows across days
        var allWindows: [ScoredWindow] = []
        
        for dayOffset in 0..<daysToScan {
            guard let day = calendar.date(byAdding: .day, value: dayOffset, to: now) else { continue }
            
            // Scan 12 two-hour windows across the day (6 AM to 6 AM = full cycle)
            for hourSlot in 0..<12 {
                let startHour = 6 + (hourSlot * 2) // Start at 6 AM
                guard var windowStart = calendar.date(bySettingHour: startHour % 24, minute: 0, second: 0, of: day) else { continue }
                
                // If hour wraps past midnight, move to next day
                if startHour >= 24 {
                    windowStart = calendar.date(byAdding: .day, value: 1, to: windowStart) ?? windowStart
                }
                
                let windowEnd = calendar.date(byAdding: .hour, value: 2, to: windowStart) ?? windowStart
                
                // Skip windows that are in the past
                if windowEnd < now { continue }
                
                await Task.yield() // Prevent actor starvation
                
                let result = await scoreWindow(
                    at: windowStart,
                    activity: activity,
                    natalPlanets: natalPlanets,
                    solarTimes: solarTimes,
                    profile: profile
                )
                
                allWindows.append(ScoredWindow(
                    start: windowStart,
                    end: windowEnd,
                    score: result.score.total,
                    factors: result.score,
                    isMercuryRetrograde: result.isMercuryRetrograde
                ))
            }
        }
        
        // Sort by score (highest first)
        allWindows.sort { $0.score > $1.score }
        
        // Overall score = best window's score
        let bestScore = allWindows.first?.score ?? 0.5
        
        // Best times = top 3 windows
        let formatter = DateFormatter()
        formatter.dateFormat = "EEE h:mm a"
        let bestTimes = allWindows.prefix(3).map { window in
            let dayLabel = calendar.isDateInToday(window.start) ? "Today" :
                           calendar.isDateInTomorrow(window.start) ? "Tomorrow" :
                           formatter.string(from: window.start)
            let endFmt = DateFormatter()
            endFmt.dateFormat = "h:mm a"
            let hourRuler = window.factors.planetaryHourName
            return "\(dayLabel) \(formatter.string(from: window.start))–\(endFmt.string(from: window.end)) • \(hourRuler) hour (\(Int(window.score * 100))%)"
        }
        
        // Avoid times = bottom 3 windows that aren't in the past
        let worstWindows = allWindows.suffix(3).reversed()
        let avoidTimes: [String] = worstWindows.compactMap { window in
            let dayLabel = calendar.isDateInToday(window.start) ? "Today" :
                           calendar.isDateInTomorrow(window.start) ? "Tomorrow" :
                           formatter.string(from: window.start)
            let reason = window.factors.worstFactor
            return "\(dayLabel) \(formatter.string(from: window.start)) • \(reason)"
        }
        
        // Tips based on the current cosmic weather
        let tips = generateTips(activity: activity, bestWindow: allWindows.first, allWindows: allWindows)
        
        // Rating text
        let rating = ratingText(score: bestScore, activity: activity)
        
        let dateStr = ISO8601DateFormatter().string(from: now)
        
        return TimingResult(
            activity: activity,
            score: bestScore,
            rating: rating,
            bestTimes: bestTimes,
            avoidTimes: avoidTimes,
            tips: tips,
            generatedAt: dateStr
        )
    }
    
    // MARK: - Window Scoring
    
    private struct ScoredWindow {
        let start: Date
        let end: Date
        let score: Double
        let factors: WindowScore
        let isMercuryRetrograde: Bool
    }
    
    private struct WindowScore {
        let planetaryHourScore: Double   // 0-1
        let moonPhaseScore: Double       // 0-1
        let vocPenalty: Double           // 0 or negative
        let transitNatalScore: Double    // 0-1
        let moonElementScore: Double     // 0-1
        let planetaryHourName: String
        let isVoidOfCourse: Bool
        
        var total: Double {
            let raw = (planetaryHourScore * 0.25) +
                      (moonPhaseScore * 0.20) +
                      (transitNatalScore * 0.25) +
                      (moonElementScore * 0.15) +
                      (0.15 + vocPenalty) // VoC baseline + penalty
            return max(0, min(1, raw))
        }
        
        var worstFactor: String {
            if isVoidOfCourse { return "Moon void-of-course" }
            if planetaryHourScore < 0.3 { return "Unfavorable planetary hour" }
            if transitNatalScore < 0.3 { return "Challenging transits" }
            if moonPhaseScore < 0.3 { return "Misaligned moon phase" }
            return "Low cosmic alignment"
        }
    }
    
    private struct WindowResult {
        let score: WindowScore
        let isMercuryRetrograde: Bool
    }
    
    private func scoreWindow(
        at date: Date,
        activity: String,
        natalPlanets: [PlanetPlacement],
        solarTimes: EphemerisEngine.SolarTimes?,
        profile: Profile
    ) async -> WindowResult {
        // Get transit positions at this time
        let transits = (try? await EphemerisEngine.shared.calculateCurrentTransits(date: date)) ?? []
        
        // 1. Planetary Hour Score (25%)
        let hourRuler = chaldeanPlanetaryHour(at: date, solarTimes: solarTimes)
        let rulers = Self.activityRulers[activity] ?? []
        let hourScore: Double = rulers.contains(hourRuler) ? 1.0 : 0.4
        
        // 2. Moon Phase Score (20%)
        var moonPhaseScore = 0.5
        if let sun = transits.first(where: { $0.name == "Sun" }),
           let moon = transits.first(where: { $0.name == "Moon" }),
           let sunDeg = sun.absoluteDegree,
           let moonDeg = moon.absoluteDegree {
            var elongation = moonDeg - sunDeg
            if elongation < 0 { elongation += 360 }
            moonPhaseScore = moonPhaseAlignment(elongation: elongation, activity: activity)
        }
        
        // 3. Void-of-Course Moon Penalty (15%)
        let isVoC = checkVoidOfCourse(transits: transits)
        let vocPenalty: Double = isVoC ? -0.15 : 0.0 // Full penalty if VoC
        
        // 4. Transit-Natal Aspects (25%)
        let transitNatalScore = scoreTransitNatalAspects(transits: transits, natalPlanets: natalPlanets, activity: activity)
        
        // 5. Moon Sign Element (15%)
        var moonElementScore = 0.5
        if let moon = transits.first(where: { $0.name == "Moon" }) {
            let element = Self.signElements[moon.sign] ?? "Unknown"
            let favoredElements = Self.activityElements[activity] ?? []
            moonElementScore = favoredElements.contains(element) ? 1.0 : 0.4
        }
        
        // Check Mercury retrograde from already-fetched transits
        let mercuryRetro = transits.first(where: { $0.name == "Mercury" })?.retrograde ?? false
        
        let windowScore = WindowScore(
            planetaryHourScore: hourScore,
            moonPhaseScore: moonPhaseScore,
            vocPenalty: vocPenalty,
            transitNatalScore: transitNatalScore,
            moonElementScore: moonElementScore,
            planetaryHourName: hourRuler,
            isVoidOfCourse: isVoC
        )
        
        return WindowResult(score: windowScore, isMercuryRetrograde: mercuryRetro)
    }
    
    // MARK: - Factor Calculations
    
    /// Score how well the current Moon phase aligns with the activity type.
    private func moonPhaseAlignment(elongation: Double, activity: String) -> Double {
        // Waxing phases favor initiation; Waning phases favor release/reflection
        let isWaxing = elongation < 180
        let isNew = elongation < 45 || elongation > 315
        let isFull = elongation > 165 && elongation < 195
        
        // Activities that need initiation energy
        let initiationActivities: Set = ["starting_project", "job_interview", "business_meeting", "signing_contracts"]
        // Activities that benefit from culmination/fullness
        let culminationActivities: Set = ["romance_date", "creative_work"]
        // Activities that benefit from reflective energy
        let reflectiveActivities: Set = ["meditation_spiritual", "financial_decision"]
        
        if initiationActivities.contains(activity) {
            if isNew { return 0.9 } // New Moon = fresh starts
            if isWaxing { return 0.8 }
            return 0.4
        } else if culminationActivities.contains(activity) {
            if isFull { return 0.95 } // Full Moon = emotional peak
            if isWaxing { return 0.7 }
            return 0.5
        } else if reflectiveActivities.contains(activity) {
            if !isWaxing { return 0.85 } // Waning = introspection
            return 0.5
        }
        
        return 0.5 // Neutral for travel etc.
    }
    
    /// Score transit-natal aspects — benefic aspects boost, malefic hard aspects penalize.
    private func scoreTransitNatalAspects(transits: [PlanetPlacement], natalPlanets: [PlanetPlacement], activity: String) -> Double {
        guard !natalPlanets.isEmpty else { return 0.5 }
        
        let rulers = Self.activityRulers[activity] ?? []
        var totalScore = 0.5 // Baseline neutral
        var aspectCount = 0
        
        for transit in transits {
            for natal in natalPlanets {
                guard let tDeg = transit.absoluteDegree, let nDeg = natal.absoluteDegree else { continue }
                guard transit.name != natal.name else { continue }
                
                var diff = abs(tDeg - nDeg)
                if diff > 180 { diff = 360 - diff }
                
                // Check for aspects within orb
                let aspects: [(name: String, angle: Double, orb: Double, nature: String)] = [
                    ("conjunction", 0, 6, "neutral"),
                    ("trine", 120, 6, "benefic"),
                    ("sextile", 60, 5, "benefic"),
                    ("square", 90, 5, "malefic"),
                    ("opposition", 180, 6, "malefic"),
                ]
                
                for aspect in aspects {
                    let orb = abs(diff - aspect.angle)
                    guard orb <= aspect.orb else { continue }
                    
                    let tightness = 1.0 - (orb / aspect.orb) // Tighter = stronger effect
                    let relevanceBoost = rulers.contains(transit.name) ? 1.5 : 1.0
                    
                    switch aspect.nature {
                    case "benefic":
                        let isBeneficPlanet = Self.beneficPlanets.contains(transit.name)
                        let boost = tightness * 0.15 * relevanceBoost * (isBeneficPlanet ? 1.3 : 1.0)
                        totalScore += boost
                    case "malefic":
                        let isMaleficPlanet = Self.maleficPlanets.contains(transit.name)
                        let penalty = tightness * 0.12 * relevanceBoost * (isMaleficPlanet ? 1.3 : 1.0)
                        totalScore -= penalty
                    case "neutral":
                        // Conjunctions depend on the planet
                        if Self.beneficPlanets.contains(transit.name) {
                            totalScore += tightness * 0.10 * relevanceBoost
                        } else if Self.maleficPlanets.contains(transit.name) {
                            totalScore -= tightness * 0.08 * relevanceBoost
                        }
                    default: break
                    }
                    
                    aspectCount += 1
                    break // One aspect per pair
                }
            }
        }
        
        return max(0, min(1, totalScore))
    }
    
    // MARK: - Void of Course Check (from CalendarOracle pattern)
    
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
    
    // MARK: - Planetary Hour (Chaldean)
    
    /// Calculate the Chaldean planetary hour ruler, optionally using real sunrise/sunset.
    private func chaldeanPlanetaryHour(at date: Date, solarTimes: EphemerisEngine.SolarTimes?) -> String {
        let calendar = Calendar.current
        let weekday = calendar.component(.weekday, from: date)
        
        let chaldean = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        let dayRulers = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        let dayRuler = dayRulers[weekday - 1]
        guard let startIdx = chaldean.firstIndex(of: dayRuler) else { return "Unknown" }
        
        if let solar = solarTimes {
            // Use real sunrise/sunset for accurate planetary hours
            let sunrise = solar.sunrise
            let sunset = solar.sunset
            
            let isDaytime = date >= sunrise && date < sunset
            let periodStart = isDaytime ? sunrise : sunset
            let periodDuration = isDaytime ? solar.daylightMinutes : solar.nighttimeMinutes
            let hourDuration = periodDuration / 12.0 // Each "hour" = 1/12 of day or night
            
            let minutesIntoPeriod = date.timeIntervalSince(periodStart) / 60.0
            let hourNum = Int(minutesIntoPeriod / hourDuration)
            let offset = isDaytime ? hourNum : hourNum + 12
            
            return chaldean[(startIdx + offset) % 7]
        } else {
            // Fallback: fixed 6 AM / 6 PM
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
    
    // MARK: - Tips Generation
    
    private func generateTips(activity: String, bestWindow: ScoredWindow?, allWindows: [ScoredWindow]) -> [String] {
        var tips: [String] = []
        
        if let best = bestWindow {
            if best.factors.isVoidOfCourse {
                tips.append("⚠️ The Moon is void-of-course during some windows — avoid signing contracts or initiating new agreements during these times.")
            }
            
            if best.factors.planetaryHourScore >= 0.8 {
                tips.append("✨ The top window falls in the planetary hour of \(best.factors.planetaryHourName), which directly rules this activity — excellent alignment.")
            }
            
            if best.factors.moonPhaseScore >= 0.8 {
                tips.append("🌙 The current Moon phase strongly supports this type of activity.")
            }
            
            if best.factors.transitNatalScore < 0.4 {
                tips.append("⚡ Your current transit weather includes some challenging aspects. If possible, wait for a window with higher cosmic alignment.")
            }
        }
        
        // Activity-specific tips
        switch activity {
        case "signing_contracts":
            tips.append("📝 Always avoid signing during Moon void-of-course periods. Check if Mercury is retrograde for extra caution.")
        case "romance_date":
            tips.append("💕 Venus-ruled hours are ideal for romance. Full and Waxing Moon phases amplify emotional connection.")
        case "starting_project":
            tips.append("🚀 New Moon phases provide the strongest initiatory energy. Mars and Jupiter hours boost ambition and expansion.")
        case "financial_decision":
            tips.append("💰 Earth sign Moons (Taurus, Virgo, Capricorn) provide grounded financial judgment. Jupiter hours favor growth.")
        case "meditation_spiritual":
            tips.append("🧘 Water sign Moons (Cancer, Scorpio, Pisces) deepen spiritual sensitivity. Waning phases favor inner work.")
        default:
            break
        }
        
        // Check for retrogrades (from pre-computed transit data)
        if let best = bestWindow, best.isMercuryRetrograde {
            tips.append("⚠️ Mercury is currently retrograde — double-check communications, travel plans, and contract details.")
        }
        
        return tips
    }
    
    // MARK: - Rating Text
    
    private func ratingText(score: Double, activity: String) -> String {
        let activityName = TimingActivity(rawValue: activity)?.displayName ?? activity
        
        switch score {
        case 0.8...1.0:
            return "Exceptional cosmic alignment for \(activityName). The planets are strongly in your favor — seize this window."
        case 0.6..<0.8:
            return "Good cosmic conditions for \(activityName). The energy supports your intentions with minor caveats."
        case 0.4..<0.6:
            return "Mixed cosmic weather for \(activityName). Proceed with awareness — some factors are favorable, others require caution."
        case 0.2..<0.4:
            return "Challenging cosmic conditions for \(activityName). Consider postponing or prepare extra carefully."
        default:
            return "Difficult cosmic alignment for \(activityName). Strong headwinds — if possible, wait for a better window."
        }
    }
}
