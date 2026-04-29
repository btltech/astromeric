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
    var sunSignEmoji: String = "✨"
    var dailyAffirmation: String?
    var luckyNumbers: [Int] = []
    var luckyColor: String?
    var dailyAdvice: String?
    var habitsCompletedToday: Int = 0
    var totalHabits: Int = 0
    
    // API client
    private let api = APIClient.shared
    private let localHabitsKey = "astromeric.local_habits.v1"
    
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
            let response: V2ApiResponse<PredictionData> = try await api.fetch(
                .reading(profile: profile, scope: .daily, date: date),
                cachePolicy: cachePolicy
            )
            
            // Extract summary from prediction data
            dailyReading = Self.makeDailyReadingSummary(from: response.data)
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
            let response: V2ApiResponse<DailyFeaturesData> = try await api.fetch(
                .dailyFeatures(profile: profile, date: date),
                cachePolicy: forceRefresh ? .networkFirst : .cacheFirst
            )
            
            dailyAffirmation = response.data.affirmation
            luckyNumbers = response.data.luckyNumbers
            luckyColor = response.data.luckyColor
            dailyAdvice = response.data.advice
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
            let response: V2ApiResponse<MoonPhaseData> = try await api.fetch(
                .currentMoon,
                cachePolicy: .cacheFirst
            )
            
            moonPhaseName = response.data.phaseName
            moonPhaseEmoji = response.data.emoji
            moonGuidance = response.data.guidance ?? ""
        } catch {
            moonPhaseName = "⚠️ Failed"
            moonPhaseEmoji = "❌"
            moonGuidance = error.localizedDescription
        }
    }

    @MainActor
    private func fetchHabitSummary(for profile: Profile) async {
        do {
            let response: V2ApiResponse<[HabitResponse]> = try await api.fetch(
                .habitsList,
                cachePolicy: .cacheFirst
            )
            let summary = Self.habitSummary(from: response.data, timezoneID: profile.timezone)
            habitsCompletedToday = summary.completed
            totalHabits = summary.total
        } catch {
            let localHabits = loadLocalHabits() ?? []
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
        let descriptions: [Int: String] = [
            1: "New beginnings & independence",
            2: "Cooperation & relationships",
            3: "Creativity & expression",
            4: "Building & organization",
            5: "Change & adventure",
            6: "Home & responsibility",
            7: "Reflection & spirituality",
            8: "Power & achievement",
            9: "Completion & humanitarianism"
        ]
        return descriptions[number] ?? "Embrace the day"
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
        
        var fetched: [(String, DashboardData)] = []
        await withTaskGroup(of: (String, DashboardData?).self) { group in
            for offset in offsets {
                guard let date = utcCalendar.date(byAdding: .day, value: offset, to: baseDate) else { continue }
                let key = Self.cacheKey(for: date)
                guard !existingKeys.contains(key) else { continue }
                
                group.addTask {
                    let data = await Self.fetchDashboardData(api: APIClient.shared, profile: profile, date: date)
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
    
    private static func fetchDashboardData(api: APIClient, profile: Profile, date: Date) async -> DashboardData? {
        async let featuresData: DailyFeaturesData? = {
            do {
                let response: V2ApiResponse<DailyFeaturesData> = try await api.fetch(
                    .dailyFeatures(profile: profile, date: date),
                    cachePolicy: .networkFirst
                )
                return response.data
            } catch {
                return nil
            }
        }()

        async let readingData: PredictionData? = {
            do {
                let response: V2ApiResponse<PredictionData> = try await api.fetch(
                    .reading(profile: profile, scope: .daily, date: date),
                    cachePolicy: .networkFirst
                )
                return response.data
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
            affirmation: features?.affirmation,
            luckyNumbers: luckyNumbers,
            luckyColor: features?.luckyColor,
            advice: features?.advice,
            reading: prediction.map { makeDailyReadingSummary(from: $0) }
        )
    }
    
    private static func calculatePersonalDaySync(for profile: Profile, date: Date) -> (number: Int, description: String) {
        let parts = profile.dateOfBirth.split(separator: "-").map(String.init)
        guard parts.count == 3,
              let birthMonth = Int(parts[1]),
              let birthDay = Int(parts[2])
        else {
            return (1, "New beginnings & independence")
        }

        let tz = TimeZone(identifier: profile.timezone ?? "") ?? TimeZone(identifier: "UTC")!
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = tz

        let comps = calendar.dateComponents([.year, .month, .day], from: date)
        guard let targetYear = comps.year,
              let targetMonth = comps.month,
              let targetDay = comps.day
        else {
            return (1, "New beginnings & independence")
        }

        let personalYear = reduceToSingleDigit(birthMonth + birthDay + targetYear)
        let personalMonth = reduceToSingleDigit(personalYear + targetMonth)
        let personalDay = reduceToSingleDigit(personalMonth + targetDay)

        return (personalDay, personalDayText(for: personalDay))
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
    
    private static func personalDayText(for number: Int) -> String {
        let descriptions: [Int: String] = [
            1: "New beginnings & independence",
            2: "Cooperation & relationships",
            3: "Creativity & expression",
            4: "Building & organization",
            5: "Change & adventure",
            6: "Home & responsibility",
            7: "Reflection & spirituality",
            8: "Power & achievement",
            9: "Completion & humanitarianism"
        ]
        return descriptions[number] ?? "Embrace the day"
    }

    static func makeDailyReadingSummary(from prediction: PredictionData) -> DailyReadingSummary {
        let headline = prediction.sections.first?.summary ?? "Your cosmic forecast is ready ✨"
        let score = prediction.overallScore
        let energy: String
        if score >= 7.0 {
            energy = "High"
        } else if score >= 4.0 {
            energy = "Moderate"
        } else {
            energy = "Low"
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

    private func loadLocalHabits() -> [LocalHabit]? {
        guard let data = UserDefaults.standard.data(forKey: localHabitsKey) else { return nil }
        return try? JSONDecoder().decode([LocalHabit].self, from: data)
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
    let affirmation: String?
    let luckyNumbers: [Int]
    let luckyColor: String?
    let advice: String?
    let reading: DailyReadingSummary?
}
