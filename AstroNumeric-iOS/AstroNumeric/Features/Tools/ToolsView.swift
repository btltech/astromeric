// ToolsView.swift
// Cosmic Tools hub - Tarot, Oracle, Affirmation

import SwiftUI

struct ToolsView: View {
    @Environment(AppStore.self) private var store
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    private var toolColumns: [GridItem] {
        if dynamicTypeSize.isAccessibilitySize {
            return [GridItem(.flexible())]
        }
        if horizontalSizeClass == .regular {
            return Array(repeating: GridItem(.flexible(), spacing: 16), count: 3)
        }
        return [GridItem(.flexible()), GridItem(.flexible())]
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Space.lg) {
                        PremiumScreenHeader(
                            eyebrow: "hero.tools.eyebrow".localized,
                            title: "hero.tools.title".localized,
                            subtitle: "hero.tools.body".localized,
                            accent: .accentPrimary,
                            chips: ["hero.tools.chip.0".localized, "hero.tools.chip.1".localized, "hero.tools.chip.2".localized]
                        )
                        .padding(.horizontal)

                        // SECTION: Daily Tools
                        toolSection(
                            title: "Daily Tools",
                            subtitle: "Symbolic & mood-based guidance",
                            badge: "Interpretive"
                        ) {
                            ToolCard(
                                title: "Tarot",
                                icon: "suit.spade.fill",
                                color: .cosmicPurple,
                                description: "Card pull for symbolic reflection.",
                                provenance: .interpretive
                            ) { TarotView() }

                            ToolCard(
                                title: "Oracle",
                                icon: "questionmark.circle.fill",
                                color: .cosmicBlue,
                                description: "Yes/no guidance using your day number and moon phase.",
                                provenance: .hybrid
                            ) { OracleView() }

                            ToolCard(
                                title: "Affirmation",
                                icon: "star.fill",
                                color: .orange,
                                description: "Supportive language tuned to today's mood.",
                                provenance: .interpretive
                            ) { AffirmationView() }

                            ToolCard(
                                title: "Moon Phase",
                                icon: "moon.fill",
                                color: .indigo,
                                description: "Current lunar phase, sign, and ritual timing.",
                                provenance: .calculated
                            ) { MoonPhaseView() }
                        }

                        // SECTION: Timing & Planning
                        toolSection(
                            title: "Timing & Planning",
                            subtitle: "Live sky scored for activity windows",
                            badge: "Calculated"
                        ) {
                            ToolCard(
                                title: "Timing Advisor",
                                icon: "clock.badge.checkmark",
                                color: .green,
                                description: "Activity windows scored from the live sky.",
                                provenance: .calculated
                            ) { TimingAdvisorView() }

                            ToolCard(
                                title: "Temporal Matrix",
                                icon: "calendar.badge.clock",
                                color: .teal,
                                description: "48-hour transit weather for planning and pacing.",
                                provenance: .calculated
                            ) { TemporalMatrixView() }

                            ToolCard(
                                title: "Daily Guide",
                                icon: "sparkles",
                                color: .yellow,
                                description: "Personal day, moon phases, retrogrades, and cues.",
                                provenance: .calculated
                            ) { DailyFeaturesView() }

                            ToolCard(
                                title: "Moon Events",
                                icon: "moonrise.fill",
                                color: .purple,
                                description: "Upcoming new and full moons with themes.",
                                provenance: .calculated
                            ) { MoonEventsView() }
                        }

                        // SECTION: Core Charts
                        toolSection(
                            title: "Core Charts",
                            subtitle: "Your natal chart and numerology",
                            badge: "Calculated"
                        ) {
                            ToolCard(
                                title: "Birth Chart",
                                icon: "circle.grid.3x3",
                                color: .cyan,
                                description: "Planetary placements from your birth data.",
                                provenance: .calculated
                            ) { ChartView() }

                            ToolCard(
                                title: "Numerology",
                                icon: "number",
                                color: .cosmicPink,
                                description: "Life path, expression, and personal year numbers.",
                                provenance: .calculated
                            ) { NumerologyView() }
                        }

                        // SECTION: Relationships
                        toolSection(
                            title: "Relationships",
                            subtitle: "Synastry and compatibility between two profiles",
                            badge: ""
                        ) {
                            ToolCard(
                                title: "Compatibility",
                                icon: "heart.fill",
                                color: .cosmicPink,
                                description: "Synastry and numerology between two profiles.",
                                provenance: .calculated
                            ) { CompatibilityView() }
                        }

                        // SECTION: Reference
                        toolSection(
                            title: "Reference",
                            subtitle: "Lookup guides and learning resources",
                            badge: "Reference"
                        ) {
                            ToolCard(
                                title: "Birthstones",
                                icon: "sparkle",
                                color: .mint,
                                description: "Gemstone guide matched to sign and month traditions.",
                                provenance: .reference
                            ) { BirthstoneGuidanceView() }
                        }
                    }
                    .padding(.vertical)
                    .readableContainer()
                }
            }
            .navigationTitle("screen.cosmicTools".localized)
            .navigationBarTitleDisplayMode(.inline)
        }
    }

    @ViewBuilder
    private func toolSection<Content: View>(
        title: String,
        subtitle: String,
        badge: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        VStack(alignment: .leading, spacing: Space.sm) {
            ToolSectionHeader(title: title, subtitle: subtitle, badge: badge)
                .padding(.horizontal)

            LazyVGrid(columns: toolColumns, spacing: Space.sm) {
                content()
            }
            .padding(.horizontal)
        }
    }
}

// MARK: - Tool Card

struct ToolCard<Destination: View>: View {
    let title: String
    let icon: String
    let color: Color
    let description: String
    let provenance: FeatureProvenance
    @ViewBuilder let destination: () -> Destination
    
    var body: some View {
        NavigationLink {
            destination()
        } label: {
            VStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 18)
                        .fill(color.opacity(0.18))
                        .frame(width: 64, height: 64)
                        .overlay(
                            RoundedRectangle(cornerRadius: 18)
                                .stroke(color.opacity(0.28), lineWidth: 1)
                        )
                    
                    Image(systemName: icon)
                        .font(.title)
                        .foregroundStyle(color)
                }
                
                Text(title)
                    .font(.headline)
                    .foregroundStyle(.primary)
                    .multilineTextAlignment(.center)

                FeatureProvenanceBadge(provenance: provenance, compact: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .lineLimit(3)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: Radius.md)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: Radius.md)
                            .stroke(Color.white.opacity(0.08), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityElement(children: .combine)
        .accessibilityLabel(title)
        .accessibilityHint("\(description) \(provenance.description)")
    }
}

// MARK: - Preview

#Preview {
    ToolsView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
