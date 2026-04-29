// CompatibilityVM.swift
// ViewModel for synastry/compatibility functionality

import SwiftUI
import Observation

@Observable
final class CompatibilityVM {
    // MARK: - State
    
    var compatibilityData: CompatibilityResult?
    var isLoading = false
    var error: String?
    
    // Second profile for comparison
    var personBName = ""
    var personBDOB = Date()
    var personBTime: Date?
    var personBPlace = ""
    
    // Use an existing saved profile for person B (higher accuracy)
    var useSavedProfileForPersonB: Bool = false
    var selectedPersonBProfileId: Int?
    
    // MARK: - Dependencies
    
    private let api = APIClient.shared
    
    // MARK: - Actions
    
    @MainActor
    func fetchCompatibility(personA: Profile, personB: ProfilePayload) async {
        guard !isLoading else { return }
        
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        do {
            let response: V2ApiResponse<CompatibilityResult> = try await api.fetch(
                .romanticCompatibility(personA: personA, personB: personB),
                cachePolicy: .networkFirst
            )
            DebugLog.log("Compatibility response received (overallScore: \(String(describing: response.data.overallScore)))")
            compatibilityData = response.data
            HapticManager.impact(.light)
        } catch {
            DebugLog.log("Compatibility API error: \(error)")
            self.error = error.localizedDescription
            HapticManager.notification(.error)
        }
    }
    
    /// Create person B profile from form data
    func buildManualPersonB() -> ProfilePayload {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let dobString = formatter.string(from: personBDOB)
        
        var timeString: String? = nil
        if let time = personBTime {
            let timeFormatter = DateFormatter()
            timeFormatter.dateFormat = "HH:mm"
            timeString = timeFormatter.string(from: time)
        }
        
        return ProfilePayload(
            name: personBName,
            dateOfBirth: dobString,
            timeOfBirth: timeString,
            latitude: nil,
            longitude: nil,
            timezone: nil
        )
    }

    func resolvedPersonB(store: AppStore) -> Profile? {
        guard useSavedProfileForPersonB, let id = selectedPersonBProfileId else { return nil }
        return store.profiles.first(where: { $0.id == id })
    }
    
    func resolvedPersonBName(store: AppStore) -> String {
        if let p = resolvedPersonB(store: store) { return p.name }
        return personBName
    }

    func resolvedPersonBDisplayName(store: AppStore, hideSensitive: Bool) -> String {
        guard hideSensitive else { return resolvedPersonBName(store: store) }
        if let p = resolvedPersonB(store: store) {
            return p.displayName(hideSensitive: true, role: .partner)
        }
        return PrivacyRedaction.partnerLabel
    }
    
    func resolvedPersonBDOBString(store: AppStore) -> String {
        if let p = resolvedPersonB(store: store) { return p.dateOfBirth }
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: personBDOB)
    }
    
    func resolvedPersonBPayload(store: AppStore) -> ProfilePayload {
        let hideSensitive = store.hideSensitiveDetailsEnabled
        if let p = resolvedPersonB(store: store) {
            return p.privacySafePayload(hideSensitive: hideSensitive)
        }
        if hideSensitive {
            let formatter = DateFormatter()
            formatter.dateFormat = "yyyy-MM-dd"
            return ProfilePayload(
                name: PrivacyRedaction.partnerLabel,
                dateOfBirth: formatter.string(from: personBDOB),
                timeOfBirth: personBTime.map {
                    let timeFormatter = DateFormatter()
                    timeFormatter.dateFormat = "HH:mm"
                    return timeFormatter.string(from: $0)
                },
                latitude: nil,
                longitude: nil,
                timezone: nil
            )
        }
        return buildManualPersonB()
    }
    
    // MARK: - Computed Properties
    
    var hasData: Bool {
        compatibilityData != nil
    }
    
    func canCalculate(store: AppStore) -> Bool {
        if store.activeProfile == nil { return false }
        if useSavedProfileForPersonB {
            return resolvedPersonB(store: store) != nil
        }
        return !personBName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
    
    var overallScore: Double {
        compatibilityData?.displayScore ?? 0
    }

    /// Confidence score 50–100. Reduced when birth times are missing.
    var confidenceScore: Double {
        compatibilityData?.dataConfidence?.score ?? 100
    }

    /// Explanation of why confidence may be reduced, nil if full data
    var confidenceNote: String? {
        compatibilityData?.dataConfidence?.note
    }
    
    var categories: [CompatibilityCategory] {
        compatibilityData?.categories ?? []
    }
    
    var advice: [String] {
        compatibilityData?.advice ?? []
    }
    
    var strengths: [String] {
        compatibilityData?.strengths ?? []
    }
    
    var challenges: [String] {
        compatibilityData?.challenges ?? []
    }
    
    func reset() {
        compatibilityData = nil
        error = nil
        personBName = ""
        personBDOB = Date()
        personBTime = nil
        personBPlace = ""
        useSavedProfileForPersonB = false
        selectedPersonBProfileId = nil
    }
}
