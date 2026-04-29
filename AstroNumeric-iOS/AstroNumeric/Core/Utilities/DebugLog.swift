// DebugLog.swift
// Minimal debug-only logging helpers

import Foundation
import os

enum DebugLog {
    private static let logger = Logger(
        subsystem: Bundle.main.bundleIdentifier ?? "com.astromeric.app",
        category: "debug"
    )

    private static let isVerboseEnabled: Bool = {
        let processInfo = ProcessInfo.processInfo
        let arguments = Set(processInfo.arguments)
        let environment = processInfo.environment
        return arguments.contains("-AstroVerboseLogs") || environment["ASTRO_VERBOSE_LOGS"] == "1"
    }()
    
    static func log(_ message: @autoclosure @escaping () -> String) {
        #if DEBUG
        logger.debug("\(message(), privacy: .public)")
        #endif
    }

    static func trace(_ message: @autoclosure @escaping () -> String) {
        #if DEBUG
        guard isVerboseEnabled else { return }
        logger.debug("\(message(), privacy: .public)")
        #endif
    }
    
    static func error(_ message: @autoclosure @escaping () -> String) {
        #if DEBUG
        logger.error("\(message(), privacy: .public)")
        #endif
    }
}
