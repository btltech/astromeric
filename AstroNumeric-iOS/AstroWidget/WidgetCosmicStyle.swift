import SwiftUI

enum WidgetCosmicStyle {
    static let backgroundTop = Color(red: 0.10, green: 0.07, blue: 0.18)
    static let backgroundBottom = Color(red: 0.02, green: 0.02, blue: 0.05)
    static let accent = Color(red: 0.62, green: 0.42, blue: 0.98)
    static let accentSecondary = Color(red: 0.95, green: 0.36, blue: 0.74)
    static let textMuted = Color.white.opacity(0.45)
}

struct WidgetCosmicBackground: View {
    var accent: Color = WidgetCosmicStyle.accent

    var body: some View {
        LinearGradient(
            colors: [
                accent.opacity(0.30),
                WidgetCosmicStyle.backgroundTop,
                WidgetCosmicStyle.backgroundBottom
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
}