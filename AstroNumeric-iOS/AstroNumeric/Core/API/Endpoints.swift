// Endpoints.swift
// Type-safe API endpoint definitions

import Foundation

enum HTTPMethod: String {
    case GET
    case POST
    case PUT
    case DELETE
    case PATCH
}

struct Endpoint {
    let path: String
    let method: HTTPMethod
    let body: (any Encodable)?
    let queryItems: [URLQueryItem]
    let isCacheable: Bool
    let cacheTTL: TimeInterval
    /// Optional override for the cache key (e.g. to scope by month/year).
    let explicitCacheKey: String?
    
    init(
        path: String,
        method: HTTPMethod = .GET,
        body: (any Encodable)? = nil,
        queryItems: [URLQueryItem] = [],
        isCacheable: Bool = false,
        cacheTTL: TimeInterval = 300, // 5 minutes default
        cacheKey: String? = nil
    ) {
        self.path = path
        self.method = method
        self.body = body
        self.queryItems = queryItems
        self.isCacheable = isCacheable
        self.cacheTTL = cacheTTL
        self.explicitCacheKey = cacheKey
    }
}

// MARK: - Auth Endpoints


// MARK: - Auth Endpoints (removed in local-first pivot)

// MARK: - Profile Endpoints

extension Endpoint {
    static var profiles: Endpoint {
        // FastAPI route is defined at "/v2/profiles/" (trailing slash).
        Endpoint(path: "/v2/profiles/", isCacheable: true, cacheTTL: 120)
    }
    
    static func profile(id: Int) -> Endpoint {
        Endpoint(path: "/v2/profiles/\(id)", isCacheable: true, cacheTTL: 300)
    }
    
    static func createProfile(_ profile: CreateProfileRequest) -> Endpoint {
        // FastAPI route is defined at "/v2/profiles/" (trailing slash).
        Endpoint(path: "/v2/profiles/", method: .POST, body: profile)
    }
    
    static func updateProfile(id: Int, _ profile: UpdateProfileRequest) -> Endpoint {
        Endpoint(path: "/v2/profiles/\(id)", method: .PUT, body: profile)
    }
    
    static func deleteProfile(id: Int) -> Endpoint {
        Endpoint(path: "/v2/profiles/\(id)", method: .DELETE)
    }
}

// MARK: - Daily Do's & Don'ts + Morning Brief

extension Endpoint {
    /// Daily Do's and Don'ts — personalized by transits, numerology, and moon phase
    static func dailyDoDont(profile: ProfilePayload) -> Endpoint {
        let today = Date().formattedDateISO8601(timeZoneId: profile.timezone)
        return Endpoint(
            path: "/v2/daily/do-dont",
            method: .POST,
            body: profile,
            isCacheable: true,
            cacheTTL: 3600,
            cacheKey: "do-dont-\(profile.name)-\(profile.dateOfBirth)-\(today)"
        )
    }

    /// 3-bullet morning brief — ideal for widgets and push notifications
    static func morningBrief(profile: ProfilePayload) -> Endpoint {
        let today = Date().formattedDateISO8601(timeZoneId: profile.timezone)
        return Endpoint(
            path: "/v2/daily/brief",
            method: .POST,
            body: profile,
            isCacheable: true,
            cacheTTL: 3600,
            cacheKey: "brief-\(profile.name)-\(profile.dateOfBirth)-\(today)"
        )
    }
}

// MARK: - Friends (Social Chart Comparison)

extension Endpoint {
    static func listFriends(ownerId: String) -> Endpoint {
        Endpoint(path: "/v2/friends/list/\(ownerId)", method: .GET, isCacheable: true, cacheTTL: 300)
    }

    static func addFriend(ownerId: String, friend: FriendProfile) -> Endpoint {
        struct AddBody: Encodable {
            let owner_id: String
            let friend: FriendProfile
        }
        return Endpoint(path: "/v2/friends/add", method: .POST, body: AddBody(owner_id: ownerId, friend: friend))
    }

