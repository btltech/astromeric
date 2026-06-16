// ContentView.swift
// Root navigation with 4-tab structure and Explore hub + Floating AI Button

import SwiftUI

struct ContentView: View {
    @Environment(AppStore.self) private var store
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @State private var selectedTab: Tab = .home
    @State private var showCreateProfile = false
    @State private var pendingFirstRunProfileCompletion = false
    @State private var profileCountBeforeCreate = 0
    @State private var showFirstRunProfileComplete = false
    @AppStorage("firstRunProfilePromptDismissed") private var firstRunProfilePromptDismissed = false
    @AppStorage("firstRunProfileCompletionShown") private var firstRunProfileCompletionShown = false
    private let localization = LocalizationService.shared
    
    enum Tab: String, CaseIterable {
        case home = "Home"
        case explore = "Explore"
        case charts = "Charts"
        case profile = "Profile"
        
        var icon: String {
            switch self {
            case .home: return "house.fill"
            case .explore: return "safari.fill"
            case .charts: return "chart.pie.fill"
            case .profile: return "person.circle"
            }
        }

        /// Localized tab label (uses tab.* keys from Localizable.strings).
        var label: String {
            switch self {
            case .home: return "tab.home".localized
            case .explore: return "nav.explore".localized
            case .charts: return "tab.charts".localized
            case .profile: return "tab.profile".localized
            }
        }
    }
    
    init() {
        // Configure tab bar appearance - lighter and shorter
        let appearance = UITabBarAppearance()
        appearance.configureWithTransparentBackground()
        appearance.backgroundEffect = UIBlurEffect(style: .systemUltraThinMaterial)
        appearance.backgroundColor = UIColor(Color.appBackground).withAlphaComponent(0.9)
        
        // Softer selected indicator
        appearance.stackedLayoutAppearance.selected.iconColor = UIColor(Color.cosmicPurple)
        appearance.stackedLayoutAppearance.selected.titleTextAttributes = [
            .foregroundColor: UIColor(Color.cosmicPurple),
            .font: UIFont.systemFont(ofSize: 10, weight: .semibold)
        ]
        appearance.stackedLayoutAppearance.normal.titleTextAttributes = [
            .foregroundColor: UIColor.tertiaryLabel,
            .font: UIFont.systemFont(ofSize: 10, weight: .medium)
        ]
        
        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
    }
    
    var body: some View {
        // Boot directly into the primary app experience.
        mainTabView
            // Force refresh when language changes
            .id(localization.refreshID)
            // Propagate selected language to SwiftUI's Locale-aware formatters
            .environment(\.locale, Locale(identifier: localization.currentLanguage.rawValue))
            // Apply accessibility preferences (High Contrast, Large Text)
            .accessibilityPreferences(store)
    }
    
    private var mainTabView: some View {
        ZStack {
            // Single shared cosmic background behind all tabs
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
                .allowsHitTesting(false)
            
            TabView(selection: $selectedTab) {
                HomeView()
                    .tabItem {
                        Label(Tab.home.label, systemImage: Tab.home.icon)
                    }
                    .tag(Tab.home)
                
                ExploreView()
                    .tabItem {
                        Label(Tab.explore.label, systemImage: Tab.explore.icon)
                    }
                    .tag(Tab.explore)
                
                ChartsView()
                    .tabItem {
                        Label(Tab.charts.label, systemImage: Tab.charts.icon)
                    }
                    .tag(Tab.charts)
                
                ProfileView()
                    .tabItem {
                        Label(Tab.profile.label, systemImage: Tab.profile.icon)
                    }
                    .tag(Tab.profile)
            }
            .tint(Color.accentColor)
            .symbolRenderingMode(.hierarchical)
            .adaptiveTabViewStyle() // iPad: sidebar; iPhone: bottom tab bar

            // Selected tab indicator dot (above tab bar). Hidden on iPad
            // sidebar mode where the bottom tab bar isn't shown.
            TabSelectedDot(selectedTab: selectedTab, tabCount: Tab.allCases.count)
                .allowsHitTesting(false)
                .opacity(horizontalSizeClass == .regular ? 0 : 1)
            
            // Floating AI Button overlay - hide on Profile tab
            if selectedTab != .profile {
                FloatingAIButton()
            }

            if shouldShowFirstRunPrompt {
                FirstRunProfilePromptView(
                    onCreateProfile: {
                        profileCountBeforeCreate = store.profiles.count
                        pendingFirstRunProfileCompletion = true
                        showCreateProfile = true
                    },
                    onExploreFirst: {
                        firstRunProfilePromptDismissed = true
                    }
                )
                .transition(.opacity.combined(with: .scale(scale: 0.98)))
                .zIndex(2)
            }

            if showFirstRunProfileComplete, let profile = store.activeProfile {
                FirstRunProfileCompleteView(
                    profile: profile,
                    moonSign: store.activeMoonSign,
                    risingSign: store.activeRisingSign,
                    primaryRecommendation: TodayRecommendation.make(profile: profile),
                    onPrimaryAction: {
                        finishFirstRunProfileComplete()
                        openTodayDestination(TodayRecommendation.make(profile: profile).destination)
                    },
                    onChart: {
                        finishFirstRunProfileComplete()
                        selectedTab = .charts
                    },
                    onDismiss: finishFirstRunProfileComplete
                )
                .transition(.opacity.combined(with: .scale(scale: 0.98)))
                .zIndex(3)
            }
        }
        .animation(.easeInOut(duration: 0.2), value: shouldShowFirstRunPrompt)
        .animation(.easeInOut(duration: 0.2), value: showFirstRunProfileComplete)
        .sheet(isPresented: $showCreateProfile, onDismiss: handleCreateProfileDismissal) {
            EditProfileView()
                .environment(store)
        }
        // Handle push notification navigation
        .onReceive(NotificationCenter.default.publisher(for: .navigateToTab)) { notification in
            if let tabIndex = notification.userInfo?["tab"] as? Int {
                let tabs: [Tab] = [.home, .explore, .charts, .profile]
                if tabIndex >= 0 && tabIndex < tabs.count {
                    selectedTab = tabs[tabIndex]
                }
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: .openTodayDestination)) { _ in
            selectedTab = .home
        }
    }

