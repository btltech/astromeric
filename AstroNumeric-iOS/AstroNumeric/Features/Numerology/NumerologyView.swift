// NumerologyView.swift
// Main numerology screen

import SwiftUI

struct NumerologyView: View {
    @Environment(AppStore.self) private var store
    @State private var numerologyData: NumerologyData?
    @State private var isLoading = false
    @State private var error: String?
    @AppStorage("useChaldeanNumerology") private var useChaldean = false

    @State private var isExplaining = false
    @State private var explanationMarkdown: String?
    @State private var explanationSource: AIInsightSource = .fallback
    @State private var explanationGeneratedAt: Date = Date()
    @State private var showExplanation = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                Group {
                    if let profile = store.selectedProfile {
                        if let data = numerologyData {
                            ScrollView {
                                VStack(spacing: 20) {
                                    Button {
                                        Task { @MainActor in
                                            await explain(
                                                data,
                                                name: profile.displayName(
                                                    hideSensitive: store.hideSensitiveDetailsEnabled,
                                                    role: .share
                                                )
                                            )
                                        }
                                    } label: {
                                        HStack(spacing: 8) {
                                            if isExplaining {
                                                ProgressView()
                                                    .scaleEffect(0.8)
                                            } else {
                                                Image(systemName: "sparkles")
                                            }
                                            Text(isExplaining ? "tern.numerology.0a".localized : "tern.numerology.0b".localized)
                                                .font(.subheadline.weight(.medium))
                                        }
                                        .foregroundStyle(.purple)
                                        .padding(.horizontal, 16)
                                        .padding(.vertical, 10)
                                        .background(Color.purple.opacity(0.15))
                                        .clipShape(Capsule())
                                    }
                                    .disabled(isExplaining)

                                    // Chaldean / Pythagorean toggle
                                    NumerologySystemToggle(useChaldean: $useChaldean) {
                                        numerologyData = nil
                                        Task { await fetchNumerology(for: profile, useChaldean: useChaldean) }
                                    }

                                    if let synthesis = data.synthesis {
                                        synthesisSection(synthesis)
                                    }

                                    // Life Purpose (main feature)
                                    if let lifePath = data.lifePath, let purpose = lifePath.lifePurpose {
                                        lifePurposeSection(lifePath: lifePath, purpose: purpose)
                                    }
                                    
                                    // Core Numbers
                                    if let core = data.coreNumbers {
                                        coreNumbersSection(core)
                                    }
                                    
                                    // Cycles
                                    if let cycles = data.cycles {
                                        cyclesSection(cycles)
                                    }
                                    
                                    // Lucky Numbers
                                    if let lucky = data.luckyNumbers, !lucky.isEmpty {
                                        luckyNumbersSection(lucky)
                                    }
                                    
                                    // Auspicious Days
                                    if let days = data.auspiciousDays, !days.isEmpty {
                                        auspiciousDaysSection(days)
                                    }
                                    
                                    // Pinnacles
                                    if let pinnacles = data.pinnacles, !pinnacles.isEmpty {
                                        pinnaclesSection(pinnacles)
                                    }

                                    // Challenges
                                    if let challenges = data.challenges, !challenges.isEmpty {
                                        challengesSection(challenges)
                                    }
                                    
                                    // Karmic Debts (only shown when present)
                                    if let debts = data.karmicDebts, !debts.isEmpty {
                                        karmicDebtsSection(debts)
                                    }
                                }
                                .padding()
                                .readableContainer()
                            }
                            .refreshable {
                                await fetchNumerology(for: profile, useChaldean: useChaldean)
                            }
                        } else if isLoading {
                            VStack(spacing: 16) {
                                SkeletonCard()
                                SkeletonCard()
                            }
                            .padding()
                        } else if let error {
                            ErrorStateView(message: error) {
                                await fetchNumerology(for: profile, useChaldean: useChaldean)
                            }
                        } else {
                            // Initial state - show loading and fetch
                            VStack(spacing: 16) {
                                SkeletonCard()
                                SkeletonCard()
                            }
                            .padding()
                            .onAppear {
                                Task.detached { @MainActor in
                                    await fetchNumerology(for: profile, useChaldean: useChaldean)
                                }
                            }
                        }
                    } else {
                        noProfileView
                    }
                }
            }
            .navigationTitle("charts.numerology".localized)
        }
        .sheet(isPresented: $showExplanation) {
            if let markdown = explanationMarkdown {
                AIInsightsSheetView(
                    markdown: markdown,
                    source: explanationSource,
                    generatedAt: explanationGeneratedAt,
                        onRegenerate: {
                            if let data = numerologyData, let profile = store.selectedProfile {
                                Task {
                                    @MainActor in
                                    await explain(
                                        data,
                                        name: profile.displayName(
                                            hideSensitive: store.hideSensitiveDetailsEnabled,
                                            role: .share
                                        ),
                                        forceRefresh: true
                                    )
                                }
                            }
                        }
                    )
                }
            }
        }
    
    // MARK: - Sections
    
    private func lifePurposeSection(lifePath: LifePathData, purpose: String) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text(String(format: "fmt.numerology.2".localized, "\(lifePath.number)"))
                        .font(.title2.bold())
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.purple, .pink],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                    Spacer()
                }
                
                Text(purpose)
                    .font(.body)
                    .foregroundStyle(.primary)
                
                if let traits = lifePath.traits, !traits.isEmpty {
                    HStack {
                        ForEach(traits.prefix(4), id: \.self) { trait in
                            Text(trait)
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.purple.opacity(0.2))
                                .clipShape(Capsule())
                        }
                    }
                }
                
                if let meaning = lifePath.meaning, !meaning.isEmpty {
                    Text(meaning)
                        .font(.subheadline)
                        .foregroundStyle(Color.textSecondary)
                }
            }
        }
    }

    private func synthesisSection(_ synthesis: NumerologySynthesis) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 14) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("ui.numerology.0".localized)
                            .font(.system(.caption2, design: .monospaced))
                            .foregroundStyle(Color.textMuted)
                        Text("ui.numerology.1".localized)
                            .font(.title3.bold())
                    }
                    Spacer()
                    Image(systemName: "sparkles.rectangle.stack")
                        .foregroundStyle(.purple)
                }

                Text(synthesis.summary)
                    .font(.body)
                    .foregroundStyle(.primary)

                VStack(alignment: .leading, spacing: 8) {
                    Text("ui.numerology.2".localized)
                        .font(.subheadline.weight(.semibold))
                    Text(synthesis.currentFocus)
                        .font(.subheadline)
                        .foregroundStyle(Color.textSecondary)
                }

                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        ForEach(synthesis.dominantNumbers) { item in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.label)
                                    .font(.caption)
                                    .foregroundStyle(Color.textSecondary)
                                Text("\(item.number)")
                                    .font(.title3.bold())
                                    .foregroundStyle(.purple)
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 10)
                            .background(Color.purple.opacity(0.12))
                            .clipShape(RoundedRectangle(cornerRadius: 14))
                        }
                    }
                }

                if !synthesis.strengths.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("ui.numerology.3".localized)
                            .font(.subheadline.weight(.semibold))
                        ForEach(Array(synthesis.strengths.prefix(3).enumerated()), id: \.offset) { _, item in
                            Text("• \(item)")
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                }

                if let growthEdge = synthesis.growthEdges.first, !growthEdge.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("ui.numerology.4".localized)
                            .font(.subheadline.weight(.semibold))
                        Text(growthEdge)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text("ui.numerology.5".localized)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.purple)
                    Text(synthesis.affirmation)
                        .font(.footnote.italic())
                        .foregroundStyle(.purple)
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.purple.opacity(0.08))
                        .clipShape(RoundedRectangle(cornerRadius: 14))
                }
            }
        }
    }
    
    @State private var tappedNumerologyLuckyNumber: Int?
    
    private func luckyNumbersSection(_ numbers: [Int]) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("ui.numerology.6".localized)
                        .font(.headline)
                    Spacer()
                    Text("ui.numerology.7".localized)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }
                
                HStack(spacing: 12) {
                    ForEach(numbers, id: \.self) { num in
                        ZStack {
                            Circle()
                                .fill(tappedNumerologyLuckyNumber == num ? Color.green.opacity(0.4) : Color.green.opacity(0.2))
                                .frame(width: 44, height: 44)
                                .scaleEffect(tappedNumerologyLuckyNumber == num ? 1.1 : 1.0)
                                .animation(.spring(response: 0.3), value: tappedNumerologyLuckyNumber)
                            Text("\(num)")
                                .font(.title2.bold())
                                .foregroundStyle(.green)
                        }
                        .onTapGesture {
                            withAnimation(.spring(response: 0.3)) {
                                tappedNumerologyLuckyNumber = tappedNumerologyLuckyNumber == num ? nil : num
                            }
                            HapticManager.impact(.light)
                        }
                    }
                }
                
                if let tapped = tappedNumerologyLuckyNumber {
                    Text(luckyNumberMeaning(tapped))
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                        .transition(.opacity.combined(with: .move(edge: .top)))
                }
            }
        }
    }
    
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
    
    private func auspiciousDaysSection(_ days: [Int]) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Text("ui.numerology.8".localized)
                    .font(.headline)
                
                HStack(spacing: 8) {
                    ForEach(days, id: \.self) { day in
                        Text("\(day)")
                            .font(.subheadline.bold())
                            .foregroundStyle(.orange)
                            .frame(width: 36, height: 36)
                            .background(Color.orange.opacity(0.2))
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    }
                }
                
                Text("ui.numerology.9".localized)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
            }
        }
    }
    
    private func coreNumbersSection(_ core: CoreNumbers) -> some View {
        VStack(spacing: 16) {
            Text("ui.numerology.10".localized)
                .font(.headline)
            
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                if let lifePath = core.lifePath {
                    NumberCardView(title: "Life Path", number: lifePath.number, meaning: lifePath.meaning)
                }
                if let expression = core.expression {
                    NumberCardView(title: "Expression", number: expression.number, meaning: expression.meaning)
                }
                if let soulUrge = core.soulUrge {
                    NumberCardView(title: "Soul Urge", number: soulUrge.number, meaning: soulUrge.meaning)
                }
                if let personality = core.personality {
                    NumberCardView(title: "Personality", number: personality.number, meaning: personality.meaning)
                }
            }
        }
    }
    
    private func cyclesSection(_ cycles: NumerologyCycles) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Text("ui.numerology.11".localized)
                    .font(.headline)
                
                if let year = cycles.personalYear {
                    CycleRow(label: "Personal Year", number: year.number, meaning: year.meaning)
                }
                if let month = cycles.personalMonth {
                    CycleRow(label: "Personal Month", number: month.number, meaning: month.meaning)
                }
                if let day = cycles.personalDay {
                    CycleRow(label: "Personal Day", number: day.number, meaning: day.meaning)
                }
            }
        }
    }
    
    private func karmicDebtsSection(_ debts: [KarmicDebt]) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("ui.numerology.12".localized)
                        .font(.headline)
                    Spacer()
                    Text("\(debts.count)")
                        .font(.caption.bold())
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .background(Color.orange.opacity(0.2))
                        .foregroundStyle(.orange)
                        .clipShape(Capsule())
                }

                Text("ui.numerology.13".localized)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)

                ForEach(debts) { debt in
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(debt.label)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(.orange)
                            Spacer()
                            // Show which core numbers carry this debt
                            let sourceLabels = debt.sources.map { $0.replacingOccurrences(of: "_", with: " ").capitalized }
                            Text(sourceLabels.joined(separator: ", "))
                                .font(.caption2)
                                .foregroundStyle(Color.textSecondary)
                        }
                        Text(debt.theme)
                            .font(.caption.italic())
                            .foregroundStyle(Color.textSecondary)
                        Text(debt.description)
                            .font(.caption)
                            .foregroundStyle(Color.textPrimary)
                            .lineLimit(4)
                    }
                    if debt.id != debts.last?.id {
                        Divider()
                    }
                }
            }
        }
    }

    private func pinnaclesSection(_ pinnacles: [Pinnacle]) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Text("ui.numerology.14".localized)
                    .font(.headline)
                
                ForEach(pinnacles) { pinnacle in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(String(format: "fmt.numerology.1".localized, "\(pinnacle.number)"))
                                .font(.subheadline.weight(.medium))
                            if let ages = pinnacle.ages {
                                Text("(\(ages))")
                                    .font(.caption)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                        if let meaning = pinnacle.meaning {
                            Text(meaning)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    if pinnacle.number != pinnacles.last?.number {
                        Divider()
                    }
                }
            }
        }
    }

    private func challengesSection(_ challenges: [Challenge]) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Text("ui.numerology.15".localized)
                    .font(.headline)

                ForEach(challenges) { challenge in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(String(format: "fmt.numerology.0".localized, "\(challenge.number)"))
                                .font(.subheadline.weight(.medium))
                            if let ages = challenge.ages {
                                Text("(\(ages))")
                                    .font(.caption)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                        if let meaning = challenge.meaning {
                            Text(meaning)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    if challenge.number != challenges.last?.number {
                        Divider()
                    }
                }
            }
        }
    }
    
    private var noProfileView: some View {
        VStack(spacing: 20) {
            Text("🔢")
                .font(.system(.largeTitle))
            Text("ui.numerology.16".localized)
                .font(.title2.bold())
            Text("ui.numerology.17".localized)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
            GradientButton("Create Profile", icon: "plus") {
                NotificationCenter.default.post(
                    name: .navigateToTab,
                    object: nil,
                    userInfo: ["tab": 3]
                )
            }
            .frame(width: 200)
        }
        .padding()
    }
    
    // MARK: - Actions
    
    private func fetchNumerology(for profile: Profile, useChaldean: Bool = false) async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        let method = useChaldean ? "tern.numerology.1a".localized : "tern.numerology.1b".localized
        do {
            let response: V2ApiResponse<NumerologyData> = try await APIClient.shared.fetch(
                .numerologyProfile(profile: profile, method: method),
                cachePolicy: .networkFirst
            )
            numerologyData = response.data
        } catch {
            self.error = error.localizedDescription
        }
    }

    @MainActor
    private func explain(_ data: NumerologyData, name: String, forceRefresh: Bool = false) async {
        isExplaining = true
        defer { isExplaining = false }

        let core = data.coreNumbers
        let sections: [SectionSummary] = [
            core?.lifePath.map { SectionSummary(title: "Life Path \($0.number)", highlights: [$0.meaning ?? ""]) },
            core?.expression.map { SectionSummary(title: "Expression \($0.number)", highlights: [$0.meaning ?? ""]) },
            core?.soulUrge.map { SectionSummary(title: "Soul Urge \($0.number)", highlights: [$0.meaning ?? ""]) },
            core?.personality.map { SectionSummary(title: "Personality \($0.number)", highlights: [$0.meaning ?? ""]) },
        ].compactMap { $0 }

        let headline = AppStore.shared.hideSensitiveDetailsEnabled ? "Your Numerology" : "Numerology for \(name)"
        let request = AIExplainRequest(
            scope: "numerology",
            headline: headline,
            theme: nil,
            sections: sections,
            numerologySummary: data.synthesis?.summary,
            simpleLanguage: true
        )

        do {
            let response: V2ApiResponse<AIExplainResponse> = try await APIClient.shared.fetch(
                .aiExplain(reading: request),
                cachePolicy: forceRefresh ? .networkOnly : .cacheFirst
            )
            explanationMarkdown = response.data.summary
            explanationSource = AIInsightSource(provider: response.data.provider)
            explanationGeneratedAt = Date()
        } catch {
            var fallback = "## TL;DR\n\n"
            if let lp = core?.lifePath?.number {
                fallback += "Your **Life Path \(lp)** is the main theme. Use the other numbers as supporting traits.\n\n"
            } else {
                fallback += "Your numerology is built from your birth date and name. Life Path is the main theme; the others are supporting traits.\n\n"
            }
            fallback += "---\n\n## What to do with this\n\n"
            fallback += "- Pick **one strength** from your Life Path and practice it this week.\n"
            fallback += "- If two numbers feel true, treat one as your **goal** and the other as your **style**.\n"
            explanationMarkdown = fallback
            explanationSource = .fallback
            explanationGeneratedAt = Date()
        }

        showExplanation = true
    }
}

