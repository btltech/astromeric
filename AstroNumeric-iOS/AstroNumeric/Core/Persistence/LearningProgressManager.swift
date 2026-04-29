// LearningProgressManager.swift
// Tracks completion of learning modules, persisted via UserDefaults

import Foundation
import Observation

@Observable
final class LearningProgressManager {
    
    static let shared = LearningProgressManager()
    
    // MARK: - State
    
    /// Set of completed module IDs
    private(set) var completedModuleIds: Set<String> = []
    
    // MARK: - UserDefaults Key
    
    private let storageKey = "completedLearningModules"
    
    // MARK: - Init
    
    private init() {
        loadProgress()
    }
    
    // MARK: - Public API
    
    /// Mark a module/lesson as complete
    func markComplete(moduleId: String) {
        completedModuleIds.insert(moduleId)
        persistProgress()
    }
    
    /// Check if a specific module is complete
    func isComplete(moduleId: String) -> Bool {
        completedModuleIds.contains(moduleId)
    }
    
    /// Calculate progress for a learning track
    /// - Parameters:
    ///   - trackId: Identifier for the track (e.g. "astrology-101")
    ///   - totalLessons: Total number of lessons in the track
    ///   - lessonIds: The IDs of lessons belonging to this track
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
        persistProgress()
    }
    
    // MARK: - Persistence
    
    private func loadProgress() {
        if let saved = UserDefaults.standard.array(forKey: storageKey) as? [String] {
            completedModuleIds = Set(saved)
        }
    }
    
    private func persistProgress() {
        UserDefaults.standard.set(Array(completedModuleIds), forKey: storageKey)
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
