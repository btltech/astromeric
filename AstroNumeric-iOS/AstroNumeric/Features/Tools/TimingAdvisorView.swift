// TimingAdvisorView.swift
// Activity-based timing advisor - best times for different activities

import SwiftUI

struct TimingAdvisorView: View {
    @Environment(AppStore.self) private var store
    @State private var selectedActivity: TimingActivity?
    @State private var timingResult: TimingResult?
    @State private var cachedResult: TimingResult?
    @State private var isLoading = false
    @State private var error: String?
    @State private var resultsRevealing = true
    
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 20) {
                    PremiumHeroCard(
                            eyebrow: "hero.timingAdvisor.eyebrow".localized,
                            title: "hero.timingAdvisor.title".localized,
                            bodyText: "hero.timingAdvisor.body".localized,
                            accent: [Color(hex: "15263a"), Color(hex: "1e8b7a"), Color(hex: "6bb45d")],
                            chips: ["hero.timingAdvisor.chip.0".localized, "hero.timingAdvisor.chip.1".localized, "hero.timingAdvisor.chip.2".localized]
                        )

                    CardView {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("ui.timingAdvisor.0".localized)
                                .font(.headline)
                            Text("ui.timingAdvisor.1".localized)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }

                    PremiumSectionHeader(
                title: "section.timingAdvisor.0.title".localized,
                subtitle: "section.timingAdvisor.0.subtitle".localized
            )

                    // Activity picker
                    activityPicker
                    
                    // Fetch button with helper text
                    VStack(spacing: 8) {
                        GradientButton("Get Timing Advice", icon: "clock.badge.checkmark", isLoading: isLoading) {
                            Task { await fetchTiming() }
                        }
                        .disabled(selectedActivity == nil || isLoading)
                        .opacity(selectedActivity == nil ? 0.6 : 1.0)
                        
                        if selectedActivity == nil {
                            Text("ui.timingAdvisor.2".localized)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    
                    if let result = timingResult {
                        PremiumSectionHeader(
                title: "section.timingAdvisor.1.title".localized,
                subtitle: "section.timingAdvisor.1.subtitle".localized
            )

                        // Results with staggered reveal
                        timingResultCard(result)
                            .slideUpReveal(isRevealing: resultsRevealing, offset: 30, delay: 0.0)
                        
                        // Best Times
                        bestTimesCard(result.bestTimes)
                            .slideUpReveal(isRevealing: resultsRevealing, offset: 30, delay: 0.1)
                        
                        // Avoid Times
                        avoidTimesCard(result.avoidTimes)
                            .slideUpReveal(isRevealing: resultsRevealing, offset: 30, delay: 0.2)
                        
                        // Tips
                        tipsCard(result.tips)
                            .slideUpReveal(isRevealing: resultsRevealing, offset: 30, delay: 0.3)
                        
                    } else if isLoading {
                        // Loading skeleton with animated message
                        loadingStateView
                        
                    } else if let error {
                        ErrorStateView(message: error) {
                            await fetchTiming()
                        }
                    } else {
                        // Preview card - what you'll get
                        whatYoullGetCard
                        
                        // Show cached result if available
                        if let cached = cachedResult {
                            cachedResultCard(cached)
                        }
                    }
                }
                .padding()
                .padding(.bottom, 80) // Extra padding to avoid FAB overlap
                .readableContainer()
            }
        }
        .navigationTitle("screen.timingAdvisor".localized)
        .navigationBarTitleDisplayMode(.inline)
        .onChange(of: timingResult) { oldValue, newValue in
            // Trigger reveal when new results arrive
            if newValue != nil && oldValue == nil {
                resultsRevealing = true
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
                    resultsRevealing = false
                }
            }
        }
    }
    
    // MARK: - Loading State
    
    private var loadingStateView: some View {
        VStack(spacing: 20) {
            CardView {
                VStack(spacing: 16) {
                    HStack(spacing: 12) {
                        ProgressView()
                            .scaleEffect(1.2)
                        
                        Text("ui.timingAdvisor.3".localized)
                            .font(.subheadline.weight(.medium))
                            .foregroundStyle(Color.textSecondary)
                    }
                    
                    // Skeleton rows
                    VStack(spacing: 12) {
                        ForEach(0..<3) { _ in
                            TimingSkeletonRow()
                        }
                    }
                }
            }
            
            SkeletonCard()
        }
    }
    
    // MARK: - What You'll Get Card
    
    private var whatYoullGetCard: some View {
        CardView {
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Text("⏰")
                        .font(.title)
                    Text("ui.timingAdvisor.4".localized)
                        .font(.headline)
                    Spacer()
                }
                
                VStack(alignment: .leading, spacing: 12) {
                    TimingBenefitRow(icon: "clock.badge.checkmark", color: .green, text: "Best times for your activity")
                    TimingBenefitRow(icon: "exclamationmark.triangle", color: .orange, text: "Times to avoid")
                    TimingBenefitRow(icon: "chart.line.uptrend.xyaxis", color: .purple, text: "Cosmic score percentage")
                    TimingBenefitRow(icon: "lightbulb", color: .yellow, text: "Personalized tips")
                }
                
                Text("ui.timingAdvisor.5".localized)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
            }
        }
    }
    
    // MARK: - Cached Result Card
    
    private func cachedResultCard(_ result: TimingResult) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("📋")
                        .font(.title2)
                    Text("ui.timingAdvisor.6".localized)
                        .font(.headline)
                    Spacer()
                    
                    Text("ui.timingAdvisor.7".localized)
                        .font(.caption2)
                        .foregroundStyle(Color.textSecondary)
                }
                
                Divider()
                
                HStack {
                    Text(TimingActivity(rawValue: result.activity)?.emoji ?? "⏰")
                        .font(.title2)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(TimingActivity(rawValue: result.activity)?.displayName ?? result.activity)
                            .font(.subheadline.weight(.medium))
                        Text(String(format: "fmt.timingAdvisor.1".localized, "\(Int(result.score * 100))"))
                            .font(.caption)
                            .foregroundStyle(result.score > 0.7 ? .green : result.score > 0.4 ? .orange : .red)
                    }
                    Spacer()
                }
            }
        }
        .opacity(0.8)
    }
    
    // MARK: - Activity Picker
    
    private var activityPicker: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Text("ui.timingAdvisor.8".localized)
                    .font(.headline)
                
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                    ForEach(TimingActivity.allCases, id: \.self) { activity in
                        Button {
                            // Allow deselect by tapping same activity
                            if selectedActivity == activity {
                                selectedActivity = nil
                                HapticManager.impact(.light)
                            } else {
                                selectedActivity = activity
                                HapticManager.impact(.medium)
                            }
                        } label: {
                            HStack(spacing: 8) {
                                Text(activity.emoji)
                                    .font(.title3)
                                Text(activity.displayName)
                                    .font(.subheadline.weight(.medium))
                                
                                if selectedActivity == activity {
                                    Image(systemName: "checkmark.circle.fill")
                                        .font(.caption)
                                        .foregroundStyle(.purple)
                                }
                            }
                            .padding(.horizontal, 14)
                            .padding(.vertical, 14)
                            .frame(maxWidth: .infinity, minHeight: 44)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(selectedActivity == activity ? .purple.opacity(0.25) : Color.borderSubtle)
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .strokeBorder(
                                        selectedActivity == activity ? Color.purple : Color.clear,
                                        lineWidth: 2
                                    )
                            )
                            .foregroundStyle(selectedActivity == activity ? .purple : .primary)
                            .shadow(color: selectedActivity == activity ? .purple.opacity(0.3) : .clear, radius: 8)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
    }
    
    // MARK: - Result Cards
    
    private func timingResultCard(_ result: TimingResult) -> some View {
        CardView {
            VStack(spacing: 12) {
                HStack {
                    Text(TimingActivity(rawValue: result.activity)?.emoji ?? selectedActivity?.emoji ?? "⏰")
                        .font(.title)
                    Text(String(format: "fmt.timingAdvisor.0".localized, "\(TimingActivity(rawValue: result.activity)?.displayName ?? selectedActivity?.displayName ?? "Activity")"))
                        .font(.headline)
                    Spacer()
                }
                
                // Score
                HStack {
                    Text("ui.timingAdvisor.9".localized)
                        .font(.subheadline)
                        .foregroundStyle(Color.textSecondary)
                    Spacer()
                    Text("\(Int(result.score * 100))%")
                        .font(.title2.bold())
                        .foregroundStyle(result.score > 0.7 ? .green : result.score > 0.4 ? .orange : .red)
                }
                
                // Rating
                Text(result.rating)
                    .font(.body)
                    .foregroundStyle(Color.textSecondary)
            }
        }
    }
    
    private func bestTimesCard(_ times: [String]) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("✅")
                        .font(.title2)
                    Text("ui.timingAdvisor.10".localized)
                        .font(.headline)
                        .foregroundStyle(.green)
                    Spacer()
                }
                
                if times.isEmpty {
                    Text("ui.timingAdvisor.11".localized)
                        .font(.subheadline)
                        .foregroundStyle(Color.textSecondary)
                } else {
                    ForEach(times, id: \.self) { time in
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundStyle(.green)
                            Text(time)
                                .font(.subheadline)
                        }
                    }
                }
            }
        }
    }
    
    private func avoidTimesCard(_ times: [String]) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("⚠️")
                        .font(.title2)
                    Text("ui.timingAdvisor.12".localized)
                        .font(.headline)
                        .foregroundStyle(.orange)
                    Spacer()
                }
                
                if times.isEmpty {
                    Text("ui.timingAdvisor.13".localized)
                        .font(.subheadline)
                        .foregroundStyle(Color.textSecondary)
                } else {
                    ForEach(times, id: \.self) { time in
                        HStack {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundStyle(.orange)
                            Text(time)
                                .font(.subheadline)
                        }
                    }
                }
            }
        }
    }
    
    private func tipsCard(_ tips: [String]) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("💡")
                        .font(.title2)
                    Text("ui.timingAdvisor.14".localized)
                        .font(.headline)
                    Spacer()
                }
                
                ForEach(tips, id: \.self) { tip in
                    HStack(alignment: .top) {
                        Text("•")
                            .foregroundStyle(.blue)
                        Text(tip)
                            .font(.subheadline)
                    }
                }
            }
        }
    }
    
    // MARK: - Actions

    private func formatHourWindow(_ hour: TimingHourPayload) -> String {
        let start = formatISOTime(hour.start)
        let end = formatISOTime(hour.end)
        return "\(start)–\(end) • \(hour.planet)"
    }

    private func formatISOTime(_ value: String) -> String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .none
        dateFormatter.timeStyle = .short

        if let date = parseISODate(value) {
            return dateFormatter.string(from: date)
        }

        // Fallback: show something readable even if parsing fails.
        if let tIndex = value.firstIndex(of: "T") {
            let afterT = value[value.index(after: tIndex)...]
            let trimmed = afterT.split(separator: "+", maxSplits: 1, omittingEmptySubsequences: true).first
                ?? afterT.split(separator: "Z", maxSplits: 1, omittingEmptySubsequences: true).first
                ?? Substring(afterT)
            return String(trimmed)
        }
        return value
    }

    private func parseISODate(_ value: String) -> Date? {
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = iso.date(from: value) {
            return date
        }
        iso.formatOptions = [.withInternetDateTime]
        return iso.date(from: value)
    }
    
    private func fetchTiming() async {
        guard let activity = selectedActivity else { return }
        
        isLoading = true
        error = nil
        HapticManager.impact(.light) // Light haptic on start
        defer { isLoading = false }
        
        do {
            guard let profile = store.selectedProfile else {
                error = "Please create a profile first"
                return
            }
            
            // LOCAL-FIRST: Use on-device Swiss Ephemeris engine
            // Only requires a profile with birth date + location
            if profile.latitude != nil && profile.longitude != nil {
                let localResult = await TimingEngine.shared.calculateTiming(
                    activity: activity.rawValue,
                    profile: profile
                )
                timingResult = localResult
                cachedResult = localResult
                HapticManager.notification(.success)
                return
            }
            
            // FALLBACK: Use API if profile lacks location data
            let response: V2ApiResponse<TimingAdvicePayload> = try await APIClient.shared.fetch(
                .timingAdvice(activity: activity.rawValue, profile: profile),
                cachePolicy: .networkFirst
            )

            let payload = response.data
            let primaryDay: TimingDayPayload
            if payload.todayIsBest == false, let bestUpcoming = payload.bestUpcoming {
                primaryDay = bestUpcoming
            } else {
                primaryDay = payload.today
            }

            let bestTimes = (primaryDay.bestHours ?? []).map(formatHourWindow)
            let avoidTimes = primaryDay.warnings ?? []

            var tips: [String] = []
            if let advice = payload.advice, !advice.isEmpty {
                tips.append(advice)
            }
            tips.append(contentsOf: primaryDay.recommendations ?? [])
            tips = Array(NSOrderedSet(array: tips)).compactMap { $0 as? String }

            let mapped = TimingResult(
                activity: activity.rawValue,
                score: Double(primaryDay.score) / 100.0,
                rating: primaryDay.rating,
                bestTimes: bestTimes,
                avoidTimes: avoidTimes,
                tips: tips,
                generatedAt: primaryDay.date
            )

            timingResult = mapped
            cachedResult = mapped // Cache for later
            HapticManager.notification(.success)
        } catch {
            self.error = error.localizedDescription
            HapticManager.notification(.error)
        }
    }
}

