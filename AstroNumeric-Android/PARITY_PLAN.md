# AstroNumeric Android — iOS Parity Audit & Plan

_Audit date: 2026-06-15. Compares the Android app (`AstroNumeric-Android`, Kotlin/Jetpack Compose) against the native iOS app (`AstroNumeric-iOS`, Swift/SwiftUI)._

## Executive summary

The Android app is **much closer to parity than its `0.1.0` version suggests** — it's a mature, well-architected Compose app (118 Kotlin files) that already matches iOS on the hard parts: an on-device Swiss Ephemeris engine with bundled data, Health Connect, FCM push, four home-screen widgets, billing, 5-locale localization, Room + DataStore persistence, and the full core feature set (readings, charts, numerology, compatibility, tools, learn, journal with voice, habits, cosmic guide, explore, profile, onboarding).

It is **ahead of iOS in one area**: in-app billing / Premium (Android has Play Billing + a `PremiumScreen`; iOS currently ships no in-app purchase).

The remaining gaps are a small number of **features** plus a **release-readiness** delta. Estimated effort to true parity + store-ready: **~2–3 focused weeks**.

## Parity matrix

| Area                                                                                                       | iOS                                          | Android                                                                                 | Status                            |
| ---------------------------------------------------------------------------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------- | --------------------------------- |
| On-device Swiss Ephemeris (+ bundled `.se1`)                                                               | ✅                                           | ✅ (assets/ephemeris, returns `Result.failure` — no fabrication)                        | **Parity**                        |
| Daily/weekly/monthly readings                                                                              | ✅                                           | ✅                                                                                      | Parity                            |
| Natal chart                                                                                                | ✅                                           | ✅                                                                                      | Parity                            |
| Numerology (core + cycles)                                                                                 | ✅                                           | ✅                                                                                      | Parity                            |
| Compatibility / Relationships / Friends                                                                    | ✅                                           | ✅                                                                                      | Parity                            |
| Tools (moon, tarot, oracle, timing, year-ahead, affirmation, daily features, temporal matrix, birthstones) | ✅                                           | ✅                                                                                      | Parity                            |
| Learn (glossary, lessons)                                                                                  | ✅                                           | ✅                                                                                      | Parity                            |
| Journal (+ voice)                                                                                          | ✅                                           | ✅                                                                                      | Parity                            |
| Habits                                                                                                     | ✅                                           | ✅                                                                                      | Parity                            |
| Cosmic Guide (AI) + Health + Calendar context                                                              | ✅                                           | ✅ (HealthConnectBridge, CalendarContext, BioCosmicCorrelator)                          | Parity                            |
| Home-screen widgets                                                                                        | ✅ AstroWidget                               | ✅ 4 providers (DailySummary, PlanetaryHour, MoonPhase, MorningBrief)                   | Parity (verify count/types match) |
| Push notifications                                                                                         | ✅                                           | ✅ FCM                                                                                  | Parity                            |
| Localization                                                                                               | ✅ en/es/fr/ne/ro                            | ✅ en/es/fr/ne/ro                                                                       | Parity                            |
| In-app purchase / Premium                                                                                  | ❌ none                                      | ✅ Play Billing + PremiumScreen                                                         | **Android ahead**                 |
| **Advanced charts** (composite, synastry, progressions)                                                    | ✅                                           | ✅                                                                                      | Parity                            |
| **Advanced charts** (solar arc, profections, lunar return, relocation, declinations, fixed stars)          | ✅ (`AdvancedChartsView`, backend-supported) | ✅ implemented (data + screens + nav; pending build verification & string localization) | **Closed**                        |
| **App shortcuts / voice intents**                                                                          | ✅ Siri App Intents (`CosmicIntents`)        | ❌ none                                                                                 | **Gap (P2)**                      |
| **Crash reporting**                                                                                        | ✅ MetricKit reporter + SDK hook             | ❌ none (Firebase present, Crashlytics not added)                                       | **Gap (P1)**                      |
| **Automated tests**                                                                                        | ✅ 5 XCTest targets                          | ❌ 0                                                                                    | **Gap (P1)**                      |
| Privacy/compliance artifact                                                                                | ✅ `PrivacyInfo.xcprivacy`                   | ⚠️ Play Data Safety form is console-side; verify permission justifications              | **Gap (P0 for release)**          |
| Release maturity (version)                                                                                 | 1.0.0 (build 4)                              | 0.1.0 (code 1)                                                                          | **Gap (P0)**                      |