    static func compareAllFriends(ownerId: String, profile: ProfilePayload) -> Endpoint {
        struct CompareAllBody: Encodable {
            let owner_id: String
            let owner_profile: ProfilePayload
        }
        let today = ISO8601DateFormatter().string(from: Date()).prefix(10)
        return Endpoint(
            path: "/v2/friends/compare-all",
            method: .POST,
            body: CompareAllBody(owner_id: ownerId, owner_profile: profile),
            isCacheable: true,
            cacheTTL: 3600,
            cacheKey: "friends-compare-\(ownerId)-\(profile.name)-\(profile.dateOfBirth)-\(today)"
        )
    }
}

// MARK: - Life Phase

extension Endpoint {
    static func lifePhase(profile: ProfilePayload) -> Endpoint {
        Endpoint(
            path: "/v2/year-ahead/life-phase",
            method: .POST,
            body: profile,
            isCacheable: true,
            cacheTTL: 86400,  // 24 hours — life phases don't change daily
            cacheKey: "life-phase-\(profile.name)-\(profile.dateOfBirth)"
        )
    }
}

// MARK: - Core Numerology (Chaldean / Pythagorean)

extension Endpoint {
    /// Calculate core numbers with system selection (pythagorean or chaldean).
    static func coreNumerology(profile: ProfilePayload, method: String = "pythagorean") -> Endpoint {
        struct Body: Encodable {
            let profile: ProfilePayload
            let method: String
        }
        return Endpoint(
            path: "/v2/numerology/core",
            method: .POST,
            body: Body(profile: profile, method: method),
            isCacheable: true,
            cacheTTL: 86400,
            cacheKey: "numerology-core-\(profile.name)-\(profile.dateOfBirth)-\(method)"
        )
    }
}

// MARK: - Reading Endpoints (v2 API)

extension Endpoint {
    /// Fetch forecast using profile ID (for saved profiles that exist on server)
    static func forecast(profileId: Int, scope: ReadingScope, date: Date? = nil) -> Endpoint {
        let dateString = date?.formattedDateISO8601()
        let cal = Calendar.current
        // Scope cache keys to the relevant time window so stale data is never served
        let scopeKey: String
        switch scope {
        case .daily:
            let d = date ?? Date()
            scopeKey = d.formattedDateISO8601()
        case .weekly:
            let weekOfYear = cal.component(.weekOfYear, from: date ?? Date())
            let year = cal.component(.year, from: date ?? Date())
            scopeKey = "\(year)-W\(weekOfYear)"
        case .monthly:
            let month = cal.component(.month, from: date ?? Date())
            let year = cal.component(.year, from: date ?? Date())
            scopeKey = "\(year)-\(month)"
        }
        return Endpoint(
            path: "/v2/forecasts/\(scope.rawValue)",
            method: .POST,
            body: ForecastByIdRequest(profileId: profileId, scope: scope.rawValue, date: dateString),
            isCacheable: true,
            cacheTTL: scope == .daily ? 3600 : 7200,
            cacheKey: "forecast-\(profileId)-\(scope.rawValue)-\(scopeKey)"
        )
    }
    
    /// Fetch forecast using full profile data (for session/guest profiles)
    static func reading(profile: Profile, scope: ReadingScope, date: Date? = nil) -> Endpoint {
        let dateString = date?.formattedDateISO8601(timeZoneId: profile.timezone)
        let cal = Calendar.current
        let toneKey = AppStore.shared.readingTone.rawValue
        let scopeKey: String
        switch scope {
        case .daily:
            let d = date ?? Date()
            scopeKey = d.formattedDateISO8601()
        case .weekly:
            let weekOfYear = cal.component(.weekOfYear, from: date ?? Date())
            let year = cal.component(.year, from: date ?? Date())
            scopeKey = "\(year)-W\(weekOfYear)"
        case .monthly:
            let month = cal.component(.month, from: date ?? Date())
            let year = cal.component(.year, from: date ?? Date())
            scopeKey = "\(year)-\(month)"
        }
        return Endpoint(
            path: "/v2/forecasts/\(scope.rawValue)",
            method: .POST,
            body: V2ForecastRequest(profile: profile, scope: scope.rawValue, date: dateString),
            isCacheable: true,
            cacheTTL: scope == .daily ? 3600 : 7200,
            cacheKey: "reading-\(profile.id)-\(scope.rawValue)-\(scopeKey)-\(toneKey)"
        )
    }
}

