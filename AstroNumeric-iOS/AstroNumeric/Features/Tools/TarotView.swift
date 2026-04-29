// TarotView.swift
// Daily tarot card draw with flip animation

import SwiftUI

struct TarotView: View {
    @Environment(AppStore.self) private var store
    @State private var tarotCard: TarotCard?
    @State private var isLoading = false
    @State private var isFlipped = false
    @State private var error: String?
    
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
            
            VStack(spacing: 24) {
                PremiumHeroCard(
                            eyebrow: "hero.tarot.eyebrow".localized,
                            title: "hero.tarot.title".localized,
                            bodyText: "hero.tarot.body".localized,
                            accent: [Color(hex: "24123a"), Color(hex: "6a39b2"), Color(hex: "b35582")],
                            chips: ["hero.tarot.chip.0".localized, "hero.tarot.chip.1".localized, "hero.tarot.chip.2".localized]
                        )

                // Card display
                cardSection
                
                // Draw button - show initially or after card is revealed
                if !isLoading {
                    if tarotCard == nil {
                        drawButton
                    } else if isFlipped {
                        drawAgainButton
                    }
                }
                
                // Card details
                if let card = tarotCard, isFlipped {
                    PremiumSectionHeader(
                title: "section.tarot.0.title".localized,
                subtitle: "section.tarot.0.subtitle".localized
            )

                    cardDetails(card)
                }
            }
            .padding()
            .alert(
                "Daily Tarot",
                isPresented: Binding(
                    get: { error != nil },
                    set: { newValue in if !newValue { error = nil } }
                )
            ) {
                Button("action.ok".localized, role: .cancel) {}
            } message: {
                Text(error ?? "Something went wrong.")
            }
            .readableContainer()
        }
        .navigationTitle("screen.tarot".localized)
        .navigationBarTitleDisplayMode(.inline)
    }
    
    private var cardSection: some View {
        ZStack {
            // Card back
            RoundedRectangle(cornerRadius: 16)
                .fill(
                    LinearGradient(
                        colors: [.purple.opacity(0.8), .indigo.opacity(0.8)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .frame(width: 200, height: 300)
                .overlay(
                    VStack {
                        Image(systemName: "star.fill")
                            .font(.system(.largeTitle))
                            .foregroundStyle(.white.opacity(0.5))
                        Text("✦")
                            .font(.system(.largeTitle))
                            .foregroundStyle(.white.opacity(0.3))
                    }
                )
                .rotation3DEffect(
                    .degrees(isFlipped ? 180 : 0),
                    axis: (x: 0, y: 1, z: 0)
                )
                .opacity(isFlipped ? 0 : 1)
            
            // Card front
            if let card = tarotCard {
                cardFront(card)
                    .rotation3DEffect(
                        .degrees(isFlipped ? 0 : -180),
                        axis: (x: 0, y: 1, z: 0)
                    )
                    .opacity(isFlipped ? 1 : 0)
            }
        }
        .animation(.spring(duration: 0.6), value: isFlipped)
    }
    
    private func cardFront(_ card: TarotCard) -> some View {
        RoundedRectangle(cornerRadius: 16)
            .fill(
                LinearGradient(
                    colors: [.white.opacity(0.1), .purple.opacity(0.2)],
                    startPoint: .top,
                    endPoint: .bottom
                )
            )
            .frame(width: 200, height: 300)
            .overlay(
                VStack(spacing: 12) {
                    Text(tarotEmoji(for: card.name))
                        .font(.system(.largeTitle))
                    
                    Text(card.name)
                        .font(.title3.bold())
                        .foregroundStyle(.white)
                        .multilineTextAlignment(.center)
                    
                    Text(card.suit)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                    
                    HStack {
                        Image(systemName: card.upright ? "tern.tarot.0a".localized : "tern.tarot.0b".localized)
                        Text(card.upright ? "tern.tarot.1a".localized : "tern.tarot.1b".localized)
                    }
                    .font(.caption2)
                    .foregroundStyle(card.upright ? .green : .orange)
                }
                .padding()
            )
    }
    
    private func cardDetails(_ card: TarotCard) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("ui.tarot.0".localized)
                .font(.headline)
            
            Text(card.meaning)
                .font(.body)
                .foregroundStyle(Color.textSecondary)
            
            Text("ui.tarot.1".localized)
                .font(.headline)
                .padding(.top, 8)
            
            Text(card.interpretation)
                .font(.body)
                .foregroundStyle(Color.textSecondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(.ultraThinMaterial)
        )
        .transition(.move(edge: .bottom).combined(with: .opacity))
    }
    
    private var drawButton: some View {
        Button {
            Task {
                await drawCard()
            }
        } label: {
            HStack {
                Image(systemName: "sparkles")
                Text("ui.tarot.2".localized)
            }
            .font(.headline)
            .foregroundStyle(.white)
            .padding(.horizontal, 24)
            .padding(.vertical, 14)
            .background(
                Capsule()
                    .fill(
                        LinearGradient(
                            colors: [.purple, .indigo],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
            )
        }
        .disabled(isLoading)
    }
    
    private var drawAgainButton: some View {
        Button {
            // Reset and draw new card
            withAnimation(.spring(duration: 0.3)) {
                isFlipped = false
                tarotCard = nil
            }
            // Small delay before drawing new card
            Task {
                try? await Task.sleep(for: .milliseconds(400))
                await drawCard()
            }
        } label: {
            HStack {
                Image(systemName: "arrow.trianglehead.2.counterclockwise.rotate.90")
                Text("ui.tarot.3".localized)
            }
            .font(.subheadline.weight(.medium))
            .foregroundStyle(.purple)
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
            .background(
                Capsule()
                    .strokeBorder(Color.purple.opacity(0.5), lineWidth: 1)
            )
        }
        .disabled(isLoading)
    }
    
    private func drawCard() async {
        isLoading = true
        defer { isLoading = false }
        error = nil
        isFlipped = false
        
        do {
            let response: V2ApiResponse<TarotCard> = try await APIClient.shared.fetch(
                .dailyTarot()
            )
            tarotCard = response.data
            
            // Delay flip for effect
            try? await Task.sleep(for: .milliseconds(300))
            withAnimation {
                isFlipped = true
            }
            HapticManager.notification(.success)
        } catch {
            self.error = "Could not draw card"
        }
    }
    
    private func tarotEmoji(for name: String) -> String {
        let emojis: [String: String] = [
            "The Fool": "🃏",
            "The Magician": "🪄",
            "The High Priestess": "🌙",
            "The Empress": "👑",
            "The Emperor": "⚔️",
            "The Hierophant": "📿",
            "The Lovers": "💕",
            "The Chariot": "🏎️",
            "Strength": "🦁",
            "The Hermit": "🏔️",
            "Wheel of Fortune": "🎡",
            "Justice": "⚖️",
            "The Hanged Man": "🙃",
            "Death": "💀",
            "Temperance": "☯️",
            "The Devil": "😈",
            "The Tower": "🗼",
            "The Star": "⭐",
            "The Moon": "🌕",
            "The Sun": "☀️",
            "Judgement": "📯",
            "The World": "🌍"
        ]
        return emojis[name] ?? "🎴"
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        TarotView()
            .environment(AppStore.shared)
    }
    .preferredColorScheme(.dark)
}
