// TransitNotificationScheduler.swift
// Proactive Oracle — runs PredictiveScanner and schedules local push notifications
// at the exact minute of each volatile transit-to-natal aspect.
// Triggers: app foreground + weekly BGAppRefreshTask.

import Foundation
import UserNotifications
import BackgroundTasks

actor TransitNotificationScheduler {
    static let shared = TransitNotificationScheduler()
    private init() {}

    /// BGTaskScheduler identifier for weekly transit scan
    static let bgTaskIdentifier = "com.astromeric.app.transitScan"

    /// UserDefaults key for tracking scheduled transit hashes
    private let scheduledHashesKey = "transit.notification.scheduledHashes"

    /// Maximum concurrent notifications (iOS limit is 64 pending)
    private let maxScheduledTransits = 20

    // MARK: - Public API

    /// Scan for upcoming transits and schedule notifications.
    /// Called on app foreground and by BGAppRefreshTask.
    func scanAndSchedule() async {
        guard let profile = await MainActor.run(body: { AppStore.shared.activeProfile }) else {
            DebugLog.log("[TransitScheduler] No active profile — skipping scan")
            return
        }

        // Check if transit alerts are enabled
        let enabled = UserDefaults.standard.bool(forKey: "settings.transitAlerts.enabled")
        guard enabled else {
            DebugLog.log("[TransitScheduler] Transit alerts disabled — skipping")
            return
        }

        do {
            // Scan next 7 days for exact transits
            let transits = try await PredictiveScanner.shared.findExactTransits(
                profile: profile, daysAhead: 7
            )

            // Filter by severity preference
            let majorOnly = UserDefaults.standard.bool(forKey: "settings.transitAlerts.majorOnly")
            let filtered = majorOnly
                ? transits.filter { $0.significance == "major" }
                : transits

            // Only schedule future transits
            let now = Date()
            let upcoming = filtered.filter { $0.exactDate > now }

            // Deduplicate against already-scheduled
            let alreadyScheduled = loadScheduledHashes()
            var newHashes: Set<String> = alreadyScheduled
            var toSchedule: [PredictiveScanner.FutureTransit] = []

            for transit in upcoming.prefix(maxScheduledTransits) {
                let hash = transitHash(transit)
                if !alreadyScheduled.contains(hash) {
                    toSchedule.append(transit)
                    newHashes.insert(hash)
                }
            }

            // Schedule notifications
            let center = UNUserNotificationCenter.current()
            for transit in toSchedule {
                let content = buildNotificationContent(for: transit)
                let trigger = UNCalendarNotificationTrigger(
                    dateMatching: Calendar.current.dateComponents(
                        [.year, .month, .day, .hour, .minute],
                        from: transit.exactDate
                    ),
                    repeats: false
                )

                let request = UNNotificationRequest(
                    identifier: "transit_\(transitHash(transit))",
                    content: content,
                    trigger: trigger
                )

                try await center.add(request)
            }

            // Persist scheduled hashes
            saveScheduledHashes(newHashes)

            DebugLog.log("[TransitScheduler] Scheduled \(toSchedule.count) new transit alerts (\(upcoming.count) total upcoming)")
        } catch {
            DebugLog.log("[TransitScheduler] Scan failed: \(error)")
        }
    }

    /// Clear all transit notifications and reset tracking.
    func clearAll() async {
        let center = UNUserNotificationCenter.current()
        let pending = await center.pendingNotificationRequests()
        let transitIds = pending.filter { $0.identifier.hasPrefix("transit_") }.map { $0.identifier }
        center.removePendingNotificationRequests(withIdentifiers: transitIds)
        saveScheduledHashes([])
        DebugLog.log("[TransitScheduler] Cleared all transit notifications")
    }

    // MARK: - Background Task Registration

    /// Register the BGAppRefreshTask — call once at app launch.
    nonisolated func registerBackgroundTask() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: Self.bgTaskIdentifier,
            using: nil
        ) { task in
            guard let refreshTask = task as? BGAppRefreshTask else { return }
            Task {
                await self.handleBackgroundRefresh(refreshTask)
            }
        }
    }

    /// Schedule the next background scan (call after each completed scan).
    nonisolated func scheduleNextBackgroundScan() {
        let request = BGAppRefreshTaskRequest(identifier: Self.bgTaskIdentifier)
        // Request earliest execution in 6 hours
        request.earliestBeginDate = Date().addingTimeInterval(6 * 3600)
        do {
            try BGTaskScheduler.shared.submit(request)
            DebugLog.log("[TransitScheduler] Background scan scheduled for ~6h from now")
        } catch {
            DebugLog.log("[TransitScheduler] Failed to schedule BG task: \(error)")
        }
    }

    private func handleBackgroundRefresh(_ task: BGAppRefreshTask) async {
        // Set expiration handler
        task.expirationHandler = {
            task.setTaskCompleted(success: false)
        }

        await scanAndSchedule()
        scheduleNextBackgroundScan()
        task.setTaskCompleted(success: true)
    }

    // MARK: - Notification Content Builder

    private func buildNotificationContent(for transit: PredictiveScanner.FutureTransit) -> UNMutableNotificationContent {
        let content = UNMutableNotificationContent()
        let severity = classifySeverity(transit)

        switch severity {
        case .volatile:
            content.title = "🚨 Volatility Warning"
            content.body = "\(transit.transitPlanet) \(transit.aspectName) your \(transit.natalPlanet). \(volatileAdvice(transit))"
            content.interruptionLevel = .timeSensitive

        case .moderate:
            content.title = "⚠️ Transit Active"
            content.body = "\(transit.transitPlanet) \(transit.aspectName) your \(transit.natalPlanet). Stay aware of shifting energy."
            content.interruptionLevel = .active

        case .supportive:
            content.title = "✨ Supportive Transit"
            content.body = "\(transit.transitPlanet) \(transit.aspectName) your \(transit.natalPlanet). Flow with this energy."
            content.interruptionLevel = .passive
        }

        content.sound = severity == .volatile ? .defaultCritical : .default
        content.categoryIdentifier = NotificationService.Category.transitAlert.rawValue
        content.userInfo = [
            "transit_planet": transit.transitPlanet,
            "natal_planet": transit.natalPlanet,
            "aspect": transit.aspectName
        ]

        return content
    }

    // MARK: - Severity Classification

    private enum Severity { case volatile, moderate, supportive }

    private func classifySeverity(_ transit: PredictiveScanner.FutureTransit) -> Severity {
        let hardAspects = ["conjunction", "opposition", "square"]
        let hardPlanets = ["Saturn", "Uranus", "Neptune", "Pluto", "Mars"]

        let isHardAspect = hardAspects.contains(transit.aspectName)
        let isHardPlanet = hardPlanets.contains(transit.transitPlanet)

        if isHardAspect && isHardPlanet { return .volatile }
        if isHardAspect || isHardPlanet { return .moderate }
        return .supportive
    }

    private func volatileAdvice(_ transit: PredictiveScanner.FutureTransit) -> String {
        switch transit.transitPlanet {
        case "Saturn":
            return "Expect restrictions or delays. Do not force outcomes."
        case "Uranus":
            return "Do not react impulsively to emails for the next 4 hours."
        case "Pluto":
            return "Power dynamics are amplified. Stay in control."
        case "Neptune":
            return "Confusion or deception likely. Verify facts before deciding."
        case "Mars":
            return "Aggression is heightened. Choose your battles deliberately."
        default:
            return "Stay alert to shifting energy."
        }
    }

    // MARK: - Hash / Dedup

    private func transitHash(_ transit: PredictiveScanner.FutureTransit) -> String {
        let dateStr = ISO8601DateFormatter().string(from: transit.exactDate)
        return "\(transit.transitPlanet)_\(transit.aspectName)_\(transit.natalPlanet)_\(dateStr)"
    }

    private func loadScheduledHashes() -> Set<String> {
        guard let arr = UserDefaults.standard.stringArray(forKey: scheduledHashesKey) else {
            return []
        }
        return Set(arr)
    }

    private func saveScheduledHashes(_ hashes: Set<String>) {
        UserDefaults.standard.set(Array(hashes), forKey: scheduledHashesKey)
    }
}
