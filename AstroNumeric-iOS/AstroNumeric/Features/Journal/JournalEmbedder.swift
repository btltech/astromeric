// JournalEmbedder.swift
// On-device semantic search over journal entries using Apple NaturalLanguage embeddings.
// Acts as a local RAG (Retrieval-Augmented Generation) engine for the Cosmic Guide AI.

import Foundation
import NaturalLanguage

actor JournalEmbedder {
    static let shared = JournalEmbedder()
    
    // MARK: - Types
    
    /// An indexed journal entry with its embedding vector
    struct IndexedEntry: Codable {
        let id: Int
        let profileId: Int
        let text: String
        let date: Date
        let outcome: String?
        var embedding: [Double]
    }
    
    // MARK: - State
    
    private var index: [IndexedEntry] = []
    private var isLoaded = false
    
    private var storageURL: URL {
        let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        return dir.appendingPathComponent("journal_embeddings.json")
    }
    
    // MARK: - Public API
    
    /// Rebuild the index from all local journal entries for a profile.
    func rebuildIndex(profileId: Int) {
        let entries = LocalJournalStore.shared.list(profileId: profileId)
        var newIndex: [IndexedEntry] = []
        
        for entry in entries {
            let text = entry.entry.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !text.isEmpty else { continue }
            
            let embedding = embed(text)
            guard !embedding.isEmpty else { continue }
            
            newIndex.append(IndexedEntry(
                id: entry.id,
                profileId: profileId,
                text: text,
                date: entry.createdAt,
                outcome: entry.outcome,
                embedding: embedding
            ))
        }
        
        index = newIndex
        persist()
        isLoaded = true
        DebugLog.log("JournalEmbedder: indexed \(newIndex.count) entries for profile \(profileId)")
    }
    
    /// Search the index for entries semantically similar to the query.
    /// Returns the top-k most relevant entries.
    func search(query: String, profileId: Int, topK: Int = 3) -> [SearchResult] {
        if !isLoaded { loadFromDisk() }
        
        let queryEmbedding = embed(query)
        guard !queryEmbedding.isEmpty else { return [] }
        
        let profileEntries = index.filter { $0.profileId == profileId }
        guard !profileEntries.isEmpty else { return [] }
        
        var scored: [(entry: IndexedEntry, score: Double)] = []
        
        for entry in profileEntries {
            let similarity = cosineSimilarity(queryEmbedding, entry.embedding)
            scored.append((entry, similarity))
        }
        
        // Sort by similarity (highest first) and take top-k
        scored.sort { $0.score > $1.score }
        let results = scored.prefix(topK)
        
        return results.map { item in
            SearchResult(
                id: item.entry.id,
                text: item.entry.text,
                date: item.entry.date,
                outcome: item.entry.outcome,
                relevanceScore: item.score
            )
        }
    }
    
    /// Format search results as context for the AI system prompt.
    func contextBlock(for query: String, profileId: Int) -> String? {
        let results = search(query: query, profileId: profileId, topK: 3)
        guard !results.isEmpty else { return nil }
        
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        
        let entries = results.enumerated().map { i, r in
            let dateStr = formatter.string(from: r.date)
            let outcomeStr = r.outcome.map { " (outcome: \($0))" } ?? ""
            let preview = String(r.text.prefix(300))
            return "  \(i + 1). [\(dateStr)]\(outcomeStr): \"\(preview)\""
        }.joined(separator: "\n")
        
        return "RELEVANT JOURNAL ENTRIES (from user's past reflections):\n\(entries)"
    }
    
    // MARK: - Embedding
    
    /// Generate a sentence embedding using Apple's NaturalLanguage framework.
    private func embed(_ text: String) -> [Double] {
        guard let embedding = NLEmbedding.sentenceEmbedding(for: .english) else {
            DebugLog.log("JournalEmbedder: NLEmbedding not available")
            return []
        }
        
        // NLEmbedding returns a fixed-dimension vector
        guard let vector = embedding.vector(for: text) else {
            return []
        }
        
        return vector
    }
    
    // MARK: - Math
    
    /// Cosine similarity between two vectors.
    private func cosineSimilarity(_ a: [Double], _ b: [Double]) -> Double {
        guard a.count == b.count, !a.isEmpty else { return 0 }
        
        var dot = 0.0
        var normA = 0.0
        var normB = 0.0
        
        for i in 0..<a.count {
            dot += a[i] * b[i]
            normA += a[i] * a[i]
            normB += b[i] * b[i]
        }
        
        let denominator = sqrt(normA) * sqrt(normB)
        return denominator > 0 ? dot / denominator : 0
    }
    
    // MARK: - Persistence
    
    private func persist() {
        do {
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            let data = try encoder.encode(index)
            try data.write(to: storageURL, options: .atomic)
        } catch {
            DebugLog.log("JournalEmbedder: persist failed — \(error)")
        }
    }
    
    private func loadFromDisk() {
        do {
            let data = try Data(contentsOf: storageURL)
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            index = try decoder.decode([IndexedEntry].self, from: data)
            isLoaded = true
        } catch {
            // No persisted index, that's fine
            isLoaded = true
        }
    }
}

// MARK: - Search Result

struct SearchResult {
    let id: Int
    let text: String
    let date: Date
    let outcome: String?
    let relevanceScore: Double
}
