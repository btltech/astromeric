// ChartView.swift
// Natal Chart display with Big Three and placements

import SwiftUI

struct ChartView: View {
    @Environment(AppStore.self) private var store
    @State private var viewModel = ChartVM()
    @State private var isRevealing = true
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        if viewModel.isLoading {
                            loadingView
                        } else if let error = viewModel.error {
                            errorView(error)
                        } else if viewModel.hasData {
                            chartContent
                                .scaleReveal(isRevealing: isRevealing, fromScale: 0.85)
                                .onAppear {
                                    // Trigger reveal animation
                                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                                        isRevealing = false
                                        HapticManager.notification(.success)
                                    }
                                }
                        } else {
                            emptyView
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Birth Chart")
            .navigationBarTitleDisplayMode(.inline)
            .task(id: store.activeProfile?.id) {
                if let profile = store.activeProfile {
                    await viewModel.fetchChart(for: profile)
                }
            }
        }
    }
    
    // MARK: - Chart Content
    
    private var chartContent: some View {
        VStack(spacing: 20) {
            // Data quality banners
            if viewModel.isLocationMissing {
                DataQualityBanner(
                    icon: "location.slash",
                    message: "No birth location — showing Sun sign only. Add your birth place for a full chart.",
                    color: .orange
                )
            } else if viewModel.birthTimeAssumed {
                DataQualityBanner(
                    icon: "clock.badge.questionmark",
                    message: "Estimated chart — birth time unknown. Rising sign and houses are approximate (noon used).",
                    color: .yellow
                )
            }

            // Moon sign uncertain warning
            if viewModel.moonSignUncertain {
                DataQualityBanner(
                    icon: "moon.stars",
                    message: "The Moon changed sign on your birth date. Your Moon sign may be uncertain without an exact birth time.",
                    color: .blue
                )
            }

            // Big Three Card
            bigThreeCard
            
            // Planet Placements
            placementsSection
            
            // Aspects (if any)
            if !viewModel.aspects.isEmpty {
                aspectsSection
            }
        }
    }
    
    // MARK: - Big Three
    
    private var bigThreeCard: some View {
        CardView {
            VStack(spacing: 16) {
                Text("Your Big Three")
                    .font(.headline)
                
                HStack(spacing: 0) {
                    ForEach(viewModel.bigThree, id: \.name) { item in
                        VStack(spacing: 8) {
                            Text(item.emoji)
                                .font(.largeTitle)
                            
                            Text(item.name)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                            
                            Text(item.sign)
                                .font(.subheadline.bold())
                                .foregroundStyle(item.name == "Rising" && viewModel.birthTimeAssumed ? .gray : .purple)
                                .opacity(item.name == "Rising" && viewModel.birthTimeAssumed ? 0.7 : 1.0)

                            // Reliability badge per Big Three planet
                            if item.name == "Sun" {
                                Label("Exact", systemImage: "checkmark.circle.fill")
                                    .font(.caption2)
                                    .foregroundStyle(.green)
                            } else if item.name == "Rising" && viewModel.birthTimeAssumed {
                                Label("estimated", systemImage: "clock.badge.questionmark")
                                    .font(.caption2)
                                    .foregroundStyle(.orange)
                            } else if item.name == "Moon" && viewModel.moonSignUncertain {
                                Label("uncertain", systemImage: "questionmark.circle")
                                    .font(.caption2)
                                    .foregroundStyle(.blue)
                            } else {
                                Label("Reliable", systemImage: "checkmark.circle.fill")
                                    .font(.caption2)
                                    .foregroundStyle(.green)
                            }
                        }
                        .frame(maxWidth: .infinity)
                    }
                }

                if viewModel.birthTimeAssumed {
                    Divider()
                    HStack(spacing: 4) {
                        Image(systemName: "info.circle")
                            .foregroundStyle(.secondary)
                        Text("Sun sign is always exact. Rising & Houses depend on birth time.")
                            .font(.caption2)
                            .foregroundStyle(Color.textSecondary)
                    }
                }
            }
        }
    }
    
    // MARK: - Placements
    
    private var placementsSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("Planet Placements")
                        .font(.headline)
                    Spacer()
                    if viewModel.birthTimeAssumed {
                        Label("Houses estimated", systemImage: "clock.badge.questionmark")
                            .font(.caption2)
                            .foregroundStyle(.orange)
                    }
                }

                // Legend when birth time is unknown
                if viewModel.birthTimeAssumed {
                    HStack(spacing: 12) {
                        Label("Exact", systemImage: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                        Label("Estimated house", systemImage: "clock.badge.questionmark")
                            .foregroundStyle(.orange)
                    }
                    .font(.caption2)
                    Divider()
                }
                
                ForEach(viewModel.placements, id: \.name) { planet in
                    let isHouseDependent = viewModel.birthTimeAssumed &&
                        ["Ascendant", "Midheaven", "ASC", "MC"].contains(planet.name)
                    HStack {
                        Text(planetEmoji(planet.name))
                            .font(.title3)
                        
                        Text(planet.name)
                            .font(.subheadline)
                            .foregroundStyle(isHouseDependent ? Color.textSecondary : Color.textPrimary)
                        
                        Spacer()
                        
                        VStack(alignment: .trailing) {
                            Text(planet.sign)
                                .font(.subheadline.bold())
                                .foregroundStyle(isHouseDependent ? .gray : .purple)
                            
                            if let house = planet.house, house > 0 {
                                HStack(spacing: 2) {
                                    Text("House \(house)")
                                        .font(.caption)
                                    if viewModel.birthTimeAssumed {
                                        Image(systemName: "clock.badge.questionmark")
                                            .font(.caption2)
                                    }
                                }
                                .foregroundStyle(viewModel.birthTimeAssumed ? .orange : Color.textSecondary)
                            }
                        }
                        
                        if planet.retrograde ?? false {
                            Text("℞")
                                .font(.caption)
                                .foregroundStyle(.orange)
                        }
                    }
                    .opacity(isHouseDependent ? 0.7 : 1.0)
                    
                    if planet.name != viewModel.placements.last?.name {
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
                Text("Key Aspects")
                    .font(.headline)
                
                ForEach(viewModel.aspects.prefix(5), id: \.self) { aspect in
                    HStack {
                        Text("\(aspect.planet1) \(aspect.aspectType) \(aspect.planet2)")
                            .font(.subheadline)
                        
                        Spacer()
                        
                        Text(String(format: "%.1f°", aspect.orb ?? 0))
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
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
            Text("Calculating your chart...")
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
                
                Text("Error loading chart")
                    .font(.headline)
                
                Text(message)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)
                
                Button("Retry") {
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
        CardView {
            VStack(spacing: 12) {
                Image(systemName: "sparkles")
                    .font(.largeTitle)
                    .foregroundStyle(.purple)
                
                Text("Create your birth chart")
                    .font(.headline)
                
                Text("Add your birth details to see your chart")
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
            }
        }
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
        default: return "⭐"
        }
    }
}

// MARK: - Data Quality Banner

struct DataQualityBanner: View {
    let icon: String
    let message: String
    let color: Color

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: icon)
                .foregroundStyle(color)
                .font(.subheadline)
            Text(message)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(color.opacity(0.1))
        .clipShape(RoundedRectangle(cornerRadius: 10))
    }
}

// MARK: - Preview

#Preview {
    ChartView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
