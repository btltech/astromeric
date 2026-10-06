// AdvancedChartModels.swift
// Solar arc, relocation, lunar return, profections, declinations, fixed stars.
// Shapes mirror backend/app/routers/charts.py. Every response field is optional
// or defaulted so one missing key never hides the whole chart.

import Foundation

extension Date {
    /// The calendar day the person picked, in their own time zone, as yyyy-MM-dd.
    var localISODay: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = .current
        return formatter.string(from: self)
    }
}

// MARK: - Requests

struct SolarArcRequest: Encodable {
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

struct RelocationRequest: Encodable {
    let profile: ProfilePayload
    let newLatitude: Double
    let newLongitude: Double
    let newTimezone: String?

    init(profile: Profile, latitude: Double, longitude: Double, timezone: String?) {
        self.profile = profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        self.newLatitude = latitude
        self.newLongitude = longitude
        self.newTimezone = timezone
    }

    enum CodingKeys: String, CodingKey {
        case profile
        case newLatitude = "new_latitude"
        case newLongitude = "new_longitude"
        case newTimezone = "new_timezone"
    }
}

struct LunarReturnRequest: Encodable {
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

struct ProfectionsRequest: Encodable {
    let profile: ProfilePayload
    let refDate: String?

    init(profile: Profile, refDate: String?) {
        self.profile = profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        self.refDate = refDate
    }

    enum CodingKeys: String, CodingKey {
        case profile
        case refDate = "ref_date"
    }
}

struct DeclinationsRequest: Encodable {
    let profile: ProfilePayload

    init(profile: Profile) {
        self.profile = profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
    }
}

struct FixedStarPlanetInput: Encodable {
    let name: String
    let absoluteDegree: Double

    enum CodingKeys: String, CodingKey {
        case name
        case absoluteDegree = "absolute_degree"
    }
}

struct FixedStarsRequest: Encodable {
    let planets: [FixedStarPlanetInput]
    let orb: Double
}

// MARK: - Responses

/// A chart cast for another moment or place (solar arc, relocation, lunar return).
struct AdvancedChartResponse: Decodable {
    let planets: [AdvancedChartPlanet]
    let aspects: [AdvancedChartAspect]
    let metadata: AdvancedChartMetadata?

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        planets = (try? c.decode([AdvancedChartPlanet].self, forKey: .planets)) ?? []
        aspects = (try? c.decode([AdvancedChartAspect].self, forKey: .aspects)) ?? []
        metadata = try? c.decode(AdvancedChartMetadata.self, forKey: .metadata)
    }

    enum CodingKeys: String, CodingKey { case planets, aspects, metadata }
}

struct AdvancedChartPlanet: Decodable, Identifiable {
    var id: String { name }
    let name: String
    let sign: String
    let degree: Double
    let house: Int?
    let retrograde: Bool?
    let natalDegree: Double?

    enum CodingKeys: String, CodingKey {
        case name, sign, degree, house, retrograde
        case natalDegree = "natal_degree"
    }
}

struct AdvancedChartAspect: Decodable, Identifiable {
    var id: String { "\(planetA)-\(planetB)-\(type)" }
    let planetA: String
    let planetB: String
    let type: String
    let orb: Double?

    enum CodingKeys: String, CodingKey {
        case planetA = "planet_a"
        case planetB = "planet_b"
        case type, orb
    }
}

struct AdvancedChartMetadata: Decodable {
    let directedTo: String?
    let solarArcDegrees: Double?
    let ageYears: Double?
    let returnLocal: String?
    let natalMoonSign: String?
    let natalMoonDegree: Double?

    enum CodingKeys: String, CodingKey {
        case directedTo = "directed_to"
        case solarArcDegrees = "solar_arc_degrees"
        case ageYears = "age_years"
        case returnLocal = "return_datetime_local"
        case natalMoon = "natal_moon"
    }

    enum MoonKeys: String, CodingKey { case sign, degree }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        directedTo = try? c.decode(String.self, forKey: .directedTo)
        solarArcDegrees = try? c.decode(Double.self, forKey: .solarArcDegrees)
        ageYears = try? c.decode(Double.self, forKey: .ageYears)
        returnLocal = try? c.decode(String.self, forKey: .returnLocal)
        if let moon = try? c.nestedContainer(keyedBy: MoonKeys.self, forKey: .natalMoon) {
            natalMoonSign = try? moon.decode(String.self, forKey: .sign)
            natalMoonDegree = try? moon.decode(Double.self, forKey: .degree)
        } else {
            natalMoonSign = nil
            natalMoonDegree = nil
        }
    }
}

struct ProfectionsResponse: Decodable {
    let age: Int
    let ascendantSign: String?
    let annualHouse: Int
    let annualSign: String?
    let annualLord: String?
    let annualFocus: String
    let annualLordThemes: String
    let monthlyHouse: Int
    let monthlySign: String?
    let monthlyLord: String?
    let monthlyFocus: String
    let interpretation: String

