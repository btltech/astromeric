import SwiftUI

struct PremiumHeroCard: View {
    let eyebrow: String
    let title: String
    let bodyText: String
    let accent: [Color]
    let chips: [String]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(eyebrow.uppercased())
                .font(.system(.caption2, design: .monospaced)).fontWeight(.bold)
                .tracking(1.6)
                .foregroundStyle(.white.opacity(0.65))

            VStack(alignment: .leading, spacing: 6) {
                Text(title)
                    .font(.system(.title3, design: .serif)).fontWeight(.semibold)
                    .foregroundStyle(.white)
                    .fixedSize(horizontal: false, vertical: true)

                Text(bodyText)
                    .font(.footnote)
                    .foregroundStyle(.white.opacity(0.78))
                    .fixedSize(horizontal: false, vertical: true)
            }

            if !chips.isEmpty {
                FlexibleChipRow(items: chips)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 18)
                .fill(
                    LinearGradient(
                        colors: accent,
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 18)
                        .stroke(Color.white.opacity(0.14), lineWidth: 1)
                )
        )
    }
}

struct PremiumSectionHeader: View {
    let title: String
    let subtitle: String

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.primary)
            Text(subtitle)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
                .lineLimit(2)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

struct FlexibleChipRow: View {
    let items: [String]

    var body: some View {
        FlowLayout(spacing: 6) {
            ForEach(items, id: \.self) { item in
                Text(item)
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(.white.opacity(0.9))
                    .padding(.horizontal, 9)
                    .padding(.vertical, 5)
                    .background(
                        Capsule()
                            .fill(.white.opacity(0.12))
                    )
            }
        }
    }
}