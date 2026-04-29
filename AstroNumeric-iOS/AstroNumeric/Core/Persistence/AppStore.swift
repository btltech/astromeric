// AppStore.swift
// Global state management with @Observable (iOS 17+)

import SwiftUI
import Observation

enum AppConfig {
    /// Personal mode keeps the app fully usable without sign-in/premium gating.
    /// Set `PERSONAL_MODE` to `false` in Info.plist when you're ready to gate features.
    static var personalMode: Bool {
        // Default to personal mode for safety (no gating) when the key is missing.
        if let value = Bundle.main.object(forInfoDictionaryKey: "PERSONAL_MODE") as? Bool {
            return value
        }
        return true
    }
}

enum ReadingTone: String {
    case veryPractical = "very_practical"
    case balancedPractical = "balanced_practical"
    case balancedMystical = "balanced_mystical"
    case veryMystical = "very_mystical"

    var label: String {
        switch self {
        case .veryPractical:
            return "Very Practical"
        case .balancedPractical:
            return "Balanced Practical"
        case .balancedMystical:
            return "Balanced Mystical"
        case .veryMystical:
            return "Very Mystical"
        }
    }

    var framingDescription: String {
        switch self {
        case .veryPractical:
            return "Direct language with minimal symbolism."
        case .balancedPractical:
            return "Clear advice with light symbolic framing."
        case .balancedMystical:
            return "Astrology-forward language with grounded takeaways."
        case .veryMystical:
            return "Most symbolic and atmospheric reading style."
        }
    }
}

@Observable
final class AppStore {
    static let shared = AppStore()
    
    // MARK: - Session State
    
    /// Currently selected profile ID (persisted)
    var selectedProfileId: Int? {
        didSet {
            if let id = selectedProfileId {
                UserDefaults.standard.set(id, forKey: "selectedProfileId")
            } else {
                UserDefaults.standard.removeObject(forKey: "selectedProfileId")
            }
            // Fetch natal signs for newly selected profile
            if let id = selectedProfileId, let profile = profiles.first(where: { $0.id == id }) {
                Task { await fetchNatalSigns(for: profile) }
            }
        }
    }
    
    /// All profiles stored on-device (guest/personal mode) and optionally synced (when signed in)
    var profiles: [Profile] = [] {
        didSet { persistProfiles() }
    }
    
    /// Currently active profile
    var selectedProfile: Profile? {
        if let id = selectedProfileId, let match = profiles.first(where: { $0.id == id }) {
            return match
        }
        return profiles.first
    }
    
    /// The currently active profile (selected or session)
    /// Use this instead of `selectedProfile ?? sessionProfile` throughout views
    var activeProfile: Profile? {
        selectedProfile
    }

    /// True after persisted local profiles have been loaded.
    var hasCompletedInitialLoad = false
    
    // MARK: - Natal Chart Sign Cache
    
    /// Cached natal chart signs keyed by profile ID
    private(set) var natalSignsCache: [Int: NatalSigns] = [:]
    
    /// Natal signs for the currently active profile
    var activeMoonSign: String? {
        guard let id = selectedProfile?.id ?? profiles.first?.id else { return nil }
        return natalSignsCache[id]?.moonSign
    }
    
    var activeRisingSign: String? {
        guard let id = selectedProfile?.id ?? profiles.first?.id else { return nil }
        return natalSignsCache[id]?.risingSign
    }
    
    // MARK: - Auth Status (local-first mode keeps all profile data on device)
    var isAuthenticated: Bool { false }
    
    // MARK: - Preferences
    
    /// App theme
    var theme: AppTheme = .default
    
    /// Tone preference (0 = Practical, 100 = Mystical)
    /// Stored property so `@Observable` tracks it. UserDefaults is the durable store.
    var tonePreference: Double = UserDefaults.standard.object(forKey: "tonePreference") as? Double ?? 50 {
        didSet { UserDefaults.standard.set(tonePreference, forKey: "tonePreference") }
    }

    var readingTone: ReadingTone {
        switch tonePreference {
        case 0..<25:
            return .veryPractical
        case 25..<50:
            return .balancedPractical
        case 50..<75:
            return .balancedMystical
        default:
            return .veryMystical
        }
    }
    
