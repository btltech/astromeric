// ChartsView.swift
// Consolidated view for Birth Chart, Numerology, Compatibility

import SwiftUI

struct ChartsView: View {
    @Environment(AppStore.self) private var store
    @State private var selectedTab: ChartTab = .birthChart
    @State private var isExporting = false
    
    enum ChartTab: String, CaseIterable {
        case birthChart = "Birth Chart"
        case numerology = "Numerology"
        case compatibility = "Compatibility"
        case advanced = "Advanced"
        
        var icon: String {
            switch self {
            case .birthChart: return "sun.and.horizon.fill"
            case .numerology: return "number.circle.fill"
            case .compatibility: return "heart.circle.fill"
            case .advanced: return "sparkles"
            }
        }
        
        var color: Color {
            switch self {
            case .birthChart: return .orange
            case .numerology: return .purple
            case .compatibility: return .pink
            case .advanced: return .blue
            }
        }
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Segmented control
                    chartTabPicker
                        .padding()
                    
                    // Content
                    TabView(selection: $selectedTab) {
                        birthChartContent
                            .tag(ChartTab.birthChart)
                        
                        numerologyContent
                            .tag(ChartTab.numerology)
                        
                        compatibilityContent
                            .tag(ChartTab.compatibility)
                        
                        AdvancedChartsView()
                            .tag(ChartTab.advanced)
                    }
                    .tabViewStyle(.page(indexDisplayMode: .never))
                }
            }
            .navigationTitle("Charts")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        exportChart()
                    } label: {
                        if isExporting {
                            ProgressView()
                                .scaleEffect(0.8)
                        } else {
                            Image(systemName: "square.and.arrow.up")
                        }
                    }
                    .disabled(store.activeProfile == nil || isExporting)
                }
            }
        }
    }
    
    // MARK: - Tab Picker
    
    private var chartTabPicker: some View {
        HStack(spacing: 0) {
            ForEach(ChartTab.allCases, id: \.self) { tab in
                Button {
                    withAnimation(.spring(duration: 0.3)) {
                        selectedTab = tab
                    }
                    HapticManager.impact(.light)
                } label: {
                    VStack(spacing: 6) {
                        Image(systemName: tab.icon)
                            .font(.title2)
                        Text(tab.rawValue)
                            .font(.caption)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(minHeight: 44) // Apple HIG minimum tap target
                    .padding(.vertical, 12)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(selectedTab == tab ? tab.color.opacity(0.2) : Color.clear)
                    )
                    .foregroundStyle(selectedTab == tab ? tab.color : Color.subtleText)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(4)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }
    
    // MARK: - Birth Chart Content
    
    private var birthChartContent: some View {
        // Use the embedded chart view for a full chart experience
        EmbeddedChartView()
    }
    
    // MARK: - Numerology Content
    
    private var numerologyContent: some View {
        ScrollView {
            VStack(spacing: 16) {
                if let profile = store.selectedProfile {
                    // Profile card for numerology
                    CardView {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("📊 Numerology Profile")
                                .font(.headline)
                            
                            Text("Based on: \(profile.name)")
                                .font(.subtext)
                            
                            Text("Birth Date: ••••-••-••")
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    
                    // Navigate to full numerology
                    NavigationLink {
                        NumerologyView()
                    } label: {
                        ChartsActionCard(
                            title: "Full Numerology Analysis",
                            subtitle: "Deep dive into your number meanings",
                            icon: "number.circle.fill",
                            gradient: [.purple, .blue]
                        )
                    }
                    .buttonStyle(.plain)
                    
                    // Numerology info
                    CardView {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("🔢 Your Core Numbers")
                                .font(.headline)
                            
                            Text("Get your Life Path, Expression, Soul Urge, and Personality numbers calculated from your name and birth date.")
                                .font(.label)
                                .foregroundStyle(Color.textMuted)
                        }
                    }
                    
                } else {
                    ChartsNoProfileCard(
                        title: "Discover Your Numbers",
                        subtitle: "Enter your birth date to calculate your core numbers",
                        icon: "number.circle.fill"
                    )
                }
            }
            .padding()
        }
    }
    
    // MARK: - Compatibility Content
    
    private var compatibilityContent: some View {
        ScrollView {
            VStack(spacing: 16) {
                // New compatibility check
                NavigationLink {
                    CompatibilityView()
                } label: {
                    VStack(spacing: 16) {
                        ZStack {
                            Circle()
                                .fill(
                                    LinearGradient(
                                        colors: [.pink, .purple],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(width: 80, height: 80)
                            
                            Image(systemName: "heart.fill")
                                .font(.largeTitle)
                                .foregroundStyle(.white)
                        }
                        
                        Text("Check Compatibility")
                            .font(.title2.bold())
                        
                        Text("Compare your charts with someone special")
                            .font(.subheadline)
                            .foregroundStyle(Color.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 32)
                    .background(
                        RoundedRectangle(cornerRadius: 20)
                            .fill(.ultraThinMaterial)
                    )
                }
                .buttonStyle(.plain)
                
                // Compatibility tips
                VStack(alignment: .leading, spacing: 12) {
                    Text("Compatibility Insights")
                        .font(.headline)
                    
                    ChartsCompatibilityTipRow(
                        icon: "☀️",
                        title: "Sun Signs",
                        description: "Core personality compatibility"
                    )
                    
                    ChartsCompatibilityTipRow(
                        icon: "🌙",
                        title: "Moon Signs",
                        description: "Emotional understanding"
                    )
                    
                    ChartsCompatibilityTipRow(
                        icon: "💕",
                        title: "Venus Signs",
                        description: "Love language harmony"
                    )
                    
                    ChartsCompatibilityTipRow(
                        icon: "💬",
                        title: "Mercury Signs",
                        description: "Communication style"
                    )
                }
                
                // Saved relationships
                NavigationLink {
                    RelationshipsView()
                } label: {
                    CardView {
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Saved Relationships")
                                    .font(.headline)
                                Text("View your compatibility history")
                                    .font(.label)
                                    .foregroundStyle(Color.textSecondary)
                            }
                            
                            Spacer()
                            
                            Image(systemName: "chevron.right")
                                .foregroundStyle(Color.subtleText)
                        }
                    }
                }
                .buttonStyle(.plain)
            }
            .padding()
        }
    }
}

// MARK: - Chart Export

extension ChartsView {
    @MainActor
    private func exportChart() {
        guard let profile = store.activeProfile else { return }
        isExporting = true
        
        let exportView = ChartExportCard(
            profileName: profile.name,
            dateOfBirth: profile.dateOfBirth,
            sunSign: profile.sunSign,
            moonSign: store.activeMoonSign,
            risingSign: store.activeRisingSign,
            element: profile.element,
            modality: profile.modality
        )
        
        let renderer = ImageRenderer(content: exportView)
        renderer.scale = 3.0
        
        if let image = renderer.uiImage {
            let activityVC = UIActivityViewController(
                activityItems: [image, "My cosmic chart from AstroNumeric ✨"],
                applicationActivities: nil
            )
            
            if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
               let rootVC = windowScene.windows.first?.rootViewController {
                rootVC.present(activityVC, animated: true)
            }
        }
        
        isExporting = false
    }
}

// MARK: - Chart Export Card

struct ChartExportCard: View {
    let profileName: String
    let dateOfBirth: String
    let sunSign: String
    let moonSign: String?
    let risingSign: String?
    let element: String
    let modality: String
    
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(hex: "0d0221"), Color(hex: "1a0533"), Color(hex: "2a1a5e")],
                startPoint: .top,
                endPoint: .bottom
            )
            
            VStack(spacing: 24) {
                // Header
                Text("ASTRONUMERIC")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .tracking(6)
                    .foregroundStyle(.white.opacity(0.5))
                
                // Name
                Text(profileName.uppercased())
                    .font(.system(size: 28, weight: .bold, design: .serif))
                    .foregroundColor(.white)
                
                // Divider
                Rectangle()
                    .fill(
                        LinearGradient(
                            colors: [.clear, .purple.opacity(0.6), .clear],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(height: 1)
                    .padding(.horizontal, 40)
                
                // Big Three
                HStack(spacing: 24) {
                    chartSignColumn(label: "SUN", sign: sunSign, emoji: sunEmoji(sunSign))
                    
                    if let moon = moonSign {
                        chartSignColumn(label: "MOON", sign: moon, emoji: "🌙")
                    }
                    
                    if let rising = risingSign {
                        chartSignColumn(label: "RISING", sign: rising, emoji: "⬆️")
                    }
                }
                
                // Element & Modality
                HStack(spacing: 20) {
                    chartInfoPill(label: elementEmoji(element) + " " + element)
                    chartInfoPill(label: modality)
                }
                
                // Birth Details
                Text("Born: ••••-••-••")
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundStyle(.white.opacity(0.4))
                
                // Footer
                Text("astronumeric.app")
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.white.opacity(0.3))
            }
            .padding(32)
        }
        .frame(width: 375, height: 500)
        .clipShape(RoundedRectangle(cornerRadius: 24))
    }
    
    private func chartSignColumn(label: String, sign: String, emoji: String) -> some View {
        VStack(spacing: 6) {
            Text(emoji)
                .font(.system(size: 28))
            Text(label)
                .font(.system(size: 9, weight: .bold, design: .monospaced))
                .tracking(2)
                .foregroundStyle(.white.opacity(0.5))
            Text(sign.uppercased())
                .font(.system(size: 14, weight: .bold))
                .foregroundColor(.white)
        }
    }
    
    private func chartInfoPill(label: String) -> some View {
        Text(label)
            .font(.system(size: 11, weight: .medium))
            .foregroundStyle(.white.opacity(0.8))
            .padding(.horizontal, 14)
            .padding(.vertical, 6)
            .background(
                Capsule()
                    .fill(.white.opacity(0.1))
                    .overlay(
                        Capsule()
                            .strokeBorder(.white.opacity(0.15), lineWidth: 1)
                    )
            )
    }
    
    private func sunEmoji(_ sign: String) -> String {
        switch sign {
        case "Aries": return "♈️"
        case "Taurus": return "♉️"
        case "Gemini": return "♊️"
        case "Cancer": return "♋️"
        case "Leo": return "♌️"
        case "Virgo": return "♍️"
        case "Libra": return "♎️"
        case "Scorpio": return "♏️"
        case "Sagittarius": return "♐️"
        case "Capricorn": return "♑️"
        case "Aquarius": return "♒️"
        case "Pisces": return "♓️"
        default: return "⭐️"
        }
    }
    
    private func elementEmoji(_ element: String) -> String {
        switch element {
        case "Fire": return "🔥"
        case "Earth": return "🌍"
        case "Air": return "💨"
        case "Water": return "💧"
        default: return "✨"
        }
    }
}

