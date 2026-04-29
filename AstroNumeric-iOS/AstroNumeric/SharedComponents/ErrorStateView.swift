// ErrorStateView.swift
// Unified error display with context-aware CTAs

import SwiftUI

// MARK: - Error Context

enum ErrorContext {
    case networkError
    case noProfile
    case apiError(String)
    case generic(String)
    
    var icon: String {
        switch self {
        case .networkError: return "wifi.slash"
        case .noProfile: return "person.crop.circle.badge.plus"
        case .apiError: return "exclamationmark.icloud"
        case .generic: return "exclamationmark.triangle"
        }
    }
    
    var title: String {
        switch self {
        case .networkError: return "You're Offline"
        case .noProfile: return "No Profile Set Up"
        case .apiError: return "Something Went Wrong"
        case .generic: return "Something Went Wrong"
        }
    }
    
    var message: String {
        switch self {
        case .networkError:
            return "Check your connection and try again, or view cached content."
        case .noProfile:
            return "Create your profile to get personalized insights."
        case .apiError(let detail):
            return detail
        case .generic(let detail):
            return detail
        }
    }
    
    var primaryLabel: String {
        switch self {
        case .networkError: return "View Cached"
        case .noProfile: return "Create Profile"
        case .apiError, .generic: return "Try Again"
        }
    }
    
    var secondaryLabel: String? {
        switch self {
        case .networkError: return "Retry"
        case .noProfile: return "Select Profile"
        case .apiError, .generic: return nil
        }
    }
}

// MARK: - Full Screen Error

struct ErrorStateView: View {
    let context: ErrorContext
    let primaryAction: (() async -> Void)?
    let secondaryAction: (() -> Void)?
    
    @State private var isLoading = false
    
    /// Simple initializer for backward compatibility
    init(message: String, retryAction: (() async -> Void)? = nil) {
        self.context = .generic(message)
        self.primaryAction = retryAction
        self.secondaryAction = nil
    }
    
    /// Full initializer with context and actions
    init(
        context: ErrorContext,
        primaryAction: (() async -> Void)? = nil,
        secondaryAction: (() -> Void)? = nil
    ) {
        self.context = context
        self.primaryAction = primaryAction
        self.secondaryAction = secondaryAction
    }
    
    var body: some View {
        VStack(spacing: 20) {
            // Icon
            Image(systemName: context.icon)
                .font(.system(.largeTitle))
                .foregroundStyle(.purple.opacity(0.8))
            
            // Title
            Text(context.title)
                .font(.title3.bold())
                .foregroundStyle(.primary)
            
            // Message
            Text(context.message)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
            
            // Actions
            VStack(spacing: 12) {
                if let primaryAction {
                    GradientButton(context.primaryLabel, icon: primaryIcon, isLoading: isLoading) {
                        Task {
                            isLoading = true
                            await primaryAction()
                            isLoading = false
                        }
                    }
                    .frame(width: 200)
                }
                
                if let secondaryLabel = context.secondaryLabel, let secondaryAction {
                    Button {
                        secondaryAction()
                    } label: {
                        Text(secondaryLabel)
                            .font(.subheadline.weight(.medium))
                            .foregroundStyle(.purple)
                    }
                }
            }
            .padding(.top, 8)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var primaryIcon: String {
        switch context {
        case .networkError: return "arrow.down.circle"
        case .noProfile: return "plus.circle.fill"
        case .apiError, .generic: return "arrow.clockwise"
        }
    }
}

// MARK: - Compact Error (Inline)

struct CompactErrorView: View {
    let message: String
    let retryAction: (() -> Void)?
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle")
                .foregroundStyle(.yellow)
            
            Text(message)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .lineLimit(2)
            
            Spacer()
            
            if let retryAction {
                Button {
                    HapticManager.impact(.light)
                    retryAction()
                } label: {
                    Image(systemName: "arrow.clockwise")
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(.purple)
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(.ultraThinMaterial)
        )
    }
}

// MARK: - Empty State (No Data)

struct EmptyStateView: View {
    let icon: String
    let title: String
    let message: String
    let actionLabel: String?
    let action: (() -> Void)?
    
    init(
        icon: String = "tray",
        title: String,
        message: String,
        actionLabel: String? = nil,
        action: (() -> Void)? = nil
    ) {
        self.icon = icon
        self.title = title
        self.message = message
        self.actionLabel = actionLabel
        self.action = action
    }
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(.largeTitle))
                .foregroundStyle(Color.textSecondary)
            
            Text(title)
                .font(.headline)
            
            Text(message)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
            
            if let actionLabel, let action {
                GradientButton(actionLabel, icon: "plus") {
                    action()
                }
                .frame(width: 180)
                .padding(.top, 8)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - Preview

#Preview("Network Error") {
    ErrorStateView(
        context: .networkError,
        primaryAction: { try? await Task.sleep(for: .seconds(1)) },
        secondaryAction: {}
    )
    .preferredColorScheme(.dark)
}

#Preview("No Profile") {
    ErrorStateView(
        context: .noProfile,
        primaryAction: {},
        secondaryAction: {}
    )
    .preferredColorScheme(.dark)
}

#Preview("Generic Error") {
    ErrorStateView(message: "Failed to load your reading")
    .preferredColorScheme(.dark)
}

#Preview("Empty State") {
    EmptyStateView(
        icon: "chart.pie",
        title: "No Chart Data",
        message: "Create your profile to see your birth chart.",
        actionLabel: "Set Up Profile"
    ) {}
    .preferredColorScheme(.dark)
}

#Preview("Compact Error") {
    CompactErrorView(message: "Network error", retryAction: {})
        .padding()
        .preferredColorScheme(.dark)
}