    /// Daily reminder enabled
    var dailyReminderEnabled: Bool = UserDefaults.standard.bool(forKey: "dailyReminderEnabled") {
        didSet { UserDefaults.standard.set(dailyReminderEnabled, forKey: "dailyReminderEnabled") }
    }

    /// Hide identifying birth/profile details in the UI and sharing surfaces.
    var hideSensitiveDetailsEnabled: Bool = UserDefaults.standard.bool(forKey: "hideSensitiveDetailsEnabled") {
        didSet { UserDefaults.standard.set(hideSensitiveDetailsEnabled, forKey: "hideSensitiveDetailsEnabled") }
    }
    
    /// Reminder cadence
    var reminderCadence: ReminderCadence = .daily
    
    // MARK: - Accessibility
    
    /// High contrast mode for better visibility
    var highContrastEnabled: Bool = UserDefaults.standard.bool(forKey: "highContrastEnabled") {
        didSet { UserDefaults.standard.set(highContrastEnabled, forKey: "highContrastEnabled") }
    }
    
    /// Large text mode for better readability
    var largeTextEnabled: Bool = UserDefaults.standard.bool(forKey: "largeTextEnabled") {
        didSet { UserDefaults.standard.set(largeTextEnabled, forKey: "largeTextEnabled") }
    }
    
    // MARK: - Streak
    
    /// Current streak count
    var streakCount: Int = UserDefaults.standard.integer(forKey: "streakCount") {
        didSet { UserDefaults.standard.set(streakCount, forKey: "streakCount") }
    }
    
    /// Last visit date
    var lastVisitDate: Date? = UserDefaults.standard.object(forKey: "lastVisitDate") as? Date {
        didSet { UserDefaults.standard.set(lastVisitDate, forKey: "lastVisitDate") }
    }
    
    // MARK: - Initialization
    
    private let isUITesting: Bool
    private var profilesHydrated = false
    private var profilesHydrationTask: Task<Void, Never>?
    private var persistProfilesTask: Task<Void, Never>?

    private init() {
#if DEBUG
        isUITesting = ProcessInfo.processInfo.arguments.contains("-ui_testing")
#else
        isUITesting = false
#endif

        // Load persisted profile ID
        let savedId = UserDefaults.standard.integer(forKey: "selectedProfileId")
        if savedId != 0 {
            selectedProfileId = savedId
        }
        
        // Profiles are hydrated lazily from disk in loadInitialData() to avoid
        // blocking launch on UserDefaults or file IO.

#if DEBUG
        configureForUITestingIfNeeded()
#endif
    }

#if DEBUG
    private func configureForUITestingIfNeeded() {
        let args = ProcessInfo.processInfo.arguments
        guard args.contains("-ui_testing") else { return }

        if args.contains("-ui_testing_reset") {
            if let bundleId = Bundle.main.bundleIdentifier {
                UserDefaults.standard.removePersistentDomain(forName: bundleId)
            }
            profiles = []
            selectedProfileId = nil
        }

        hideSensitiveDetailsEnabled = args.contains("-ui_testing_hide_sensitive")

        let wantsTwoProfiles = args.contains("-ui_testing_profiles_2")
        let wantsOneProfile = args.contains("-ui_testing_profile") || args.contains("-ui_testing_profiles_1") || !wantsTwoProfiles

        let primary = Profile(
            id: -1,
            name: "ABIOLA BOLAJI",
            dateOfBirth: "1977-07-02",
            timeOfBirth: "12:00:00",
            timeConfidence: "exact",
            placeOfBirth: "Lagos, Nigeria",
            latitude: 6.5244,
            longitude: 3.3792,
            timezone: "Africa/Lagos",
            houseSystem: "Placidus"
        )

        if wantsTwoProfiles {
            let secondary = Profile(
                id: -2,
                name: "Test Partner",
                dateOfBirth: "1980-01-15",
                timeOfBirth: "09:30:00",
                timeConfidence: "exact",
                placeOfBirth: "New York, USA",
                latitude: 40.7128,
                longitude: -74.0060,
                timezone: "America/New_York",
                houseSystem: "Placidus"
            )
            profiles = [primary, secondary]
            selectedProfileId = primary.id
        } else if wantsOneProfile {
            profiles = [primary]
            selectedProfileId = primary.id
        } else {
            profiles = []
            selectedProfileId = nil
        }

        // UI tests seed profiles directly.
        profilesHydrated = true
    }
#endif
    
