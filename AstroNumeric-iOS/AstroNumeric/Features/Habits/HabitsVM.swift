// HabitsVM.swift
// ViewModel for lunar-aligned habit tracking

import SwiftUI
import Observation

@Observable
final class HabitsVM {
    // MARK: - State
    
    var habits: [LocalHabit] = []
    var categories: [LocalHabitCategory] = []
    var lunarGuidance: LunarHabitGuidance?
    var currentMoonPhase: String = "waxing_crescent"
    var selectedCategory: String = "all"
    var isLoading = false
    var error: String?
    
    // MARK: - Computed Properties
    
    var filteredHabits: [LocalHabit] {
        if selectedCategory == "all" {
            return habits
        }
        return habits.filter { $0.category == selectedCategory }
    }
    
    var todayCompletedCount: Int {
        habits.filter { $0.isCompletedToday }.count
    }
    
    var overallStreak: Int {
        habits.map { $0.currentStreak }.max() ?? 0
    }

    var suggestedNextHabit: LocalHabit? {
        // Prefer an incomplete habit aligned with today's lunar guidance.
        let incomplete = habits.filter { !$0.isCompletedToday }
        guard !incomplete.isEmpty else { return nil }

        if let guidance = lunarGuidance {
            if let aligned = incomplete.first(where: { guidance.idealHabits.contains($0.category) }) {
                return aligned
            }
        }
        return incomplete.first
    }

    func totalCount(for categoryId: String) -> Int {
        if categoryId == "all" {
            return habits.count
        }
        return habits.filter { $0.category == categoryId }.count
    }

    func completedCount(for categoryId: String) -> Int {
        if categoryId == "all" {
            return habits.filter { $0.isCompletedToday }.count
        }
        return habits.filter { $0.category == categoryId && $0.isCompletedToday }.count
    }
    
    // MARK: - Dependencies
    
    private let api = APIClient.shared
    private let localHabitsKey = "astromeric.local_habits.v1"
    
    // MARK: - Actions
    
