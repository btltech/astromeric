// NumerologyVM.swift
// Feature ViewModel for Numerology functionality

import SwiftUI
import Observation

// Use the NumerologyData model from Models.swift
typealias V2NumerologyResponse = NumerologyData

@Observable
final class NumerologyVM {
    // MARK: - State

    /// v2 numerology response data
    var numerologyData: V2NumerologyResponse?

    /// Loading state
    var isLoading = false

    /// Error message
    var error: String?

    // MARK: - Dependencies

    private let api = APIClient.shared

    // MARK: - Actions

    /// Fetch numerology for a profile using the stored method preference.
    @MainActor
    func fetchNumerology(for profile: Profile, useChaldean: Bool = false) async {
        guard !isLoading else { return }

        isLoading = true
        error = nil
        defer { isLoading = false }

        let method = useChaldean ? "tern.numerologyVM.0a".localized : "tern.numerologyVM.0b".localized

        do {
            let response: V2ApiResponse<V2NumerologyResponse> = try await api.fetch(
                .numerologyProfile(profile: profile, method: method),
                cachePolicy: .networkFirst
            )
            numerologyData = response.data
            HapticManager.impact(.light)
        } catch {
            self.error = error.localizedDescription
            HapticManager.notification(.error)
        }
    }

    /// Fetch numerology with name and DOB only (for onboarding preview)
    @MainActor
    func fetchNumerology(name: String, dateOfBirth: String) async {
        guard !isLoading else { return }
        
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        do {
            let response: V2ApiResponse<V2NumerologyResponse> = try await api.fetch(
                .numerology(name: name, dateOfBirth: dateOfBirth),
                cachePolicy: .networkFirst
            )
            numerologyData = response.data
            HapticManager.impact(.light)
        } catch {
            self.error = error.localizedDescription
            HapticManager.notification(.error)
        }
    }
    
    /// Retry fetching
    @MainActor
    func retry(for profile: Profile) async {
        await fetchNumerology(for: profile)
    }
    
    /// Clear data
    func reset() {
        numerologyData = nil
        error = nil
    }
    
    // MARK: - Computed Properties
    
    /// Whether we have data to display
    var hasData: Bool {
        numerologyData != nil
    }
    
    /// Life path number display
    var lifePathNumber: Int? {
        numerologyData?.lifePath?.number
    }
    
    /// Personal year number
    var personalYearNumber: Int? {
        numerologyData?.personalYear?.cycleNumber
    }
    
    /// Lucky numbers
    var luckyNumbers: [Int] {
        numerologyData?.luckyNumbers ?? []
    }
}

// Note: V2NumerologyResponse, LifePathData, and PersonalYearData are defined in Models.swift