    // MARK: - Local Profile Persistence
    
    private let profilesKey = "astromeric.local_profiles.v1" // legacy UserDefaults key (migration)
    
    private func persistProfiles() {
        let snapshot = profiles
        persistProfilesTask?.cancel()
        persistProfilesTask = Task(priority: .utility) {
            await LocalProfilesStore.shared.save(snapshot)
        }
    }
    
    private func migrateLegacySessionProfileIfNeeded() {
        guard let data = UserDefaults.standard.data(forKey: "sessionProfile"),
              let legacy = try? JSONDecoder().decode(Profile.self, from: data) else {
            return
        }
        
        // Merge legacy into profiles and select it if nothing is selected.
        upsertProfile(legacy, select: selectedProfileId == nil)
        UserDefaults.standard.removeObject(forKey: "sessionProfile")
    }

    @MainActor
    private func ensureProfilesHydrated() async {
        guard !profilesHydrated else { return }
        guard !isUITesting else { return }

        if let task = profilesHydrationTask {
            await task.value
            return
        }

        profilesHydrationTask = Task(priority: .utility) {
            let loaded = await LocalProfilesStore.shared.load(migratingFromUserDefaultsKey: profilesKey)
            await MainActor.run {
                self.profiles = loaded
                self.migrateLegacySessionProfileIfNeeded()
                self.profilesHydrated = true
            }
        }

        if let task = profilesHydrationTask {
            await task.value
        }
    }
    
    /// Generate the next local-only profile id (negative to avoid collisions with server ids).
    func nextLocalProfileId() -> Int {
        let minId = profiles.map(\.id).min() ?? 0
        return min(minId - 1, -1)
    }
    
    /// Insert or update a profile in local storage and optionally select it.
    func upsertProfile(_ profile: Profile, select: Bool = true) {
        if let idx = profiles.firstIndex(where: { $0.id == profile.id }) {
            profiles[idx] = profile
        } else {
            profiles.insert(profile, at: 0)
        }
        if select { selectedProfileId = profile.id }
    }
    
    func deleteProfileLocal(id: Int) {
        profiles.removeAll { $0.id == id }
        if selectedProfileId == id {
            selectedProfileId = profiles.first?.id
        }
    }
    
    // MARK: - Actions
    
    func loadInitialData() async {
        await ensureProfilesHydrated()
        hasCompletedInitialLoad = true

        // Local-first mode does not require auth, tokens, or server profiles.
        updateStreak()
        
        // Fetch natal signs for active profile
        if let profile = selectedProfile ?? profiles.first {
            await fetchNatalSigns(for: profile)
        }
    }
    
    // MARK: - Natal Sign Fetching
    
    /// Fetch and cache moon/rising signs — local-first, API fallback
    func fetchNatalSigns(for profile: Profile) async {
        // Skip if already cached
        guard natalSignsCache[profile.id] == nil else { return }
        let profileLabel = profile.displayName(
            hideSensitive: hideSensitiveDetailsEnabled,
            role: .activeUser
        )
        
        // LOCAL-FIRST: Try Swiss Ephemeris on-device
        do {
            let signs = try await EphemerisEngine.shared.getNatalSigns(for: profile)
            await MainActor.run {
                self.natalSignsCache[profile.id] = NatalSigns(
                    moonSign: signs.moonSign,
                    risingSign: signs.risingSign
                )
            }
            DebugLog.trace("Natal signs (local) cached for \(profileLabel): Moon=\(signs.moonSign ?? "nil"), Rising=\(signs.risingSign ?? "nil")")
            return
        } catch {
            DebugLog.log("Local ephemeris failed for natal signs, falling back to API: \(error)")
        }
        
        // FALLBACK: API
        do {
            let response: V2ApiResponse<ChartData> = try await APIClient.shared.fetch(
                .natalChart(profile: profile)
            )
            
            let moonSign = response.data.planets.first(where: { $0.name == "Moon" })?.sign
            let risingSign = response.data.planets.first(where: {
                $0.name == "Ascendant" || $0.name == "ASC" || $0.name == "Rising"
            })?.sign
            
            await MainActor.run {
                self.natalSignsCache[profile.id] = NatalSigns(
                    moonSign: moonSign,
                    risingSign: risingSign
                )
            }
            DebugLog.trace("Natal signs (API) cached for \(profileLabel): Moon=\(moonSign ?? "nil"), Rising=\(risingSign ?? "nil")")
        } catch {
            DebugLog.log("Failed to fetch natal signs for \(profileLabel): \(error)")
        }
    }
    
