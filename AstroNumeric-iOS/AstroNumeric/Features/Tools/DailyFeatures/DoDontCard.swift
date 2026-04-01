// DoDontCard.swift
// Daily Do's and Don'ts — personalized card powered by transits + numerology

import SwiftUI

// MARK: - Data Models

struct DoDontData: Codable {
    let dos: [String]
    let donts: [String]
    let personalDay: Int
    let moonPhase: String
    let mercuryRetrograde: Bool
    let venusRetrograde: Bool

    enum CodingKeys: String, CodingKey {
        case dos, donts
        case personalDay = "personal_day"
        case moonPhase = "moon_phase"
        case mercuryRetrograde = "mercury_retrograde"
        case venusRetrograde = "venus_retrograde"
    }
}

struct BriefBulletData: Codable {
    let emoji: String
    let text: String
}

struct MorningBriefData: Codable {
    let date: Date
    let greeting: String
    let bullets: [BriefBulletData]
    let moonPhase: String
    let personalDay: Int
    let vibe: String

    enum CodingKeys: String, CodingKey {
        case date, greeting, bullets, vibe
        case moonPhase = "moon_phase"
        case personalDay = "personal_day"
    }
}

// MARK: - Do / Don't Card View

struct DoDontCard: View {
    let data: DoDontData
    @State private var showingDonts = false

    var body: some View {
        CardView {
            VStack(spacing: 0) {
                // Header with pill toggle
                HStack {
                    Text("Your Day's Guide")
                        .font(.headline)
                    Spacer()
                    // Pill toggle
                    HStack(spacing: 0) {
                        pillButton(label: "✅ Do", isSelected: !showingDonts) {
                            withAnimation(.spring(response: 0.3)) { showingDonts = false }
                        }
                        pillButton(label: "🚫 Avoid", isSelected: showingDonts) {
                            withAnimation(.spring(response: 0.3)) { showingDonts = true }
                        }
                    }
                    .background(.ultraThinMaterial)
                    .clipShape(Capsule())
                }
                .padding(.bottom, 16)

                // Retrograde badges
                if data.mercuryRetrograde || data.venusRetrograde {
                    HStack(spacing: 8) {
                        if data.mercuryRetrograde {
                            retrogradeBadge("☿ Mercury Rx", color: .orange)
                        }
                        if data.venusRetrograde {
                            retrogradeBadge("♀ Venus Rx", color: .pink)
                        }
                        Spacer()
                    }
                    .padding(.bottom, 12)
                }

                // List items with animated swap
                let items = showingDonts ? data.donts : data.dos
                VStack(spacing: 12) {
                    ForEach(Array(items.enumerated()), id: \.offset) { index, item in
                        HStack(alignment: .top, spacing: 12) {
                            // Number circle
                            ZStack {
                                Circle()
                                    .fill(showingDonts ? Color.red.opacity(0.15) : Color.green.opacity(0.15))
                                    .frame(width: 28, height: 28)
                                Text("\(index + 1)")
                                    .font(.caption.bold())
                                    .foregroundStyle(showingDonts ? .red : .green)
                            }

                            Text(item)
                                .font(.subheadline)
                                .foregroundStyle(Color.textPrimary)
                                .fixedSize(horizontal: false, vertical: true)

                            Spacer(minLength: 0)
                        }
                        .transition(.asymmetric(
                            insertion: .move(edge: .trailing).combined(with: .opacity),
                            removal: .move(edge: .leading).combined(with: .opacity)
                        ))
                        .id("\(showingDonts)-\(index)")
                    }
                }

                // Personal Day footer
                Divider()
                    .padding(.vertical, 12)

                HStack {
                    Text("🔢")
                    Text("Personal Day \(data.personalDay) · \(data.moonPhase)")
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                    Spacer()
                }
            }
        }
    }

    @ViewBuilder
    private func pillButton(label: String, isSelected: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(label)
                .font(.subheadline.bold())
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(isSelected ? Color.accentColor : Color.clear)
                .foregroundStyle(isSelected ? .white : Color.textSecondary)
                .clipShape(Capsule())
                .shadow(color: isSelected ? .black.opacity(0.2) : .clear, radius: 4, x: 0, y: 2)
        }
        .buttonStyle(.plain)
    }

    @ViewBuilder
    private func retrogradeBadge(_ label: String, color: Color) -> some View {
        Text(label)
            .font(.caption.bold())
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(color.opacity(0.15))
            .foregroundStyle(color)
            .clipShape(Capsule())
            .overlay(Capsule().stroke(color.opacity(0.3), lineWidth: 1))
    }
}

// MARK: - Morning Brief Card

struct MorningBriefCard: View {
    let data: MorningBriefData

    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 10) {
                // Greeting
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(data.greeting)
                            .font(.title3.bold())
                        Text("Here's your cosmic snapshot")
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    Spacer()
                    Text("⚡")
                        .font(.largeTitle)
                }

                Divider()

                // Bullets
                ForEach(data.bullets, id: \.text) { bullet in
                    HStack(alignment: .top, spacing: 12) {
                        Text(bullet.emoji)
                            .font(.title3)
                        Text(bullet.text)
                            .font(.callout)
                            .foregroundStyle(Color.textPrimary)
                            .fixedSize(horizontal: false, vertical: true)
                        Spacer(minLength: 0)
                    }
                }
            }
        }
    }
}
