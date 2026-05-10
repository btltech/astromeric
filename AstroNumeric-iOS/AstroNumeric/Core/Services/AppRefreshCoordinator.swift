import Foundation

actor AppRefreshCoordinator {
    private let widgets: WidgetService
    private let notifications: NotificationSchedulingService
    private let clock: Clock

    init(
        widgets: WidgetService = LiveWidgetService(),
        notifications: NotificationSchedulingService = LiveNotificationSchedulingService(),
        clock: Clock = SystemClock()
    ) {
        self.widgets = widgets
        self.notifications = notifications
        self.clock = clock
    }

    func refreshOnLaunch(profile: Profile?, dailyReminderEnabled: Bool) async {
        if dailyReminderEnabled {
            let status = await notifications.checkPermissionStatus()
            if status == .authorized {
                await notifications.scheduleDailyReminder(at: 8, minute: 0)
            }
        }

        if let profile {
            _ = try? await widgets.refreshMorningBrief(profile: profile, force: false)
        }
    }

    func refreshOnForeground(profile: Profile?) async {
        await notifications.clearBadge()

        await withTaskGroup(of: Void.self) { group in
            group.addTask {
                await BiometricLogger.shared.logToday(profile: profile)
            }

            group.addTask { [widgets] in
                if let lat = profile?.latitude, let lon = profile?.longitude {
                    await widgets.updatePlanetaryHours(latitude: lat, longitude: lon)
                }
            }

            group.addTask { [widgets] in
                await widgets.updateMoonPhase()
            }

            group.addTask { [widgets] in
                if let profile {
                    _ = try? await widgets.refreshMorningBrief(profile: profile, force: false)
                }
            }

            group.addTask { [widgets] in
                widgets.reloadAllTimelines()
            }

            group.addTask { [clock] in
                let lastScan = UserDefaults.standard.double(forKey: "transit.lastScanTimestamp")
                let sixHours: TimeInterval = 6 * 3600
                if clock.now.timeIntervalSince1970 - lastScan > sixHours {
                    await TransitNotificationScheduler.shared.scanAndSchedule()
                    TransitNotificationScheduler.shared.scheduleNextBackgroundScan()
                    UserDefaults.standard.set(clock.now.timeIntervalSince1970, forKey: "transit.lastScanTimestamp")
                }
            }
        }

        CachePrewarmScheduler.shared.scheduleNextBackgroundPrewarm()
    }
}