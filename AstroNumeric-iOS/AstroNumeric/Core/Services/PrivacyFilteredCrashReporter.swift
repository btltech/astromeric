import Foundation
import os.log

#if canImport(MetricKit)
import MetricKit
#endif

protocol CrashReporting: AnyObject {
    func start()
    func recordNonFatal(_ error: Error, context: [String: String])
}

/// Plug-in seam for a production crash/diagnostics SDK (e.g. Sentry, Firebase
/// Crashlytics). Adopt this in a thin wrapper around the SDK and register it via
/// `PrivacyFilteredCrashReporter.shared.setExternalForwarder(_:)` at launch.
///
/// IMPORTANT: only already-redacted data reaches a forwarder. No birth details,
/// chart data, journal text, or profile names are ever passed through. See
/// docs/CrashReporting.md for integration + CI symbol-upload steps.
protocol CrashReportForwarding: AnyObject {
    func forwardNonFatal(_ error: Error, redactedContext: [String: String])
    func forwardDiagnostic(_ summary: String)
}

final class PrivacyFilteredCrashReporter: NSObject, CrashReporting {
    static let shared = PrivacyFilteredCrashReporter()

    private let logger = Logger(subsystem: "com.astromeric.app", category: "crash")
    private let sensitiveKeys = [
        "name", "birth", "dob", "dateOfBirth", "timeOfBirth", "placeOfBirth",
        "latitude", "longitude", "journal", "chart", "profile"
    ]
    private var isStarted = false

    /// Optional production SDK forwarder. Receives only redacted payloads.
    private var externalForwarder: CrashReportForwarding?

    private override init() {}

    /// Register a production crash/diagnostics SDK wrapper. Safe to call once at
    /// app launch. Only redacted data is ever forwarded.
    func setExternalForwarder(_ forwarder: CrashReportForwarding) {
        externalForwarder = forwarder
    }

    func start() {
        guard !isStarted else { return }
        isStarted = true
        NSSetUncaughtExceptionHandler { exception in
            UserDefaults.standard.set(exception.name.rawValue, forKey: "crash.lastExceptionName")
            UserDefaults.standard.set(Date(), forKey: "crash.lastExceptionAt")
        }

        #if canImport(MetricKit)
        MXMetricManager.shared.add(self)
        #endif
    }

    func recordNonFatal(_ error: Error, context: [String: String] = [:]) {
        let redacted = redactedContext(context)
        logger.error("Non-fatal error: \(error.localizedDescription, privacy: .public) context=\(String(describing: redacted), privacy: .public)")
        externalForwarder?.forwardNonFatal(error, redactedContext: redacted)
    }

    private func redactedContext(_ context: [String: String]) -> [String: String] {
        context.reduce(into: [:]) { result, pair in
            let key = pair.key
            let lower = key.lowercased()
            let shouldRedact = sensitiveKeys.contains { lower.contains($0.lowercased()) }
            result[key] = shouldRedact ? "<redacted>" : pair.value
        }
    }
}

#if canImport(MetricKit)
extension PrivacyFilteredCrashReporter: MXMetricManagerSubscriber {
    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            let summary = "MetricKit diagnostic payload received: \(String(describing: payload.timeStampBegin))"
            logger.error("\(summary, privacy: .public)")
            externalForwarder?.forwardDiagnostic(summary)
        }
    }
}
#endif