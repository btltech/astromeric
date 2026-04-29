// LegalConfig.swift
// Centralized legal/disclaimer links (Privacy Policy, Terms)

import Foundation

enum LegalConfig {
    static var websiteBaseURL: URL {
        let fallback = URL(string: "https://astromeric.pages.dev")!
        let raw = Bundle.main.object(forInfoDictionaryKey: "WEBSITE_BASE_URL") as? String
        guard let raw, let url = URL(string: raw), let scheme = url.scheme, scheme == "https" || scheme == "http" else {
            return fallback
        }
        return url
    }

    static var privacyPolicyURL: URL {
        // Web app supports /privacy-policy (and can redirect /privacy to it).
        websiteBaseURL.appendingPathComponent("privacy-policy")
    }

    static var termsOfServiceURL: URL {
        websiteBaseURL.appendingPathComponent("terms")
    }
}
