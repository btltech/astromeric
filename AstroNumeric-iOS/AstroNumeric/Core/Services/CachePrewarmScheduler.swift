// CachePrewarmScheduler.swift
// BGAppRefreshTask that pre-warms cache for instant launch experiences.

import Foundation
import BackgroundTasks

actor CachePrewarmScheduler {
    static let shared = CachePrewarmScheduler()
    private init() {}

    static let bgTaskIdentifier = "com.astromeric.app.cachePrewarm"

    private let lastRunKey = "cachePrewarm.lastRunTimestamp"
    private let minInterval: TimeInterval = 3 * 3600 // 3 hours

    // MARK: - Public API

    /// Register the BGAppRefreshTask — call once at app launch.
    nonisolated func registerBackgroundTask() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: Self.bgTaskIdentifier,
            using: nil
        ) { task in
            guard let refreshTask = task as? BGAppRefreshTask else { return }
            Task { await self.handleBackgroundRefresh(refreshTask) }
        }
    }

    /// Schedule the next background prewarm (call opportunistically).
    nonisolated func scheduleNextBackgroundPrewarm() {
        let request = BGAppRefreshTaskRequest(identifier: Self.bgTaskIdentifier)
        request.earliestBeginDate = Date().addingTimeInterval(2 * 3600) // best-effort
        do {
            try BGTaskScheduler.shared.submit(request)
            DebugLog.trace("[CachePrewarm] Background prewarm scheduled for ~2h from now")
        } catch {
            DebugLog.log("[CachePrewarm] Failed to schedule BG task: \(error)")
        }
    }

    // MARK: - BGTask handling

    private func handleBackgroundRefresh(_ task: BGAppRefreshTask) async {
        task.expirationHandler = {
            task.setTaskCompleted(success: false)
        }

        let ok = await prewarmIfNeeded()
        scheduleNextBackgroundPrewarm()
        task.setTaskCompleted(success: ok)
    }

    // MARK: - Prewarm logic

    private func prewarmIfNeeded() async -> Bool {
        let now = Date().timeIntervalSince1970
        let last = UserDefaults.standard.double(forKey: lastRunKey)
        if last > 0, now - last < minInterval {
            return true
        }

        guard let profile = await MainActor.run(body: { AppStore.shared.activeProfile }) else {
            DebugLog.log("[CachePrewarm] No active profile — skipping")
            return false
        }

        await prewarm(profile: profile)
        UserDefaults.standard.set(now, forKey: lastRunKey)
        return true
    }

    private func prewarm(profile: Profile) async {
        await withTaskGroup(of: Void.self) { group in
            group.addTask {
                do {
                    let _: V2ApiResponse<PredictionData> = try await APIClient.shared.fetch(
                        .reading(profile: profile, scope: .daily, date: Date()),
                        cachePolicy: .networkFirst
                    )
                } catch {
                    DebugLog.log("[CachePrewarm] reading prewarm failed: \(error)")
                }
            }

            group.addTask {
                do {
                    let _: V2ApiResponse<DailyFeaturesData> = try await APIClient.shared.fetch(
                        .dailyFeatures(profile: profile, date: Date()),
                        cachePolicy: .networkFirst
                    )
                } catch {
                    DebugLog.log("[CachePrewarm] dailyFeatures prewarm failed: \(error)")
                }
            }
        }
    }
}

