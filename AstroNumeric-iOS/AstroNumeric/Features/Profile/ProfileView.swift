// ProfileView.swift
// Profile management and settings

import SwiftUI
import HealthKit
import UIKit
import UserNotifications

struct ProfileView: View {
    @Environment(AppStore.self) private var store
    @State private var showCreateProfile = false
    @State private var editingProfile: Profile?
    @State private var profileToDelete: Profile?
    @State private var showDOB = false
    @State private var notificationStatus: UNAuthorizationStatus = .notDetermined
    @State private var pendingNotificationCount = 0
    @State private var nextDailyReminderDate: Date?
    @State private var nextDailyBriefDate: Date?
    @State private var nextTransitAlertDate: Date?
    @State private var hasAPNSToken = false
    @State private var widgetRefreshDiagnostics = WidgetRefreshDiagnostics.empty
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        PremiumHeroCard(
                            eyebrow: "hero.profile.eyebrow".localized,
                            title: "hero.profile.title".localized,
                            bodyText: "hero.profile.body".localized,
                            accent: [Color(hex: "201235"), Color(hex: "7b3fb6"), Color(hex: "2a7f92")],
                            chips: ["hero.profile.chip.0".localized, "hero.profile.chip.1".localized, "hero.profile.chip.2".localized, "hero.profile.chip.3".localized]
                        )

                        // Profile header
                        profileHeader

                        // Profiles (multi-profile support)
                        if !store.profiles.isEmpty {
                            profilesSection
                        }
                        
                        // Current profile or create prompt
                        if let profile = store.activeProfile {
                            currentProfileSection(profile)
                        } else {
                            noProfileSection
                        }
                        
                        // Settings
                        settingsSection

                        // Trust and support
                        trustSection
                        
#if DEBUG
                        systemDiagnosticsSection
#endif
                        
