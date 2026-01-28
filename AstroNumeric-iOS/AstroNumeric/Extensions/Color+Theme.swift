// Color+Theme.swift
// App color theme and palette

import SwiftUI

extension Color {
    // MARK: - Primary Colors
    
    static let cosmicPurple = Color(red: 0.5, green: 0.3, blue: 0.9)
    static let cosmicPink = Color(red: 0.9, green: 0.4, blue: 0.7)
    static let cosmicBlue = Color(red: 0.3, green: 0.5, blue: 0.9)
    
    // MARK: - Element Colors
    
    static let fireElement = Color(red: 1.0, green: 0.4, blue: 0.3)
    static let waterElement = Color(red: 0.3, green: 0.5, blue: 1.0)
    static let airElement = Color(red: 0.6, green: 0.8, blue: 1.0)
    static let earthElement = Color(red: 0.4, green: 0.8, blue: 0.4)
    
    // MARK: - Background Colors
    
    static let cosmicBackground = Color(red: 0.04, green: 0.05, blue: 0.08)
    static let appBackground = Color(red: 0.03, green: 0.035, blue: 0.05)
    static let surfaceBase = Color(red: 0.07, green: 0.08, blue: 0.12)
    static let surfaceElevated = Color(red: 0.10, green: 0.11, blue: 0.16)
    static let surfaceHighlight = Color.white.opacity(0.06)
    static let cardBackground = surfaceElevated
    static let borderSubtle = Color.white.opacity(0.08)
    static let borderStrong = Color.white.opacity(0.16)
    
    // MARK: - Text Colors
    
    static let textPrimary = Color(red: 0.96, green: 0.97, blue: 0.99)
    /// Boosted secondary text - readable against cosmic background
    static let textSecondary = Color(red: 0.85, green: 0.87, blue: 0.92)
    /// Standard muted text - boosted for WCAG compliance
    static let textMuted = Color(red: 0.75, green: 0.78, blue: 0.84)
    /// Subtle text for labels/captions - still readable
    static let subtleText = Color(red: 0.68, green: 0.72, blue: 0.78)
    /// High contrast variant for accessibility mode
    static let textMutedHighContrast = Color(red: 0.85, green: 0.88, blue: 0.92)
    
    /// Themed secondary color (replaces gray.opacity() for better look)
    static let cosmicSecondary = Color(red: 0.45, green: 0.48, blue: 0.55)
    
    /// Returns appropriate muted text color based on accessibility setting
    static func adaptiveTextMuted(highContrast: Bool) -> Color {
        highContrast ? textMutedHighContrast : textMuted
    }
    
    // MARK: - Status Colors
    
    static let positiveGreen = Color(red: 0.3, green: 0.85, blue: 0.5)
    static let warningOrange = Color(red: 1.0, green: 0.6, blue: 0.2)
    static let negativeRed = Color(red: 1.0, green: 0.35, blue: 0.35)
    
    // MARK: - Gradients
    
    static var cosmicGradient: LinearGradient {
        LinearGradient(
            colors: [cosmicPurple, cosmicPink],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
    
    static var fireGradient: LinearGradient {
        LinearGradient(
            colors: [.orange, .red],
            startPoint: .top,
            endPoint: .bottom
        )
    }
    
    static var waterGradient: LinearGradient {
        LinearGradient(
            colors: [.blue, .cyan],
            startPoint: .top,
            endPoint: .bottom
        )
    }
    
    static var airGradient: LinearGradient {
        LinearGradient(
            colors: [.mint, .teal],
            startPoint: .top,
            endPoint: .bottom
        )
    }
    
    static var earthGradient: LinearGradient {
        LinearGradient(
            colors: [.brown, .green],
            startPoint: .top,
            endPoint: .bottom
        )
    }
    
    // MARK: - Element Helper
    
    static func forElement(_ element: String?) -> Color {
        switch element {
        case "Fire": return fireElement
        case "Water": return waterElement
        case "Air": return airElement
        case "Earth": return earthElement
        default: return cosmicPurple
        }
    }
}

// MARK: - Theme Configuration

struct ThemeConfig {
    let primary: Color
    let secondary: Color
    let background: Color
    let cardBorder: Color
    
    static let `default` = ThemeConfig(
        primary: .cosmicPurple,
        secondary: .cosmicPink,
        background: .appBackground,
        cardBorder: .borderSubtle
    )
    
    static let ocean = ThemeConfig(
        primary: .cosmicBlue,
        secondary: .cyan,
        background: Color(red: 0.02, green: 0.05, blue: 0.1),
        cardBorder: .borderSubtle
    )
    
    static let midnight = ThemeConfig(
        primary: Color(red: 0.2, green: 0.2, blue: 0.4),
        secondary: .indigo,
        background: Color(red: 0.02, green: 0.02, blue: 0.06),
        cardBorder: .borderSubtle
    )
    
    static let sage = ThemeConfig(
        primary: Color(red: 0.4, green: 0.6, blue: 0.5),
        secondary: .mint,
        background: Color(red: 0.04, green: 0.06, blue: 0.05),
        cardBorder: .borderSubtle
    )
}
