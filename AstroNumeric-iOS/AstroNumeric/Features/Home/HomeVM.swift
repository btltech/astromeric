// HomeVM.swift
// ViewModel for the Home dashboard

import SwiftUI

@MainActor
@Observable
final class HomeVM {
    // State
    var isLoading = false
    var errorMessage: String?
    var selectedDate: Date = Date()
    var dailyReading: DailyReadingSummary?
    var moonPhaseName: String = "Loading..."
    var moonPhaseEmoji: String = "🌙"
    var moonGuidance: String = ""
    var personalDayNumber: Int?
    var personalDayDescription: String?
    var personalYearNumber: Int?
    var personalMonthNumber: Int?
    /// Combined cycle guidance — Day overrides Year/Month tone when they conflict
    var cycleGuidance: String?
    var sunSignEmoji: String = "✨"
    var dailyAffirmation: String?
    var luckyNumbers: [Int] = []
    var luckyColor: String?
    var dailyAdvice: String?
    var habitsCompletedToday: Int = 0
    var totalHabits: Int = 0
    
    private let dailyContent: DailyContentRepository
    private let habitsRepository: HabitRepository

    init(
        dailyContent: DailyContentRepository = DefaultDailyContentRepository(),
        habitsRepository: HabitRepository = DefaultHabitRepository()
    ) {
        self.dailyContent = dailyContent
        self.habitsRepository = habitsRepository
    }
    
    // Weekly cache for Time Travel slider
    private var weeklyCache: [String: DashboardData] = [:]
    private var isCacheLoaded = false
    
    // MARK: - Load Dashboard
    
