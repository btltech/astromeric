// GradientButton.swift
// Primary action button with gradient and haptic feedback

import SwiftUI

struct GradientButton: View {
    let title: String
    let icon: String?
    let isLoading: Bool
    let action: () -> Void
    
    @State private var isPressed = false
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    
    init(
        _ title: String,
        icon: String? = nil,
        isLoading: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.isLoading = isLoading
        self.action = action
    }
    
    var body: some View {
        Button {
            HapticManager.impact(.medium)
            action()
        } label: {
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    if let icon {
                        Image(systemName: icon)
                            .accessibilityHidden(true)
                    }
                    Text(title)
                }
            }
            .font(.headline)
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(
                        LinearGradient(
                            colors: [
                                Color(red: 0.5, green: 0.3, blue: 0.9),
                                Color(red: 0.3, green: 0.2, blue: 0.7)
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .strokeBorder(
                        Color.white.opacity(0.2),
                        lineWidth: 1
                    )
            )
            .shadow(color: Color.purple.opacity(0.4), radius: 10, y: 4)
            .scaleEffect(isPressed ? 0.98 : 1)
            .animation(reduceMotion ? nil : .spring(duration: 0.2), value: isPressed)
        }
        .disabled(isLoading)
        .buttonStyle(PressableButtonStyle(isPressed: $isPressed))
        .accessibilityLabel(title)
        .accessibilityHint(isLoading ? "tern.gradientButton.0a".localized : "tern.gradientButton.0b".localized)
        .accessibilityAddTraits(.isButton)
    }
}

// MARK: - Secondary Button

struct SecondaryButton: View {
    let title: String
    let icon: String?
    let action: () -> Void
    
    init(
        _ title: String,
        icon: String? = nil,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.action = action
    }
    
    var body: some View {
        Button {
            HapticManager.impact(.light)
            action()
        } label: {
            HStack(spacing: 8) {
                if let icon {
                    Image(systemName: icon)
                }
                Text(title)
            }
            .font(.subheadline.weight(.medium))
            .foregroundStyle(.primary)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(.ultraThinMaterial)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .strokeBorder(Color.white.opacity(0.2), lineWidth: 1)
            )
        }
    }
}

// MARK: - Destructive Button

struct DestructiveButton: View {
    let title: String
    let icon: String?
    let action: () -> Void
    
    init(
        _ title: String,
        icon: String? = nil,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.action = action
    }
    
    var body: some View {
        Button {
            HapticManager.notification(.warning)
            action()
        } label: {
            HStack(spacing: 8) {
                if let icon {
                    Image(systemName: icon)
                }
                Text(title)
            }
            .font(.subheadline.weight(.medium))
            .foregroundStyle(.red)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.red.opacity(0.15))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .strokeBorder(Color.red.opacity(0.3), lineWidth: 1)
            )
        }
    }
}

// MARK: - Icon Button

struct IconButton: View {
    let icon: String
    let action: () -> Void
    
    var body: some View {
        Button {
            HapticManager.impact(.light)
            action()
        } label: {
            Image(systemName: icon)
                .font(.title2)
                .foregroundStyle(.primary)
                .frame(width: 44, height: 44)
                .background(
                    Circle()
                        .fill(.ultraThinMaterial)
                )
        }
    }
}

// MARK: - Pressable Button Style

struct PressableButtonStyle: ButtonStyle {
    @Binding var isPressed: Bool
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .onChange(of: configuration.isPressed) { _, newValue in
                withAnimation(.easeInOut(duration: 0.1)) {
                    isPressed = newValue
                }
            }
    }
}

/// Simple scale button style for cards and navigation links
struct ScaleButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.97 : 1.0)
            .opacity(configuration.isPressed ? 0.9 : 1.0)
            .animation(.easeInOut(duration: 0.12), value: configuration.isPressed)
    }
}

/// Accessible button style that enforces minimum 44pt tap target (Apple HIG)
struct AccessibleButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .frame(minWidth: 44, minHeight: 44)
            .contentShape(Rectangle())
            .opacity(configuration.isPressed ? 0.7 : 1.0)
    }
}

// MARK: - Haptic Manager

enum HapticManager {
    static func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
        #if !targetEnvironment(simulator)
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.prepare()
        generator.impactOccurred()
        #endif
    }
    
    static func notification(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        #if !targetEnvironment(simulator)
        let generator = UINotificationFeedbackGenerator()
        generator.prepare()
        generator.notificationOccurred(type)
        #endif
    }
    
    static func selection() {
        #if !targetEnvironment(simulator)
        let generator = UISelectionFeedbackGenerator()
        generator.prepare()
        generator.selectionChanged()
        #endif
    }
}

// MARK: - Previews

#Preview("Buttons") {
    VStack(spacing: 20) {
        GradientButton("Get Your Reading", icon: "sparkles") {
            print("Tapped!")
        }
        
        GradientButton("Loading...", isLoading: true) {}
        
        SecondaryButton("ui.gradientButton.0".localized, icon: "chevron.right") {}
        
        HStack(spacing: 16) {
            IconButton(icon: "square.and.arrow.up") {}
            IconButton(icon: "heart") {}
            IconButton(icon: "bookmark") {}
        }
    }
    .padding()
    .background(Color.black)
    .preferredColorScheme(.dark)
}
