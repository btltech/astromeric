// WeeklyVibeView.swift
// 7-day cosmic energy timeline with share functionality

import SwiftUI

struct WeeklyVibeView: View {
    @Environment(AppStore.self) private var store
    @State private var viewModel = WeeklyVibeVM()
    @State private var showShareSheet = false
    @State private var shareItems: [Any] = []
    
    /// Show the share button
    var showShare: Bool = true

    /// On the full page, days are tappable and the chosen day's forecast shows
    /// under the strip. The Home card is itself a link, so it stays a strip.
    var showsDayDetail: Bool = true
    @State private var selectedDayId: String?

    private var selectedDay: ForecastDay? {
        viewModel.days.first { $0.id == selectedDayId } ?? viewModel.days.first
    }

    /// Kept in step with VibeDayCard so the skeleton matches the loaded row.
    @ScaledMetric(relativeTo: .caption) private var cardWidth: CGFloat = 70
    @ScaledMetric(relativeTo: .caption) private var cardMinHeight: CGFloat = 110

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            headerSection
            
            // Timeline
            if viewModel.isLoading {
                loadingView
            } else if !viewModel.days.isEmpty {
                timelineSection
                if showsDayDetail, let day = selectedDay {
                    dayDetail(day)
                }
            } else {
                emptyView
            }
        }
        .task(id: store.activeProfile?.id) {
            if let profile = store.activeProfile {
                await viewModel.fetchForecast(for: profile)
            }
        }
        .sheet(isPresented: $showShareSheet) {
            ShareSheet(items: shareItems)
        }
    }
    
    // MARK: - Header
    
    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                PremiumSectionHeader(
                    title: "weeklyVibe.title".localized,
                    subtitle: "weeklyVibe.subtitle".localized
                )

                Spacer()

                if showShare && store.selectedProfile != nil {
                    Button {
                        shareVibeLink()
                    } label: {
                        HStack(spacing: 4) {
                            Image(systemName: "square.and.arrow.up")
                                .font(.caption)
                            Text("weeklyVibe.share".localized)
                                .font(.caption.weight(.medium))
                        }
                        .padding(.horizontal, 12)
                        .frame(minHeight: 44)
                        .background(
                            Capsule()
                                .fill(Color.accentPrimary.opacity(0.2))
                        )
                        .foregroundStyle(Color.accentPrimary)
                    }
                    .buttonStyle(ScaleButtonStyle())
                }
            }
        }
    }
    
    // MARK: - Timeline
    
    private var timelineSection: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(viewModel.days) { day in
                    if showsDayDetail {
                        Button {
                            selectedDayId = day.id
                            HapticManager.impact(.light)
                        } label: {
                            VibeDayCard(day: day)
                                .overlay(
                                    RoundedRectangle(cornerRadius: Radius.md)
                                        .strokeBorder(Color.white.opacity(0.7), lineWidth: 2)
                                        .opacity(day.id == selectedDay?.id && !day.isToday ? 1 : 0)
                                )
                        }
                        .buttonStyle(ScaleButtonStyle())
                        .accessibilityAddTraits(day.id == selectedDay?.id ? .isSelected : [])
                    } else {
                        VibeDayCard(day: day)
                    }
                }
            }
            .padding(.horizontal, 4)
            .padding(.vertical, 2)
        }
    }

    // MARK: - Day detail

    private func dayDetail(_ day: ForecastDay) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                Text(day.dateObject?.formatted(.dateTime.weekday(.wide).day().month(.wide)) ?? day.weekday)
                    .font(.headline)
                    .foregroundStyle(Color.textPrimary)
                Spacer()
                Text("\(day.icon) \(day.vibe) · \(day.score)%")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(Color.accentPrimary)
            }

            Text(day.recommendation)
                .font(.bodyCopy)
                .foregroundStyle(Color.textPrimary)

            if let overview = day.overview {
                Text(overview)
                    .font(.bodyCopy)
                    .foregroundStyle(Color.textSecondary)
            }

            if let embrace = day.embrace, !embrace.isEmpty {
                detailLine(title: "Good for", items: embrace, icon: "checkmark.circle.fill", color: .green)
            }
            if let avoid = day.avoid, !avoid.isEmpty {
                detailLine(title: "Go easy on", items: avoid, icon: "exclamationmark.circle.fill", color: .orange)
            }
            if let bestTime = day.bestTime {
                Label(bestTime, systemImage: "clock.fill")
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(RoundedRectangle(cornerRadius: Radius.md).fill(.ultraThinMaterial))
        .animation(.easeInOut(duration: 0.2), value: day.id)
    }

    private func detailLine(title: String, items: [String], icon: String, color: Color) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Image(systemName: icon)
                .foregroundStyle(color)
            Text("\(Text("\(title):").fontWeight(.semibold).foregroundStyle(Color.textPrimary)) \(items.joined(separator: ", "))")
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
        }
    }
    
    // MARK: - States
    
    private var loadingView: some View {
        HStack(spacing: 12) {
            ForEach(0..<7, id: \.self) { _ in
                RoundedRectangle(cornerRadius: 16)
                    .fill(.ultraThinMaterial)
                    .frame(width: cardWidth, height: cardMinHeight * 0.9)
                    .shimmer()
            }
        }
    }
    
    private var emptyView: some View {
        Text("weeklyVibe.loading".localized)
            .font(.caption)
            .foregroundStyle(Color.textSecondary)
            .frame(maxWidth: .infinity, alignment: .center)
            .padding(.vertical, 20)
    }
    
    // MARK: - Actions
    
    private func shareVibeLink() {
        guard let profile = store.selectedProfile else { return }

        if store.hideSensitiveDetailsEnabled {
            shareItems = [
                "Check out AstroNumeric's weekly vibe ✨",
                LegalConfig.websiteBaseURL
            ]
        } else {
            let shareURL = viewModel.getShareURL(for: profile)
            UIPasteboard.general.string = shareURL
            if let url = URL(string: shareURL) {
                shareItems = [
                    "Check out my cosmic vibe! 🌟",
                    url
                ]
            } else {
                shareItems = ["Check out my cosmic vibe! 🌟"]
            }
        }
        
        HapticManager.notification(.success)
        showShareSheet = true
    }
}