    @MainActor
    func loadDashboard(for profile: Profile?, date: Date? = nil, forceRefresh: Bool = false) async {
        guard let profile = profile else { return }
        let targetDate = date ?? Date()
        self.selectedDate = targetDate
        self.sunSignEmoji = profile.sunSignEmoji
        
        isLoading = true
        defer { isLoading = false }
        
        // Clear previous errors
        errorMessage = nil
        
        // Load in parallel
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.fetchDailyReading(for: profile, date: targetDate, forceRefresh: forceRefresh) }
            group.addTask { await self.fetchDailyFeatures(for: profile, date: targetDate, forceRefresh: forceRefresh) }
            group.addTask { await self.calculatePersonalDay(for: profile, date: targetDate) }
            group.addTask { await self.fetchMoonPhase() }
            group.addTask { await self.fetchHabitSummary(for: profile) }
        }
    }
    
    @MainActor
    private func fetchDailyReading(for profile: Profile, date: Date, forceRefresh: Bool) async {
        do {
            let cachePolicy: CachePolicy = forceRefresh ? .networkFirst : .cacheFirst
            let prediction = try await dailyContent.reading(
                profile: profile,
                scope: .daily,
                date: date,
                cachePolicy: cachePolicy
            )
            
            // Extract summary from prediction data
            dailyReading = Self.makeDailyReadingSummary(from: prediction)
        } catch {
            // Preserve the raw error for troubleshooting.
            errorMessage = "📡 Reading: \(error.localizedDescription)"
            dailyReading = DailyReadingSummary(
                headline: "⚠️ \(error.localizedDescription)",
                tldr: nil,
                overallEnergy: "Unknown"
            )
        }
    }
    
    @MainActor
    private func fetchDailyFeatures(for profile: Profile, date: Date? = nil, forceRefresh: Bool = false) async {
        do {
            let features = try await dailyContent.dailyFeatures(
                profile: profile,
                date: date,
                cachePolicy: forceRefresh ? .networkFirst : .cacheFirst
            )
            
            dailyAffirmation = features.affirmation
            luckyNumbers = features.luckyNumbers
            luckyColor = features.luckyColor
            dailyAdvice = features.advice
        } catch {
            // Set fallback values and expose error for UI feedback
            dailyAffirmation = nil
            luckyColor = nil
            dailyAdvice = nil
            errorMessage = "Some daily features unavailable. Pull to refresh."
        }
    }
    
    @MainActor
    private func fetchMoonPhase() async {
        do {
            let moon = try await dailyContent.currentMoon(cachePolicy: .cacheFirst)
            
            moonPhaseName = moon.phaseName
            moonPhaseEmoji = moon.emoji
            moonGuidance = moon.guidance ?? ""
        } catch {
            moonPhaseName = "⚠️ Failed"
            moonPhaseEmoji = "❌"
            moonGuidance = error.localizedDescription
        }
    }

    @MainActor
    private func fetchHabitSummary(for profile: Profile) async {
        do {
            let remoteHabits = try await habitsRepository.fetchHabits(cachePolicy: .cacheFirst)
            let summary = Self.habitSummary(from: remoteHabits, timezoneID: profile.timezone)
            habitsCompletedToday = summary.completed
            totalHabits = summary.total
        } catch {
            let localHabits = await habitsRepository.loadLocalHabits() ?? []
            habitsCompletedToday = localHabits.filter(\.isCompletedToday).count
            totalHabits = localHabits.count
        }
    }
    
    @MainActor
    private func calculatePersonalDay(for profile: Profile, date: Date) async {
        // Align with backend numerology cycles:
        // personal_year = reduce(birth_month + birth_day + target_year, keep_master: false)
        // personal_month = reduce(personal_year + target_month, keep_master: false)
        // personal_day = reduce(personal_month + target_day, keep_master: false)
        let parts = profile.dateOfBirth.split(separator: "-").map(String.init)
        guard parts.count == 3,
              let birthMonth = Int(parts[1]),
              let birthDay = Int(parts[2])
        else { return }

        let tz = TimeZone(identifier: profile.timezone ?? "") ?? TimeZone(identifier: "UTC")!
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = tz

        let comps = calendar.dateComponents([.year, .month, .day], from: date)
        guard let targetYear = comps.year,
              let targetMonth = comps.month,
              let targetDay = comps.day
        else { return }

        let personalYear = reduceNumber(birthMonth + birthDay + targetYear, keepMasterNumbers: false)
        let personalMonth = reduceNumber(personalYear + targetMonth, keepMasterNumbers: false)
        let personalDay = reduceNumber(personalMonth + targetDay, keepMasterNumbers: false)

        personalDayNumber = personalDay
        personalDayDescription = personalDayText(for: personalDay)
        personalYearNumber = personalYear
        personalMonthNumber = personalMonth
        cycleGuidance = Self.buildCycleGuidance(day: personalDay, month: personalMonth, year: personalYear)
    }
    
    // MARK: - Helpers
    
    func greetingText() -> String {
        let hour = Calendar.current.component(.hour, from: Date())
        if hour < 12 {
            return "Good Morning"
        } else if hour < 17 {
            return "Good Afternoon"
        } else {
            return "Good Evening"
        }
    }
    
    private func reduceNumber(_ number: Int, keepMasterNumbers: Bool) -> Int {
        var n = number
        while n > 9 && (keepMasterNumbers ? (n != 11 && n != 22 && n != 33) : true) {
            var sum = 0
            var temp = n
            while temp > 0 {
                sum += temp % 10
                temp /= 10
            }
            n = sum
        }
        return n
    }
    
    private func personalDayText(for number: Int) -> String {
        return Self.personalDayText(for: number)
    }

    /// Shorter label shown in metric tile
    static func personalDayText(for number: Int) -> String {
        let descriptions: [Int: String] = [
            1: "Start something — action pays off today",
            2: "Listen more than you speak",
            3: "Put your ideas out there",
            4: "Focus on one practical task",
            5: "Stay flexible, changes are coming",
            6: "Help someone or handle home matters",
            7: "Reflect, research, or rest — do not rush",
            8: "Execute — your effort gets rewarded",
            9: "Finish what needs finishing"
        ]
        return descriptions[number] ?? "Take things one step at a time"
    }

    /// Builds a short cycle-aware guidance sentence.
    /// Day number sets the tone; Year and Month add context without overriding.
    static func buildCycleGuidance(day: Int, month: Int, year: Int) -> String {
        let dayTone = personalDayTone(day)
        let yearContext = personalYearContext(year)
        let monthContext = personalMonthContext(month)

        // Day 7 is explicitly quiet — always lead with that, never override with active language
        if day == 7 {
            let yearNote = year == 1 ? " Your Personal Year 1 supports new beginnings, but today asks you to pause, think clearly, and refine what you have already started." : " \(yearContext)"
            return "Today is better for reflection, research, and quiet planning than rushing into action.\(yearNote)"
        }

        // Low-activity days (2, 4, 6, 9) — use supportive not pushy language
        if [2, 4, 6, 9].contains(day) {
            return "\(dayTone) \(monthContext)"
        }

        // High-activity days (1, 3, 5, 8) — can reference year context
        return "\(dayTone) \(yearContext)"
    }

    private static func personalDayTone(_ day: Int) -> String {
        switch day {
        case 1: return "Good day to start. Pick one thing and take the first real step."
        case 2: return "A cooperative day — listen, collaborate, and avoid forcing decisions."
        case 3: return "Express yourself. Share ideas, write, or have the creative conversation you have been delaying."
        case 4: return "A building day — focus on one practical task and see it through."
        case 5: return "Expect the unexpected. Stay flexible and open to what comes up."
        case 6: return "A responsibility day — attend to home, family, or someone who needs support."
        case 7: return "A reflective day — research, plan quietly, and trust your intuition."
        case 8: return "An execution day — your effort gets rewarded. Push forward on your most important goal."
        case 9: return "A completion day — close open loops, finish lingering tasks, and let go of what is no longer useful."
        default: return "Take things one step at a time today."
        }
    }

    private static func personalYearContext(_ year: Int) -> String {
        switch year {
        case 1: return "Your Personal Year 1 is still in its opening chapter — today's action plants seeds."
        case 2: return "Your Personal Year 2 rewards patience over force right now."
        case 3: return "Your Personal Year 3 favours visibility — small wins build momentum."
        case 4: return "Your Personal Year 4 asks for steady, consistent effort."
        case 5: return "Your Personal Year 5 is about change — stay adaptable."
        case 6: return "Your Personal Year 6 is centred on responsibility and repair."
        case 7: return "Your Personal Year 7 is a year for inner development — depth over breadth."
        case 8: return "Your Personal Year 8 rewards decisive moves."
        case 9: return "Your Personal Year 9 is about completion and clearing — what no longer fits can go."
        default: return ""
        }
    }

    private static func personalMonthContext(_ month: Int) -> String {
        switch month {
        case 1: return "This month opens a new cycle — a supportive window for beginnings."
        case 2: return "This month favours patience and cooperation."
        case 3: return "A creative month — expression and connection flow well now."
        case 4: return "A grounding month — steady work pays off."
        case 5: return "This month brings movement and change — stay nimble."
        case 6: return "A month for home, family, service, and stability."
        case 7: return "A quieter month — good for research, reflection, and refinement."
        case 8: return "An ambitious month — execution and results are in focus."
        case 9: return "A completion month — wrap up, release, and prepare to move forward."
        default: return ""
        }
    }
    
    // MARK: - Time Travel Cache
    
    /// Pre-fetch dashboard data for ±7 days for instant slider response
    @MainActor
    func preloadWeek(for profile: Profile) async {
        guard !isCacheLoaded else { return }

        let existingKeys = Set(weeklyCache.keys)
        let offsets = Array(-7...7)
        var utcCalendar = Calendar(identifier: .gregorian)
        utcCalendar.timeZone = TimeZone(identifier: "UTC")!
        let baseDate = Date()
        let dailyContent = self.dailyContent
        
        var fetched: [(String, DashboardData)] = []
        await withTaskGroup(of: (String, DashboardData?).self) { group in
            for offset in offsets {
                guard let date = utcCalendar.date(byAdding: .day, value: offset, to: baseDate) else { continue }
                let key = Self.cacheKey(for: date)
                guard !existingKeys.contains(key) else { continue }
                
                group.addTask {
                    let data = await Self.fetchDashboardData(dailyContent: dailyContent, profile: profile, date: date)
                    return (key, data)
                }
            }
            
            for await (key, data) in group {
                if let data {
                    fetched.append((key, data))
                }
            }
        }
        
        for (key, data) in fetched {
            weeklyCache[key] = data
        }
        
        isCacheLoaded = true
    }
    
    /// Get cached dashboard data for a specific date (used by Time Travel slider)
    @MainActor
    func getFromCache(for date: Date) -> DashboardData? {
        weeklyCache[Self.cacheKey(for: date)]
    }

    @MainActor
    func invalidateWeekCache() {
        weeklyCache.removeAll()
        isCacheLoaded = false
    }
    
    /// Apply cached data to current view state
    @MainActor
    func applyCachedData(_ data: DashboardData) {
        personalDayNumber = data.personalDayNumber
        personalDayDescription = data.personalDayDescription
        personalYearNumber = data.personalYearNumber
        personalMonthNumber = data.personalMonthNumber
        cycleGuidance = data.cycleGuidance
        dailyAffirmation = data.affirmation
        luckyNumbers = data.luckyNumbers
        luckyColor = data.luckyColor
        dailyAdvice = data.advice
        dailyReading = data.reading
        selectedDate = data.date
    }
    
    private static func cacheKey(for date: Date) -> String {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(identifier: "UTC")!
        let components = calendar.dateComponents([.year, .month, .day], from: date)
        guard let year = components.year, let month = components.month, let day = components.day else {
            return "\(date.timeIntervalSince1970)"
        }
        return String(format: "%04d-%02d-%02d", year, month, day)
    }
    
    private static func fetchDashboardData(dailyContent: DailyContentRepository, profile: Profile, date: Date) async -> DashboardData? {
        async let featuresData: DailyFeaturesData? = {
            do {
                return try await dailyContent.dailyFeatures(
                    profile: profile,
                    date: date,
                    cachePolicy: .networkFirst
                )
            } catch {
                return nil
            }
        }()

        async let readingData: PredictionData? = {
            do {
                return try await dailyContent.reading(
                    profile: profile,
                    scope: .daily,
                    date: date,
                    cachePolicy: .networkFirst
                )
            } catch {
                return nil
            }
        }()

        let features = await featuresData
        let prediction = await readingData
        guard features != nil || prediction != nil else {
            return nil
        }

        let personalDay = calculatePersonalDaySync(for: profile, date: date)
        let luckyNumbers = features?.luckyNumbers ?? []

        return DashboardData(
            date: date,
            personalDayNumber: personalDay.number,
            personalDayDescription: personalDay.description,
            personalYearNumber: personalDay.year,
            personalMonthNumber: personalDay.month,
            cycleGuidance: buildCycleGuidance(day: personalDay.number, month: personalDay.month, year: personalDay.year),
            affirmation: features?.affirmation,
            luckyNumbers: luckyNumbers,
            luckyColor: features?.luckyColor,
            advice: features?.advice,
            reading: prediction.map { makeDailyReadingSummary(from: $0) }
        )
    }
    
    private static func calculatePersonalDaySync(for profile: Profile, date: Date) -> (number: Int, description: String, year: Int, month: Int) {
        let parts = profile.dateOfBirth.split(separator: "-").map(String.init)
        guard parts.count == 3,
              let birthMonth = Int(parts[1]),
              let birthDay = Int(parts[2])
        else {
            return (1, "New beginnings & independence", 1, 1)
        }

        let tz = TimeZone(identifier: profile.timezone ?? "") ?? TimeZone(identifier: "UTC")!
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = tz

        let comps = calendar.dateComponents([.year, .month, .day], from: date)
        guard let targetYear = comps.year,
              let targetMonth = comps.month,
              let targetDay = comps.day
        else {
            return (1, "New beginnings & independence", 1, 1)
        }

        let personalYear = reduceToSingleDigit(birthMonth + birthDay + targetYear)
        let personalMonth = reduceToSingleDigit(personalYear + targetMonth)
        let personalDay = reduceToSingleDigit(personalMonth + targetDay)

        return (personalDay, personalDayText(for: personalDay), personalYear, personalMonth)
    }
    
    private static func reduceToSingleDigit(_ number: Int) -> Int {
        var n = number
        while n > 9 {
            var sum = 0
            var temp = n
            while temp > 0 {
                sum += temp % 10
                temp /= 10
            }
            n = sum
        }
        return n
    }
    
    static func makeDailyReadingSummary(from prediction: PredictionData) -> DailyReadingSummary {
        let headline = prediction.sections.first?.summary ?? "Your cosmic forecast is ready."
        let score = prediction.overallScore
        let energy: String
        if score >= 7.0 {
            energy = "Strong flow"
        } else if score >= 4.0 {
            energy = "Steady energy"
        } else {
            energy = "Quieter day"
        }

        return DailyReadingSummary(
            headline: headline,
            tldr: nil,
            overallEnergy: energy
        )
    }

    static func habitSummary(from habits: [HabitResponse], timezoneID: String?) -> (completed: Int, total: Int) {
        let completed = habits.filter { habit in
            guard let lastCompleted = habit.summary.lastCompleted,
                  let parsed = ISO8601DateFormatter().date(from: lastCompleted) else {
                return false
            }
            var calendar = Calendar(identifier: .gregorian)
            calendar.timeZone = TimeZone(identifier: timezoneID ?? "") ?? TimeZone(identifier: "UTC")!
            return calendar.isDateInToday(parsed)
        }.count

        return (completed, habits.count)
    }
}

// MARK: - Models

struct DailyReadingSummary {
    let headline: String
    let tldr: String?
    let overallEnergy: String
}

/// Cached dashboard data for Time Travel slider
struct DashboardData {
    let date: Date
    let personalDayNumber: Int?
    let personalDayDescription: String?
    let personalYearNumber: Int?
    let personalMonthNumber: Int?
    let cycleGuidance: String?
    let affirmation: String?
    let luckyNumbers: [Int]
    let luckyColor: String?
    let advice: String?
    let reading: DailyReadingSummary?
}