    func updateStreak() {
        let tz = TimeZone(identifier: activeProfile?.timezone ?? "") ?? TimeZone(identifier: "UTC")!
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = tz
        let today = calendar.startOfDay(for: Date())
        
        if let lastVisit = lastVisitDate {
            let lastVisitDay = calendar.startOfDay(for: lastVisit)
            let daysDiff = calendar.dateComponents([.day], from: lastVisitDay, to: today).day ?? 0
            
            if daysDiff == 0 {
                // Same day, no change
            } else if daysDiff == 1 {
                // Consecutive day
                streakCount += 1
            } else {
                // Streak broken
                streakCount = 1
            }
        } else {
            streakCount = 1
        }
        
        lastVisitDate = Date()
    }
}

// MARK: - Local Profiles Store (Disk-backed)

private actor LocalProfilesStore {
    static let shared = LocalProfilesStore()

    private init() {}

    private func fileURL() -> URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        return base
            .appendingPathComponent("com.astromeric", isDirectory: true)
            .appendingPathComponent("local_profiles.v1.json", isDirectory: false)
    }

    func load(migratingFromUserDefaultsKey legacyKey: String) -> [Profile] {
        let url = fileURL()
        let fm = FileManager.default

        if let data = try? Data(contentsOf: url),
           let decoded = try? JSONDecoder().decode([Profile].self, from: data) {
            return decoded
        }

        // Legacy migration: UserDefaults blob -> disk file.
        if let legacy = UserDefaults.standard.data(forKey: legacyKey),
           let decoded = try? JSONDecoder().decode([Profile].self, from: legacy) {
            save(decoded)
            UserDefaults.standard.removeObject(forKey: legacyKey)
            return decoded
        }

        // Ensure directory exists for later writes.
        let dir = url.deletingLastPathComponent()
        if !fm.fileExists(atPath: dir.path) {
            try? fm.createDirectory(at: dir, withIntermediateDirectories: true)
        }

        return []
    }

    func save(_ profiles: [Profile]) {
        let url = fileURL()
        let fm = FileManager.default
        let dir = url.deletingLastPathComponent()

        if !fm.fileExists(atPath: dir.path) {
            try? fm.createDirectory(at: dir, withIntermediateDirectories: true)
        }

        guard !profiles.isEmpty else {
            try? fm.removeItem(at: url)
            return
        }

        guard let data = try? JSONEncoder().encode(profiles) else { return }
        try? data.write(to: url, options: [.atomic])
    }
}

// MARK: - Natal Signs

struct NatalSigns {
    let moonSign: String?
    let risingSign: String?
}

// MARK: - Supporting Types

enum AppTheme: String, CaseIterable, Codable {
    case `default` = "default"
    case ocean = "ocean"
    case midnight = "midnight"
    case sage = "sage"
    
    var displayName: String {
        switch self {
        case .default: return "Cosmic Purple"
        case .ocean: return "Deep Ocean"
        case .midnight: return "Midnight Blue"
        case .sage: return "Sage Green"
        }
    }
}

enum ReminderCadence: String, CaseIterable, Codable {
    case daily = "daily"
    case weekdays = "weekdays"
    case weekly = "weekly"
    
    var displayName: String {
        switch self {
        case .daily: return "Every Day"
        case .weekdays: return "Weekdays Only"
        case .weekly: return "Once a Week"
        }
    }
}
