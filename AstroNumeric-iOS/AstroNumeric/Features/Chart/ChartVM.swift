// ChartVM.swift
// ViewModel for natal chart functionality

import SwiftUI
import Observation

@Observable
final class ChartVM {
    // MARK: - State
    
    var chartData: ChartData?
    var isLoading = false
    var error: String?
    
    // MARK: - Dependencies
    
    private let api = APIClient.shared
    
    // MARK: - Actions
    
    @MainActor
    func fetchChart(for profile: Profile) async {
        guard !isLoading else { return }
        _lastProfile = profile

        // Only timezone is hard required; missing location degrades to sun-sign display
        let missing = missingChartFields(for: profile)
        if !missing.isEmpty {
            chartData = nil
            error = "Your birth chart needs: \(missing.joined(separator: ", ")). Update your profile and try again."
            HapticManager.notification(.warning)
            return
        }

        isLoading = true
        error = nil
        defer { isLoading = false }
        
        // LOCAL-FIRST: Try Swiss Ephemeris on-device calculation
        do {
            let localChart = try await EphemerisEngine.shared.calculateNatalChart(profile: profile)
            chartData = localChart
            HapticManager.impact(.light)
            return
        } catch {
            DebugLog.log("Local ephemeris failed, falling back to API: \(error)")
        }
        
        // FALLBACK: API calculation
        do {
            let response: V2ApiResponse<ChartData> = try await api.fetch(
                .natalChart(profile: profile),
                cachePolicy: .networkFirst
            )
            chartData = response.data
            HapticManager.impact(.light)
        } catch {
            self.error = error.localizedDescription
            HapticManager.notification(.error)
        }
    }

    private func missingChartFields(for profile: Profile) -> [String] {
        var missing: [String] = []
        if (profile.timezone?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ?? true) {
            missing.append("timezone")
        }
        return missing
    }

    /// True when the profile lacks lat/lon — chart will be sun-sign only
    var isLocationMissing: Bool {
        guard let profile = _lastProfile else { return false }
        return profile.latitude == nil || profile.longitude == nil
    }

    private var _lastProfile: Profile?
    
    // MARK: - Computed Properties
    
    var hasData: Bool {
        chartData != nil
    }
    
    /// True when birth time was not provided and noon was used as default
    var birthTimeAssumed: Bool {
        chartData?.metadata?.birthTimeAssumed ?? false
    }

    /// True when the Moon changes sign on the birth date — Moon sign may be wrong
    var moonSignUncertain: Bool {
        chartData?.metadata?.moonSignUncertain ?? false
    }

    /// Big Three: Sun, Moon, Rising (Ascendant)
    var bigThree: [BigThreeItem] {
        guard let planets = chartData?.planets else { return [] }
        
        var result: [BigThreeItem] = []
        
        if let sun = planets.first(where: { $0.name.lowercased() == "sun" }) {
            result.append(BigThreeItem(name: "Sun", sign: sun.sign, emoji: "☀️"))
        }
        if let moon = planets.first(where: { $0.name.lowercased() == "moon" }) {
            result.append(BigThreeItem(name: "Moon", sign: moon.sign, emoji: "🌙"))
        }
        if let asc = planets.first(where: { $0.name.lowercased().contains("ascendant") || $0.name.lowercased() == "rising" }) {
            result.append(BigThreeItem(name: "Rising", sign: asc.sign, emoji: "⬆️"))
        }
        
        return result
    }
    
    /// All planet placements
    var placements: [PlanetPlacement] {
        chartData?.planets ?? []
    }
    
    /// House placements
    var houses: [HousePlacement] {
        chartData?.houses ?? []
    }
    
    /// Aspects
    var aspects: [ChartAspect] {
        chartData?.aspects ?? []
    }
}

struct BigThreeItem: Identifiable {
    let id = UUID()
    let name: String
    let sign: String
    let emoji: String
}
