// AffirmationView.swift
// Daily affirmation display

import SwiftUI

struct AffirmationView: View {
    @Environment(AppStore.self) private var store
    @State private var affirmation: String?
    @State private var isLoading = false
    @State private var showAnimation = false
    
    private let affirmations = [
        "You are aligned with the universe's infinite possibilities.",
        "Your intuition guides you toward your highest good.",
        "Today, you radiate positive energy and attract abundance.",
        "You trust the timing of your life's journey.",
        "Your inner wisdom illuminates the path ahead.",
        "You are worthy of all the good that comes your way.",
        "The stars have aligned in your favor today.",
        "You embrace change as an opportunity for growth.",
        "Your energy creates your reality—shine bright.",
        "You are connected to the cosmic flow of abundance."
    ]
    
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
            
            VStack(spacing: 32) {
                Spacer()

                PremiumHeroCard(
                            eyebrow: "hero.affirmation.eyebrow".localized,
                            title: "hero.affirmation.title".localized,
                            bodyText: "hero.affirmation.body".localized,
                            accent: [Color(hex: "2a1437"), Color(hex: "8e3fa7"), Color(hex: "d86d71")],
                            chips: ["hero.affirmation.chip.0".localized, "hero.affirmation.chip.1".localized, "hero.affirmation.chip.2".localized]
                        )
                
                // Affirmation display
                if let affirmation = affirmation {
                    affirmationCard(affirmation)
                } else {
                    placeholderCard
                }

                refreshButton
                
                Spacer()
            }
            .padding()
            .readableContainer()
        }
        .navigationTitle("screen.affirmation".localized)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            if affirmation == nil {
                Task { await loadAffirmation(forceRefresh: false) }
            }
        }
    }
    
    private func affirmationCard(_ text: String) -> some View {
        VStack(spacing: 24) {
            // Star decoration
            HStack(spacing: 8) {
                ForEach(0..<5, id: \.self) { i in
                    Image(systemName: "star.fill")
                        .font(.caption)
                        .foregroundStyle(.yellow)
                        .scaleEffect(showAnimation ? 1 : 0.5)
                        .animation(
                            .spring(duration: 0.5).delay(Double(i) * 0.1),
                            value: showAnimation
                        )
                }
            }
            
            Text(text)
                .font(.title2)
                .fontWeight(.medium)
                .multilineTextAlignment(.center)
                .foregroundStyle(.white)
                .opacity(showAnimation ? 1 : 0)
                .animation(.easeIn(duration: 0.5).delay(0.3), value: showAnimation)
            
            // Sparkle decoration
            Image(systemName: "sparkles")
                .font(.title)
                .foregroundStyle(.purple)
                .scaleEffect(showAnimation ? 1 : 0)
                .animation(.spring(duration: 0.6).delay(0.5), value: showAnimation)
        }
        .padding(32)
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 24)
                .fill(
                    LinearGradient(
                        colors: [.purple.opacity(0.3), .indigo.opacity(0.2)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 24)
                        .strokeBorder(.white.opacity(0.1), lineWidth: 1)
                )
        )
    }
    
    private var placeholderCard: some View {
        VStack(spacing: 16) {
            if isLoading {
                ProgressView()
                    .scaleEffect(1.5)
                Text("ui.affirmation.0".localized)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
            } else {
                Image(systemName: "sun.max.fill")
                    .font(.system(.largeTitle))
                    .foregroundStyle(.yellow.opacity(0.5))
                Text("ui.affirmation.1".localized)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
            }
        }
        .padding(32)
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 24)
                .fill(.ultraThinMaterial)
        )
    }
    
    private var refreshButton: some View {
        Button {
            Task {
                await loadAffirmation(forceRefresh: true)
            }
        } label: {
            HStack {
                Image(systemName: "arrow.clockwise")
                Text(store.activeProfile == nil ? "tern.affirmation.0a".localized : "tern.affirmation.0b".localized)
            }
            .font(.headline)
            .foregroundStyle(.white)
            .padding(.horizontal, 24)
            .padding(.vertical, 14)
            .background(
                Capsule()
                    .fill(
                        LinearGradient(
                            colors: [.orange, .pink],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
            )
        }
        .disabled(isLoading)
    }
    
    @MainActor
    private func loadAffirmation(forceRefresh: Bool) async {
        withAnimation {
            showAnimation = false
            affirmation = nil
        }
        
        isLoading = true
        defer { isLoading = false }
        
        guard let profile = store.activeProfile else {
            affirmation = affirmations.randomElement()
            showAnimation = true
            return
        }
        
        do {
            let response: V2ApiResponse<AffirmationResponse> = try await APIClient.shared.fetch(
                .dailyAffirmation(profile: profile),
                cachePolicy: forceRefresh ? .networkFirst : .cacheFirst
            )
            affirmation = response.data.affirmation
            showAnimation = true
            HapticManager.notification(.success)
        } catch {
            affirmation = affirmations.randomElement()
            showAnimation = true
            HapticManager.notification(.success)
        }
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        AffirmationView()
            .environment(AppStore.shared)
    }
    .preferredColorScheme(.dark)
}