// Helper for date formatting
private extension Date {
    func formattedDateISO8601() -> String {
        formattedDateISO8601(timeZone: TimeZone(identifier: "UTC")!)
    }

    func formattedDateISO8601(timeZoneId: String?) -> String {
        let tz = TimeZone(identifier: timeZoneId ?? "") ?? TimeZone(identifier: "UTC")!
        return formattedDateISO8601(timeZone: tz)
    }

    func formattedDateISO8601(timeZone: TimeZone) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        formatter.timeZone = timeZone
        return formatter.string(from: self)
    }
}

// MARK: - Numerology Endpoints (v2 API)

extension Endpoint {
    /// Get numerology analysis for a profile (v2 API)
    static func numerologyProfile(profile: Profile, method: String = "pythagorean") -> Endpoint {
        let cal = Calendar.current
        let month = cal.component(.month, from: Date())
        let year  = cal.component(.year,  from: Date())
        return Endpoint(
            path: "/v2/numerology/profile",
            method: .POST,
            body: V2NumerologyRequest(profile: profile, method: method),
            isCacheable: true,
            cacheTTL: 3600,
            cacheKey: "numerology-profile-\(profile.id)-\(year)-\(month)-\(method)"
        )
    }
    
    /// Get numerology analysis with name and DOB only
    static func numerology(name: String, dateOfBirth: String, method: String = "pythagorean") -> Endpoint {
        let cal = Calendar.current
        let month = cal.component(.month, from: Date())
        let year  = cal.component(.year,  from: Date())
        return Endpoint(
            path: "/v2/numerology/profile",
            method: .POST,
            body: V2NumerologyRequest(name: name, dateOfBirth: dateOfBirth, method: method),
            isCacheable: true,
            cacheTTL: 3600,
            cacheKey: "numerology-\(name)-\(dateOfBirth)-\(year)-\(month)-\(method)"
        )
    }
    
    /// Numerology compatibility between two people
    static func numerologyCompatibility(profile1: Profile, profile2: Profile) -> Endpoint {
        let year = Calendar.current.component(.year, from: Date())
        return Endpoint(
            path: "/v2/numerology/compatibility",
            method: .POST,
            body: NumerologyCompatibilityRequest(profile1: profile1, profile2: profile2),
            isCacheable: true,
            cacheTTL: 86400,
            cacheKey: "numcompat-\(profile1.id)-\(profile2.id)-\(year)"
        )
    }
}

// MARK: - AI Endpoints (v2 API)

extension Endpoint {
    /// Chat with cosmic guide AI (v2 path)
    static func cosmicGuideChat(message: String, sunSign: String?, moonSign: String?, risingSign: String?, history: [ChatMessage]?, systemPrompt: String? = nil, tone: String? = nil) -> Endpoint {
        Endpoint(
            path: "/v2/cosmic-guide/chat",
            method: .POST,
            body: V2CosmicGuideChatRequest(
                message: message,
                sunSign: sunSign,
                moonSign: moonSign,
                risingSign: risingSign,
                birthTimeAssumed: nil,
                timeConfidence: nil,
                history: history,
                systemPrompt: systemPrompt,
                tone: tone
            )
        )
    }

    /// Chat with context, system prompt, and tone
    static func cosmicGuideChat(message: String, context: ChatContext, systemPrompt: String? = nil, tone: String? = nil) -> Endpoint {
        Endpoint(
            path: "/v2/cosmic-guide/chat",
            method: .POST,
            body: V2CosmicGuideChatRequest(
                message: message,
                sunSign: context.sunSign,
                moonSign: context.moonSign,
                risingSign: context.risingSign,
                birthTimeAssumed: context.birthTimeAssumed,
                timeConfidence: context.timeConfidence,
                history: context.history,
                systemPrompt: systemPrompt,
                tone: tone
            )
        )
    }
    
