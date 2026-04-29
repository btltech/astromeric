// MoonPhaseView.swift
// Moon phase display and lunar guidance

import SwiftUI

struct MoonPhaseView: View {
    @Environment(AppStore.self) private var store
    @State private var currentPhase: MoonPhase = .waxingCrescent
    @State private var illumination: Double = 0.35
    @State private var moonData: MoonData?
    @State private var ritual: MoonRitualDetail?
    @State private var isLoading = false
    @State private var error: String?
    
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 32) {
                    PremiumHeroCard(
                            eyebrow: "hero.moonPhase.eyebrow".localized,
                            title: "hero.moonPhase.title".localized,
                            bodyText: "hero.moonPhase.body".localized,
                            accent: [Color(hex: "111d35"), Color(hex: "4156b9"), Color(hex: "5a7fb3")],
                            chips: ["hero.moonPhase.chip.0".localized, "hero.moonPhase.chip.1".localized, "hero.moonPhase.chip.2".localized, "hero.moonPhase.chip.3".localized]
                        )

                    // Moon visual
                    moonVisual
                    
                    // Phase info
                    phaseInfo
                    
                    // Guidance
                    PremiumSectionHeader(
                title: "section.moonPhase.0.title".localized,
                subtitle: "section.moonPhase.0.subtitle".localized
            )

                    guidanceSection
                    
                    // Ritual section (if loaded from API)
                    if let ritual = ritual {
                        ritualSection(ritual)
                    }
                }
                .padding()
                .readableContainer()
            }
            
            if isLoading {
                LoadingOverlay()
            }
        }
        .navigationTitle("screen.moonPhase".localized)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await fetchMoonData()
        }
    }
    
    private func ritualSection(_ ritual: MoonRitualDetail) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("🕯️")
                        .font(.title2)
                    Text("ui.moonPhase.0".localized)
                        .font(.headline)
                    Spacer()
                }
                
                Text(ritual.theme)
                    .font(.subheadline.bold())
                
                Text(ritual.energy)
                    .font(.body)
                    .foregroundStyle(Color.textSecondary)
                
                if !ritual.activities.isEmpty {
                    Divider()
                    ForEach(Array(ritual.activities.enumerated()), id: \.offset) { index, step in
                        HStack(alignment: .top) {
                            Text("\(index + 1).")
                                .font(.caption.bold())
                                .foregroundStyle(.purple)
                            Text(step)
                                .font(.caption)
                        }
                    }
                }
                
                if let affirmation = ritual.affirmation {
                    Divider()
                    Text(affirmation)
                        .font(.caption.italic())
                        .foregroundStyle(Color.textSecondary)
                }
            }
        }
    }
    
    private var moonVisual: some View {
        ZStack {
            // Glow
            Circle()
                .fill(
                    RadialGradient(
                        colors: [.white.opacity(0.3), .clear],
                        center: .center,
                        startRadius: 60,
                        endRadius: 120
                    )
                )
                .frame(width: 240, height: 240)
            
            // Moon
            Circle()
                .fill(
                    LinearGradient(
                        colors: [Color.textMuted.opacity(0.3), Color.textMuted.opacity(0.1)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .frame(width: 150, height: 150)
                .overlay(
                    // Illuminated portion
                    Circle()
                        .fill(.white)
                        .frame(width: 150, height: 150)
                        .mask(
                            Rectangle()
                                .frame(width: 150 * illumination)
                                .offset(x: currentPhase.isWaxing ? -75 + (75 * illumination) : 75 - (75 * illumination))
                        )
                )
                .shadow(color: .white.opacity(0.3), radius: 20)
        }
    }
    
    private var phaseInfo: some View {
        VStack(spacing: 12) {
            Text(currentPhase.emoji)
                .font(.system(.largeTitle))
            
            Text(currentPhase.name)
                .font(.title2.bold())
            
            Text(String(format: "fmt.moonPhase.0".localized, "\(Int(illumination * 100))"))
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
        }
    }
    
    private var guidanceSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("ui.moonPhase.1".localized)
                .font(.headline)
            
            Text(currentPhase.guidance)
                .font(.body)
                .foregroundStyle(Color.textSecondary)
            
            Divider()
            
            HStack {
                VStack(alignment: .leading) {
                    Text("ui.moonPhase.2".localized)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                    Text(currentPhase.bestFor)
                        .font(.subheadline)
                }
                
                Spacer()
                
                VStack(alignment: .trailing) {
                    Text("ui.moonPhase.3".localized)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                    Text(currentPhase.avoid)
                        .font(.subheadline)
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }
    
    private func calculateMoonPhase() {
        // Simplified moon phase calculation (fallback)
        let date = Date()
        let calendar = Calendar.current
        let day = calendar.component(.day, from: date)
        
        // Approximate 29.5 day lunar cycle
        let cycleDay = day % 30
        
        switch cycleDay {
        case 0...3: currentPhase = .newMoon; illumination = 0.05
        case 4...7: currentPhase = .waxingCrescent; illumination = 0.25
        case 8...10: currentPhase = .firstQuarter; illumination = 0.5
        case 11...14: currentPhase = .waxingGibbous; illumination = 0.75
        case 15...17: currentPhase = .fullMoon; illumination = 1.0
        case 18...21: currentPhase = .waningGibbous; illumination = 0.75
        case 22...24: currentPhase = .lastQuarter; illumination = 0.5
        default: currentPhase = .waningCrescent; illumination = 0.25
        }
    }
    
    private func fetchMoonData() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            // Fetch current moon phase from API
            let moonResponse: V2ApiResponse<MoonData> = try await APIClient.shared.fetch(
                .currentMoon,
                cachePolicy: .cacheFirst
            )
            moonData = moonResponse.data
            
            // Update phase from API data
            if let phaseString = moonData?.phaseName,
               let phase = MoonPhase.from(apiString: phaseString) {
                currentPhase = phase
            }
            if let illum = moonData?.illumination {
                illumination = illum
            }
            
            // Fetch ritual suggestion
            let ritualResponse: V2ApiResponse<MoonRitualResponse> = try await APIClient.shared.fetch(
                .moonRitual(profile: store.activeProfile),
                cachePolicy: .cacheFirst
            )
            ritual = ritualResponse.data.ritual
            
            HapticManager.impact(.light)
        } catch {
            // Fall back to local calculation
            calculateMoonPhase()
            self.error = nil // Don't show error, fallback is fine
        }
    }
}

// MARK: - Moon Phase Enum

enum MoonPhase: String, CaseIterable {
    case newMoon, waxingCrescent, firstQuarter, waxingGibbous
    case fullMoon, waningGibbous, lastQuarter, waningCrescent
    
    var name: String {
        switch self {
        case .newMoon: return "New Moon"
        case .waxingCrescent: return "Waxing Crescent"
        case .firstQuarter: return "First Quarter"
        case .waxingGibbous: return "Waxing Gibbous"
        case .fullMoon: return "Full Moon"
        case .waningGibbous: return "Waning Gibbous"
        case .lastQuarter: return "Last Quarter"
        case .waningCrescent: return "Waning Crescent"
        }
    }
    
    static func from(apiString: String) -> MoonPhase? {
        let normalized = apiString.lowercased().replacingOccurrences(of: "_", with: " ").replacingOccurrences(of: "-", with: " ")
        switch normalized {
        case "new moon", "new": return .newMoon
        case "waxing crescent": return .waxingCrescent
        case "first quarter": return .firstQuarter
        case "waxing gibbous": return .waxingGibbous
        case "full moon", "full": return .fullMoon
        case "waning gibbous": return .waningGibbous
        case "last quarter", "third quarter": return .lastQuarter
        case "waning crescent": return .waningCrescent
        default: return nil
        }
    }
    
    var emoji: String {
        switch self {
        case .newMoon: return "🌑"
        case .waxingCrescent: return "🌒"
        case .firstQuarter: return "🌓"
        case .waxingGibbous: return "🌔"
        case .fullMoon: return "🌕"
        case .waningGibbous: return "🌖"
        case .lastQuarter: return "🌗"
        case .waningCrescent: return "🌘"
        }
    }
    
    var isWaxing: Bool {
        switch self {
        case .newMoon, .waxingCrescent, .firstQuarter, .waxingGibbous: return true
        default: return false
        }
    }
    
    var guidance: String {
        switch self {
        case .newMoon:
            return "A time for new beginnings and setting intentions. Plant seeds for what you want to manifest."
        case .waxingCrescent:
            return "Build momentum toward your goals. Take small, consistent actions."
        case .firstQuarter:
            return "Time to make decisions and take action. Push through challenges."
        case .waxingGibbous:
            return "Refine and adjust your approach. Pay attention to details."
        case .fullMoon:
            return "Peak energy time. Celebrate achievements and release what no longer serves you."
        case .waningGibbous:
            return "Share your wisdom with others. Practice gratitude."
        case .lastQuarter:
            return "Time for reflection and letting go. Clear out old energy."
        case .waningCrescent:
            return "Rest and recharge. Prepare for the new cycle ahead."
        }
    }
    
    var bestFor: String {
        switch self {
        case .newMoon: return "Planning"
        case .waxingCrescent: return "Starting"
        case .firstQuarter: return "Action"
        case .waxingGibbous: return "Refining"
        case .fullMoon: return "Manifesting"
        case .waningGibbous: return "Sharing"
        case .lastQuarter: return "Releasing"
        case .waningCrescent: return "Resting"
        }
    }
    
    var avoid: String {
        switch self {
        case .newMoon: return "Big launches"
        case .waxingCrescent: return "Overthinking"
        case .firstQuarter: return "Indecision"
        case .waxingGibbous: return "Rushing"
        case .fullMoon: return "New starts"
        case .waningGibbous: return "Holding on"
        case .lastQuarter: return "Clinging"
        case .waningCrescent: return "Overexertion"
        }
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        MoonPhaseView()
            .environment(AppStore.shared)
    }
    .preferredColorScheme(.dark)
}

// MARK: - API Response Models

struct MoonRitualResponse: Codable {
    let ritual: MoonRitualDetail
    let currentPhase: MoonPhaseSummary?
    let moonSign: String?
    let upcomingEvents: [MoonEvent]?
    
    enum CodingKeys: String, CodingKey {
        case ritual
        case currentPhase = "current_phase"
        case moonSign = "moon_sign"
        case upcomingEvents = "upcoming_events"
    }
}

struct MoonRitualDetail: Codable {
    let phase: String
    let moonSign: String
    let theme: String
    let energy: String
    let signFocus: String?
    let activities: [String]
    let avoid: String?
    let elementBoost: String?
    let bodyFocus: String?
    let crystals: [String]?
    let colors: [String]?
    let affirmation: String?
    let natalInsight: String?
    let numerologyInsight: String?
    
    enum CodingKeys: String, CodingKey {
        case phase
        case moonSign = "moon_sign"
        case theme
        case energy
        case signFocus = "sign_focus"
        case activities
        case avoid
        case elementBoost = "element_boost"
        case bodyFocus = "body_focus"
        case crystals
        case colors
        case affirmation
        case natalInsight = "natal_insight"
        case numerologyInsight = "numerology_insight"
    }
}

struct MoonPhaseSummary: Codable {
    let phaseName: String?
    let illumination: Double?
    let phaseEmoji: String?
    let daysUntilNext: Int?
    let nextPhase: String?
    
    enum CodingKeys: String, CodingKey {
        case phaseName = "phase_name"
        case illumination
        case phaseEmoji = "phase_emoji"
        case daysUntilNext = "days_until_next"
        case nextPhase = "next_phase"
    }
}

struct MoonEvent: Codable {
    let date: String
    let phase: String
    let type: String
    let description: String
}
