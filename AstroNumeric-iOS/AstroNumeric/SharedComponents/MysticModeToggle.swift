// MysticModeToggle.swift
// Custom segmented control replacing the stock Toggle for the Mystic / Mundane switch.
// Sliding capsule with weighted labels, tracking animation, and snap haptic.

import SwiftUI

struct MysticModeToggle: View {
    @Binding var isMystic: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Namespace private var ns

    private let labels = ["MUNDANE", "MYSTIC"]

    var body: some View {
        HStack(spacing: 0) {
            ForEach(Array(labels.enumerated()), id: \.offset) { idx, label in
                let active = (idx == 1) == isMystic
                Button {
                    HapticManager.impact(.light)
                    withAnimation(reduceMotion ? nil : Motion.press) {
                        isMystic = (idx == 1)
                    }
                } label: {
                    Text(label)
                        .font(.system(.caption, design: .monospaced))
                        .fontWeight(active ? .bold : .regular)
                        .tracking(active ? 2.5 : 1.5)
                        .foregroundStyle(active ? .white : Color.textMuted)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(
                            ZStack {
                                if active {
                                    Capsule()
                                        .fill(
                                            LinearGradient(
                                                colors: [
                                                    Color.cosmicPurple.opacity(0.85),
                                                    Color.cosmicPurple.opacity(0.55)
                                                ],
                                                startPoint: .topLeading,
                                                endPoint: .bottomTrailing
                                            )
                                        )
                                        .matchedGeometryEffect(id: "modeCapsule", in: ns)
                                        .shadow(color: .cosmicPurple.opacity(0.45), radius: 12, y: 4)
                                }
                            }
                        )
                        .contentShape(Capsule())
                }
                .buttonStyle(.plain)
                .accessibilityLabel(label.capitalized)
                .accessibilityAddTraits(active ? [.isSelected, .isButton] : .isButton)
            }
        }
        .padding(4)
        .background(
            Capsule().fill(Color.white.opacity(0.04))
        )
        .overlay(
            Capsule().stroke(Color.borderSubtle, lineWidth: Stroke.hairline)
        )
        .accessibilityElement(children: .contain)
        .accessibilityValue(isMystic ? "tern.mysticModeToggle.0a".localized : "tern.mysticModeToggle.0b".localized)
    }
}

#Preview {
    @Previewable @State var on = true
    return MysticModeToggle(isMystic: $on)
        .padding()
        .background(Color.appBackground)
}