    /// AI explanation for reading summary
    static func aiExplain(reading: AIExplainRequest) -> Endpoint {
        // Scope cache key to date + headline so each day's explanation is distinct
        // and the same reading on the same day is served from cache.
        let today = ISO8601DateFormatter().string(from: Date()).prefix(10)
        let contentKey = (reading.headline ?? reading.theme ?? "general")
            .prefix(40)
            .replacingOccurrences(of: " ", with: "-")
        return Endpoint(
            path: "/v2/ai/explain",
            method: .POST,
            body: reading,
            isCacheable: true,
            cacheTTL: 86400, // 24 h — refreshes daily
            cacheKey: "ai-explain-\(today)-\(contentKey)"
        )
    }
}

// MARK: - Compatibility Endpoints

extension Endpoint {
    static func compatibility(profile1: Profile, profile2: Profile) -> Endpoint {
        Endpoint(
            path: "/v2/compatibility/romantic",
            method: .POST,
            body: CompatibilityRequest(personA: profile1, personB: profile2, relationshipType: "romantic"),
            isCacheable: true,
            cacheTTL: 3600
        )
    }
}

// MARK: - Chart Endpoints

extension Endpoint {
    static func natalChart(profile: Profile) -> Endpoint {
        Endpoint(
            path: "/v2/charts/natal",
            method: .POST,
            body: NatalChartRequest(profile: profile),
            isCacheable: true,
            cacheTTL: 86400
        )
    }

    static func progressedChart(profile: Profile, targetDate: Date? = nil) -> Endpoint {
        let dateString = targetDate?.formattedDateISO8601()
        return Endpoint(
            path: "/v2/charts/progressed",
            method: .POST,
            body: ProgressedChartRequest(profile: profile, targetDate: dateString),
            isCacheable: true,
            cacheTTL: 86400
        )
    }

    static func compositeChart(personA: Profile, personB: ProfilePayload) -> Endpoint {
        Endpoint(
            path: "/v2/charts/composite",
            method: .POST,
            body: CompositeChartRequest(personA: personA, personB: personB),
            isCacheable: true,
            cacheTTL: 86400
        )
    }
    
    static func synastryChart(personA: Profile, personB: ProfilePayload) -> Endpoint {
        Endpoint(
            path: "/v2/charts/synastry",
            method: .POST,
            body: SynastryChartRequest(personA: personA, personB: personB),
            isCacheable: true,
            cacheTTL: 86400
        )
    }
    
    static func romanticCompatibility(personA: Profile, personB: ProfilePayload) -> Endpoint {
        let year = Calendar.current.component(.year, from: Date())
        return Endpoint(
            path: "/v2/compatibility/romantic",
            method: .POST,
            body: RomanticCompatibilityRequest(personA: personA, personB: personB),
            isCacheable: true,
            cacheTTL: 86400,
            cacheKey: "romantic-compat-\(personA.id)-\(year)"
        )
    }
}

// MARK: - Timing Endpoints

extension Endpoint {
    static func timingAdvice(activity: String, profile: Profile?) -> Endpoint {
        Endpoint(
            path: "/v2/timing/advice",
            method: .POST,
            body: TimingRequest(activity: activity, profile: profile),
            isCacheable: true,
            cacheTTL: 1800
        )
    }
    
    static func bestDays(activity: String, daysAhead: Int) -> Endpoint {
        Endpoint(
            path: "/v2/timing/best-days",
            method: .POST,
            body: BestDaysRequest(activity: activity, daysAhead: daysAhead),
            isCacheable: true,
            cacheTTL: 3600
        )
    }
    
    static var timingActivities: Endpoint {
        Endpoint(path: "/v2/timing/activities", isCacheable: true, cacheTTL: 86400)
    }
    
    /// Get daily cosmic features (affirmation, lucky numbers, colors, power hours)
    static func dailyFeatures(profile: Profile, date: Date? = nil) -> Endpoint {
        var payload = profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
        payload.date = date?.formattedDateISO8601(timeZoneId: profile.timezone)
        let dayKey = (date ?? Date()).formattedDateISO8601(timeZoneId: profile.timezone)
        return Endpoint(
            path: "/v2/daily/reading",
            method: .POST,
            body: payload,
            isCacheable: true,
            cacheTTL: 3600,
            cacheKey: "daily-features-\(profile.id)-\(dayKey)"
        )
    }
}

