// NotificationSettingsView.swift
// Notification preferences and scheduling

import SwiftUI
import UserNotifications

struct NotificationSettingsView: View {
    @Environment(AppStore.self) private var store
    private let alertPreferencesRepository: AlertPreferencesRepository = DefaultAlertPreferencesRepository()
    @AppStorage("notify_daily_reading") private var notifyDailyReading = false
    @AppStorage("notify_moon_events") private var notifyMoonEvents = false
    @AppStorage("notify_habit_reminder") private var notifyHabitReminder = false
    @AppStorage("notify_timing_alert") private var notifyTimingAlert = false
    @AppStorage("notify_transit_alert") private var notifyTransitAlert = false
    @State private var dailyTime = Date()
    @State private var habitTime = Date()
    @State private var timingTime = Date()
    @State private var transitTime = Date()
    @State private var statusText: String?
    @State private var authorizationStatus: UNAuthorizationStatus = .notDetermined
    @AppStorage("alerts.mercury_retrograde") private var mercuryRetrogradeAlerts = true
    @AppStorage("alerts.frequency") private var alertFrequency = "every_retrograde"
    @AppStorage("settings.transitAlerts.enabled") private var proactiveTransitAlerts = true
    @AppStorage("settings.transitAlerts.majorOnly") private var proactiveTransitMajorOnly = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Space.md) {
                        PremiumScreenHeader(
                            eyebrow: "hero.notificationSettings.eyebrow".localized,
                            title: "hero.notificationSettings.title".localized,
                            subtitle: "hero.notificationSettings.body".localized,
                            accent: .accentPrimary,
                            chips: ["hero.notificationSettings.chip.0".localized, "hero.notificationSettings.chip.1".localized, "hero.notificationSettings.chip.2".localized, "hero.notificationSettings.chip.3".localized]
                        )

                        permissionBanner
                        dailyInsightsGroup
                        celestialEventsGroup
                        personalRemindersGroup
                        advancedTransitGroup

                        if let statusText {
                            PremiumStatusBanner(
                                title: "settings.notifications.status.title".localized,
                                message: statusText,
                                tone: .info
                            )
                        }

                        habitsLink
                    }
                    .padding()
                    .readableContainer()
                }
            }
            .navigationTitle("screen.notifications".localized)
            .navigationBarTitleDisplayMode(.inline)
            .task {
                await initializePermissionStatus()
                await loadAlertPreferences()
            }
        }
    }

    private var permissionBanner: some View {
        PremiumStatusBanner(
            title: permissionTitle,
            message: permissionMessage,
            tone: permissionTone,
            actionTitle: authorizationStatus == .denied ? "settings.notifications.openIOSSettings".localized : nil,
            action: authorizationStatus == .denied ? { openAppSettings() } : nil
        )
    }

    private var dailyInsightsGroup: some View {
        PremiumSettingsGroup(
            title: "settings.notifications.daily.title".localized,
            subtitle: "settings.notifications.daily.subtitle".localized,
            icon: "sun.max.fill",
            accent: .accentPrimary
        ) {
            PremiumToggleRow(
                title: "ui.notificationSettings.10".localized,
                subtitle: "settings.notifications.dailyReading.detail".localized,
                icon: "sparkles.rectangle.stack.fill",
                accent: .accentPrimary,
                isOn: $notifyDailyReading
            )
            .onChange(of: notifyDailyReading) { _, newValue in
                Task { await handleDailyReadingToggle(newValue) }
            }

            if notifyDailyReading {
                PremiumDivider()
                NotificationTimeRow(
                    title: "settings.notifications.dailyReading.time".localized,
                    date: $dailyTime,
                    accent: .accentPrimary
                ) {
                    Task { await rescheduleDailyReading() }
                }
            }
        }
    }

    private var celestialEventsGroup: some View {
        PremiumSettingsGroup(
            title: "settings.notifications.celestial.title".localized,
            subtitle: "settings.notifications.celestial.subtitle".localized,
            icon: "moon.stars.fill",
            accent: .indigo
        ) {
            PremiumToggleRow(
                title: "ui.notificationSettings.11".localized,
                subtitle: "settings.notifications.moon.detail".localized,
                icon: "moon.fill",
                accent: .indigo,
                isOn: $notifyMoonEvents
            )
            .onChange(of: notifyMoonEvents) { _, newValue in
                Task { await handleMoonEventsToggle(newValue) }
            }

            PremiumDivider()

            PremiumToggleRow(
                title: "ui.notificationSettings.13".localized,
                subtitle: "settings.notifications.transit.detail".localized,
                icon: "sparkle.magnifyingglass",
                accent: .pink,
                isOn: $notifyTransitAlert
            )
            .onChange(of: notifyTransitAlert) { _, newValue in
                Task { await handleTransitToggle(newValue) }
            }

            if notifyTransitAlert {
                NotificationTimeRow(
                    title: "settings.notifications.transit.time".localized,
                    date: $transitTime,
                    accent: .pink
                ) {
                    Task { await rescheduleTransitAlert() }
                }
            }

            PremiumDivider()

            PremiumToggleRow(
                title: "ui.notificationSettings.17".localized,
                subtitle: "settings.notifications.retrograde.detail".localized,
                icon: "arrow.triangle.2.circlepath.circle.fill",
                accent: .accentSecondary,
                isOn: $mercuryRetrogradeAlerts
            )
            .onChange(of: mercuryRetrogradeAlerts) { _, _ in
                Task { await updateAlertPreferences() }
            }

            if mercuryRetrogradeAlerts {
                Picker("ui.notificationSettings.18".localized, selection: $alertFrequency) {
                    Text("ui.notificationSettings.4".localized).tag("every_retrograde")
                    Text("ui.notificationSettings.5".localized).tag("weekly_digest")
                    Text("ui.notificationSettings.6".localized).tag("once_per_year")
                    Text("ui.notificationSettings.7".localized).tag("none")
                }
                .pickerStyle(.menu)
                .tint(.accentSecondary)
                .onChange(of: alertFrequency) { _, _ in
                    Task { await updateAlertPreferences() }
                }
            }
        }
    }

    private var personalRemindersGroup: some View {
        PremiumSettingsGroup(
            title: "settings.notifications.personal.title".localized,
            subtitle: "settings.notifications.personal.subtitle".localized,
            icon: "person.crop.circle.badge.clock",
            accent: .positiveGreen
        ) {
            PremiumToggleRow(
                title: "ui.notificationSettings.12".localized,
                subtitle: "settings.notifications.habit.detail".localized,
                icon: "checkmark.circle.fill",
                accent: .positiveGreen,
                isOn: $notifyHabitReminder
            )
            .onChange(of: notifyHabitReminder) { _, newValue in
                Task { await handleHabitToggle(newValue) }
            }

            if notifyHabitReminder {
                NotificationTimeRow(
                    title: "settings.notifications.habit.time".localized,
                    date: $habitTime,
                    accent: .positiveGreen
                ) {
                    Task { await rescheduleHabitReminder() }
                }
            }

            PremiumDivider()

            PremiumToggleRow(
                title: "ui.notificationSettings.14".localized,
                subtitle: "settings.notifications.timing.detail".localized,
                icon: "clock.badge.checkmark.fill",
                accent: .warningOrange,
                isOn: $notifyTimingAlert
            )
            .onChange(of: notifyTimingAlert) { _, newValue in
                Task { await handleTimingToggle(newValue) }
            }

            if notifyTimingAlert {
                NotificationTimeRow(
                    title: "settings.notifications.timing.time".localized,
                    date: $timingTime,
                    accent: .warningOrange
                ) {
                    Task { await rescheduleTimingReminder() }
                }
            }
        }
    }

    private var advancedTransitGroup: some View {
        PremiumSettingsGroup(
            title: "settings.notifications.advanced.title".localized,
            subtitle: "settings.notifications.advanced.subtitle".localized,
            icon: "antenna.radiowaves.left.and.right",
            accent: .negativeRed
        ) {
            PremiumToggleRow(
                title: "ui.notificationSettings.15".localized,
                subtitle: "ui.notificationSettings.3".localized,
                icon: "waveform.path.ecg",
                accent: .negativeRed,
                isOn: $proactiveTransitAlerts
            )
            .onChange(of: proactiveTransitAlerts) { _, newValue in
                Task {
                    if newValue {
                        await TransitNotificationScheduler.shared.scanAndSchedule()
                    } else {
                        await TransitNotificationScheduler.shared.clearAll()
                    }
                }
            }

            if proactiveTransitAlerts {
                PremiumDivider()
                PremiumToggleRow(
                    title: "ui.notificationSettings.16".localized,
                    subtitle: "settings.notifications.majorOnly.detail".localized,
                    icon: "scope",
                    accent: .warningOrange,
                    isOn: $proactiveTransitMajorOnly
                )
                .onChange(of: proactiveTransitMajorOnly) { _, _ in
                    Task {
                        await TransitNotificationScheduler.shared.clearAll()
                        await TransitNotificationScheduler.shared.scanAndSchedule()
                    }
                }
            }
        }
    }

    private var habitsLink: some View {
        NavigationLink {
            HabitsView()
        } label: {
            PremiumActionCard(
                title: "ui.notificationSettings.8".localized,
                subtitle: "ui.notificationSettings.9".localized,
                icon: "checkmark.circle.fill",
                label: "settings.notifications.related".localized,
                accent: .positiveGreen
            )
        }
        .buttonStyle(ScaleButtonStyle())
    }

    private var permissionTitle: String {
        switch authorizationStatus {
        case .authorized, .provisional, .ephemeral:
            return "settings.notifications.permission.ready".localized
        case .denied:
            return "settings.notifications.permission.denied".localized
        case .notDetermined:
            return "settings.notifications.permission.notDetermined".localized
        @unknown default:
            return "settings.notifications.permission.unknown".localized
        }
    }

    private var permissionMessage: String {
        switch authorizationStatus {
        case .authorized, .provisional, .ephemeral:
            return "settings.notifications.permission.ready.body".localized
        case .denied:
            return "settings.notifications.permission.denied.body".localized
        case .notDetermined:
            return "settings.notifications.permission.notDetermined.body".localized
        @unknown default:
            return "settings.notifications.permission.unknown.body".localized
        }
    }

    private var permissionTone: PremiumStatusTone {
        switch authorizationStatus {
        case .authorized, .provisional, .ephemeral:
            return .success
        case .denied:
            return .warning
        case .notDetermined:
            return .info
        @unknown default:
            return .info
        }
    }
    
    @MainActor
    private func initializePermissionStatus() async {
        let status = await NotificationService.shared.checkPermissionStatus()
        authorizationStatus = status
        if status == .denied {
            statusText = "settings.notifications.disabledStatus".localized
        }
    }

    private func openAppSettings() {
        guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
        UIApplication.shared.open(url)
    }
    
    private func handleDailyReadingToggle(_ enabled: Bool) async {
        let granted = await requestPermissionIfNeeded()
        guard granted else {
            await MainActor.run { notifyDailyReading = false }
            return
        }
        if enabled {
            await rescheduleDailyReading()
        } else {
            await NotificationService.shared.cancelDailyReminder()
        }
    }
    
    private func rescheduleDailyReading() async {
        guard notifyDailyReading else { return }
        let comps = Calendar.current.dateComponents([.hour, .minute], from: dailyTime)
        await NotificationService.shared.scheduleDailyReminder(at: comps.hour ?? 9, minute: comps.minute ?? 0)
    }
    
    private func handleMoonEventsToggle(_ enabled: Bool) async {
        let granted = await requestPermissionIfNeeded()
        guard granted else {
            await MainActor.run { notifyMoonEvents = false }
            return
        }
        if enabled {
            await scheduleUpcomingMoonEvents()
        } else {
            await NotificationService.shared.cancelMoonPhaseNotifications()
        }
    }
    
    private func handleHabitToggle(_ enabled: Bool) async {
        let granted = await requestPermissionIfNeeded()
        guard granted else {
            await MainActor.run { notifyHabitReminder = false }
            return
        }
        if enabled {
            await rescheduleHabitReminder()
        } else {
            await NotificationService.shared.cancelHabitReminder(habitId: "daily_habits")
        }
    }
    
    private func rescheduleHabitReminder() async {
        guard notifyHabitReminder else { return }
        let comps = Calendar.current.dateComponents([.hour, .minute], from: habitTime)
        await NotificationService.shared.scheduleHabitReminder(habitId: "daily_habits", habitName: "Your habits", at: comps.hour ?? 20, minute: comps.minute ?? 0)
    }
    
    private func handleTimingToggle(_ enabled: Bool) async {
        let granted = await requestPermissionIfNeeded()
        guard granted else {
            await MainActor.run { notifyTimingAlert = false }
            return
        }
        if enabled {
            await rescheduleTimingReminder()
        } else {
            UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: ["timing_tip"])
        }
    }
    
    private func rescheduleTimingReminder() async {
        guard notifyTimingAlert else { return }
        let comps = Calendar.current.dateComponents([.hour, .minute], from: timingTime)
        let content = UNMutableNotificationContent()
        content.title = "⏳ Cosmic Timing"
        content.body = "Check today’s best windows for action."
        content.sound = .default
        
        var dateComponents = DateComponents()
        dateComponents.hour = comps.hour ?? 10
        dateComponents.minute = comps.minute ?? 0
        
        let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
        let request = UNNotificationRequest(identifier: "timing_tip", content: content, trigger: trigger)
        try? await UNUserNotificationCenter.current().add(request)
    }
    
    private func handleTransitToggle(_ enabled: Bool) async {
        let granted = await requestPermissionIfNeeded()
        guard granted else {
            await MainActor.run { notifyTransitAlert = false }
            return
        }
        if enabled {
            await rescheduleTransitAlert()
        } else {
            await NotificationService.shared.cancelTransitAlert()
        }
    }
    
    private func rescheduleTransitAlert() async {
        guard notifyTransitAlert else { return }
        let comps = Calendar.current.dateComponents([.hour, .minute], from: transitTime)
        await NotificationService.shared.scheduleTransitAlert(at: comps.hour ?? 9, minute: comps.minute ?? 0)
    }
    
    private func scheduleUpcomingMoonEvents() async {
        do {
            let events = try await alertPreferencesRepository.upcomingMoonEvents()
            for event in events {
                if let date = parseDate(event.date) {
                    let emoji = event.type.lowercased().contains("new") ? "🌑" : "🌕"
                    await NotificationService.shared.scheduleMoonPhaseNotification(phase: event.phase, emoji: emoji, date: date)
                }
            }
        } catch {
            await MainActor.run { statusText = error.localizedDescription }
        }
    }
    
    private func requestPermissionIfNeeded() async -> Bool {
        let status = await NotificationService.shared.checkPermissionStatus()
        await MainActor.run { authorizationStatus = status }
        if status == .notDetermined {
            let granted = await NotificationService.shared.requestPermission()
            let updatedStatus = await NotificationService.shared.checkPermissionStatus()
            await MainActor.run { authorizationStatus = updatedStatus }
            return granted
        }
        if status == .denied {
            await MainActor.run { statusText = "settings.notifications.enableInSettings".localized }
            return false
        }
        return true
    }
    
    private func parseDate(_ value: String) -> Date? {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: value)
    }
    
    private func loadAlertPreferences() async {
        // In personal/guest mode, keep preferences on-device.
        if AppConfig.personalMode || !store.isAuthenticated {
            return
        }
        do {
            let response = try await alertPreferencesRepository.loadPreferences()
            await MainActor.run {
                mercuryRetrogradeAlerts = response.alertMercuryRetrograde
                alertFrequency = response.alertFrequency
            }
        } catch {
            await MainActor.run { statusText = error.localizedDescription }
        }
    }
    
    private func updateAlertPreferences() async {
        // In personal/guest mode, AppStorage persists preferences locally.
        if AppConfig.personalMode || !store.isAuthenticated {
            return
        }
        do {
            _ = try await alertPreferencesRepository.updatePreferences(
                AlertPreferencesRequest(
                    alertMercuryRetrograde: mercuryRetrogradeAlerts,
                    alertFrequency: alertFrequency
                )
            )
        } catch {
            await MainActor.run { statusText = error.localizedDescription }
        }
    }
}

