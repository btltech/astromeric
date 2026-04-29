// MoonPhaseActivity.swift
// Live Activity attributes + manager for the Moon Phase Dynamic Island / Lock Screen tile.
//
// MANUAL XCODE SETUP REQUIRED (one-time, ~5 minutes):
//   1. File → New → Target… → Widget Extension. Name it "AstroNumericWidgets".
//      Check "Include Live Activity".
//   2. In the host app target's `Info.plist`, add:
//        NSSupportsLiveActivities = YES
//   3. Move (or symlink) this file into the new Widget Extension target as well so the
//      attributes type is shared. You'll also create a `Widget` whose `ActivityConfiguration`
//      uses `MoonPhaseActivityAttributes`.
//   4. Call `MoonPhaseLiveActivityManager.shared.start(...)` after the user has a profile and
//      the moon phase is known (e.g. from `HomeVM` once `vm.moonPhaseName` resolves).
//
// This file compiles inside the host app today; it just won't show a Live Activity until the
// extension target exists.

import Foundation
#if canImport(ActivityKit)
import ActivityKit
#endif

#if canImport(ActivityKit)
@available(iOS 16.2, *)
public struct MoonPhaseActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        public var phaseName: String
        public var phaseEmoji: String
        public var illuminationPercent: Int
        public var nextPhaseName: String
        public var nextPhaseDate: Date
        public var headline: String

        public init(
            phaseName: String,
            phaseEmoji: String,
            illuminationPercent: Int,
            nextPhaseName: String,
            nextPhaseDate: Date,
            headline: String
        ) {
            self.phaseName = phaseName
            self.phaseEmoji = phaseEmoji
            self.illuminationPercent = illuminationPercent
            self.nextPhaseName = nextPhaseName
            self.nextPhaseDate = nextPhaseDate
            self.headline = headline
        }
    }

    public var profileName: String

    public init(profileName: String) {
        self.profileName = profileName
    }
}

@available(iOS 16.2, *)
public final class MoonPhaseLiveActivityManager {
    public static let shared = MoonPhaseLiveActivityManager()
    private init() {}

    private var currentActivity: Activity<MoonPhaseActivityAttributes>?

    public var isAvailable: Bool {
        ActivityAuthorizationInfo().areActivitiesEnabled
    }

    public func start(
        profileName: String,
        state: MoonPhaseActivityAttributes.ContentState
    ) {
        guard isAvailable else { return }
        // Only one Live Activity per type at a time.
        if currentActivity != nil { return }

        let attributes = MoonPhaseActivityAttributes(profileName: profileName)
        do {
            currentActivity = try Activity<MoonPhaseActivityAttributes>.request(
                attributes: attributes,
                content: .init(state: state, staleDate: nil),
                pushType: nil
            )
        } catch {
            #if DEBUG
            print("MoonPhaseLiveActivity start failed: \(error)")
            #endif
        }
    }

    public func update(_ state: MoonPhaseActivityAttributes.ContentState) async {
        guard let activity = currentActivity else { return }
        await activity.update(.init(state: state, staleDate: nil))
    }

    public func end() async {
        guard let activity = currentActivity else { return }
        await activity.end(nil, dismissalPolicy: .immediate)
        currentActivity = nil
    }
}
#endif
