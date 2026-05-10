import Foundation
import SQLite3

actor LocalDomainDatabase {
    static let shared = LocalDomainDatabase()

    private let databaseURL: URL

    private init() {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        databaseURL = base
            .appendingPathComponent("com.astromeric", isDirectory: true)
            .appendingPathComponent("local_domain.sqlite", isDirectory: false)
    }

    func loadProfiles() -> [Profile]? {
        guard let json = loadJSON(domain: "profiles", key: "local_profiles.v1"),
              let data = json.data(using: .utf8) else {
            return nil
        }
        return try? JSONDecoder().decode([Profile].self, from: data)
    }

    func saveProfiles(_ profiles: [Profile]) {
        guard let data = try? JSONEncoder().encode(profiles),
              let json = String(data: data, encoding: .utf8) else {
            return
        }
        saveJSON(json, domain: "profiles", key: "local_profiles.v1")
    }

    func removeProfiles() {
        delete(domain: "profiles", key: "local_profiles.v1")
    }

    func load<T: Decodable>(_ type: T.Type, domain: String, key: String) -> T? {
        guard let json = loadJSON(domain: domain, key: key),
              let data = json.data(using: .utf8) else {
            return nil
        }
        return try? JSONDecoder().decode(type, from: data)
    }

    func save<T: Encodable>(_ value: T, domain: String, key: String) {
        guard let data = try? JSONEncoder().encode(value),
              let json = String(data: data, encoding: .utf8) else {
            return
        }
        saveJSON(json, domain: domain, key: key)
    }

    func remove(domain: String, key: String) {
        delete(domain: domain, key: key)
    }

    private func loadJSON(domain: String, key: String) -> String? {
        var db: OpaquePointer?
        guard open(&db) else { return nil }
        defer { sqlite3_close(db) }

        let sql = "SELECT json FROM domain_records WHERE domain = ? AND record_key = ? LIMIT 1"
        var statement: OpaquePointer?
        guard sqlite3_prepare_v2(db, sql, -1, &statement, nil) == SQLITE_OK else { return nil }
        defer { sqlite3_finalize(statement) }

        sqlite3_bind_text(statement, 1, domain, -1, SQLITE_TRANSIENT)
        sqlite3_bind_text(statement, 2, key, -1, SQLITE_TRANSIENT)

        guard sqlite3_step(statement) == SQLITE_ROW,
              let text = sqlite3_column_text(statement, 0) else {
            return nil
        }
        return String(cString: text)
    }

    private func saveJSON(_ json: String, domain: String, key: String) {
        var db: OpaquePointer?
        guard open(&db) else { return }
        defer { sqlite3_close(db) }

        let sql = """
        INSERT INTO domain_records(domain, record_key, json, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(domain, record_key) DO UPDATE SET
            json = excluded.json,
            updated_at = excluded.updated_at
        """
        var statement: OpaquePointer?
        guard sqlite3_prepare_v2(db, sql, -1, &statement, nil) == SQLITE_OK else { return }
        defer { sqlite3_finalize(statement) }

        sqlite3_bind_text(statement, 1, domain, -1, SQLITE_TRANSIENT)
        sqlite3_bind_text(statement, 2, key, -1, SQLITE_TRANSIENT)
        sqlite3_bind_text(statement, 3, json, -1, SQLITE_TRANSIENT)
        sqlite3_bind_double(statement, 4, Date().timeIntervalSince1970)
        sqlite3_step(statement)
    }

    private func delete(domain: String, key: String) {
        var db: OpaquePointer?
        guard open(&db) else { return }
        defer { sqlite3_close(db) }

        let sql = "DELETE FROM domain_records WHERE domain = ? AND record_key = ?"
        var statement: OpaquePointer?
        guard sqlite3_prepare_v2(db, sql, -1, &statement, nil) == SQLITE_OK else { return }
        defer { sqlite3_finalize(statement) }

        sqlite3_bind_text(statement, 1, domain, -1, SQLITE_TRANSIENT)
        sqlite3_bind_text(statement, 2, key, -1, SQLITE_TRANSIENT)
        sqlite3_step(statement)
    }

    private func open(_ db: inout OpaquePointer?) -> Bool {
        let directory = databaseURL.deletingLastPathComponent()
        if !FileManager.default.fileExists(atPath: directory.path) {
            try? FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        }

        guard sqlite3_open(databaseURL.path, &db) == SQLITE_OK else { return false }
        let sql = """
        CREATE TABLE IF NOT EXISTS domain_records (
            domain TEXT NOT NULL,
            record_key TEXT NOT NULL,
            json TEXT NOT NULL,
            updated_at REAL NOT NULL,
            PRIMARY KEY(domain, record_key)
        )
        """
        return sqlite3_exec(db, sql, nil, nil, nil) == SQLITE_OK
    }
}

private let SQLITE_TRANSIENT = unsafeBitCast(-1, to: sqlite3_destructor_type.self)