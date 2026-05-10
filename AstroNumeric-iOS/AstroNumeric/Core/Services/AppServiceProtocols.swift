import Foundation
import UserNotifications
#if canImport(WidgetKit)
import WidgetKit
#endif

protocol Clock {
    var now: Date { get }
}

struct SystemClock: Clock {
    var now: Date { Date() }
}

protocol APIService: Sendable {
    func fetch<T: Decodable>(_ endpoint: Endpoint, cachePolicy: CachePolicy) async throws -> T
}

struct LiveAPIService: APIService {
    func fetch<T: Decodable>(_ endpoint: Endpoint, cachePolicy: CachePolicy = .networkFirst) async throws -> T {
        try await APIClient.shared.fetch(endpoint, cachePolicy: cachePolicy)
    }
}

protocol EphemerisService: Sendable {
    func calculateNatalChart(profile: Profile) async throws -> ChartData
    func getNatalSigns(for profile: Profile) async throws -> (moonSign: String?, risingSign: String?)
    func calculateCurrentTransits(date: Date) async throws -> [PlanetPlacement]
    func calculateSunriseSunset(latitude: Double, longitude: Double, date: Date) async throws -> EphemerisEngine.SolarTimes
}

struct LiveEphemerisService: EphemerisService {
    func calculateNatalChart(profile: Profile) async throws -> ChartData {
        try await EphemerisEngine.shared.calculateNatalChart(profile: profile)
    }

    func getNatalSigns(for profile: Profile) async throws -> (moonSign: String?, risingSign: String?) {
        try await EphemerisEngine.shared.getNatalSigns(for: profile)
    }

    func calculateCurrentTransits(date: Date = Date()) async throws -> [PlanetPlacement] {
        try await EphemerisEngine.shared.calculateCurrentTransits(date: date)
    }

    func calculateSunriseSunset(latitude: Double, longitude: Double, date: Date = Date()) async throws -> EphemerisEngine.SolarTimes {
        try await EphemerisEngine.shared.calculateSunriseSunset(latitude: latitude, longitude: longitude, date: date)
    }
}

protocol NotificationSchedulingService {
    func checkPermissionStatus() async -> UNAuthorizationStatus
    func clearBadge() async
    func scheduleDailyReminder(at hour: Int, minute: Int) async
    func scheduleDailyBriefNotification(bullets: [String], personalDay: Int) async
    func listPendingNotifications() async -> [UNNotificationRequest]
}

struct LiveNotificationSchedulingService: NotificationSchedulingService {
    func checkPermissionStatus() async -> UNAuthorizationStatus {
        await NotificationService.shared.checkPermissionStatus()
    }

    func clearBadge() async {
        await NotificationService.shared.clearBadge()
    }

    func scheduleDailyReminder(at hour: Int, minute: Int) async {
        await NotificationService.shared.scheduleDailyReminder(at: hour, minute: minute)
    }

    func scheduleDailyBriefNotification(bullets: [String], personalDay: Int) async {
        await NotificationService.shared.scheduleDailyBriefNotification(bullets: bullets, personalDay: personalDay)
    }

    func listPendingNotifications() async -> [UNNotificationRequest] {
        await NotificationService.shared.listPendingNotifications()
    }
}

protocol WidgetService {
    func updatePlanetaryHours(latitude: Double, longitude: Double) async
    func updateMoonPhase() async
    func refreshMorningBrief(profile: Profile, force: Bool) async throws -> MorningBriefData
    func reloadAllTimelines()
}

struct LiveWidgetService: WidgetService {
    func updatePlanetaryHours(latitude: Double, longitude: Double) async {
        await WidgetDataProvider.shared.updatePlanetaryHours(latitude: latitude, longitude: longitude)
    }

    func updateMoonPhase() async {
        await WidgetDataProvider.shared.updateMoonPhase()
    }

    func refreshMorningBrief(profile: Profile, force: Bool = false) async throws -> MorningBriefData {
        try await WidgetDataProvider.shared.refreshMorningBrief(profile: profile, force: force)
    }

    func reloadAllTimelines() {
        WidgetCenterBridge.reloadAllTimelines()
    }
}

private enum WidgetCenterBridge {
    static func reloadAllTimelines() {
        #if canImport(WidgetKit)
        WidgetCenter.shared.reloadAllTimelines()
        #endif
    }
}

@MainActor
protocol ProfileRepository {
    var profiles: [Profile] { get }
    var activeProfile: Profile? { get }
    func upsert(_ profile: Profile, select: Bool)
    func delete(id: Int)
    func nextLocalProfileId() -> Int
}

@MainActor
final class AppStoreProfileRepository: ProfileRepository {
    private let store: AppStore

    init(store: AppStore = .shared) {
        self.store = store
    }

    var profiles: [Profile] { store.profiles }
    var activeProfile: Profile? { store.activeProfile }

    func upsert(_ profile: Profile, select: Bool = true) {
        store.upsertProfile(profile, select: select)
    }

    func delete(id: Int) {
        store.deleteProfileLocal(id: id)
    }

    func nextLocalProfileId() -> Int {
        store.nextLocalProfileId()
    }
}