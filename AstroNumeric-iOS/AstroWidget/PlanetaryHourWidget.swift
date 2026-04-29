// PlanetaryHourWidget.swift
// Lock Screen + Home Screen widget showing the current planetary hour ruler and countdown.
// Reads pre-computed schedule from App Group UserDefaults.

import WidgetKit
import SwiftUI

private struct PlanetaryHourEntry: Codable {
    let rulerName: String
    let startDate: Date
    let endDate: Date

    var emoji: String {
        switch rulerName {
        case "Sun":     return "☉"
        case "Moon":    return "☽"
        case "Mars":    return "♂"
        case "Mercury": return "☿"
        case "Jupiter": return "♃"
        case "Venus":   return "♀"
        case "Saturn":  return "♄"
        default:        return "⚫"
        }
    }
}

// MARK: - Timeline Entry

struct PlanetaryHourTimelineEntry: TimelineEntry {
    let date: Date
    let rulerName: String
    let rulerEmoji: String
    let hourEndDate: Date
    let nextHours: [(name: String, emoji: String, start: Date)]
    let isPlaceholder: Bool
}

// MARK: - Timeline Provider

struct PlanetaryHourProvider: TimelineProvider {
    func placeholder(in context: Context) -> PlanetaryHourTimelineEntry {
        PlanetaryHourTimelineEntry(
            date: .now,
            rulerName: "Mercury",
            rulerEmoji: "☿",
            hourEndDate: .now.addingTimeInterval(1800),
            nextHours: [],
            isPlaceholder: true
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (PlanetaryHourTimelineEntry) -> Void) {
        completion(currentEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<PlanetaryHourTimelineEntry>) -> Void) {
        let schedule = readSchedule()
        guard !schedule.isEmpty else {
            let entry = PlanetaryHourTimelineEntry(
                date: .now,
                rulerName: "—",
                rulerEmoji: "⚫",
                hourEndDate: .now.addingTimeInterval(3600),
                nextHours: [],
                isPlaceholder: false
            )
            let timeline = Timeline(entries: [entry], policy: .after(.now.addingTimeInterval(900)))
            completion(timeline)
            return
        }

        // Create an entry for each remaining planetary hour today
        var entries: [PlanetaryHourTimelineEntry] = []
        let now = Date()

        for (idx, hour) in schedule.enumerated() where hour.endDate > now {
            let nextHours = schedule.dropFirst(idx + 1).prefix(3).map {
                (name: $0.rulerName, emoji: $0.emoji, start: $0.startDate)
            }
            entries.append(PlanetaryHourTimelineEntry(
                date: max(hour.startDate, now),
                rulerName: hour.rulerName,
                rulerEmoji: hour.emoji,
                hourEndDate: hour.endDate,
                nextHours: nextHours,
                isPlaceholder: false
            ))
        }

        if entries.isEmpty {
            entries.append(currentEntry())
        }

        // Refresh after the last entry's end or 1h, whichever is sooner
        let refreshDate = entries.last?.hourEndDate ?? now.addingTimeInterval(3600)
        let timeline = Timeline(entries: entries, policy: .after(refreshDate))
        completion(timeline)
    }

    private func currentEntry() -> PlanetaryHourTimelineEntry {
        let schedule = readSchedule()
        let now = Date()
        if let current = schedule.first(where: { now >= $0.startDate && now < $0.endDate }) {
            let idx = schedule.firstIndex(where: { $0.startDate == current.startDate }) ?? 0
            let nextHours = schedule.dropFirst(idx + 1).prefix(3).map {
                (name: $0.rulerName, emoji: $0.emoji, start: $0.startDate)
            }
            return PlanetaryHourTimelineEntry(
                date: now,
                rulerName: current.rulerName,
                rulerEmoji: current.emoji,
                hourEndDate: current.endDate,
                nextHours: nextHours,
                isPlaceholder: false
            )
        }
        return PlanetaryHourTimelineEntry(
            date: now, rulerName: "—", rulerEmoji: "⚫",
            hourEndDate: now.addingTimeInterval(3600), nextHours: [], isPlaceholder: false
        )
    }

    private func readSchedule() -> [PlanetaryHourEntry] {
                guard let defaults = AppGroupStore.sharedDefaults,
              let data = defaults.data(forKey: "widget.planetaryHour.schedule"),
              let schedule = try? JSONDecoder().decode([PlanetaryHourEntry].self, from: data) else {
            return []
        }
        return schedule
    }
}

// MARK: - Views

struct PlanetaryHourWidgetView: View {
    @Environment(\.widgetFamily) var family
    let entry: PlanetaryHourTimelineEntry

