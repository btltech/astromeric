// TabSelectedDot.swift
// Premium selected-tab indicator: a small glowing dot above the active tab.

import SwiftUI

struct TabSelectedDot<Tab: Hashable>: View {
    let selectedTab: Tab
    let tabCount: Int
    private let allCases: [Tab]?

    init(selectedTab: Tab, tabCount: Int) where Tab: CaseIterable, Tab.AllCases == [Tab] {
        self.selectedTab = selectedTab
        self.tabCount = tabCount
        self.allCases = Tab.allCases
    }

    var body: some View {
        GeometryReader { geo in
            let width = geo.size.width
            let segment = width / CGFloat(tabCount)
            let index = allCases?.firstIndex(of: selectedTab) ?? 0
            let x = segment * (CGFloat(index) + 0.5)

            VStack {
                Spacer()
                Circle()
                    .fill(Color.cosmicPurple)
                    .frame(width: 5, height: 5)
                    .shadow(color: .cosmicPurple.opacity(0.7), radius: 6)
                    .position(x: x, y: geo.size.height - 86)
                    .animation(.spring(response: 0.4, dampingFraction: 0.78), value: selectedTab)
            }
        }
        .accessibilityHidden(true)
    }
}
