// NotificationService.swift
// Push notification management and daily reminder scheduling

import UserNotifications
import UIKit

actor NotificationService {
    static let shared = NotificationService()
    
    private init() {}
    
    // MARK: - Notification Categories
    
    enum Category: String {
        case dailyReading = "DAILY_READING"
        case moonPhase = "MOON_PHASE"
        case habitReminder = "HABIT_REMINDER"
        case transitAlert = "TRANSIT_ALERT"
    }
    
    // MARK: - Permission
    
    /// Request notification permission from user
    func requestPermission() async -> Bool {
        let center = UNUserNotificationCenter.current()
        
        do {
            let granted = try await center.requestAuthorization(options: [.alert, .sound, .badge])
            
            if granted {
                await MainActor.run {
                    UIApplication.shared.registerForRemoteNotifications()
                }
                await setupNotificationCategories()
            }
            
            return granted
        } catch {
            DebugLog.log("Notification permission error: \(error)")
            return false
        }
    }
    
    /// Check current authorization status
    func checkPermissionStatus() async -> UNAuthorizationStatus {
        let settings = await UNUserNotificationCenter.current().notificationSettings()
        return settings.authorizationStatus
    }
    
    // MARK: - Categories Setup
    
    private func setupNotificationCategories() async {
        let readAction = UNNotificationAction(
            identifier: "VIEW_READING",
            title: "View Reading",
            options: .foreground
        )
        
        let dismissAction = UNNotificationAction(
            identifier: "DISMISS",
            title: "Dismiss",
            options: .destructive
        )
        
        let dailyReadingCategory = UNNotificationCategory(
            identifier: Category.dailyReading.rawValue,
            actions: [readAction, dismissAction],
            intentIdentifiers: [],
            options: .customDismissAction
        )
        
        let moonPhaseCategory = UNNotificationCategory(
            identifier: Category.moonPhase.rawValue,
            actions: [readAction, dismissAction],
            intentIdentifiers: [],
            options: []
        )
        
        let completeAction = UNNotificationAction(
            identifier: "COMPLETE_HABIT",
            title: "Mark Complete",
            options: .foreground
        )
        
        let habitCategory = UNNotificationCategory(
            identifier: Category.habitReminder.rawValue,
            actions: [completeAction, dismissAction],
            intentIdentifiers: [],
            options: []
        )
        
        let transitCategory = UNNotificationCategory(
            identifier: Category.transitAlert.rawValue,
            actions: [readAction, dismissAction],
            intentIdentifiers: [],
            options: []
        )
        
        let center = UNUserNotificationCenter.current()
        center.setNotificationCategories([dailyReadingCategory, moonPhaseCategory, habitCategory, transitCategory])
    }
    
    // MARK: - Daily Reminder Scheduling
    
    /// Schedule daily reading reminder
    func scheduleDailyReminder(at hour: Int, minute: Int) async {
        let center = UNUserNotificationCenter.current()
        
        // Remove existing daily reminders
        center.removePendingNotificationRequests(withIdentifiers: ["daily_reminder"])
        
        // Create content
        let content = UNMutableNotificationContent()
        content.title = "✨ Your Daily Cosmic Guidance"
        content.body = "The stars have new insights for you today. Tap to see your personalized reading."
        content.sound = .default
        content.categoryIdentifier = Category.dailyReading.rawValue
        content.badge = 1
        
        // Create trigger for specific time each day
        var dateComponents = DateComponents()
        dateComponents.hour = hour
        dateComponents.minute = minute
        
        let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
        
        let request = UNNotificationRequest(
            identifier: "daily_reminder",
            content: content,
            trigger: trigger
        )
        
        do {
            try await center.add(request)
            DebugLog.trace("Daily reminder scheduled for \(hour):\(String(format: "%02d", minute))")
        } catch {
            DebugLog.log("Failed to schedule daily reminder: \(error)")
        }
    }
    
    /// Cancel daily reminder
    func cancelDailyReminder() async {
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["daily_reminder"])
    }

    /// Schedule the morning brief notification at 7 AM with real bullet content.
    /// Called automatically after a successful brief fetch — replaces any previous brief notification.
    func scheduleDailyBriefNotification(bullets: [String], personalDay: Int) async {
        let center = UNUserNotificationCenter.current()
        center.removePendingNotificationRequests(withIdentifiers: ["daily_brief"])

        guard !bullets.isEmpty else { return }

        let content = UNMutableNotificationContent()
        content.title = personalDay > 0
            ? "🌅 Morning Brief · Personal Day \(personalDay)"
            : "🌅 Your Morning Cosmic Brief"
        content.body = bullets.first ?? "Open app for today's cosmic insights."
        if bullets.count > 1 {
            content.subtitle = bullets.dropFirst().first ?? ""
        }
        content.sound = .default
        content.categoryIdentifier = Category.dailyReading.rawValue

        var components = DateComponents()
        components.hour = 7
        components.minute = 0

        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: true)
        let request = UNNotificationRequest(identifier: "daily_brief", content: content, trigger: trigger)

        do {
            try await center.add(request)
            DebugLog.trace("Daily brief notification scheduled for 7:00 AM")
        } catch {
            DebugLog.log("Failed to schedule daily brief notification: \(error)")
        }
    }

    /// Cancel daily brief notification
    func cancelDailyBriefNotification() async {
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["daily_brief"])
    }

    // MARK: - Moon Phase Notifications
    
    /// Schedule moon phase notification
    func scheduleMoonPhaseNotification(phase: String, emoji: String, date: Date) async {
        let content = UNMutableNotificationContent()
        content.title = "\(emoji) \(phase) Tonight"
        content.body = "The \(phase) brings special cosmic energy. Tap to see your lunar guidance."
        content.sound = .default
        content.categoryIdentifier = Category.moonPhase.rawValue
        
        let trigger = UNCalendarNotificationTrigger(
            dateMatching: Calendar.current.dateComponents([.year, .month, .day, .hour], from: date),
            repeats: false
        )
        
        let request = UNNotificationRequest(
            identifier: "moon_phase_\(date.timeIntervalSince1970)",
            content: content,
            trigger: trigger
        )
        
        do {
            try await UNUserNotificationCenter.current().add(request)
        } catch {
            DebugLog.log("Failed to schedule moon phase notification: \(error)")
        }
    }
    
    // MARK: - Habit Reminders
    
    /// Schedule habit reminder
    func scheduleHabitReminder(habitId: String, habitName: String, at hour: Int, minute: Int) async {
        let content = UNMutableNotificationContent()
        content.title = "🌙 Habit Reminder"
        content.body = "Time for: \(habitName)"
        content.sound = .default
        content.categoryIdentifier = Category.habitReminder.rawValue
        content.userInfo = ["habit_id": habitId]
        
        var dateComponents = DateComponents()
        dateComponents.hour = hour
        dateComponents.minute = minute
        
        let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
        
        let request = UNNotificationRequest(
            identifier: "habit_\(habitId)",
            content: content,
            trigger: trigger
        )
        
        do {
            try await UNUserNotificationCenter.current().add(request)
        } catch {
            DebugLog.log("Failed to schedule habit reminder: \(error)")
        }
    }
    
    /// Cancel habit reminder
    func cancelHabitReminder(habitId: String) async {
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["habit_\(habitId)"])
    }

    /// Cancel only moon phase notifications, preserving unrelated reminders.
    func cancelMoonPhaseNotifications() async {
        let center = UNUserNotificationCenter.current()
        let requests = await center.pendingNotificationRequests()
        let moonIdentifiers = requests.compactMap { request -> String? in
            if request.content.categoryIdentifier == Category.moonPhase.rawValue {
                return request.identifier
            }
            if request.identifier.hasPrefix("moon_phase_") {
                return request.identifier
            }
            return nil
        }
        guard !moonIdentifiers.isEmpty else { return }
        center.removePendingNotificationRequests(withIdentifiers: moonIdentifiers)
    }
    
    // MARK: - Transit Alerts
    
    /// Schedule daily transit alert
    func scheduleTransitAlert(at hour: Int, minute: Int) async {
        let content = UNMutableNotificationContent()
        content.title = "🪐 Transit Alert"
        content.body = "Check today’s key transits and cosmic shifts."
        content.sound = .default
        content.categoryIdentifier = Category.transitAlert.rawValue
        
        var dateComponents = DateComponents()
        dateComponents.hour = hour
        dateComponents.minute = minute
        
        let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
        let request = UNNotificationRequest(identifier: "daily_transit_alert", content: content, trigger: trigger)
        
        do {
            try await UNUserNotificationCenter.current().add(request)
        } catch {
            DebugLog.log("Failed to schedule transit alert: \(error)")
        }
    }
    
    /// Cancel daily transit alert
    func cancelTransitAlert() async {
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["daily_transit_alert"])
    }
    
    // MARK: - Badge Management
    
    /// Clear app badge
    func clearBadge() async {
        try? await UNUserNotificationCenter.current().setBadgeCount(0)
    }
    
    /// Set app badge
    func setBadge(_ count: Int) async {
        try? await UNUserNotificationCenter.current().setBadgeCount(count)
    }
    
    // MARK: - Token Registration
    
    /// Handle device token registration
    func registerDeviceToken(_ tokenData: Data) async {
        let token = tokenData.map { String(format: "%02.2hhx", $0) }.joined()
        
        // Store token locally
        UserDefaults.standard.set(token, forKey: "apns_device_token")
        
        // Upload to backend for push notifications
        do {
            let _: V2ApiResponse<EmptyResponse> = try await APIClient.shared.fetch(
                .registerDeviceToken(token)
            )
            DebugLog.log("Device token registered with backend")
        } catch {
            DebugLog.log("Failed to register device token: \(error)")
        }
    }
    
    // MARK: - Pending Notifications
    
    /// Get count of pending notifications
    func getPendingNotificationCount() async -> Int {
        let requests = await UNUserNotificationCenter.current().pendingNotificationRequests()
        return requests.count
    }
    
    /// List all pending notifications
    func listPendingNotifications() async -> [UNNotificationRequest] {
        await UNUserNotificationCenter.current().pendingNotificationRequests()
    }
    
    /// Remove all pending notifications
    func removeAllPendingNotifications() async {
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
    }
}

// MARK: - Empty Response for API

struct EmptyResponse: Codable {}

// MARK: - Endpoint Extension

extension Endpoint {
    static func registerDeviceToken(_ token: String) -> Endpoint {
        Endpoint(
            path: "/v2/notifications/register",
            method: .POST,
            body: DeviceTokenRequest(token: token, platform: "ios")
        )
    }
}

struct DeviceTokenRequest: Encodable {
    let token: String
    let platform: String
}
