# iOS Real-Device QA Checklist

Last updated: 2026-04-08

## Scope

This checklist covers the parts of AstroNumeric that are not fully proven by simulator builds and unit tests:

- widgets and app group data sharing
- notification permissions, local notifications, and APNs registration
- HealthKit authorization and biometric reads
- background refresh behavior
- release capability/signing alignment

## Current Status

- Native simulator tests are passing.
- Backend tests are passing.
- Release app-group entitlement was added to the main app on 2026-04-08 so widget data sharing is no longer debug-only.
- A release simulator build succeeds after that entitlement fix.

## Preconditions

Before running the checklist:

1. Use a physical iPhone with Developer Mode enabled.
2. Install a signed build from the `AstroNumeric` scheme.
3. Launch the app once and create or select an active profile.
4. Confirm the device has network access.
5. For HealthKit checks, use a device with Health data available.

## Core Smoke Test

1. Launch the app cold.
2. Confirm the app opens to the main tab shell without a crash.
3. Confirm a daily reading, daily features, moon phase, and home dashboard content load for the active profile.
4. Background the app and reopen it.
5. Confirm the app still opens cleanly and the streak/dashboard refresh path does not regress.

Pass criteria:

- no launch crash
- active profile remains selected
- home dashboard renders real content, not placeholders only

## Widgets

Relevant code:

- `AstroNumeric/Core/Services/WidgetDataProvider.swift`
- `AstroWidget/MorningBriefWidget.swift`
- `AstroWidget/DailySummaryWidget.swift`
- `AstroWidget/PlanetaryHourWidget.swift`
- `AstroWidget/MoonPhaseWidget.swift`

Test steps:

1. Add the Morning Brief widget to the Home Screen.
2. Add the Daily Summary widget to the Home Screen.
3. Add the Moon Phase widget to the Home Screen or Lock Screen.
4. Add the Planetary Hour widget to the Home Screen or Lock Screen.
5. Open the app, wait for the dashboard to finish loading, then return to the Home Screen.
6. Confirm widgets show live data instead of fallback text like `Open app to generate...` or `Open app to sync`.
7. Lock the device and confirm Lock Screen widgets render without blank states.
8. Force-close the app, relaunch it, and confirm widget content repopulates.
9. Reboot the device and confirm widgets still load from the shared app group after the app is reopened.

Pass criteria:

- all widgets render non-placeholder data after app refresh
- no widget stays blank because of app-group access failure
- Home Screen and Lock Screen variants both render

## Notifications

Relevant code:

- `AstroNumeric/Core/Services/NotificationService.swift`
- `AstroNumeric/Core/Services/TransitNotificationScheduler.swift`
- `AstroNumeric/Features/Tools/NotificationSettingsView.swift`
- `AstroNumeric/AstroNumericApp.swift`

Test steps:

1. Open the notification settings screen in-app.
2. Enable notifications when prompted.
3. Toggle `Daily Reading Reminder` on and set the time a few minutes ahead.
4. Toggle `Habit Reminder` on and set the time a few minutes ahead.
5. Toggle `Transit Alert` on and set the time a few minutes ahead.
6. Toggle `Timing Tip` on and set the time a few minutes ahead.
7. Enable `Proactive Transit Alerts`.
8. Background the app and wait for the scheduled alerts.
9. Tap each delivered notification and confirm routing:
   - daily reading opens the reading/home path
   - habit reminder can mark complete
   - moon phase opens the tools tab
10. Revoke notification permission in iOS Settings, return to the app, and confirm the app handles the denied state cleanly.

Pass criteria:

- permission prompt appears once and status is reflected correctly
- pending notifications are created for each enabled reminder
- notification taps route to the expected screen/action
- denied permission does not leave the app in a broken toggle state

## APNs Registration

Relevant code:

- `AstroNumeric/AstroNumericApp.swift`
- `AstroNumeric/Core/Services/NotificationService.swift`

Test steps:

1. Grant notification permission on a physical device.
2. Confirm the app registers for remote notifications.
3. Confirm the device token is stored and upload does not fail silently.
4. If backend logging is available, verify `/v2/notifications/register` receives the token.

Pass criteria:

- `didRegisterForRemoteNotificationsWithDeviceToken` fires
- token upload succeeds or produces a visible actionable error

## HealthKit

Relevant code:

- `AstroNumeric/EphemerisEngine/HealthKitBridge.swift`
- `AstroNumeric/Features/CosmicGuide/CosmicGuideVM.swift`
- `AstroNumeric/Features/Profile/ProfileView.swift`

Test steps:

1. Launch the app on a device with HealthKit.
2. Deny Health access on first prompt.
3. Open the profile diagnostics section and confirm the app remains usable.
4. Re-enable Health access from iOS Settings.
5. Relaunch the app.
6. Open Cosmic Guide and trigger a response that should include biometric context.
7. Confirm the app does not crash if some metrics are missing.

Pass criteria:

- deny path is safe
- allow path reads data without blocking app launch
- Cosmic Guide works with and without biometric data

## Background Refresh

Relevant code:

- `AstroNumeric/Core/Services/TransitNotificationScheduler.swift`
- `AstroNumeric/Core/Services/CachePrewarmScheduler.swift`
- `AstroNumeric/AstroNumericApp.swift`
- `AstroNumeric/Info.plist`

Test steps:

1. Launch the app and let the dashboard load completely.
2. Background the app for several hours, ideally across a local day change.
3. Reopen the app and confirm dashboard content updates to the correct local day.
4. Confirm widgets refresh after foreground activity.
5. Confirm pending transit alerts are still present after the app has been backgrounded.
6. Confirm no duplicate flood of transit notifications is scheduled.

Pass criteria:

- background task scheduling does not break app launch
- daily content rolls over on the user timezone day boundary
- transit alerts remain deduplicated

## Release Validation

Relevant files:

- `AstroNumeric/AstroNumeric.entitlements`
- `AstroNumeric/AstroNumericDebug.entitlements`
- `AstroWidget/AstroWidget.entitlements`

Checks:

1. Confirm the main app and widget extension both include `group.com.astromeric.shared`.
2. Confirm a Release device build still signs successfully.
3. Confirm widgets work in a Release or TestFlight-style install, not only Debug.

Pass criteria:

- release entitlements match the widget data-sharing requirement
- widget behavior is identical between Debug and Release installs

## Product-Scope Questions

These capabilities exist in entitlements or resources, but no runtime iOS flow was found in the native app code during this pass:

- Sign in with Apple UI flow
- StoreKit purchase / restore flow

Action:

1. Confirm whether these features are intentionally out of scope for the current app.
2. If they are not in scope, remove unused capabilities and assets.
3. If they are in scope, add an explicit QA checklist after the implementation exists.

## Exit Criteria

The device pass is complete when:

1. widgets render live data on device
2. local notifications fire and route correctly
3. APNs token registration succeeds
4. HealthKit deny and allow flows both behave correctly
5. background refresh does not regress local-day content
6. release install behaves the same as debug for widget sharing
