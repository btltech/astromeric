// LearningProgressManager.swift
// Tracks completion of learning modules.
// Storage migrated to SQLite (LocalDomainDatabase) with legacy UserDefaults fallback.

import Foundation
import Observation

@Observable
final class LearningProgressManager {

    static let shared = LearningProgressManager()

    // MARK: - State

    /// Set of completed module IDs
    private(set) var completedModuleIds: Set<String> = []

    // MARK: - Storage

    private let domain = "learning"
    private let storageKey = "completed_modules.v1"
    private let legacyDefaultsKey = "completedLearningModules"

    // MARK: - Init

    private init() {
        // Hydrate synchronously from legacy UserDefaults so the very first read is correct.
        // SQLite is the source of truth going forward; load it asynchronously and replace
        // the legacy snapshot once it's available.
        if let saved = UserDefaults.standard.array(forKey: legacyDefaultsKey) as? [String] {
            completedModuleIds = Set(saved)
        }
        Task { [weak self] in
            await self?.hydrateFromDatabase()
        }
    }

    // MARK: - Public API

    /// Mark a module/lesson as complete
    func markComplete(moduleId: String) {
        guard completedModuleIds.insert(moduleId).inserted else { return }
        persistAsync()
    }

    /// Check if a specific module is complete
    func isComplete(moduleId: String) -> Bool {
        completedModuleIds.contains(moduleId)
    }

    /// Calculate progress for a learning track
    /// - Parameter lessonIds: The IDs of lessons belonging to this track
    /// - Returns: Progress from 0.0 to 1.0
    func progress(for lessonIds: [String]) -> Double {
        guard !lessonIds.isEmpty else { return 0.0 }
        let completed = lessonIds.filter { completedModuleIds.contains($0) }.count
        return Double(completed) / Double(lessonIds.count)
    }

    /// Number of completed lessons from a given set
    func completedCount(from lessonIds: [String]) -> Int {
        lessonIds.filter { completedModuleIds.contains($0) }.count
    }

    /// Reset all progress (for testing/debug)
    func resetAll() {
        completedModuleIds.removeAll()
        persistAsync()
    }

    // MARK: - Persistence

    private func hydrateFromDatabase() async {
        if let stored = await LocalDomainDatabase.shared.load(
            [String].self,
            domain: domain,
            key: storageKey
        ) {
            await MainActor.run { self.completedModuleIds = Set(stored) }
            return
        }
        // First migration: persist whatever we hydrated from legacy UserDefaults
        // and clear the legacy key.
        let snapshot = Array(self.completedModuleIds)
        if !snapshot.isEmpty {
            await LocalDomainDatabase.shared.save(snapshot, domain: domain, key: storageKey)
        }
        UserDefaults.standard.removeObject(forKey: legacyDefaultsKey)
    }

    private func persistAsync() {
        let snapshot = Array(completedModuleIds)
        let domain = self.domain
        let key = self.storageKey
        Task {
            if snapshot.isEmpty {
                await LocalDomainDatabase.shared.remove(domain: domain, key: key)
            } else {
                await LocalDomainDatabase.shared.save(snapshot, domain: domain, key: key)
            }
        }
    }
}

// MARK: - Learning Track Lesson IDs

/// Static lesson ID sets for each learning track, matching the backend module IDs
enum LearningTrack {
    static let astrology101LessonIds = (1...12).map { "astro-\($0)" }
    static let numerologyBasicsLessonIds = (1...8).map { "numerology-\($0)" }
    static let moonWisdomLessonIds = (1...6).map { "moon-\($0)" }
    static let tarotMasteryLessonIds = (1...10).map { "tarot-\($0)" }
}
