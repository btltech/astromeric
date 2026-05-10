import Foundation
import os.log

#if canImport(MetricKit)
import MetricKit
#endif

protocol CrashReporting: AnyObject {
    func start()
    func recordNonFatal(_ error: Error, context: [String: String])
}

final class PrivacyFilteredCrashReporter: NSObject, CrashReporting {
    static let shared = PrivacyFilteredCrashReporter()

    private let logger = Logger(subsystem: "com.astromeric.app", category: "crash")
    private let sensitiveKeys = [
        "name", "birth", "dob", "dateOfBirth", "timeOfBirth", "placeOfBirth",
        "latitude", "longitude", "journal", "chart", "profile"
    ]
    private var isStarted = false

    private override init() {}

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
            logger.error("MetricKit diagnostic payload received: \(String(describing: payload.timeStampBegin), privacy: .public)")
        }
    }
}
#endif