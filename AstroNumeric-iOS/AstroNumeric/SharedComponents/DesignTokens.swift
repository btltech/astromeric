// DesignTokens.swift
// Centralized radius, shadow, stroke, motion, and grain tokens for premium consistency.
// Use these everywhere instead of hard-coded literals.

import SwiftUI

// MARK: - Radius Scale

enum Radius {
    /// 12pt – chips, inline pills, small inputs.
    static let sm: CGFloat = 12
    /// 20pt – standard cards and bento tiles.
    static let md: CGFloat = 20
    /// 28pt – hero surfaces and full-width feature blocks.
    static let lg: CGFloat = 28
    /// 14pt – legacy/transition value while migrating older surfaces. Prefer `sm`/`md`.
    static let legacy: CGFloat = 14
}

// MARK: - Stroke Scale

enum Stroke {
    /// Hairline 0.5pt – default for standard cards.
    static let hairline: CGFloat = 0.5
    /// 1pt – reserved for hero / emphasized surfaces.
    static let emphasized: CGFloat = 1
}

// MARK: - Elevation Shadows

enum Elevation {
    /// Resting card – soft, low-contrast.
    static func card<V: View>(_ view: V) -> some View {
        view.shadow(color: .black.opacity(0.32), radius: 14, x: 0, y: 8)
    }

    /// Featured tile – deeper, with a tint hint.
    static func feature<V: View>(_ view: V, tint: Color = .cosmicPurple) -> some View {
        view
            .shadow(color: .black.opacity(0.40), radius: 22, x: 0, y: 12)
            .shadow(color: tint.opacity(0.18), radius: 32, x: 0, y: 0)
    }
}

extension View {
    /// Apply the resting card elevation.
    func elevatedCardShadow() -> some View {
        self.shadow(color: .black.opacity(0.32), radius: 14, x: 0, y: 8)
    }

    /// Apply the featured (hero) elevation with tinted aura.
    func featureShadow(tint: Color = .cosmicPurple) -> some View {
        self
            .shadow(color: .black.opacity(0.40), radius: 22, x: 0, y: 12)
            .shadow(color: tint.opacity(0.18), radius: 32, x: 0, y: 0)
    }
}

// MARK: - Inner Top Highlight

/// A subtle "lit-from-above" inner highlight used on premium dark surfaces.
struct PremiumTopHighlight: View {
    let cornerRadius: CGFloat

    var body: some View {
        RoundedRectangle(cornerRadius: cornerRadius)
            .stroke(
                LinearGradient(
                    colors: [
                        Color.white.opacity(0.18),
                        Color.white.opacity(0.04),
                        Color.clear
                    ],
                    startPoint: .top,
                    endPoint: .center
                ),
                lineWidth: Stroke.hairline
            )
            .blendMode(.plusLighter)
            .allowsHitTesting(false)
    }
}

// MARK: - Grain Overlay

/// Procedural film-grain overlay drawn with Canvas. Gives premium dark UIs their characteristic
/// "tactile" feel and breaks up flat gradients. Intensity is intentionally low (`opacity` ~0.06).
struct GrainOverlay: View {
    var intensity: Double = 0.06
    var density: Int = 1400
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        Canvas { context, size in
            // Deterministic seed so grain doesn't shimmer between renders unless we want it.
            var generator = SeededGenerator(seed: 42)
            for _ in 0..<density {
                let x = Double.random(in: 0...size.width, using: &generator)
                let y = Double.random(in: 0...size.height, using: &generator)
                let s = Double.random(in: 0.4...1.4, using: &generator)
                let alpha = Double.random(in: 0.15...0.55, using: &generator) * intensity
                let rect = CGRect(x: x, y: y, width: s, height: s)
                context.fill(Path(ellipseIn: rect), with: .color(.white.opacity(alpha)))
            }
        }
        .blendMode(.overlay)
        .allowsHitTesting(false)
        .accessibilityHidden(true)
    }
}

private struct SeededGenerator: RandomNumberGenerator {
    private var state: UInt64
    init(seed: UInt64) { self.state = seed == 0 ? 0xdeadbeef : seed }
    mutating func next() -> UInt64 {
        state ^= state << 13
        state ^= state >> 7
        state ^= state << 17
        return state
    }
}

// MARK: - Motion Tokens

enum Motion {
    /// Standard spring used for tap / press feedback.
    static let press = Animation.spring(response: 0.28, dampingFraction: 0.78)
    /// Stage entrance spring for reveal cascades.
    static let enter = Animation.spring(response: 0.55, dampingFraction: 0.82)
    /// Slow ambient loop (gradient drift, aura pulse).
    static let ambient = Animation.easeInOut(duration: 3.6).repeatForever(autoreverses: true)

    /// Staggered delay for staged reveals.
    static func stagger(index: Int, base: Double = 0.06) -> Double {
        Double(index) * base
    }
}

// MARK: - Premium Card Background Builder

/// Composable premium surface used by both `CardView` and bespoke bento tiles.
/// Combines fill + top highlight + (optional) grain + hairline stroke.
struct PremiumCardBackground: View {
    var cornerRadius: CGFloat = Radius.md
    var fill: AnyShapeStyle = AnyShapeStyle(Color.surfaceElevated)
    var stroke: Color = .borderSubtle
    var strokeWidth: CGFloat = Stroke.hairline
    var withGrain: Bool = false

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: cornerRadius)
                .fill(fill)

            if withGrain {
                GrainOverlay()
                    .clipShape(RoundedRectangle(cornerRadius: cornerRadius))
            }

            // Outer hairline stroke
            RoundedRectangle(cornerRadius: cornerRadius)
                .stroke(stroke, lineWidth: strokeWidth)

            // Inner lit-from-above highlight
            PremiumTopHighlight(cornerRadius: cornerRadius)
        }
        .compositingGroup()
    }
}
