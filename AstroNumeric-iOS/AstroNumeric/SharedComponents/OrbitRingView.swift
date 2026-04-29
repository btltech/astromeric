// OrbitRingView.swift  
// Premium animated orbit ring visual for hero cards

import SwiftUI

struct OrbitRingView: View {
    let sunEmoji: String
    let moonEmoji: String
    
    @State private var orbitRotation: Double = 0
    @State private var pulseScale: CGFloat = 1.0
    @State private var glowOpacity: Double = 0.4
    
    var body: some View {
        ZStack {
            // Outer glow
            Circle()
                .fill(
                    RadialGradient(
                        colors: [.purple.opacity(0.3), .clear],
                        center: .center,
                        startRadius: 40,
                        endRadius: 70
                    )
                )
                .frame(width: 140, height: 140)
                .opacity(glowOpacity)
            
            // Orbit rings
            ForEach(0..<3) { index in
                Circle()
                    .stroke(
                        LinearGradient(
                            colors: [
                                .purple.opacity(0.3 - Double(index) * 0.1),
                                .pink.opacity(0.2 - Double(index) * 0.05)
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 1
                    )
                    .frame(width: CGFloat(60 + index * 25), height: CGFloat(60 + index * 25))
            }
            
            // Orbiting moon
            Text(moonEmoji)
                .font(.title3)
                .offset(x: 45)
                .rotationEffect(.degrees(orbitRotation))
                .shadow(color: .purple.opacity(0.5), radius: 4)
            
            // Central sun with pulse
            ZStack {
                Circle()
                    .fill(
                        RadialGradient(
                            colors: [.yellow.opacity(0.3), .orange.opacity(0.1), .clear],
                            center: .center,
                            startRadius: 0,
                            endRadius: 25
                        )
                    )
                    .frame(width: 50, height: 50)
                    .scaleEffect(pulseScale)
                
                Text(sunEmoji)
                    .font(.largeTitle)
            }
        }
        .frame(width: 140, height: 140)
        .onAppear {
            startAnimations()
        }
    }
    
    private func startAnimations() {
        // Orbit animation
        withAnimation(.linear(duration: 20).repeatForever(autoreverses: false)) {
            orbitRotation = 360
        }
        
        // Pulse animation
        withAnimation(.easeInOut(duration: 2).repeatForever(autoreverses: true)) {
            pulseScale = 1.15
        }
        
        // Glow animation
        withAnimation(.easeInOut(duration: 3).repeatForever(autoreverses: true)) {
            glowOpacity = 0.6
        }
    }
}

// MARK: - Premium Hero Card

struct TodayHeroCard: View {
    let sunSign: String
    let sunEmoji: String
    let moonPhase: String
    let moonEmoji: String
    let headline: String
    
    @State private var appeared = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Hero visual
            HStack(spacing: 20) {
                OrbitRingView(sunEmoji: sunEmoji, moonEmoji: moonEmoji)
                    .scaleEffect(appeared ? 1 : 0.8)
                    .opacity(appeared ? 1 : 0)
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("ui.orbitRing.0".localized)
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(Color.textSecondary)
                    
                    Text(headline)
                        .font(.title3.bold())
                        .lineLimit(3)
                        .fixedSize(horizontal: false, vertical: true)
                    
                    HStack(spacing: 16) {
                        Label(sunSign, systemImage: "sun.max.fill")
                            .font(.label)
                            .foregroundStyle(.orange)
                        
                        Label(moonPhase, systemImage: "moon.fill")
                            .font(.label)
                            .foregroundStyle(.purple)
                    }
                }
                .offset(x: appeared ? 0 : 20)
                .opacity(appeared ? 1 : 0)
            }
            .padding()
        }
        .background {
            RoundedRectangle(cornerRadius: 20)
                .fill(.ultraThinMaterial)
                .overlay {
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(
                            LinearGradient(
                                colors: [.purple.opacity(0.5), .pink.opacity(0.3), .clear],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            lineWidth: 1
                        )
                }
        }
        .onAppear {
            withAnimation(.spring(response: 0.6, dampingFraction: 0.8)) {
                appeared = true
            }
        }
    }
}

// MARK: - Preview

#Preview {
    ZStack {
        Color.black.ignoresSafeArea()
        
        VStack(spacing: 20) {
            TodayHeroCard(
                sunSign: "Aquarius",
                sunEmoji: "♒️",
                moonPhase: "Waxing",
                moonEmoji: "🌓",
                headline: "A day for creative breakthroughs and unexpected connections"
            )
            .padding()
            
            OrbitRingView(sunEmoji: "♌️", moonEmoji: "🌙")
        }
    }
    .preferredColorScheme(.dark)
}