// MARK: - Skeleton Row

struct TimingSkeletonRow: View {
    @State private var isAnimating = false
    
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(Color.borderSubtle)
                .frame(width: 20, height: 20)
            
            RoundedRectangle(cornerRadius: 4)
                .fill(Color.borderSubtle.opacity(0.7))
                .frame(height: 12)
        }
        .opacity(isAnimating ? 0.5 : 1.0)
        .animation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true), value: isAnimating)
        .onAppear { isAnimating = true }
    }
}

// MARK: - Activity Enum

enum TimingActivity: String, CaseIterable {
    case businessMeeting = "business_meeting"
    case romanceDate = "romance_date"
    case jobInterview = "job_interview"
    case creativeWork = "creative_work"
    case financialDecision = "financial_decision"
    case travel = "travel"
    case signingContracts = "signing_contracts"
    case startingProject = "starting_project"
    case meditationSpiritual = "meditation_spiritual"
    
    var displayName: String {
        switch self {
        case .businessMeeting: return "Meeting"
        case .romanceDate: return "Date"
        case .jobInterview: return "Interview"
        case .creativeWork: return "Create"
        case .financialDecision: return "Finance"
        case .travel: return "Travel"
        case .signingContracts: return "Sign"
        case .startingProject: return "Start"
        case .meditationSpiritual: return "Meditate"
        }
    }
    