// MARK: - Habit Endpoints

extension Endpoint {
    /// List habits
    static var habitsList: Endpoint {
        Endpoint(path: "/v2/habits/list", isCacheable: true, cacheTTL: 60)
    }

    /// Create a new habit
    static func createHabit(_ habit: CreateHabitRequest) -> Endpoint {
        Endpoint(
            path: "/v2/habits/create",
            method: .POST,
            body: habit
        )
    }
    
    /// Get habit by ID
    static func habit(id: Int) -> Endpoint {
        Endpoint(path: "/v2/habits/habit/\(id)", isCacheable: true, cacheTTL: 300)
    }
    
    /// Log habit completion
    static func logHabitEntry(habitId: Int, completed: Bool, note: String?) -> Endpoint {
        Endpoint(
            path: "/v2/habits/log-entry",
            method: .POST,
            body: HabitLogRequest(habitId: habitId, completed: completed, note: note)
        )
    }
}

// MARK: - Moon Endpoints

extension Endpoint {
    static var currentMoon: Endpoint {
        Endpoint(path: "/v2/moon/phase", isCacheable: true, cacheTTL: 3600)
    }
    
    static func moonRitual(profile: Profile?) -> Endpoint {
        Endpoint(
            path: "/v2/moon/ritual",
            method: .POST,
            body: MoonRitualRequest(
                profile: profile.map { $0.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled) }
            ),
            isCacheable: true,
            cacheTTL: 3600
        )
    }
}

// MARK: - Learning Endpoints

extension Endpoint {
    static var learningModules: Endpoint {
        Endpoint(path: "/v2/learning/modules", isCacheable: true, cacheTTL: 86400)
    }
    
    static func learningModulesByCategory(_ category: String) -> Endpoint {
        Endpoint(
            path: "/v2/learning/modules",
            queryItems: [URLQueryItem(name: "category", value: category)],
            isCacheable: true,
            cacheTTL: 86400
        )
    }
    
    static func learningModule(id: String) -> Endpoint {
        Endpoint(path: "/v2/learning/module/\(id)", isCacheable: true, cacheTTL: 86400)
    }
    
    static func zodiacGuidance(sign: String) -> Endpoint {
        Endpoint(path: "/v2/learning/zodiac/\(sign)", isCacheable: true, cacheTTL: 3600)
    }
    
    static var glossary: Endpoint {
        Endpoint(path: "/v2/learning/glossary", isCacheable: true, cacheTTL: 86400)
    }
}

// MARK: - System Endpoints

extension Endpoint {
    static var health: Endpoint {
        Endpoint(path: "/health")
    }
}

// MARK: - Daily Features Endpoints

extension Endpoint {
    /// Weekly forecast with 7-day energy timeline
    static func weeklyForecast(profile: Profile) -> Endpoint {
        Endpoint(
            path: "/v2/daily/forecast",
            method: .POST,
            body: profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled),
            isCacheable: true,
            cacheTTL: 3600  // Cache for 1 hour
        )
    }
    
    static func dailyTarot(question: String? = nil) -> Endpoint {
        // Date-scoped key so yesterday's card is never served after midnight.
        let today = ISO8601DateFormatter().string(from: Date()).prefix(10)
        return Endpoint(
            path: "/v2/daily/tarot",
            method: .POST,
            queryItems: question.map { [URLQueryItem(name: "question", value: $0)] } ?? [],
            isCacheable: true,
            cacheTTL: 3600, // 1h — expires well before end of day
            cacheKey: "tarot-\(today)-\(question ?? "daily")"
        )
    }
    
    static func dailyYesNo(question: String, profile: Profile) -> Endpoint {
        Endpoint(
            path: "/v2/daily/yes-no",
            method: .POST,
            body: profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled),
            queryItems: [URLQueryItem(name: "question", value: question)]
        )
    }
    
    static func dailyAffirmation(profile: Profile) -> Endpoint {
        // POST with profile body so the backend can personalize by element and life path.
        let cal = Calendar.current
        let month = cal.component(.month, from: Date())
        let year  = cal.component(.year,  from: Date())
        return Endpoint(
            path: "/v2/daily/affirmation",
            method: .POST,
            body: profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled),
            isCacheable: true,
            cacheTTL: 3600, // 1h — content changes daily
            cacheKey: "affirmation-\(profile.id)-\(year)-\(month)"
        )
    }
}

