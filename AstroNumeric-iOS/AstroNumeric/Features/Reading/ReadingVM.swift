// ReadingVM.swift
// Feature ViewModel for Reading functionality

import SwiftUI
import Observation

@Observable
final class ReadingVM {
    // MARK: - State
    
    /// Selected reading scope
    var selectedScope: ReadingScope = .daily
    
    /// Current reading data
    var currentReading: PredictionData?
    
    /// Loading state
    var isLoading = false
    
    /// Error message
    var error: String?
    
    // MARK: - Private
    
    private let api = APIClient.shared
    
    // MARK: - Actions
    
    /// Fetch reading for the given profile
    @MainActor
    func fetchReading(for profile: Profile) async {
        isLoading = true
        error = nil
        
        defer { isLoading = false }
        
        do {
            // Always use full profile data (works without auth)
            let response: V2ApiResponse<PredictionData> = try await api.fetch(
                .reading(profile: profile, scope: selectedScope),
                cachePolicy: .networkFirst
            )
            currentReading = response.data
        } catch {
            self.error = error.localizedDescription
        }
    }
    
    /// Reset to initial state
    func reset() {
        currentReading = nil
        error = nil
    }
    
    /// Change scope and refetch
    @MainActor
    func changeScope(to scope: ReadingScope, for profile: Profile) async {
        // Clear current reading and fetch new one
        currentReading = nil
        selectedScope = scope
        await fetchReading(for: profile)
    }
}
