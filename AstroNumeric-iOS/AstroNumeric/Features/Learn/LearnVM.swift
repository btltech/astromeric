// LearnVM.swift
// ViewModel for learning content - fetches from API with fallback

import SwiftUI
import Observation

@Observable
final class LearnVM {
    // MARK: - State
    
    var modules: [LearningModule] = []
    var selectedCategory: String = "astrology"
    var isLoading = false
    var error: String?
    var hasFetchedFromAPI = false
    
    // MARK: - Dependencies
    
    private let api = APIClient.shared
    
    // MARK: - Actions
    
    @MainActor
    func fetchModules() async {
        guard !isLoading else { return }
        
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        do {
            let response: PaginatedLearningModules = try await api.fetch(
                .learningModulesByCategory(selectedCategory),
                cachePolicy: .cacheFirst
            )
            modules = response.data
            hasFetchedFromAPI = true
            HapticManager.impact(.light)
        } catch {
            // Fall back to hardcoded content
            self.error = nil // Don't show error, use fallback
            modules = fallbackModules(for: selectedCategory)
        }
    }
    
    @MainActor
    func switchCategory(_ category: String) {
        selectedCategory = category
        Task {
            await fetchModules()
        }
    }
    
    // MARK: - Fallback Content
    
    private func fallbackModules(for category: String) -> [LearningModule] {
        switch category.lowercased() {
        case "astrology":
            return [
                LearningModule(
                    id: "astro-1",
                    title: "What is Astrology?",
                    description: "Understanding the cosmic language",
                    category: "astrology",
                    difficulty: "beginner",
                    durationMinutes: 5,
                    content: "Astrology is an ancient practice that studies the positions and movements of celestial bodies and their influence on human affairs. For thousands of years, cultures around the world have looked to the stars for guidance, believing that the cosmos reflects patterns in our lives.",
                    keywords: ["astrology", "basics", "introduction"],
                    relatedModules: ["astro-2", "astro-3"]
                ),
                LearningModule(
                    id: "astro-2",
                    title: "The Birth Chart",
                    description: "Your cosmic blueprint",
                    category: "astrology",
                    difficulty: "beginner",
                    durationMinutes: 8,
                    content: "Your birth chart, also known as a natal chart, is a snapshot of the sky at the exact moment you were born. It shows the positions of all major celestial bodies in relation to the zodiac signs and houses.",
                    keywords: ["birth chart", "natal chart", "blueprint"],
                    relatedModules: ["astro-1", "astro-3"]
                ),
                LearningModule(
                    id: "astro-3",
                    title: "Planets & Their Meanings",
                    description: "Celestial influences",
                    category: "astrology",
                    difficulty: "intermediate",
                    durationMinutes: 10,
                    content: "Each planet in astrology represents different aspects of life and personality. The Sun represents your core identity, the Moon your emotions, Mercury your communication style, Venus your approach to love and beauty, and Mars your drive and energy.",
                    keywords: ["planets", "meanings", "celestial"],
                    relatedModules: ["astro-2", "astro-4"]
                ),
                LearningModule(
                    id: "astro-4",
                    title: "Houses in Astrology",
                    description: "Life areas and experiences",
                    category: "astrology",
                    difficulty: "intermediate",
                    durationMinutes: 12,
                    content: "The 12 houses in astrology represent different areas of life. The 1st house is about self and appearance, the 7th about relationships, the 10th about career, and so on. Each house tells a story about a specific life domain.",
                    keywords: ["houses", "life areas", "domains"],
                    relatedModules: ["astro-3"]
                )
            ]
        case "numerology":
            return [
                LearningModule(
                    id: "num-1",
                    title: "Introduction to Numerology",
                    description: "The power of numbers",
                    category: "numerology",
                    difficulty: "beginner",
                    durationMinutes: 5,
                    content: "Numerology is the study of the mystical relationship between numbers and events in life. Each number carries its own unique vibration and meaning that can reveal insights about your personality and life path.",
                    keywords: ["numerology", "numbers", "introduction"],
                    relatedModules: ["num-2"]
                ),
                LearningModule(
                    id: "num-2",
                    title: "Your Life Path Number",
                    description: "Your soul's purpose",
                    category: "numerology",
                    difficulty: "beginner",
                    durationMinutes: 7,
                    content: "The Life Path Number is the most important number in your numerology chart. Calculated from your birth date, it reveals your primary purpose in life and the lessons you're here to learn.",
                    keywords: ["life path", "purpose", "destiny"],
                    relatedModules: ["num-1", "num-3"]
                ),
                LearningModule(
                    id: "num-3",
                    title: "Personal Year Cycles",
                    description: "Annual energy themes",
                    category: "numerology",
                    difficulty: "intermediate",
                    durationMinutes: 8,
                    content: "Personal Year cycles run in 9-year patterns. Each year carries a specific energy and theme that influences what you should focus on. Year 1 is about new beginnings, Year 5 about change, Year 9 about completion.",
                    keywords: ["cycles", "personal year", "themes"],
                    relatedModules: ["num-2"]
                )
            ]
        case "zodiac":
            return [
                LearningModule(
                    id: "zodiac-1",
                    title: "The 12 Signs",
                    description: "Overview of the zodiac",
                    category: "zodiac",
                    difficulty: "beginner",
                    durationMinutes: 10,
                    content: "The zodiac consists of 12 signs, each with unique characteristics. From fiery Aries to dreamy Pisces, each sign represents a different archetype and approach to life.",
                    keywords: ["zodiac", "signs", "overview"],
                    relatedModules: ["zodiac-2"]
                ),
                LearningModule(
                    id: "zodiac-2",
                    title: "Sun, Moon & Rising",
                    description: "Your cosmic trinity",
                    category: "zodiac",
                    difficulty: "intermediate",
                    durationMinutes: 8,
                    content: "Your Sun sign represents your core identity, your Moon sign your emotional nature, and your Rising sign how others perceive you. Together, these three create a more complete picture of your personality.",
                    keywords: ["sun", "moon", "rising", "trinity"],
                    relatedModules: ["zodiac-1", "zodiac-3"]
                ),
                LearningModule(
                    id: "zodiac-3",
                    title: "Sign Compatibility",
                    description: "Cosmic connections",
                    category: "zodiac",
                    difficulty: "intermediate",
                    durationMinutes: 10,
                    content: "Some signs naturally harmonize while others create tension. Understanding sign compatibility can help you navigate relationships more effectively.",
                    keywords: ["compatibility", "relationships", "harmony"],
                    relatedModules: ["zodiac-2"]
                )
            ]
        case "elements":
            return [
                LearningModule(
                    id: "elem-1",
                    title: "Fire Signs",
                    description: "Aries, Leo, Sagittarius",
                    category: "elements",
                    difficulty: "beginner",
                    durationMinutes: 6,
                    content: "Fire signs are passionate, dynamic, and energetic. They bring warmth and enthusiasm to everything they do. Aries leads with courage, Leo with heart, and Sagittarius with adventure.",
                    keywords: ["fire", "aries", "leo", "sagittarius"],
                    relatedModules: ["elem-2", "elem-3", "elem-4"]
                ),
                LearningModule(
                    id: "elem-2",
                    title: "Earth Signs",
                    description: "Taurus, Virgo, Capricorn",
                    category: "elements",
                    difficulty: "beginner",
                    durationMinutes: 6,
                    content: "Earth signs are grounded, practical, and reliable. They value stability and material security. Taurus brings patience, Virgo brings precision, and Capricorn brings ambition.",
                    keywords: ["earth", "taurus", "virgo", "capricorn"],
                    relatedModules: ["elem-1", "elem-3", "elem-4"]
                ),
                LearningModule(
                    id: "elem-3",
                    title: "Air Signs",
                    description: "Gemini, Libra, Aquarius",
                    category: "elements",
                    difficulty: "beginner",
                    durationMinutes: 6,
                    content: "Air signs are intellectual, communicative, and social. They thrive on ideas and connections. Gemini brings curiosity, Libra brings harmony, and Aquarius brings innovation.",
                    keywords: ["air", "gemini", "libra", "aquarius"],
                    relatedModules: ["elem-1", "elem-2", "elem-4"]
                ),
                LearningModule(
                    id: "elem-4",
                    title: "Water Signs",
                    description: "Cancer, Scorpio, Pisces",
                    category: "elements",
                    difficulty: "beginner",
                    durationMinutes: 6,
                    content: "Water signs are emotional, intuitive, and sensitive. They navigate life through feeling. Cancer brings nurturing, Scorpio brings depth, and Pisces brings compassion.",
                    keywords: ["water", "cancer", "scorpio", "pisces"],
                    relatedModules: ["elem-1", "elem-2", "elem-3"]
                )
            ]
        default:
            return []
        }
    }
    
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
