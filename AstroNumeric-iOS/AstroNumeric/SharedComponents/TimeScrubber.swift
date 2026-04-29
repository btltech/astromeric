// TimeScrubber.swift
// Premium replacement for the stock Slider used by Time Travel.
// Tick marks for ±N days, a glowing today marker, snap haptic on each step.

import SwiftUI

struct TimeScrubber: View {
    @Binding var offset: Double
    var range: ClosedRange<Double> = -7...7
    var step: Double = 1
    var onChange: ((Double) -> Void)? = nil

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var lastTick: Double = 0

    private var tickCount: Int { Int((range.upperBound - range.lowerBound) / step) + 1 }

    var body: some View {
        VStack(spacing: 12) {
            GeometryReader { geo in
                let width = geo.size.width
                let pct = (offset - range.lowerBound) / (range.upperBound - range.lowerBound)
                let knobX = width * CGFloat(pct)

                ZStack(alignment: .leading) {
                    // Track
                    Capsule()
                        .fill(Color.white.opacity(0.06))
                        .frame(height: 4)

                    // Filled center→knob highlight
                    Capsule()
                        .fill(
                            LinearGradient(
                                colors: [.cosmicPurple.opacity(0.0), .cosmicPurple.opacity(0.55)],
                                startPoint: offset >= 0 ? .leading : .trailing,
                                endPoint: offset >= 0 ? .trailing : .leading
                            )
                        )
                        .frame(
                            width: abs(knobX - width / 2),
                            height: 4
                        )
                        .offset(x: offset >= 0 ? width / 2 : knobX)

                    // Ticks
                    ForEach(0..<tickCount, id: \.self) { i in
                        let x = width * CGFloat(i) / CGFloat(tickCount - 1)
                        let isCenter = i == tickCount / 2
                        Circle()
                            .fill(isCenter ? Color.cosmicPurple : Color.white.opacity(0.25))
                            .frame(width: isCenter ? 6 : 3, height: isCenter ? 6 : 3)
                            .shadow(
                                color: isCenter ? .cosmicPurple.opacity(0.6) : .clear,
                                radius: isCenter ? 6 : 0
                            )
                            .position(x: x, y: 8)
                    }

                    // Knob
                    Circle()
                        .fill(.white)
                        .frame(width: 18, height: 18)
                        .overlay(
                            Circle()
                                .stroke(Color.cosmicPurple.opacity(0.55), lineWidth: 2)
                        )
                        .shadow(color: .cosmicPurple.opacity(0.5), radius: 10)
                        .position(x: knobX, y: 8)
                        .gesture(
                            DragGesture(minimumDistance: 0)
                                .onChanged { value in
                                    let raw = (value.location.x / width)
                                        * (range.upperBound - range.lowerBound)
                                        + range.lowerBound
                                    let clamped = min(max(raw, range.lowerBound), range.upperBound)
                                    let snapped = (clamped / step).rounded() * step
                                    if snapped != lastTick {
                                        HapticManager.impact(.light)
                                        lastTick = snapped
                                    }
                                    offset = snapped
                                    onChange?(snapped)
                                }
                                .onEnded { _ in
                                    if offset == 0 { HapticManager.impact(.medium) }
                                }
                        )
                }
                .frame(height: 20)
            }
            .frame(height: 20)

            // Labels row
            HStack {
                Text("ui.timeScrubber.0".localized)
                    .font(.system(.caption2, design: .monospaced))
                    .foregroundStyle(Color.textMuted)
                Spacer()
                Text(label)
                    .font(.system(.caption, design: .monospaced))
                    .fontWeight(.semibold)
                    .foregroundStyle(.white)
                    .contentTransition(.numericText())
                    .animation(reduceMotion ? nil : Motion.press, value: offset)
                Spacer()
                Text("ui.timeScrubber.1".localized)
                    .font(.system(.caption2, design: .monospaced))
                    .foregroundStyle(Color.textMuted)
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Time travel scrubber")
        .accessibilityValue(label)
        .accessibilityAdjustableAction { dir in
            switch dir {
            case .increment:
                offset = min(offset + step, range.upperBound)
                HapticManager.impact(.light)
                onChange?(offset)
            case .decrement:
                offset = max(offset - step, range.lowerBound)
                HapticManager.impact(.light)
                onChange?(offset)
            @unknown default: break
            }
        }
    }

    private var label: String {
        if offset == 0 { return "TODAY" }
        let n = Int(offset)
        return n > 0 ? "+\(n)D · FUTURE" : "\(n)D · PAST"
    }
}
