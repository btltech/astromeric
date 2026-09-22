# Crash Reporting & Diagnostics

The app ships with `PrivacyFilteredCrashReporter`, a privacy-first reporter built
on MetricKit + `os.Logger`. It captures the last uncaught-exception name and
MetricKit diagnostic payloads, and redacts sensitive keys (name, birth date/time,
place, latitude/longitude, journal, chart, profile) from any non-fatal context.

What it does **not** do on its own: aggregate, symbolicate, or upload crash
reports to a dashboard. Before public launch, wire a production SDK to the
forwarding seam below (tracked in `ProductionReadinessChecklist.md`).

## Integration seam

`PrivacyFilteredCrashReporter` exposes a forwarder protocol so a third-party SDK
can receive **only redacted** payloads:

```swift
protocol CrashReportForwarding: AnyObject {
    func forwardNonFatal(_ error: Error, redactedContext: [String: String])
    func forwardDiagnostic(_ summary: String)
}
```

Register a wrapper once at launch (e.g. in the App's init / `onAppear`):

```swift
PrivacyFilteredCrashReporter.shared.setExternalForwarder(SentryCrashForwarder())
PrivacyFilteredCrashReporter.shared.start()
```

### Example wrapper (Sentry)

```swift
import Sentry

final class SentryCrashForwarder: CrashReportForwarding {
    init() {
        SentrySDK.start { options in
            options.dsn = Secrets.sentryDSN          // injected via xcconfig, not committed
            options.enableAutoSessionTracking = true
            options.attachStacktrace = true
            // Do NOT enable PII collection.
            options.sendDefaultPii = false
        }
    }
    func forwardNonFatal(_ error: Error, redactedContext: [String: String]) {
        SentrySDK.capture(error: error) { scope in
            scope.setContext(value: redactedContext, key: "app")
        }
    }
    func forwardDiagnostic(_ summary: String) {
        SentrySDK.capture(message: summary)
    }
}
```

Firebase Crashlytics is equivalent: forward `record(error:)` and
`log(_:)` from the two methods.

## Privacy requirements

- Never disable the redaction in `PrivacyFilteredCrashReporter`. Forwarders
  receive the already-redacted context only.
- Keep `sendDefaultPii`/automatic PII collection **off**.
- If you add an analytics/crash SDK, update `PrivacyInfo.xcprivacy`
  (data types + any third-party `NSPrivacyAccessedAPITypeReasons`) and the
  in-app privacy copy, per the readiness checklist.

## CI: dSYM / symbol upload

Release builds must upload dSYMs so crashes symbolicate:

- **Sentry:** add `sentry-cli upload-dif --org <org> --project <proj> $DWARF_DSYM_FOLDER_PATH`
  as a post-archive run-script phase (or use `sentry-cli` in the CI archive step).
  Store the auth token as a CI secret.
- **Crashlytics:** add the `upload-symbols` run-script phase and ensure
  `DEBUG_INFORMATION_FORMAT = dwarf-with-dsym` for Release (already set in
  `project.yml`).
- Verify a test crash appears symbolicated in the dashboard before launch.