    var body: some View {
        switch family {
        case .accessoryRectangular:
            lockScreenView
        case .systemSmall:
            smallView
        case .systemMedium:
            mediumView
        default:
            smallView
        }
    }

    // MARK: Lock Screen — Brutalist text
    private var lockScreenView: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text("\(entry.rulerEmoji) Hour of \(entry.rulerName)")
                .font(.headline)
                .minimumScaleFactor(0.7)
            Text("ends \(entry.hourEndDate, style: .relative)")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    // MARK: Small — Current hour + countdown
    private var smallView: some View {
        VStack(spacing: 6) {
            Text(entry.rulerEmoji)
                .font(.system(size: 36))
            Text(entry.rulerName)
                .font(.headline)
                .foregroundStyle(.white)
            Text(entry.hourEndDate, style: .relative)
                .font(.caption2)
                .foregroundStyle(.white.opacity(0.7))
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .containerBackground(for: .widget) {
            planetGradient(for: entry.rulerName)
        }
    }

    // MARK: Medium — Current + next 3 hours
    private var mediumView: some View {
        HStack(spacing: 0) {
            // Current hour (left side, 40% width)
            VStack(spacing: 4) {
                Text(entry.rulerEmoji)
                    .font(.system(size: 32))
                Text(entry.rulerName)
                    .font(.headline)
                    .foregroundStyle(.white)
                Text(entry.hourEndDate, style: .relative)
                    .font(.caption2)
                    .foregroundStyle(.white.opacity(0.7))
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

            // Divider
            Rectangle()
                .fill(.white.opacity(0.2))
                .frame(width: 1)
                .padding(.vertical, 8)

            // Next 3 hours (right side, 60% width)
            VStack(alignment: .leading, spacing: 6) {
                Text("UPCOMING")
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundStyle(.white.opacity(0.5))

                ForEach(Array(entry.nextHours.enumerated()), id: \.offset) { _, hour in
                    HStack(spacing: 6) {
                        Text(hour.emoji)
                            .font(.caption)
                        Text(hour.name)
                            .font(.caption2)
                            .foregroundStyle(.white.opacity(0.9))
                        Spacer()
                        Text(hour.start, style: .time)
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundStyle(.white.opacity(0.5))
                    }
                }

                if entry.nextHours.isEmpty {
                    Text("Open app to sync")
                        .font(.caption2)
                        .foregroundStyle(.white.opacity(0.5))
                }
            }
            .padding(.leading, 12)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        }
        .containerBackground(for: .widget) {
            planetGradient(for: entry.rulerName)
        }
    }

    private func planetGradient(for planet: String) -> some View {
        let colors: [Color] = {
            switch planet {
            case "Sun":     return [.orange, .red]
            case "Moon":    return [Color(white: 0.3), Color(white: 0.15)]
            case "Mars":    return [.red, Color(red: 0.5, green: 0, blue: 0)]
            case "Mercury": return [.teal, Color(red: 0, green: 0.3, blue: 0.4)]
            case "Jupiter": return [.purple, .indigo]
            case "Venus":   return [.pink, Color(red: 0.6, green: 0.2, blue: 0.4)]
            case "Saturn":  return [Color(white: 0.25), .black]
            default:        return [Color(white: 0.2), .black]
            }
        }()
        return LinearGradient(colors: colors, startPoint: .topLeading, endPoint: .bottomTrailing)
    }
}

// MARK: - Widget Definition

struct PlanetaryHourWidget: Widget {
    let kind: String = "PlanetaryHourWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: PlanetaryHourProvider()) { entry in
            PlanetaryHourWidgetView(entry: entry)
        }
        .configurationDisplayName("Planetary Hour")
        .description("Current Chaldean planetary hour ruler and countdown.")
        .supportedFamilies([.accessoryRectangular, .systemSmall, .systemMedium])
    }
}

#Preview(as: .systemSmall) {
    PlanetaryHourWidget()
} timeline: {
    PlanetaryHourTimelineEntry(
        date: .now,
        rulerName: "Mercury",
        rulerEmoji: "☿",
        hourEndDate: .now.addingTimeInterval(1800),
        nextHours: [
            (name: "Moon", emoji: "☽", start: .now.addingTimeInterval(1800)),
            (name: "Saturn", emoji: "♄", start: .now.addingTimeInterval(3600)),
            (name: "Jupiter", emoji: "♃", start: .now.addingTimeInterval(5400))
        ],
        isPlaceholder: false
    )
}
