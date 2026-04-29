// LifePhaseCard.swift
// "The Pattern"-style life phase narrative — current astrological life cycle

import SwiftUI

// MARK: - Models

struct LifePhaseData: Codable {
    let currentPhase: LifePhase
    let nextPhase: UpcomingPhase?

    enum CodingKeys: String, CodingKey {
        case currentPhase = "current_phase"
        case nextPhase = "next_phase"
    }
}

struct LifePhase: Codable {
    let name: String
    let age: Int
    let minAge: Int
    let maxAge: Int
    let duration: String
    let narrative: String
    let keywords: [String]
    let progressPct: Int

    enum CodingKeys: String, CodingKey {
        case name, age, duration, narrative, keywords
        case minAge = "min_age"
        case maxAge = "max_age"
        case progressPct = "progress_pct"
    }
}

struct UpcomingPhase: Codable {
    let name: String
    let beginsInYears: Int
    let beginsAtAge: Int
    let preview: String

    enum CodingKeys: String, CodingKey {
        case name, preview
        case beginsInYears = "begins_in_years"
        case beginsAtAge = "begins_at_age"
    }
}

// MARK: - Life Phase Card View

struct LifePhaseCard: View {
    let data: LifePhaseData
    @State private var expanded = false

    var current: LifePhase { data.currentPhase }

    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 14) {
                // Header
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Label("ui.lifePhaseCard.0".localized, systemImage: "arrow.trianglehead.clockwise")
                            .font(.caption.bold())
                            .foregroundStyle(Color.textSecondary)
                            .accessibilityHidden(true)
                        Text(current.name)
                            .font(.title3.bold())
                            .accessibilityAddTraits(.isHeader)
                    }
                    Spacer()
                    Text(String(format: "fmt.lifePhaseCard.2".localized, "\(current.age)"))
                        .font(.caption.bold())
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(Color.accentColor.opacity(0.15))
                        .foregroundStyle(Color.accentColor)
                        .clipShape(Capsule())
                        .accessibilityLabel("Current age: \(current.age)")
                }

                // Progress bar: where in this phase are you?
                VStack(alignment: .leading, spacing: 4) {
                    GeometryReader { geo in
                        ZStack(alignment: .leading) {
                            Capsule()
                                .fill(Color.surfaceElevated)
                                .frame(height: 6)
                            Capsule()
                                .fill(Color.accentColor)
                                .frame(width: geo.size.width * CGFloat(current.progressPct) / 100.0, height: 6)
                                .animation(.spring(response: 0.8), value: current.progressPct)
                        }
                    }
                    .frame(height: 6)
                    .accessibilityLabel("Phase progress: \(current.progressPct)% through \(current.name)")
                    .accessibilityValue("\(current.progressPct) percent")
                    HStack {
                        Text(String(format: "fmt.lifePhaseCard.1".localized, "\(current.minAge)", "\(current.maxAge)"))
                        Spacer()
                        Text("~\(current.duration)")
                    }
                    .font(.caption)
                    .foregroundStyle(Color.textMuted)
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Ages \(current.minAge) to \(current.maxAge), duration approximately \(current.duration)")
                }

                // Narrative — expandable
                Text(expanded ? current.narrative : String(current.narrative.prefix(120)) + (current.narrative.count > 120 ? "…" : ""))
                    .font(.subheadline)
                    .foregroundStyle(Color.textPrimary)
                    .fixedSize(horizontal: false, vertical: true)
                    .animation(.easeInOut(duration: 0.2), value: expanded)
                    .accessibilityLabel(expanded ? current.narrative : String(current.narrative.prefix(120)))

                Button(expanded ? "tern.lifePhaseCard.0a".localized : "tern.lifePhaseCard.0b".localized) {
                    withAnimation { expanded.toggle() }
                }
                .font(.caption.bold())
                .foregroundStyle(Color.accentColor)
                .accessibilityLabel(expanded ? "tern.lifePhaseCard.1a".localized : "tern.lifePhaseCard.1b".localized)
                .accessibilityHint(expanded ? "Collapses description" : "Expands full description of \(current.name)")

                // Keywords
                HStack(spacing: 6) {
                    ForEach(current.keywords, id: \.self) { kw in
                        Text(kw)
                            .font(.caption2.bold())
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.purple.opacity(0.12))
                            .foregroundStyle(.purple)
                            .clipShape(Capsule())
                            .accessibilityLabel("Theme: \(kw)")
                    }
                }
                .accessibilityElement(children: .contain)

                // Upcoming phase teaser
                if let next = data.nextPhase {
                    Divider()
                    HStack(alignment: .top, spacing: 10) {
                        Image(systemName: "chevron.forward.2")
                            .font(.caption)
                            .foregroundStyle(Color.textMuted)
                            .padding(.top, 2)
                            .accessibilityHidden(true)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(String(format: "fmt.lifePhaseCard.0".localized, "\(next.beginsInYears)", "\(next.name)"))
                                .font(.caption.bold())
                            Text(next.preview)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                                .lineLimit(2)
                        }
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Upcoming: \(next.name) in \(next.beginsInYears) years at age \(next.beginsAtAge). \(next.preview)")
                }
            }
        }
    }
}
