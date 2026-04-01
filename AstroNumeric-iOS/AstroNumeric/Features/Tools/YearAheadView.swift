// YearAheadView.swift
// Year-ahead forecast view

import SwiftUI

struct YearAheadView: View {
    @Environment(AppStore.self) private var store
    @State private var vm = YearAheadVM()
    @State private var selectedYear = Calendar.current.component(.year, from: Date())
    @State private var lifePhaseData: LifePhaseData?

    @State private var isExplaining = false
    @State private var explanationMarkdown: String?
    @State private var explanationSource: AIInsightSource = .fallback
    @State private var explanationGeneratedAt: Date = Date()
    @State private var showExplanation = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        // Warn when birth time unknown — Solar Return depends on exact time
                        if store.activeProfile?.dataQuality != .full {
                            DataQualityBanner(
                                icon: "clock.badge.questionmark",
                                message: "Year Ahead forecast is less precise without an exact birth time. The Solar Return Ascendant and house themes may be inaccurate.",
                                color: .yellow
                            )
                            .padding(.horizontal)
                        }

                        if let forecast = vm.forecast {
                            Button {
                                Task { @MainActor in
                                    await explain(forecast)
                                }
                            } label: {
                                HStack(spacing: 8) {
                                    if isExplaining {
                                        ProgressView()
                                            .scaleEffect(0.8)
                                    } else {
                                        Image(systemName: "sparkles")
                                    }
                                    Text(isExplaining ? "Generating..." : "Explain This Year")
                                        .font(.subheadline.weight(.medium))
                                }
                                .foregroundStyle(.purple)
                                .padding(.horizontal, 16)
                                .padding(.vertical, 10)
                                .background(Color.purple.opacity(0.15))
                                .clipShape(Capsule())
                            }
                            .disabled(isExplaining)

                            // Life Phase — show FIRST for context
                            if let phase = lifePhaseData {
                                LifePhaseCard(data: phase)
                            }

                            CardView {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Year Ahead \(forecast.year)")
                                        .font(.headline)
                                    Text("Personal Year \(forecast.personalYear.number): \(forecast.personalYear.theme)")
                                        .font(.subheadline)
                                    Text(forecast.personalYear.description ?? "")
                                        .font(.caption)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }
                            
                            CardView {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Solar Return")
                                        .font(.headline)
                                    Text(forecast.solarReturn.date)
                                        .font(.subheadline)
                                    Text(forecast.solarReturn.description)
                                        .font(.caption)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }
                            
                            if !forecast.keyThemes.isEmpty {
                                CardView {
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text("Key Themes")
                                            .font(.headline)
                                        ForEach(forecast.keyThemes, id: \.self) { theme in
                                            Text("• \(theme)")
                                                .font(.caption)
                                                .foregroundStyle(Color.textSecondary)
                                        }
                                    }
                                }
                            }
                            
