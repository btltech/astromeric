// RelationshipsVM.swift
// ViewModel for saved relationships and compatibility history

import SwiftUI
import Observation

@Observable
final class RelationshipsVM {
    // MARK: - State
    
    var savedRelationships: [SavedRelationship] = []
    var isLoading = false
    var error: String?
    
    // MARK: - Dependencies
    
    private let api = APIClient.shared
    private let defaults = UserDefaults.standard
    private let storageKey = "savedRelationships"
    
    // MARK: - Initialization
    
    init() {
        loadFromStorage()
        if AppStore.shared.hideSensitiveDetailsEnabled {
            scrubSensitiveDetails()
        }
    }
    
    // MARK: - Actions
    
    @MainActor
    func loadRelationships() async {
        // For now, relationships are stored locally
        // Backend sync can be added later
        loadFromStorage()
    }
    
    @MainActor
    func saveRelationship(_ relationship: SavedRelationship) {
        // Check for duplicate
        if let existingIndex = savedRelationships.firstIndex(where: {
            $0.personAName == relationship.personAName && $0.personBName == relationship.personBName
        }) {
            // Update existing
            savedRelationships[existingIndex] = relationship
        } else {
            // Add new
            savedRelationships.insert(relationship, at: 0)
        }
        
        persistToStorage()
        HapticManager.notification(.success)
    }
    
    @MainActor
    func deleteRelationship(_ relationship: SavedRelationship) {
        withAnimation {
            savedRelationships.removeAll { $0.id == relationship.id }
        }
        persistToStorage()
        HapticManager.notification(.warning)
    }
    
    @MainActor
    func refreshCompatibility(for relationship: SavedRelationship) async {
        guard let index = savedRelationships.firstIndex(where: { $0.id == relationship.id }) else { return }
        
        isLoading = true
        defer { isLoading = false }
        
        // Re-fetch compatibility data from API
        // This requires reconstructing the profile objects
        // For now, just update the last updated date
        savedRelationships[index].lastUpdated = Date()
        persistToStorage()
        HapticManager.impact(.light)
    }
    
    // MARK: - Storage
    
    private func loadFromStorage() {
        guard let data = defaults.data(forKey: storageKey),
              let relationships = try? JSONDecoder().decode([SavedRelationship].self, from: data) else {
            // Use sample data for empty state demo
            savedRelationships = []
            return
        }
        savedRelationships = relationships
    }
    
    private func persistToStorage() {
        guard let data = try? JSONEncoder().encode(savedRelationships) else { return }
        defaults.set(data, forKey: storageKey)
    }

    private func scrubSensitiveDetails() {
        savedRelationships = savedRelationships.map { $0.redactedCopy() }
        persistToStorage()
    }

    static func scrubStoredSensitiveDetails() {
        let defaults = UserDefaults.standard
        let storageKey = "savedRelationships"
        guard let data = defaults.data(forKey: storageKey),
              let relationships = try? JSONDecoder().decode([SavedRelationship].self, from: data) else {
            return
        }

        let scrubbed = relationships.map { $0.redactedCopy() }
        guard let scrubbedData = try? JSONEncoder().encode(scrubbed) else { return }
        defaults.set(scrubbedData, forKey: storageKey)
    }
    
    // MARK: - Computed Properties
    
    var relationshipsByType: [RelationshipType: [SavedRelationship]] {
        Dictionary(grouping: savedRelationships, by: { $0.type })
    }
    
    var averageCompatibility: Double {
        guard !savedRelationships.isEmpty else { return 0 }
        let total = savedRelationships.reduce(0) { $0 + $1.overallScore }
        return total / Double(savedRelationships.count)
    }
}

// MARK: - Models

struct SavedRelationship: Identifiable, Codable {
    let id: String
    let personAName: String
    let personBName: String
    let personADOB: String
    let personBDOB: String
    let type: RelationshipType
    let overallScore: Double
    let categories: [CompatibilityCategorySummary]
    let strengths: [String]
    let challenges: [String]
    let createdAt: Date
    var lastUpdated: Date
    
    init(
        id: String = UUID().uuidString,
        personAName: String,
        personBName: String,
        personADOB: String,
        personBDOB: String,
        type: RelationshipType,
        overallScore: Double,
        categories: [CompatibilityCategorySummary] = [],
        strengths: [String] = [],
        challenges: [String] = [],
        createdAt: Date = Date(),
        lastUpdated: Date = Date()
    ) {
        self.id = id
        self.personAName = personAName
        self.personBName = personBName
        self.personADOB = personADOB
        self.personBDOB = personBDOB
        self.type = type
        self.overallScore = overallScore
        self.categories = categories
        self.strengths = strengths
        self.challenges = challenges
        self.createdAt = createdAt
        self.lastUpdated = lastUpdated
    }
    
    var scoreColor: Color {
        if overallScore >= 75 { return .green }
        if overallScore >= 50 { return .orange }
        return .red
    }
    
    var formattedScore: String {
        "\(Int(overallScore))%"
    }
}

struct CompatibilityCategorySummary: Codable {
    let name: String
    let score: Double
    let emoji: String
}

enum RelationshipType: String, Codable, CaseIterable {
    case romantic = "romantic"
    case friendship = "friendship"
    case family = "family"
    case business = "business"
    
    var displayName: String {
        switch self {
        case .romantic: return "Romantic"
        case .friendship: return "Friendship"
        case .family: return "Family"
        case .business: return "Business"
        }
    }
    
    var emoji: String {
        switch self {
        case .romantic: return "❤️"
        case .friendship: return "🤝"
        case .family: return "👨‍👩‍👧"
        case .business: return "💼"
        }
    }
    
    var color: Color {
        switch self {
        case .romantic: return .pink
        case .friendship: return .blue
        case .family: return .orange
        case .business: return .purple
        }
    }
}

// MARK: - Helper to create from CompatibilityResult

extension SavedRelationship {
    static func from(
        personA: Profile,
        personBName: String,
        personBDOB: String,
        result: CompatibilityResult,
        type: RelationshipType = .romantic,
        hideSensitive: Bool = false
    ) -> SavedRelationship {
        // Map dimensions to categories
        let categories = result.dimensions?.map { dim in
            CompatibilityCategorySummary(
                name: dim.name,
                score: dim.score,
                emoji: emojiForDimension(dim.name)
            )
        } ?? []
        
        return SavedRelationship(
            personAName: hideSensitive ? "You" : personA.name,
            personBName: hideSensitive ? "\(type.displayName) Match" : personBName,
            personADOB: hideSensitive ? PrivacyRedaction.maskedDate : personA.dateOfBirth,
            personBDOB: hideSensitive ? PrivacyRedaction.maskedDate : personBDOB,
            type: type,
            overallScore: result.overallScore ?? Double(result.score ?? 0),
            categories: categories,
            strengths: result.strengths ?? [],
            challenges: result.challenges ?? []
        )
    }
    
    private static func emojiForDimension(_ name: String) -> String {
        let normalized = name.lowercased()
        if normalized.contains("love") || normalized.contains("romantic") { return "💕" }
        if normalized.contains("emotional") || normalized.contains("feelings") { return "💝" }
        if normalized.contains("communication") || normalized.contains("mental") { return "💬" }
        if normalized.contains("physical") || normalized.contains("passion") { return "🔥" }
        if normalized.contains("trust") || normalized.contains("security") { return "🤝" }
        if normalized.contains("values") || normalized.contains("goals") { return "🌟" }
        if normalized.contains("intellectual") || normalized.contains("mental") { return "🧠" }
        if normalized.contains("spiritual") { return "✨" }
        return "💫"
    }
}
