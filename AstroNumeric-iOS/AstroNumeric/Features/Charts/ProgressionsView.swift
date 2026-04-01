// ProgressionsView.swift
// Secondary progressed chart overview

import SwiftUI

struct ProgressionsView: View {
    @Environment(AppStore.self) private var store
    @State private var vm = ProgressionsVM()
    @State private var targetDate = Date()
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        // Warn when birth time is unknown — progressions depend on exact time
                        if store.activeProfile?.dataQuality != .full {
                            DataQualityBanner(
                                icon: "clock.badge.questionmark",
                                message: "Secondary progressions are less precise without an exact birth time. Add your birth time in Profile for more accurate results.",
                                color: .yellow
                            )
                            .padding(.horizontal)
                        }

                        DatePicker("Target Date", selection: $targetDate, displayedComponents: .date)
                            .onChange(of: targetDate) { _, _ in
                                Task { await vm.load(profile: store.activeProfile, targetDate: targetDate) }
                            }
                            .padding(.horizontal)
                        
                        if vm.isLoading {
                            ProgressView("Calculating progressions...")
                                .tint(.white)
                        } else if let chart = vm.chart {
                            CardView {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Progressed Chart")
                                        .font(.headline)
                                    Text("Progressed Date: \(chart.metadata.progressedDate)")
                                        .font(.subtext)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }

                            let insights = progressionInsights(for: chart)
                            if !insights.isEmpty {
                                CardView {
                                    VStack(alignment: .leading, spacing: 6) {
                                        Text("Interpretation")
                                            .font(.headline)
                                        ForEach(insights, id: \.self) { item in
                                            Text("• \(item)")
                                                .font(.subtext)
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
                        } else {
                            CardView {
                                Text("Select a profile to view progressions.")
                                    .font(.subtext)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Progressions")
            .navigationBarTitleDisplayMode(.inline)
            .task(id: store.activeProfile?.id) {
                await vm.load(profile: store.activeProfile, targetDate: targetDate)
            }
        }
    }
}

private func progressionInsights(for chart: ProgressedChartResponse) -> [String] {
    let keywords = signKeywords
    func line(for planetName: String, prefix: String) -> String? {
        guard let planet = chart.planets.first(where: { $0.name.lowercased() == planetName }) else { return nil }
        let key = keywords[planet.sign] ?? "new focus areas"
        return "\(prefix) in \(planet.sign): \(key)."
    }
    return [
        line(for: "sun", prefix: "Progressed Sun"),
        line(for: "moon", prefix: "Progressed Moon"),
        line(for: "venus", prefix: "Progressed Venus"),
        line(for: "mars", prefix: "Progressed Mars")
    ].compactMap { $0 }
}

private let signKeywords: [String: String] = [
    "Aries": "growth through initiative, courage, and bold beginnings",
    "Taurus": "stability, values, and slow-burn mastery",
    "Gemini": "curiosity, communication, and learning new pathways",
    "Cancer": "emotional security, home, and nurturing bonds",
    "Leo": "visibility, creativity, and heartfelt leadership",
    "Virgo": "craft, refinement, and practical self-improvement",
    "Libra": "balance, harmony, and relationship recalibration",
    "Scorpio": "transformation, depth, and emotional intensity",
    "Sagittarius": "expansion, truth-seeking, and exploration",
    "Capricorn": "discipline, structure, and long-term goals",
    "Aquarius": "innovation, community, and future-facing ideals",
    "Pisces": "intuition, compassion, and spiritual integration"
]

@Observable
final class ProgressionsVM {
    var chart: ProgressedChartResponse?
    var isLoading = false
    var error: String?
    
    private let api = APIClient.shared
    
    @MainActor
    func load(profile: Profile?, targetDate: Date) async {
        guard let profile else {
            chart = nil
            error = nil
            return
        }
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            let response: V2ApiResponse<ProgressedChartResponse> = try await api.fetch(
                .progressedChart(profile: profile, targetDate: targetDate),
                cachePolicy: .networkFirst
            )
            chart = response.data
        } catch {
            chart = nil
            self.error = error.localizedDescription
        }
    }
}

struct ProgressedChartResponse: Codable {
    let planets: [ChartPlanet]
    let metadata: ProgressedMetadata
}

struct ChartPlanet: Codable {
    let name: String
    let sign: String
    let degree: Double
    let absoluteDegree: Double?
    
    enum CodingKeys: String, CodingKey {
        case name, sign, degree
        case absoluteDegree = "absolute_degree"
    }
}

struct ProgressedMetadata: Codable {
    let progressedDate: String
    let targetDate: String
    let houseSystem: String?
    
    enum CodingKeys: String, CodingKey {
        case progressedDate = "progressed_date"
        case targetDate = "target_date"
        case houseSystem = "house_system"
    }
}

#Preview {
    ProgressionsView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
