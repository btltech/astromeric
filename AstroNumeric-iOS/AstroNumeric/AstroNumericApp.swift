// AstroNumericApp.swift
// Main entry point for AstroNumeric iOS app

import SwiftUI
import UserNotifications
import WidgetKit
import BackgroundTasks

@main
struct AstroNumericApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @State private var appStore = AppStore.shared
    @Environment(\.scenePhase) private var scenePhase
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(appStore)
                .preferredColorScheme(.dark)
                .task {
                    await appStore.loadInitialData()
                    await setupNotificationsIfNeeded()
                    if let profile = appStore.activeProfile {
                        _ = try? await WidgetDataProvider.shared.refreshMorningBrief(profile: profile)
                    }
                }
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)) { _ in
                    Task {
                        await NotificationService.shared.clearBadge()
                        // Update streak on foreground in case user crossed midnight
                        await MainActor.run {
                            appStore.updateStreak()
                        }
                    }
                }
                .onChange(of: scenePhase) { oldPhase, newPhase in
                    if newPhase == .active {
                        let profile = AppStore.shared.activeProfile

                        // All foreground work in PARALLEL, independent tasks.
                        // No actor waits on another.

                        Task.detached(priority: .background) {
                            await BiometricLogger.shared.logToday(profile: profile)
                        }

                        Task.detached(priority: .background) {
                            if let lat = profile?.latitude, let lon = profile?.longitude {
                                await WidgetDataProvider.shared.updatePlanetaryHours(
                                    latitude: lat, longitude: lon
                                )
                            }
                        }

                        Task.detached(priority: .background) {
                            await WidgetDataProvider.shared.updateMoonPhase()
                        }

                        Task.detached(priority: .background) {
                            if let profile {
                                _ = try? await WidgetDataProvider.shared.refreshMorningBrief(profile: profile)
                            }
                        }

                        Task.detached(priority: .background) {
                            WidgetCenter.shared.reloadAllTimelines()
                        }

                        Task.detached(priority: .background) {
                            let lastScan = UserDefaults.standard.double(forKey: "transit.lastScanTimestamp")
                            let sixHours: TimeInterval = 6 * 3600
                            if Date().timeIntervalSince1970 - lastScan > sixHours {
                                await TransitNotificationScheduler.shared.scanAndSchedule()
                                TransitNotificationScheduler.shared.scheduleNextBackgroundScan()
                                UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "transit.lastScanTimestamp")
                            }
                        }

                        // Keep background cache prewarm scheduled.
                        CachePrewarmScheduler.shared.scheduleNextBackgroundPrewarm()
                    }
                }
        }
    }
    
    private func setupNotificationsIfNeeded() async {
        // NOTE: BGTask registration is in AppDelegate.didFinishLaunchingWithOptions

        // Check if daily reminder is enabled
        if appStore.dailyReminderEnabled {
            let status = await NotificationService.shared.checkPermissionStatus()
            if status == .authorized {
                // Schedule reminder for 8 AM by default
                await NotificationService.shared.scheduleDailyReminder(at: 8, minute: 0)
            }
        }
    }
}

// MARK: - App Delegate for Push Notifications

class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {
    
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        UNUserNotificationCenter.current().delegate = self

        // BGTaskScheduler MUST register during didFinishLaunchingWithOptions
        TransitNotificationScheduler.shared.registerBackgroundTask()
        CachePrewarmScheduler.shared.registerBackgroundTask()
        CachePrewarmScheduler.shared.scheduleNextBackgroundPrewarm()

        return true
    }
    
    // Handle device token registration
    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        Task {
            await NotificationService.shared.registerDeviceToken(deviceToken)
        }
    }
    
    func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        DebugLog.log("Failed to register for remote notifications: \(error)")
    }
    
    // Handle notification when app is in foreground
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        // Show notification even when app is in foreground
        completionHandler([.banner, .sound, .badge])
    }
    
    // Handle notification tap
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let categoryId = response.notification.request.content.categoryIdentifier
        let actionId = response.actionIdentifier
        
        switch categoryId {
        case NotificationService.Category.dailyReading.rawValue:
            if actionId == "VIEW_READING" || actionId == UNNotificationDefaultActionIdentifier {
                // Navigate to reading tab
                NotificationCenter.default.post(name: .navigateToTab, object: nil, userInfo: ["tab": 0])
            }
            
        case NotificationService.Category.habitReminder.rawValue:
            if actionId == "COMPLETE_HABIT" {
                if let habitId = response.notification.request.content.userInfo["habit_id"] as? String {
                    // Mark habit as complete
                    NotificationCenter.default.post(name: .completeHabit, object: nil, userInfo: ["habitId": habitId])
                }
            }
            
        case NotificationService.Category.moonPhase.rawValue:
            // Navigate to tools/moon phase
            NotificationCenter.default.post(name: .navigateToTab, object: nil, userInfo: ["tab": 1])
            
        default:
            break
        }
        
        completionHandler()
    }
}

// MARK: - Notification Names

extension Notification.Name {
    static let navigateToTab = Notification.Name("navigateToTab")
    static let completeHabit = Notification.Name("completeHabit")
}
