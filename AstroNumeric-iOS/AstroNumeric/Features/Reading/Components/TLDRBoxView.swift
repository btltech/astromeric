// TLDRBoxView.swift
// Highlighted headline/summary box

import SwiftUI

struct TLDRBoxView: View {
    let text: String
    
    var body: some View {
        VStack(spacing: 8) {
            Text("ui.tLDRBox.0".localized)
                .font(.caption.weight(.bold))
                .foregroundStyle(.purple)
            
            Text(text)
                .font(.subheadline)
                .multilineTextAlignment(.center)
                .foregroundStyle(.primary)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(
                    LinearGradient(
                        colors: [
                            Color.purple.opacity(0.2),
                            Color.purple.opacity(0.1)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .strokeBorder(Color.purple.opacity(0.3), lineWidth: 1)
        )
    }
}

#Preview {
    TLDRBoxView(text: "Today brings exciting opportunities for creative breakthroughs and meaningful connections.")
        .padding()
        .background(Color.black)
        .preferredColorScheme(.dark)
}
