// EphemerisEngine.swift
// Actor-based Swiss Ephemeris wrapper for offline natal chart calculations.
// Thread-safe: all C-library calls serialized through this actor.

import Foundation

actor EphemerisEngine {
    static let shared = EphemerisEngine()

    private var isInitialized = false
    private nonisolated static let requiredEphemerisFiles = [
        "seas_18.se1",
        "semo_18.se1",
        "sepl_18.se1",
    ]

    // MARK: - Transit Cache (5-min TTL)
    // Planets move slowly — no need to call the C library more than once per 5 minutes.
    private var cachedTransits: [PlanetPlacement]?
    private var cachedTransitsTimestamp: Date?
    private let transitCacheTTL: TimeInterval = 300 // 5 minutes

    // MARK: - Planet Definitions

    /// Planets to calculate (Swiss Ephemeris IDs)
    private static let planets: [(id: Int32, name: String)] = [
        (SE_SUN,       "Sun"),
        (SE_MOON,      "Moon"),
        (SE_MERCURY,   "Mercury"),
        (SE_VENUS,     "Venus"),
        (SE_MARS,      "Mars"),
        (SE_JUPITER,   "Jupiter"),
        (SE_SATURN,    "Saturn"),
        (SE_URANUS,    "Uranus"),
        (SE_NEPTUNE,   "Neptune"),
        (SE_PLUTO,     "Pluto"),
    ]

    /// Sensitive points to calculate locally for parity with the backend chart API.
    private static let chartPoints: [(id: Int32, name: String)] = [
        (SE_MEAN_NODE, "North Node"),
        (SE_CHIRON,    "Chiron"),
    ]

    /// Zodiac signs in order (0° Aries = index 0)
    private static let signs = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    /// House system codes for swe_houses()
    private static let houseSystemCodes: [String: Int32] = [
        "Placidus":      Int32(Character("P").asciiValue!),
        "Koch":          Int32(Character("K").asciiValue!),
        "Equal":         Int32(Character("E").asciiValue!),
        "Whole Sign":    Int32(Character("W").asciiValue!),
        "Campanus":      Int32(Character("C").asciiValue!),
        "Regiomontanus": Int32(Character("R").asciiValue!),
    ]

    /// Traditional + modern essential dignities. Mirrors backend chart_service.py.
    private static let dignities: [String: [String: String]] = [
        "Sun": ["Leo": "domicile", "Aries": "exaltation", "Aquarius": "detriment", "Libra": "fall"],
        "Moon": ["Cancer": "domicile", "Taurus": "exaltation", "Capricorn": "detriment", "Scorpio": "fall"],
        "Mercury": ["Gemini": "domicile", "Virgo": "domicile", "Sagittarius": "detriment", "Pisces": "fall"],
        "Venus": ["Taurus": "domicile", "Libra": "domicile", "Pisces": "exaltation", "Aries": "detriment", "Scorpio": "detriment", "Virgo": "fall"],
        "Mars": ["Aries": "domicile", "Scorpio": "domicile", "Capricorn": "exaltation", "Taurus": "detriment", "Libra": "detriment", "Cancer": "fall"],
        "Jupiter": ["Sagittarius": "domicile", "Pisces": "domicile", "Cancer": "exaltation", "Gemini": "detriment", "Virgo": "detriment", "Capricorn": "fall"],
        "Saturn": ["Capricorn": "domicile", "Aquarius": "domicile", "Libra": "exaltation", "Cancer": "detriment", "Leo": "detriment", "Aries": "fall"],
        "Uranus": ["Aquarius": "domicile"],
        "Neptune": ["Pisces": "domicile"],
        "Pluto": ["Scorpio": "domicile"],
    ]

    // MARK: - Initialization

    private init() {}

    private final class BundleMarker {}

    /// Initialize the Swiss Ephemeris with the correct data file path.
    /// CRITICAL: Must be called before any calculations.
    private func ensureInitialized() {
        guard !isInitialized else { return }

        if let ephemerisDirectory = Self.resolveEphemerisDirectory() {
            swe_set_ephe_path(ephemerisDirectory.path)
            DebugLog.trace("[Ephemeris] Using data path: \(ephemerisDirectory.path)")
        } else if let resourcePath = Bundle.main.resourcePath {
            // Best-effort fallback so the engine still attempts bundled resources.
            swe_set_ephe_path(resourcePath)
            DebugLog.trace("[Ephemeris] Falling back to Bundle.main.resourcePath: \(resourcePath)")
        } else {
            DebugLog.log("[Ephemeris] No ephemeris resource path found")
        }

        isInitialized = true
    }

    private nonisolated static func resolveEphemerisDirectory() -> URL? {
        let fileManager = FileManager.default

        func hasRequiredFiles(at directory: URL) -> Bool {
            requiredEphemerisFiles.allSatisfy { file in
                fileManager.fileExists(atPath: directory.appendingPathComponent(file).path)
            }
        }

        var seen = Set<String>()
        var candidates: [URL] = []

        func addCandidate(_ url: URL?) {
            guard let url else { return }
            let standardized = url.standardizedFileURL
            let path = standardized.path
            guard !path.isEmpty, seen.insert(path).inserted else { return }
            candidates.append(standardized)
        }

        let bundles = [Bundle.main, Bundle(for: BundleMarker.self)] + Bundle.allBundles + Bundle.allFrameworks
        for bundle in bundles {
            let roots = [bundle.resourceURL, bundle.bundleURL].compactMap { $0 }
            for root in roots {
                addCandidate(root)
                addCandidate(root.appendingPathComponent("Ephemeris", isDirectory: true))
                addCandidate(root.appendingPathComponent("Resources", isDirectory: true))
                addCandidate(root.appendingPathComponent("Resources/Ephemeris", isDirectory: true))

                let parent = root.deletingLastPathComponent()
                addCandidate(parent)
                addCandidate(parent.appendingPathComponent("Ephemeris", isDirectory: true))
                addCandidate(parent.appendingPathComponent("Resources/Ephemeris", isDirectory: true))
            }
        }

        if let envPath = ProcessInfo.processInfo.environment["EPHEMERIS_PATH"], !envPath.isEmpty {
            addCandidate(URL(fileURLWithPath: envPath, isDirectory: true))
        }

        for candidate in candidates where hasRequiredFiles(at: candidate) {
            return candidate
        }

        for bundle in bundles {
            guard let resourceURL = bundle.resourceURL else { continue }
            let enumerator = fileManager.enumerator(
                at: resourceURL,
                includingPropertiesForKeys: [.isDirectoryKey],
                options: [.skipsHiddenFiles]
            )

            while let url = enumerator?.nextObject() as? URL {
                let relative = url.path.replacingOccurrences(of: resourceURL.path, with: "")
                let depth = relative.split(separator: "/").count
                if depth > 4 {
                    enumerator?.skipDescendants()
                    continue
                }

                guard hasRequiredFiles(at: url) else { continue }
                return url
            }
        }

        return nil
    }

    // MARK: - Public API

    /// Calculate a complete natal chart for a profile.
    /// Returns the same ChartData structure the API returns.
    func calculateNatalChart(profile: Profile) throws -> ChartData {
        ensureInitialized()

        guard let lat = profile.latitude, let lon = profile.longitude else {
            throw EphemerisError.missingLocation
        }

        guard let tz = profile.timezone, !tz.isEmpty else {
            throw EphemerisError.missingTimezone
        }

        // Parse birth date
        let dateParts = profile.dateOfBirth.split(separator: "-").compactMap { Int($0) }
        guard dateParts.count == 3 else {
            throw EphemerisError.invalidDate
        }
        let year = dateParts[0]
        let month = dateParts[1]
        let day = dateParts[2]

        // Convert local birth date/time to UTC correctly, preserving date rollovers.
        let birthUTC = try birthUTCComponents(
            year: year,
            month: month,
            day: day,
            timeString: profile.timeOfBirth,
            timezone: tz
        )

        // Calculate Julian Day using UTC components.
        let jd = swe_julday(
            Int32(birthUTC.year),
            Int32(birthUTC.month),
            Int32(birthUTC.day),
            birthUTC.hour,
            SE_GREG_CAL
        )

        // Calculate planet positions
        let planets = calculatePlanets(julianDay: jd)

        // Calculate houses
        let houseSystem = profile.houseSystem ?? "Placidus"
        let houses = calculateHouses(julianDay: jd, latitude: lat, longitude: lon, system: houseSystem)
        let planetPlacements = assignHouses(to: planets, using: houses)

        // Calculate ascendant from ascmc[0] (exact Ascendant degree)
        // and Midheaven from ascmc[1] — NOT from cusps array
        var allPlanets = planetPlacements
        let ascDegree = calculateAscendant(julianDayUT: jd, latitude: lat, longitude: lon, houseSystem: houseSystem)
        let ascSign = Self.signs[Int(ascDegree / 30.0) % 12]
        allPlanets.append(PlanetPlacement(
            name: "Ascendant",
            sign: ascSign,
            degree: ascDegree.truncatingRemainder(dividingBy: 30.0),
            absoluteDegree: ascDegree,
            house: 1,
            retrograde: false,
            dignity: nil
        ))

        let mcDegree = calculateMidheaven(julianDayUT: jd, latitude: lat, longitude: lon, houseSystem: houseSystem)
        let mcSign = Self.signs[Int(mcDegree / 30.0) % 12]
        allPlanets.append(PlanetPlacement(
            name: "Midheaven",
            sign: mcSign,
            degree: mcDegree.truncatingRemainder(dividingBy: 30.0),
            absoluteDegree: mcDegree,
            house: 10,
            retrograde: false,
            dignity: nil
        ))

        // Calculate chart points with the same shape as the backend API.
        let points = calculatePoints(
            julianDay: jd,
            houses: houses,
            ascDegree: ascDegree,
            planets: planetPlacements
        )

        // Calculate aspects
        let aspects = calculateAspects(planets: allPlanets)

        return ChartData(
            planets: allPlanets,
            points: points,
            houses: houses,
            aspects: aspects,
            metadata: ChartMetadata(
                chartType: "natal",
                datetime: "\(profile.dateOfBirth)T\(profile.timeOfBirth ?? "12:00:00")",
                houseSystem: houseSystem,
                provider: "SwissEphemeris-Local",
                birthTimeAssumed: profile.timeConfidence.map { $0 != "exact" } ?? true,
                moonSignUncertain: moonChangesSignOnDate(profile: profile),
                dataQuality: metadataDataQuality(for: profile.dataQuality),
                timeConfidence: profile.timeConfidence
            )
        )
    }

    /// Calculate current planetary positions (for transit tracking).
    /// Results are cached for 5 minutes when using the default (now) date.
    func calculateCurrentTransits(date: Date = Date()) throws -> [PlanetPlacement] {
        // Return cached result if within TTL (only for "now" requests)
        let isNowRequest = abs(date.timeIntervalSinceNow) < 60  // within 1 min of now
        if isNowRequest,
           let cached = cachedTransits,
           let timestamp = cachedTransitsTimestamp,
           Date().timeIntervalSince(timestamp) < transitCacheTTL {
            return cached
        }

        ensureInitialized()

        let calendar = Calendar.current
        let components = calendar.dateComponents(in: TimeZone(identifier: "UTC")!, from: date)

        guard let year = components.year, let month = components.month, let day = components.day else {
            throw EphemerisError.invalidDate
        }

        let hour = Double(components.hour ?? 0) + Double(components.minute ?? 0) / 60.0
        let jd = swe_julday(Int32(year), Int32(month), Int32(day), hour, SE_GREG_CAL)

        let result = calculatePlanets(julianDay: jd)

        // Cache only "now" requests
        if isNowRequest {
            cachedTransits = result
            cachedTransitsTimestamp = Date()
        }

        return result
    }

    /// Get the moon sign and rising sign for a profile (used by AppStore cache).
    func getNatalSigns(for profile: Profile) throws -> (moonSign: String?, risingSign: String?) {
        let chart = try calculateNatalChart(profile: profile)
        let moonSign = chart.planets.first(where: { $0.name == "Moon" })?.sign
        let risingSign = chart.planets.first(where: { $0.name == "Ascendant" })?.sign
        return (moonSign, risingSign)
    }

    // MARK: - Ascendant & Midheaven (Astrological Identity)

    /// Calculates the exact degree (0.0 to 359.99) of the Ascendant (Rising Sign).
    /// Uses ascmc[0] from swe_houses — the mathematically correct Ascendant,
    /// NOT the first house cusp approximation.
    func calculateAscendant(julianDayUT: Double, latitude: Double, longitude: Double, houseSystem: String = "Placidus") -> Double {
        let hsys = Self.houseSystemCodes[houseSystem] ?? Int32(Character("P").asciiValue!)
        var cusps = [Double](repeating: 0.0, count: 13)
        var ascmc = [Double](repeating: 0.0, count: 10)
        swe_houses(julianDayUT, latitude, longitude, hsys, &cusps, &ascmc)
        return ascmc[0] // ascmc[0] = exact Ascendant degree
    }

    /// Calculates the exact degree (0.0 to 359.99) of the Midheaven (MC).
    func calculateMidheaven(julianDayUT: Double, latitude: Double, longitude: Double, houseSystem: String = "Placidus") -> Double {
        let hsys = Self.houseSystemCodes[houseSystem] ?? Int32(Character("P").asciiValue!)
        var cusps = [Double](repeating: 0.0, count: 13)
        var ascmc = [Double](repeating: 0.0, count: 10)
        swe_houses(julianDayUT, latitude, longitude, hsys, &cusps, &ascmc)
        return ascmc[1] // ascmc[1] = exact Midheaven degree
    }

    // MARK: - Generic Horizon Crossing (Astronomical Clock)

    /// Calculates the exact UTC timestamp when any celestial body crosses the local horizon.
    /// - Parameters:
    ///   - planet: Swiss Ephemeris planet ID (0=Sun, 1=Moon, 2=Mercury, etc.)
    ///   - isRising: true for rise, false for set
    ///   - latitude/longitude: Observer's geographic coordinates
    ///   - date: The day to calculate for
    /// - Returns: The exact moment as a Date, or nil for circumpolar cases
    func calculateRiseSet(planet: Int32, isRising: Bool, latitude: Double, longitude: Double, date: Date = Date()) throws -> Date? {
        ensureInitialized()

        let calendar = Calendar.current
        let components = calendar.dateComponents(in: TimeZone(identifier: "UTC")!, from: date)
        let year = Int32(components.year ?? 2026)
        let month = Int32(components.month ?? 1)
        let day = Int32(components.day ?? 1)
        let hour = Double(components.hour ?? 12)

        let jd = swe_julday(year, month, day, hour, SE_GREG_CAL)

        var geopos: [Double] = [longitude, latitude, 0.0]
        var tret: Double = 0
        var serr = [CChar](repeating: 0, count: 256)

        let riseOrSet: Int32 = isRising ? (SE_CALC_RISE | SE_BIT_DISC_CENTER) : (SE_CALC_SET | SE_BIT_DISC_CENTER)

        let result = swe_rise_trans(
            jd - 0.5,       // search from midnight
            planet,
            nil,             // not a fixed star
            SEFLG_SWIEPH,
            riseOrSet,
            &geopos,
            1013.25,         // standard atmospheric pressure (mbar)
            15.0,            // standard temperature (°C)
            &tret,
            &serr
        )

        // -1 = error (e.g., circumpolar — body doesn't rise/set that day)
        if result == -1 {
            return nil
        }

        return julianDayToDate(tret)
    }

    // MARK: - Moonrise / Moonset

    struct LunarTimes {
        let moonrise: Date?
        let moonset: Date?
    }

    /// Calculate moonrise and moonset for a given location and date.
    /// Either value may be nil in circumpolar regions.
    func calculateMoonriseMoonset(latitude: Double, longitude: Double, date: Date = Date()) throws -> LunarTimes {
        let rise = try calculateRiseSet(planet: SE_MOON, isRising: true, latitude: latitude, longitude: longitude, date: date)
        let set = try calculateRiseSet(planet: SE_MOON, isRising: false, latitude: latitude, longitude: longitude, date: date)
        return LunarTimes(moonrise: rise, moonset: set)
    }

    // MARK: - Sunrise / Sunset

    struct SolarTimes {
        let sunrise: Date
        let sunset: Date
        /// Duration of daylight in minutes
        var daylightMinutes: Double {
            sunset.timeIntervalSince(sunrise) / 60.0
        }
        /// Duration of nighttime in minutes (from sunset to next sunrise)
        var nighttimeMinutes: Double {
            1440.0 - daylightMinutes
        }
    }

    /// Calculate true sunrise and sunset for a given location and date using swe_rise_trans().
    func calculateSunriseSunset(latitude: Double, longitude: Double, date: Date = Date()) throws -> SolarTimes {
        ensureInitialized()

        let calendar = Calendar.current
        let components = calendar.dateComponents(in: TimeZone(identifier: "UTC")!, from: date)
        let year = Int32(components.year ?? 2026)
        let month = Int32(components.month ?? 1)
        let day = Int32(components.day ?? 1)
        let hour = Double(components.hour ?? 12)

        let jd = swe_julday(year, month, day, hour, SE_GREG_CAL)

        // geopos: [longitude, latitude, altitude]
        var geopos: [Double] = [longitude, latitude, 0]
        var trise: Double = 0
        var tset: Double = 0
        var serr = [CChar](repeating: 0, count: 256)

        // Calculate sunrise
        let riseResult = swe_rise_trans(
            jd - 0.5,                    // search from midnight
            SE_SUN,                       // Sun
            nil,                          // not a star
            SEFLG_SWIEPH,                 // ephemeris flag
            SE_CALC_RISE | SE_BIT_DISC_CENTER,  // sunrise of disc center
            &geopos,
            1013.25,                      // standard atmospheric pressure (mbar)
            15.0,                         // standard temperature (°C)
            &trise,
            &serr
        )

        guard riseResult >= 0 else {
            throw EphemerisError.calculationFailed("Sunrise calculation failed")
        }

        // Calculate sunset
        let setResult = swe_rise_trans(
            jd - 0.5,
            SE_SUN,
            nil,
            SEFLG_SWIEPH,
            SE_CALC_SET | SE_BIT_DISC_CENTER,
            &geopos,
            1013.25,
            15.0,
            &tset,
            &serr
        )

        guard setResult >= 0 else {
            throw EphemerisError.calculationFailed("Sunset calculation failed")
        }

        // Convert Julian days back to Date
        let sunriseDate = julianDayToDate(trise)
        let sunsetDate = julianDayToDate(tset)

        return SolarTimes(sunrise: sunriseDate, sunset: sunsetDate)
    }

    /// Convert a Julian Day (UT) to a Swift Date.
    private func julianDayToDate(_ jd: Double) -> Date {
        var year: Int32 = 0, month: Int32 = 0, day: Int32 = 0
        var hour: Double = 0
        swe_revjul(jd, SE_GREG_CAL, &year, &month, &day, &hour)

        let hrs = Int(hour)
        let mins = Int((hour - Double(hrs)) * 60)
        let secs = Int(((hour - Double(hrs)) * 60 - Double(mins)) * 60)

        var components = DateComponents()
        components.year = Int(year)
        components.month = Int(month)
        components.day = Int(day)
        components.hour = hrs
        components.minute = mins
        components.second = secs
        components.timeZone = TimeZone(identifier: "UTC")

        return Calendar.current.date(from: components) ?? Date()
    }

    // MARK: - Cleanup

    func shutdown() {
        swe_close()
        isInitialized = false
    }

    // MARK: - Private Calculations

    private func calculatePlanets(julianDay jd: Double) -> [PlanetPlacement] {
        let iflag = SEFLG_SWIEPH | SEFLG_SPEED
        var results: [PlanetPlacement] = []

        for planet in Self.planets {
            var xx = [Double](repeating: 0, count: 6)
            var serr = [CChar](repeating: 0, count: 256)

            let ret = swe_calc_ut(jd, planet.id, iflag, &xx, &serr)

            if ret >= 0 {
                let longitude = xx[0]  // ecliptic longitude in degrees
                let speed = xx[3]      // daily speed (negative = retrograde)

                let signIndex = Int(longitude / 30.0) % 12
                let degreeInSign = longitude.truncatingRemainder(dividingBy: 30.0)

                results.append(PlanetPlacement(
                    name: planet.name,
                    sign: Self.signs[signIndex],
                    degree: degreeInSign,
                    absoluteDegree: longitude,
                    house: nil, // assigned after house calculation
                    retrograde: speed < 0,
                    dignity: Self.dignities[planet.name]?[Self.signs[signIndex]]
                ))
            }
        }

        return results
    }

    private func assignHouses(to planets: [PlanetPlacement], using houses: [HousePlacement]) -> [PlanetPlacement] {
        let cusps = houses.compactMap(\ .degree)
        guard cusps.count == 12 else { return planets }

        return planets.map { planet in
            guard let longitude = planet.absoluteDegree else { return planet }
            return PlanetPlacement(
                name: planet.name,
                sign: planet.sign,
                degree: planet.degree,
                absoluteDegree: planet.absoluteDegree,
                house: houseForLongitude(longitude, houseCusps: cusps),
                retrograde: planet.retrograde,
                dignity: planet.dignity
            )
        }
    }

    private func calculatePoints(julianDay jd: Double, houses: [HousePlacement], ascDegree: Double, planets: [PlanetPlacement]) -> [ChartPoint] {
        let iflag = SEFLG_SWIEPH | SEFLG_SPEED
        let houseCusps = houses.compactMap(\ .degree)
        var points: [ChartPoint] = []

        for point in Self.chartPoints {
            var xx = [Double](repeating: 0, count: 6)
            var serr = [CChar](repeating: 0, count: 256)
            let ret = swe_calc_ut(jd, point.id, iflag, &xx, &serr)
            guard ret >= 0 else { continue }

            let longitude = xx[0]
            let signIndex = Int(longitude / 30.0) % 12
            let sign = Self.signs[signIndex]
            let degreeInSign = longitude.truncatingRemainder(dividingBy: 30.0)
            points.append(
                ChartPoint(
                    name: point.name,
                    sign: sign,
                    degree: degreeInSign,
                    absoluteDegree: longitude,
                    house: houseForLongitude(longitude, houseCusps: houseCusps),
                    retrograde: xx[3] < 0,
                    chartType: nil
                )
            )
        }

        if let northNode = points.first(where: { $0.name == "North Node" }) {
            let southLongitude = (northNode.absoluteDegree ?? 0 + 180.0).truncatingRemainder(dividingBy: 360.0)
            let signIndex = Int(southLongitude / 30.0) % 12
            points.append(
                ChartPoint(
                    name: "South Node",
                    sign: Self.signs[signIndex],
                    degree: southLongitude.truncatingRemainder(dividingBy: 30.0),
                    absoluteDegree: southLongitude,
                    house: houseForLongitude(southLongitude, houseCusps: houseCusps),
                    retrograde: northNode.retrograde,
                    chartType: nil
                )
            )
        }

        if let sun = planets.first(where: { $0.name == "Sun" })?.absoluteDegree,
           let moon = planets.first(where: { $0.name == "Moon" })?.absoluteDegree {
            let dayDelta = normalizeDegrees(sun - ascDegree)
            let isDayChart = dayDelta >= 180.0
            let normalizedLongitude = isDayChart
                ? normalizeDegrees(ascDegree + moon - sun)
                : normalizeDegrees(ascDegree + sun - moon)
            let signIndex = Int(normalizedLongitude / 30.0) % 12
            points.append(
                ChartPoint(
                    name: "Part of Fortune",
                    sign: Self.signs[signIndex],
                    degree: normalizedLongitude.truncatingRemainder(dividingBy: 30.0),
                    absoluteDegree: normalizedLongitude,
                    house: houseForLongitude(normalizedLongitude, houseCusps: houseCusps),
                    retrograde: false,
                    chartType: isDayChart ? "tern.ephemerisEngine.0a".localized : "tern.ephemerisEngine.0b".localized
                )
            )
        }

        return points
    }

    private func normalizeDegrees(_ value: Double) -> Double {
        let normalized = value.truncatingRemainder(dividingBy: 360.0)
        return normalized >= 0 ? normalized : normalized + 360.0
    }

    private func houseForLongitude(_ longitude: Double, houseCusps: [Double]) -> Int {
        guard houseCusps.count == 12 else { return 1 }
        for index in 0..<12 {
            let start = houseCusps[index]
            let end = houseCusps[(index + 1) % 12]
            if start > end {
                if longitude >= start || longitude < end {
                    return index + 1
                }
            } else if start <= longitude && longitude < end {
                return index + 1
            }
        }
        return 1
    }

    private func calculateHouses(julianDay jd: Double, latitude: Double, longitude: Double, system: String) -> [HousePlacement] {
        let hsys = Self.houseSystemCodes[system] ?? Int32(Character("P").asciiValue!)

        var cusps = [Double](repeating: 0, count: 13) // cusps[1..12]
        var ascmc = [Double](repeating: 0, count: 10) // ASC, MC, etc.

        swe_houses(jd, latitude, longitude, hsys, &cusps, &ascmc)

        var houses: [HousePlacement] = []
        for idx in 1...12 {
            let degree = cusps[idx]
            let signIndex = Int(degree / 30.0) % 12
            houses.append(HousePlacement(
                house: idx,
                sign: Self.signs[signIndex],
                degree: degree
            ))
        }

        return houses
    }

    private func calculateAspects(planets: [PlanetPlacement]) -> [ChartAspect] {
        // Major aspect definitions: name, angle, orb
        let aspectDefs: [(name: String, angle: Double, orb: Double)] = [
            ("conjunction",  0,   8),
            ("opposition",   180, 8),
            ("trine",        120, 8),
            ("square",       90,  7),
            ("sextile",      60,  6),
            ("quincunx",     150, 3),
        ]

        var aspects: [ChartAspect] = []

        for idx in 0..<planets.count {
            for jdx in (idx+1)..<planets.count {
                guard let deg1 = planets[idx].absoluteDegree,
                      let deg2 = planets[jdx].absoluteDegree else { continue }

                var diff = abs(deg1 - deg2)
                if diff > 180 { diff = 360 - diff }

                for aspect in aspectDefs {
                    let orb = abs(diff - aspect.angle)
                    if orb <= aspect.orb {
                        aspects.append(ChartAspect(
                            planet1: planets[idx].name,
                            planet2: planets[jdx].name,
                            aspectType: aspect.name,
                            orb: orb,
                            strength: 1.0 - (orb / aspect.orb) // tighter = stronger
                        ))
                        break // only one aspect per planet pair
                    }
                }
            }
        }

        return aspects
    }

    // MARK: - Timezone Helpers

    private func birthUTCComponents(year: Int, month: Int, day: Int, timeString: String?, timezone: String) throws -> (year: Int, month: Int, day: Int, hour: Double) {
        guard let timeZone = TimeZone(identifier: timezone) else {
            throw EphemerisError.missingTimezone
        }

        let timeParts = (timeString ?? "12:00:00").split(separator: ":").compactMap { Int($0) }
        let hour = timeParts.indices.contains(0) ? timeParts[0] : 12
        let minute = timeParts.indices.contains(1) ? timeParts[1] : 0
        let second = timeParts.indices.contains(2) ? timeParts[2] : 0

        var localCalendar = Calendar(identifier: .gregorian)
        localCalendar.timeZone = timeZone

        let localDate = localCalendar.date(from: DateComponents(
            timeZone: timeZone,
            year: year,
            month: month,
            day: day,
            hour: hour,
            minute: minute,
            second: second
        ))

        guard let localDate else {
            throw EphemerisError.invalidDate
        }

        var utcCalendar = Calendar(identifier: .gregorian)
        utcCalendar.timeZone = TimeZone(secondsFromGMT: 0) ?? .current
        let utc = utcCalendar.dateComponents([.year, .month, .day, .hour, .minute, .second], from: localDate)

        let utcHour = Double(utc.hour ?? 0)
            + Double(utc.minute ?? 0) / 60.0
            + Double(utc.second ?? 0) / 3600.0

        return (utc.year ?? year, utc.month ?? month, utc.day ?? day, utcHour)
    }

    private func moonChangesSignOnDate(profile: Profile) -> Bool {
        guard let tz = profile.timezone,
              let timeZone = TimeZone(identifier: tz) else { return false }

        let dateParts = profile.dateOfBirth.split(separator: "-").compactMap { Int($0) }
        guard dateParts.count == 3 else { return false }
        let year = dateParts[0]
        let month = dateParts[1]
        let day = dateParts[2]

        func moonSign(localHour: Int) -> String? {
            do {
                let utc = try birthUTCComponents(
                    year: year,
                    month: month,
                    day: day,
                    timeString: String(format: "%02d:00:00", localHour),
                    timezone: timeZone.identifier
                )
                let jd = swe_julday(Int32(utc.year), Int32(utc.month), Int32(utc.day), utc.hour, SE_GREG_CAL)
                var xx = [Double](repeating: 0, count: 6)
                var serr = [CChar](repeating: 0, count: 256)
                let ret = swe_calc_ut(jd, SE_MOON, SEFLG_SWIEPH | SEFLG_SPEED, &xx, &serr)
                guard ret >= 0 else { return nil }
                return Self.signs[Int(xx[0] / 30.0) % 12]
            } catch {
                return nil
            }
        }

        guard let startSign = moonSign(localHour: 0), let endSign = moonSign(localHour: 23) else {
            return false
        }
        return startSign != endSign
    }

    private func metadataDataQuality(for quality: DataQuality) -> String {
        switch quality {
        case .full:
            return "full"
        case .dateAndPlace:
            return "date_and_place"
        case .dateOnly:
            return "date_only"
        }
    }

    // MARK: - Solar Return

    /// Data model for a Solar Return chart.
    struct SolarReturn {
        let exactDate: Date          // the precise moment the Sun returns to natal degree
        let planets: [PlanetPlacement]
        let ascendantSign: String?
        let mcSign: String?
    }

    /// Calculate the Solar Return for the given year.
    /// Uses bisection (binary search) to find the exact Julian Day
    /// when the transiting Sun's ecliptic longitude equals the natal Sun's longitude.
    func calculateSolarReturn(profile: Profile, year: Int) throws -> SolarReturn {
        ensureInitialized()

        guard let lat = profile.latitude, let lon = profile.longitude else {
            throw EphemerisError.missingLocation
        }

        // Step 1: Get natal Sun degree
        let natalChart = try calculateNatalChart(profile: profile)
        guard let natalSun = natalChart.planets.first(where: { $0.name == "Sun" }),
              let natalDeg = natalSun.absoluteDegree else {
            throw EphemerisError.calculationFailed("Could not find natal Sun position")
        }

        // Step 2: Set up search window — the Sun's birthday ± 2 days
        let dateParts = profile.dateOfBirth.split(separator: "-").compactMap { Int($0) }
        guard dateParts.count == 3 else { throw EphemerisError.invalidDate }
        let birthMonth = dateParts[1]
        let birthDay = dateParts[2]

        // Start from (year, birthMonth, birthDay-2) — search ±2 days
        let jdStart = swe_julday(Int32(year), Int32(birthMonth), Int32(birthDay - 2), 12.0, SE_GREG_CAL)
        let jdEnd   = swe_julday(Int32(year), Int32(birthMonth), Int32(birthDay + 2), 12.0, SE_GREG_CAL)

        // Step 3: Bisection root-finding (target: sunLon == natalDeg)
        func sunLongitude(at jd: Double) -> Double {
            var xx = [Double](repeating: 0, count: 6)
            var serr = [CChar](repeating: 0, count: 256)
            swe_calc_ut(jd, SE_SUN, SEFLG_SWIEPH | SEFLG_SPEED, &xx, &serr)
            return xx[0]
        }

        /// Angular difference: positive if sunLon > natalDeg, handles 360° wrap.
        func angularDiff(_ sunLon: Double, _ target: Double) -> Double {
            var d = sunLon - target
            if d > 180  { d -= 360 }
            if d < -180 { d += 360 }
            return d
        }

        var lo = jdStart
        var hi = jdEnd

        // 30 iterations of bisection → precision < 0.1 second of time
        for _ in 0..<30 {
            let mid = (lo + hi) / 2.0
            let diff = angularDiff(sunLongitude(at: mid), natalDeg)
            if diff < 0 {
                lo = mid
            } else {
                hi = mid
            }
        }

        let jdExact = (lo + hi) / 2.0
        let exactDate = julianDayToDate(jdExact)

        // Step 4: Calculate full chart at exact Solar Return moment
        let planets = calculatePlanets(julianDay: jdExact)
        let houseSystem = profile.houseSystem ?? "Placidus"
        let ascDeg = calculateAscendant(julianDayUT: jdExact, latitude: lat, longitude: lon, houseSystem: houseSystem)
        let mcDeg  = calculateMidheaven(julianDayUT: jdExact, latitude: lat, longitude: lon, houseSystem: houseSystem)

        return SolarReturn(
            exactDate: exactDate,
            planets: planets,
            ascendantSign: Self.signs[Int(ascDeg / 30.0) % 12],
            mcSign: Self.signs[Int(mcDeg / 30.0) % 12]
        )
    }

    // MARK: - Synastry (Inter-Chart Aspects)

    /// Data model for an inter-chart aspect (person A planet → person B planet).
    struct InterChartAspect {
        let planetA: String
        let planetB: String
        let aspectType: String
        let orb: Double
        let significance: String   // "major" or "minor"
    }

    /// Calculate all inter-chart aspects between two sets of planet placements.
    /// Standard synastry: every planet in chartA checked against every planet in chartB.
    func calculateInterChartAspects(chartA: [PlanetPlacement], chartB: [PlanetPlacement]) -> [InterChartAspect] {
        let aspectDefs: [(name: String, angle: Double, orb: Double, sig: String)] = [
            ("conjunction",  0,   8, "major"),
            ("opposition",   180, 8, "major"),
            ("trine",        120, 8, "major"),
            ("square",       90,  7, "major"),
            ("sextile",      60,  6, "minor"),
            ("quincunx",     150, 3, "minor"),
        ]

        var results: [InterChartAspect] = []

        for pA in chartA {
            guard let degA = pA.absoluteDegree else { continue }
            for pB in chartB {
                guard let degB = pB.absoluteDegree else { continue }

                var diff = abs(degA - degB)
                if diff > 180 { diff = 360 - diff }

                for asp in aspectDefs {
                    let orbVal = abs(diff - asp.angle)
                    if orbVal <= asp.orb {
                        results.append(InterChartAspect(
                            planetA: pA.name,
                            planetB: pB.name,
                            aspectType: asp.name,
                            orb: orbVal,
                            significance: asp.sig
                        ))
                        break // one aspect per pair
                    }
                }
            }
        }

        return results
    }
}

// MARK: - Errors

enum EphemerisError: LocalizedError {
    case missingLocation
    case missingTimezone
    case invalidDate
    case calculationFailed(String)

    var errorDescription: String? {
        switch self {
        case .missingLocation: return "Birth location (latitude/longitude) is required for chart calculation."
        case .missingTimezone: return "Timezone is required for chart calculation."
        case .invalidDate: return "Could not parse birth date."
        case .calculationFailed(let msg): return "Ephemeris calculation failed: \(msg)"
        }
    }
}