// MARK: - Upcoming Moon Events

struct UpcomingMoonEventsResponse: Codable {
    let events: [UpcomingMoonEvent]
    let daysAhead: Int
    
    enum CodingKeys: String, CodingKey {
        case events
        case daysAhead = "days_ahead"
    }
}

struct UpcomingMoonEvent: Codable, Identifiable {
    var id: String { date + type }
    let date: String
    let phase: String
    let type: String
    let description: String
}

private struct NotificationTimeRow: View {
    let title: String
    @Binding var date: Date
    let accent: Color
    let onChange: () -> Void

    var body: some View {
        DatePicker(title, selection: $date, displayedComponents: .hourAndMinute)
            .font(.subheadline.weight(.semibold))
            .foregroundStyle(Color.textPrimary)
            .tint(accent)
            .padding(.horizontal, Space.sm)
            .padding(.vertical, Space.xs)
            .background(
                RoundedRectangle(cornerRadius: Radius.sm)
                    .fill(accent.opacity(0.10))
                    .overlay(
                        RoundedRectangle(cornerRadius: Radius.sm)
                            .stroke(accent.opacity(0.22), lineWidth: Stroke.hairline)
                    )
            )
            .onChange(of: date) { _, _ in
                onChange()
            }
    }
}

#Preview {
    NotificationSettingsView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}

// MARK: - Alert Preferences (server-backed alert preference models)

struct AlertPreferencesResponse: Codable {
    let alertMercuryRetrograde: Bool
    let alertFrequency: String
    
    enum CodingKeys: String, CodingKey {
        case alertMercuryRetrograde = "alert_mercury_retrograde"
        case alertFrequency = "alert_frequency"
    }
}

struct AlertPreferencesRequest: Codable {
    let alertMercuryRetrograde: Bool
    let alertFrequency: String
    
    enum CodingKeys: String, CodingKey {
        case alertMercuryRetrograde = "alert_mercury_retrograde"
        case alertFrequency = "alert_frequency"
    }
}