    private var shouldShowFirstRunPrompt: Bool {
        store.hasCompletedInitialLoad &&
        store.profiles.isEmpty &&
        !firstRunProfilePromptDismissed
    }

    private func handleCreateProfileDismissal() {
        guard pendingFirstRunProfileCompletion else { return }
        pendingFirstRunProfileCompletion = false

        guard store.profiles.count > profileCountBeforeCreate,
              let profile = store.activeProfile,
              !firstRunProfileCompletionShown else {
            return
        }

        firstRunProfilePromptDismissed = true
        selectedTab = .home
        showFirstRunProfileComplete = true

        Task {
            await store.fetchNatalSigns(for: profile)
        }
    }

    private func finishFirstRunProfileComplete() {
        firstRunProfileCompletionShown = true
        showFirstRunProfileComplete = false
    }

    private func openTodayDestination(_ destination: TodayDestination) {
        selectedTab = .home
        DispatchQueue.main.async {
            NotificationCenter.default.post(
                name: .openTodayDestination,
                object: nil,
                userInfo: destination.notificationUserInfo
            )
        }
    }
}

enum TodayDestination: String, Identifiable {
    case createProfile
    case editProfile
    case reading
    case timing
    case journal
    case numerology
    case moonPhase

    var id: String { rawValue }

    static func from(userInfo: [AnyHashable: Any]?) -> TodayDestination? {
        guard let rawValue = userInfo?["destination"] as? String else { return nil }
        return TodayDestination(rawValue: rawValue)
    }

    var notificationUserInfo: [AnyHashable: Any] {
        ["destination": rawValue]
    }
}

struct TodayRecommendationContext {
    var hasReading = false
    var habitsCompletedToday = 0
    var totalHabits = 0
    var dailyAdvice: String?

    static let empty = TodayRecommendationContext()
}

struct TodayRecommendation {
    let title: String
    let subtitle: String
    let icon: String
    let label: String
    let ctaTitle: String
    let accent: Color
    let destination: TodayDestination

