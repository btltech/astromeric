# AstroNumeric Android — Play Release Checklist

Companion to `PARITY_PLAN.md`. Tracks what was done in the parity pass and what
remains before a Play Store release. Items marked ☐ are console-side or require a
verified build (couldn't be done from the code environment).

## Done in this pass (code)

- ✅ Version bumped to `1.0.0` (versionCode `2`).
- ✅ Crashlytics wired: `firebase-crashlytics` plugin + dependency, `CrashReporter`
  (redacts only custom-key values whose key names match its sensitive list; log
  messages and exception text are sent as-is — see its KDoc), initialized in
  `AstroNumericApplication` (collection off in DEBUG).
- ✅ HTTPS-only enforced via `res/xml/network_security_config.xml`
  (`usesCleartextTraffic=false`).
- ✅ ProGuard/R8 keep rules staged in `proguard-rules.pro` (Gson models, Retrofit,
  coroutines) — ready for when minification is enabled.
- ✅ App Shortcuts (`res/xml/shortcuts.xml`): Reading, Numerology, Compatibility,
  deep-linking through the existing `launch_route` path.
- ✅ Ephemeris diagnostic: missing bundled `.se1` asset now logs loudly and fails
  (never fabricates positions).

## Before release (console / verified build)

- ☐ **Data Safety form (Play Console).** Declare data the app handles:
  - Personal info: **Name** (app functionality, on-device + sent to backend for chart calc).
  - Location: **birthplace lat/long** the user enters (app functionality).
  - Health & fitness: **heart rate, resting heart rate, sleep, steps, calories**
    via Health Connect — declare purpose (personalized insights), state whether it
    leaves the device, and link the privacy policy. Health Connect also requires a
    visible in-app privacy disclosure.
  - Audio: **voice journal** recordings (microphone) — declare handling.
  - Confirm encryption-in-transit (yes, HTTPS) and a data-deletion path.
- ☐ **Permissions justification.** `RECORD_AUDIO` (voice journal),
  `READ_CALENDAR` (cosmic-guide context), `SCHEDULE_EXACT_ALARM` (transit alarms),
  `POST_NOTIFICATIONS`, and the five Health Connect read permissions — each must
  map to a user-facing feature in the listing/Data Safety. Remove any that aren't
  actually used.
- ☐ **Release signing.** Configure an upload keystore (`signingConfigs`) and
  verify `./gradlew bundleRelease` produces a signed `.aab`.
- ☐ **Enable R8.** Flip `isMinifyEnabled = true` (and `isShrinkResources = true`)
  in the release build type, then **fully test the release build** — Gson/Retrofit
  use reflection, so confirm chart/numerology/compatibility responses still parse.
  Keep rules are already staged. Crashlytics mapping upload happens automatically
  once minify is on.
- ☐ **Crashlytics smoke test.** Trigger a test non-fatal via
  `CrashReporter.recordNonFatal(...)` and confirm it appears (symbolicated) in the
  Firebase console.

## Advanced chart types — IMPLEMENTED (verify build)

All six iOS/backend chart types are now wired on Android (solar arc, lunar return,
relocation, profections, declinations, fixed stars):

- ✅ Gson models matching `backend/app/routers/charts.py` exactly (`ChartModels.kt`).
- ✅ Retrofit endpoints + data-source wrappers (`AstroRemoteData.kt`).
- ✅ Compose screens (`AdvancedChartScreens.kt`) — solar-arc/lunar-return/relocation
  render the natal-style chart; profections/declinations/fixed-stars render their
  data; fixed-stars derives planet longitudes from the natal chart first.
- ✅ Routes (`AstroNavigation.kt`) + registrations (`AstroRouteGraphs.kt`) + entry
  buttons in the Charts → Advanced tab (`ChartsTabs.kt` / `ChartsScreen.kt`).
- ☐ **Verify build** (`./gradlew assembleDebug`) — not compiled in this environment.
- ☐ **Localize** the new screens' inline English strings into `strings.xml`
  (kept as literals to avoid unverified string-resource references).

## Remaining (needs Android Studio)

- ◑ **Automated tests** — test harness bootstrapped (`testImplementation` JUnit)
  with two JVM suites: `AdvancedChartModelsTest.kt` (new advanced-chart models) and
  `NatalChartModelTest.kt` (core natal `ChartData` contract + snake_case mapping).
  Run with `./gradlew testDebugUnitTest`. Still to add: `LocalSwissEphemerisEngine`
  (instrumented — needs bundled assets), numerology, and repository parsing tests.

## Verify

```bash
cd AstroNumeric-Android
./gradlew assembleDebug            # confirm the parity-pass changes compile
./gradlew lintDebug
# later, once signing + R8 configured:
./gradlew bundleRelease
```
