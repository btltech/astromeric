// LearnVM.swift
// ViewModel for learning content - serves the lessons bundled in the app

import SwiftUI
import Observation

@Observable
final class LearnVM {
    // MARK: - State
    
    var modules: [LearningModule] = []
    var selectedCategory: String = "astrology"
    
    // MARK: - Actions
    
    @MainActor
    func fetchModules() async {
        // Lessons are static, long-form reference content bundled in the app.
        // Render ONLY the local content so the full lessons always show — never
        // overwritten by thin/stale server data or a cache.
        modules = fallbackModules(for: selectedCategory)
        HapticManager.impact(.light)
    }
    
    @MainActor
    func switchCategory(_ category: String) {
        selectedCategory = category
        Task {
            await fetchModules()
        }
    }
    
    // MARK: - Fallback Content
    
    /// Lessons for a category, from the bundled lessons.json. The same file
    /// is served by the API to the website, so app and web teach the same
    /// thing; a backend test fails if the two copies differ.
    func fallbackModules(for category: String) -> [LearningModule] {
        Self.bundledLessons.filter { $0.category.lowercased() == category.lowercased() }
    }

    static let bundledLessons: [LearningModule] = {
        guard let url = Bundle.main.url(forResource: "lessons", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let lessons = try? JSONDecoder().decode([LearningModule].self, from: data)
        else { return [] }
        return lessons
    }()

    // MARK: - Categories
    
    var categories: [(id: String, title: String, icon: String)] {
        [
            ("astrology", "Astrology", "sparkles"),
            ("numerology", "Numerology", "number.circle"),
            ("zodiac", "Zodiac", "sun.max"),
            ("elements", "Elements", "leaf.fill")
        ]
    }
}
