// NotificationSettingsView.swift
// Notification preferences and scheduling

import SwiftUI

struct NotificationSettingsView: View {
    @Environment(AppStore.self) private var store
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
                    VStack(spacing: 16) {
                        PremiumHeroCard(
                            eyebrow: "hero.notificationSettings.eyebrow".localized,
                            title: "hero.notificationSettings.title".localized,
                            bodyText: "hero.notificationSettings.body".localized,
                            accent: [Color(hex: "1c1639"), Color(hex: "6c44b5"), Color(hex: "1a8a87")],
                            chips: ["hero.notificationSettings.chip.0".localized, "hero.notificationSettings.chip.1".localized, "hero.notificationSettings.chip.2".localized, "hero.notificationSettings.chip.3".localized]
                        )

                        CardView {
                            VStack(alignment: .leading, spacing: 12) {
                                Text("ui.notificationSettings.0".localized)
                                    .font(.headline)
                                Text("ui.notificationSettings.1".localized)
                                    .font(.caption)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }

                        PremiumSectionHeader(
                title: "section.notificationSettings.0.title".localized,
                subtitle: "section.notificationSettings.0.subtitle".localized
            )
                        
                        Toggle("ui.notificationSettings.10".localized, isOn: $notifyDailyReading)
                            .tint(.purple)
                            .onChange(of: notifyDailyReading) { _, newValue in
                                Task { await handleDailyReadingToggle(newValue) }
                            }
                        DatePicker("Daily Time", selection: $dailyTime, displayedComponents: .hourAndMinute)
                            .onChange(of: dailyTime) { _, _ in
                                Task { await rescheduleDailyReading() }
                            }
                        
                        Toggle("ui.notificationSettings.11".localized, isOn: $notifyMoonEvents)
                            .tint(.indigo)
                            .onChange(of: notifyMoonEvents) { _, newValue in
                                Task { await handleMoonEventsToggle(newValue) }
                            }
                        
                        Toggle("ui.notificationSettings.12".localized, isOn: $notifyHabitReminder)
                            .tint(.green)
                            .onChange(of: notifyHabitReminder) { _, newValue in
                                Task { await handleHabitToggle(newValue) }
                            }
                        DatePicker("Habit Time", selection: $habitTime, displayedComponents: .hourAndMinute)
                            .onChange(of: habitTime) { _, _ in
                                Task { await rescheduleHabitReminder() }
                            }
                        
                        Toggle("ui.notificationSettings.13".localized, isOn: $notifyTransitAlert)
                            .tint(.pink)
                            .onChange(of: notifyTransitAlert) { _, newValue in
                                Task { await handleTransitToggle(newValue) }
                            }
                        DatePicker("Transit Time", selection: $transitTime, displayedComponents: .hourAndMinute)
                            .onChange(of: transitTime) { _, _ in
                                Task { await rescheduleTransitAlert() }
                            }
                        
                        Toggle("ui.notificationSettings.14".localized, isOn: $notifyTimingAlert)
                            .tint(.orange)
                            .onChange(of: notifyTimingAlert) { _, newValue in
                                Task { await handleTimingToggle(newValue) }
                            }
                        DatePicker("Timing Time", selection: $timingTime, displayedComponents: .hourAndMinute)
                            .onChange(of: timingTime) { _, _ in
                                Task { await rescheduleTimingReminder() }
                            }
                        
                        Divider().opacity(0.3)

                        // MARK: - Proactive Transit Alerts (PredictiveScanner → Push)
                        Text("ui.notificationSettings.2".localized)
                            .font(.system(.caption, design: .monospaced)).fontWeight(.bold)
                            .foregroundStyle(.white.opacity(0.5))
                            .frame(maxWidth: .infinity, alignment: .leading)

                        Toggle("ui.notificationSettings.15".localized, isOn: $proactiveTransitAlerts)
                            .tint(.red)
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
                            Toggle("ui.notificationSettings.16".localized, isOn: $proactiveTransitMajorOnly)
                                .tint(.orange)
                                .onChange(of: proactiveTransitMajorOnly) { _, _ in
                                    Task {
                                        await TransitNotificationScheduler.shared.clearAll()
                                        await TransitNotificationScheduler.shared.scanAndSchedule()
                                    }
                                }
                            Text("ui.notificationSettings.3".localized)
                                .font(.caption)
                                .foregroundStyle(.white.opacity(0.4))
                        }

                        Divider().opacity(0.3)
                        
                        Toggle("ui.notificationSettings.17".localized, isOn: $mercuryRetrogradeAlerts)
                            .tint(.pink)
                            .onChange(of: mercuryRetrogradeAlerts) { _, _ in
                                Task { await updateAlertPreferences() }
                            }
                        Picker("ui.notificationSettings.18".localized, selection: $alertFrequency) {
                            Text("ui.notificationSettings.4".localized).tag("every_retrograde")
                            Text("ui.notificationSettings.5".localized).tag("weekly_digest")
                            Text("ui.notificationSettings.6".localized).tag("once_per_year")
                            Text("ui.notificationSettings.7".localized).tag("none")
                        }
                        .onChange(of: alertFrequency) { _, _ in
                            Task { await updateAlertPreferences() }
                        }
                        
                        if let statusText {
                            Text(statusText)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                        }
                        
                        NavigationLink {
                            HabitsView()
                        } label: {
                            CardView {
                                HStack {
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("ui.notificationSettings.8".localized)
                                            .font(.headline)
                                        Text("ui.notificationSettings.9".localized)
                                            .font(.caption)
                                            .foregroundStyle(Color.textSecondary)
                                    }
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }
                        }
                        .buttonStyle(.plain)
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
    
    @MainActor
    private func initializePermissionStatus() async {
        let status = await NotificationService.shared.checkPermissionStatus()
        if status == .denied {
            statusText = "Notifications are disabled in iOS Settings."
        }
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
            let response: V2ApiResponse<UpcomingMoonEventsResponse> = try await APIClient.shared.fetch(.upcomingMoonEvents)
            let events = response.data.events
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
        if status == .notDetermined {
            return await NotificationService.shared.requestPermission()
        }
        if status == .denied {
            await MainActor.run { statusText = "Enable notifications in iOS Settings." }
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
            let response: AlertPreferencesResponse = try await APIClient.shared.fetch(.alertPreferences)
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
            let _: AlertPreferencesResponse = try await APIClient.shared.fetch(
                .updateAlertPreferences(
                    AlertPreferencesRequest(
                        alertMercuryRetrograde: mercuryRetrogradeAlerts,
                        alertFrequency: alertFrequency
                    )
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
