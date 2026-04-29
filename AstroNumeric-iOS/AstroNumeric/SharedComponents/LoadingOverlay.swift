// LoadingOverlay.swift
// Full-screen and inline loading indicators

import SwiftUI

struct LoadingOverlay: View {
    let message: String?
    
    init(message: String? = nil) {
        self.message = message
    }
    
    var body: some View {
        ZStack {
            Color.black.opacity(0.3)
                .ignoresSafeArea()
            
            VStack(spacing: 16) {
                // Animated cosmic spinner
                CosmicSpinner()
                
                if let message {
                    Text(message)
                        .font(.subheadline)
                        .foregroundStyle(Color.textSecondary)
                }
            }
            .padding(32)
            .background(
                RoundedRectangle(cornerRadius: 20)
                    .fill(.ultraThinMaterial)
            )
        }
    }
}

// MARK: - Cosmic Spinner

struct CosmicSpinner: View {
    @State private var rotation: Double = 0
    @State private var scale: CGFloat = 1
    
    var body: some View {
        ZStack {
            // Outer ring
            Circle()
                .stroke(
                    LinearGradient(
                        colors: [.purple.opacity(0.5), .blue.opacity(0.5)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 3
                )
                .frame(width: 50, height: 50)
                .rotationEffect(.degrees(rotation))
            
            // Moon emoji
            Text("🌙")
                .font(.title)
                .scaleEffect(scale)
        }
        .onAppear {
            withAnimation(.linear(duration: 2).repeatForever(autoreverses: false)) {
                rotation = 360
            }
            withAnimation(.easeInOut(duration: 1).repeatForever()) {
                scale = 1.1
            }
        }
    }
}

// MARK: - Inline Loading

struct InlineLoading: View {
    let message: String
    
    var body: some View {
        HStack(spacing: 12) {
            ProgressView()
                .tint(.accentColor)
            
            Text(message)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
        }
        .padding()
    }
}

// MARK: - Skeleton Loading

struct SkeletonView: View {
    let height: CGFloat
    @State private var shimmer = false
    
    init(height: CGFloat = 20) {
        self.height = height
    }
    
    var body: some View {
        RoundedRectangle(cornerRadius: 8)
            .fill(
                LinearGradient(
                    colors: [
                        Color.cosmicSecondary.opacity(0.5),
                        Color.cosmicSecondary.opacity(0.2),
                        Color.cosmicSecondary.opacity(0.5)
                    ],
                    startPoint: shimmer ? .leading : .trailing,
                    endPoint: shimmer ? .trailing : .leading
                )
            )
            .frame(height: height)
            .onAppear {
                withAnimation(.linear(duration: 1.5).repeatForever(autoreverses: false)) {
                    shimmer.toggle()
                }
            }
    }
}

struct SkeletonCard: View {
    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                SkeletonView(height: 24)
                    .frame(width: 150)
                SkeletonView(height: 16)
                SkeletonView(height: 16)
                    .frame(width: 200)
            }
        }
    }
}

// MARK: - Previews

#Preview("Loading Overlay") {
    ZStack {
        Color.black
        LoadingOverlay(message: "Analyzing the cosmos...")
    }
    .preferredColorScheme(.dark)
}

#Preview("Inline Loading") {
    InlineLoading(message: "Loading your reading...")
        .preferredColorScheme(.dark)
}

#Preview("Skeleton") {
    VStack(spacing: 16) {
        SkeletonCard()
        SkeletonCard()
    }
    .padding()
    .background(Color.black)
    .preferredColorScheme(.dark)
}
