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
                // 1. The "Void" Background
                Color.appBackground.ignoresSafeArea()
                
                // Dynamic Star Field that reacts to Time Scrubber
                // We'll pass the timeOffset to control speed/direction eventually
                CosmicBackgroundView(element: nil)
                    .opacity(0.3)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(alignment: .leading, spacing: verticalRhythm) {
                        headerView
                        modeToggle

                        todayAtAGlanceCard
                        
                        // Main Bento Grid
                        LazyVGrid(columns: columns, spacing: 16) {
                            
                            // 1. Hero Block (Spans 2 columns)
                            NavigationLink {
                                ReadingView()
                            } label: {
                                dailyHeroBlock
                            }
                            .buttonStyle(.plain)
                            .gridCellColumns(gridColumnCount)
                            
                            // 2. Numerology Block
                            NavigationLink {
                                NumerologyView()
                            } label: {
                                numerologyBlock
                            }
                            .buttonStyle(.plain)
                            
                            // 3. Transit Block
                            NavigationLink {
                                DailyFeaturesView()
                            } label: {
                                transitAlertBlock
                            }
                            .buttonStyle(.plain)
                            
                            // 4. Action Block (Study/Chat) (Spans 2 columns)
                            NavigationLink {
                                TimingAdvisorView()
                            } label: {
                                actionBlock
                            }
                            .buttonStyle(.plain)
                            .gridCellColumns(gridColumnCount)
                        }
                        .symbolRenderingMode(.hierarchical)

                        // Daily Reading card
                        if let reading = vm.dailyReading {
                            dailyReadingCard(reading)
                        }

                        // Weekly Vibe timeline
                        NavigationLink {
                            WeeklyVibeView(showShare: true)
                        } label: {
                            WeeklyVibeCard(showShare: false)
                        }
                        .buttonStyle(ScaleButtonStyle())

                        // Moon phase snapshot
                        moonPhaseBlock

                        // Quick Tools
                        quickToolsSection

                        // Habits widget
                        habitsWidget
                        
                        // Time Scrubber
                        timeScrubber
                            .padding(.top, vSizeClass == .compact ? 12 : 20)
                    }
                    .padding(.horizontal, hSizeClass == .regular ? 28 : 20)
                    .padding(.bottom, 24)
                    .readableContainer()
                }
                .refreshable {
                    guard let profile = store.activeProfile else { return }
                    vm.invalidateWeekCache()
                    await vm.loadDashboard(for: profile, date: vm.selectedDate, forceRefresh: true)
                    await vm.preloadWeek(for: profile)
                }
            }
            // Custom Toolbar
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        shareCosmicID()
                    }) {
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
                // Pre-fetch week for instant Time Travel
                Task { await vm.preloadWeek(for: profile) }
            }
        }
    }
    
    // MARK: - Subviews
    
    private var headerView: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(vm.selectedDate.formatted(.dateTime.weekday(.wide).month().day()))
                .font(.system(.subheadline, design: .monospaced))
                .textCase(.uppercase)
                .tracking(2.5)
                .foregroundStyle(Color.textMuted)

            Text("ui.home.0".localized)
                .font(.system(.largeTitle, design: .serif).weight(.bold))
                .minimumScaleFactor(0.8)
                .foregroundStyle(
                    LinearGradient(
                        colors: [.white, Color.white.opacity(0.78)],
                        startPoint: .top, endPoint: .bottom
                    )
                )

            Text(homePromiseCopy)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .lineSpacing(3)
        }
        .padding(.top, topInset)
    }

    private var todayAtAGlanceCard: some View {
        CardView {
            VStack(alignment: .leading, spacing: 14) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("ui.home.1".localized)
                            .font(.system(.caption2, design: .monospaced))
                            .foregroundStyle(Color.textMuted)
                        Text(todayLead)
                            .font(.system(.title3, design: .serif).weight(.bold))
                    }
                    Spacer()
                    Text(vm.sunSignEmoji)
                        .font(.title)
                }

                Text(todaySupportCopy)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)

                HStack(spacing: 12) {
                    premiumMetricChip(title: "Energy", value: vm.dailyReading?.overallEnergy ?? "Syncing")
                    premiumMetricChip(title: "Day", value: vm.personalDayNumber.map(String.init) ?? "-")
                    premiumMetricChip(title: "Color", value: vm.luckyColor ?? "Loading")
                }
            }
        }
    }
    
    private var modeToggle: some View {
        MysticModeToggle(isMystic: $isMysticMode)
            .frame(maxWidth: 320)
    }
    
    private var dailyHeroBlock: some View {
        PremiumHeroBlock(
            eyebrow: getSunSignHeading(),
            headline: heroHeadlineText,
            support: heroSupportCopy,
            isMystic: isMysticMode
        )
    }

    private var heroHeadlineText: String {
        if isMysticMode { return mysticHeroHeadline }
        if let h = vm.dailyReading?.headline { return h }
        return "Tuning into today’s sky"
    }
    
    private var numerologyBlock: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("ui.home.2".localized)
                .font(.system(.caption2, design: .monospaced))
                .tracking(1.5)
                .foregroundStyle(Color.textMuted)

            HStack(alignment: .firstTextBaseline, spacing: 6) {
                if let n = vm.personalDayNumber {
                    Text(String(n))
                        .font(.system(.largeTitle, design: .serif).weight(.semibold))
                        .lineLimit(1)
                        .minimumScaleFactor(0.6)
                        .foregroundStyle(
                            LinearGradient(colors: [.white, Color.textMuted], startPoint: .top, endPoint: .bottom)
                        )
                } else {
                    PremiumSkeleton(cornerRadius: 8, height: 44, width: 56)
                }
                Text("ui.home.3".localized)
                    .font(.system(.caption, design: .monospaced))
                    .foregroundColor(.white.opacity(0.7))
            }

            Group {
                if let desc = vm.personalDayDescription {
                    Text(desc)
                        .font(.caption)
                        .foregroundStyle(Color.textMuted)
                        .lineLimit(2)
                } else {
                    PremiumSkeletonStack(lines: 2)
                }
            }

            Spacer(minLength: 0)
        }
        .padding(18)
        .frame(minHeight: 180, maxHeight: .infinity, alignment: .topLeading)
        .background(PremiumCardBackground(cornerRadius: Radius.md))
        .elevatedCardShadow()
    }
    
    private var transitAlertBlock: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 6) {
                Circle().fill(Color.cosmicPurple).frame(width: 8, height: 8)
                    .flickerEffect()
                Text("ui.home.4".localized)
                    .font(.system(.caption2, design: .monospaced))
                    .tracking(1.5)
                    .foregroundStyle(Color.cosmicPurple)
            }

            if vm.moonPhaseName == "Loading..." {
                PremiumSkeleton(height: 18, width: 160)
                PremiumSkeletonStack(lines: 2)
            } else {
                Text(moonPhaseHeadline)
                    .font(.system(.headline, design: .serif))
                    .foregroundColor(.white)

                Text(moonPhaseSupportCopy)
                    .font(.caption)
                    .foregroundStyle(Color.textMuted)
                    .lineLimit(3)
            }

            Spacer(minLength: 0)
        }
        .padding(18)
        .frame(minHeight: 180, maxHeight: .infinity, alignment: .topLeading)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            PremiumCardBackground(
                cornerRadius: Radius.md,
                stroke: Color.cosmicPurple.opacity(0.25)
            )
        )
        .elevatedCardShadow()
    }

    private func premiumMetricChip(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title.uppercased())
                .font(.system(.caption2, design: .monospaced))
                .foregroundStyle(Color.textMuted)
            Text(value)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.white)
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color.white.opacity(0.04))
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
    
    private var timeScrubber: some View {
        VStack(spacing: 14) {
            HStack {
                Text("ui.home.5".localized)
                    .font(.system(.caption, design: .monospaced))
                    .tracking(2)
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
        .padding(18)
        .background(PremiumCardBackground(cornerRadius: Radius.md))
        .elevatedCardShadow()
    }

    private func dailyReadingCard(_ reading: DailyReadingSummary) -> some View {
        NavigationLink {
            ReadingView()
        } label: {
            CardView {
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("ui.home.6".localized)
                            .font(.headline)
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    
                    Text(reading.headline)
                        .font(.subheadline)
                        .lineLimit(2)

                    Text(readingSignalSummary)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                        .lineLimit(2)
                    
                    if let tldr = reading.tldr {
                        Text(tldr)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                            .lineLimit(3)
                    }
                }
            }
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityLabel("Daily reading")
        .accessibilityHint("Double tap to view your full daily reading")
    }

    private var moonPhaseBlock: some View {
        NavigationLink {
            MoonPhaseView()
        } label: {
            CardView {
                HStack(spacing: 16) {
                    Text(vm.moonPhaseEmoji)
                        .font(.system(.largeTitle))
                    VStack(alignment: .leading, spacing: 4) {
                        Text("ui.home.7".localized)
                            .font(.headline)
                        Text(vm.moonPhaseName)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    Spacer()
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }
            }
        }
        .buttonStyle(ScaleButtonStyle())
    }

    private var quickToolsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("ui.home.8".localized)
                .font(.headline)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    QuickToolButton(title: "Tarot", icon: "suit.spade.fill", color: .purple) {
                        TarotView()
                    }
                    
                    QuickToolButton(title: "Oracle", icon: "questionmark.circle.fill", color: .blue) {
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
                HStack(spacing: 16) {
                    ZStack {
                        Circle()
                            .fill(Color.green.opacity(0.2))
                            .frame(width: 50, height: 50)
                        
                        Image(systemName: "checkmark.circle.fill")
                            .font(.title2)
                            .foregroundStyle(.green)
                    }
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("ui.home.9".localized)
                            .font(.headline)
                        Text(String(format: "fmt.home.0".localized, "\(vm.habitsCompletedToday)", "\(vm.totalHabits)"))
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    
                    Spacer()
                    
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }
            }
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityLabel("Today's habits, \(vm.habitsCompletedToday) of \(vm.totalHabits) completed")
        .accessibilityHint("Double tap to view your habits")
    }
    
    // MARK: - Helpers
    
    private func getSunSignHeading() -> String {
        let sign = store.activeProfile?.sunSign ?? "Aquarius"
        return "SUN IN \(sign.uppercased())"
    }

    private var mysticHeroHeadline: String {
        if let personalDayNumber = vm.personalDayNumber {
            return "\(vm.sunSignEmoji) \(activeSunSign) Sun / Personal Day \(personalDayNumber)"
        }

        return "\(vm.sunSignEmoji) \(activeSunSign) Sun in focus"
    }

    private var heroSupportCopy: String {
        let readingLead = vm.dailyReading?.headline ?? "Your forecast is syncing."
        return "\(readingLead) Built from your birth chart, numerology timing, and today's strongest scored themes."
    }

    private var homePromiseCopy: String {
        "A daily command center for your chart, numbers, and live timing so you know what matters before the day pulls you in five directions."
    }

    private var todayLead: String {
        if let advice = vm.dailyAdvice, !advice.isEmpty {
            return advice
        }

        return vm.dailyReading?.headline ?? "Your day is syncing"
    }

    private var todaySupportCopy: String {
        if let affirmation = vm.dailyAffirmation, !affirmation.isEmpty {
            return affirmation
        }

        return "Pulling together your forecast tone, personal day, and live lunar context."
    }

    private var moonPhaseHeadline: String {
        guard vm.moonPhaseName != "Loading..." else { return "Moon phase loading" }
        return isMysticMode ? "\(vm.moonPhaseName) window" : "Moon phase: \(vm.moonPhaseName)"
    }

    private var moonPhaseSupportCopy: String {
        if !vm.moonGuidance.isEmpty {
            return vm.moonGuidance
        }

        if let dailyAffirmation = vm.dailyAffirmation, !dailyAffirmation.isEmpty {
            return dailyAffirmation
        }

        return "Live lunar timing is still loading."
    }

    private var readingSignalSummary: String {
        var parts: [String] = [activeSunSign]

        if let personalDayNumber = vm.personalDayNumber {
            parts.append("Personal Day \(personalDayNumber)")
        }

        if vm.moonPhaseName != "Loading..." {
            parts.append(vm.moonPhaseName)
        }

        return parts.joined(separator: " / ")
    }

    private var activeSunSign: String {
        store.activeProfile?.sunSign ?? "Aquarius"
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
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundStyle(.white)
                    .frame(width: 44, height: 44)
                    .background(color.opacity(0.25))
                    .clipShape(Circle())
                
                Text(title)
                    .font(.caption)
                    .foregroundStyle(.white)
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
            .background(Color.black.opacity(0.2))
            .cornerRadius(16)
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityElement(children: .combine)
        .accessibilityLabel(title)
        .accessibilityHint("Opens \(title)")
    }
}
    private var actionBlock: some View {
        HStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 6) {
                Text("ui.home.10".localized)
                    .font(.system(.caption, design: .monospaced))
                    .tracking(2)
                    .foregroundStyle(Color.cosmicPurple)
                Text("ui.home.11".localized)
                    .font(.system(.headline, design: .serif))
                    .foregroundColor(.white)
                Text("ui.home.12".localized)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .lineLimit(2)
            }
            Spacer()
            Image(systemName: "arrow.right")
                .font(.title3.weight(.semibold))
                .symbolRenderingMode(.hierarchical)
                .foregroundStyle(.white)
                .frame(width: 44, height: 44)
                .background(
                    Circle()
                        .fill(Color.white.opacity(0.08))
                        .overlay(Circle().stroke(.white.opacity(0.2), lineWidth: Stroke.hairline))
                )
        }
        .padding(22)
        .background(PremiumCardBackground(cornerRadius: Radius.md))
        .elevatedCardShadow()
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