// MARK: - Number Card View

struct NumberCardView: View {
    let title: String
    let number: Int
    let meaning: String?
    
    @State private var showTooltip = false
    
    var body: some View {
        GlowCardView(glowColor: .purple, glowRadius: 15) {
            VStack(spacing: 8) {
                Text(title)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                
                Text("\(number)")
                    .font(.system(.largeTitle, design: .rounded)).fontWeight(.bold)
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.purple, .pink],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                
                if meaning != nil {
                    Button {
                        showTooltip = true
                    } label: {
                        Image(systemName: "info.circle")
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                }
            }
        }
        .sheet(isPresented: $showTooltip) {
            if let meaning {
                TooltipSheet(title: "\(title) Number \(number)", content: meaning)
            }
        }
    }
}

// MARK: - Cycle Row

struct CycleRow: View {
    let label: String
    let number: Int
    let meaning: String?
    
    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
            Spacer()
            Text("\(number)")
                .font(.title3.weight(.bold))
                .foregroundStyle(.purple)
        }
    }
}

// MARK: - Tooltip Sheet

struct TooltipSheet: View {
    @Environment(\.dismiss) private var dismiss
    let title: String
    let content: String
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text(content)
                        .font(.body)
                }
                .padding()
            }
            .navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                Button("action.done".localized) { dismiss() }
            }
        }
        .presentationDetents([.medium])
    }
}