// MARK: - Vibe Day Card

struct VibeDayCard: View {
    let day: ForecastDay
    /// The card grows with the text inside it: a fixed height clipped the score
    /// row at accessibility sizes.
    @ScaledMetric(relativeTo: .caption) private var cardWidth: CGFloat = 70
    @ScaledMetric(relativeTo: .caption) private var cardMinHeight: CGFloat = 110
    
    var body: some View {
        VStack(spacing: 8) {
            // Day header
            VStack(spacing: 2) {
                Text(day.weekday)
                    .font(.caption.weight(.medium))
                    .foregroundStyle(day.isToday ? .white : .secondary)
                
                Text("\(day.dayNumber)")
                    .font(.subheadline.bold())
                    .foregroundStyle(day.isToday ? .white : .primary)
            }
            
            // Vibe icon with glow
            ZStack {
                // Glow effect
                Circle()
                    .fill(scoreColor.opacity(0.3))
                    .frame(width: 40, height: 40)
                    .blur(radius: 8)
                
                // Icon
                Text(day.icon)
                    .font(.title2)
            }
            
            // Score and vibe
            VStack(spacing: 2) {
                Text(day.vibe)
                    .font(.caption2)
                    .foregroundStyle(Color.textSecondary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                HStack(spacing: 4) {
                    Circle()
                        .fill(scoreColor)
                        .frame(width: 6, height: 6)
                    
                    Text("\(day.score)%")
                        .font(.caption2.bold())
                        .foregroundStyle(scoreColor)
                }
            }
        }
        .frame(width: cardWidth)
        .frame(minHeight: cardMinHeight)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: Radius.md)
                .fill(day.isToday ? Color.accentPrimary : Color.clear)
                .overlay(
                    RoundedRectangle(cornerRadius: Radius.md)
                        .fill(.ultraThinMaterial)
                        .opacity(day.isToday ? 0 : 1)
                )
        )
        .overlay(
            RoundedRectangle(cornerRadius: Radius.md)
                .strokeBorder(day.isToday ? Color.accentPrimary : Color.clear, lineWidth: 2)
        )
    }
    
    private var scoreColor: Color {
        if day.score >= 80 { return .yellow }
        if day.score >= 60 { return .accentPrimary }
        return .red
    }
}

// MARK: - ViewModel

@Observable
final class WeeklyVibeVM {
    var days: [ForecastDay] = []
    var isLoading = false
    var error: String?
    
    private let api = APIClient.shared
    
    @MainActor
    func fetchForecast(for profile: Profile) async {
        guard !isLoading else { return }
        
        isLoading = true
        defer { isLoading = false }
        
        do {
            let response: V2ApiResponse<WeeklyForecastResponse> = try await api.fetch(
                .weeklyForecast(profile: profile),
                cachePolicy: .cacheFirst
            )
            self.days = response.data.days
        } catch {
            self.error = error.localizedDescription
            // Silently fail - weekly vibe is optional content
        }
    }
    
    /// Generate comparison URL for sharing
    func getShareURL(for profile: Profile) -> String {
        let shareableProfile = ShareableProfile(from: profile)
        let encodedProfile = shareableProfile.encode() ?? ""
        let compareURL = LegalConfig.websiteBaseURL.appendingPathComponent("compare")
        var components = URLComponents(url: compareURL, resolvingAgainstBaseURL: false)
        components?.queryItems = [URLQueryItem(name: "p", value: encodedProfile)]
        return components?.url?.absoluteString ?? compareURL.absoluteString
    }
}

// MARK: - Card Wrapper Version

/// Wrapped version for embedding in cards
struct WeeklyVibeCard: View {
    var showShare: Bool = true
    
    var body: some View {
        CardView {
            WeeklyVibeView(showShare: showShare, showsDayDetail: false)
        }
    }
}

// MARK: - Shimmer Modifier

extension View {
    func shimmer() -> some View {
        self.modifier(ShimmerModifier())
    }
}

struct ShimmerModifier: ViewModifier {
    @State private var phase: CGFloat = 0
    
    func body(content: Content) -> some View {
        content
            .overlay(
                LinearGradient(
                    colors: [
                        .clear,
                        .white.opacity(0.3),
                        .clear
                    ],
                    startPoint: .leading,
                    endPoint: .trailing
                )
                .offset(x: phase)
                .animation(.linear(duration: 1.5).repeatForever(autoreverses: false), value: phase)
                .mask(content)
            )
            .onAppear {
                // Repeating animations are attached to the one property they drive, not
                // started with withAnimation in onAppear: that swept any layout change made
                // in the same moment (e.g. a navigation push) into the endless loop too.
                phase = 200
            }
    }
}

// MARK: - Preview

#Preview {
    VStack {
        WeeklyVibeCard()
    }
    .padding()
    .background(Color.black)
    .environment(AppStore.shared)
    .preferredColorScheme(.dark)
}