// MARK: - Journal Endpoints

extension Endpoint {
    /// Create or update a journal entry
    static func journalEntry(body: JournalEntryRequest) -> Endpoint {
        Endpoint(path: "/v2/journal/entry", method: .POST, body: body)
    }
    
    /// Get journal prompts
    static var journalPrompts: Endpoint {
        Endpoint(path: "/v2/journal/prompts", isCacheable: true, cacheTTL: 3600)
    }
    
    /// Get saved readings for a profile
    static func journalReadings(profileId: Int) -> Endpoint {
        Endpoint(path: "/v2/journal/readings/\(profileId)", isCacheable: true, cacheTTL: 300)
    }
    
    /// Get a specific reading from journal
    static func journalReading(readingId: String) -> Endpoint {
        Endpoint(path: "/v2/journal/reading/\(readingId)", isCacheable: true, cacheTTL: 300)
    }
    
    /// Get journal stats for a profile
    static func journalStats(profileId: Int) -> Endpoint {
        Endpoint(path: "/v2/journal/stats/\(profileId)", isCacheable: true, cacheTTL: 300)
    }
    
    /// Get journal patterns analysis
    static func journalPatterns(profileId: Int) -> Endpoint {
        Endpoint(path: "/v2/journal/patterns/\(profileId)", isCacheable: true, cacheTTL: 3600)
    }
    
    /// Generate journal report
    static func journalReport(body: JournalReportRequest) -> Endpoint {
        Endpoint(path: "/v2/journal/report", method: .POST, body: body)
    }
    
    /// Record prediction outcome
    static func journalOutcome(body: JournalOutcomeRequest) -> Endpoint {
        Endpoint(path: "/v2/journal/outcome", method: .POST, body: body)
    }
}

// MARK: - Relationships Endpoints

extension Endpoint {
    /// Get Venus status for relationship timing
    static var venusStatus: Endpoint {
        Endpoint(path: "/v2/relationships/venus-status", isCacheable: true, cacheTTL: 3600)
    }
    
    /// Get relationship phases calendar
    static var relationshipPhases: Endpoint {
        Endpoint(path: "/v2/relationships/phases", isCacheable: true, cacheTTL: 3600)
    }
    
    /// Get relationship timing advice
    static func relationshipTiming(sunSign: String, partnerSign: String?, date: Date? = nil) -> Endpoint {
        Endpoint(
            path: "/v2/relationships/timing",
            method: .POST,
            body: RelationshipTimingRequest(
                sunSign: sunSign,
                partnerSign: partnerSign,
                date: date?.formattedDateISO8601()
            ),
            isCacheable: true,
            cacheTTL: 3600
        )
    }
    
    /// Get upcoming relationship events
    static var relationshipEvents: Endpoint {
        Endpoint(path: "/v2/relationships/events", isCacheable: true, cacheTTL: 3600)
    }
    
    /// Get relationship timeline
    static func relationshipTimeline(sunSign: String, partnerSign: String?, monthsAhead: Int = 6) -> Endpoint {
        Endpoint(
            path: "/v2/relationships/timeline",
            method: .POST,
            body: RelationshipTimelineRequest(
                sunSign: sunSign,
                partnerSign: partnerSign,
                monthsAhead: monthsAhead
            ),
            isCacheable: true,
            cacheTTL: 3600
        )
    }
    
    /// Get best days for romance for a sun sign
    static func relationshipBestDays(sunSign: String) -> Endpoint {
        let today = Calendar.current.startOfDay(for: Date())
        let dateStr = ISO8601DateFormatter().string(from: today).prefix(10)
        return Endpoint(
            path: "/v2/relationships/best-days/\(sunSign)",
            isCacheable: true,
            cacheTTL: 3600,
            cacheKey: "rel-best-days-\(sunSign)-\(dateStr)"
        )
    }
    
