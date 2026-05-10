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
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @Environment(\.horizontalSizeClass) private var hSizeClass
    @Environment(\.verticalSizeClass) private var vSizeClass
    @AppStorage("useChaldeanNumerology") private var useChaldeanNumerology = false
    @State private var vm = HomeVM()
    @State private var isMysticMode = true // Toggle state
    @State private var timeOffset: Double = 0 // Time scrubber state

    private var bento: AdaptiveBentoColumns {
        AdaptiveBentoColumns(
            hSize: hSizeClass,
            vSize: vSizeClass,
            isAccessibilityType: dynamicTypeSize.isAccessibilitySize
        )
    }

    private var columns: [GridItem] { bento.columns }
    private var gridColumnCount: Int { bento.columnCount }

    /// Compact landscape iPhone needs less vertical breathing room.
    private var verticalRhythm: CGFloat { vSizeClass == .compact ? 16 : 24 }
    private var topInset: CGFloat { vSizeClass == .compact ? 4 : 16 }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.appBackground.ignoresSafeArea()

                CosmicBackgroundView(element: nil)
                    .opacity(0.25)
                    .ignoresSafeArea()

                ScrollView {
                    VStack(alignment: .leading, spacing: Space.lg) {
                        // 1. Screen header — date + greeting
                        headerView

                        // 2. Today's primary insight — ONLY gradient card on the page
                        todayInsightCard

                        // 3. One recommended next action
                        recommendedActionCard

                        // 4. At-a-glance metrics row (personal day + moon)
                        metricsRow

                        // 5. Quick Tools horizontal scroll
                        quickToolsSection

                        // 6. Daily Reading detail (below fold)
                        if let reading = vm.dailyReading {
                            dailyReadingCard(reading)
                        }

                        // 7. Weekly Timing card
                        NavigationLink {
                            WeeklyVibeView(showShare: true)
                        } label: {
                            WeeklyVibeCard(showShare: false)
                        }
                        .buttonStyle(ScaleButtonStyle())

                        // 8. Habits widget
                        habitsWidget

                        // 9. Time Scrubber (power user feature)
                        timeScrubber
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
                .font(.system(.title, design: .serif).weight(.bold))
                .foregroundStyle(Color.textPrimary)
        }
    }

    private var todayInsightCard: some View {
        NavigationLink {
            ReadingView()
        } label: {
            PremiumHeroCard(
                eyebrow: getSunSignHeading(),
                title: heroHeadlineText,
                bodyText: heroSupportCopy,
                accent: .accentPrimary,
                chips: todayChips
            )
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityLabel("Today's insight")
        .accessibilityHint("Opens your full daily reading")
    }

    private var todayChips: [String] {
        var chips: [String] = []
        if vm.moonPhaseName != "Loading..." { chips.append(vm.moonPhaseName) }
        if let n = vm.personalDayNumber { chips.append("Day \(n)") }
        if let energy = vm.dailyReading?.overallEnergy { chips.append(energy) }
        return chips
    }

    private var recommendedActionCard: some View {
        NavigationLink {
            TimingAdvisorView()
        } label: {
            PremiumActionCard(
                title: "section.timingAdvisor.0.title".localized,
                subtitle: "section.timingAdvisor.0.subtitle".localized,
                icon: "clock.badge.checkmark.fill",
                label: "label.recommended".localized,
                accent: .cosmicPurple,
                emphasized: true
            )
        }
        .buttonStyle(ScaleButtonStyle())
    }

    private var metricsRow: some View {
        HStack(spacing: Space.sm) {
            numerologyMetricTile
            moonMetricTile
        }
    }

    private var numerologyMetricTile: some View {
        NavigationLink {
            NumerologyView()
        } label: {
            VStack(alignment: .leading, spacing: Space.sm) {
                Text("ui.home.2".localized)
                    .font(.system(.caption2, design: .monospaced))
                    .tracking(1.4)
                    .foregroundStyle(Color.textMuted)

                HStack(alignment: .firstTextBaseline, spacing: 4) {
                    if let n = vm.personalDayNumber {
                        Text(String(n))
                            .font(.system(.title, design: .serif).weight(.semibold))
                            .foregroundStyle(.white)
                    } else {
                        PremiumSkeleton(cornerRadius: 6, height: 36, width: 44)
                    }
                    Text("ui.home.3".localized)
                        .font(.system(.caption2, design: .monospaced))
                        .foregroundStyle(Color.textMuted)
                }

                Group {
                    if let desc = vm.personalDayDescription {
                        Text(desc)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                            .lineLimit(2)
                    } else {
                        PremiumSkeletonStack(lines: 2)
                    }
                }
            }
            .padding(Space.md)
            .frame(maxWidth: .infinity, minHeight: 130, alignment: .topLeading)
            .background(PremiumCardBackground(cornerRadius: Radius.md))
            .elevatedCardShadow()
        }
        .buttonStyle(ScaleButtonStyle())
    }

    private var moonMetricTile: some View {
        NavigationLink {
            MoonPhaseView()
        } label: {
            VStack(alignment: .leading, spacing: Space.sm) {
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
                    .lineLimit(3)
            }
            .padding(Space.md)
            .frame(maxWidth: .infinity, minHeight: 130, alignment: .topLeading)
            .background(
                PremiumCardBackground(
                    cornerRadius: Radius.md,
                    stroke: Color.cosmicPurple.opacity(0.20)
                )
            )
            .elevatedCardShadow()
        }
        .buttonStyle(ScaleButtonStyle())
    }

    private var quickToolsSection: some View {
        VStack(alignment: .leading, spacing: Space.sm) {
            Text("ui.home.8".localized)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(Color.textPrimary)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: Space.sm) {
                    QuickToolButton(title: "Tarot", icon: "suit.spade.fill", color: .cosmicPurple) {
                        TarotView()
                    }
                    QuickToolButton(title: "Oracle", icon: "questionmark.circle.fill", color: .cosmicBlue) {
                        OracleView()
                    }
                    QuickToolButton(title: "Affirmation", icon: "star.fill", color: .orange) {
                        AffirmationView()
                    }
                    QuickToolButton(title: "Moon", icon: "moon.fill", color: .indigo) {
                        MoonPhaseView()
                    }
                    QuickToolButton(title: "Timing", icon: "clock.fill", color: .green) {
                        TimingAdvisorView()
                    }
                }
            }
        }
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

    private var timeScrubber: some View {
        VStack(spacing: Space.sm) {
            HStack {
                Text("ui.home.5".localized)
                    .font(.system(.caption2, design: .monospaced))
                    .tracking(1.6)
                    .foregroundStyle(Color.textMuted)
                Spacer()
                NavigationLink {
                    ReadingView()
                } label: {
                    Image(systemName: "chevron.right")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color.textSecondary)
                }
            }
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
        .padding(Space.md)
        .background(PremiumCardBackground(cornerRadius: Radius.md))
        .elevatedCardShadow()
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

// MARK: - Quick Tool Button

struct QuickToolButton<Destination: View>: View {
    let title: String
    let icon: String
    let color: Color
    let destination: () -> Destination

    init(title: String, icon: String, color: Color, @ViewBuilder destination: @escaping () -> Destination) {
        self.title = title
        self.icon = icon
        self.color = color
        self.destination = destination
    }

    var body: some View {
        NavigationLink {
            destination()
        } label: {
            VStack(spacing: Space.xs) {
                Image(systemName: icon)
                    .font(.title3)
                    .foregroundStyle(color)
                    .frame(width: 44, height: 44)
                    .background(color.opacity(0.18))
                    .clipShape(RoundedRectangle(cornerRadius: Radius.sm))

                Text(title)
                    .font(.caption.weight(.medium))
                    .foregroundStyle(Color.textPrimary)
            }
            .padding(.vertical, Space.sm)
            .padding(.horizontal, 10)
            .background(Color.surfaceBase)
            .clipShape(RoundedRectangle(cornerRadius: Radius.legacy))
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityElement(children: .combine)
        .accessibilityLabel(title)
        .accessibilityHint("Opens \(title)")
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
