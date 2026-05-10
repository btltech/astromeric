// ChartsView.swift
// Progressive disclosure chart hub — Big 3 → Numerology → Compatibility → Advanced

import SwiftUI

struct ChartsView: View {
    @Environment(AppStore.self) private var store
    @State private var isExporting = false

    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()

                ScrollView {
                    VStack(alignment: .leading, spacing: Space.lg) {
                        PremiumScreenHeader(
                            eyebrow: "hero.charts.eyebrow".localized,
                            title: "hero.charts.title".localized,
                            subtitle: "hero.charts.body".localized,
                            accent: .accentPrimary,
                            chips: [
                                "hero.charts.chip.0".localized,
                                "hero.charts.chip.1".localized,
                                "hero.charts.chip.2".localized,
                                "hero.charts.chip.3".localized
                            ]
                        )

                        // SECTION: Birth Chart — always first, most fundamental
                        ToolSectionHeader(
                            title: "section.charts.birthChart.title".localized,
                            subtitle: "section.charts.birthChart.subtitle".localized,
                            badge: "badge.calculated".localized
                        )
                        EmbeddedChartView()

                        // SECTION: Numerology
                        ToolSectionHeader(
                            title: "section.charts.numerology.title".localized,
                            subtitle: "section.charts.numerology.subtitle".localized,
                            badge: "badge.calculated".localized
                        )
                        numerologySection

                        // SECTION: Compatibility
                        ToolSectionHeader(
                            title: "section.charts.compat.title".localized,
                            subtitle: "section.charts.compat.subtitle".localized,
                            badge: "badge.calculated".localized
                        )
                        compatibilitySection

                        // SECTION: Advanced — gated behind a single link (progressive disclosure)
                        ToolSectionHeader(
                            title: "section.charts.advanced.title".localized,
                            subtitle: "section.charts.advanced.subtitle".localized,
                            badge: "badge.advanced".localized,
                            accent: .cosmicBlue
                        )
                        NavigationLink {
                            AdvancedChartsView()
                        } label: {
                            ChartsActionCard(
                                title: "ui.charts.advancedCharts".localized,
                                subtitle: "ui.charts.advancedChartsSubtitle".localized,
                                icon: "sparkles",
                                gradient: [.accentPrimary, .cosmicBlue]
                            )
                        }
                        .buttonStyle(ScaleButtonStyle())
                        .accessibilityLabel("section.charts.advanced.title".localized)
                    }
                    .padding()
                    .readableContainer()
                }
            }
            .navigationTitle("charts.title".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        exportChart()
                    } label: {
                        if isExporting {
                            ProgressView().scaleEffect(0.8)
                        } else {
                            Image(systemName: "square.and.arrow.up")
                        }
                    }
                    .disabled(store.activeProfile == nil || isExporting)
                }
            }
        }
    }

    // MARK: - Numerology Section

    private var numerologySection: some View {
        Group {
            if let profile = store.selectedProfile {
                VStack(spacing: Space.sm) {
                    CardView {
                        VStack(alignment: .leading, spacing: Space.sm) {
                            Text("ui.charts.0".localized)
                                .font(.headline)
                            Text(String(format: "fmt.charts.2".localized, "\(profile.displayName(hideSensitive: store.hideSensitiveDetailsEnabled, role: .activeUser))"))
                                .font(.subtext)
                            Text("ui.charts.1".localized)
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    NavigationLink {
                        NumerologyView()
                    } label: {
                        ChartsActionCard(
                            title: "ui.charts.numerologyFull".localized,
                            subtitle: "ui.charts.numerologyFullSubtitle".localized,
                            icon: "number.circle.fill",
                            gradient: [.accentPrimary, .cosmicBlue]
                        )
                    }
                    .buttonStyle(ScaleButtonStyle())
                }
            } else {
                Text("charts.numerology.noProfile".localized)
                    .font(.subtext)
                    .foregroundStyle(Color.textMuted)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
    }

    // MARK: - Compatibility Section

    private var compatibilitySection: some View {
        VStack(spacing: Space.sm) {
            NavigationLink {
                CompatibilityView()
            } label: {
                ChartsActionCard(
                    title: "ui.charts.4".localized,
                    subtitle: "ui.charts.5".localized,
                    icon: "heart.circle.fill",
                    gradient: [.accentSecondary, .accentPrimary]
                )
            }
            .buttonStyle(ScaleButtonStyle())

            NavigationLink {
                RelationshipsView()
            } label: {
                CardView {
                    HStack {
                        VStack(alignment: .leading, spacing: Space.xs) {
                            Text("ui.charts.7".localized)
                                .font(.headline)
                            Text("ui.charts.8".localized)
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundStyle(Color.subtleText)
                    }
                }
            }
            .buttonStyle(ScaleButtonStyle())
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
            profileName: profile.displayName(
                hideSensitive: store.hideSensitiveDetailsEnabled,
                role: .share
            ),
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
                Text("ui.charts.9".localized)
                    .font(.system(.caption, design: .monospaced)).fontWeight(.bold)
                    .tracking(6)
                    .foregroundStyle(.white.opacity(0.5))
                
                // Name
                Text(profileName.uppercased())
                    .font(.system(.title, design: .serif)).fontWeight(.bold)
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
                Text("ui.charts.10".localized)
                    .font(.system(.caption, design: .monospaced))
                    .foregroundStyle(.white.opacity(0.4))
                
                // Footer
                Text("ui.charts.11".localized)
                    .font(.system(.caption2, design: .monospaced))
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
                .font(.system(.title))
            Text(label)
                .font(.system(.caption2, design: .monospaced)).fontWeight(.bold)
                .tracking(2)
                .foregroundStyle(.white.opacity(0.5))
            Text(sign.uppercased())
                .font(.system(.subheadline)).fontWeight(.bold)
                .foregroundColor(.white)
        }
    }
    
    private func chartInfoPill(label: String) -> some View {
        Text(label)
            .font(.system(.caption)).fontWeight(.medium)
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
    @Environment(AppStore.self) private var store
    let profile: Profile
    
    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("ui.charts.12".localized)
                        .font(.headline)
                    Spacer()
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(profile.displayName(hideSensitive: store.hideSensitiveDetailsEnabled, role: .activeUser))
                        .font(.subheadline.weight(.medium))
                    
                    Text("ui.charts.13".localized)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                    
                    if let place = profile.placeOfBirth {
                        Text(String(format: "fmt.charts.1".localized, "\(store.hideSensitiveDetailsEnabled ? PrivacyRedaction.hiddenValue : place)"))
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    
                    if let time = profile.timeOfBirth {
                        Text(String(format: "fmt.charts.0".localized, "\(store.hideSensitiveDetailsEnabled ? PrivacyRedaction.hiddenValue : time)"))
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
            RoundedRectangle(cornerRadius: Radius.md)
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
                .font(.system(.largeTitle))
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
                Text("ui.charts.14".localized)
                    .font(.headline)
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: Radius.sm)
                            .fill(Color.accentPrimary)
                    )
            }
            .padding(.top)
        }
        .padding(Space.xl)
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: Radius.md)
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
            RoundedRectangle(cornerRadius: Radius.sm)
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
