import Foundation
import Observation

@Observable
@MainActor
final class AppServices {
    static let live = AppServices()

    let api: APIService
    let ephemeris: EphemerisService
    let notifications: NotificationSchedulingService
    let widgets: WidgetService
    let profiles: ProfileRepository
    let charts: ChartRepository
    let dailyContent: DailyContentRepository
    let journal: JournalRepository
    let cosmicGuide: CosmicGuideRepository
    let alertPreferences: AlertPreferencesRepository
    let clock: Clock
    let crashReporter: CrashReporting
    let refreshCoordinator: AppRefreshCoordinator

    init(
        api: APIService = LiveAPIService(),
        ephemeris: EphemerisService = LiveEphemerisService(),
        notifications: NotificationSchedulingService = LiveNotificationSchedulingService(),
        widgets: WidgetService = LiveWidgetService(),
        profiles: ProfileRepository? = nil,
        journal: JournalRepository? = nil,
        cosmicGuide: CosmicGuideRepository? = nil,
        alertPreferences: AlertPreferencesRepository? = nil,
        clock: Clock = SystemClock(),
        crashReporter: CrashReporting = PrivacyFilteredCrashReporter.shared
    ) {
        self.api = api
        self.ephemeris = ephemeris
        self.notifications = notifications
        self.widgets = widgets
        self.profiles = profiles ?? AppStoreProfileRepository()
        self.clock = clock
        self.crashReporter = crashReporter
        self.charts = DefaultChartRepository(api: api, ephemeris: ephemeris)
        self.dailyContent = DefaultDailyContentRepository(api: api)
        self.journal = journal ?? DefaultJournalRepository.shared
        self.cosmicGuide = cosmicGuide ?? DefaultCosmicGuideRepository(api: api)
        self.alertPreferences = alertPreferences ?? DefaultAlertPreferencesRepository(api: api)
        self.refreshCoordinator = AppRefreshCoordinator(
            widgets: widgets,
            notifications: notifications,
            clock: clock
        )
    }
}