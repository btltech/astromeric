// DailyFeaturePresentation.swift
// Presentation helpers for daily feature data (lucky color hints, luck normalization).
// Extracted so they can be unit-tested without instantiating views.

import Foundation

enum DailyFeaturePresentation {

    // MARK: - Lucky Color

    /// Returns a usage hint string for a backend-supplied lucky color name.
    /// Handles both simple names ("Red") and compound names ("Sunset Orange", "Forest Green").
    static func usageHint(for color: String) -> String {
        let lower = color.lowercased()

        // Exact / compound matches first
        switch lower {
        case "red":                                         return "Wear for confidence and bold action"
        case "blue", "deep blue", "royal blue":            return "Use for calm focus and communication"
        case "green", "mint", "forest green":              return "Carry for abundance and fresh starts"
        case "yellow", "gold":                             return "Embrace for clarity and optimism"
        case "purple", "deep purple", "cosmic violet", "lavender": return "Channel for intuition and spiritual insight"
        case "pink", "rose":                               return "Invite for love and creative flow"
        case "orange", "sunset orange":                    return "Activate for energy and enthusiasm"
        case "white", "ivory":                             return "Embody for clarity and new beginnings"
        case "teal", "turquoise":                          return "Breathe in for healing and expression"
        case "indigo":                                     return "Tap into for deep wisdom and vision"
        default: break
        }

        // Keyword fallback for unknown compound names
        if lower.contains("orange") { return "Activate for energy and enthusiasm" }
        if lower.contains("green")  { return "Carry for abundance and fresh starts" }
        if lower.contains("red")    { return "Wear for confidence and bold action" }
        if lower.contains("blue")   { return "Use for calm focus and communication" }
        if lower.contains("purple") { return "Channel for intuition and spiritual insight" }
        if lower.contains("gold")   { return "Embrace for clarity and optimism" }
        if lower.contains("pink")   { return "Invite for love and creative flow" }
        if lower.contains("teal") || lower.contains("turquoise") { return "Breathe in for healing and expression" }
        if lower.contains("indigo") { return "Tap into for deep wisdom and vision" }
        if lower.contains("white") || lower.contains("ivory") { return "Embody for clarity and new beginnings" }

        return "Wear or carry to align with today's energy"
    }

    // MARK: - Luck Percentage

    /// Normalises a luck value returned by the backend.
    /// - Values > 1.0 are treated as a percentage already (clamped to 100).
    /// - Values in 0…1 are multiplied by 100.
    static func normalizedLuckPercentage(_ value: Double) -> Double {
        let percentage = value > 1.0 ? value : value * 100.0
        return min(percentage, 100.0)
    }
}
