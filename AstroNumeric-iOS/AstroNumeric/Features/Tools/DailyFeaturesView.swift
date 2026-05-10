// DailyFeaturesView.swift
// All-in-one daily cosmic features: lucky numbers, colors, mood, affirmation

import SwiftUI
import UIKit

struct DailyFeaturesView: View {
    @Environment(AppStore.self) private var store
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @State private var dailyData: DailyFeaturesData?
    @State private var doDontData: DoDontData?
    @State private var briefData: MorningBriefData?
    @State private var isLoading = false
    @State private var error: String?
    @State private var showAllPowerHours = false
    @State private var tappedLuckyNumber: Int?
    @State private var copiedAffirmation = false

    private var metricsColumns: [GridItem] {
        if dynamicTypeSize.isAccessibilitySize { return [GridItem(.flexible())] }
        if horizontalSizeClass == .regular { return Array(repeating: GridItem(.flexible(), spacing: Space.xs), count: 4) }
        return Array(repeating: GridItem(.flexible(), spacing: Space.xs), count: 3)
    }

    private var hasLoadedContent: Bool {
        dailyData != nil || doDontData != nil || briefData != nil
    }
    
    var body: some View {
        ZStack {
            Color.appBackground.ignoresSafeArea()
            
            ScrollView {
                VStack(alignment: .leading, spacing: Space.md) {
                    if store.selectedProfile == nil {
                        noProfileCard
                    } else if !hasLoadedContent && isLoading {
                        VStack(spacing: Space.sm) {
                            SkeletonCard()
                            SkeletonCard()
                            SkeletonCard()
                        }
                    } else if !hasLoadedContent, let error {
                        ErrorStateView(message: error) {
                            await fetchDailyFeatures()
                        }
                    } else {
                        if let data = dailyData {
                            dailyFocusCard(data)
                        }

                        if let brief = briefData {
                            MorningBriefCard(data: brief)
                        }

                        if let doDont = doDontData {
                            DoDontCard(data: doDont)
                        } else if isLoading && briefData == nil {
                            SkeletonCard()
                        }

                        if let data = dailyData {
                            affirmationCard(data.affirmation)
                            luckyNumbersCard(data.luckyNumbers)
                            luckyColorCard(data.luckyColor ?? "Cosmic Violet")
                            powerHoursCard(data.powerHours)

                            if let dailyLuck = data.dailyLuck {
                                dailyLuckCard(dailyLuck)
                            } else {
                                emptyLuckCard
                            }
                        } else if isLoading {
                            VStack(spacing: Space.sm) {
                                SkeletonCard()
                                SkeletonCard()
                            }
                        }
                    }
                }
                .padding(.horizontal, Space.sm)
                .padding(.top, Space.sm)
                .padding(.bottom, Space.lg)
                .readableContainer()
            }
        }
        .accessibilityIdentifier("DailyGuideScreen")
        .navigationTitle("screen.dailyCosmic".localized)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await fetchAll()
        }
    }
    
    // MARK: - Cards

    private var noProfileCard: some View {
        PremiumActionCard(
            title: "ui.content.0".localized,
            subtitle: "ui.content.1".localized,
            icon: "person.crop.circle.badge.plus",
            label: "label.startHere".localized,
            accent: .accentPrimary,
            emphasized: true,
            showsChevron: false
        )
    }

    private func dailyFocusCard(_ data: DailyFeaturesData) -> some View {
        CardView(padding: Space.sm, cornerRadius: Radius.lg, materialOpacity: 0.06) {
            VStack(alignment: .leading, spacing: Space.sm) {
                HStack(alignment: .top) {
                    PremiumBadge(text: "label.recommended".localized)
                    Spacer()
                    Text(briefData?.greeting ?? "✨")
                        .font(.metadata.weight(.semibold))
                        .foregroundStyle(Color.textMuted)
                }

                VStack(alignment: .leading, spacing: Space.xs) {
                    Text("ui.home.1".localized)
                        .font(.sectionTitle)
                        .foregroundStyle(Color.textPrimary)

                    Text(data.advice)
                        .font(.bodyCopy)
                        .foregroundStyle(Color.textPrimary)

                    if let vibe = briefData?.vibe, !vibe.isEmpty {
                        Text(vibe)
                            .font(.bodyCopy)
                            .foregroundStyle(Color.textMuted)
                    }
                }

                LazyVGrid(columns: metricsColumns, spacing: Space.xs) {
                    DailyGuideMetricCard(title: "ui.dailyFeatures.8".localized, value: focusLuckValue)
                    DailyGuideMetricCard(title: "numerology.personalDay".localized, value: focusPersonalDayValue)
                    DailyGuideMetricCard(title: "screen.moonPhase".localized, value: focusMoonPhaseValue)
                }
            }
        }
    }

    private var emptyLuckCard: some View {
        CardView {
            HStack(spacing: 12) {
                Text("🍀")
                    .font(.title)
                VStack(alignment: .leading, spacing: 4) {
                    Text("ui.dailyFeatures.0".localized)
                        .font(.headline)
                    Text("ui.dailyFeatures.1".localized)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }
                Spacer()
            }
        }
    }
    
    private func affirmationCard(_ affirmation: String) -> some View {
        CardView {
            VStack(spacing: 12) {
                HStack {
                    Text("✨")
                        .font(.title)
                    Text("ui.dailyFeatures.2".localized)
                        .font(.headline)
                    Spacer()
                }

                Text(affirmation)
                    .font(.body)
                    .italic()
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.primary)

                HStack(spacing: 20) {
                    ShareLink(item: affirmation) {
                        Label("ui.dailyFeatures.9".localized, systemImage: "square.and.arrow.up")
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    .buttonStyle(ScaleButtonStyle())

                    Button {
                        UIPasteboard.general.string = affirmation
                        withAnimation(.spring(response: 0.3)) { copiedAffirmation = true }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                            withAnimation(.spring(response: 0.3)) { copiedAffirmation = false }
                        }
                    } label: {
                        Label(copiedAffirmation ? "tern.dailyFeatures.0a".localized : "tern.dailyFeatures.0b".localized, systemImage: copiedAffirmation ? "tern.dailyFeatures.1a".localized : "tern.dailyFeatures.1b".localized)
                            .font(.caption)
                            .foregroundStyle(copiedAffirmation ? .green : Color.textSecondary)
                    }
                    .buttonStyle(ScaleButtonStyle())
                }
            }
        }
    }
    
    private func luckyNumbersCard(_ numbers: [Int]) -> some View {
        CardView {
            VStack(spacing: 12) {
                HStack {
                    Text("🔢")
                        .font(.title)
                    VStack(alignment: .leading, spacing: 2) {
                        Text("ui.dailyFeatures.3".localized)
                            .font(.headline)
                        Text("ui.dailyFeatures.4".localized)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    Spacer()
                }

                HStack(spacing: 12) {
                    ForEach(numbers, id: \.self) { number in
                        let isTapped = tappedLuckyNumber == number
                        ZStack {
                            Circle()
                                .fill(isTapped ? .purple.opacity(0.6) : .purple.opacity(0.3))
                                .frame(width: 50, height: 50)
                            Text("\(number)")
                                .font(.title2.bold())
                                .foregroundStyle(.purple)
                        }
                        .scaleEffect(isTapped ? 1.1 : 1.0)
                        .onTapGesture {
                            withAnimation(.spring(response: 0.3)) {
                                tappedLuckyNumber = (tappedLuckyNumber == number) ? nil : number
                            }
                        }
                    }
                }

                if let tapped = tappedLuckyNumber, numbers.contains(tapped) {
                    Text(luckyNumberMeaning(tapped))
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                        .multilineTextAlignment(.center)
                        .transition(.opacity.combined(with: .move(edge: .top)))
                }
            }
        }
    }
    
    private func luckyColorCard(_ color: String) -> some View {
        CardView {
            HStack(spacing: 16) {
                Text("🎨")
                    .font(.title)

                VStack(alignment: .leading, spacing: 4) {
                    Text("ui.dailyFeatures.5".localized)
                        .font(.headline)
                    Text(color)
                        .font(.title3.bold())
                        .foregroundStyle(colorFromName(color))
                    Text(colorUsageHint(color))
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }

                Spacer()

                Circle()
                    .fill(colorFromName(color))
                    .frame(width: 40, height: 40)
            }
        }
    }
    
    private func powerHoursCard(_ hours: [String]) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("⏰")
                        .font(.title)
                    Text("ui.dailyFeatures.6".localized)
                        .font(.headline)
                    Spacer()
                }

                if hours.isEmpty {
                    Text("ui.dailyFeatures.7".localized)
                        .font(.subheadline)
                        .foregroundStyle(Color.textSecondary)
                } else {
                    let displayed = showAllPowerHours ? hours : Array(hours.prefix(3))
                    FlowLayout(spacing: 8) {
                        ForEach(displayed, id: \.self) { hour in
                            Text(hour)
                                .font(.caption.bold())
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(.purple.opacity(0.25))
                                .foregroundStyle(.purple)
                                .clipShape(Capsule())
                        }
                    }

                    if hours.count > 3 {
                        Button {
                            withAnimation(.spring(response: 0.3)) {
                                showAllPowerHours.toggle()
                            }
                        } label: {
                            Text(showAllPowerHours ? "Show less" : "See all \(hours.count - 3) more")
                                .font(.caption)
                                .foregroundStyle(.purple)
                        }
                        .buttonStyle(ScaleButtonStyle())
                    }
                }
            }
        }
    }
    
    private func dailyLuckCard(_ luck: Double) -> some View {
        let pct = DailyFeaturePresentation.normalizedLuckPercentage(luck)
        let fraction = pct / 100.0
        return CardView {
            HStack(spacing: 12) {
                Text("🍀")
                    .font(.title)

                VStack(alignment: .leading, spacing: 4) {
                    Text("ui.dailyFeatures.8".localized)
                        .font(.headline)
                    Text("\(Int(pct))%")
                        .font(.title2.bold())
                        .foregroundStyle(pct > 70 ? .green : pct > 40 ? .orange : .red)
                }

                Spacer()

                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Capsule()
                            .fill(Color.borderSubtle)
                            .frame(height: 8)
                        Capsule()
                            .fill(pct > 70 ? Color.green : pct > 40 ? Color.orange : Color.red)
                            .frame(width: geo.size.width * fraction, height: 8)
                    }
                }
                .frame(width: 80, height: 8)
            }
        }
    }

    private var focusLuckValue: String {
        guard let dailyLuck = dailyData?.dailyLuck else { return "--" }
        return "\(Int(DailyFeaturePresentation.normalizedLuckPercentage(dailyLuck)))%"
    }

    private var focusPersonalDayValue: String {
        if let personalDay = briefData?.personalDay ?? doDontData?.personalDay {
            return String(personalDay)
        }
        return "--"
    }

    private var focusMoonPhaseValue: String {
        let phase = briefData?.moonPhase ?? doDontData?.moonPhase
        guard let phase, !phase.isEmpty else { return "--" }
        return phase
    }
    
    // MARK: - Helpers

    private func luckyNumberMeaning(_ n: Int) -> String {
        let meanings: [Int: String] = [
            1: "Leadership & new beginnings", 2: "Balance & partnership",
            3: "Creativity & expression", 4: "Stability & foundation",
            5: "Freedom & change", 6: "Harmony & nurturing",
            7: "Wisdom & inner knowing", 8: "Abundance & power",
            9: "Completion & compassion"
        ]
        let reduced = n > 9 ? (n % 9 == 0 ? 9 : n % 9) : n
        return meanings[reduced] ?? "Universal energy"
    }

    private func colorUsageHint(_ color: String) -> String {
        DailyFeaturePresentation.usageHint(for: color)
    }

    private func colorFromName(_ name: String) -> Color {
        switch name.lowercased() {
        case "red": return .red
        case "blue": return .blue
        case "green": return .green
        case "yellow": return .yellow
        case "orange": return .orange
        case "purple": return .purple
        case "pink": return .pink
        case "gold": return .yellow
        case "silver": return Color.textMuted
        case "white": return .white
        case "black": return .black
        case "indigo": return .indigo
        case "teal": return .teal
        default: return .purple
        }
    }
    
    // MARK: - Actions

    private func toPayload(_ p: Profile) -> ProfilePayload {
        p.privacySafePayload(hideSensitive: store.hideSensitiveDetailsEnabled)
    }

    private func fetchAll() async {
        async let features: () = fetchDailyFeatures()
        async let doDont: () = fetchDoDont()
        async let brief: () = fetchBrief()
        _ = await (features, doDont, brief)
    }

    private func fetchDoDont() async {
        guard let p = store.activeProfile else { return }
        let profile = toPayload(p)
        do {
            let response: V2ApiResponse<DoDontData> = try await APIClient.shared.fetch(
                .dailyDoDont(profile: profile),
                cachePolicy: .networkFirst
            )
            await MainActor.run { doDontData = response.data }
        } catch {
            // Silent fail — card just won't appear
        }
    }

    private func fetchBrief() async {
        guard let p = store.activeProfile else { return }
        do {
            let brief = try await WidgetDataProvider.shared.refreshMorningBrief(profile: p, force: true)
            await MainActor.run { briefData = brief }
        } catch {
            // Silent fail
        }
    }

    private func fetchDailyFeatures() async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        do {
            guard let profile = store.activeProfile else {
                error = "Please create a profile first"
                return
            }
            
            let response: V2ApiResponse<DailyFeaturesData> = try await APIClient.shared.fetch(
                .dailyFeatures(profile: profile),
                cachePolicy: .networkFirst
            )
            dailyData = response.data
            HapticManager.impact(.light)
        } catch {
            self.error = error.localizedDescription
            HapticManager.notification(.error)
        }
    }
}

// MARK: - Data Model

struct DailyGuideMetricCard: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.metadata.weight(.semibold))
                .foregroundStyle(Color.textMuted)
                .lineLimit(1)

            Text(value)
                .font(.cardTitle)
                .foregroundStyle(Color.textPrimary)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: Radius.sm)
                .fill(Color.surfaceBase)
                .overlay(
                    RoundedRectangle(cornerRadius: Radius.sm)
                        .stroke(Color.borderSubtle, lineWidth: Stroke.hairline)
                )
        )
    }
}

struct DailyFeaturesData: Codable {
    let date: Date
    let affirmation: String
    let luckyNumbers: [Int]
    let luckyColor: String?
    let powerHours: [String]
    let dailyLuck: Double?
    let advice: String
    let generatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case date, affirmation, advice
        case luckyNumbers = "lucky_numbers"
        case luckyColor = "lucky_color"
        case powerHours = "power_hours"
        case dailyLuck = "daily_luck"
        case generatedAt = "generated_at"
    }
}

#Preview {
    DailyFeaturesView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