                        // App info
                        appInfoSection
                    }
                    .padding()
                    .readableContainer()
                }
            }
            .navigationTitle("nav.profile".localized)
        }
        .sheet(isPresented: $showCreateProfile) {
            EditProfileView()
        }
        .sheet(item: $editingProfile) { profile in
            EditProfileView(profile: profile)
        }
        .confirmationDialog(
            "Delete Profile?",
            isPresented: Binding(
                get: { profileToDelete != nil },
                set: { newValue in
                    if !newValue { profileToDelete = nil }
                }
            )
        ) {
            Button("action.delete".localized, role: .destructive) {
                guard let profileToDelete else { return }
                Task {
                    await deleteProfile(profileToDelete)
                    self.profileToDelete = nil
                }
            }
            Button("action.cancel".localized, role: .cancel) { profileToDelete = nil }
        } message: {
            Text("ui.profile.0".localized)
        }
    }
    
    // MARK: - Profile Header
    
    private var profileHeader: some View {
        VStack(spacing: 12) {
            // Avatar
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.purple, .pink],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 80, height: 80)

                if store.hideSensitiveDetailsEnabled {
                    Image(systemName: "lock.fill")
                        .font(.title.bold())
                        .foregroundStyle(.white)
                } else {
                    Text(store.activeProfile?.name.prefix(1).uppercased() ?? "?")
                        .font(.largeTitle.bold())
                        .foregroundStyle(.white)
                }
            }
            
            // Name
            if let profile = store.activeProfile {
                Text(profile.displayName(hideSensitive: store.hideSensitiveDetailsEnabled, role: .activeUser))
                    .font(.title2.bold())
            }
            
            // Local-first mode does not require an account email.
            
            // Streak
            if store.streakCount > 0 {
                HStack(spacing: 4) {
                    Text("🔥")
                    Text(String(format: "fmt.profile.1".localized, "\(store.streakCount)"))
                        .font(.label.weight(.medium))
                        .foregroundStyle(.orange)
                }
            }
        }
    }
    

    
    // MARK: - No Profile Section
    
    private var noProfileSection: some View {
        CardView {
            VStack(spacing: 16) {
                Image(systemName: "person.crop.circle.badge.plus")
                    .font(.system(.largeTitle))
                    .foregroundStyle(.purple)
                
                Text("ui.profile.1".localized)
                    .font(.headline)
                
                Text("ui.profile.2".localized)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)
                
                GradientButton("Create Profile", icon: "plus.circle.fill") {
                    showCreateProfile = true
                }

                Divider()

                ProfileExportImportButtons(profile: nil)
            }
            .padding(.vertical, 8)
        }
    }

    // MARK: - Profiles Section
    
    private var profilesSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("ui.profile.3".localized)
                        .font(.headline)
                    Spacer()
                    Button {
                        showCreateProfile = true
                    } label: {
                        Image(systemName: "plus.circle.fill")
                            .foregroundStyle(.purple)
                    }
                    .buttonStyle(AccessibleButtonStyle())
                    .accessibilityLabel("Create profile")
                    .accessibilityHint("Opens the create profile form")
                }
                
                ForEach(Array(store.profiles.enumerated()), id: \.element.id) { index, profile in
                    Button {
                        withAnimation(.spring(duration: 0.25)) {
                            store.selectedProfileId = profile.id
                        }
                        HapticManager.impact(.light)
                    } label: {
                        HStack(spacing: 12) {
                            ZStack {
                                Circle()
                                    .fill(Color.purple.opacity(0.2))
                                    .frame(width: 36, height: 36)
                                if store.hideSensitiveDetailsEnabled {
                                    Image(systemName: "person.fill")
                                        .foregroundStyle(.purple)
                                } else {
                                    Text(profile.name.prefix(1).uppercased())
                                        .font(.headline)
                                        .foregroundStyle(.purple)
                                }
                            }
                            
                            VStack(alignment: .leading, spacing: 2) {
                                Text(profile.displayName(
                                    hideSensitive: store.hideSensitiveDetailsEnabled,
                                    role: .genericProfile,
                                    index: index
                                ))
                                    .font(.subheadline.weight(.semibold))
                                Text((showDOB && !store.hideSensitiveDetailsEnabled) ? profile.dateOfBirth : PrivacyRedaction.maskedDate)
                                    .font(.meta)
                                    .foregroundStyle(Color.textSecondary)
                            }
                            
                            Spacer()
                            
                            if store.activeProfile?.id == profile.id {
                                Text("ui.profile.4".localized)
                                    .font(.caption.weight(.semibold))
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 6)
                                    .background(Capsule().fill(Color.purple.opacity(0.2)))
                                    .foregroundStyle(.purple)
                            } else {
                                Image(systemName: "chevron.right")
                                    .font(.label)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(profile.displayName(
                        hideSensitive: store.hideSensitiveDetailsEnabled,
                        role: .genericProfile,
                        index: index
                    ))
                    .accessibilityValue(store.activeProfile?.id == profile.id ? "tern.profile.0a".localized : "tern.profile.0b".localized)
                    .accessibilityHint("Switches to this profile")
                    .contextMenu {
                        Button {
                            editingProfile = profile
                        } label: {
                            Label("ui.profile.33".localized, systemImage: "pencil")
                        }
                        
                        Button(role: .destructive) {
                            profileToDelete = profile
                        } label: {
                            Label("ui.profile.34".localized, systemImage: "trash")
                        }
                    }
                    
                    if profile.id != store.profiles.last?.id {
                        Divider()
                    }
                }
            }
        }
    }
    
    // MARK: - Current Profile Section
    
    private func currentProfileSection(_ profile: Profile) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Text("ui.profile.5".localized)
                        .font(.headline)
                    
                    Spacer()
                    
                    Button {
                        editingProfile = profile
                    } label: {
                        HStack(spacing: 4) {
                            Image(systemName: "pencil")
                            Text("ui.profile.6".localized)
                        }
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(.purple)
                    }
                    .buttonStyle(AccessibleButtonStyle())
                }
                
                Button {
                    withAnimation {
                        if !store.hideSensitiveDetailsEnabled {
                            showDOB.toggle()
                        }
                    }
                } label: {
                    ProfileDetailRow(
                        icon: "calendar",
                        label: "Birth Date",
                        value: store.hideSensitiveDetailsEnabled
                            ? PrivacyRedaction.hiddenValue
                            : (showDOB ? formatDateForDisplay(profile.dateOfBirth) : "Tap to reveal")
                    )
                }
                .buttonStyle(AccessibleButtonStyle())
                .accessibilityLabel("Birth date")
                .accessibilityValue((showDOB && !store.hideSensitiveDetailsEnabled) ? formatDateForDisplay(profile.dateOfBirth) : "Hidden")
                .accessibilityHint(
                    store.hideSensitiveDetailsEnabled
                        ? "Privacy mode is hiding your birth date"
                        : (showDOB ? "tern.profile.1a".localized : "tern.profile.1b".localized)
                )
                
                if store.hideSensitiveDetailsEnabled {
                    ProfileDetailRow(icon: "clock", label: "Birth Time", value: profile.maskedBirthTime(hideSensitive: true))
                } else if let time = profile.timeOfBirth {
                    ProfileDetailRow(icon: "clock", label: "Birth Time", value: formatTimeForDisplay(time))
                } else {
                    ProfileDetailRow(icon: "clock", label: "Birth Time", value: "Not set")
                }
                
                if store.hideSensitiveDetailsEnabled {
                    ProfileDetailRow(icon: "mappin", label: "Birthplace", value: profile.maskedBirthplace(hideSensitive: true))
                } else if let place = profile.placeOfBirth {
                    ProfileDetailRow(icon: "mappin", label: "Birthplace", value: place)
                } else {
                    ProfileDetailRow(icon: "mappin", label: "Birthplace", value: "Not set")
                }
                
                Divider()
                
                // Export/Import buttons
                ProfileExportImportButtons(profile: profile)
            }
        }
    }
    
    // MARK: - Settings Section
    
    private var settingsSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 16) {
                PremiumSectionHeader(
                title: "section.profile.0.title".localized,
                subtitle: "section.profile.0.subtitle".localized
            )
                
                // Learn section link
                NavigationLink {
                    LearnView()
                } label: {
                    HStack(spacing: 12) {
                        Image(systemName: "book.fill")
                            .foregroundStyle(.blue)
                        Text("ui.profile.7".localized)
                            .font(.subheadline)
                            .foregroundStyle(.primary)
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.label)
                            .foregroundStyle(Color.textSecondary)
                    }
                }

                Divider()

                // Support links
                Group {
                    Text("ui.profile.8".localized)
                        .font(.label.weight(.semibold))
                        .foregroundStyle(Color.textSecondary)

                    NavigationLink {
                        UserGuideView()
                    } label: {
                        HStack(spacing: 12) {
                            Image(systemName: "map.fill")
                                .foregroundStyle(.teal)
                            Text("ui.profile.9".localized)
                                .font(.subheadline)
                                .foregroundStyle(.primary)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    .accessibilityLabel("User Guide")
                    .accessibilityHint("Comprehensive guide to all app features")

                    NavigationLink {
                        HelpView()
                    } label: {
                        HStack(spacing: 12) {
                            Image(systemName: "questionmark.circle.fill")
                                .foregroundStyle(.orange)
                            Text("ui.profile.10".localized)
                                .font(.subheadline)
                                .foregroundStyle(.primary)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    .accessibilityLabel("Help and Frequently Asked Questions")
                    .accessibilityHint("Searchable answers to common questions")

                    NavigationLink {
                        PrivacyView()
                    } label: {
                        HStack(spacing: 12) {
                            Image(systemName: "lock.shield.fill")
                                .foregroundStyle(.purple)
                            Text("ui.profile.11".localized)
                                .font(.subheadline)
                                .foregroundStyle(.primary)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    .accessibilityLabel("Privacy Policy")
                    .accessibilityHint("How your data is collected, stored, and protected")
                }

                Divider()

                Link(destination: supportEmailURL) {
                    HStack(spacing: 12) {
                        Image(systemName: "envelope.fill")
                            .foregroundStyle(.green)
                        VStack(alignment: .leading, spacing: 2) {
                            Text("ui.profile.12".localized)
                                .font(.subheadline)
                                .foregroundStyle(.primary)
                            Text("ui.profile.13".localized)
                                .font(.meta)
                                .foregroundStyle(Color.textSecondary)
                        }
                        Spacer()
                        Image(systemName: "arrow.up.forward")
                            .font(.label)
                            .foregroundStyle(Color.textSecondary)
                    }
                }
                .accessibilityLabel("Email support")
                .accessibilityHint("Creates an email with app version and device details, without birth data")

                Divider()

                Toggle(isOn: Binding(
                    get: { store.hideSensitiveDetailsEnabled },
                    set: { newValue in
                        let wasEnabled = store.hideSensitiveDetailsEnabled
                        store.hideSensitiveDetailsEnabled = newValue
                        if newValue {
                            showDOB = false
                        }
                        if newValue && !wasEnabled {
                            RelationshipsVM.scrubStoredSensitiveDetails()
                            Task { await ResponseCache.shared.clearAll() }
                        }
                    }
                )) {
                    HStack(spacing: 12) {
                        Image(systemName: "eye.slash.fill")
                            .foregroundStyle(.purple)
                        VStack(alignment: .leading, spacing: 2) {
                            Text("ui.profile.14".localized)
                                .font(.subheadline)
                            Text("ui.profile.15".localized)
                                .font(.meta)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                }
                .tint(.purple)
                
                // Daily reminder toggle
                Toggle(isOn: Binding(
                    get: { store.dailyReminderEnabled },
                    set: { newValue in
                        store.dailyReminderEnabled = newValue
                        if newValue {
                            requestNotificationPermission()
                        }
                    }
                )) {
                    HStack(spacing: 12) {
                        Image(systemName: "bell.fill")
                            .foregroundStyle(.purple)
                        Text("ui.profile.16".localized)
                            .font(.subheadline)
                    }
                }
                .tint(.purple)
                
                Divider()
                
                // Language selector — temporarily hidden until full UI translation lands.
                // Re-enable once all `Text(...)` literals are routed through `.localized`.
                // LanguageSelectorRow()
                // Divider()
                
                // Tone preference
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text("ui.profile.17".localized)
                            .font(.subheadline)
                        Spacer()
                        Text(toneLabel)
                            .font(.label)
                            .foregroundStyle(Color.textSecondary)
                    }
                    
                    Slider(
                        value: Binding(
                            get: { store.tonePreference },
                            set: { store.tonePreference = $0 }
                        ),
                        in: 0...100
                    )
                    .tint(.purple)
                    
                    HStack {
                        Text("ui.profile.18".localized)
                            .font(.meta)
                            .foregroundStyle(Color.textSecondary)
                        Spacer()
                        Text("ui.profile.19".localized)
                            .font(.meta)
                            .foregroundStyle(Color.textSecondary)
                    }
                }
                
                Divider()
                
                // Accessibility section
                VStack(alignment: .leading, spacing: 12) {
                    Text("ui.profile.20".localized)
                        .font(.label.weight(.semibold))
                        .foregroundStyle(Color.textSecondary)
                    
                    Toggle(isOn: Binding(
                        get: { store.highContrastEnabled },
                        set: { store.highContrastEnabled = $0 }
                    )) {
                        HStack(spacing: 12) {
                            Image(systemName: "circle.lefthalf.filled")
                                .foregroundStyle(.orange)
                            VStack(alignment: .leading, spacing: 2) {
                                Text("ui.profile.21".localized)
                                    .font(.subheadline)
                                Text("ui.profile.22".localized)
                                    .font(.meta)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                    }
                    .tint(.orange)
                    
                    Toggle(isOn: Binding(
                        get: { store.largeTextEnabled },
                        set: { store.largeTextEnabled = $0 }
                    )) {
                        HStack(spacing: 12) {
                            Image(systemName: "textformat.size.larger")
                                .foregroundStyle(.blue)
                            VStack(alignment: .leading, spacing: 2) {
                                Text("ui.profile.23".localized)
                                    .font(.subheadline)
                                Text("ui.profile.24".localized)
                                    .font(.meta)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                    }
                    .tint(.blue)
                }
            }
        }
    }

    // MARK: - Trust Section

    private var trustSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 14) {
                PremiumSectionHeader(
                title: "section.profile.1.title".localized,
                subtitle: "section.profile.1.subtitle".localized
            )

                trustPoint(
                    icon: "lock.fill",
                    title: "Private profile by default",
                    detail: "Birth profiles and preferences start on this device."
                )

                trustPoint(
                    icon: "eye.slash.fill",
                    title: "Privacy mode",
                    detail: "Names, birth details, share cards, and cached identifiers can be masked."
                )

                trustPoint(
                    icon: "network",
                    title: "Clear backend boundary",
                    detail: "Forecasts, AI guidance, friend sync, widgets, and notifications use the backend only when those features need it."
                )

                Link(destination: supportEmailURL) {
                    Label("ui.profile.35".localized, systemImage: "envelope.fill")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(Color.green.opacity(0.18))
                        .foregroundStyle(.green)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .accessibilityHint("Creates a privacy-safe support email with app version and device details")
            }
        }
    }

    private func trustPoint(icon: String, title: String, detail: String) -> some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon)
                .foregroundStyle(.purple)
                .frame(width: 24)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                Text(detail)
                    .font(.meta)
                    .foregroundStyle(Color.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
    
    private var toneLabel: String {
        switch store.tonePreference {
        case 0..<25: return "Very Practical"
        case 25..<50: return "Balanced Practical"
        case 50..<75: return "Balanced Mystical"
        default: return "Very Mystical"
        }
    }
    
    // MARK: - Date/Time Formatting
    
    private func formatDateForDisplay(_ dateString: String) -> String {
        let inputFormatter = DateFormatter()
        inputFormatter.dateFormat = "yyyy-MM-dd"
        
        guard let date = inputFormatter.date(from: dateString) else {
            return dateString
        }
        
        let outputFormatter = DateFormatter()
        outputFormatter.dateStyle = .long
        return outputFormatter.string(from: date)
    }
    
    private func formatTimeForDisplay(_ timeString: String) -> String {
        let inputFormatter = DateFormatter()
        inputFormatter.locale = Locale(identifier: "en_US_POSIX")
        inputFormatter.timeZone = TimeZone(identifier: "UTC")

        for format in ["HH:mm:ss", "HH:mm"] {
            inputFormatter.dateFormat = format
            if let time = inputFormatter.date(from: timeString) {
                let outputFormatter = DateFormatter()
                outputFormatter.timeStyle = .short
                return outputFormatter.string(from: time)
            }
        }

        return timeString
    }
    

    // MARK: - App Info Section
    
    private var appInfoSection: some View {
        VStack(spacing: 8) {
            Text("ui.profile.25".localized)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
            
            Text("ui.profile.26".localized)
                .font(.meta)
                .foregroundStyle(Color.textSecondary)

            Text(appVersionText)
                .font(.meta)
                .foregroundStyle(Color.textSecondary)
        }
        .padding(.top)
    }

    private var appVersionText: String {
        let version = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "?"
        let build = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "?"
        return "Version \(version) (\(build))"
    }

    private var supportEmailURL: URL {
        var components = URLComponents()
        components.scheme = "mailto"
        components.path = "support@astromeric.app"
        components.queryItems = [
            URLQueryItem(name: "subject", value: "AstroNumeric iOS Support"),
            URLQueryItem(name: "body", value: supportEmailBody)
        ]
        return components.url ?? URL(string: "mailto:support@astromeric.app")!
    }

    private var supportEmailBody: String {
        let device = UIDevice.current
        return """
        Please describe what happened:

        Screen or feature:
        Expected result:
        Actual result:
        Steps to reproduce:

        ---
        Diagnostics
        \(appVersionText)
        iOS \(device.systemVersion)
        Device: \(device.model)
        Profiles on device: \(store.profiles.count)
        Privacy mode: \(store.hideSensitiveDetailsEnabled ? "tern.profile.2a".localized : "tern.profile.2b".localized)

        No birth date, birth time, birthplace, journal text, or chart data is included automatically.
        """
    }
    
    // MARK: - Helpers
    
    private func requestNotificationPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, _ in
            if !granted {
                DispatchQueue.main.async {
                    store.dailyReminderEnabled = false
                }
            }
        }
    }

    @MainActor
    private func deleteProfile(_ profile: Profile) async {
        store.deleteProfileLocal(id: profile.id)
    }

    @MainActor
    private func refreshSystemDiagnostics() async {
        cacheMemCount = await ResponseCache.shared.entryCount
        cacheDiskCount = await ResponseCache.shared.diskEntryCount
        notificationStatus = await NotificationService.shared.checkPermissionStatus()

        let pendingRequests = await NotificationService.shared.listPendingNotifications()
        pendingNotificationCount = pendingRequests.count
        nextDailyReminderDate = nextTriggerDate(for: "daily_reminder", in: pendingRequests)
        nextDailyBriefDate = nextTriggerDate(for: "daily_brief", in: pendingRequests)
        nextTransitAlertDate = nextTriggerDate(for: "daily_transit_alert", in: pendingRequests)
        hasAPNSToken = !(UserDefaults.standard.string(forKey: "apns_device_token")?.isEmpty ?? true)
        widgetRefreshDiagnostics = WidgetDataProvider.readRefreshDiagnostics()
    }

    private func nextTriggerDate(for identifier: String, in requests: [UNNotificationRequest]) -> Date? {
        guard let request = requests.first(where: { $0.identifier == identifier }) else {
            return nil
        }
        if let trigger = request.trigger as? UNCalendarNotificationTrigger {
            return trigger.nextTriggerDate()
        }
        return nil
    }

    private func notificationStatusLabel(_ status: UNAuthorizationStatus) -> String {
        switch status {
        case .authorized: return "AUTHORIZED"
        case .provisional: return "PROVISIONAL"
        case .ephemeral: return "EPHEMERAL"
        case .denied: return "DENIED"
        case .notDetermined: return "NOT ASKED"
        @unknown default: return "UNKNOWN"
        }
    }

    private func notificationStatusColor(_ status: UNAuthorizationStatus) -> Color {
        switch status {
        case .authorized, .provisional, .ephemeral:
            return .green
        case .denied:
            return .red
        case .notDetermined:
            return .orange
        @unknown default:
            return .orange
        }
    }

    @ViewBuilder
    private func diagnosticStatusRow(title: String, status: String, color: Color) -> some View {
        HStack {
            Circle()
                .fill(color)
                .frame(width: 8, height: 8)
            Text(title)
                .font(.subheadline)
            Spacer()
            Text(status)
                .font(.caption.monospaced())
                .foregroundStyle(color)
        }
    }

    @ViewBuilder
    private func diagnosticValueRow(title: String, value: String, accent: Color = .orange) -> some View {
        HStack {
            Image(systemName: "smallcircle.filled.circle")
                .font(.caption2)
                .foregroundStyle(accent)
                .frame(width: 8)
            Text(title)
                .font(.subheadline)
            Spacer()
            Text(value)
                .font(.caption.monospaced())
                .foregroundStyle(accent)
        }
    }

    @ViewBuilder
    private func diagnosticScheduleRow(title: String, date: Date?, fallback: String) -> some View {
        HStack {
            Image(systemName: "clock")
                .font(.caption2)
                .foregroundStyle(date == nil ? Color.orange : .green)
                .frame(width: 8)
            Text(title)
                .font(.subheadline)
            Spacer()
            if let date {
                Text(date, style: .relative)
                    .font(.caption.monospaced())
                    .foregroundStyle(Color.textSecondary)
            } else {
                Text(fallback)
                    .font(.caption.monospaced())
                    .foregroundStyle(.orange)
            }
        }
    }
    
    // MARK: - System Diagnostics
    
    @State private var cacheMemCount = 0
    @State private var cacheDiskCount = 0
    
    private var systemDiagnosticsSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    HStack(spacing: 8) {
                        Image(systemName: "wrench.and.screwdriver")
                            .foregroundStyle(.red)
                        Text("ui.profile.27".localized)
                            .font(.headline)
                    }
                    Spacer()
                    Button {
                        Task { await refreshSystemDiagnostics() }
                    } label: {
                        Image(systemName: "arrow.clockwise")
                            .foregroundStyle(.purple)
                            .frame(width: 44, height: 44)
                            .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel("Refresh diagnostics")
                    .accessibilityHint("Reloads cache, widget, and notification status")
                }
                
                Divider()
                
                // Ephemeris Engine
                HStack {
                    Circle()
                        .fill(.green)
                        .frame(width: 8, height: 8)
                    Text("ui.profile.28".localized)
                        .font(.subheadline)
                    Spacer()
                    Text("ui.profile.29".localized)
                        .font(.caption.monospaced())
                        .foregroundStyle(.green)
                }
                
                // ResponseCache
                HStack {
                    Circle()
                        .fill(.green)
                        .frame(width: 8, height: 8)
                    Text("ui.profile.30".localized)
                        .font(.subheadline)
                    Spacer()
                    Text(String(format: "fmt.profile.0".localized, "\(cacheMemCount)", "\(cacheDiskCount)"))
                        .font(.caption.monospaced())
                        .foregroundStyle(.orange)
                }
                
                // HealthKit
                HStack {
                    Circle()
                        .fill(HKHealthStore.isHealthDataAvailable() ? .green : .red)
                        .frame(width: 8, height: 8)
                    Text("ui.profile.31".localized)
                        .font(.subheadline)
                    Spacer()
                    Text(HKHealthStore.isHealthDataAvailable() ? "tern.profile.3a".localized : "tern.profile.3b".localized)
                        .font(.caption.monospaced())
                        .foregroundStyle(HKHealthStore.isHealthDataAvailable() ? .green : .red)
                }

                Divider()

                diagnosticStatusRow(
                    title: "Notifications",
                    status: notificationStatusLabel(notificationStatus),
                    color: notificationStatusColor(notificationStatus)
                )

                diagnosticValueRow(title: "Pending Requests", value: "\(pendingNotificationCount)")

                diagnosticValueRow(
                    title: "APNs Token",
                    value: hasAPNSToken ? "tern.profile.4a".localized : "tern.profile.4b".localized,
                    accent: hasAPNSToken ? .green : .orange
                )

                diagnosticScheduleRow(
                    title: "Daily Reminder",
                    date: nextDailyReminderDate,
                    fallback: store.dailyReminderEnabled ? "tern.profile.5a".localized : "tern.profile.5b".localized
                )

                diagnosticScheduleRow(
                    title: "Morning Brief",
                    date: nextDailyBriefDate,
                    fallback: "NOT SCHEDULED"
                )

                diagnosticScheduleRow(
                    title: "Transit Alert",
                    date: nextTransitAlertDate,
                    fallback: "NOT SCHEDULED"
                )

                Divider()

                diagnosticScheduleRow(
                    title: "Widget Sync",
                    date: widgetRefreshDiagnostics.overall,
                    fallback: "NO SHARED DATA"
                )

                diagnosticScheduleRow(
                    title: "Morning Brief Cache",
                    date: widgetRefreshDiagnostics.morningBrief,
                    fallback: "EMPTY"
                )

                diagnosticScheduleRow(
                    title: "Daily Summary Cache",
                    date: widgetRefreshDiagnostics.dailySummary,
                    fallback: "EMPTY"
                )

                diagnosticScheduleRow(
                    title: "Planetary Hour Cache",
                    date: widgetRefreshDiagnostics.planetaryHour,
                    fallback: "EMPTY"
                )

                diagnosticScheduleRow(
                    title: "Moon Phase Cache",
                    date: widgetRefreshDiagnostics.moonPhase,
                    fallback: "EMPTY"
                )
                
                // App Version
                HStack {
                    Image(systemName: "info.circle")
                        .foregroundStyle(.purple)
                        .frame(width: 8)
                    Text("ui.profile.32".localized)
                        .font(.subheadline)
                    Spacer()
                    let version = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "?"
                    let build = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "?"
                    Text("v\(version) (\(build))")
                        .font(.caption.monospaced())
                        .foregroundStyle(Color.textSecondary)
                }
            }
        }
        .task {
            await refreshSystemDiagnostics()
        }
    }
}

// MARK: - Profile Detail Row

struct ProfileDetailRow: View {
    let icon: String
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundStyle(.purple)
                .frame(width: 24)
            
            Text(label)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
            
            Spacer()
            
            Text(value)
                .font(.subheadline)
        }
    }
}

// MARK: - Preview

#Preview {
    ProfileView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
