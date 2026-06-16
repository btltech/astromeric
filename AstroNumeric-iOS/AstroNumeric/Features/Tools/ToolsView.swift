// ToolsView.swift
// Compatibility shim after Explore replaced the standalone tools hub.

import SwiftUI

struct ToolsView: View {
    var body: some View {
        ExploreView()
    }
}

// MARK: - Preview

#Preview {
    ToolsView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