    @MainActor
    func loadData() async {
        guard !isLoading else { return }
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        // Load in parallel
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.fetchCategories() }
            group.addTask { await self.fetchLunarGuidance() }
            group.addTask { await self.fetchHabits() }
        }
    }
    
    @MainActor
    private func fetchCategories() async {
        // Backend doesn't have categories endpoint - use local fallbacks
        categories = LocalHabitCategory.fallbackCategories
    }
    
    @MainActor
    private func fetchLunarGuidance() async {
        // Backend doesn't have lunar-guidance endpoint - use local fallback
        lunarGuidance = LunarHabitGuidance.fallback
        currentMoonPhase = lunarGuidance?.phase ?? "waxing_crescent"
    }
    
    @MainActor
    private func fetchHabits() async {
        do {
            let response: V2ApiResponse<[HabitResponse]> = try await api.fetch(
                .habitsList,
                cachePolicy: .networkFirst
            )

            habits = response.data.map { apiHabit in
                LocalHabit(
                    id: apiHabit.id,
                    name: apiHabit.name,
                    category: apiHabit.category,
                    emoji: categoryEmoji(for: apiHabit.category),
                    currentStreak: apiHabit.summary.currentStreak,
                    longestStreak: apiHabit.summary.longestStreak,
                    completionRate: apiHabit.summary.completionRate,
                    isCompletedToday: apiHabit.summary.lastCompleted.map { isToday(iso8601: $0) } ?? false,
                    lastCompleted: apiHabit.summary.lastCompleted.flatMap { parseISO8601($0) }
                )
            }
            saveLocalHabits()
        } catch {
            // Backend not available/deployed yet: fall back to locally saved habits.
            if let cached = loadLocalHabits() {
                habits = cached
            } else if habits.isEmpty {
                habits = []
            }
        }
    }
    
    @MainActor
    func createHabit(name: String, category: String, description: String = "") async -> Bool {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let request = CreateHabitRequest(name: name, category: category, frequency: "daily", description: description)
            let response: V2ApiResponse<HabitResponse> = try await api.fetch(
                .createHabit(request)
            )
            
            // Convert response to local habit model
            let newHabit = LocalHabit(
                id: response.data.id,
                name: response.data.name,
                category: response.data.category,
                emoji: categoryEmoji(for: category),
                currentStreak: response.data.summary.currentStreak,
                longestStreak: response.data.summary.longestStreak,
                completionRate: response.data.summary.completionRate,
                isCompletedToday: false,
                lastCompleted: nil
            )
            habits.insert(newHabit, at: 0)
            saveLocalHabits()
            HapticManager.notification(.success)
            return true
        } catch {
            // Local fallback so the feature remains usable without backend.
            let newHabit = LocalHabit(
                id: UUID().uuidString,
                name: name,
                category: category,
                emoji: categoryEmoji(for: category),
                currentStreak: 0,
                longestStreak: 0,
                completionRate: 0,
                isCompletedToday: false,
                lastCompleted: nil
            )
            habits.insert(newHabit, at: 0)
            saveLocalHabits()
            self.error = "Saved locally (sync unavailable)"
            HapticManager.notification(.warning)
            return true
        }
    }
    
    @MainActor
    func toggleHabitCompletion(_ habit: LocalHabit) async {
        guard let index = habits.firstIndex(where: { $0.id == habit.id }) else { return }
        
        let previous = habits[index]
        let wasCompleted = habits[index].isCompletedToday
        
        // Optimistic update
        withAnimation(.spring(duration: 0.3)) {
            habits[index].isCompletedToday.toggle()
            if !wasCompleted {
                habits[index].currentStreak += 1
                habits[index].lastCompleted = Date()
            } else {
                habits[index].currentStreak = max(0, habits[index].currentStreak - 1)
            }
        }
        
        HapticManager.impact(.medium)
        saveLocalHabits()
        
        // Sync with backend
        do {
            // Only attempt sync when we have a server-style numeric habit id.
            guard let habitIdInt = Int(habit.id) else { return }
            let _: V2ApiResponse<HabitEntry> = try await api.fetch(
                .logHabitEntry(habitId: habitIdInt, completed: !wasCompleted, note: nil)
            )
        } catch {
            // Revert on failure
            withAnimation {
                habits[index] = previous
            }
            saveLocalHabits()
        }
    }
    
    @MainActor
    func deleteHabit(_ habit: LocalHabit) {
        withAnimation {
            habits.removeAll { $0.id == habit.id }
        }
        saveLocalHabits()
        HapticManager.notification(.warning)
    }
    
    // MARK: - Helpers
    
    private func categoryEmoji(for category: String) -> String {
        let emojis: [String: String] = [
            "exercise": "🏃",
            "meditation": "🧘",
            "learning": "📚",
            "creative": "🎨",
            "social": "👥",
            "productivity": "💼",
            "health": "🥗",
            "rest": "😴",
            "financial": "💰",
            "spiritual": "✨"
        ]
        return emojis[category] ?? "✅"
    }

    private func parseISO8601(_ value: String) -> Date? {
        ISO8601DateFormatter().date(from: value)
    }

    private func isToday(iso8601 value: String) -> Bool {
        guard let date = parseISO8601(value) else { return false }
        return Calendar.current.isDateInToday(date)
    }

    private func saveLocalHabits() {
        guard let data = try? JSONEncoder().encode(habits) else { return }
        UserDefaults.standard.set(data, forKey: localHabitsKey)
    }

    private func loadLocalHabits() -> [LocalHabit]? {
        guard let data = UserDefaults.standard.data(forKey: localHabitsKey) else { return nil }
        return try? JSONDecoder().decode([LocalHabit].self, from: data)
    }
    
    func isPhaseGoodFor(category: String) -> Bool {
        guard let guidance = lunarGuidance else { return true }
        return guidance.idealHabits.contains(category)
    }
}

// MARK: - Local Models (for UI state, distinct from API models)

