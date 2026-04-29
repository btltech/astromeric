// PremiumSkeleton.swift
// Shimmer loading placeholders for premium "Loading…" states.
// Named with `Premium` prefix to avoid collision with the legacy `SkeletonView` in
// `LoadingOverlay.swift`.

import SwiftUI

struct PremiumSkeleton: View {
    var cornerRadius: CGFloat = Radius.sm
    var height: CGFloat = 14
    var width: CGFloat? = nil

    @State private var phase: CGFloat = -1
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        RoundedRectangle(cornerRadius: cornerRadius)
            .fill(Color.white.opacity(0.06))
            .frame(width: width, height: height)
            .overlay(
                GeometryReader { geo in
                    LinearGradient(
                        colors: [.clear, .white.opacity(0.18), .clear],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                    .frame(width: geo.size.width * 0.6)
                    .offset(x: phase * geo.size.width)
                    .blendMode(.overlay)
                }
            )
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius))
            .onAppear {
                guard !reduceMotion else { return }
                withAnimation(.linear(duration: 1.4).repeatForever(autoreverses: false)) {
                    phase = 1.6
                }
            }
            .accessibilityHidden(true)
    }
}

struct PremiumSkeletonStack: View {
    let lines: Int
    var spacing: CGFloat = 8

    var body: some View {
        VStack(alignment: .leading, spacing: spacing) {
            ForEach(0..<lines, id: \.self) { i in
                PremiumSkeleton(height: 12, width: i == lines - 1 ? 120 : nil)
            }
        }
    }
}
