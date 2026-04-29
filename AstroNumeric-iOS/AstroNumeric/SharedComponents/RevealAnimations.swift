// RevealAnimations.swift
// Reusable reveal animation modifiers for premium hero moments

import SwiftUI

// MARK: - Shimmer Reveal Modifier

struct ShimmerRevealModifier: ViewModifier {
    let isRevealing: Bool
    let delay: Double
    
    @State private var shimmerPhase: CGFloat = 0
    
    func body(content: Content) -> some View {
        content
            .opacity(isRevealing ? 0 : 1)
            .scaleEffect(isRevealing ? 0.95 : 1)
            .animation(.spring(response: 0.6, dampingFraction: 0.8).delay(delay), value: isRevealing)
            .overlay {
                if !isRevealing {
                    // Subtle shimmer on reveal
                    LinearGradient(
                        colors: [
                            .clear,
                            .white.opacity(0.2),
                            .clear
                        ],
                        startPoint: .init(x: shimmerPhase - 0.3, y: 0.5),
                        endPoint: .init(x: shimmerPhase, y: 0.5)
                    )
                    .blendMode(.overlay)
                    .onAppear {
                        withAnimation(.easeInOut(duration: 0.8)) {
                            shimmerPhase = 1.3
                        }
                    }
                }
            }
            .clipped()
    }
}

// MARK: - Scale Reveal Modifier

struct ScaleRevealModifier: ViewModifier {
    let isRevealing: Bool
    let fromScale: CGFloat
    let delay: Double
    
    func body(content: Content) -> some View {
        content
            .opacity(isRevealing ? 0 : 1)
            .scaleEffect(isRevealing ? fromScale : 1)
            .animation(.spring(response: 0.5, dampingFraction: 0.7).delay(delay), value: isRevealing)
    }
}

// MARK: - Slide Up Reveal Modifier

struct SlideUpRevealModifier: ViewModifier {
    let isRevealing: Bool
    let offset: CGFloat
    let delay: Double
    
    func body(content: Content) -> some View {
        content
            .opacity(isRevealing ? 0 : 1)
            .offset(y: isRevealing ? offset : 0)
            .animation(.spring(response: 0.5, dampingFraction: 0.8).delay(delay), value: isRevealing)
    }
}

// MARK: - Card Flip Modifier

struct CardFlipModifier: ViewModifier {
    let isFlipped: Bool
    let frontContent: AnyView
    let backContent: AnyView
    
    func body(content: Content) -> some View {
        ZStack {
            backContent
                .rotation3DEffect(.degrees(isFlipped ? 0 : 180), axis: (x: 0, y: 1, z: 0))
                .opacity(isFlipped ? 1 : 0)
            
            frontContent
                .rotation3DEffect(.degrees(isFlipped ? 180 : 0), axis: (x: 0, y: 1, z: 0))
                .opacity(isFlipped ? 0 : 1)
        }
        .animation(.spring(response: 0.6, dampingFraction: 0.8), value: isFlipped)
    }
}

// MARK: - Animated Counter

struct AnimatedCounter: View {
    let value: Int
    let duration: Double
    
    @State private var displayValue: Int = 0
    
    var body: some View {
        Text("\(displayValue)")
            .contentTransition(.numericText())
            .onAppear {
                withAnimation(.easeOut(duration: duration)) {
                    displayValue = value
                }
            }
            .onChange(of: value) { _, newValue in
                withAnimation(.easeOut(duration: duration)) {
                    displayValue = newValue
                }
            }
    }
}

// MARK: - Animated Score Circle

struct AnimatedScoreCircle: View {
    let score: Double // 0-100
    let color: Color
    let label: String
    let delay: Double
    
    @State private var animatedProgress: Double = 0
    @State private var isVisible = false
    
    var body: some View {
        VStack(spacing: 8) {
            ZStack {
                // Background circle
                Circle()
                    .stroke(color.opacity(0.2), lineWidth: 6)
                
                // Animated progress circle
                Circle()
                    .trim(from: 0, to: animatedProgress)
                    .stroke(
                        color,
                        style: StrokeStyle(lineWidth: 6, lineCap: .round)
                    )
                    .rotationEffect(.degrees(-90))
                
                // Score text
                Text("\(Int(score))")
                    .font(.system(.title3, design: .rounded)).fontWeight(.bold)
                    .foregroundStyle(color)
            }
            .frame(width: 60, height: 60)
            
            Text(label)
                .font(.meta)
                .foregroundStyle(Color.textSecondary)
        }
        .opacity(isVisible ? 1 : 0)
        .scaleEffect(isVisible ? 1 : 0.8)
        .onAppear {
            withAnimation(.spring(response: 0.4, dampingFraction: 0.7).delay(delay)) {
                isVisible = true
            }
            withAnimation(.easeOut(duration: 0.8).delay(delay + 0.2)) {
                animatedProgress = score / 100
            }
        }
    }
}

// MARK: - Staggered List Modifier

struct StaggeredRevealModifier: ViewModifier {
    let index: Int
    let isRevealing: Bool
    let baseDelay: Double
    let staggerDelay: Double
    
    private var totalDelay: Double {
        baseDelay + (Double(index) * staggerDelay)
    }
    
    func body(content: Content) -> some View {
        content
            .opacity(isRevealing ? 0 : 1)
            .offset(y: isRevealing ? 20 : 0)
            .animation(.spring(response: 0.4, dampingFraction: 0.8).delay(totalDelay), value: isRevealing)
    }
}

// MARK: - View Extensions

extension View {
    func shimmerReveal(isRevealing: Bool, delay: Double = 0) -> some View {
        modifier(ShimmerRevealModifier(isRevealing: isRevealing, delay: delay))
    }
    
    func scaleReveal(isRevealing: Bool, fromScale: CGFloat = 0.8, delay: Double = 0) -> some View {
        modifier(ScaleRevealModifier(isRevealing: isRevealing, fromScale: fromScale, delay: delay))
    }
    
    func slideUpReveal(isRevealing: Bool, offset: CGFloat = 30, delay: Double = 0) -> some View {
        modifier(SlideUpRevealModifier(isRevealing: isRevealing, offset: offset, delay: delay))
    }
    
    func staggeredReveal(index: Int, isRevealing: Bool, baseDelay: Double = 0, staggerDelay: Double = 0.05) -> some View {
        modifier(StaggeredRevealModifier(index: index, isRevealing: isRevealing, baseDelay: baseDelay, staggerDelay: staggerDelay))
    }
}

// MARK: - Preview

#Preview("Reveal Animations") {
    VStack(spacing: 20) {
        AnimatedScoreCircle(score: 85, color: .purple, label: "Energy", delay: 0)
        AnimatedScoreCircle(score: 70, color: .blue, label: "Luck", delay: 0.1)
        AnimatedScoreCircle(score: 92, color: .green, label: "Love", delay: 0.2)
    }
    .padding()
    .preferredColorScheme(.dark)
}
