// EmbeddedChartView.swift
// Embeddable chart view for use within ChartsView tabs

import SwiftUI

/// A chart view designed to be embedded within another view (no NavigationStack)
struct EmbeddedChartView: View {
    @Environment(AppStore.self) private var store
    @State private var viewModel = ChartVM()
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                if viewModel.isLoading {
                    loadingView
                } else if let error = viewModel.error {
                    errorView(error)
                } else if viewModel.hasData {
                    chartContent
                } else {
                    emptyView
                }
            }
            .padding()
            .readableContainer()
        }
        .task(id: store.activeProfile?.id) {
            if let profile = store.activeProfile {
                await viewModel.fetchChart(for: profile)
            }
        }
        .refreshable {
            if let profile = store.activeProfile {
                await viewModel.fetchChart(for: profile)
            }
        }
    }
    
    // MARK: - Chart Content
    
    private var chartContent: some View {
        VStack(spacing: 20) {
            // Profile info card
            if let profile = store.activeProfile {
                ChartsProfileInfoCard(profile: profile)
            }

            PremiumSectionHeader(
                title: "section.embeddedChart.0.title".localized,
                subtitle: "section.embeddedChart.0.subtitle".localized
            )
            
            // Big Three Card
            bigThreeCard
            
            // Planet Placements
            placementsSection
            
            // Aspects (if any)
            if !viewModel.aspects.isEmpty {
                aspectsSection
            }
            
            // Houses (if any)
            if !viewModel.houses.isEmpty {
                housesSection
            }
        }
    }
    
    // MARK: - Big Three
    
    private var bigThreeCard: some View {
        CardView {
            VStack(spacing: 16) {
                PremiumSectionHeader(
                title: "charts.yourBigThree".localized,
                subtitle: "section.embeddedChart.1.subtitle".localized
            )
                
                HStack(spacing: 0) {
                    ForEach(viewModel.bigThree) { item in
                        VStack(spacing: 8) {
                            Text(item.emoji)
                                .font(.largeTitle)
                            
                            Text(item.name)
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                            
                            Text(item.sign)
                                .font(.subheadline.bold())
                                .foregroundStyle(.purple)
                        }
                        .frame(maxWidth: .infinity)
                    }
                }
            }
        }
    }
    
    // MARK: - Placements
    
    private var placementsSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                PremiumSectionHeader(
                title: "charts.planetPositions".localized,
                subtitle: "section.embeddedChart.2.subtitle".localized
            )
                
                ForEach(viewModel.placements) { planet in
                    HStack {
                        Text(planetEmoji(planet.name))
                            .font(.title3)
                        
                        Text(planet.name)
                            .font(.subheadline)
                        
                        Spacer()
                        
                        VStack(alignment: .trailing) {
                            Text(planet.sign)
                                .font(.subheadline.bold())
                                .foregroundStyle(.purple)
                            
                            if let house = planet.house {
                                Text(String(format: "fmt.embeddedChart.0".localized, "\(house)"))
                                    .font(.label)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                        
                        if planet.retrograde ?? false {
                            Text("℞")
                                .font(.caption.bold())
                                .foregroundStyle(.orange)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(
                                    Capsule()
                                        .fill(Color.orange.opacity(0.2))
                                )
                        }
                    }
                    
                    if planet.id != viewModel.placements.last?.id {
                        Divider()
                    }
                }
            }
        }
    }
    
    // MARK: - Aspects
    
    private var aspectsSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                PremiumSectionHeader(
                title: "charts.keyAspects".localized,
                subtitle: "section.embeddedChart.3.subtitle".localized
            )
                
                ForEach(Array(viewModel.aspects.prefix(8)), id: \.self) { aspect in
                    HStack {
                        Text(aspectSymbol(aspect.aspectType))
                            .font(.title3)
                            .foregroundStyle(aspectColor(aspect.aspectType))
                        
                        Text("\(aspect.planet1)")
                            .font(.subheadline.weight(.medium))
                        
                        Text(aspect.aspectType)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                        
                        Text("\(aspect.planet2)")
                            .font(.subheadline.weight(.medium))
                        
                        Spacer()
                        
                        if let orb = aspect.orb {
                            Text(String(format: "%.1f°", orb))
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    
                    if aspect != viewModel.aspects.prefix(8).last {
                        Divider()
                    }
                }
            }
        }
    }
    
    // MARK: - Houses
    
    private var housesSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                PremiumSectionHeader(
                title: "section.embeddedChart.4.title".localized,
                subtitle: "section.embeddedChart.4.subtitle".localized
            )
                
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 12) {
                    ForEach(viewModel.houses) { house in
                        VStack(spacing: 4) {
                            Text("\(house.house)")
                                .font(.caption2.bold())
                                .foregroundStyle(.white)
                                .frame(width: 24, height: 24)
                                .background(Circle().fill(Color.purple))
                            
                            Text(house.sign)
                                .font(.caption.bold())
                            
                            if let degree = house.degree {
                                Text(String(format: "%.0f°", degree))
                                    .font(.meta)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 8)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(.ultraThinMaterial)
                        )
                    }
                }
            }
        }
    }
    
    // MARK: - States
    
    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)
            Text("common.consultingStars".localized)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
        }
        .frame(maxWidth: .infinity, minHeight: 300)
    }
    
    private func errorView(_ message: String) -> some View {
        CardView {
            VStack(spacing: 12) {
                Image(systemName: "exclamationmark.triangle")
                    .font(.largeTitle)
                    .foregroundStyle(.orange)
                
                Text("error.loadingChart".localized)
                    .font(.headline)
                
                Text(message)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)
                
                Button("common.retry".localized) {
                    Task {
                        if let profile = store.activeProfile {
                            await viewModel.fetchChart(for: profile)
                        }
                    }
                }
                .buttonStyle(.bordered)
            }
        }
    }
    
    private var emptyView: some View {
        ChartsNoProfileCard(
            title: "charts.createChart".localized,
            subtitle: "charts.addDetailsForChart".localized,
            icon: "sun.and.horizon.fill"
        )
    }
    
    // MARK: - Helpers
    
    private func planetEmoji(_ name: String) -> String {
        switch name.lowercased() {
        case "sun": return "☀️"
        case "moon": return "🌙"
        case "mercury": return "☿️"
        case "venus": return "♀️"
        case "mars": return "♂️"
        case "jupiter": return "♃"
        case "saturn": return "♄"
        case "uranus": return "⛢"
        case "neptune": return "♆"
        case "pluto": return "♇"
        case "north node", "northnode": return "☊"
        case "south node", "southnode": return "☋"
        case "chiron": return "⚷"
        case "ascendant", "rising": return "↑"
        case "midheaven", "mc": return "MC"
        default: return "⭐"
        }
    }
    
    private func aspectSymbol(_ type: String) -> String {
        switch type.lowercased() {
        case "conjunction": return "☌"
        case "opposition": return "☍"
        case "trine": return "△"
        case "square": return "□"
        case "sextile": return "⚹"
        case "quincunx", "inconjunct": return "⚻"
        default: return "●"
        }
    }
    
    private func aspectColor(_ type: String) -> Color {
        switch type.lowercased() {
        case "conjunction": return .yellow
        case "opposition": return .red
        case "trine": return .green
        case "square": return .orange
        case "sextile": return .blue
        default: return .secondary
        }
    }
}

// MARK: - Preview

#Preview {
    EmbeddedChartView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
