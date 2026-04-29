// AdvancedChartsView.swift
// Advanced charting entry points

import SwiftUI

struct AdvancedChartsView: View {
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                PremiumHeroCard(
                            eyebrow: "hero.advancedCharts.eyebrow".localized,
                            title: "hero.advancedCharts.title".localized,
                            bodyText: "hero.advancedCharts.body".localized,
                            accent: [Color(hex: "171a38"), Color(hex: "3e58be"), Color(hex: "8b4bb5")],
                            chips: ["hero.advancedCharts.chip.0".localized, "hero.advancedCharts.chip.1".localized, "hero.advancedCharts.chip.2".localized, "hero.advancedCharts.chip.3".localized]
                        )

                PremiumSectionHeader(
                title: "section.advancedCharts.0.title".localized,
                subtitle: "section.advancedCharts.0.subtitle".localized
            )

                NavigationLink {
                    YearAheadView()
                } label: {
                    ChartsActionCard(
                        title: "Solar Return + Year Ahead",
                        subtitle: "Your personal year, eclipses, and monthly themes",
                        icon: "sparkles",
                        gradient: [.purple, .blue]
                    )
                }
                .buttonStyle(.plain)

                NavigationLink {
                    ProgressionsView()
                } label: {
                    ChartsActionCard(
                        title: "Progressions",
                        subtitle: "Secondary progressed chart",
                        icon: "timer",
                        gradient: [.teal, .blue]
                    )
                }
                .buttonStyle(.plain)
                
                NavigationLink {
                    SynastryChartView()
                } label: {
                    ChartsActionCard(
                        title: "Synastry",
                        subtitle: "Aspect-level relationship insights",
                        icon: "heart.circle.fill",
                        gradient: [.pink, .purple]
                    )
                }
                .buttonStyle(.plain)

                NavigationLink {
                    CompositeChartView()
                } label: {
                    ChartsActionCard(
                        title: "Composite Chart",
                        subtitle: "Combined relationship chart",
                        icon: "sparkles",
                        gradient: [.orange, .pink]
                    )
                }
                .buttonStyle(.plain)
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
