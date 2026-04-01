// ToolsView.swift
// Cosmic Tools hub - Tarot, Oracle, Affirmation

import SwiftUI

struct ToolsView: View {
    @Environment(AppStore.self) private var store
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Tool Cards
                        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                            ToolCard(
                                title: "Tarot",
                                icon: "suit.spade.fill",
                                color: .purple,
                                description: "Daily card draw"
                            ) {
                                TarotView()
                            }
                            
                            ToolCard(
                                title: "Oracle",
                                icon: "questionmark.circle.fill",
                                color: .blue,
                                description: "Yes/No guidance"
                            ) {
                                OracleView()
                            }
                            
                            ToolCard(
                                title: "Affirmation",
                                icon: "star.fill",
                                color: .orange,
                                description: "Daily inspiration"
                            ) {
                                AffirmationView()
                            }
                            
                            ToolCard(
                                title: "Moon Phase",
                                icon: "moon.fill",
                                color: .indigo,
                                description: "Lunar guidance"
                            ) {
                                MoonPhaseView()
                            }
                            
                            ToolCard(
                                title: "Birth Chart",
                                icon: "circle.grid.3x3",
                                color: .teal,
                                description: "Your cosmic map"
                            ) {
                                ChartView()
                            }
                            
                            ToolCard(
                                title: "Compatibility",
                                icon: "heart.fill",
                                color: .pink,
                                description: "Relationship synastry"
                            ) {
                                CompatibilityView()
                            }
                            
                            ToolCard(
                                title: "Daily Guide",
                                icon: "sparkles",
                                color: .yellow,
                                description: "Daily cosmic features"
                            ) {
                                DailyFeaturesView()
                            }
                            
                            ToolCard(
                                title: "Timing",
                                icon: "clock.badge.checkmark",
                                color: .green,
                                description: "Best time for activities"
                            ) {
                                TimingAdvisorView()
                            }
                            
                            ToolCard(
                                title: "Temporal Matrix",
                                icon: "calendar.badge.clock",
                                color: .cyan,
                                description: "48h cosmic weather HUD"
                            ) {
                                TemporalMatrixView()
                            }

                            ToolCard(
                                title: "Birthstones",
                                icon: "sparkle",
                                color: .mint,
                                description: "Gems for your sign"
                            ) {
                                BirthstoneGuidanceView()
                            }
                        }
                        .padding(.horizontal)
                    }
                    .padding(.vertical)
                }
            }
            .navigationTitle("Cosmic Tools")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
}

// MARK: - Tool Card

struct ToolCard<Destination: View>: View {
    let title: String
    let icon: String
    let color: Color
    let description: String
    @ViewBuilder let destination: () -> Destination
    
    var body: some View {
        NavigationLink {
            destination()
        } label: {
            VStack(spacing: 12) {
                ZStack {
                    Circle()
                        .fill(color.opacity(0.2))
                        .frame(width: 60, height: 60)
                    
                    Image(systemName: icon)
                        .font(.title)
                        .foregroundStyle(color)
                }
                
                Text(title)
                    .font(.headline)
                    .foregroundStyle(.primary)
                
                Text(description)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(.ultraThinMaterial)
            )
        }
    }
}

// MARK: - Preview

#Preview {
    ToolsView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
