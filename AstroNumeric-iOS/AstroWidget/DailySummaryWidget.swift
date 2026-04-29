// DailySummaryWidget.swift
// Medium widget showing a brutalist text block: AI-generated day summary + dominant transit.

import WidgetKit
import SwiftUI

// MARK: - Timeline Entry

struct DailySummaryTimelineEntry: TimelineEntry {
    let date: Date
    let summary: String
    let moonPhase: String
    let moonSign: String
    let isPlaceholder: Bool
    let lastUpdated: Date?
}

// MARK: - Provider

struct DailySummaryProvider: TimelineProvider {
    func placeholder(in context: Context) -> DailySummaryTimelineEntry {
        DailySummaryTimelineEntry(
            date: .now,
            summary: "Mercury stations direct today. Communication clarity returns after 3 weeks of review.",
            moonPhase: "🌓", moonSign: "Scorpio", isPlaceholder: true, lastUpdated: .now
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (DailySummaryTimelineEntry) -> Void) {
        completion(currentEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<DailySummaryTimelineEntry>) -> Void) {
        let entry = currentEntry()
        // Refresh at midnight
        let tomorrow = Calendar.current.startOfDay(for: .now.addingTimeInterval(86400))
        let timeline = Timeline(entries: [entry], policy: .after(tomorrow))
        completion(timeline)
    }

    private func currentEntry() -> DailySummaryTimelineEntry {
        let defaults = AppGroupStore.sharedDefaults
        let summary = defaults?.string(forKey: "widget.daily.summary") ?? "Open app to generate today's cosmic briefing."
        let moon = defaults?.string(forKey: "widget.moon.phase") ?? "🌑"
        let sign = defaults?.string(forKey: "widget.moon.sign") ?? "—"
        let lastUpdated = defaults?.object(forKey: "widget.daily.lastUpdated") as? Date
            ?? defaults?.object(forKey: "widget.lastUpdated") as? Date

        return DailySummaryTimelineEntry(
            date: .now, summary: summary,
            moonPhase: moon, moonSign: sign, isPlaceholder: false, lastUpdated: lastUpdated
        )
    }
}

// MARK: - View

struct DailySummaryWidgetView: View {
    let entry: DailySummaryTimelineEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                Text("COSMIC BRIEFING")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundStyle(.white.opacity(0.5))
                Spacer()
                Text("\(entry.moonPhase) \(entry.moonSign)")
                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                    .foregroundStyle(.white.opacity(0.6))
            }

            // Summary
            Text(entry.summary)
                .font(.system(size: 13, weight: .regular))
                .foregroundStyle(.white.opacity(0.9))
                .lineLimit(3)
                .minimumScaleFactor(0.8)

            Spacer(minLength: 0)

            // Timestamp
            HStack {
                Text(entry.date, style: .date)
                    .font(.system(size: 9, design: .monospaced))
                    .foregroundStyle(.white.opacity(0.3))
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
            Color.black
        }
    }
}

// MARK: - Widget

struct DailySummaryWidget: Widget {
    let kind: String = "DailySummaryWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: DailySummaryProvider()) { entry in
            DailySummaryWidgetView(entry: entry)
        }
        .configurationDisplayName("Cosmic Briefing")
        .description("AI-generated daily summary with moon phase.")
        .supportedFamilies([.systemMedium])
    }
}
