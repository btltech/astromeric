//
//  BentoDashboardView.swift
//  AstroNumeric
//
//  Created by GitHub Copilot on 2026-01-27.
//  Concept: Celestial Brutalism / Bento Grid Layout
//

import SwiftUI

struct HomeView: View {
    @Environment(AppStore.self) private var store
    @Environment(\.horizontalSizeClass) private var hSizeClass
    @Environment(\.verticalSizeClass) private var vSizeClass
    @AppStorage("useChaldeanNumerology") private var useChaldeanNumerology = false
    @State private var vm = HomeVM()
    @State private var timeOffset: Double = 0 // Time scrubber state
    @State private var showAdvancedTiming = false
    @State private var showCreateProfileSheet = false
    @State private var editingProfileFromHome: Profile?
    @State private var navigationTarget: TodayDestination?
    private var topInset: CGFloat { vSizeClass == .compact ? 4 : 16 }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.appBackground.ignoresSafeArea()

                CosmicBackgroundView(element: nil)
                    .opacity(0.25)
                    .ignoresSafeArea()

                ScrollView {
                    VStack(alignment: .leading, spacing: Space.md) {
                        // 1. Screen header — date + greeting
                        headerView

                        // 2. Unified Today snapshot: insight, next move, and key signals
                        todaySnapshotCard

                        // 3. Immediate actions without burying the daily flow
                        todayQuickActions

                        // 4. Weekly Timing card
                        NavigationLink {
                            WeeklyVibeView(showShare: true)
                        } label: {
                            WeeklyVibeCard(showShare: false)
                        }
                        .buttonStyle(ScaleButtonStyle())

                        // 6. Habits widget
                        habitsWidget

                        // 7. Advanced timing controls
                        advancedTimingSection
                    }
                    .padding(.horizontal, hSizeClass == .regular ? 28 : Space.md)
                    .padding(.bottom, Space.xl)
                    .readableContainer()
                }
                .refreshable {
                    guard let profile = store.activeProfile else { return }
                    vm.invalidateWeekCache()
                    await vm.loadDashboard(for: profile, date: vm.selectedDate, forceRefresh: true)
                    await vm.preloadWeek(for: profile)
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: shareCosmicID) {
                        Image(systemName: "square.and.arrow.up")
                            .foregroundColor(.white)
                    }
                    .buttonStyle(AccessibleButtonStyle())
                    .accessibilityLabel("Share dashboard")
                    .accessibilityHint("Shares your cosmic dashboard as an image")
                }
            }
            .task(id: store.activeProfile?.id) {
                guard let profile = store.activeProfile else { return }
                await vm.loadDashboard(for: profile)
                Task { await vm.preloadWeek(for: profile) }
            }
            .navigationDestination(item: $navigationTarget) { destination in
                todayDestinationView(for: destination)
            }
            .sheet(isPresented: $showCreateProfileSheet) {
                EditProfileView()
            }
            .sheet(item: $editingProfileFromHome) { profile in
                EditProfileView(profile: profile)
            }
            .onReceive(NotificationCenter.default.publisher(for: .openTodayDestination)) { notification in
                guard let destination = TodayDestination.from(userInfo: notification.userInfo) else { return }
                openTodayDestination(destination)
            }
        }
    }

    // MARK: - Subviews

    private var headerView: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(vm.selectedDate.formatted(.dateTime.weekday(.wide).month().day()))
                .font(.system(.caption2, design: .monospaced))
                .textCase(.uppercase)
                .tracking(2.0)
                .foregroundStyle(Color.textMuted)
                .padding(.top, topInset)

            Text("ui.home.0".localized)
                .font(.system(.title2, design: .serif).weight(.bold))
                .foregroundStyle(Color.textPrimary)
                .lineLimit(2)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private var todayChips: [String] {
        var chips: [String] = []
        if vm.moonPhaseName != "Loading..." { chips.append(vm.moonPhaseName) }
        if let n = vm.personalDayNumber { chips.append("Day \(n)") }
        if let energy = vm.dailyReading?.overallEnergy { chips.append(energy) }
        return chips
    }

    private var todaySnapshotCard: some View {
        let recommendation = todayRecommendation

        return VStack(alignment: .leading, spacing: Space.md) {
            Button {
                openTodayDestination(.reading)
            } label: {
                VStack(alignment: .leading, spacing: Space.sm) {
                    HStack(alignment: .top) {
                        VStack(alignment: .leading, spacing: 6) {
                            Text(getSunSignHeading())
                                .font(.system(.caption2, design: .monospaced).weight(.bold))
                                .tracking(1.6)
                                .foregroundStyle(Color.textMuted)

                            Text(heroHeadlineText)
                                .font(.system(.title3, design: .serif).weight(.bold))
                                .foregroundStyle(.white)
                                .lineLimit(3)
                                .multilineTextAlignment(.leading)

                            Text(heroSupportCopy)
                                .font(.subheadline)
                                .foregroundStyle(Color.textSecondary)
                                .lineLimit(3)
                                .multilineTextAlignment(.leading)
                        }

                        Spacer(minLength: Space.md)

                        Image(systemName: "sparkles.rectangle.stack.fill")
                            .font(.title2.weight(.semibold))
                            .foregroundStyle(Color.accentPrimary)
                            .padding(12)
                            .background(Color.white.opacity(0.08), in: RoundedRectangle(cornerRadius: Radius.sm))
                    }

                    if !todayChips.isEmpty {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: Space.xs) {
                                ForEach(todayChips, id: \.self) { chip in
                                    PremiumBadge(text: chip, tint: .accentPrimary)
                                }
                            }
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Today's snapshot")
            .accessibilityHint("Opens your full daily reading")

            Divider()
                .overlay(Color.white.opacity(0.08))

            Button {
                openTodayDestination(recommendation.destination)
            } label: {
                HStack(spacing: Space.md) {
                    Image(systemName: recommendation.icon)
                        .font(.system(.title3, weight: .semibold))
                        .foregroundStyle(recommendation.accent)
                        .frame(width: 42, height: 42)
                        .background(
                            RoundedRectangle(cornerRadius: Radius.sm)
                                .fill(recommendation.accent.opacity(0.16))
                        )

                    VStack(alignment: .leading, spacing: 4) {
                        HStack(spacing: 6) {
                            Text(recommendation.title)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(Color.textPrimary)
                            PremiumBadge(text: recommendation.label, tint: recommendation.accent)
                        }

                        Text(recommendation.subtitle)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                            .multilineTextAlignment(.leading)
                    }

                    Spacer(minLength: Space.md)

                    Image(systemName: "arrow.right")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color.textSecondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .buttonStyle(.plain)

            HStack(spacing: Space.sm) {
                Button {
                    openTodayDestination(.numerology)
                } label: {
                    VStack(alignment: .leading, spacing: Space.xs) {
                        Text("ui.home.2".localized)
                            .font(.system(.caption2, design: .monospaced))
                            .tracking(1.4)
                            .foregroundStyle(Color.textMuted)

                        HStack(alignment: .firstTextBaseline, spacing: 4) {
                            if let n = vm.personalDayNumber {
                                Text(String(n))
                                    .font(.system(.title3, design: .serif).weight(.semibold))
                                    .foregroundStyle(.white)
                            } else {
                                PremiumSkeleton(cornerRadius: 6, height: 28, width: 34)
                            }
                            Text("ui.home.3".localized)
                                .font(.system(.caption2, design: .monospaced))
                                .foregroundStyle(Color.textMuted)
                        }

                        if let desc = vm.personalDayDescription {
                            Text(desc)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                                .lineLimit(2)
                        } else {
                            PremiumSkeletonStack(lines: 2)
                        }
                    }
                    .frame(maxWidth: .infinity, minHeight: 112, alignment: .topLeading)
                    .padding(Space.md)
                    .background(Color.white.opacity(0.04), in: RoundedRectangle(cornerRadius: Radius.md))
                }
                .buttonStyle(.plain)

                Button {
                    openTodayDestination(.moonPhase)
                } label: {
                    VStack(alignment: .leading, spacing: Space.xs) {
                        HStack(spacing: Space.xs) {
                            Circle()
                                .fill(Color.cosmicPurple)
                                .frame(width: 7, height: 7)
                            Text("ui.home.4".localized)
                                .font(.system(.caption2, design: .monospaced))
                                .tracking(1.4)
                                .foregroundStyle(Color.cosmicPurple)
                        }

                        Text(vm.moonPhaseEmoji + " " + (vm.moonPhaseName == "Loading..." ? "—" : vm.moonPhaseName))
                            .font(.system(.subheadline, design: .serif).weight(.semibold))
                            .foregroundStyle(.white)
                            .lineLimit(2)

                        Text(moonPhaseSupportCopy)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                            .lineLimit(2)
                    }
                    .frame(maxWidth: .infinity, minHeight: 112, alignment: .topLeading)
                    .padding(Space.md)
                    .background(Color.white.opacity(0.04), in: RoundedRectangle(cornerRadius: Radius.md))
                }
                .buttonStyle(.plain)
            }
        }
        .padding(Space.md)
        .background(
            RoundedRectangle(cornerRadius: Radius.lg)
                .fill(
                    LinearGradient(
                        colors: [
                            Color.accentPrimary.opacity(0.18),
                            Color.cardBackground.opacity(0.96),
                            Color.cosmicPurple.opacity(0.12)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: Radius.lg)
                        .stroke(Color.white.opacity(0.08), lineWidth: 1)
                )
        )
        .elevatedCardShadow()
    }

    private var todayRecommendationContext: TodayRecommendationContext {
        TodayRecommendationContext(
            hasReading: vm.dailyReading != nil,
            habitsCompletedToday: vm.habitsCompletedToday,
            totalHabits: vm.totalHabits,
            dailyAdvice: vm.dailyAdvice
        )
    }

    private var todayRecommendation: TodayRecommendation {
        TodayRecommendation.make(profile: store.activeProfile, context: todayRecommendationContext)
    }

    @ViewBuilder
    private func todayDestinationView(for destination: TodayDestination) -> some View {
        switch destination {
        case .reading:
            ReadingView()
        case .timing:
            TimingAdvisorView()
        case .journal:
            JournalView()
        case .numerology:
            NumerologyView()
        case .moonPhase:
            MoonPhaseView()
        case .createProfile, .editProfile:
            VStack(alignment: .leading, spacing: Space.sm) {
                Text("Complete your profile from Home")
                    .font(.headline)
                Text("Home opens profile completion as a sheet for this route.")
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
            }
            .padding(Space.md)
            .readableContainer()
        }
    }

    private var exploreHubCard: some View {
        Button {
            NotificationCenter.default.post(name: .navigateToTab, object: nil, userInfo: ["tab": 1])
        } label: {
            PremiumActionCard(
                title: "hero.explore.title".localized,
                subtitle: "hero.explore.body".localized,
                icon: "safari.fill",
                label: "nav.explore".localized,
                accent: .accentPrimary,
                emphasized: true
            )
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityHint("Switches to Explore for tools, habits, relationships, and settings")
    }

    private var todayQuickActions: some View {
        LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: Space.sm), count: 3), spacing: Space.sm) {
            HomeQuickActionButton(
                title: "nav.explore".localized,
                icon: "safari.fill",
                accent: .accentPrimary
            ) {
                NotificationCenter.default.post(name: .navigateToTab, object: nil, userInfo: ["tab": 1])
            }

            HomeQuickActionButton(
                title: "screen.timingAdvisor".localized,
                icon: "clock.badge.checkmark.fill",
                accent: .positiveGreen
            ) {
                openTodayDestination(.timing)
            }

            HomeQuickActionButton(
                title: "screen.journal".localized,
                icon: "book.closed.fill",
                accent: .accentSecondary
            ) {
                openTodayDestination(.journal)
            }
        }
        .accessibilityElement(children: .contain)
    }

    private var habitsWidget: some View {
        NavigationLink {
            HabitsView()
        } label: {
            CardView {
                HStack(spacing: Space.md) {
                    ZStack {
                        Circle()
                            .fill(Color.green.opacity(0.18))
                            .frame(width: 46, height: 46)
                        Image(systemName: "checkmark.circle.fill")
                            .font(.title2)
                            .foregroundStyle(.green)
                    }
                    VStack(alignment: .leading, spacing: 4) {
                        Text("ui.home.9".localized)
                            .font(.subheadline.weight(.semibold))
                        Text(String(format: "fmt.home.0".localized, "\(vm.habitsCompletedToday)", "\(vm.totalHabits)"))
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    Spacer()
                    Image(systemName: "chevron.right")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color.textSecondary)
                }
            }
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityLabel("Today's habits, \(vm.habitsCompletedToday) of \(vm.totalHabits) completed")
        .accessibilityHint("Double tap to view your habits")
    }

    private var advancedTimingSection: some View {
        CardView {
            DisclosureGroup(isExpanded: $showAdvancedTiming) {
                VStack(alignment: .leading, spacing: Space.sm) {
                    Text("Compare nearby days without crowding the main dashboard.")
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)

                    TimeScrubber(offset: $timeOffset) { newValue in
                        let targetDate = Date().addingTimeInterval(newValue * 86400)
                        if let cachedData = vm.getFromCache(for: targetDate) {
                            vm.applyCachedData(cachedData)
                        } else {
                            Task {
                                try? await Task.sleep(nanoseconds: 300_000_000)
                                if self.timeOffset == newValue {
                                    if let profile = store.activeProfile {
                                        await vm.loadDashboard(for: profile, date: targetDate)
                                    }
                                }
                            }
                        }
                    }
                }
                .padding(.top, Space.sm)
            } label: {
                HStack(spacing: Space.md) {
                    Image(systemName: "clock.arrow.trianglehead.counterclockwise.rotate.90")
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(Color.cosmicPurple)
                        .frame(width: 42, height: 42)
                        .background(
                            RoundedRectangle(cornerRadius: Radius.sm)
                                .fill(Color.cosmicPurple.opacity(0.15))
                        )

                    VStack(alignment: .leading, spacing: 4) {
                        Text("Advanced timing")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(Color.textPrimary)

                        Text("Inspect how the next week shifts before you act.")
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                }
            }
            .tint(Color.textPrimary)
        }
    }

    private func dailyReadingCard(_ reading: DailyReadingSummary) -> some View {
        NavigationLink {
            ReadingView()
        } label: {
            CardView {
                VStack(alignment: .leading, spacing: Space.sm) {
                    HStack {
                        Text("ui.home.6".localized)
                            .font(.subheadline.weight(.semibold))
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(Color.textSecondary)
                    }
                    Text(reading.headline)
                        .font(.subheadline)
                        .foregroundStyle(Color.textSecondary)
                        .lineLimit(3)
                    if let tldr = reading.tldr {
                        Text(tldr)
                            .font(.caption)
                            .foregroundStyle(Color.textMuted)
                            .lineLimit(2)
                    }
                }
            }
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityLabel("Daily reading")
        .accessibilityHint("Double tap to view your full daily reading")
    }

    // MARK: - Helpers

    private func getSunSignHeading() -> String {
        let sign = store.activeProfile?.sunSign ?? "Aquarius"
        return "SUN IN \(sign.uppercased())"
    }

    private var heroHeadlineText: String {
        if let h = vm.dailyReading?.headline { return h }
        return "\(vm.sunSignEmoji) \(activeSunSign) Sun in focus"
    }

    private var heroSupportCopy: String {
        // Cycle-aware guidance is the most relevant copy for the hero card
        if let guidance = vm.cycleGuidance, !guidance.isEmpty { return guidance }
        if let affirmation = vm.dailyAffirmation, !affirmation.isEmpty { return affirmation }
        return vm.dailyReading?.tldr ?? "Built from your birth chart, numerology, and today's live sky."
    }

    private var moonPhaseSupportCopy: String {
        if !vm.moonGuidance.isEmpty { return vm.moonGuidance }
        return "Live lunar timing."
    }

    private var activeSunSign: String {
        store.activeProfile?.sunSign ?? "Aquarius"
    }

    private func openTodayDestination(_ destination: TodayDestination) {
        switch destination {
        case .createProfile:
            showCreateProfileSheet = true
        case .editProfile:
            if let profile = store.activeProfile {
                editingProfileFromHome = profile
            } else {
                showCreateProfileSheet = true
            }
        case .reading, .timing, .journal, .numerology, .moonPhase:
            navigationTarget = destination
        }
    }

    // MARK: - Share Logic
    
    @MainActor
    private func shareCosmicID() {
        let renderer = ImageRenderer(content: CosmicIDCard(
            name: store.hideSensitiveDetailsEnabled
                ? PrivacyRedaction.privateProfile
                : (store.activeProfile?.name ?? "Cosmic Traveler"),
            sunSign: store.activeProfile?.sunSign ?? "Aquarius",
            lifePath: Self.cosmicIDLifePathText(
                profile: store.activeProfile,
                useChaldean: useChaldeanNumerology
            )
        ))
        
        renderer.scale = 3.0 // High resolution
        
        if let image = renderer.uiImage {
            let activityVC = UIActivityViewController(activityItems: [image], applicationActivities: nil)
            // Get the current window scene to present
            if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
               let rootVC = windowScene.windows.first?.rootViewController {
                rootVC.present(activityVC, animated: true)
            }
        }
    }

    static func cosmicIDLifePathText(profile: Profile?, useChaldean: Bool) -> String {
        guard let lifePath = profile?.lifePathNumber(useChaldean: useChaldean) else {
            return "?"
        }
        return String(lifePath)
    }
}

// MARK: - Cosmic ID Card View (For Sharing)
struct CosmicIDCard: View {
    let name: String
    let sunSign: String
    let lifePath: String
    
    var body: some View {
        ZStack {
            Color.black
            
            VStack(spacing: 20) {
                Text("ui.home.13".localized)
                    .font(.system(.caption, design: .monospaced)).fontWeight(.bold)
                    .tracking(4)
                    .foregroundStyle(Color.textMuted)
                
                Spacer()
                
                Text(name.uppercased())
                    .font(.system(.title, design: .serif)).fontWeight(.bold)
                    .foregroundColor(.white)
                
                Divider().background(.white)
                
                HStack(spacing: 40) {
                    VStack {
                        Text("ui.home.14".localized)
                            .font(.system(.caption2, design: .monospaced))
                            .foregroundStyle(Color.textMuted)
                        Text(sunSign.uppercased())
                            .font(.system(.body)).fontWeight(.bold)
                            .foregroundColor(.white)
                    }
                    
                    VStack {
                        Text("ui.home.15".localized)
                            .font(.system(.caption2, design: .monospaced))
                            .foregroundStyle(Color.textMuted)
                        Text(lifePath)
                            .font(.system(.body)).fontWeight(.bold)
                            .foregroundColor(.white)
                    }
                }
                
                Spacer()
                
                Text("ui.home.16".localized)
                    .font(.system(.caption2, design: .monospaced))
                    .foregroundColor(.white.opacity(0.5))
            }
            .padding(40)
        }
        .frame(width: 375, height: 600)
    }
}

struct HomeQuickActionButton: View {
    let title: String
    let icon: String
    let accent: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: Space.xs) {
                Image(systemName: icon)
                    .font(.system(.title3, weight: .semibold))
                    .foregroundStyle(accent)
                    .frame(width: 38, height: 38)
                    .background(Circle().fill(accent.opacity(0.14)))

                Text(title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color.textPrimary)
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                    .minimumScaleFactor(0.75)
            }
            .frame(maxWidth: .infinity, minHeight: 90)
            .padding(Space.sm)
            .background(
                RoundedRectangle(cornerRadius: Radius.md)
                    .fill(Color.cardBackground.opacity(0.88))
                    .overlay(
                        RoundedRectangle(cornerRadius: Radius.md)
                            .stroke(Color.borderSubtle, lineWidth: Stroke.hairline)
                    )
            )
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityLabel(title)
    }
}

// MARK: - Helper Extensions

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// Flashing animation modifier
struct FlickerRequest: ViewModifier {
    @State private var opacity: Double = 1.0
    func body(content: Content) -> some View {
        content
            .opacity(opacity)
            .onAppear {
                withAnimation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true)) {
                    opacity = 0.4
                }
            }
    }
}

extension View {
    func flickerEffect() -> some View {
        modifier(FlickerRequest())
    }
}

#Preview {
    HomeView()
        .preferredColorScheme(.dark)
        .environment(AppStore.shared)
}
