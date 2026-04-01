// DataQualityEngine.swift
// Central rule engine that determines which features are available
// based on how complete a profile's birth data is.

import SwiftUI

// MARK: - Feature Gate

enum GatedFeature {
    case risingSign
    case houseDetails
    case solarReturn
    case secondaryProgressions
    case synastryChart
    case compositeChart
    case timingAdvisor
    case temporalMatrix

    var requiredQuality: DataQuality {
        switch self {
        case .risingSign, .houseDetails:
            return .dateAndPlace
        case .solarReturn, .secondaryProgressions,
             .synastryChart, .compositeChart,
             .timingAdvisor, .temporalMatrix:
            return .full
        }
    }

    var missingDataHint: String {
        switch requiredQuality {
        case .full:
            return "Add your exact birth time and place to unlock this feature."
        case .dateAndPlace:
            return "Add your birth place to unlock this feature."
        case .dateOnly:
            return ""
        }
    }
}

// MARK: - Data Quality Engine

struct DataQualityEngine {

    let quality: DataQuality

    init(profile: Profile?) {
        self.quality = profile?.dataQuality ?? .dateOnly
    }

    /// Returns true if the feature is available for this profile's data quality
    func isAvailable(_ feature: GatedFeature) -> Bool {
        qualityRank(quality) >= qualityRank(feature.requiredQuality)
    }

    /// Returns a hint message when a feature is locked, nil when available
    func lockReason(for feature: GatedFeature) -> String? {
        isAvailable(feature) ? nil : feature.missingDataHint
    }

    private func qualityRank(_ q: DataQuality) -> Int {
        switch q {
        case .dateOnly:     return 0
        case .dateAndPlace: return 1
        case .full:         return 2
        }
    }
}

// MARK: - SwiftUI View Modifier

struct DataQualityGate: ViewModifier {
    let feature: GatedFeature
    let engine: DataQualityEngine

    func body(content: Content) -> some View {
        if engine.isAvailable(feature) {
            content
        } else {
            LockedFeatureView(hint: feature.missingDataHint)
        }
    }
}

extension View {
    func gated(by feature: GatedFeature, engine: DataQualityEngine) -> some View {
        modifier(DataQualityGate(feature: feature, engine: engine))
    }
}

// MARK: - Locked Feature Placeholder

struct LockedFeatureView: View {
    let hint: String

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "lock.circle")
                .font(.largeTitle)
                .foregroundStyle(.secondary)
            Text("More Data Needed")
                .font(.headline)
            Text(hint)
                .font(.caption)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }
}
