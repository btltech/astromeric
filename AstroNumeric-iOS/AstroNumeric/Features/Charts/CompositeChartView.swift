// CompositeChartView.swift
// Composite chart for two profiles

import SwiftUI

struct CompositeChartView: View {
    @Environment(AppStore.self) private var store
    @State private var vm = CompositeChartVM()
    @State private var selectedPartnerId: Int?
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        PremiumHeroCard(
                            eyebrow: "hero.compositeChart.eyebrow".localized,
                            title: "hero.compositeChart.title".localized,
                            bodyText: "hero.compositeChart.body".localized,
                            accent: [Color(hex: "241532"), Color(hex: "8750b7"), Color(hex: "d07a56")],
                            chips: ["hero.compositeChart.chip.0".localized, "hero.compositeChart.chip.1".localized, "hero.compositeChart.chip.2".localized]
                        )

                        if store.profiles.count < 2 {
                            CardView {
                                Text("ui.compositeChart.0".localized)
                                    .font(.caption)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        } else {
                            Picker("ui.compositeChart.3".localized, selection: $selectedPartnerId) {
                                ForEach(Array(store.profiles.filter { $0.id != store.activeProfile?.id }.enumerated()), id: \.element.id) { index, profile in
                                    Text(profile.displayName(
                                        hideSensitive: store.hideSensitiveDetailsEnabled,
                                        role: .genericProfile,
                                        index: index
                                    ))
                                    .tag(Optional(profile.id))
                                }
                            }
                            .pickerStyle(.menu)
                            .onChange(of: selectedPartnerId) { _, _ in
                                Task { await vm.load(store: store, partnerId: selectedPartnerId) }
                            }

                            PremiumSectionHeader(
                title: "section.compositeChart.0.title".localized,
                subtitle: "section.compositeChart.0.subtitle".localized
            )

                            // Data quality warning when either profile lacks exact birth time
                            let personA = store.activeProfile
                            let personB = store.profiles.first { $0.id == selectedPartnerId }
                            if personA?.dataQuality != .full || personB?.dataQuality != .full {
                                DataQualityBanner(
                                    icon: "chart.pie.fill",
                                    message: "Composite chart accuracy is reduced — one or more profiles lack a confirmed birth time. House placements and the Composite Ascendant are estimated.",
                                    color: .orange
                                )
                            }
                            
                            if vm.isLoading {
                                ProgressView("Building composite chart...")
                                    .tint(.white)
                            } else if let chart = vm.chart {
                                CardView {
                                    VStack(alignment: .leading, spacing: 6) {
                                        Text("ui.compositeChart.1".localized)
                                            .font(.headline)
                                        Text(
                                            store.hideSensitiveDetailsEnabled
                                                ? "You + Match"
                                                : "\(chart.metadata.personA) + \(chart.metadata.personB)"
                                        )
                                            .font(.caption)
                                            .foregroundStyle(Color.textSecondary)
                                    }
                                }

                                let insights = compositeInsights(for: chart)
                                if !insights.isEmpty {
                                    CardView {
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text("ui.compositeChart.2".localized)
                                                .font(.headline)
                                            ForEach(insights, id: \.self) { item in
                                                Text("• \(item)")
                                                    .font(.caption)
                                                    .foregroundStyle(Color.textSecondary)
                                            }
                                        }
                                    }
                                }
                                
                                ForEach(chart.planets, id: \.name) { planet in
                                    CardView {
                                        HStack {
                                            Text(planet.name)
                                                .font(.headline)
                                            Spacer()
                                            Text("\(planet.sign) \(planet.degree, specifier: "%.1f")°")
                                                .font(.subheadline)
                                                .foregroundStyle(Color.textSecondary)
                                        }
                                    }
                                }
                            }
                        }
                    }
                    .padding()
                    .readableContainer()
                }
            }
            .navigationTitle("screen.compositeChart".localized)
            .navigationBarTitleDisplayMode(.inline)
            .task(id: "\(store.activeProfile?.id ?? 0)-\(store.profiles.count)") {
                if selectedPartnerId == nil {
                    selectedPartnerId = store.profiles.first { $0.id != store.activeProfile?.id }?.id
                    await vm.load(store: store, partnerId: selectedPartnerId)
                }
            }
        }
    }
}

private func compositeInsights(for chart: CompositeChartResponse) -> [String] {
    let keywords = compositeSignKeywords
    func line(for planetName: String, prefix: String, suffix: String) -> String? {
        guard let planet = chart.planets.first(where: { $0.name.lowercased() == planetName }) else { return nil }
        let key = keywords[planet.sign] ?? "shared growth"
        return "\(prefix) in \(planet.sign): \(key) \(suffix)."
    }
    return [
        line(for: "sun", prefix: "Composite Sun", suffix: "defines the shared purpose"),
        line(for: "moon", prefix: "Composite Moon", suffix: "sets the emotional climate"),
        line(for: "venus", prefix: "Composite Venus", suffix: "shows how affection is expressed"),
        line(for: "mars", prefix: "Composite Mars", suffix: "drives momentum and conflict style")
    ].compactMap { $0 }
}

private let compositeSignKeywords: [String: String] = [
    "Aries": "the bond thrives on initiative and bold starts",
    "Taurus": "the bond values loyalty, comfort, and consistency",
    "Gemini": "the bond grows through conversation and curiosity",
    "Cancer": "the bond centers care, safety, and belonging",
    "Leo": "the bond seeks joy, play, and shared visibility",
    "Virgo": "the bond improves through service and practical care",
    "Libra": "the bond emphasizes harmony and fairness",
    "Scorpio": "the bond deepens through intensity and transformation",
    "Sagittarius": "the bond expands through adventure and honesty",
    "Capricorn": "the bond matures through commitment and structure",
    "Aquarius": "the bond innovates through friendship and vision",
    "Pisces": "the bond softens through empathy and spiritual connection"
]

@Observable
final class CompositeChartVM {
    var chart: CompositeChartResponse?
    var isLoading = false
    var error: String?
    
    private let api = APIClient.shared
    
    @MainActor
    func load(store: AppStore, partnerId: Int?) async {
        guard let personA = store.activeProfile,
              let partnerId,
              let personBProfile = store.profiles.first(where: { $0.id == partnerId }) else { return }
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        let payload = personBProfile.privacySafePayload(hideSensitive: store.hideSensitiveDetailsEnabled)
        do {
            let response: V2ApiResponse<CompositeChartResponse> = try await api.fetch(
                .compositeChart(personA: personA, personB: payload),
                cachePolicy: .networkFirst
            )
            chart = response.data
        } catch {
            chart = nil
            self.error = error.localizedDescription
        }
    }
}

struct CompositeChartResponse: Codable {
    let planets: [ChartPlanet]
    let metadata: CompositeMetadata
}

struct CompositeMetadata: Codable {
    let personA: String
    let personB: String
    let method: String
    
    enum CodingKeys: String, CodingKey {
        case personA = "person_a"
        case personB = "person_b"
        case method
    }
}

#Preview {
    CompositeChartView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
