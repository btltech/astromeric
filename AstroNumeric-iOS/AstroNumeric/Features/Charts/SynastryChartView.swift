// SynastryChartView.swift
// Synastry aspects + compatibility highlights

import SwiftUI

struct SynastryChartView: View {
    @Environment(AppStore.self) private var store
    @State private var vm = SynastryChartVM()
    @State private var selectedPartnerId: Int?
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        PremiumHeroCard(
                            eyebrow: "hero.synastryChart.eyebrow".localized,
                            title: "hero.synastryChart.title".localized,
                            bodyText: "hero.synastryChart.body".localized,
                            accent: [Color(hex: "2c1530"), Color(hex: "97457c"), Color(hex: "5052ba")],
                            chips: ["hero.synastryChart.chip.0".localized, "hero.synastryChart.chip.1".localized, "hero.synastryChart.chip.2".localized, "hero.synastryChart.chip.3".localized]
                        )

                        if store.profiles.count < 2 {
                            CardView {
                                Text("ui.synastryChart.0".localized)
                                    .font(.subtext)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        } else {
                            Picker("ui.synastryChart.7".localized, selection: $selectedPartnerId) {
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
                title: "section.synastryChart.0.title".localized,
                subtitle: "section.synastryChart.0.subtitle".localized
            )

                            // Data quality warning when either profile lacks exact birth time
                            let personA = store.activeProfile
                            let personB = store.profiles.first { $0.id == selectedPartnerId }
                            let bothExact = personA?.dataQuality == .full && personB?.dataQuality == .full
                            let eitherMissing = personA?.dataQuality != .full || personB?.dataQuality != .full
                            if eitherMissing {
                                DataQualityBanner(
                                    icon: "person.2.slash",
                                    message: bothExact ? "" :
                                        "Synastry accuracy is reduced — \(personA?.dataQuality != .full && personB?.dataQuality != .full ? "tern.synastryChart.0a".localized : "tern.synastryChart.0b".localized) a confirmed birth time. Rising sign and house overlaps are estimated.",
                                    color: .orange
                                )
                            }
                            
                            if vm.isLoading {
                                ProgressView("Loading synastry...")
                                    .tint(.white)
                            } else if let error = vm.error {
                                CardView {
                                    VStack(spacing: 8) {
                                        Image(systemName: "exclamationmark.triangle.fill")
                                            .font(.title)
                                            .foregroundStyle(.red)
                                        Text("ui.synastryChart.1".localized)
                                            .font(.headline)
                                        Text(error)
                                            .font(.caption.monospaced())
                                            .foregroundStyle(.red.opacity(0.8))
                                            .multilineTextAlignment(.center)
                                    }
                                }
                            } else if let result = vm.result {
                                let summary = synastrySummary(result.compatibility)
                                if !summary.isEmpty {
                                    CardView {
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text("ui.synastryChart.2".localized)
                                                .font(.headline)
                                            Text(summary)
                                                .font(.subtext)
                                                .foregroundStyle(Color.textSecondary)
                                        }
                                    }
                                }

                                if !result.compatibility.strengths.isEmpty {
                                    CardView {
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text("ui.synastryChart.3".localized)
                                                .font(.headline)
                                            ForEach(result.compatibility.strengths, id: \.self) { item in
                                                Text("• \(item)")
                                                    .font(.subtext)
                                                    .foregroundStyle(Color.textSecondary)
                                            }
                                        }
                                    }
                                }
                                
                                if !result.compatibility.challenges.isEmpty {
                                    CardView {
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text("ui.synastryChart.4".localized)
                                                .font(.headline)
                                            ForEach(result.compatibility.challenges, id: \.self) { item in
                                                Text("• \(item)")
                                                    .font(.subtext)
                                                    .foregroundStyle(Color.textSecondary)
                                            }
                                        }
                                    }
                                }

                                if !result.compatibility.advice.isEmpty {
                                    CardView {
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text("ui.synastryChart.5".localized)
                                                .font(.headline)
                                            ForEach(result.compatibility.advice, id: \.self) { item in
                                                Text("• \(item)")
                                                    .font(.subtext)
                                                    .foregroundStyle(Color.textSecondary)
                                            }
                                        }
                                    }
                                }
                                
                                if !result.synastryAspects.isEmpty {
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text("ui.synastryChart.6".localized)
                                            .font(.headline)
                                            .padding(.horizontal, 4)
                                        ForEach(result.synastryAspects) { aspect in
                                            CardView {
                                                VStack(alignment: .leading, spacing: 4) {
                                                    Text("\(aspect.planet1) \(aspect.aspect) \(aspect.planet2)")
                                                        .font(.headline)
                                                    Text(String(format: "fmt.synastryChart.0".localized, String(format: "%.1f", aspect.orb)))
                                                        .font(.subtext)
                                                        .foregroundStyle(Color.textSecondary)
                                                }
                                            }
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
            .navigationTitle("screen.synastry".localized)
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

private func synastrySummary(_ compatibility: SynastryCompatibility) -> String {
    let strengthsCount = compatibility.strengths.count
    let challengesCount = compatibility.challenges.count
    if strengthsCount == 0 && challengesCount == 0 { return "" }
    var summary = "Balance \(strengthsCount) strengths with \(challengesCount) growth edges."
    if let focus = compatibility.advice.first {
        summary.append(" Focus next on: \(focus)")
    }
    return summary
}

@Observable
final class SynastryChartVM {
    var result: SynastryChartResponse?
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
            let response: V2ApiResponse<SynastryChartResponse> = try await api.fetch(
                .synastryChart(personA: personA, personB: payload),
                cachePolicy: .networkFirst
            )
            result = response.data
        } catch {
            result = nil
            self.error = error.localizedDescription
        }
    }
}

struct SynastryChartResponse: Codable {
    let synastryAspects: [SynastryAspect]
    let compatibility: SynastryCompatibility
    
    enum CodingKeys: String, CodingKey {
        case synastryAspects = "synastry_aspects"
        case compatibility
    }
}

struct SynastryAspect: Codable, Identifiable {
    var id: String { planet1 + planet2 + aspect }
    let planet1: String
    let planet2: String
    let aspect: String
    let orb: Double
}

struct SynastryCompatibility: Codable {
    let strengths: [String]
    let challenges: [String]
    let advice: [String]
}

#Preview {
    SynastryChartView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
