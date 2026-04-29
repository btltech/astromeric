// CardView.swift
// Glass morphism card component

import SwiftUI

enum FeatureProvenance: String {
    case calculated
    case hybrid
    case interpretive
    case reference

    var label: String {
        switch self {
        case .calculated: return "Calculated"
        case .hybrid: return "Hybrid"
        case .interpretive: return "Interpretive"
        case .reference: return "Reference"
        }
    }

    var description: String {
        switch self {
        case .calculated:
            return "Driven directly by astrology or numerology calculations."
        case .hybrid:
            return "Blends calculated signals with interpretive guidance."
        case .interpretive:
            return "Reflective guidance rather than a direct chart calculation."
        case .reference:
            return "Static guidance based on established correspondences."
        }
    }

    var accent: Color {
        switch self {
        case .calculated: return .green
        case .hybrid: return .blue
        case .interpretive: return .orange
        case .reference: return .mint
        }
    }
}

struct FeatureProvenanceBadge: View {
    let provenance: FeatureProvenance
    var compact: Bool = false

    var body: some View {
        Text(provenance.label)
            .font(compact ? .caption2.weight(.semibold) : .caption.weight(.semibold))
            .foregroundStyle(provenance.accent)
            .padding(.horizontal, compact ? 8 : 10)
            .padding(.vertical, compact ? 4 : 6)
            .background(provenance.accent.opacity(0.16))
            .clipShape(Capsule())
            .accessibilityLabel("\(provenance.label) feature")
            .accessibilityHint(provenance.description)
    }
}

struct CardView<Content: View>: View {
    let content: Content
    var padding: CGFloat = 18
    var cornerRadius: CGFloat = Radius.md
    var material: Material = .ultraThinMaterial
    var backgroundColor: Color = .cardBackground
    var borderColor: Color = .borderSubtle
    var withShadow: Bool = true

    init(
        padding: CGFloat = 18,
        cornerRadius: CGFloat = Radius.md,
        material: Material = .ultraThinMaterial,
        backgroundColor: Color = .cardBackground,
        borderColor: Color = .borderSubtle,
        withShadow: Bool = true,
        @ViewBuilder content: () -> Content
    ) {
        self.padding = padding
        self.cornerRadius = cornerRadius
        self.material = material
        self.backgroundColor = backgroundColor
        self.borderColor = borderColor
        self.withShadow = withShadow
        self.content = content()
    }

    var body: some View {
        content
            .padding(padding)
            .background(
                ZStack {
                    RoundedRectangle(cornerRadius: cornerRadius)
                        .fill(backgroundColor)
                    RoundedRectangle(cornerRadius: cornerRadius)
                        .fill(material)
                        .opacity(0.5)
                }
            )
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius)
                    .stroke(borderColor, lineWidth: Stroke.hairline)
            )
            .overlay(PremiumTopHighlight(cornerRadius: cornerRadius))
            .compositingGroup()
            .modifier(ConditionalCardShadow(enabled: withShadow))
            .contentShape(RoundedRectangle(cornerRadius: cornerRadius))
            .hoverEffect(.lift) // iPad pointer / Magic Keyboard polish; no-op on touch
    }
}

private struct ConditionalCardShadow: ViewModifier {
    let enabled: Bool
    func body(content: Content) -> some View {
        if enabled {
            content.elevatedCardShadow()
        } else {
            content
        }
    }
}

// MARK: - Glow Card Variant

struct GlowCardView<Content: View>: View {
    let content: Content
    var glowColor: Color = .purple
    var glowRadius: CGFloat = 20
    var padding: CGFloat = 16
    var cornerRadius: CGFloat = 16
    var backgroundColor: Color = .cardBackground
    
    init(
        glowColor: Color = .purple,
        glowRadius: CGFloat = 20,
        padding: CGFloat = 16,
        cornerRadius: CGFloat = 16,
        backgroundColor: Color = .cardBackground,
        @ViewBuilder content: () -> Content
    ) {
        self.glowColor = glowColor
        self.glowRadius = glowRadius
        self.padding = padding
        self.cornerRadius = cornerRadius
        self.backgroundColor = backgroundColor
        self.content = content()
    }
    
    var body: some View {
        content
            .padding(padding)
            .background(
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(backgroundColor)
                    .overlay(
                        RoundedRectangle(cornerRadius: cornerRadius)
                            .fill(.ultraThinMaterial)
                            .opacity(0.6)
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius)
                    .strokeBorder(
                        glowColor.opacity(0.5),
                        lineWidth: 1
                    )
            )
            .shadow(color: glowColor.opacity(0.3), radius: glowRadius / 2)
    }
}

// MARK: - Section Card

struct SectionCard<Content: View>: View {
    let title: String
    let icon: String?
    let content: Content
    
    init(
        title: String,
        icon: String? = nil,
        @ViewBuilder content: () -> Content
    ) {
        self.title = title
        self.icon = icon
        self.content = content()
    }
    
    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 8) {
                    if let icon {
                        Text(icon)
                            .font(.title2)
                            .accessibilityHidden(true)
                    }
                    Text(title)
                        .font(.headline)
                        .accessibilityAddTraits(.isHeader)
                }
                
                content
            }
        }
        .accessibilityElement(children: .contain)
    }
}

// MARK: - Previews

#Preview("Card View") {
    VStack(spacing: 16) {
        CardView {
            VStack(alignment: .leading, spacing: 8) {
                Text("ui.card.0".localized)
                    .font(.headline)
                Text("ui.card.1".localized)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
            }
        }
        
        GlowCardView(glowColor: .purple) {
            VStack(spacing: 8) {
                Text("ui.card.2".localized)
                    .font(.label)
                    .foregroundStyle(Color.textSecondary)
                Text("7")
                    .font(.system(.largeTitle, design: .rounded)).fontWeight(.bold)
            }
        }
        
        SectionCard(title: "Love & Relationships", icon: "❤️") {
            Text("ui.card.3".localized)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
        }
    }
    .padding()
    .background(Color.black)
    .preferredColorScheme(.dark)
}
