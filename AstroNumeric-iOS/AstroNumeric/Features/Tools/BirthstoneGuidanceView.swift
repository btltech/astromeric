// BirthstoneGuidanceView.swift
// Personalized birthstone guidance based on the user's zodiac sign.

import SwiftUI

struct BirthstoneGuidanceView: View {
    @Environment(AppStore.self) private var store

    private var zodiacSign: ZodiacSign? {
        guard let dob = store.activeProfile?.dateOfBirth else { return nil }
        return ZodiacSign.from(dateOfBirth: dob)
    }

    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()

            ScrollView {
                VStack(spacing: 20) {
                    if let sign = zodiacSign {
                        PremiumHeroCard(
                            eyebrow: "hero.birthstoneGuidance.eyebrow".localized,
                            title: "hero.birthstoneGuidance.title".localized,
                            bodyText: "hero.birthstoneGuidance.body".localized,
                            accent: [Color(hex: "1f1738"), Color(hex: "8e45af"), Color(hex: "1d9aa0")],
                            chips: ["hero.birthstoneGuidance.chip.0".localized, "hero.birthstoneGuidance.chip.1".localized, "hero.birthstoneGuidance.chip.2".localized]
                        )

                        headerCard(sign)

                        PremiumSectionHeader(
                title: "section.birthstoneGuidance.0.title".localized,
                subtitle: "section.birthstoneGuidance.0.subtitle".localized
            )

                        ForEach(Array(sign.birthstones.enumerated()), id: \.offset) { index, stone in
                            birthstoneCard(stone, index: index)
                        }

                        usageTipBanner
                    } else {
                        PremiumHeroCard(
                            eyebrow: "hero.birthstoneGuidance2.eyebrow".localized,
                            title: "hero.birthstoneGuidance2.title".localized,
                            bodyText: "hero.birthstoneGuidance2.body".localized,
                            accent: [Color(hex: "1f1738"), Color(hex: "8e45af"), Color(hex: "1d9aa0")],
                            chips: []
                        )

                        noProfileCard
                    }
                }
                .padding()
                .readableContainer()
            }
        }
        .navigationTitle("screen.birthstone".localized)
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Header

    private func headerCard(_ sign: ZodiacSign) -> some View {
        CardView {
            VStack(spacing: 14) {
                Text(sign.emoji)
                    .font(.system(.largeTitle))

                VStack(spacing: 4) {
                    Text(String(format: "fmt.birthstoneGuidance.1".localized, "\(sign.displayName)"))
                        .font(.title2.bold())
                        .multilineTextAlignment(.center)

                    HStack(spacing: 16) {
                        Label(sign.element, systemImage: "")
                            .font(.caption.weight(.medium))
                            .foregroundStyle(elementColor(sign.element))

                        Text("•")
                            .foregroundStyle(Color.textMuted)

                        Text(sign.modality)
                            .font(.caption.weight(.medium))
                            .foregroundStyle(Color.textSecondary)
                    }
                }

                Text("ui.birthstoneGuidance.0".localized)
                    .font(.subtext)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)
                    .lineSpacing(4)
            }
            .padding(.vertical, 4)
        }
    }

    // MARK: - Birthstone Card

    private func birthstoneCard(_ stone: BirthstoneInfo, index: Int) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 14) {
                // Title row
                HStack(alignment: .center, spacing: 12) {
                    ZStack {
                        Circle()
                            .fill(stoneColor(index).opacity(0.18))
                            .frame(width: 52, height: 52)
                        Text(stone.emoji)
                            .font(.system(.title))
                    }

                    VStack(alignment: .leading, spacing: 2) {
                        Text(stone.name)
                            .font(.headline)
                        Text(String(format: "fmt.birthstoneGuidance.0".localized, "\(index + 1)"))
                            .font(.caption)
                            .foregroundStyle(Color.textMuted)
                    }

                    Spacer()
                }

                // Meaning
                VStack(alignment: .leading, spacing: 6) {
                    Label("ui.birthstoneGuidance.5".localized, systemImage: "sparkles")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(stoneColor(index))

                    Text(stone.meaning)
                        .font(.subtext)
                        .foregroundStyle(.primary)
                        .lineSpacing(3)
                }

                Divider()
                    .background(Color.borderSubtle)

                // How to use
                VStack(alignment: .leading, spacing: 6) {
                    Label("ui.birthstoneGuidance.6".localized, systemImage: "hand.raised.fill")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color.textSecondary)

                    Text(stone.howToUse)
                        .font(.subtext)
                        .foregroundStyle(Color.textSecondary)
                        .lineSpacing(3)
                }
            }
        }
    }

    // MARK: - Usage Tip Banner

    private var usageTipBanner: some View {
        HStack(spacing: 12) {
            Text("💡")
                .font(.title2)

            VStack(alignment: .leading, spacing: 4) {
                Text("ui.birthstoneGuidance.1".localized)
                    .font(.caption.weight(.bold))
                Text("ui.birthstoneGuidance.2".localized)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .lineSpacing(2)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.purple.opacity(0.08))
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .strokeBorder(Color.purple.opacity(0.2), lineWidth: 1)
                )
        )
    }

    // MARK: - No Profile

    private var noProfileCard: some View {
        CardView {
            VStack(spacing: 16) {
                Text("💎")
                    .font(.system(.largeTitle))

                VStack(spacing: 8) {
                    Text("ui.birthstoneGuidance.3".localized)
                        .font(.headline)
                    Text("ui.birthstoneGuidance.4".localized)
                        .font(.subtext)
                        .foregroundStyle(Color.textSecondary)
                        .multilineTextAlignment(.center)
                        .lineSpacing(3)
                }
            }
            .padding(.vertical, 8)
        }
    }

    // MARK: - Helpers

    private func elementColor(_ element: String) -> Color {
        if element.contains("Fire") { return .orange }
        if element.contains("Earth") { return .green }
        if element.contains("Air") { return .cyan }
        if element.contains("Water") { return .blue }
        return .purple
    }

    private func stoneColor(_ index: Int) -> Color {
        let colors: [Color] = [.purple, .pink, .teal]
        return colors[index % colors.count]
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        BirthstoneGuidanceView()
            .environment(AppStore.shared)
    }
    .preferredColorScheme(.dark)
}
