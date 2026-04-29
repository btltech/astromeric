// ShareCardView.swift
// Visual share card for readings using ImageRenderer

import SwiftUI

struct ShareCardView: View {
    let reading: PredictionData
    
    var body: some View {
        VStack(spacing: 0) {
            shareCardHeader(icon: "sparkles", title: "AstroNumeric")
            
            // Content
            VStack(spacing: 16) {
                // Scope and date
                Text(String(format: "fmt.shareCard.1".localized, "\(reading.scope.capitalized)"))
                    .font(.headline)
                
                Text(reading.date)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)

                Text("ui.shareCard.0".localized)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)
                
                // Score
                ZStack {
                    Circle()
                        .stroke(Color.purple.opacity(0.3), lineWidth: 8)
                        .frame(width: 80, height: 80)
                    
                    Circle()
                        .trim(from: 0, to: CGFloat(reading.overallScore) / 10)
                        .stroke(
                            LinearGradient(
                                colors: [.purple, .pink],
                                startPoint: .leading,
                                endPoint: .trailing
                            ),
                            style: StrokeStyle(lineWidth: 8, lineCap: .round)
                        )
                        .frame(width: 80, height: 80)
                        .rotationEffect(.degrees(-90))
                    
                    VStack(spacing: 2) {
                        Text(String(format: "%.1f", reading.overallScore))
                            .font(.title2.bold())
                        Text("/10")
                            .font(.caption2)
                            .foregroundStyle(Color.textSecondary)
                    }
                }
                
                // Top sections
                ForEach(reading.sections.prefix(3)) { section in
                    HStack {
                        Text(section.title)
                            .font(.subheadline)
                        Spacer()
                        Text(section.summary.prefix(30) + (section.summary.count > 30 ? "..." : ""))
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                            .lineLimit(1)
                    }
                    .padding(.horizontal)
                }
            }
            .padding()
            .background(Color(.systemBackground))
            
            shareCardFooter
        }
        .frame(width: 300)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.2), radius: 10)
    }
}

// MARK: - Share Card Generator

@MainActor
struct ShareCardGenerator {
    // Reading share card
    static func generateImage(for reading: PredictionData) -> UIImage? {
        let view = ShareCardView(reading: reading)
        let renderer = ImageRenderer(content: view)
        renderer.scale = 3.0 // High resolution
        return renderer.uiImage
    }
    
    // Numerology share card
    static func generateImage(for numerology: NumerologyData, profileName: String) -> UIImage? {
        let safeName = AppStore.shared.hideSensitiveDetailsEnabled ? PrivacyRedaction.privateProfile : profileName
        let view = NumerologyShareCard(data: numerology, profileName: safeName)
        let renderer = ImageRenderer(content: view)
        renderer.scale = 3.0
        return renderer.uiImage
    }
    
    // Timing share card
    static func generateImage(for timing: TimingResult, activity: String) -> UIImage? {
        let view = TimingShareCard(data: timing, activity: activity)
        let renderer = ImageRenderer(content: view)
        renderer.scale = 3.0
        return renderer.uiImage
    }
    
    // Chart share card
    static func generateImage(for chart: ChartData, profileName: String, birthTimeAssumed: Bool = false) -> UIImage? {
        let safeName = AppStore.shared.hideSensitiveDetailsEnabled ? PrivacyRedaction.privateProfile : profileName
        let view = ChartShareCard(data: chart, profileName: safeName, birthTimeAssumed: birthTimeAssumed)
        let renderer = ImageRenderer(content: view)
        renderer.scale = 3.0
        return renderer.uiImage
    }
}

// MARK: - Numerology Share Card

struct NumerologyShareCard: View {
    let data: NumerologyData
    let profileName: String
    
    var body: some View {
        VStack(spacing: 0) {
            // Header with gradient
            shareCardHeader(icon: "sparkle", title: "Numerology")
            
            // Content
            VStack(spacing: 16) {
                Text(profileName)
                    .font(.headline)
                
                if let lifePath = data.lifePath {
                    VStack(spacing: 8) {
                        Text("ui.shareCard.1".localized)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                        
                        Text("\(lifePath.number)")
                            .font(.system(.largeTitle)).fontWeight(.bold)
                            .foregroundStyle(.purple)
                        
                        if let meaning = lifePath.meaning {
                            Text(meaning.prefix(60) + (meaning.count > 60 ? "..." : ""))
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                                .multilineTextAlignment(.center)
                        }
                    }
                }
                
                if let luckyNumbers = data.luckyNumbers, !luckyNumbers.isEmpty {
                    HStack(spacing: 8) {
                        Text("ui.shareCard.2".localized)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                        ForEach(luckyNumbers.prefix(5), id: \.self) { num in
                            Text("\(num)")
                                .font(.caption.bold())
                                .foregroundStyle(.purple)
                        }
                    }
                }
            }
            .padding()
            .background(Color(.systemBackground))
            
            shareCardFooter
        }
        .frame(width: 300)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.2), radius: 10)
    }
}

