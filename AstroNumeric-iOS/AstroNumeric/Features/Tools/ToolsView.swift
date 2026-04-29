// ToolsView.swift
// Cosmic Tools hub - Tarot, Oracle, Affirmation

import SwiftUI

struct ToolsView: View {
    @Environment(AppStore.self) private var store
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    private var toolColumns: [GridItem] {
        if dynamicTypeSize.isAccessibilitySize {
            return [GridItem(.flexible())]
        }
        return [GridItem(.flexible()), GridItem(.flexible())]
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        PremiumHeroCard(
                            eyebrow: "hero.tools.eyebrow".localized,
                            title: "hero.tools.title".localized,
                            bodyText: "hero.tools.body".localized,
                            accent: [Color(hex: "25103f"), Color(hex: "5531a7"), Color(hex: "0f6a7d")],
                            chips: ["hero.tools.chip.0".localized, "hero.tools.chip.1".localized, "hero.tools.chip.2".localized]
                        )
                        .padding(.horizontal)

                        PremiumSectionHeader(
                title: "section.tools.0.title".localized,
                subtitle: "section.tools.0.subtitle".localized
            )
                        .padding(.horizontal)

                        CardView {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("ui.tools.0".localized)
                                    .font(.headline)

                                Text("ui.tools.1".localized)
                                    .font(.subheadline)
                                    .foregroundStyle(Color.textSecondary)

                                HStack(spacing: 8) {
                                    FeatureProvenanceBadge(provenance: .calculated, compact: true)
                                    FeatureProvenanceBadge(provenance: .hybrid, compact: true)
                                    FeatureProvenanceBadge(provenance: .interpretive, compact: true)
                                    FeatureProvenanceBadge(provenance: .reference, compact: true)
                                }
                            }
                        }
                        .padding(.horizontal)

                        PremiumSectionHeader(
                title: "section.tools.1.title".localized,
                subtitle: "section.tools.1.subtitle".localized
            )
                        .padding(.horizontal)

                        // Tool Cards
                        LazyVGrid(columns: toolColumns, spacing: 16) {
                            ToolCard(
                                title: "Tarot",
                                icon: "suit.spade.fill",
                                color: .purple,
                                description: "Card pull for symbolic reflection.",
                                provenance: .interpretive
                            ) {
                                TarotView()
                            }
                            
                            ToolCard(
                                title: "Oracle",
                                icon: "questionmark.circle.fill",
                                color: .blue,
                                description: "Yes/no guidance using your day number and moon phase.",
                                provenance: .hybrid
                            ) {
                                OracleView()
                            }
                            
                            ToolCard(
                                title: "Affirmation",
                                icon: "star.fill",
                                color: .orange,
                                description: "Supportive language tuned to today's mood.",
                                provenance: .interpretive
                            ) {
                                AffirmationView()
                            }
                            
                            ToolCard(
                                title: "Moon Phase",
                                icon: "moon.fill",
                                color: .indigo,
                                description: "Current lunar phase, sign, and ritual timing.",
                                provenance: .calculated
                            ) {
                                MoonPhaseView()
                            }
                            
                            ToolCard(
                                title: "Birth Chart",
                                icon: "circle.grid.3x3",
                                color: .teal,
                                description: "Planetary placements from your birth data.",
                                provenance: .calculated
                            ) {
                                ChartView()
                            }
                            
                            ToolCard(
                                title: "Compatibility",
                                icon: "heart.fill",
                                color: .pink,
                                description: "Synastry and numerology between two profiles.",
                                provenance: .calculated
                            ) {
                                CompatibilityView()
                            }
                            
                            ToolCard(
                                title: "Daily Guide",
                                icon: "sparkles",
                                color: .yellow,
                                description: "Personal day, moon phase, retrogrades, and cues.",
                                provenance: .calculated
                            ) {
                                DailyFeaturesView()
                            }
                            
                            ToolCard(
                                title: "Timing",
                                icon: "clock.badge.checkmark",
                                color: .green,
                                description: "Activity windows scored from the live sky.",
                                provenance: .calculated
                            ) {
                                TimingAdvisorView()
                            }
                            
                            ToolCard(
                                title: "Temporal Matrix",
                                icon: "calendar.badge.clock",
                                color: .cyan,
                                description: "48-hour transit weather for planning and pacing.",
                                provenance: .calculated
                            ) {
                                TemporalMatrixView()
                            }

                            ToolCard(
                                title: "Birthstones",
                                icon: "sparkle",
                                color: .mint,
                                description: "Gemstone guide matched to sign and month traditions.",
                                provenance: .reference
                            ) {
                                BirthstoneGuidanceView()
                            }
                        }
                        .padding(.horizontal)
                    }
                    .padding(.vertical)
                    .readableContainer()
                }
            }
            .navigationTitle("screen.cosmicTools".localized)
            .navigationBarTitleDisplayMode(.inline)
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
                RoundedRectangle(cornerRadius: 16)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.white.opacity(0.08), lineWidth: 1)
                    )
            )
        }
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
