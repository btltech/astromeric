// WidgetDataProvider.swift
// Writes pre-computed cosmic data to App Group UserDefaults for the Widget Extension.
// The main app computes; the widget reads. No Swiss Ephemeris in the widget process.

import Foundation
import WidgetKit

/// Keys for shared UserDefaults
enum WidgetDataKey: String {
    case planetaryHourName = "widget.planetaryHour.name"
    case planetaryHourEndDate = "widget.planetaryHour.endDate"
    case planetaryHourSchedule = "widget.planetaryHour.schedule"
    case planetaryHourLastUpdated = "widget.planetaryHour.lastUpdated"
    case moonPhaseName = "widget.moon.phase"
    case moonPhaseIllumination = "widget.moon.illumination"
    case moonSign = "widget.moon.sign"
    case isVoidOfCourse = "widget.moon.isVoid"
    case moonPhaseLastUpdated = "widget.moon.lastUpdated"
    case dailySummary = "widget.daily.summary"
    case dailySummaryLastUpdated = "widget.daily.lastUpdated"
    case briefBullets = "widget.brief.bullets"      // JSON [String] array
    case briefPersonalDay = "widget.brief.personalDay"
    case briefLastUpdated = "widget.brief.lastUpdated"
    case lastUpdated = "widget.lastUpdated"
}

/// Encoded planetary hour block for timeline
struct PlanetaryHourEntry: Codable {
    let rulerName: String      // e.g., "Mercury"
    let startDate: Date
    let endDate: Date

    var emoji: String {
        switch rulerName {
        case "Sun":     return "☉"
        case "Moon":    return "☽"
        case "Mars":    return "♂"
        case "Mercury": return "☿"
        case "Jupiter": return "♃"
        case "Venus":   return "♀"
        case "Saturn":  return "♄"
        default:        return "⚫"
        }
    }
}

struct WidgetRefreshDiagnostics {
    let overall: Date?
    let planetaryHour: Date?
    let moonPhase: Date?
    let dailySummary: Date?
    let morningBrief: Date?

    static let empty = WidgetRefreshDiagnostics(
        overall: nil,
        planetaryHour: nil,
        moonPhase: nil,
        dailySummary: nil,
        morningBrief: nil
    )
}

