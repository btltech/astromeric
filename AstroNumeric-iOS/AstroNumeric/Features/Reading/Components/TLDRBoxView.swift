// TLDRBoxView.swift
// Highlighted headline/summary box

import SwiftUI

struct TLDRBoxView: View {
    let text: String
    
    var body: some View {
        VStack(spacing: Space.sm) {
            Text("ui.tLDRBox.0".localized)
                .font(.caption.weight(.bold))
                .foregroundStyle(Color.accentPrimary)
            
            Text(text)
                .font(.subheadline)
                .multilineTextAlignment(.center)
                .foregroundStyle(.primary)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: Radius.md)
                .fill(
                    LinearGradient(
                        colors: [
                            Color.accentPrimary.opacity(0.2),
                            Color.accentPrimary.opacity(0.1)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
        )
        .overlay(
            RoundedRectangle(cornerRadius: Radius.md)
                .strokeBorder(Color.accentPrimary.opacity(0.3), lineWidth: 1)
        )
    }
}

#Preview {
    TLDRBoxView(text: "Today brings exciting opportunities for creative breakthroughs and meaningful connections.")
        .padding()
        .background(Color.black)
        .preferredColorScheme(.dark)
}
