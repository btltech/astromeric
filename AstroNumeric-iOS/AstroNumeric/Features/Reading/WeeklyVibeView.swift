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
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            headerSection
            
            // Timeline
            if viewModel.isLoading {
                loadingView
            } else if !viewModel.days.isEmpty {
                timelineSection
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
                                .fill(Color.purple.opacity(0.2))
                        )
                        .foregroundStyle(.purple)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }
    
    // MARK: - Timeline
    
    private var timelineSection: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(viewModel.days) { day in
                    VibeDayCard(day: day)
                }
            }
            .padding(.horizontal, 4)
        }
    }
    
    // MARK: - States
    
    private var loadingView: some View {
        HStack(spacing: 12) {
            ForEach(0..<7, id: \.self) { _ in
                RoundedRectangle(cornerRadius: 16)
                    .fill(.ultraThinMaterial)
                    .frame(width: 70, height: 100)
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
        .frame(width: 70, height: 110)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(day.isToday ? Color.purple : Color.clear)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(.ultraThinMaterial)
                        .opacity(day.isToday ? 0 : 1)
                )
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .strokeBorder(day.isToday ? Color.purple : Color.clear, lineWidth: 2)
        )
    }
    
    private var scoreColor: Color {
        if day.score >= 80 { return .yellow }
        if day.score >= 60 { return .purple }
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
            WeeklyVibeView(showShare: showShare)
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
                .mask(content)
            )
            .onAppear {
                withAnimation(.linear(duration: 1.5).repeatForever(autoreverses: false)) {
                    phase = 200
                }
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
