// ChartModels.swift
// Astrological chart models (natal, transit, progressed, composite)

import Foundation

// MARK: - Charts Data

struct ChartsData: Codable {
    let natal: NatalChart?
}

struct NatalChart: Codable {
    let planets: [PlanetPlacement]?
    let houses: [HousePlacement]?
    let aspects: [Aspect]?
}

struct PlanetPlacement: Codable, Identifiable {
    var id: String { name }
    let name: String
    let sign: String
    let degree: Double
    let absoluteDegree: Double?
    let house: Int?
    let retrograde: Bool?
    let dignity: String?
    
    enum CodingKeys: String, CodingKey {
        case name, sign, degree, house, retrograde, dignity
        case absoluteDegree = "absolute_degree"
    }
}

struct ChartPoint: Codable, Identifiable {
    var id: String { name }
    let name: String
    let sign: String
    let degree: Double
    let absoluteDegree: Double?
    let house: Int?
    let retrograde: Bool?
    let chartType: String?   // "day" or "night" (Part of Fortune only)

    enum CodingKeys: String, CodingKey {
        case name, sign, degree, house, retrograde
        case absoluteDegree = "absolute_degree"
        case chartType = "chart_type"
    }
}

struct HousePlacement: Codable, Identifiable {
    var id: Int { house }
    let house: Int
    let sign: String
    let degree: Double?
}

struct Aspect: Codable, Identifiable {
    var id: String { "\(planet1)-\(planet2)-\(aspect)" }
    let planet1: String
    let planet2: String
    let aspect: String
    let orb: Double?
}

// MARK: - Chart Requests

struct NatalChartRequest: Encodable {
    let profile: ProfilePayload
    let lang: String
    
    init(profile: Profile) {
        self.profile = profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        self.lang = "en"
    }
}

struct ProgressedChartRequest: Encodable {
    let profile: ProfilePayload
    let targetDate: String?
    
    init(profile: Profile, targetDate: String?) {
        self.profile = profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        self.targetDate = targetDate
    }
    
    enum CodingKeys: String, CodingKey {
        case profile
        case targetDate = "target_date"
    }
}

struct CompositeChartRequest: Encodable {
    let personA: ProfilePayload
    let personB: ProfilePayload
    
    init(personA: Profile, personB: ProfilePayload) {
        self.personA = personA.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        self.personB = personB
    }
    
    enum CodingKeys: String, CodingKey {
        case personA = "person_a"
        case personB = "person_b"
    }
}

struct SynastryChartRequest: Encodable {
    let personA: NatalProfileData
    let personB: ProfilePayload
    
    init(personA: Profile, personB: ProfilePayload) {
        self.personA = NatalProfileData(
            name: AppStore.shared.hideSensitiveDetailsEnabled ? PrivacyRedaction.privateUser : personA.name,
            dateOfBirth: personA.dateOfBirth,
            timeOfBirth: personA.timeOfBirth,
            latitude: personA.latitude ?? 0,
            longitude: personA.longitude ?? 0,
            timezone: personA.timezone ?? "UTC",
            houseSystem: personA.houseSystem ?? "Placidus"
        )
        self.personB = personB
    }
    
    enum CodingKeys: String, CodingKey {
        case personA = "person_a"
        case personB = "person_b"
    }
}

// MARK: - Chart Data (v2 API)

struct ChartData: Codable {
    let planets: [PlanetPlacement]
    let points: [ChartPoint]?
    let houses: [HousePlacement]?
    let aspects: [ChartAspect]?
    let metadata: ChartMetadata?
}

struct ChartAspect: Codable, Hashable {
    let planet1: String
    let planet2: String
    let aspectType: String
    let orb: Double?
    let strength: Double?
    
    enum CodingKeys: String, CodingKey {
        case planet1 = "planet_a"
        case planet2 = "planet_b"
        case aspectType = "type"
        case orb
        case strength
    }
}

struct ChartMetadata: Codable {
    let chartType: String?
    let datetime: String?
    let houseSystem: String?
    let provider: String?
    let birthTimeAssumed: Bool?
    let moonSignUncertain: Bool?
    let dataQuality: String?
    let timeConfidence: String?
    
    enum CodingKeys: String, CodingKey {
        case chartType = "chart_type"
        case datetime
        case houseSystem = "house_system"
        case provider
        case birthTimeAssumed = "birth_time_assumed"
        case moonSignUncertain = "moon_sign_uncertain"
        case dataQuality = "data_quality"
        case timeConfidence = "time_confidence"
    }
}

// MARK: - Transit Models

struct TransitSubscribeRequest: Encodable {
    let profileId: Int
    let transitTypes: [String]
    let notificationPreferences: NotificationPrefs?
    
    enum CodingKeys: String, CodingKey {
        case profileId = "profile_id"
        case transitTypes = "transit_types"
        case notificationPreferences = "notification_preferences"
    }
    
    struct NotificationPrefs: Encodable {
        let push: Bool
        let email: Bool
    }
}

struct TransitRequest: Encodable {
    let profile: ProfilePayload
}
