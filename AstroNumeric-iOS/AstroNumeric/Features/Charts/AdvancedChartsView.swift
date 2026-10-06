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

                // SECTION: More techniques
                ToolSectionHeader(
                    title: "More techniques",
                    subtitle: "Directions, returns, yearly timing and the finer points of your chart",
                    badge: "Calculated"
                )

                VStack(spacing: Space.sm) {
                    advancedLink("Solar Arc", "Every planet moved forward by your solar arc", "arrow.triangle.swap", [.orange, .cosmicPurple]) { SolarArcView() }
                    advancedLink("Lunar Return", "The chart for the Moon's monthly return", "moon.circle.fill", [.cosmicBlue, .cosmicPurple]) { LunarReturnView() }
                    advancedLink("Profections", "This year's house and its Time Lord", "calendar.circle.fill", [.teal, .cosmicPurple]) { ProfectionsView() }
                    advancedLink("Relocation", "Your birth chart cast for another city", "mappin.circle.fill", [.cosmicPink, .orange]) { RelocationChartView() }
                    advancedLink("Declinations", "Parallels and out-of-bounds planets", "line.3.horizontal.decrease.circle.fill", [.cosmicBlue, .teal]) { DeclinationsView() }
                    advancedLink("Fixed Stars", "Bright stars within a degree of your planets", "star.circle.fill", [.cosmicPurple, .cosmicPink]) { FixedStarsView() }
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
        // Match the other pushed pages: a title and the app background.
        .background(Color.appBackground.ignoresSafeArea())
        .navigationTitle("section.charts.advanced.title".localized)
        .navigationBarTitleDisplayMode(.inline)
    }

    private func advancedLink<Destination: View>(
        _ title: String,
        _ subtitle: String,
        _ icon: String,
        _ gradient: [Color],
        @ViewBuilder destination: () -> Destination
    ) -> some View {
        NavigationLink {
            destination()
        } label: {
            ChartsActionCard(title: title, subtitle: subtitle, icon: icon, gradient: gradient)
        }
        .buttonStyle(ScaleButtonStyle())
        .accessibilityLabel(title)
    }
}

#Preview {
    NavigationStack {
        AdvancedChartsView()
    }
    .preferredColorScheme(.dark)
}