    enum CodingKeys: String, CodingKey {
        case age, interpretation
        case ascendantSign = "ascendant_sign"
        case annualHouse = "annual_house"
        case annualSign = "annual_sign"
        case annualLord = "annual_lord"
        case annualFocus = "annual_focus"
        case annualLordThemes = "annual_lord_themes"
        case monthlyHouse = "monthly_house"
        case monthlySign = "monthly_sign"
        case monthlyLord = "monthly_lord"
        case monthlyFocus = "monthly_focus"
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        age = (try? c.decode(Int.self, forKey: .age)) ?? 0
        ascendantSign = try? c.decode(String.self, forKey: .ascendantSign)
        annualHouse = (try? c.decode(Int.self, forKey: .annualHouse)) ?? 0
        annualSign = try? c.decode(String.self, forKey: .annualSign)
        annualLord = try? c.decode(String.self, forKey: .annualLord)
        annualFocus = (try? c.decode(String.self, forKey: .annualFocus)) ?? ""
        annualLordThemes = (try? c.decode(String.self, forKey: .annualLordThemes)) ?? ""
        monthlyHouse = (try? c.decode(Int.self, forKey: .monthlyHouse)) ?? 0
        monthlySign = try? c.decode(String.self, forKey: .monthlySign)
        monthlyLord = try? c.decode(String.self, forKey: .monthlyLord)
        monthlyFocus = (try? c.decode(String.self, forKey: .monthlyFocus)) ?? ""
        interpretation = (try? c.decode(String.self, forKey: .interpretation)) ?? ""
    }
}

struct DeclinationsResponse: Decodable {
    let declinations: [DeclinationEntry]
    let parallels: [DeclinationParallel]
    let note: String?

    enum CodingKeys: String, CodingKey { case declinations, parallels, note }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        declinations = (try? c.decode([DeclinationEntry].self, forKey: .declinations)) ?? []
        parallels = (try? c.decode([DeclinationParallel].self, forKey: .parallels)) ?? []
        note = try? c.decode(String.self, forKey: .note)
    }
}

struct DeclinationEntry: Decodable, Identifiable {
    var id: String { name }
    let name: String
    let declination: Double
    let outOfBounds: Bool

    enum CodingKeys: String, CodingKey {
        case name, declination
        case outOfBounds = "out_of_bounds"
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        name = (try? c.decode(String.self, forKey: .name)) ?? ""
        declination = (try? c.decode(Double.self, forKey: .declination)) ?? 0
        outOfBounds = (try? c.decode(Bool.self, forKey: .outOfBounds)) ?? false
    }
}

struct DeclinationParallel: Decodable, Identifiable {
    var id: String { "\(planetA)-\(planetB)-\(type)" }
    let planetA: String
    let planetB: String
    let type: String
    let orb: Double

    enum CodingKeys: String, CodingKey {
        case planetA = "planet_a"
        case planetB = "planet_b"
        case type, orb
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        planetA = (try? c.decode(String.self, forKey: .planetA)) ?? ""
        planetB = (try? c.decode(String.self, forKey: .planetB)) ?? ""
        type = (try? c.decode(String.self, forKey: .type)) ?? ""
        orb = (try? c.decode(Double.self, forKey: .orb)) ?? 0
    }
}

struct FixedStarConjunction: Decodable, Identifiable {
    var id: String { "\(planet)-\(star)" }
    let planet: String
    let star: String
    let orb: Double
    let nature: String
    let keywords: String
    let interpretation: String

    enum CodingKeys: String, CodingKey { case planet, star, orb, nature, keywords, interpretation }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        planet = (try? c.decode(String.self, forKey: .planet)) ?? ""
        star = (try? c.decode(String.self, forKey: .star)) ?? ""
        orb = (try? c.decode(Double.self, forKey: .orb)) ?? 0
        nature = (try? c.decode(String.self, forKey: .nature)) ?? ""
        keywords = (try? c.decode(String.self, forKey: .keywords)) ?? ""
        interpretation = (try? c.decode(String.self, forKey: .interpretation)) ?? ""
    }
}

// MARK: - Endpoints

extension Endpoint {
    static func solarArcChart(profile: Profile, targetDate: Date?) -> Endpoint {
        Endpoint(
            path: "/v2/charts/solar-arc",
            method: .POST,
            body: SolarArcRequest(profile: profile, targetDate: targetDate?.localISODay),
            isCacheable: true,
            cacheTTL: 86400
        )
    }

    static func relocationChart(profile: Profile, latitude: Double, longitude: Double, timezone: String?) -> Endpoint {
        Endpoint(
            path: "/v2/charts/relocation",
            method: .POST,
            body: RelocationRequest(profile: profile, latitude: latitude, longitude: longitude, timezone: timezone),
            isCacheable: true,
            cacheTTL: 86400
        )
    }

    static func lunarReturnChart(profile: Profile, targetDate: Date?) -> Endpoint {
        Endpoint(
            path: "/v2/charts/lunar-return",
            method: .POST,
            body: LunarReturnRequest(profile: profile, targetDate: targetDate?.localISODay),
            isCacheable: true,
            cacheTTL: 3600
        )
    }

    static func profections(profile: Profile, refDate: Date?) -> Endpoint {
        Endpoint(
            path: "/v2/charts/profections",
            method: .POST,
            body: ProfectionsRequest(profile: profile, refDate: refDate?.localISODay),
            isCacheable: true,
            cacheTTL: 86400
        )
    }

    static func declinations(profile: Profile) -> Endpoint {
        Endpoint(
            path: "/v2/charts/declinations",
            method: .POST,
            body: DeclinationsRequest(profile: profile),
            isCacheable: true,
            cacheTTL: 86400
        )
    }

    static func fixedStars(planets: [FixedStarPlanetInput], orb: Double = 1.0) -> Endpoint {
        Endpoint(
            path: "/v2/charts/fixed-stars",
            method: .POST,
            body: FixedStarsRequest(planets: planets, orb: orb),
            isCacheable: true,
            cacheTTL: 86400
        )
    }
}
