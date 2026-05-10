// AdvancedChartsView.swift
// Advanced charting entry points

import SwiftUI

struct AdvancedChartsView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Space.lg) {
                PremiumScreenHeader(
                    eyebrow: "hero.advancedCharts.eyebrow".localized,
                    title: "hero.advancedCharts.title".localized,
                    subtitle: "hero.advancedCharts.body".localized,
                    accent: .accentPrimary,
                    chips: ["hero.advancedCharts.chip.0".localized, "hero.advancedCharts.chip.1".localized, "hero.advancedCharts.chip.2".localized, "hero.advancedCharts.chip.3".localized]
                )

                // SECTION: Timing
                ToolSectionHeader(
                    title: "Timing",
                    subtitle: "Solar return and long-range progressions",
                    badge: "Calculated"
                )

                VStack(spacing: Space.sm) {
                    NavigationLink {
                        YearAheadView()
                    } label: {
                        ChartsActionCard(
                            title: "Solar Return + Year Ahead",
                            subtitle: "Your personal year, eclipses, and monthly themes",
                            icon: "sparkles",
                            gradient: [.cosmicPurple, .cosmicBlue]
                        )
                    }
                    .buttonStyle(ScaleButtonStyle())
                    .accessibilityLabel("Solar Return and Year Ahead")

                    NavigationLink {
                        ProgressionsView()
                    } label: {
                        ChartsActionCard(
                            title: "Progressions",
                            subtitle: "Secondary progressed chart — inner growth over time",
                            icon: "timer",
                            gradient: [.teal, .cosmicBlue]
                        )
                    }
                    .buttonStyle(ScaleButtonStyle())
                    .accessibilityLabel("Progressions")
                }

                // SECTION: Relationships
                ToolSectionHeader(
                    title: "Relationships",
                    subtitle: "Synastry and composite charts for any two people",
                    badge: "Calculated"
                )

                VStack(spacing: Space.sm) {
                    NavigationLink {
                        SynastryChartView()
                    } label: {
                        ChartsActionCard(
                            title: "Synastry",
                            subtitle: "Aspect-level relationship insights between two charts",
                            icon: "heart.circle.fill",
                            gradient: [.cosmicPink, .cosmicPurple]
                        )
                    }
                    .buttonStyle(ScaleButtonStyle())
                    .accessibilityLabel("Synastry")

                    NavigationLink {
                        CompositeChartView()
                    } label: {
                        ChartsActionCard(
                            title: "Composite Chart",
                            subtitle: "The relationship's own chart — midpoints combined",
                            icon: "person.2.circle.fill",
                            gradient: [.orange, .cosmicPink]
                        )
                    }
                    .buttonStyle(ScaleButtonStyle())
                    .accessibilityLabel("Composite Chart")
                }
            }
            .padding()
            .readableContainer()
        }
    }
}

#Preview {
    NavigationStack {
        AdvancedChartsView()
    }
    .preferredColorScheme(.dark)
}
