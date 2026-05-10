// DailyGuidanceView.swift
// Display lucky numbers, colors, and guidance

import SwiftUI
import UIKit

struct DailyGuidanceView: View {
    let guidance: DailyGuidance
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    private var guidanceColumns: [GridItem] {
        if dynamicTypeSize.isAccessibilitySize { return [GridItem(.flexible())] }
        if horizontalSizeClass == .regular { return Array(repeating: GridItem(.flexible(), spacing: 12), count: 3) }
        return [GridItem(.flexible()), GridItem(.flexible())]
    }
    
    var body: some View {
        CardView {
            VStack(spacing: 16) {
                // Header
                HStack {
                    Text("🌙")
                        .font(.title2)
                    Text("ui.dailyGuidance.0".localized)
                        .font(.headline)
                    Spacer()
                    
                    if let power = guidance.power {
                        PowerBadge(power: power)
                    }
                }

                PremiumSectionHeader(
                title: "section.dailyGuidance.0.title".localized,
                subtitle: "section.dailyGuidance.0.subtitle".localized
            )
                
                // Grid of guidance items
                LazyVGrid(columns: guidanceColumns, spacing: 12) {
                    // Lucky Numbers
                    if let numbers = guidance.luckyNumbers, !numbers.isEmpty {
                        GuidanceItem(
                            icon: "🔢",
                            label: "Lucky Numbers",
                            value: numbers.map(String.init).joined(separator: ", ")
                        )
                    }
                    
                    // Lucky Color
                    if let color = guidance.luckyColor {
                        GuidanceItem(
                            icon: "🎨",
                            label: "Lucky Color",
                            value: color
                        )
                    }
                    
                    // Moon Phase
                    if let phase = guidance.moonPhase {
                        GuidanceItem(
                            icon: moonPhaseEmoji(phase),
                            label: "Moon Phase",
                            value: moonPhaseHumanText(phase)
                        )
                    }
                    
                    // Moon Sign
                    if let sign = guidance.moonSign {
                        GuidanceItem(
                            icon: "♋️",
                            label: "Moon Sign",
                            value: sign
                        )
                    }
                }
                
                // Affirmation
                if let affirmation = guidance.affirmation {
                    VStack(spacing: 8) {
                        Text("ui.dailyGuidance.1".localized)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                        
                        Text("\"\(affirmation)\"")
                            .font(.subheadline.italic())
                            .multilineTextAlignment(.center)
                        
                        HStack(spacing: 16) {
                            Spacer()
                            ShareLink(item: affirmation) {
                                Label("ui.dailyGuidance.2".localized, systemImage: "square.and.arrow.up")
                                    .font(.caption)
                                    .foregroundStyle(Color.textSecondary)
                            }
                            Button {
                                UIPasteboard.general.string = affirmation
                                HapticManager.notification(.success)
                            } label: {
                                Label("ui.dailyGuidance.3".localized, systemImage: "doc.on.doc")
                                    .font(.caption)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                    }
                    .padding(.top, 8)
                }
            }
        }
    }
    
    private func moonPhaseEmoji(_ phase: String) -> String {
        switch phase.lowercased() {
        case let p where p.contains("new"): return "🌑"
        case let p where p.contains("waxing crescent"): return "🌒"
        case let p where p.contains("first quarter"): return "🌓"
        case let p where p.contains("waxing gibbous"): return "🌔"
        case let p where p.contains("full"): return "🌕"
        case let p where p.contains("waning gibbous"): return "🌖"
        case let p where p.contains("last quarter"), let p where p.contains("third quarter"): return "🌗"
        case let p where p.contains("waning crescent"): return "🌘"
        default: return "🌙"
        }
    }

    /// Converts a raw moon phase string like "Waxing Gibbous in Scorpio (100% illuminated)"
    /// into a plain-English sentence the user can understand at a glance.
    private func moonPhaseHumanText(_ phase: String) -> String {
        let lower = phase.lowercased()
        // Extract sign if present (e.g. "in Scorpio")
        var signNote = ""
        if let range = phase.range(of: #"in ([A-Z][a-z]+)"#, options: .regularExpression) {
            let matched = phase[range]
            let sign = matched.replacingOccurrences(of: "in ", with: "")
            signNote = " in \(sign)"
        }

        if lower.contains("new moon") || (lower.contains("new") && !lower.contains("crescent")) {
            return "New Moon\(signNote) — a fresh start. Set intentions today."
        } else if lower.contains("waxing crescent") {
            return "The Moon is a slim crescent\(signNote) — plant seeds and take first steps."
        } else if lower.contains("first quarter") {
            return "First Quarter Moon\(signNote) — push past early obstacles and commit."
        } else if lower.contains("waxing gibbous") {
            return "The Moon is building toward fullness\(signNote) — energy and awareness are rising."
        } else if lower.contains("full moon") || lower.contains("full") {
            return "Full Moon\(signNote) — emotions and awareness are at their peak."
        } else if lower.contains("waning gibbous") {
            return "The Moon is beginning to wane\(signNote) — a time for gratitude and sharing."
        } else if lower.contains("last quarter") || lower.contains("third quarter") {
            return "Last Quarter Moon\(signNote) — release what is not working and simplify."
        } else if lower.contains("waning crescent") {
            return "The Moon is fading\(signNote) — rest, reflect, and prepare for the next cycle."
        }

        // Fallback: strip parenthetical illumination percentage for a cleaner display
        let cleaned = phase
            .replacingOccurrences(of: #"\s*\(\d+%\s*illuminated\)"#, with: "", options: .regularExpression)
            .trimmingCharacters(in: .whitespaces)
        return cleaned.isEmpty ? phase : cleaned
    }
}

// MARK: - Guidance Item

struct GuidanceItem: View {
    let icon: String
    let label: String
    let value: String
    
    var body: some View {
        VStack(spacing: 6) {
            Text(icon)
                .font(.title2)
            
            Text(label)
                .font(.caption2)
                .foregroundStyle(Color.textSecondary)
            
            Text(value)
                .font(.caption.weight(.medium))
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.white.opacity(0.05))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.white.opacity(0.06), lineWidth: 1)
                )
        )
    }
}

// MARK: - Power Badge

struct PowerBadge: View {
    let power: Int
    
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: "bolt.fill")
                .font(.caption2)
            Text("\(power)%")
                .font(.caption.weight(.bold))
        }
        .foregroundStyle(powerColor)
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(
            Capsule()
                .fill(powerColor.opacity(0.2))
        )
    }
    
    private var powerColor: Color {
        switch power {
        case 80...100: return .positiveGreen
        case 60..<80: return .yellow
        case 40..<60: return .warningOrange
        default: return .negativeRed
        }
    }
}

// MARK: - Preview

#Preview {
    DailyGuidanceView(
        guidance: DailyGuidance(
            luckyNumbers: [7, 11, 22],
            luckyColor: "Royal Blue",
            affirmation: "I embrace change with an open heart",
            advice: nil,
            moonPhase: "Waxing Crescent",
            moonSign: "Pisces",
            power: 75
        )
    )
    .padding()
    .background(Color.black)
    .preferredColorScheme(.dark)
}
