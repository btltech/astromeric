// ResponseCache.swift
// In-memory + disk response cache with TTL support.
// Entries with TTL ≥ 1 hour are persisted to disk so LLM responses
// survive app restarts. No paying for the same AI generation twice.

import Foundation
import CryptoKit

actor ResponseCache {
    static let shared = ResponseCache()
    
    /// Disk-persistable cache entry — stores the original key for round-tripping.
    private struct CacheEntry: Codable {
        let key: String
        let data: Data
        let expiresAt: Date
        var lastAccessedAt: Date?
    }
    
    private var cache: [String: CacheEntry] = [:]
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()
    
    /// Entries with TTL above this threshold are persisted to disk
    private let diskThreshold: TimeInterval = 3600 // 1 hour

    // Keep cache bounded to prevent unbounded disk growth.
    private let maxMemoryEntries: Int = 200
    private let maxDiskEntries: Int = 250
    private let maxDiskBytes: Int64 = 30 * 1024 * 1024 // 30 MB
    
    private static var diskCacheURL: URL {
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        return appSupport.appendingPathComponent("com.astromeric.responseCache", isDirectory: true)
    }

    private static var legacyDiskCacheURL: URL {
        let caches = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first!
        return caches.appendingPathComponent("com.astromeric.responseCache", isDirectory: true)
    }
    
    private init() {
        encoder.dateEncodingStrategy = .iso8601
        decoder.dateDecodingStrategy = .iso8601
        Self.migrateLegacyDiskCacheIfNeeded()
        Self.ensureDiskDirectoryExists()
        // Hydrate from disk synchronously on init
        cache = Self.loadDiskEntries()
        Task { [weak self] in
            guard let self else { return }
            await self.pruneExpired()
            await self.enforceMemoryLimits()
            await self.enforceDiskLimits()
        }
    }
    
    // MARK: - Public API
    
    /// Get cached value if not expired
    func get<T: Decodable>(for key: String) -> T? {
        guard let entry = cache[key] else { return nil }
        
        if Date() > entry.expiresAt {
            cache.removeValue(forKey: key)
            removeDiskEntry(for: key)
            return nil
        }

        // Touch access time (for memory LRU) and file mod time (for disk LRU)
        var updated = entry
        updated.lastAccessedAt = Date()
        cache[key] = updated
        touchDiskEntry(for: key)
        
        return try? decoder.decode(T.self, from: entry.data)
    }
    
    /// Store value with TTL. Entries with TTL ≥ 1hr are also written to disk.
    func set<T: Encodable>(_ value: T, for key: String, ttl: TimeInterval) {
        guard let data = try? encoder.encode(value) else { return }
        
        let entry = CacheEntry(key: key, data: data, expiresAt: Date().addingTimeInterval(ttl), lastAccessedAt: Date())
        cache[key] = entry
        
        if ttl >= diskThreshold {
            writeDiskEntry(entry)
        }

        enforceMemoryLimits()
        enforceDiskLimits()
    }
    
    /// Store type-erased encodable value with TTL
    func setAny(_ value: any Encodable, for key: String, ttl: TimeInterval) {
        guard let data = try? encoder.encode(value) else { return }
        
        let entry = CacheEntry(key: key, data: data, expiresAt: Date().addingTimeInterval(ttl), lastAccessedAt: Date())
        cache[key] = entry
        
        if ttl >= diskThreshold {
            writeDiskEntry(entry)
        }

        enforceMemoryLimits()
        enforceDiskLimits()
    }
    
    /// Remove specific cache entry
    func remove(for key: String) {
        cache.removeValue(forKey: key)
        removeDiskEntry(for: key)
    }
    
    /// Clear all cache entries (memory + disk)
    func clearAll() {
        cache.removeAll()
        try? FileManager.default.removeItem(at: Self.diskCacheURL)
    }
    
    // MARK: - Diagnostics
    
    /// Number of live cache entries in memory
    var entryCount: Int { cache.count }
    
    /// Number of disk-persisted entries
    var diskEntryCount: Int {
        let url = Self.diskCacheURL
        guard let files = try? FileManager.default.contentsOfDirectory(at: url, includingPropertiesForKeys: nil) else { return 0 }
        return files.filter { $0.pathExtension == "cache" }.count
    }
    
    /// Remove expired entries (memory + disk)
    func pruneExpired() {
        let now = Date()
        let expired = cache.filter { $0.value.expiresAt <= now }
        for key in expired.keys {
            cache.removeValue(forKey: key)
            removeDiskEntry(for: key)
        }
    }
    
    /// Get cache size for debugging
    var count: Int {
        cache.count
    }
    
    // MARK: - Disk Persistence
    
    private static func diskFilename(for key: String) -> String {
        let hash = SHA256.hash(data: Data(key.utf8))
        return hash.compactMap { String(format: "%02x", $0) }.joined().prefix(32) + ".cache"
    }
    
    private func diskPath(for key: String) -> URL {
        Self.diskCacheURL.appendingPathComponent(Self.diskFilename(for: key))
    }
    
    private func writeDiskEntry(_ entry: CacheEntry) {
        Self.ensureDiskDirectoryExists()
        let plistEncoder = PropertyListEncoder()
        plistEncoder.outputFormat = .binary
        if let data = try? plistEncoder.encode(entry) {
            try? data.write(to: diskPath(for: entry.key))
        }
    }

    private func removeDiskEntry(for key: String) {
        try? FileManager.default.removeItem(at: diskPath(for: key))
    }

    private func touchDiskEntry(for key: String) {
        let path = diskPath(for: key).path
        try? FileManager.default.setAttributes([.modificationDate: Date()], ofItemAtPath: path)
    }
    
    /// Load all valid (non-expired) disk entries into memory.
    /// Called from init — must be nonisolated static.
    private static func loadDiskEntries() -> [String: CacheEntry] {
        let fm = FileManager.default
        let url = diskCacheURL
        guard fm.fileExists(atPath: url.path),
              let files = try? fm.contentsOfDirectory(at: url, includingPropertiesForKeys: nil) else {
            return [:]
        }
        
        let plistDecoder = PropertyListDecoder()
        let now = Date()
        var result: [String: CacheEntry] = [:]
        
        for file in files where file.pathExtension == "cache" {
            guard let data = try? Data(contentsOf: file),
                  let entry = try? plistDecoder.decode(CacheEntry.self, from: data) else {
                try? fm.removeItem(at: file) // corrupt, remove
                continue
            }
            
            if entry.expiresAt > now {
                result[entry.key] = entry
            } else {
                try? fm.removeItem(at: file) // expired, clean up
            }
        }
        
        return result
    }

    private func enforceMemoryLimits() {
        guard cache.count > maxMemoryEntries else { return }

        // Evict least-recently-used entries first.
        let orderedKeys = cache
            .map { (key: $0.key, last: $0.value.lastAccessedAt ?? $0.value.expiresAt, expiresAt: $0.value.expiresAt) }
            .sorted { a, b in
                if a.last == b.last { return a.expiresAt < b.expiresAt }
                return a.last < b.last
            }
            .map(\.key)

        let overflow = cache.count - maxMemoryEntries
        guard overflow > 0 else { return }

        for key in orderedKeys.prefix(overflow) {
            // Best-effort: keep cache consistent (memory + disk)
            cache.removeValue(forKey: key)
            removeDiskEntry(for: key)
        }

        // Also prune any entries that are already expired.
        if !cache.isEmpty {
            pruneExpired()
        }
    }

    private func enforceDiskLimits() {
        let fm = FileManager.default
        let url = Self.diskCacheURL
        guard let files = try? fm.contentsOfDirectory(at: url, includingPropertiesForKeys: [
            .fileSizeKey,
            .contentModificationDateKey,
            .isRegularFileKey,
        ]) else { return }

        var entries: [(url: URL, size: Int64, modified: Date)] = []
        entries.reserveCapacity(files.count)

        for file in files where file.pathExtension == "cache" {
            let values = try? file.resourceValues(forKeys: [.fileSizeKey, .contentModificationDateKey, .isRegularFileKey])
            guard values?.isRegularFile == true else { continue }
            let size = Int64(values?.fileSize ?? 0)
            let modified = values?.contentModificationDate ?? Date.distantPast
            entries.append((file, size, modified))
        }

        guard !entries.isEmpty else { return }

        // Sort oldest-first by modification date (which we "touch" on reads).
        entries.sort { $0.modified < $1.modified }

        var totalBytes = entries.reduce(Int64(0)) { $0 + $1.size }
        var totalCount = entries.count

        var idx = 0
        while (totalCount > maxDiskEntries) || (totalBytes > maxDiskBytes) {
            guard idx < entries.count else { break }
            let victim = entries[idx]
            idx += 1

            try? fm.removeItem(at: victim.url)
            totalBytes -= victim.size
            totalCount -= 1
        }
    }

    private static func ensureDiskDirectoryExists() {
        let fm = FileManager.default
        var url = diskCacheURL

        if !fm.fileExists(atPath: url.path) {
            try? fm.createDirectory(at: url, withIntermediateDirectories: true)
        }

        // Treat this as a cache even though it lives in Application Support: don't back it up to iCloud.
        var values = URLResourceValues()
        values.isExcludedFromBackup = true
        try? url.setResourceValues(values)
    }

    private static func migrateLegacyDiskCacheIfNeeded() {
        let fm = FileManager.default
        let legacy = legacyDiskCacheURL
        let target = diskCacheURL

        guard fm.fileExists(atPath: legacy.path) else { return }

        // If the new directory doesn't exist, move the entire legacy folder.
        if !fm.fileExists(atPath: target.path) {
            try? fm.moveItem(at: legacy, to: target)
            return
        }

        // Otherwise, merge any legacy entries that aren't present in the target.
        guard let legacyFiles = try? fm.contentsOfDirectory(at: legacy, includingPropertiesForKeys: nil),
              let targetFiles = try? fm.contentsOfDirectory(at: target, includingPropertiesForKeys: nil) else {
            return
        }

        let existing = Set(targetFiles.map { $0.lastPathComponent })
        for file in legacyFiles where file.pathExtension == "cache" {
            let name = file.lastPathComponent
            guard !existing.contains(name) else { continue }
            try? fm.moveItem(at: file, to: target.appendingPathComponent(name))
        }

        // Best-effort cleanup.
        try? fm.removeItem(at: legacy)
    }
}

// MARK: - Cache Key Generation

extension Endpoint {
    var cacheKey: String {
        let rawKey: String

        // Prefer an explicit override (e.g. month-scoped numerology keys).
        if let explicit = explicitCacheKey {
            rawKey = explicit
        } else {
            var components = [path, method.rawValue]
            
            // Include query parameters in cache key
            for item in queryItems {
                if let value = item.value {
                    components.append("\(item.name)=\(value)")
                }
            }
            
            // Include body hash for POST requests to prevent cache collisions
            if let body = body {
                let encoder = JSONEncoder()
                encoder.outputFormatting = .sortedKeys // Deterministic encoding
                if let bodyData = try? encoder.encode(body),
                   let bodyHash = bodyData.sha256Hash {
                    components.append("body:\(bodyHash)")
                }
            }

            rawKey = components.joined(separator: "|")
        }

        if let hashed = Data(rawKey.utf8).sha256Hash {
            return "cache:\(hashed)"
        }

        return rawKey
    }
}

// MARK: - Data Hashing Extension

private extension Data {
    var sha256Hash: String? {
        let hash = SHA256.hash(data: self)
        return hash.compactMap { String(format: "%02x", $0) }.joined().prefix(16).description
    }
}
