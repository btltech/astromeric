// FriendsOwnerKey.swift
// Unguessable owner key for server-side friend lists.

import CryptoKit
import Foundation
import Security

/// The `/v2/friends/*` endpoints are keyed only by the owner key sent in the
/// `X-Owner-Key` header, so that key must be an unguessable secret. Local profile ids (-1, -2, ...) are the same on every device and
/// must never be sent.
///
/// A random 256-bit install secret is created once and kept in the Keychain for this
/// device only (not synced; it survives reinstalls). Each profile's owner key is
/// SHA-256("<secret>:<profileId>") as 64 hex characters, so every profile keeps its
/// own friend list.
enum FriendsOwnerKey {
    static let defaultService = "com.astromeric.app.friends-owner"
    private static let account = "install-secret"
    private static let secretLength = 32

    /// Owner id for a profile, or nil if the Keychain is unavailable (callers must not
    /// fall back to the profile id).
    static func ownerId(forProfileId profileId: Int, service: String = defaultService) -> String? {
        guard let secret = installSecret(service: service) else { return nil }
        return derive(secret: secret, profileId: profileId)
    }

    static func derive(secret: Data, profileId: Int) -> String {
        var input = secret
        input.append(Data(":\(profileId)".utf8))
        return SHA256.hash(data: input).map { String(format: "%02x", $0) }.joined()
    }

    static func installSecret(service: String = defaultService) -> Data? {
        if let existing = readSecret(service: service) { return existing }

        var bytes = [UInt8](repeating: 0, count: secretLength)
        guard SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes) == errSecSuccess else {
            return nil
        }
        let secret = Data(bytes)

        let attributes: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly,
            kSecValueData as String: secret,
        ]
        switch SecItemAdd(attributes as CFDictionary, nil) {
        case errSecSuccess:
            return secret
        case errSecDuplicateItem:
            // Another caller created it first; use the stored value.
            return readSecret(service: service)
        default:
            return nil
        }
    }

    private static func readSecret(service: String) -> Data? {
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
              data.count == secretLength
        else { return nil }
        return data
    }

    #if DEBUG
    /// Test support: remove the secret stored under `service`.
    static func deleteSecret(service: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        SecItemDelete(query as CFDictionary)
    }
    #endif
}
