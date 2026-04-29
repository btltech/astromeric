import Foundation

enum AppGroupStore {
    static let suiteName = "group.com.astromeric.shared"

    private static let cachedDefaults: UserDefaults? = {
        guard FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: suiteName) != nil else {
            return nil
        }
        return UserDefaults(suiteName: suiteName)
    }()

    static var sharedDefaults: UserDefaults? {
        cachedDefaults
    }
}