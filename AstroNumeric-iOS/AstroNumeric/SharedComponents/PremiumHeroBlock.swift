// PremiumHeroBlock.swift
// The polished hero tile used by HomeView's bento grid.
// Animated gradient, grain overlay, lit-from-above highlight, refined chevron.

import SwiftUI

struct PremiumHeroBlock: View {
    let eyebrow: String
    let headline: String
    let support: String
    let isMystic: Bool

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var gradientPhase: CGFloat = 0

    var body: some View {
        ZStack(alignment: .bottomLeading) {
            // Animated gradient base
            LinearGradient(
                colors: [.heroGradientStart, .heroGradientEnd],
                startPoint: UnitPoint(x: 0, y: gradientPhase),
                endPoint: UnitPoint(x: 1, y: 1 - gradientPhase * 0.4)
            )

            // Soft inner glow top-left
            RadialGradient(
                colors: [Color.white.opacity(0.18), .clear],
                center: .topLeading,
                startRadius: 10,
                endRadius: 240
            )
            .blendMode(.plusLighter)

            // Grain overlay
            GrainOverlay(intensity: 0.08, density: 1800)

            // Content
            VStack(alignment: .leading, spacing: 10) {
                HStack(spacing: 6) {
                    Image(systemName: "sun.max.fill")
                        .font(.caption.weight(.semibold))
                        .symbolRenderingMode(.hierarchical)
                    Text(eyebrow)
                        .font(.system(.caption, design: .monospaced))
                        .fontWeight(.bold)
                        .tracking(1.5)
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(
                    Capsule()
                        .fill(.ultraThinMaterial)
                        .overlay(Capsule().stroke(.white.opacity(0.2), lineWidth: Stroke.hairline))
                )

                Text(headline)
                    .font(.system(.title3, design: .serif)).fontWeight(.semibold)
                    .lineLimit(3)
                    .multilineTextAlignment(.leading)
                    .animation(.easeInOut(duration: 0.25), value: isMystic)

                Text(support)
                    .font(.footnote)
                    .foregroundStyle(.white.opacity(0.78))
                    .lineLimit(2)
            }
            .padding(20)
            .foregroundStyle(.white)

            // Refined chevron in top-right
            VStack {
                HStack {
                    Spacer()
                    chevronBadge
                }
                Spacer()
            }
            .padding(16)
        }
        .frame(height: 220)
        .clipShape(RoundedRectangle(cornerRadius: Radius.lg))
        .overlay(
            RoundedRectangle(cornerRadius: Radius.lg)
                .stroke(.white.opacity(0.12), lineWidth: Stroke.emphasized)
        )
        .overlay(PremiumTopHighlight(cornerRadius: Radius.lg))
        .featureShadow(tint: .cosmicPurple)
        .onAppear {
            guard !reduceMotion else { return }
            withAnimation(Motion.ambient) { gradientPhase = 1 }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(eyebrow). \(headline). \(support)")
        .accessibilityAddTraits(.isButton)
    }

    private var chevronBadge: some View {
        ZStack {
            Circle()
                .stroke(.white.opacity(0.45), lineWidth: 1.5)
                .frame(width: 30, height: 30)
            Image(systemName: "chevron.right")
                .font(.caption.weight(.bold))
                .foregroundStyle(.white)
        }
    }
}
