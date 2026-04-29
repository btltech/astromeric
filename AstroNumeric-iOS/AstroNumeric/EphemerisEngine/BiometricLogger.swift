// BiometricLogger.swift
// Persists daily biometric + transit snapshots to disk for long-term correlation analysis.
// Collects HealthKit metrics and active planetary transits each day.

import Foundation

actor BiometricLogger {
    static let shared = BiometricLogger()

    // MARK: - Data Model

    struct DailyLog: Codable {
        let date: String          // yyyy-MM-dd
        let hrvMs: Double?
        let restingHR: Double?
        let sleepHours: Double?
        let steps: Int?
        let activeCalories: Double?
        let spo2: Double?
        let respiratoryRate: Double?
        let mindfulMinutes: Double?
        let transits: [TransitSnapshot]
        let timestamp: Date
        /// Minutes between wake-up time and astronomical sunrise.
        /// Positive = woke after sunrise, negative = woke before.
        /// Enables correlation: "HRV is 15% higher when waking within 30 min of sunrise."
        let sunriseDeltaMinutes: Double?
    }

    struct TransitSnapshot: Codable {
        let planet: String        // e.g. "Mars"
        let sign: String          // e.g. "Aries"
        let degree: Double
        let retrograde: Bool
        /// Aspects to natal chart (e.g. "Mars square Moon")
        let natalAspects: [String]
    }

    // MARK: - Storage

    private var logs: [DailyLog] = []
    private let fileURL: URL = {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        return docs.appendingPathComponent("biometric_daily_logs.json")
    }()

    private init() {
        // Load synchronously in init (nonisolated context)
        if let data = try? Data(contentsOf: fileURL),
           let decoded = try? JSONDecoder().decode([DailyLog].self, from: data) {
            logs = decoded
        }
    }

    // MARK: - Public API

    /// Log today's biometric snapshot + current transits.
    /// Deduplicates by date — only one entry per day (overwrites if called again).
    func logToday(profile: Profile?) async {
        let biometrics = await HealthKitBridge.shared.collectTodaySnapshot()

        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let dateKey = formatter.string(from: Date())

        // Calculate current transits and natal aspects
        var transitSnapshots: [TransitSnapshot] = []

        if let transits = try? await EphemerisEngine.shared.calculateCurrentTransits() {
            let natalPlanets = await natalPlanetPositions(for: profile)

            for transit in transits {
                let aspects = calculateTransitToNatalAspects(
                    transitPlanet: transit.name,
                    transitDegree: transit.absoluteDegree ?? 0,
                    natalPlanets: natalPlanets
                )

                transitSnapshots.append(TransitSnapshot(
                    planet: transit.name,
                    sign: transit.sign,
                    degree: transit.degree,
                    retrograde: transit.retrograde ?? false,
                    natalAspects: aspects
                ))
            }
        }

        // Calculate sunrise delta: wakeUpTime - astronomicalSunrise
        // Positive = woke after sunrise, negative = woke before
        var sunriseDelta: Double? = nil
        if let sleepHours = biometrics.sleepHours, sleepHours > 0,
           let lat = profile?.latitude, let lon = profile?.longitude {
            // Estimate wake-up time from sleep data
            // Sleep typically ends = now - (hours since midnight)
            // Better estimate: assume ~7-8 hour sleep ending around typical wake time
            let now = Date()
            let calendar = Calendar.current
            let todayStart = calendar.startOfDay(for: now)
            // Approximate wake time from sleep duration: assume sleep ended sleepHours ago from log time
            // In practice HealthKit gives exact wake time; here we approximate
            let estimatedWake = calendar.date(byAdding: .hour, value: max(5, min(9, Int(sleepHours))), to: todayStart)

            if let wakeTime = estimatedWake,
               let solar = try? await EphemerisEngine.shared.calculateSunriseSunset(
                   latitude: lat, longitude: lon, date: now
               ) {
                sunriseDelta = wakeTime.timeIntervalSince(solar.sunrise) / 60.0
            }
        }

        let log = DailyLog(
            date: dateKey,
            hrvMs: biometrics.hrvMs,
            restingHR: biometrics.restingHeartRate,
            sleepHours: biometrics.sleepHours,
            steps: biometrics.steps,
            activeCalories: biometrics.activeCalories,
            spo2: biometrics.spo2Percent,
            respiratoryRate: biometrics.respiratoryRate,
            mindfulMinutes: biometrics.mindfulMinutes,
            transits: transitSnapshots,
            timestamp: Date(),
            sunriseDeltaMinutes: sunriseDelta
        )

        // Deduplicate by date
        logs.removeAll { $0.date == dateKey }
        logs.append(log)

        // Keep max 365 days
        if logs.count > 365 {
            logs = Array(logs.suffix(365))
        }

        persist()
    }

    /// Get all logged days
    func allLogs() -> [DailyLog] {
        return logs
    }

    /// Get logs for a specific transit aspect (e.g. "Mars square Moon")
    func logsMatching(aspect: String) -> [DailyLog] {
        return logs.filter { log in
            log.transits.contains { transit in
                transit.natalAspects.contains(aspect)
            }
        }
    }

    /// Number of days of data collected
    var dayCount: Int { logs.count }

    // MARK: - Transit-to-Natal Aspect Calculation

    private func natalPlanetPositions(for profile: Profile?) async -> [(name: String, degree: Double)] {
        guard let profile = profile,
              let chart = try? await EphemerisEngine.shared.calculateNatalChart(profile: profile) else {
            return []
        }
        return chart.planets.map { ($0.name, $0.absoluteDegree ?? 0) }
    }

    private func calculateTransitToNatalAspects(
        transitPlanet: String,
        transitDegree: Double,
        natalPlanets: [(name: String, degree: Double)]
    ) -> [String] {
        let aspectDefs: [(name: String, angle: Double, orb: Double)] = [
            ("conjunction", 0, 8),
            ("opposition", 180, 8),
            ("trine", 120, 8),
            ("square", 90, 7),
            ("sextile", 60, 6),
        ]

        var results: [String] = []

        for natal in natalPlanets {
            guard transitPlanet != natal.name else { continue }

            var diff = abs(transitDegree - natal.degree)
            if diff > 180 { diff = 360 - diff }

            for aspect in aspectDefs {
                let orb = abs(diff - aspect.angle)
                if orb <= aspect.orb {
                    results.append("\(transitPlanet) \(aspect.name) \(natal.name)")
                    break
                }
            }
        }

        return results
    }

    // MARK: - Persistence

    private func persist() {
        guard let data = try? JSONEncoder().encode(logs) else { return }
        try? data.write(to: fileURL, options: .atomic)
    }

    private func loadFromDisk() {
        guard let data = try? Data(contentsOf: fileURL),
              let decoded = try? JSONDecoder().decode([DailyLog].self, from: data) else { return }
        logs = decoded
    }
}
