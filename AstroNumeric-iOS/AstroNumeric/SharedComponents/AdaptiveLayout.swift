// AdaptiveLayout.swift
// Size-class-aware helpers so the same SwiftUI hierarchy adapts to:
//   • iPhone portrait  (compact × regular)
//   • iPhone landscape (compact × compact)
//   • iPhone Pro Max landscape / iPad (regular × *)
// Apple HIG (2026): use horizontalSizeClass + readable widths instead of
// device idiom checks. Use Dynamic Type styles instead of fixed point sizes.

import SwiftUI

// MARK: - Readable Width Container

/// Caps content width on regular size class so iPad / Pro Max landscape
/// don't stretch text edge-to-edge. iPhone portrait is unaffected.
struct ReadableContainer: ViewModifier {
    @Environment(\.horizontalSizeClass) private var hSize

    func body(content: Content) -> some View {
        content
            .frame(maxWidth: hSize == .regular ? 760 : .infinity)
            .frame(maxWidth: .infinity, alignment: .center)
    }
}

extension View {
    /// Constrains content to a comfortable reading width on iPad and large iPhones.
    func readableContainer() -> some View {
        modifier(ReadableContainer())
    }
}

// MARK: - Adaptive Bento Columns

/// Returns a column layout that adapts to size class and Dynamic Type.
/// - iPhone compact: 2 columns (1 if accessibility size).
/// - iPad / regular: 3 columns.
/// - Landscape compact (height-constrained iPhone): 3 columns.
struct AdaptiveBentoColumns {
    let hSize: UserInterfaceSizeClass?
    let vSize: UserInterfaceSizeClass?
    let isAccessibilityType: Bool

    var columnCount: Int {
        if isAccessibilityType { return 1 }
        if hSize == .regular { return 3 }
        if vSize == .compact { return 3 } // landscape iPhone
        return 2
    }

    var columns: [GridItem] {
        Array(
            repeating: GridItem(.flexible(), spacing: 16),
            count: columnCount
        )
    }
}

// MARK: - Hover Effect (iPad / Magic Keyboard)

extension View {
    /// Adds a subtle lift on iPad pointer / external trackpad. No-op on iPhone touch.
    @ViewBuilder
    func cardHoverLift() -> some View {
        self.hoverEffect(.lift)
    }
}

// MARK: - Sidebar-adaptable TabView (iOS 18+)

extension View {
    /// Applies `.tabViewStyle(.sidebarAdaptable)` on iOS 18+ where it exists,
    /// preserving the bottom tab bar on iPhone and promoting to sidebar on iPad.
    @ViewBuilder
    func adaptiveTabViewStyle() -> some View {
        if #available(iOS 18.0, *) {
            self.tabViewStyle(.sidebarAdaptable)
        } else {
            self
        }
    }
}

// MARK: - Scaled padding helpers

/// Bottom inset that scales with Dynamic Type — used by the floating AI button
/// so it clears the tab bar on every device class.
struct ScaledBottomInset: ViewModifier {
    @ScaledMetric(relativeTo: .body) var value: CGFloat = 96
    let trailing: CGFloat

    func body(content: Content) -> some View {
        content
            .padding(.trailing, trailing)
            .padding(.bottom, value)
    }
}

extension View {
    func scaledBottomInset(value: CGFloat = 96, trailing: CGFloat = 16) -> some View {
        modifier(ScaledBottomInset(trailing: trailing))
    }
}
