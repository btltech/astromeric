// AIAccessCode.swift
// Private access code that unlocks live AI answers on the owner's own device.

import Foundation
import Observation
import Security

/// Live AI runs on an unpaid Gemini key whose prompts Google may use to improve
/// its products, so it is reserved for the owner's device instead of shipping to
/// everyone. The backend only calls Gemini for requests carrying this code
/// (`ai_service.has_ai_access`); the code is typed in once on the device and is
/// never part of the App Store build, so other users' questions and chart data
/// stay on our own servers and they get the built-in responses instead.
enum AIAccessCode {
    static let defaultService = "com.astromeric.app.ai-access"
    static let header = "X-AI-Access"
    private static let account = "access-code"

    /// The stored code, or nil when this device has none (the normal case).
    static func current(service: String = defaultService) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var result: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
              let data = result as? Data,
              let code = String(data: data, encoding: .utf8),
              !code.isEmpty
        else { return nil }
        return code
    }

    /// Stores `code`, or clears it when `code` is empty. Returns false if the
    /// Keychain refused the write.
    @discardableResult
    static func set(_ code: String, service: String = defaultService) -> Bool {
        let trimmed = code.trimmingCharacters(in: .whitespacesAndNewlines)
        clear(service: service)
        guard !trimmed.isEmpty else { return true }

        let attributes: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly,
            kSecValueData as String: Data(trimmed.utf8),
        ]
        return SecItemAdd(attributes as CFDictionary, nil) == errSecSuccess
    }

    static func clear(service: String = defaultService) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        SecItemDelete(query as CFDictionary)
    }
}

/// Whether this device shows AI features at all. Without the owner's code the
/// server only returns canned stand-ins, so the Oracle, the floating Cosmic
/// Guide button and "AI insights" are hidden rather than offered half-working.
@MainActor
@Observable
final class AIAvailability {
    static let shared = AIAvailability()

    private(set) var isEnabled: Bool

    init(isEnabled: Bool = AIAccessCode.current() != nil) {
        self.isEnabled = isEnabled
    }

    /// Call after the code is saved or cleared so screens update immediately.
    func refresh() {
        isEnabled = AIAccessCode.current() != nil
    }
}
