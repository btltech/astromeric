// MorningBriefWidget.swift
// Compact widget showing today's morning brief — 3 quick cosmic bullets

import WidgetKit
import SwiftUI

// MARK: - Timeline Entry

struct MorningBriefTimelineEntry: TimelineEntry {
    let date: Date
    let bullets: [String]
    let personalDay: Int
    let moonEmoji: String
    let lastUpdated: Date?
}

// MARK: - Provider

struct MorningBriefProvider: TimelineProvider {

    func placeholder(in context: Context) -> MorningBriefTimelineEntry {
        MorningBriefTimelineEntry(
            date: .now,
            bullets: [
                "Moon in Scorpio — go deep today",
                "Personal Day 7 — reflection & insight",
                "Vibe: introspective and focused"
            ],
            personalDay: 7,
            moonEmoji: "🌒",
            lastUpdated: .now
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (MorningBriefTimelineEntry) -> Void) {
        completion(currentEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<MorningBriefTimelineEntry>) -> Void) {
        let entry = currentEntry()
        // Refresh daily at 5 AM
        var components = Calendar.current.dateComponents([.year, .month, .day], from: .now)
        components.hour = 5
        components.minute = 0
        let nextRefresh = Calendar.current.date(from: components)?.addingTimeInterval(86400) ?? .now.addingTimeInterval(86400)
        let timeline = Timeline(entries: [entry], policy: .after(nextRefresh))
        completion(timeline)
    }

    private func currentEntry() -> MorningBriefTimelineEntry {
        let defaults = AppGroupStore.sharedDefaults

        // Read bullets stored as JSON array string
        let bulletsJSON = defaults?.string(forKey: "widget.brief.bullets") ?? "[]"
        let bullets: [String]
        if let data = bulletsJSON.data(using: .utf8),
           let decoded = try? JSONDecoder().decode([String].self, from: data) {
            bullets = decoded
        } else {
            bullets = ["Open app to generate today's morning brief."]
        }

        let personalDay = defaults?.integer(forKey: "widget.brief.personalDay") ?? 0
        let moon = defaults?.string(forKey: "widget.moon.phase") ?? "🌑"
        let lastUpdated = defaults?.object(forKey: "widget.brief.lastUpdated") as? Date
            ?? defaults?.object(forKey: "widget.lastUpdated") as? Date

        return MorningBriefTimelineEntry(
            date: .now,
            bullets: bullets,
            personalDay: personalDay,
            moonEmoji: moon,
            lastUpdated: lastUpdated
        )
    }
}

// MARK: - Small Widget View

struct MorningBriefSmallView: View {
    let entry: MorningBriefTimelineEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 4) {
                Text(entry.moonEmoji)
                    .font(.system(size: 12))
                Text("BRIEF")
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundStyle(.white.opacity(0.5))
                Spacer()
                if entry.personalDay > 0 {
                    Text("Day \(entry.personalDay)")
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                        .foregroundStyle(.purple.opacity(0.9))
                }
            }

            Spacer(minLength: 2)

            ForEach(Array(entry.bullets.prefix(2).enumerated()), id: \.offset) { _, bullet in
                Text("• \(bullet)")
                    .font(.system(size: 11))
                    .foregroundStyle(.white.opacity(0.85))
                    .lineLimit(2)
                    .minimumScaleFactor(0.75)
            }

            Spacer(minLength: 0)

            HStack {
                Spacer()
                if let lastUpdated = entry.lastUpdated {
                    Text("↻ \(lastUpdated, style: .time)")
                        .font(.system(size: 8, weight: .medium, design: .monospaced))
                        .foregroundStyle(.white.opacity(0.35))
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .padding(10)
        .containerBackground(for: .widget) {
            LinearGradient(
                colors: [Color(hue: 0.75, saturation: 0.6, brightness: 0.2), Color.black],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
    }
}

// MARK: - Medium Widget View

struct MorningBriefMediumView: View {
    let entry: MorningBriefTimelineEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                HStack(spacing: 4) {
                    Text(entry.moonEmoji)
                    Text("MORNING BRIEF")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundStyle(.white.opacity(0.5))
                }
                Spacer()
                if entry.personalDay > 0 {
                    Text("Personal Day \(entry.personalDay)")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundStyle(.purple.opacity(0.9))
                }
            }

            // Bullets
            VStack(alignment: .leading, spacing: 5) {
                ForEach(Array(entry.bullets.prefix(3).enumerated()), id: \.offset) { _, bullet in
                    HStack(alignment: .top, spacing: 5) {
                        Text("•")
                            .font(.system(size: 12, weight: .bold))
                            .foregroundStyle(.purple.opacity(0.8))
                        Text(bullet)
                            .font(.system(size: 12))
                            .foregroundStyle(.white.opacity(0.9))
                            .lineLimit(1)
                            .minimumScaleFactor(0.8)
                    }
                }
            }

            Spacer(minLength: 0)

            HStack {
                Text(entry.date, style: .date)
                    .font(.system(size: 9, design: .monospaced))
                    .foregroundStyle(.white.opacity(0.25))
                Spacer()
                if let lastUpdated = entry.lastUpdated {
                    Text("Updated \(lastUpdated, style: .time)")
                        .font(.system(size: 9, design: .monospaced))
                        .foregroundStyle(.white.opacity(0.35))
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .containerBackground(for: .widget) {
            LinearGradient(
                colors: [Color(hue: 0.75, saturation: 0.6, brightness: 0.2), Color.black],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
    }
}

// MARK: - Widget

struct MorningBriefWidget: Widget {
    let kind: String = "MorningBriefWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: MorningBriefProvider()) { entry in
            if #available(iOSApplicationExtension 16.0, *) {
                switch entry.bullets.count {
                case 0, 1:
                    MorningBriefSmallView(entry: entry)
                default:
                    MorningBriefMediumView(entry: entry)
                }
            } else {
                MorningBriefMediumView(entry: entry)
            }
        }
        .configurationDisplayName("Morning Brief")
        .description("3 quick cosmic insights for your day — moon, energy, and vibe.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
