// TemporalMatrixView.swift
// Temporal Threat Matrix — 48h calendar events with cosmic weather overlay
// Surfaces CalendarOracle data as a tactical event HUD

import SwiftUI
import EventKit

struct TemporalMatrixView: View {
    @Environment(AppStore.self) private var store
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @State private var events: [CalendarOracle.CosmicEvent] = []
    @State private var snapshots: [Date: CalendarOracle.HorarySnapshot] = [:]
    @State private var isLoading = true
    @State private var permissionDenied = false

    private var prefersStackedEventLayout: Bool {
        dynamicTypeSize.isAccessibilitySize
    }
    
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 16) {
                    PremiumHeroCard(
                            eyebrow: "hero.temporalMatrix.eyebrow".localized,
                            title: "hero.temporalMatrix.title".localized,
                            bodyText: "hero.temporalMatrix.body".localized,
                            accent: [Color(hex: "101f39"), Color(hex: "2f55b3"), Color(hex: "14808a")],
                            chips: ["hero.temporalMatrix.chip.0".localized, "hero.temporalMatrix.chip.1".localized, "hero.temporalMatrix.chip.2".localized]
                        )

                    headerSection

                    PremiumSectionHeader(
                title: "section.temporalMatrix.0.title".localized,
                subtitle: "section.temporalMatrix.0.subtitle".localized
            )
                    
                    if isLoading {
                        loadingSection
                    } else if permissionDenied {
                        permissionDeniedSection
                    } else if events.isEmpty {
                        emptySection
                    } else {
                        eventsSection
                    }
                }
                .padding()
                .readableContainer()
            }
        }
        .navigationTitle("screen.temporalMatrix".localized)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await loadEvents()
        }
    }
    
    // MARK: - Header
    
    private var headerSection: some View {
        VStack(spacing: 6) {
            Text("⏱")
                .font(.system(.largeTitle))
            Text("ui.temporalMatrix.0".localized)
                .font(.title3.bold())
            Text("ui.temporalMatrix.1".localized)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
        }
        .padding(.top, 10)
    }
    
    // MARK: - Loading
    
    private var loadingSection: some View {
        VStack(spacing: 12) {
            ProgressView()
            Text("ui.temporalMatrix.2".localized)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
        }
        .padding(.vertical, 40)
    }
    
    // MARK: - Permission Denied
    
    private var permissionDeniedSection: some View {
        VStack(spacing: 12) {
            Image(systemName: "calendar.badge.exclamationmark")
                .font(.largeTitle)
                .foregroundStyle(.orange)
            Text("ui.temporalMatrix.3".localized)
                .font(.headline)
            Text("ui.temporalMatrix.4".localized)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
            
            Button("ui.temporalMatrix.7".localized) {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            }
            .buttonStyle(.borderedProminent)
            .tint(.blue)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }
    
    // MARK: - Empty
    
    private var emptySection: some View {
        VStack(spacing: 12) {
            Image(systemName: "calendar")
                .font(.largeTitle)
                .foregroundStyle(.secondary)
            Text("ui.temporalMatrix.5".localized)
                .font(.headline)
            Text("ui.temporalMatrix.6".localized)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }
    
    // MARK: - Events
    
    private var eventsSection: some View {
        LazyVStack(spacing: 12) {
            ForEach(Array(events.enumerated()), id: \.offset) { _, event in
                eventCard(event)
            }
        }
    }
    
    private func eventCard(_ event: CalendarOracle.CosmicEvent) -> some View {
        let snapshot = snapshots[event.startDate]
        let threatLevel = snapshot?.threatLevel ?? .yellow
        let threatColor: Color = {
            switch threatLevel {
            case .green: return .green
            case .yellow: return .yellow
            case .red: return .red
            }
        }()
        
        return VStack(alignment: .leading, spacing: 10) {
            if prefersStackedEventLayout {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 6) {
                        timeBadge(for: event.startDate)
                        eventIdentity(for: event)
                    }

                    Spacer()

                    Text(threatLevel.label)
                        .font(.title2)
                }
            } else {
                HStack(alignment: .top) {
                    timeBadge(for: event.startDate)
                        .frame(minWidth: 65, alignment: .leading)

                    eventIdentity(for: event)

                    Spacer()

                    Text(threatLevel.label)
                        .font(.title2)
                }
            }
            
            // Cosmic weather row
            HStack(spacing: 8) {
                Text("↳")
                    .foregroundStyle(Color.textSecondary)
                
                cosmicBadge(
                    icon: planetSymbol(event.planetaryHour),
                    text: "Hour of \(event.planetaryHour)",
                    color: threatColor
                )
                
                if event.isVoidOfCourse {
                    cosmicBadge(icon: "⚠️", text: "Moon VOC", color: .red)
                } else {
                    cosmicBadge(
                        icon: "☽",
                        text: "\(event.moonSign)",
                        color: .cyan
                    )
                }
            }
            
            // Key transits
            if !event.keyTransits.isEmpty {
                HStack(spacing: 4) {
                    Text("↳")
                        .foregroundStyle(Color.textSecondary)
                    Text(event.keyTransits.prefix(2).joined(separator: " • "))
                        .font(.system(.caption2, design: .monospaced))
                        .foregroundStyle(.cyan.opacity(0.7))
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(threatColor.opacity(0.3), lineWidth: 1)
                )
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilitySummary(for: event, threatLevel: threatLevel.label))
    }
    
    // MARK: - Helpers
    
    private func cosmicBadge(icon: String, text: String, color: Color) -> some View {
        HStack(spacing: 4) {
            Text(icon)
                .font(.caption2)
            Text(text)
                .font(.caption2.bold())
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(
            Capsule()
                .fill(color.opacity(0.15))
        )
        .foregroundStyle(color)
    }

    private func timeBadge(for date: Date) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(timeString(date))
                .font(.system(.subheadline, design: .monospaced).bold())
            if !Calendar.current.isDateInToday(date) {
                Text(dayString(date))
                    .font(.system(.caption2, design: .monospaced))
                    .foregroundStyle(Color.textSecondary)
            }
        }
    }

    private func eventIdentity(for event: CalendarOracle.CosmicEvent) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(event.title)
                .font(.headline)
                .lineLimit(prefersStackedEventLayout ? nil : 2)

            if let loc = event.location, !loc.isEmpty {
                HStack(spacing: 4) {
                    Image(systemName: "location.fill")
                        .font(.caption2)
                    Text(loc)
                        .font(.caption)
                }
                .foregroundStyle(Color.textSecondary)
            }
        }
    }

    private func accessibilitySummary(for event: CalendarOracle.CosmicEvent, threatLevel: String) -> String {
        var parts = [
            event.title,
            "\(dayString(event.startDate)) \(timeString(event.startDate))",
            "Moon in \(event.moonSign)",
            "Planetary hour of \(event.planetaryHour)",
            "Threat \(threatLevel)"
        ]

        if event.isVoidOfCourse {
            parts.append("Void of course moon")
        }

        return parts.joined(separator: ", ")
    }
    
    private func planetSymbol(_ planet: String) -> String {
        let symbols: [String: String] = [
            "Saturn": "♄", "Jupiter": "♃", "Mars": "♂",
            "Sun": "☉", "Venus": "♀", "Mercury": "☿", "Moon": "☽"
        ]
        return symbols[planet] ?? "⊙"
    }
    
    private func timeString(_ date: Date) -> String {
        let fmt = DateFormatter()
        fmt.dateFormat = "HH:mm"
        return fmt.string(from: date)
    }
    
    private func dayString(_ date: Date) -> String {
        let fmt = DateFormatter()
        fmt.dateFormat = "EEE"
        return fmt.string(from: date)
    }
    
    // MARK: - Data Loading
    
    private func loadEvents() async {
        isLoading = true
        defer { isLoading = false }
        
        let granted = await CalendarOracle.shared.requestAccess()
        guard granted else {
            permissionDenied = true
            return
        }
        
        let lat = store.activeProfile?.latitude
        let lon = store.activeProfile?.longitude
        
        let cosmicEvents = await CalendarOracle.shared.scanUpcomingEvents(
            days: 2,
            latitude: lat,
            longitude: lon
        )
        
        // Build snapshot for each event's start time
        var snapshotMap: [Date: CalendarOracle.HorarySnapshot] = [:]
        for event in cosmicEvents {
            let snap = await CalendarOracle.shared.snapshot(
                at: event.startDate,
                latitude: lat,
                longitude: lon
            )
            snapshotMap[event.startDate] = snap
        }
        
        events = cosmicEvents.sorted { $0.startDate < $1.startDate }
        snapshots = snapshotMap
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        TemporalMatrixView()
            .environment(AppStore.shared)
    }
    .preferredColorScheme(.dark)
}
