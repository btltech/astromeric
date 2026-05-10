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
    @State private var services = AppServices.live
    @Environment(\.scenePhase) private var scenePhase
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(appStore)
                .environment(services)
                .preferredColorScheme(.dark)
                .task {
                    await appStore.loadInitialData()
                    await services.refreshCoordinator.refreshOnLaunch(
                        profile: appStore.activeProfile,
                        dailyReminderEnabled: appStore.dailyReminderEnabled
                    )
                }
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)) { _ in
                    Task {
                        // Update streak on foreground in case user crossed midnight
                        await MainActor.run {
                            appStore.updateStreak()
                        }
                    }
                }
                .onChange(of: scenePhase) { oldPhase, newPhase in
                    if newPhase == .active {
                        let profile = AppStore.shared.activeProfile
                        Task {
                            await services.refreshCoordinator.refreshOnForeground(profile: profile)
                        }
                    }
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
        PrivacyFilteredCrashReporter.shared.start()

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