## Prioritized gaps & plan

### P0 — Release readiness (do first; blocks a store launch)

1. **Play Data Safety + permissions justification.** The app requests Health (heart rate, resting HR, sleep, steps, calories), Calendar, Microphone, exact alarms, and notifications. Each must be declared/justified in the Play Console Data Safety form and (for Health Connect) meet Google's health-data policy + in-app privacy disclosure. This is the Android analogue of the iOS privacy-manifest work. _Effort: 0.5 day + console submission._
2. **Version + build config for release.** Bump `versionName` to `1.0.0` / `versionCode` appropriately; confirm `signingConfigs` (release keystore), `isMinifyEnabled = true` with R8/ProGuard rules validated, and a release `API_BASE_URL` default pointing at the production backend over https. _Effort: 0.5 day._
3. **Explicit network security.** Add a `network_security_config.xml` that disallows cleartext (defense-in-depth; targetSdk 35 already defaults to no cleartext) and pins the prod origin set. _Effort: 0.25 day._

### P1 — Feature & quality parity

4. **Advanced chart types.** ✅ DONE (pending build verification). All six types
   (solar arc, lunar return, relocation, profections, declinations, fixed stars)
   are implemented: models in `ChartModels.kt`, endpoints/wrappers in
   `AstroRemoteData.kt`, screens in `AdvancedChartScreens.kt`, and nav + entry
   buttons in `ChartsTabs.kt`/`AstroRouteGraphs.kt`. Remaining: `./gradlew
assembleDebug` to compile-check, and move the new screens' inline English
   strings into `strings.xml` for localization.
5. **Crash reporting (Crashlytics).** Firebase is already integrated (BOM 33.7.0). Add `firebase-crashlytics` + Gradle plugin, with a privacy filter that strips birth/chart/journal data from logs (mirror iOS `PrivacyFilteredCrashReporter`), and wire mapping-file (ProGuard) upload in CI. _Effort: 1 day._
6. **Automated tests.** Android currently has 0 test files vs 5 on iOS. Add JVM unit tests for the highest-value, deterministic logic: `LocalSwissEphemerisEngine` (chart/transit math vs known values), numerology calculations, and repository parsing. Target the same coverage areas as the iOS `EphemerisEngineTests`. _Effort: 2–3 days._

### P2 — Nice-to-have / platform polish

7. **App Shortcuts + Assistant App Actions.** Add static/dynamic shortcuts (e.g., "Today's reading", "Birth chart", "Compatibility") and optionally Google Assistant App Actions to mirror the iOS Siri intents. _Effort: 1–2 days._
8. **Ephemeris diagnostics.** The engine already fails safely (`Result.failure`, no fabricated data). Add a one-time log/diagnostic when `assets/ephemeris/*.se1` can't be opened, mirroring the iOS `ephemerisDataAvailable` signal. _Effort: 0.25 day._
9. **Widget parity check.** Confirm the four Android widgets map to the iOS widget set in content and refresh cadence; add any missing widget. _Effort: 0.5–1 day._

## Suggested sequencing

- **Week 1 (release-readiness):** P0 items (Data Safety, version/signing/R8, network config) + Crashlytics (P1 #5) + ephemeris diagnostic (P2 #8). Outcome: a store-submittable, observable build.
- **Week 2 (feature parity):** Advanced chart types (P1 #4) + automated tests (P1 #6).
- **Week 3 (polish):** App Shortcuts/Assistant (P2 #7) + widget parity (P2 #9) + a manual QA pass mirroring `AstroNumeric-iOS/ProductionReadinessChecklist.md`.

## Reverse note (iOS, out of scope here)

Android has in-app billing and a Premium screen that iOS lacks. If monetization is intended on both platforms, iOS needs a StoreKit/IAP implementation to reach parity in the other direction — track separately.

## Verification

- Build: `cd AstroNumeric-Android && ./gradlew assembleRelease lintRelease testDebugUnitTest`.
- Backend contract: the shared `scripts/smoke_test.py` already validates the endpoints both apps consume.
- Manual QA: run the iOS production-readiness checklist flows on Android (profile creation across exact/approximate/unknown birth time, daily guide, chart render, numerology, compatibility, cosmic guide, widgets, notifications, offline/backend-unavailable).