/// The main app calls this to push data to the widget.
actor WidgetDataProvider {
    static let shared = WidgetDataProvider()
    private init() {}

    private let morningBriefRefreshKeyPrefix = "morningBrief.lastRefresh."

    private var sharedDefaults: UserDefaults? {
        AppGroupStore.sharedDefaults
    }

    // MARK: - Write (Main App)

    /// Compute and cache the full planetary hour schedule for today.
    /// Called on app foreground and after midnight.
    func updatePlanetaryHours(latitude: Double, longitude: Double) async {
        guard let defaults = sharedDefaults else { return }

        let now = Date()
        let calendar = Calendar.current
        let weekday = calendar.component(.weekday, from: now)

        let chaldean = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        let dayRulers = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        let dayRuler = dayRulers[weekday - 1]
        guard let startIdx = chaldean.firstIndex(of: dayRuler) else { return }

        // Get real sunrise/sunset from EphemerisEngine
        guard let solar = try? await EphemerisEngine.shared.calculateSunriseSunset(
            latitude: latitude, longitude: longitude, date: now
        ) else { return }

        let sunrise = solar.sunrise
        let sunset = solar.sunset
        let dayHourDuration = solar.daylightMinutes / 12.0   // minutes per day hour
        let nightHourDuration = solar.nighttimeMinutes / 12.0 // minutes per night hour

        var schedule: [PlanetaryHourEntry] = []

        // 12 day hours (sunrise to sunset)
        for idx in 0..<12 {
            let start = sunrise.addingTimeInterval(Double(idx) * dayHourDuration * 60)
            let end = sunrise.addingTimeInterval(Double(idx + 1) * dayHourDuration * 60)
            let ruler = chaldean[(startIdx + idx) % 7]
            schedule.append(PlanetaryHourEntry(rulerName: ruler, startDate: start, endDate: end))
        }

        // 12 night hours (sunset to next sunrise)
        for idx in 0..<12 {
            let start = sunset.addingTimeInterval(Double(idx) * nightHourDuration * 60)
            let end = sunset.addingTimeInterval(Double(idx + 1) * nightHourDuration * 60)
            let ruler = chaldean[(startIdx + 12 + idx) % 7]
            schedule.append(PlanetaryHourEntry(rulerName: ruler, startDate: start, endDate: end))
        }

        // Find current hour
        if let current = schedule.first(where: { now >= $0.startDate && now < $0.endDate }) {
            defaults.set(current.rulerName, forKey: WidgetDataKey.planetaryHourName.rawValue)
            defaults.set(current.endDate, forKey: WidgetDataKey.planetaryHourEndDate.rawValue)
        }

        // Encode full schedule for timeline
        if let data = try? JSONEncoder().encode(schedule) {
            defaults.set(data, forKey: WidgetDataKey.planetaryHourSchedule.rawValue)
        }

        defaults.set(now, forKey: WidgetDataKey.planetaryHourLastUpdated.rawValue)
        defaults.set(now, forKey: WidgetDataKey.lastUpdated.rawValue)
    }

    /// Update moon phase data.
    func updateMoonPhase() async {
        guard let defaults = sharedDefaults else { return }
        let now = Date()

        guard let transits = try? await EphemerisEngine.shared.calculateCurrentTransits() else { return }

        if let moon = transits.first(where: { $0.name == "Moon" }) {
            defaults.set(moon.sign, forKey: WidgetDataKey.moonSign.rawValue)
        }

        // Moon phase from Sun-Moon elongation
        if let sun = transits.first(where: { $0.name == "Sun" }),
           let moon = transits.first(where: { $0.name == "Moon" }),
           let sunDeg = sun.absoluteDegree,
           let moonDeg = moon.absoluteDegree {
            var elongation = moonDeg - sunDeg
            if elongation < 0 { elongation += 360 }

            let phaseName: String
            let illumination: Double
            switch elongation {
            case 0..<45:     phaseName = "🌑"; illumination = elongation / 180 * 100
            case 45..<90:    phaseName = "🌒"; illumination = elongation / 180 * 100
            case 90..<135:   phaseName = "🌓"; illumination = elongation / 180 * 100
            case 135..<180:  phaseName = "🌔"; illumination = elongation / 180 * 100
            case 180..<225:  phaseName = "🌕"; illumination = (360 - elongation) / 180 * 100
            case 225..<270:  phaseName = "🌖"; illumination = (360 - elongation) / 180 * 100
            case 270..<315:  phaseName = "🌗"; illumination = (360 - elongation) / 180 * 100
            case 315..<360:  phaseName = "🌘"; illumination = (360 - elongation) / 180 * 100
            default:         phaseName = "🌑"; illumination = 0
            }

            defaults.set(phaseName, forKey: WidgetDataKey.moonPhaseName.rawValue)
            defaults.set(illumination, forKey: WidgetDataKey.moonPhaseIllumination.rawValue)
        }

        defaults.set(now, forKey: WidgetDataKey.moonPhaseLastUpdated.rawValue)
        defaults.set(now, forKey: WidgetDataKey.lastUpdated.rawValue)
    }

    /// Write daily summary (called by AI at midnight or on first launch).
    func updateDailySummary(_ summary: String) {
        guard let defaults = sharedDefaults else { return }
        let now = Date()
        defaults.set(summary, forKey: WidgetDataKey.dailySummary.rawValue)
        defaults.set(now, forKey: WidgetDataKey.dailySummaryLastUpdated.rawValue)
        defaults.set(now, forKey: WidgetDataKey.lastUpdated.rawValue)
        WidgetCenter.shared.reloadAllTimelines()
    }

    /// Write morning brief data for the widget.
    /// - Parameters:
    ///   - bullets: Up to 3 short cosmic insight strings.
    ///   - personalDay: Personal Day number (1–9).
    func updateMorningBrief(bullets: [String], personalDay: Int) {
        guard let defaults = sharedDefaults else { return }
        let now = Date()
        if let data = try? JSONEncoder().encode(bullets) {
            defaults.set(String(data: data, encoding: .utf8), forKey: WidgetDataKey.briefBullets.rawValue)
        }
        defaults.set(personalDay, forKey: WidgetDataKey.briefPersonalDay.rawValue)
        defaults.set(now, forKey: WidgetDataKey.briefLastUpdated.rawValue)
        defaults.set(now, forKey: WidgetDataKey.lastUpdated.rawValue)
    }

    /// Refresh the morning brief and persist it for the widget + push notification flows.
    func refreshMorningBrief(profile: Profile, force: Bool = false) async throws -> MorningBriefData {
        let refreshKey = morningBriefRefreshKeyPrefix + String(profile.id)
        let todayKey = Self.dayKey(for: profile.timezone)
        let cachePolicy: CachePolicy = force ? .networkFirst : .cacheFirst

        if !force, UserDefaults.standard.string(forKey: refreshKey) == todayKey {
            let response: V2ApiResponse<MorningBriefData> = try await APIClient.shared.fetch(
                .morningBrief(profile: profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)),
                cachePolicy: .cacheFirst
            )
            return response.data
        }

        let response: V2ApiResponse<MorningBriefData> = try await APIClient.shared.fetch(
            .morningBrief(profile: profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)),
            cachePolicy: cachePolicy
        )

        let brief = response.data
        let bullets = brief.bullets.map { "\($0.emoji) \($0.text)" }

        updateMorningBrief(bullets: bullets, personalDay: brief.personalDay)

        let status = await NotificationService.shared.checkPermissionStatus()
        if status == .authorized {
            await NotificationService.shared.scheduleDailyBriefNotification(
                bullets: bullets,
                personalDay: brief.personalDay
            )
        }

        UserDefaults.standard.set(todayKey, forKey: refreshKey)
        WidgetCenter.shared.reloadAllTimelines()

        return brief
    }

    // MARK: - Read (Widget Process)

    /// Read the cached planetary hour schedule.
    static func readPlanetaryHourSchedule() -> [PlanetaryHourEntry] {
                guard let defaults = AppGroupStore.sharedDefaults,
              let data = defaults.data(forKey: WidgetDataKey.planetaryHourSchedule.rawValue),
              let schedule = try? JSONDecoder().decode([PlanetaryHourEntry].self, from: data) else {
            return []
        }
        return schedule
    }

    /// Read current planetary hour.
    static func readCurrentHour() -> (name: String, endDate: Date)? {
                guard let defaults = AppGroupStore.sharedDefaults,
              let name = defaults.string(forKey: WidgetDataKey.planetaryHourName.rawValue),
              let endDate = defaults.object(forKey: WidgetDataKey.planetaryHourEndDate.rawValue) as? Date else {
            return nil
        }
        return (name, endDate)
    }

    /// Read moon phase data.
    static func readMoonPhase() -> (emoji: String, sign: String, illumination: Double)? {
                guard let defaults = AppGroupStore.sharedDefaults,
              let emoji = defaults.string(forKey: WidgetDataKey.moonPhaseName.rawValue),
              let sign = defaults.string(forKey: WidgetDataKey.moonSign.rawValue) else {
            return nil
        }
        let illumination = defaults.double(forKey: WidgetDataKey.moonPhaseIllumination.rawValue)
        return (emoji, sign, illumination)
    }

    /// Read daily summary.
    static func readDailySummary() -> String? {
        AppGroupStore.sharedDefaults?.string(forKey: WidgetDataKey.dailySummary.rawValue)
    }

    static func readRefreshDiagnostics() -> WidgetRefreshDiagnostics {
        guard let defaults = AppGroupStore.sharedDefaults else {
            return .empty
        }
        return WidgetRefreshDiagnostics(
            overall: defaults.object(forKey: WidgetDataKey.lastUpdated.rawValue) as? Date,
            planetaryHour: defaults.object(forKey: WidgetDataKey.planetaryHourLastUpdated.rawValue) as? Date,
            moonPhase: defaults.object(forKey: WidgetDataKey.moonPhaseLastUpdated.rawValue) as? Date,
            dailySummary: defaults.object(forKey: WidgetDataKey.dailySummaryLastUpdated.rawValue) as? Date,
            morningBrief: defaults.object(forKey: WidgetDataKey.briefLastUpdated.rawValue) as? Date
        )
    }

    private nonisolated static func dayKey(for timezoneID: String?) -> String {
        let timeZone = TimeZone(identifier: timezoneID ?? "") ?? TimeZone(identifier: "UTC")!
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        formatter.timeZone = timeZone
        return formatter.string(from: Date())
    }
}