struct LocalHabit: Identifiable, Codable, Equatable {
    var id: String
    var name: String
    var category: String
    var emoji: String
    var currentStreak: Int
    var longestStreak: Int
    var completionRate: Double
    var isCompletedToday: Bool
    var lastCompleted: Date?
    
}

struct LocalHabitCategory: Identifiable, Codable {
    let id: String
    let name: String
    let emoji: String
    let description: String
    let bestPhases: [String]
    let avoidPhases: [String]
    
    enum CodingKeys: String, CodingKey {
        case id, name, emoji, description
        case bestPhases = "best_phases"
        case avoidPhases = "avoid_phases"
    }
    
    static let fallbackCategories: [LocalHabitCategory] = [
        LocalHabitCategory(id: "exercise", name: "Exercise", emoji: "🏃", description: "Physical activity", bestPhases: ["first_quarter", "full_moon"], avoidPhases: ["waning_crescent"]),
        LocalHabitCategory(id: "meditation", name: "Meditation", emoji: "🧘", description: "Mindfulness", bestPhases: ["new_moon", "waning_crescent"], avoidPhases: []),
        LocalHabitCategory(id: "learning", name: "Learning", emoji: "📚", description: "Study & skills", bestPhases: ["waxing_crescent", "first_quarter"], avoidPhases: []),
        LocalHabitCategory(id: "creative", name: "Creative", emoji: "🎨", description: "Art & creation", bestPhases: ["waxing_gibbous", "full_moon"], avoidPhases: []),
        LocalHabitCategory(id: "health", name: "Health", emoji: "🥗", description: "Diet & self-care", bestPhases: ["new_moon", "waxing_crescent"], avoidPhases: []),
        LocalHabitCategory(id: "spiritual", name: "Spiritual", emoji: "✨", description: "Practice & ritual", bestPhases: ["new_moon", "full_moon"], avoidPhases: [])
    ]
}

struct LunarHabitGuidance: Codable {
    let phase: String
    let phaseName: String
    let emoji: String
    let theme: String
    let bestFor: [String]
    let avoid: [String]
    let energy: String
    let idealHabits: [String]
    let powerScoreModifier: Double
    
    enum CodingKeys: String, CodingKey {
        case phase, emoji, theme, energy
        case phaseName = "phase_name"
        case bestFor = "best_for"
        case avoid
        case idealHabits = "ideal_habits"
        case powerScoreModifier = "power_score_modifier"
    }
    
    static let fallback = LunarHabitGuidance(
        phase: "waxing_crescent",
        phaseName: "Waxing Crescent",
        emoji: "🌒",
        theme: "Building Momentum",
        bestFor: ["Taking first steps", "Building routines", "Learning new skills"],
        avoid: ["Giving up early", "Overanalyzing"],
        energy: "Increasing, hopeful",
        idealHabits: ["exercise", "learning", "creative", "social"],
        powerScoreModifier: 1.1
    )
}

struct HabitResponse: Codable {
    let id: String
    let name: String
    let description: String
    let category: String
    let createdDate: String
    let entries: [HabitEntry]
    let summary: HabitSummary
    
    enum CodingKeys: String, CodingKey {
        case id, name, description, category, entries, summary
        case createdDate = "created_date"
    }
}

struct HabitSummary: Codable {
    let habitId: String
    let habitName: String
    let totalDays: Int
    let completedDays: Int
    let currentStreak: Int
    let longestStreak: Int
    let completionRate: Double
    let lastCompleted: String?

    enum CodingKeys: String, CodingKey {
        case habitId = "habit_id"
        case habitName = "habit_name"
        case totalDays = "total_days"
        case completedDays = "completed_days"
        case currentStreak = "current_streak"
        case longestStreak = "longest_streak"
        case completionRate = "completion_rate"
        case lastCompleted = "last_completed"
    }
}

struct HabitEntry: Codable {
    let id: String
    let habitName: String
    let category: String
    let date: String
    let completed: Bool
    let notes: String?
    let streakDays: Int
    
    enum CodingKeys: String, CodingKey {
        case id, category, date, completed, notes
        case habitName = "habit_name"
        case streakDays = "streak_days"
    }
}