// MARK: - Supporting Views

struct ChartsProfileInfoCard: View {
    let profile: Profile
    
    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("✨ Your Birth Chart")
                        .font(.headline)
                    Spacer()
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(profile.name)
                        .font(.subheadline.weight(.medium))
                    
                    Text("Born: ••••-••-••")
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                    
                    if let place = profile.placeOfBirth {
                        Text("Location: \(place)")
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    
                    if let time = profile.timeOfBirth {
                        Text("Time: \(time)")
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                }
            }
        }
    }
}

struct ChartsActionCard: View {
    let title: String
    let subtitle: String
    let icon: String
    let gradient: [Color]
    
    var body: some View {
        HStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(Color.white.opacity(0.2))
                    .frame(width: 50, height: 50)
                
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundStyle(.white)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(subtitle)
                    .font(.caption)
                    .opacity(0.8)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right.circle.fill")
                .font(.title2)
                .opacity(0.8)
        }
        .foregroundStyle(.white)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(
                    LinearGradient(
                        colors: gradient,
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
        )
    }
}

struct ChartsNoProfileCard: View {
    let title: String
    let subtitle: String
    let icon: String
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 50))
                .foregroundStyle(Color.textSecondary)
            
            Text(title)
                .font(.title2.bold())
            
            Text(subtitle)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
            
            NavigationLink {
                ProfileView()
            } label: {
                Text("Set Up Profile")
                    .font(.headline)
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.purple)
                    )
            }
            .padding(.top)
        }
        .padding(32)
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(.ultraThinMaterial)
        )
    }
}

struct ChartsCompatibilityTipRow: View {
    let icon: String
    let title: String
    let description: String
    
    var body: some View {
        HStack(spacing: 12) {
            Text(icon)
                .font(.title2)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.medium))
                Text(description)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
            }
            
            Spacer()
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(.ultraThinMaterial)
        )
    }
}

// MARK: - Preview

#Preview {
    ChartsView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
