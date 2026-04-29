// AccessibilityHelpers.swift
// Accessibility utilities and view modifiers for VoiceOver support

import SwiftUI

// MARK: - Accessibility View Modifiers

extension View {
    /// Add comprehensive accessibility to a card/section
    func accessibleCard(label: String, hint: String? = nil, traits: AccessibilityTraits = []) -> some View {
        self
            .accessibilityElement(children: .combine)
            .accessibilityLabel(label)
            .accessibilityHint(hint ?? "")
            .accessibilityAddTraits(traits)
    }
    
    /// Make a score/percentage accessible
    func accessibleScore(_ score: Double, context: String) -> some View {
        self
            .accessibilityLabel("\(context): \(Int(score * 100)) percent")
    }
    
    /// Add accessibility for a toggle/checkbox
    func accessibleToggle(label: String, isOn: Bool) -> some View {
        self
            .accessibilityLabel(label)
            .accessibilityValue(isOn ? "tern.accessibilityHelpers.0a".localized : "tern.accessibilityHelpers.0b".localized)
            .accessibilityAddTraits(.isButton)
    }
    
    /// Add accessibility for a date
    func accessibleDate(_ date: Date, context: String) -> some View {
        let formatter = DateFormatter()
        formatter.dateStyle = .long
        return self
            .accessibilityLabel("\(context): \(formatter.string(from: date))")
    }
    
    /// Hide decorative elements from accessibility
    func accessibilityDecorative() -> some View {
        self.accessibilityHidden(true)
    }
    
    /// Make an element a header for VoiceOver navigation
    func accessibilityHeader() -> some View {
        self.accessibilityAddTraits(.isHeader)
    }
    
    /// Add custom action for accessibility
    func accessibilityAction(named name: String, action: @escaping () -> Void) -> some View {
        self.accessibilityAction(named: Text(name), action)
    }
}

// MARK: - Accessibility-Aware Components

/// Accessible progress ring for scores
struct AccessibleScoreRing: View {
    let score: Double
    let label: String
    let color: Color
    let size: CGFloat
    
    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.borderSubtle, lineWidth: size / 10)
            
            Circle()
                .trim(from: 0, to: score)
                .stroke(
                    color,
                    style: StrokeStyle(lineWidth: size / 10, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
            
            VStack(spacing: 0) {
                Text("\(Int(score * 100))%")
                    .font(.system(size: size / 4, weight: .bold, design: .rounded))
                Text(label)
                    .font(.system(size: size / 8))
                    .foregroundStyle(Color.textSecondary)
            }
        }
        .frame(width: size, height: size)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(label): \(Int(score * 100)) percent")
        .accessibilityValue(scoreDescription)
    }
    
    private var scoreDescription: String {
        if score >= 0.8 { return "Excellent" }
        if score >= 0.6 { return "Good" }
        if score >= 0.4 { return "Moderate" }
        return "Needs attention"
    }
}

/// Accessible streak display
struct AccessibleStreakBadge: View {
    let count: Int
    let label: String
    
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: "flame.fill")
                .foregroundStyle(.orange)
            Text("\(count)")
                .fontWeight(.bold)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(label): \(count) day streak")
    }
}

/// Accessible moon phase display
struct AccessibleMoonPhase: View {
    let phase: String
    let emoji: String
    let illumination: Double
    
    var body: some View {
        VStack {
            Text(emoji)
                .font(.largeTitle)
            Text(phase)
                .font(.headline)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(phase), \(Int(illumination * 100)) percent illuminated")
    }
}

// MARK: - Semantic Colors for Accessibility

extension Color {
    /// High contrast version for accessibility
    static func accessibleColor(for score: Double) -> Color {
        if score >= 0.7 { return .green }
        if score >= 0.4 { return .orange }
        return .red
    }
}

// MARK: - Announcement Helper

struct AccessibilityAnnouncement {
    /// Post an announcement for VoiceOver users
    static func announce(_ message: String) {
        UIAccessibility.post(notification: .announcement, argument: message)
    }
    
    /// Notify VoiceOver that screen has changed
    static func screenChanged(focus element: Any? = nil) {
        UIAccessibility.post(notification: .screenChanged, argument: element)
    }
    
    /// Notify VoiceOver that layout has changed
    static func layoutChanged(focus element: Any? = nil) {
        UIAccessibility.post(notification: .layoutChanged, argument: element)
    }
}

// MARK: - Dynamic Type Support

extension View {
    /// Apply scaling for dynamic type while capping max size
    @ViewBuilder
    func dynamicTypeSize(minimum: DynamicTypeSize = .xSmall, maximum: DynamicTypeSize = .accessibility3) -> some View {
        self.dynamicTypeSize(minimum...maximum)
    }
}

// MARK: - Reduce Motion Support

struct ReduceMotionModifier: ViewModifier {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    
    let animation: Animation
    let reducedAnimation: Animation
    
    func body(content: Content) -> some View {
        content.animation(reduceMotion ? reducedAnimation : animation, value: UUID())
    }
}

extension View {
    /// Use reduced animation if Reduce Motion is enabled
    func respectReduceMotion(
        _ animation: Animation = .spring(),
        reduced: Animation = .linear(duration: 0.1)
    ) -> some View {
        modifier(ReduceMotionModifier(animation: animation, reducedAnimation: reduced))
    }
}

// MARK: - App Accessibility Modifiers

extension View {
    /// Apply app-wide accessibility preferences from AppStore
    func accessibilityPreferences(_ store: AppStore) -> some View {
        self
            .environment(\.legibilityWeight, (store.highContrastEnabled || store.largeTextEnabled) ? .bold : .regular)
            .dynamicTypeSize(store.largeTextEnabled ? .xxxLarge...(.accessibility5) : .xSmall...(.accessibility5))
    }
    
    /// Ensure minimum 44pt tap target (Apple HIG)
    func minimumTapTarget() -> some View {
        self.frame(minWidth: 44, minHeight: 44)
    }
    
    /// Apply high contrast muted text color when enabled
    func mutedTextStyle(highContrast: Bool) -> some View {
        self.foregroundStyle(Color.adaptiveTextMuted(highContrast: highContrast))
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 20) {
        AccessibleScoreRing(score: 0.75, label: "Compatibility", color: .green, size: 100)
        AccessibleStreakBadge(count: 7, label: "Current streak")
        AccessibleMoonPhase(phase: "Waxing Crescent", emoji: "🌒", illumination: 0.35)
    }
    .preferredColorScheme(.dark)
}