// MARK: - Numerology System Toggle

struct NumerologySystemToggle: View {
    @Binding var useChaldean: Bool
    let onToggle: () -> Void
    @State private var showInfo = false

    var body: some View {
        VStack(spacing: 6) {
            HStack(spacing: 0) {
                // Pythagorean
                Button {
                    guard useChaldean else { return }
                    withAnimation(.spring(response: 0.3)) { useChaldean = false }
                    onToggle()
                } label: {
                    Text("ui.numerology.18".localized)
                        .font(.subheadline.weight(useChaldean ? .regular : .bold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(useChaldean ? Color.clear : Color.purple)
                        .foregroundStyle(useChaldean ? Color.textSecondary : .white)
                }
                .accessibilityLabel("Pythagorean numerology system")
                .accessibilityHint("Modern Western system using numbers 1 through 9")
                .accessibilityAddTraits(useChaldean ? [] : .isSelected)

                // Chaldean
                Button {
                    guard !useChaldean else { return }
                    withAnimation(.spring(response: 0.3)) { useChaldean = true }
                    onToggle()
                } label: {
                    HStack(spacing: 4) {
                        Text("ui.numerology.19".localized)
                        Text("✨")
                            .font(.caption)
                            .accessibilityHidden(true)
                    }
                    .font(.subheadline.weight(useChaldean ? .bold : .regular))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 8)
                    .background(useChaldean ? Color.purple : Color.clear)
                    .foregroundStyle(useChaldean ? .white : Color.textSecondary)
                }
                .accessibilityLabel("Chaldean numerology system")
                .accessibilityHint("Ancient Babylonian system using numbers 1 through 8")
                .accessibilityAddTraits(useChaldean ? .isSelected : [])
            }
            .clipShape(Capsule())
            .background(Capsule().fill(Color.surfaceElevated))

            // Info row
            Button {
                showInfo.toggle()
            } label: {
                Label(useChaldean ? "tern.numerology.2a".localized : "tern.numerology.2b".localized, systemImage: "info.circle")
                    .font(.caption)
                    .foregroundStyle(Color.textMuted)
            }
            .buttonStyle(.plain)
        }
        .sheet(isPresented: $showInfo) {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("ui.numerology.20".localized)
                        Text("ui.numerology.21".localized)
                        Text("ui.numerology.22".localized)
                    }
                    .padding()
                }
                .navigationTitle("screen.numerologySystems".localized)
                .toolbar { Button("action.done".localized) { showInfo = false } }
            }
            .presentationDetents([.medium])
        }
    }
}

// MARK: - Preview


#Preview {
    NumerologyView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
