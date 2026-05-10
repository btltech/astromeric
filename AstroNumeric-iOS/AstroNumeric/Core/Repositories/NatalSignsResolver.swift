// NatalSignsResolver.swift
// Local-first resolution of natal Moon/Rising signs with API fallback.
// Stateless — caching lives in AppStore.

import Foundation

protocol NatalSignsResolving: Sendable {
    func resolve(for profile: Profile) async -> NatalSigns?
}

struct DefaultNatalSignsResolver: NatalSignsResolving {
    private let api: APIService
    private let ephemeris: EphemerisService

    init(
        api: APIService = LiveAPIService(),
        ephemeris: EphemerisService = LiveEphemerisService()
    ) {
        self.api = api
        self.ephemeris = ephemeris
    }

    func resolve(for profile: Profile) async -> NatalSigns? {
        // LOCAL-FIRST: deterministic on-device ephemeris.
        do {
            let signs = try await ephemeris.getNatalSigns(for: profile)
            return NatalSigns(moonSign: signs.moonSign, risingSign: signs.risingSign)
        } catch {
            DebugLog.log("Local ephemeris failed for natal signs, falling back to API: \(error)")
        }

        // FALLBACK: API.
        do {
            let response: V2ApiResponse<ChartData> = try await api.fetch(
                .natalChart(profile: profile),
                cachePolicy: .networkFirst
            )
            let moonSign = response.data.planets.first(where: { $0.name == "Moon" })?.sign
            let risingSign = response.data.planets.first(where: {
                $0.name == "Ascendant" || $0.name == "ASC" || $0.name == "Rising"
            })?.sign
            return NatalSigns(moonSign: moonSign, risingSign: risingSign)
        } catch {
            DebugLog.log("Failed to fetch natal signs via API: \(error)")
            return nil
        }
    }
}