    var emoji: String {
        switch self {
        case .businessMeeting: return "💼"
        case .romanceDate: return "❤️"
        case .jobInterview: return "🎯"
        case .creativeWork: return "🎨"
        case .financialDecision: return "💰"
        case .travel: return "✈️"
        case .signingContracts: return "✍️"
        case .startingProject: return "🚀"
        case .meditationSpiritual: return "🧘"
        }
    }
}

// MARK: - Data Model

/// Raw payload returned by `POST /v2/timing/advice`.
/// We map this into `TimingResult` for the existing UI.
struct TimingAdvicePayload: Decodable {
    let activity: String
    let advice: String?
    let today: TimingDayPayload
    let bestUpcoming: TimingDayPayload?
    let todayIsBest: Bool?
    let allDays: [TimingDayPayload]?

    enum CodingKeys: String, CodingKey {
        case activity
        case advice
        case today
        case bestUpcoming = "best_upcoming"
        case todayIsBest = "today_is_best"
        case allDays = "all_days"
    }
}

struct TimingDayPayload: Decodable {
    let date: String
    let score: Int
    let rating: String
    let warnings: [String]?
    let recommendations: [String]?
    let bestHours: [TimingHourPayload]?
    let weekday: String?

    enum CodingKeys: String, CodingKey {
        case date
        case score
        case rating
        case warnings
        case recommendations
        case bestHours = "best_hours"
        case weekday
    }
}

struct TimingHourPayload: Decodable {
    let start: String
    let end: String
    let planet: String
}

struct TimingResult: Codable, Equatable {
    let activity: String
    let score: Double
    let rating: String
    let bestTimes: [String]
    let avoidTimes: [String]
    let tips: [String]
    let generatedAt: String
    
    enum CodingKeys: String, CodingKey {
        case activity, score, rating, tips
        case bestTimes = "best_times"
        case avoidTimes = "avoid_times"
        case generatedAt = "generated_at"
    }
}

struct TimingBenefitRow: View {
    let icon: String
    let color: Color
    let text: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundStyle(color)
                .frame(width: 20)
            
            Text(text)
                .font(.subheadline)
        }
    }
}

#Preview {
    NavigationStack {
        TimingAdvisorView()
            .environment(AppStore.shared)
            .preferredColorScheme(.dark)
    }
}