    static func make(
        profile: Profile?,
        context: TodayRecommendationContext = .empty
    ) -> TodayRecommendation {
        guard let profile else {
            return TodayRecommendation(
                title: "Create your birth profile",
                subtitle: "Add your birth details to unlock today’s reading, timing, and moon context.",
                icon: "person.crop.circle.badge.plus",
                label: "Start Here",
                ctaTitle: "Create Profile",
                accent: .accentPrimary,
                destination: .createProfile
            )
        }

        switch profile.dataQuality {
        case .dateOnly:
            return TodayRecommendation(
                title: "Add your birth place",
                subtitle: "Your Sun sign is ready, but place and time unlock a sharper chart and daily timing.",
                icon: "mappin.and.ellipse",
                label: "Sharpen Chart",
                ctaTitle: "Add Birth Place",
                accent: .orange,
                destination: .editProfile
            )
        case .dateAndPlace:
            return TodayRecommendation(
                title: "Add your birth time",
                subtitle: "Unlock your rising sign, houses, and tighter timing windows with one update.",
                icon: "clock.badge.exclamationmark",
                label: "Sharpen Chart",
                ctaTitle: "Add Birth Time",
                accent: .orange,
                destination: .editProfile
            )
        case .full:
            break
        }

        if !context.hasReading {
            return TodayRecommendation(
                title: "Open your daily guide",
                subtitle: "Your chart, numbers, and live sky are ready for today.",
                icon: "sparkles",
                label: "Today",
                ctaTitle: "Open Daily Guide",
                accent: .accentPrimary,
                destination: .reading
            )
        }

        if context.totalHabits > 0 && context.habitsCompletedToday == 0 {
            return TodayRecommendation(
                title: "Place your key move",
                subtitle: "Check the strongest window before the day gets noisy.",
                icon: "clock.badge.checkmark.fill",
                label: "Right Now",
                ctaTitle: "Check Timing",
                accent: .green,
                destination: .timing
            )
        }

        if let advice = condensed(context.dailyAdvice) {
            return TodayRecommendation(
                title: "Keep today’s cue close",
                subtitle: advice,
                icon: "book.closed.fill",
                label: "Reflect",
                ctaTitle: "Open Journal",
                accent: .cosmicPurple,
                destination: .journal
            )
        }

        return TodayRecommendation(
            title: "Review your timing",
            subtitle: "Use the live sky to place your most important call, launch, or conversation.",
            icon: "clock.badge.checkmark.fill",
            label: "Recommended",
            ctaTitle: "Review Timing",
            accent: .cosmicPurple,
            destination: .timing
        )
    }

    private static func condensed(_ advice: String?) -> String? {
        guard let advice = advice?
            .replacingOccurrences(of: "\n", with: " ")
            .trimmingCharacters(in: .whitespacesAndNewlines),
            !advice.isEmpty else {
            return nil
        }

        guard advice.count > 96 else { return advice }
        let endIndex = advice.index(advice.startIndex, offsetBy: 93)
        return String(advice[..<endIndex]) + "..."
    }
}

extension Notification.Name {
    static let openTodayDestination = Notification.Name("openTodayDestination")
}

private struct FirstRunProfilePromptView: View {
    let onCreateProfile: () -> Void
    let onExploreFirst: () -> Void

    var body: some View {
        ZStack {
            Color.black.opacity(0.72)
                .ignoresSafeArea()

            VStack(spacing: 24) {
                header
                proofPoints
                actions
            }
            .padding(24)
            .frame(maxWidth: 420)
            .background(
                RoundedRectangle(cornerRadius: 28)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 28)
                            .stroke(Color.white.opacity(0.14), lineWidth: 1)
                    )
            )
            .padding(20)
        }
        .accessibilityElement(children: .contain)
    }

    private var header: some View {
        VStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.purple, .pink],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 76, height: 76)

                Image(systemName: "sparkles")
                    .font(.system(.title)).fontWeight(.semibold)
                    .foregroundStyle(.white)
            }

            VStack(spacing: 8) {
                Text("ui.content.0".localized)
                    .font(.title2.bold())
                    .multilineTextAlignment(.center)

                Text("ui.content.1".localized)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)
                    .lineSpacing(3)
            }
        }
    }

    private var proofPoints: some View {
        VStack(spacing: 10) {
            FirstRunProofRow(
                icon: "lock.shield.fill",
                title: "Local-first by default",
                detail: "Your profile starts on this device."
            )

            FirstRunProofRow(
                icon: "circle.grid.cross.fill",
                title: "Chart and numerology together",
                detail: "A full natal map plus the number patterns shaping your life."
            )

            FirstRunProofRow(
                icon: "clock.badge.checkmark.fill",
                title: "Practical daily timing",
                detail: "Personal day, moon context, forecasts, and planning windows."
            )
        }
    }

    private var actions: some View {
        VStack(spacing: 12) {
            GradientButton("Create Profile", icon: "person.crop.circle.badge.plus") {
                onCreateProfile()
            }
            .accessibilityHint("Opens the birth details form")

            Button("ui.content.5".localized) {
                onExploreFirst()
            }
            .font(.subheadline.weight(.semibold))
            .foregroundStyle(Color.textSecondary)
            .frame(minHeight: 44)
            .accessibilityHint("Dismisses this prompt. You can create a profile later from Profile.")
        }
    }
}