    /// Friendship compatibility
    static func friendshipCompatibility(personA: Profile, personB: ProfilePayload) -> Endpoint {
        let year = Calendar.current.component(.year, from: Date())
        return Endpoint(
            path: "/v2/compatibility/friendship",
            method: .POST,
            body: FriendshipCompatibilityRequest(personA: personA, personB: personB),
            isCacheable: true,
            cacheTTL: 86400,
            cacheKey: "friendship-compat-\(personA.id)-\(year)"
        )
    }
}

// MARK: - Transits Endpoints

extension Endpoint {
    /// Get daily transits
    static func dailyTransits(profile: Profile) -> Endpoint {
        Endpoint(
            path: "/v2/transits/daily",
            method: .POST,
            body: TransitRequest(
                profile: profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled)
            ),
            isCacheable: true,
            cacheTTL: 3600
        )
    }
    
    /// Subscribe to transit alerts
    static func subscribeToTransits(body: TransitSubscribeRequest) -> Endpoint {
        Endpoint(path: "/v2/transits/subscribe", method: .POST, body: body)
    }
}

// MARK: - Sky/Planets Endpoints

extension Endpoint {
    /// Get current planetary positions
    static var skyPlanets: Endpoint {
        Endpoint(path: "/v2/sky/planets", isCacheable: true, cacheTTL: 3600)
    }
}

// MARK: - Year Ahead Endpoints

extension Endpoint {
    /// Get year ahead forecast
    static func yearAheadForecast(profile: Profile, year: Int? = nil) -> Endpoint {
        let targetYear = year ?? Calendar.current.component(.year, from: Date())
        return Endpoint(
            path: "/v2/year-ahead/forecast",
            method: .POST,
            body: YearAheadRequest(
                profile: profile.privacySafePayload(hideSensitive: AppStore.shared.hideSensitiveDetailsEnabled),
                year: year
            ),
            isCacheable: true,
            cacheTTL: 86400,
            cacheKey: "year-ahead-\(profile.id)-\(targetYear)"
        )
    }
}

// MARK: - Extended Moon Endpoints

extension Endpoint {
    /// Get upcoming moon events
    static var upcomingMoonEvents: Endpoint {
        Endpoint(path: "/v2/moon/upcoming", isCacheable: true, cacheTTL: 3600)
    }
}

// MARK: - Extended AI Endpoints

extension Endpoint {
    /// Get cosmic guidance (v2)
    static func cosmicGuidance(body: CosmicGuidanceRequest) -> Endpoint {
        Endpoint(path: "/v2/cosmic-guide/guidance", method: .POST, body: body)
    }
    
    /// Interpret chart/reading (v2)
    static func cosmicInterpret(body: CosmicInterpretRequest) -> Endpoint {
        Endpoint(path: "/v2/cosmic-guide/interpret", method: .POST, body: body)
    }
}

// MARK: - Feedback Endpoints

extension Endpoint {
    /// Submit section feedback
    static func sectionFeedback(body: SectionFeedbackRequest) -> Endpoint {
        Endpoint(path: "/v2/feedback/section", method: .POST, body: body)
    }
}

// MARK: - Alerts Preferences Endpoints

extension Endpoint {
    static var alertPreferences: Endpoint {
        Endpoint(path: "/v2/alerts/preferences", method: .GET, isCacheable: true, cacheTTL: 300)
    }
    
    static func updateAlertPreferences(_ prefs: AlertPreferencesRequest) -> Endpoint {
        Endpoint(path: "/v2/alerts/preferences", method: .POST, body: prefs)
    }
}

// MARK: - Profile Natal Endpoints

extension Endpoint {
    /// Get natal chart data for profiles
    static var profilesNatal: Endpoint {
        Endpoint(path: "/v2/profiles/natal", isCacheable: true, cacheTTL: 300)
    }
    
    /// Get natal chart for specific profile
    static func profileNatal(profileId: Int) -> Endpoint {
        Endpoint(path: "/v2/profiles/natal/\(profileId)", isCacheable: true, cacheTTL: 300)
    }
}