// MARK: - Timing Share Card

struct TimingShareCard: View {
    let data: TimingResult
    let activity: String
    
    var body: some View {
        VStack(spacing: 0) {
            shareCardHeader(icon: "clock.badge.checkmark", title: "Best Timing")
            
            VStack(spacing: 16) {
                Text(activity.capitalized)
                    .font(.headline)
                
                if let best = data.bestTimes.first {
                    VStack(spacing: 4) {
                        Text("ui.shareCard.3".localized)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                        
                        Text(best)
                            .font(.title2.bold())
                            .foregroundStyle(.green)
                    }
                }
                
                if !data.tips.isEmpty {
                    Text("💡 \(data.tips.first ?? "")")
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                }
            }
            .padding()
            .background(Color(.systemBackground))
            
            shareCardFooter
        }
        .frame(width: 300)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.2), radius: 10)
    }
}

// MARK: - Chart Share Card

struct ChartShareCard: View {
    let data: ChartData
    let profileName: String
    var birthTimeAssumed: Bool = false

    var body: some View {
        VStack(spacing: 0) {
            shareCardHeader(icon: "circle.hexagongrid", title: "Birth Chart")

            VStack(spacing: 16) {
                Text(profileName)
                    .font(.headline)

                // Big Three
                HStack(spacing: 20) {
                    if let sun = data.planets.first(where: { $0.name == "Sun" }) {
                        BigThreeShareItem(label: "☉", sign: sun.sign, estimated: false)
                    }
                    if let moon = data.planets.first(where: { $0.name == "Moon" }) {
                        BigThreeShareItem(label: "☾", sign: moon.sign, estimated: false)
                    }
                    if let asc = data.planets.first(where: { $0.name == "Asc" }) {
                        BigThreeShareItem(label: "↑", sign: asc.sign, estimated: birthTimeAssumed)
                    }
                }

                // More planets summary
                let planetCount = data.planets.count
                Text(String(format: "fmt.shareCard.0".localized, "\(planetCount)"))
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)

                if birthTimeAssumed {
                    Text("ui.shareCard.4".localized)
                        .font(.caption2)
                        .foregroundStyle(.orange)
                        .multilineTextAlignment(.center)
                }
            }
            .padding()
            .background(Color(.systemBackground))

            shareCardFooter
        }
        .frame(width: 300)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.2), radius: 10)
    }
}

struct BigThreeShareItem: View {
    let label: String
    let sign: String
    var estimated: Bool = false

    var body: some View {
        VStack(spacing: 4) {
            Text(label)
                .font(.title2)
            Text(estimated ? "~\(sign)" : sign)
                .font(.caption.bold())
                .foregroundStyle(estimated ? .orange : .purple)
            if estimated {
                Text("ui.shareCard.5".localized)
                    .font(.system(.caption2))
                    .foregroundStyle(.orange.opacity(0.8))
            }
        }
    }
}

// MARK: - Shared Components

@ViewBuilder
private func shareCardHeader(icon: String, title: String) -> some View {
    ZStack {
        LinearGradient(
            colors: [Color(hex: "20123a"), Color(hex: "6241b5"), Color(hex: "187f8a")],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.system(.title))
                .foregroundStyle(.white)
            
            Text(title)
                .font(.title3.bold())
                .foregroundStyle(.white)

            Text("ui.shareCard.6".localized)
                .font(.caption2.weight(.medium))
                .foregroundStyle(.white.opacity(0.75))
        }
        .padding(.vertical, 20)
    }
    .frame(height: 90)
}

private var shareCardFooter: some View {
    VStack(spacing: 4) {
        Text("ui.shareCard.7".localized)
            .font(.caption2.weight(.semibold))
            .foregroundStyle(Color.textSecondary)
        Text("ui.shareCard.8".localized)
            .font(.system(.caption2, design: .monospaced)).fontWeight(.medium)
            .foregroundStyle(Color.textMuted)
    }
    .padding(.vertical, 8)
    .frame(maxWidth: .infinity)
    .background(Color(.secondarySystemBackground))
}

// MARK: - Enhanced Share Sheet

struct EnhancedShareSheet: UIViewControllerRepresentable {
    let items: [Any]
    
    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items, applicationActivities: nil)
    }
    
    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

// MARK: - Preview

#Preview {
    ZStack {
        Color.black.ignoresSafeArea()
        
        ShareCardView(reading: PredictionData(
            profile: nil,
            scope: "daily",
            date: "2024-01-15",
            sections: [
                ForecastSection(title: "Love", summary: "Good day for romance and connections", topics: [:], avoid: [], embrace: []),
                ForecastSection(title: "Career", summary: "Focus on long-term goals", topics: [:], avoid: [], embrace: []),
                ForecastSection(title: "Health", summary: "Energy levels are high", topics: [:], avoid: [], embrace: [])
            ],
            overallScore: 8.2,
            generatedAt: "2024-01-15T10:00:00Z"
        ))
    }
}
