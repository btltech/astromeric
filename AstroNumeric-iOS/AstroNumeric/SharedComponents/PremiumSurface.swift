import SwiftUI

// MARK: - Premium Hero Card
// Used for the single most-prominent hero on a screen (e.g. Home daily insight,
// Charts hub). Uses a consistent single-accent gradient so every screen looks
// unified. Callers pass ONE accent Color; the dark-to-accent gradient is
// computed automatically. No more per-screen arbitrary color arrays.

struct PremiumHeroCard: View {
    let eyebrow: String
    let title: String
    let bodyText: String
    /// Single accent color drives the gradient. Defaults to accentPrimary.
    var accent: Color = .accentPrimary
    var chips: [String] = []

    // Legacy convenience: callers that previously passed [Color] can migrate
    // over time. For now they can pass accent directly.

    var body: some View {
        // Gradient: deep cosmic dark → accent tinted midnight
        let base = Color(red: 0.07, green: 0.06, blue: 0.13)
        let mid  = accent.opacity(0.40)
        let tip  = accent.opacity(0.18)

        VStack(alignment: .leading, spacing: 10) {
            Text(eyebrow.uppercased())
                .font(.system(.caption2, design: .monospaced).weight(.bold))
                .tracking(1.6)
                .foregroundStyle(.white.opacity(0.60))

            VStack(alignment: .leading, spacing: 6) {
                Text(title)
                    .font(.system(.title3, design: .serif).weight(.semibold))
                    .foregroundStyle(.white)
                    .fixedSize(horizontal: false, vertical: true)

                Text(bodyText)
                    .font(.footnote)
                    .foregroundStyle(.white.opacity(0.75))
                    .fixedSize(horizontal: false, vertical: true)
            }

            if !chips.isEmpty {
                FlexibleChipRow(items: chips, tint: accent)
            }
        }
        .padding(.horizontal, Space.md)
        .padding(.vertical, 14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            ZStack {
                RoundedRectangle(cornerRadius: Radius.md)
                    .fill(
                        LinearGradient(
                            colors: [base, mid, tip],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                GrainOverlay()
                    .clipShape(RoundedRectangle(cornerRadius: Radius.md))
                RoundedRectangle(cornerRadius: Radius.md)
                    .stroke(accent.opacity(0.22), lineWidth: Stroke.hairline)
                PremiumTopHighlight(cornerRadius: Radius.md)
            }
            .compositingGroup()
        )
        .elevatedCardShadow()
    }
}

// MARK: - Premium Screen Header
// Lightweight alternative to PremiumHeroCard for screens where a full gradient
// background would add noise. Renders as clean text — no background surface.

struct PremiumScreenHeader: View {
    let eyebrow: String
    let title: String
    var subtitle: String = ""
    var badge: String = ""
    var accent: Color = .accentPrimary
    var chips: [String] = []
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    var body: some View {
        VStack(alignment: .leading, spacing: Space.sm) {
            if !eyebrow.isEmpty {
                Text(eyebrow.uppercased())
                    .font(.system(.caption2, design: .monospaced).weight(.bold))
                    .tracking(1.6)
                    .foregroundStyle(accent.opacity(0.85))
            }

            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Text(title)
                    .font(.system(.title2, design: .serif).weight(.bold))
                    .foregroundStyle(Color.textPrimary)
                    .fixedSize(horizontal: false, vertical: true)

                if !badge.isEmpty {
                    PremiumBadge(text: badge, tint: accent)
                }
            }

            if !subtitle.isEmpty {
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
                    .lineLimit(dynamicTypeSize.isAccessibilitySize ? nil : 3)
                    .fixedSize(horizontal: false, vertical: true)
            }

            if !chips.isEmpty {
                FlexibleChipRow(items: chips, tint: accent)
                    .padding(.top, Space.xs)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

// MARK: - Tool Section Header
// Used inside ToolsView / AdvancedChartsView to group items under a named section.

struct ToolSectionHeader: View {
    let title: String
    var subtitle: String = ""
    var badge: String = ""
    var accent: Color = .accentPrimary

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack(spacing: 6) {
                Text(title)
                    .font(.headline.weight(.semibold))
                    .foregroundStyle(Color.textPrimary)
                if !badge.isEmpty {
                    PremiumBadge(text: badge, tint: accent)
                }
            }
            if !subtitle.isEmpty {
                Text(subtitle)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

// MARK: - Premium Section Header (detail-level subheader inside a card)

struct PremiumSectionHeader: View {
    let title: String
    let subtitle: String
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.primary)
                .fixedSize(horizontal: false, vertical: true)
            Text(subtitle)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
                .lineLimit(dynamicTypeSize.isAccessibilitySize ? nil : 2)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

// MARK: - Flexible Chip Row

struct FlexibleChipRow: View {
    let items: [String]
    var tint: Color = .accentPrimary

    var body: some View {
        FlowLayout(spacing: 6) {
            ForEach(items, id: \.self) { item in
                Text(item)
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(tint.opacity(0.9))
                    .padding(.horizontal, 9)
                    .padding(.vertical, 5)
                    .background(
                        Capsule()
                            .fill(tint.opacity(0.14))
                    )
            }
        }
    }
}

// MARK: - Premium Action Card

/// A standard tappable action card used across features to drive a primary CTA.
/// Callers attach `.onTapGesture` or embed inside a `Button` as needed.
struct PremiumActionCard: View {
    let title: String
    let subtitle: String
    let icon: String
    var label: String = ""
    let accent: Color
    var emphasized: Bool = false
    var showsChevron: Bool = true

    var body: some View {
        HStack(spacing: Space.md) {
            Image(systemName: icon)
                .font(.system(.title3, weight: .semibold))
                .foregroundStyle(accent)
                .frame(width: 42, height: 42)
                .background(
                    RoundedRectangle(cornerRadius: Radius.sm)
                        .fill(accent.opacity(0.15))
                )

            VStack(alignment: .leading, spacing: 3) {
                HStack(spacing: 6) {
                    Text(title)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(Color.textPrimary)
                    if !label.isEmpty {
                        PremiumBadge(text: label, tint: accent)
                    }
                }
                Text(subtitle)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer()

            if showsChevron {
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color.textSecondary)
            }
        }
        .padding(emphasized ? Space.md : 14)
        .background(
            RoundedRectangle(cornerRadius: Radius.md)
                .fill(emphasized ? accent.opacity(0.10) : Color.cardBackground)
                .overlay(
                    RoundedRectangle(cornerRadius: Radius.md)
                        .stroke(
                            emphasized ? accent.opacity(0.30) : Color.borderSubtle,
                            lineWidth: emphasized ? Stroke.emphasized : Stroke.hairline
                        )
                )
        )
    }
}

// MARK: - Premium Badge

/// A small capsule badge — "Start Here", "Recommended", "Advanced", etc.
struct PremiumBadge: View {
    let text: String
    var tint: Color = .accentPrimary

    var body: some View {
        Text(text.uppercased())
            .font(.system(.caption2, design: .monospaced).weight(.bold))
            .tracking(0.8)
            .foregroundStyle(tint)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Capsule().fill(tint.opacity(0.14)))
    }
}

// MARK: - Premium Filter Chip

/// A segmented-filter capsule chip. Embed inside a `Button` to handle taps.
struct PremiumFilterChip: View {
    let title: String
    var isSelected: Bool = false

    var body: some View {
        Text(title)
            .font(.caption.weight(.semibold))
            .foregroundStyle(isSelected ? Color.accentPrimary : Color.textSecondary)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(
                Capsule()
                    .fill(isSelected ? Color.accentPrimary.opacity(0.15) : Color.surfaceBase)
                    .overlay(
                        Capsule()
                            .stroke(
                                isSelected ? Color.accentPrimary.opacity(0.40) : Color.borderSubtle,
                                lineWidth: Stroke.hairline
                            )
                    )
            )
            .animation(.spring(response: 0.25, dampingFraction: 0.75), value: isSelected)
    }
}