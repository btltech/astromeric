// ProfileModels.swift
// User profile and related request/response models

import Foundation

// MARK: - Data Quality

/// Describes how complete a profile's birth data is.
/// Drives reading depth, feature gating, and UI warnings.
enum DataQuality: String, Codable {
    case full          // date + exact time + place
    case dateAndPlace  // date + place, no time (noon assumed)
    case dateOnly      // date only, no place or time

    var label: String {
        switch self {
        case .full:         return "Full Data"
        case .dateAndPlace: return "No Birth Time"
        case .dateOnly:     return "Date Only"
        }
    }

    var description: String {
        switch self {
        case .full:
            return "Your chart is calculated from your exact birth time and place."
        case .dateAndPlace:
            return "Rising sign and houses are estimated — birth time unknown (noon used)."
        case .dateOnly:
            return "Only your Sun sign is reliable — birth place and time unknown."
        }
    }
}

// MARK: - Profile

struct Profile: Codable, Identifiable, Equatable, Hashable {
    let id: Int
    let name: String
    let dateOfBirth: String
    let timeOfBirth: String?
    let timeConfidence: String?
    let placeOfBirth: String?
    let latitude: Double?
    let longitude: Double?
    let timezone: String?
    let houseSystem: String?

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case dateOfBirth = "date_of_birth"
        case timeOfBirth = "time_of_birth"
        case timeConfidence = "time_confidence"
        case placeOfBirth = "place_of_birth"
        case latitude
        case longitude
        case timezone
        case houseSystem = "house_system"
    }

    /// Computed data quality tier based on available birth data
    var dataQuality: DataQuality {
        let hasLocation = latitude != nil && longitude != nil
        let tc = timeConfidence ?? "unknown"
        let hasTime = timeOfBirth != nil && !(timeOfBirth?.isEmpty ?? true) && tc == "exact"
        if hasLocation && hasTime { return .full }
        if hasLocation { return .dateAndPlace }
        return .dateOnly
    }
}

struct ProfilesResponse: Codable {
    let profiles: [Profile]
}

struct CreateProfileRequest: Encodable {
    let name: String
    let dateOfBirth: String
    let timeOfBirth: String?
    let timeConfidence: String?
    let placeOfBirth: String?
    let latitude: Double?
    let longitude: Double?
    let timezone: String?
    let saveProfile: Bool
    
    enum CodingKeys: String, CodingKey {
        case name
        case dateOfBirth = "date_of_birth"
        case timeOfBirth = "time_of_birth"
        case timeConfidence = "time_confidence"
        case placeOfBirth = "place_of_birth"
        case latitude
        case longitude
        case timezone
        case saveProfile = "save_profile"
    }
}

struct UpdateProfileRequest: Encodable {
    let name: String?
    let timeOfBirth: String?
    let timeConfidence: String?
    let placeOfBirth: String?
    let latitude: Double?
    let longitude: Double?
    let timezone: String?
    let houseSystem: String?
    
    enum CodingKeys: String, CodingKey {
        case name
        case timeOfBirth = "time_of_birth"
        case timeConfidence = "time_confidence"
        case placeOfBirth = "place_of_birth"
        case latitude
        case longitude
        case timezone
        case houseSystem = "house_system"
    }
}

/// Profile payload matching backend's ProfilePayload schema
struct ProfilePayload: Codable {
    let name: String
    let dateOfBirth: String
    let timeOfBirth: String?
    let placeOfBirth: String?
    let latitude: Double?
    let longitude: Double?
    let timezone: String?
    let houseSystem: String?
    var date: String?

    init(
        name: String,
        dateOfBirth: String,
        timeOfBirth: String?,
        placeOfBirth: String? = nil,
        latitude: Double?,
        longitude: Double?,
        timezone: String?,
        houseSystem: String? = nil,
        date: String? = nil
    ) {
        self.name = name
        self.dateOfBirth = dateOfBirth
        self.timeOfBirth = timeOfBirth
        self.placeOfBirth = placeOfBirth
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.houseSystem = houseSystem
        self.date = date
    }
    
    enum CodingKeys: String, CodingKey {
        case name
        case dateOfBirth = "date_of_birth"
        case timeOfBirth = "time_of_birth"
        case placeOfBirth = "place_of_birth"
        case latitude
        case longitude
        case timezone
        case houseSystem = "house_system"
        case date
    }
}

/// Shareable profile data for comparison links
struct ShareableProfile: Codable {
    let name: String
    let dob: String  // date of birth
    let tob: String? // time of birth
    let lat: Double?
    let lng: Double?
    let tz: String?
    
    /// Create from Profile
    init(from profile: Profile) {
        self.name = profile.name
        self.dob = profile.dateOfBirth
        self.tob = profile.timeOfBirth
        self.lat = profile.latitude
        self.lng = profile.longitude
        self.tz = profile.timezone
    }
    
    /// Encode to base64 URL-safe string
    func encode() -> String? {
        guard let data = try? JSONEncoder().encode(self) else { return nil }
        return data.base64EncodedString()
            .replacingOccurrences(of: "+", with: "-")
            .replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: "=", with: "")
    }
    
    /// Decode from base64 URL-safe string
    static func decode(from string: String) -> ShareableProfile? {
        var base64 = string
            .replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")
        
        // Add padding if needed
        while base64.count % 4 != 0 {
            base64 += "="
        }
        
        guard let data = Data(base64Encoded: base64),
              let profile = try? JSONDecoder().decode(ShareableProfile.self, from: data) else {
            return nil
        }
        return profile
    }
}

// MARK: - Location

struct LocationData: Codable {
    let latitude: Double
    let longitude: Double
    let timezone: String
}

// NatalProfileData for backwards compatibility
struct NatalProfileData: Encodable {
    let name: String
    let dateOfBirth: String
    let timeOfBirth: String?
    let latitude: Double
    let longitude: Double
    let timezone: String
    let houseSystem: String
    
    enum CodingKeys: String, CodingKey {
        case name
        case dateOfBirth = "date_of_birth"
        case timeOfBirth = "time_of_birth"
        case latitude
        case longitude
        case timezone
        case houseSystem = "house_system"
    }
}
