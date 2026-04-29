// MoonPhaseWidget.swift
// Lock Screen + Small widget showing moon phase, sign, and illumination.

import WidgetKit
import SwiftUI

// MARK: - Timeline Entry

struct MoonPhaseTimelineEntry: TimelineEntry {
    let date: Date
    let phaseEmoji: String
    let moonSign: String
    let illumination: Double
    let isPlaceholder: Bool
}

// MARK: - Provider

struct MoonPhaseProvider: TimelineProvider {
    func placeholder(in context: Context) -> MoonPhaseTimelineEntry {
        MoonPhaseTimelineEntry(
            date: .now, phaseEmoji: "🌓", moonSign: "Scorpio",
            illumination: 50, isPlaceholder: true
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (MoonPhaseTimelineEntry) -> Void) {
        completion(currentEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<MoonPhaseTimelineEntry>) -> Void) {
        let entry = currentEntry()
        // Moon sign changes ~every 2.5 days; refresh every 2 hours
        let refreshDate = Calendar.current.date(byAdding: .hour, value: 2, to: .now)!
        let timeline = Timeline(entries: [entry], policy: .after(refreshDate))
        completion(timeline)
    }

    private func currentEntry() -> MoonPhaseTimelineEntry {
        let defaults = AppGroupStore.sharedDefaults
        let emoji = defaults?.string(forKey: "widget.moon.phase") ?? "🌑"
        let sign = defaults?.string(forKey: "widget.moon.sign") ?? "—"
        let illum = defaults?.double(forKey: "widget.moon.illumination") ?? 0

        return MoonPhaseTimelineEntry(
            date: .now, phaseEmoji: emoji, moonSign: sign,
            illumination: illum, isPlaceholder: false
        )
    }
}

// MARK: - Views

struct MoonPhaseWidgetView: View {
    @Environment(\.widgetFamily) var family
    let entry: MoonPhaseTimelineEntry

    var body: some View {
        switch family {
        case .accessoryCircular:
            circularView
        case .accessoryRectangular:
            rectangularView
        case .systemSmall:
            smallView
        default:
            smallView
        }
    }

    // Lock Screen circular — just the moon emoji
    private var circularView: some View {
        VStack(spacing: 1) {
            Text(entry.phaseEmoji)
                .font(.title2)
            Text("\(Int(entry.illumination))%")
                .font(.system(size: 10, weight: .medium, design: .monospaced))
        }
    }

    // Lock Screen rectangular
    private var rectangularView: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack(spacing: 4) {
                Text(entry.phaseEmoji)
                Text("Moon in \(entry.moonSign)")
                    .font(.headline)
            }
            Text("\(Int(entry.illumination))% illumination")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    // Home Screen small
    private var smallView: some View {
        VStack(spacing: 8) {
            Text(entry.phaseEmoji)
                .font(.system(size: 48))

            Text(entry.moonSign)
                .font(.headline)
                .foregroundStyle(.white)

            Text("\(Int(entry.illumination))%")
                .font(.system(size: 14, weight: .bold, design: .monospaced))
                .foregroundStyle(.white.opacity(0.6))
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .containerBackground(for: .widget) {
            LinearGradient(
                colors: [Color(white: 0.12), Color(white: 0.05)],
                startPoint: .top, endPoint: .bottom
            )
        }
    }
}

// MARK: - Widget

struct MoonPhaseWidget: Widget {
    let kind: String = "MoonPhaseWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: MoonPhaseProvider()) { entry in
            MoonPhaseWidgetView(entry: entry)
        }
        .configurationDisplayName("Moon Phase")
        .description("Current moon phase, sign, and illumination.")
        .supportedFamilies([.accessoryCircular, .accessoryRectangular, .systemSmall])
    }
}