                            if !forecast.advice.isEmpty {
                                CardView {
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text("Year Advice")
                                            .font(.headline)
                                        ForEach(forecast.advice, id: \.self) { tip in
                                            Text("• \(tip)")
                                                .font(.caption)
                                                .foregroundStyle(Color.textSecondary)
                                        }
                                    }
                                }
                            }
                            
                            if !forecast.monthlyForecasts.isEmpty {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Monthly Highlights")
                                        .font(.headline)
                                        .padding(.horizontal, 4)
                                    ForEach(forecast.monthlyForecasts, id: \.month) { month in
                                        CardView {
                                            VStack(alignment: .leading, spacing: 6) {
                                                HStack {
                                                    Text("\(month.monthName) \(month.year)")
                                                        .font(.headline)
                                                    Spacer()
                                                    Text("Personal Month \(month.personalMonth)")
                                                        .font(.caption)
                                                        .foregroundStyle(Color.textSecondary)
                                                }
                                                Text(month.focus)
                                                    .font(.subheadline)
                                                if !month.highlights.isEmpty {
                                                    ForEach(month.highlights, id: \.self) { highlight in
                                                        Text("• \(highlight)")
                                                            .font(.caption)
                                                            .foregroundStyle(Color.textSecondary)
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        } else if vm.isLoading {
                            ProgressView("Loading year ahead...")
                                .tint(.white)
                        } else if let error = vm.error {
                            ErrorStateView(message: error) {
                                await vm.load(profile: store.activeProfile, year: selectedYear)
                            }
                        } else {
                            CardView {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Year Ahead")
                                        .font(.headline)
                                    Text(store.activeProfile == nil ? "Select a profile to generate your forecast." : "Tap the year in the top-right to refresh.")
                                        .font(.caption)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Year Ahead")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        ForEach((selectedYear-2)...(selectedYear+1), id: \.self) { year in
                            Button(String(year)) {
                                selectedYear = year
                                Task { await vm.load(profile: store.activeProfile, year: year) }
                            }
                        }
                    } label: {
                        Text(String(selectedYear))
                    }
                }
            }
            .task(id: "\(store.activeProfile?.id ?? 0)-\(selectedYear)") {
                async let forecast: () = vm.load(profile: store.activeProfile, year: selectedYear)
                async let phase: () = fetchLifePhase()
                _ = await (forecast, phase)
            }
            .sheet(isPresented: $showExplanation) {
                if let markdown = explanationMarkdown {
                    AIInsightsSheetView(
                        markdown: markdown,
                        source: explanationSource,
                        generatedAt: explanationGeneratedAt,
                        onRegenerate: {
                            if let forecast = vm.forecast {
                                Task { @MainActor in await explain(forecast, forceRefresh: true) }
                            }
                        }
                    )
                }
            }
        }
    }

    @MainActor
    private func explain(_ forecast: YearAheadForecast, forceRefresh: Bool = false) async {
        isExplaining = true
        defer { isExplaining = false }

        let headline = "Year Ahead \(forecast.year) • Personal Year \(forecast.personalYear.number)"
        let sections: [SectionSummary] = [
            SectionSummary(title: "Personal Year \(forecast.personalYear.number)", highlights: [
                forecast.personalYear.theme,
                forecast.personalYear.description ?? ""
            ].filter { !$0.isEmpty }),
            SectionSummary(title: "Solar Return", highlights: [
                "Date: \(forecast.solarReturn.date)",
                forecast.solarReturn.description
            ]),
            SectionSummary(title: "Key Themes", highlights: Array(forecast.keyThemes.prefix(6))),
            SectionSummary(title: "Advice", highlights: Array(forecast.advice.prefix(6))),
        ]

        let request = AIExplainRequest(
            scope: "year_ahead",
            headline: headline,
            theme: forecast.personalYear.theme,
            sections: sections,
            numerologySummary: nil,
            simpleLanguage: true
        )

        do {
            let response: V2ApiResponse<AIExplainResponse> = try await APIClient.shared.fetch(
                .aiExplain(reading: request),
                cachePolicy: forceRefresh ? .networkOnly : .cacheFirst
            )
            explanationMarkdown = response.data.summary
            explanationSource = .ai
            explanationGeneratedAt = Date()
        } catch {
            var fallback = "## TL;DR\n\n"
            fallback += "Your **Personal Year \(forecast.personalYear.number)** sets the tone for \(forecast.year). Focus on **\(forecast.personalYear.theme.lowercased())**.\n\n"
            fallback += "---\n\n"
            fallback += "## Key points\n"
            fallback += "- Solar Return: **\(forecast.solarReturn.date)**\n"
            if !forecast.keyThemes.isEmpty {
                let themes = forecast.keyThemes.prefix(4).map { "**\($0)**" }.joined(separator: ", ")
                fallback += "- Themes: \(themes)\n"
            }
            if let firstAdvice = forecast.advice.first, !firstAdvice.isEmpty {
                fallback += "- Advice: \(firstAdvice)\n"
            }
            fallback += "\n---\n\n"
            fallback += "## Practical next step\n\n"
            fallback += "Pick **one theme** and choose **one small habit** you can repeat weekly. Use the monthly highlights to plan around it."

            explanationMarkdown = fallback
            explanationSource = .fallback
            explanationGeneratedAt = Date()
        }

        showExplanation = true
    }

    // MARK: - Life Phase

    private func fetchLifePhase() async {
        guard let profile = store.activeProfile else { return }
        do {
            let payload = ProfilePayload(
                name: profile.name,
                dateOfBirth: profile.dateOfBirth,
                timeOfBirth: profile.timeOfBirth,
                placeOfBirth: profile.placeOfBirth,
                latitude: profile.latitude,
                longitude: profile.longitude,
                timezone: profile.timezone ?? "UTC",
                houseSystem: profile.houseSystem
            )
            let response: V2ApiResponse<LifePhaseData> = try await APIClient.shared.fetch(
                .lifePhase(profile: payload),
                cachePolicy: .networkFirst
            )
            await MainActor.run { lifePhaseData = response.data }
        } catch {
            // Silent — LifePhaseCard stays hidden if unavailable
        }
    }
}