private struct FirstRunProofRow: View {
    let icon: String
    let title: String
    let detail: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.headline)
                .foregroundStyle(.purple)
                .frame(width: 34, height: 34)
                .background(Circle().fill(Color.purple.opacity(0.18)))

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(Color.textPrimary)

                Text(detail)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.white.opacity(0.05))
        )
    }
}

private struct FirstRunProfileCompleteView: View {
    let profile: Profile
    let moonSign: String?
    let risingSign: String?
    let primaryRecommendation: TodayRecommendation
    let onPrimaryAction: () -> Void
    let onChart: () -> Void
    let onDismiss: () -> Void

    var body: some View {
        ZStack {
            Color.black.opacity(0.72)
                .ignoresSafeArea()

            VStack(spacing: 22) {
                header
                signalGrid
                actions
            }
            .padding(24)
            .frame(maxWidth: 430)
            .background(
                RoundedRectangle(cornerRadius: 24)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 24)
                            .stroke(Color.white.opacity(0.14), lineWidth: 1)
                    )
            )
            .padding(20)
        }
        .accessibilityElement(children: .contain)
    }

    private var header: some View {
        VStack(spacing: 10) {
            Image(systemName: "checkmark.seal.fill")
                .font(.system(.largeTitle)).fontWeight(.semibold)
                .foregroundStyle(.green)

            Text("ui.content.2".localized)
                .font(.title2.bold())
                .multilineTextAlignment(.center)

            Text("ui.content.3".localized)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
                .lineSpacing(3)
        }
    }

    private var signalGrid: some View {
        VStack(spacing: 10) {
            FirstRunSignalRow(
                icon: "sun.max.fill",
                title: "\(profile.sunSign) Sun",
                detail: "\(profile.element) element, \(profile.modality.lowercased()) mode"
            )

            FirstRunSignalRow(
                icon: "moon.stars.fill",
                title: moonSign.map { "\($0) Moon" } ?? "Moon Sign Syncing",
                detail: moonSign == nil ? "tern.content.0a".localized : "tern.content.0b".localized
            )

            FirstRunSignalRow(
                icon: "number.circle.fill",
                title: lifePathTitle,
                detail: lifePathDetail
            )

            FirstRunSignalRow(
                icon: "shield.lefthalf.filled",
                title: profile.dataQuality.label,
                detail: profile.dataQuality.description
            )
        }
    }

    private var actions: some View {
        VStack(spacing: 12) {
            GradientButton(primaryRecommendation.ctaTitle, icon: primaryRecommendation.icon) {
                onPrimaryAction()
            }

            Button {
                onChart()
            } label: {
                Label("ui.content.4".localized, systemImage: "chart.pie.fill")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(Color.white.opacity(0.08))
                    .foregroundStyle(Color.textPrimary)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            .buttonStyle(.plain)

            Button("action.continue".localized) {
                onDismiss()
            }
            .font(.subheadline.weight(.semibold))
            .foregroundStyle(Color.textSecondary)
            .frame(minHeight: 44)
        }
    }

    private var lifePathTitle: String {
        guard let number = profile.lifePathNumber() else { return "Life Path Syncing" }
        return "Life Path \(number)"
    }

    private var lifePathDetail: String {
        guard let number = profile.lifePathNumber() else {
            return "Your core numerology theme will appear after profile sync."
        }

        switch number {
        case 1: return "Initiation, independence, and fresh starts"
        case 2: return "Partnership, sensitivity, and careful timing"
        case 3: return "Expression, creativity, and social flow"
        case 4: return "Structure, discipline, and steady building"
        case 5: return "Change, movement, and adaptive choices"
        case 6: return "Care, responsibility, and relationship repair"
        case 7: return "Reflection, study, and inner truth"
        case 8: return "Power, resources, and long-range decisions"
        case 9: return "Completion, release, and wider perspective"
        case 11: return "Intuition, signal sensitivity, and inspiration"
        case 22: return "Large-scale building and practical vision"
        case 33: return "Service, teaching, and compassionate leadership"
        default: return "A core numerology theme for timing and reflection"
        }
    }
}

private struct FirstRunSignalRow: View {
    let icon: String
    let title: String
    let detail: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.headline)
                .foregroundStyle(.purple)
                .frame(width: 34, height: 34)
                .background(Circle().fill(Color.purple.opacity(0.18)))

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(Color.textPrimary)

                Text(detail)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.white.opacity(0.05))
        )
    }
}

#Preview {
    ContentView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
