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
                    .readableContainer()
                }
                .refreshable {
                    if let profile = store.activeProfile {
                        await viewModel.fetchChart(for: profile)
                    }
                }
            }
            .navigationTitle("charts.birthChart".localized)
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

            chartAuthorityCard

            // Big Three Card
            bigThreeCard
            
            // Planet Placements
            placementsSection
            
            // Sensitive Points (Nodes, Chiron, Part of Fortune)
            if !viewModel.chartPoints.isEmpty {
                sensitivePointsSection
            }

            // Aspects (if any)
            if !viewModel.aspects.isEmpty {
                aspectsSection
            }
        }
    }
    
    // MARK: - Big Three

    private var chartAuthorityCard: some View {
        CardView {
            VStack(alignment: .leading, spacing: 14) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("ui.chart.0".localized)
                            .font(.system(.caption2, design: .monospaced))
                            .foregroundStyle(Color.textMuted)
                        Text(chartAuthorityHeadline)
                            .font(.title3.bold())
                    }
                    Spacer()
                    Label(chartAuthorityBadge, systemImage: "checkmark.seal.fill")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.green)
                }

                Text(chartAuthoritySupport)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)

                HStack(spacing: 12) {
                    authorityStat(title: "Planets", value: "\(viewModel.placements.count)")
                    authorityStat(title: "Points", value: "\(viewModel.chartPoints.count)")
                    authorityStat(title: "Dignities", value: "\(dignityCount)")
                }
            }
        }
    }

    private func authorityStat(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title.uppercased())
                .font(.system(.caption2, design: .monospaced))
                .foregroundStyle(Color.textMuted)
            Text(value)
                .font(.headline)
                .foregroundStyle(.white)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color.white.opacity(0.04))
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
    
    private var bigThreeCard: some View {
        CardView {
            VStack(spacing: 16) {
                Text("ui.chart.1".localized)
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
                                Label("ui.chart.10".localized, systemImage: "checkmark.circle.fill")
                                    .font(.caption2)
                                    .foregroundStyle(.green)
                            } else if item.name == "Rising" && viewModel.birthTimeAssumed {
                                Label("ui.chart.11".localized, systemImage: "clock.badge.questionmark")
                                    .font(.caption2)
                                    .foregroundStyle(.orange)
                            } else if item.name == "Moon" && viewModel.moonSignUncertain {
                                Label("ui.chart.12".localized, systemImage: "questionmark.circle")
                                    .font(.caption2)
                                    .foregroundStyle(.blue)
                            } else {
                                Label("ui.chart.13".localized, systemImage: "checkmark.circle.fill")
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
                        Text("ui.chart.2".localized)
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
                    Text("ui.chart.3".localized)
                        .font(.headline)
                    Spacer()
                    if viewModel.birthTimeAssumed {
                        Label("ui.chart.14".localized, systemImage: "clock.badge.questionmark")
                            .font(.caption2)
                            .foregroundStyle(.orange)
                    }
                }

                // Legend when birth time is unknown
                if viewModel.birthTimeAssumed {
                    HStack(spacing: 12) {
                        Label("ui.chart.15".localized, systemImage: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                        Label("ui.chart.16".localized, systemImage: "clock.badge.questionmark")
                            .foregroundStyle(.orange)
                    }
                    .font(.caption2)
                    Divider()
                }
                
                ForEach(viewModel.placements, id: \.name) { planet in
                    let isHouseDependent = viewModel.birthTimeAssumed &&
                        ["Ascendant", "Midheaven", "ASC", "MC"].contains(planet.name)
                    HStack(alignment: .top) {
                        Text(planetEmoji(planet.name))
                            .font(.title3)

                        VStack(alignment: .leading, spacing: 2) {
                            Text(planet.name)
                                .font(.subheadline)
                                .foregroundStyle(isHouseDependent ? Color.textSecondary : Color.textPrimary)

                            if let dignity = planet.dignity {
                                Text(dignityLabel(dignity))
                                    .font(.caption2.weight(.semibold))
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(dignityColor(dignity).opacity(0.14))
                                    .foregroundStyle(dignityColor(dignity))
                                    .clipShape(Capsule())
                            }
                        }

                        Spacer()

                        VStack(alignment: .trailing) {
                            Text(planet.sign)
                                .font(.subheadline.bold())
                                .foregroundStyle(isHouseDependent ? .gray : .purple)

                            if let house = planet.house, house > 0 {
                                HStack(spacing: 2) {
                                    Text(String(format: "fmt.chart.1".localized, "\(house)"))
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
    
    // MARK: - Sensitive Points

    private var sensitivePointsSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Text("ui.chart.4".localized)
                    .font(.headline)

                ForEach(viewModel.chartPoints) { point in
                    HStack {
                        Text(pointEmoji(point.name))
                            .font(.title3)

                        VStack(alignment: .leading, spacing: 2) {
                            Text(point.name)
                                .font(.subheadline)
                                .foregroundStyle(Color.textPrimary)
                            if point.name == "Part of Fortune", let ct = point.chartType {
                                Text(ct == "day" ? "tern.chart.0a".localized : "tern.chart.0b".localized)
                                    .font(.caption2)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }

                        Spacer()

                        VStack(alignment: .trailing) {
                            Text(point.sign)
                                .font(.subheadline.bold())
                                .foregroundStyle(.purple)
                            if let house = point.house, house > 0 {
                                Text(String(format: "fmt.chart.0".localized, "\(house)"))
                                    .font(.caption)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }

                        if point.retrograde == true {
                            Text("℞")
                                .font(.caption)
                                .foregroundStyle(.orange)
                        }
                    }

                    if point.id != viewModel.chartPoints.last?.id {
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
                Text("ui.chart.5".localized)
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
            Text("ui.chart.6".localized)
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
                
                Text("ui.chart.7".localized)
                    .font(.headline)
                
                Text(message)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)
                
                Button("action.retry".localized) {
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
                
                Text("ui.chart.8".localized)
                    .font(.headline)
                
                Text("ui.chart.9".localized)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
            }
        }
    }
    
    // MARK: - Helpers
    
    private func pointEmoji(_ name: String) -> String {
        switch name {
        case "North Node": return "☊"
        case "South Node": return "☋"
        case "Chiron": return "⚷"
        case "Part of Fortune": return "⊕"
        default: return "✦"
        }
    }

    private func dignityLabel(_ dignity: String) -> String {
        switch dignity.lowercased() {
        case "domicile": return "Domicile"
        case "exaltation": return "Exaltation"
        case "detriment": return "Detriment"
        case "fall": return "Fall"
        default: return dignity.capitalized
        }
    }

    private func dignityColor(_ dignity: String) -> Color {
        switch dignity.lowercased() {
        case "domicile", "exaltation": return .green
        case "detriment", "fall": return .orange
        default: return .secondary
        }
    }

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

    private var dignityCount: Int {
        viewModel.placements.compactMap(\ .dignity).count
    }

    private var chartAuthorityHeadline: String {
        if viewModel.isLocationMissing {
            return "Partial chart available"
        }
        if viewModel.birthTimeAssumed {
            return "Strong chart, estimated angles"
        }
        return "Full chart, calculated from birth time"
    }

    private var chartAuthorityBadge: String {
        if viewModel.isLocationMissing {
            return "Sun-sign only"
        }
        if viewModel.birthTimeAssumed {
            return "High confidence"
        }
        return "Full precision"
    }

    private var chartAuthoritySupport: String {
        if viewModel.isLocationMissing {
            return "You have enough data for a basic identity layer, but location is required for houses, angles, and the full interpretive picture."
        }
        if viewModel.birthTimeAssumed {
            return "Planet signs remain useful, but houses and the Rising sign are being estimated because the birth time is missing or uncertain."
        }
        return "This chart is using birth date, location, exact birth time, chart points, and dignity markers so the interpretation reads as a full natal map rather than a horoscope shortcut."
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