@Observable
final class YearAheadVM {
    var forecast: YearAheadForecast?
    var isLoading = false
    var error: String?
    
    private let api = APIClient.shared
    
    @MainActor
    func load(profile: Profile?, year: Int) async {
        guard let profile else {
            forecast = nil
            error = nil
            return
        }
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            let response: V2ApiResponse<YearAheadForecast> = try await api.fetch(
                .yearAheadForecast(profile: profile, year: year),
                cachePolicy: .networkFirst
            )
            forecast = response.data
        } catch {
            forecast = nil
            self.error = error.localizedDescription
        }
    }
}

// MARK: - Models

struct YearAheadForecast: Codable {
    let year: Int
    let personalYear: YearNumberTheme
    let universalYear: YearNumberTheme
    let solarReturn: SolarReturnInfo
    let eclipses: EclipseBundle
    let ingresses: [Ingress]
    let monthlyForecasts: [MonthlyForecast]
    let keyThemes: [String]
    let advice: [String]
    
    enum CodingKeys: String, CodingKey {
        case year
        case personalYear = "personal_year"
        case universalYear = "universal_year"
        case solarReturn = "solar_return"
        case eclipses
        case ingresses
        case monthlyForecasts = "monthly_forecasts"
        case keyThemes = "key_themes"
        case advice
    }
}

struct YearNumberTheme: Codable {
    let number: Int
    let theme: String
    let description: String?
}

struct SolarReturnInfo: Codable {
    let date: String
    let description: String
}

struct EclipseBundle: Codable {
    let all: [EclipseEvent]
    let personalImpacts: [EclipseImpact]
    
    enum CodingKeys: String, CodingKey {
        case all
        case personalImpacts = "personal_impacts"
    }
}

struct EclipseEvent: Codable, Identifiable {
    var id: String { date + type + sign }
    let date: String
    let type: String
    let sign: String
    let degree: Double?
}

struct EclipseImpact: Codable {
    let eclipse: EclipseEvent
    let impacts: [ImpactDetail]
    let significance: String
}

struct ImpactDetail: Codable {
    let type: String
    let name: String
    let aspect: String
    let orb: Double?
}

struct Ingress: Codable, Identifiable {
    var id: String { date + planet + sign }
    let date: String
    let planet: String
    let sign: String
    let impact: String
}

struct MonthlyForecast: Codable, Identifiable {
    var id: Int { month }
    let month: Int
    let monthName: String
    let year: Int
    let season: String
    let focus: String
    let element: String
    let personalMonth: Int
    let eclipses: [EclipseEvent]
    let ingresses: [Ingress]
    let highlights: [String]
    
    enum CodingKeys: String, CodingKey {
        case month
        case monthName = "month_name"
        case year, season, focus, element
        case personalMonth = "personal_month"
        case eclipses, ingresses, highlights
    }
}

#Preview {
    YearAheadView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
