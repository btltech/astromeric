// ReadingResultView.swift
// Display reading results with sections

import SwiftUI

struct ReadingResultView: View {
    let scope: ReadingScope
    let data: PredictionData
    let onRefresh: (() async -> Void)?
    
    @State private var showShareSheet = false
    @State private var showExplanation = false
    @State private var selectedSection: ForecastSection?
    @State private var aiExplanation: String?
    @State private var aiExplanationSource: AIInsightSource = .fallback
    @State private var aiGeneratedAt: Date = Date()
    @State private var isExplaining = false
    @State private var isRevealing = true

    private let api = APIClient.shared
    
    init(scope: ReadingScope = .daily, data: PredictionData, onRefresh: (() async -> Void)? = nil) {
        self.scope = scope
        self.data = data
        self.onRefresh = onRefresh
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Header
                VStack(spacing: 12) {
                    Text(String(format: "fmt.readingResult.1".localized, "\(data.scope.capitalized)"))
                        .font(.title.bold())
                    
                    Text(data.date)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }
                .padding(.top)
                
                // Overall Score
                CardView {
                    VStack(spacing: 8) {
                        Text("ui.readingResult.0".localized)
                            .font(.headline)
                        Text(String(format: "%.1f", data.overallScore))
                            .font(.system(.largeTitle)).fontWeight(.bold)
                            .foregroundStyle(.purple)
                        Text("ui.readingResult.1".localized)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                }

                CardView {
                    VStack(alignment: .leading, spacing: 14) {
                        Text("ui.readingResult.2".localized)
                            .font(.headline)

                        Text(todayMeaningSummary)
                            .font(.subheadline)
                            .foregroundStyle(.primary)

                        HStack(alignment: .top, spacing: 12) {
                            insightPill(title: "Lean Into", body: todayBestMove, color: .green)
                            insightPill(title: "Watch For", body: todayWatchFor, color: .orange)
                        }
                    }
                }

                if !readingDrivers.isEmpty {
                    CardView {
                        VStack(alignment: .leading, spacing: 14) {
                            HStack {
                                Text("ui.readingResult.3".localized)
                                    .font(.headline)
                                Spacer()
                                FeatureProvenanceBadge(provenance: .calculated, compact: true)
                            }

                            Text("ui.readingResult.4".localized)
                                .font(.subheadline)
                                .foregroundStyle(Color.textSecondary)

                            VStack(spacing: 10) {
                                ForEach(readingDrivers) { driver in
                                    readingDriverRow(driver)
                                }
                            }
                        }
                    }
                }

                // Monthly-only: Horoscope Summary + Lucky Numbers
                if scope == .monthly {
                    if let sign = derivedZodiacSign {
                        monthlyHoroscopeSummaryCard(sign: sign)
                            .staggeredReveal(index: 0, isRevealing: isRevealing, baseDelay: 0.05, staggerDelay: 0.08)
                    }

                    monthlyLuckyNumbersCard
                        .staggeredReveal(index: 1, isRevealing: isRevealing, baseDelay: 0.1, staggerDelay: 0.08)
                }
                
                // AI Explain Button (for full reading)
                Button {
                    Task { await generateFullExplanation(forceRefresh: false) }
                } label: {
                    HStack(spacing: 8) {
                        if isExplaining {
                            ProgressView()
                                .scaleEffect(0.8)
                        } else {
                            Image(systemName: "sparkles")
                        }
                        Text(isExplaining ? "tern.readingResult.0a".localized : "tern.readingResult.0b".localized)
                            .font(.subheadline.weight(.medium))
                    }
                    .foregroundStyle(.purple)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(Color.purple.opacity(0.15))
                    .clipShape(Capsule())
                }
                .disabled(isExplaining)
                
                // Sections with staggered reveal
                ForEach(Array(data.sections.enumerated()), id: \.element.id) { index, section in
                    CardView {
                        VStack(alignment: .leading, spacing: 12) {
                            Text(section.title)
                                .font(.headline)
                            
                            Text(section.summary)
                                .font(.subheadline)
                                .foregroundStyle(Color.textSecondary)

                            if !topTopics(for: section).isEmpty {
                                VStack(alignment: .leading, spacing: 6) {
                                    Text("ui.readingResult.5".localized)
                                        .font(.caption.weight(.medium))
                                        .foregroundStyle(.purple)

                                    ForEach(topTopics(for: section), id: \.key) { topic in
                                        HStack {
                                            Text(displayTopicName(topic.key))
                                                .font(.caption)
                                            Spacer()
                                            Text(topicWeightLabel(topic.value))
                                                .font(.caption.weight(.medium))
                                                .foregroundStyle(Color.textSecondary)
                                        }
                                    }
                                }
                            }
                            
                            if !section.embrace.isEmpty {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("ui.readingResult.6".localized)
                                        .font(.caption.weight(.medium))
                                        .foregroundStyle(.green)
                                    ForEach(section.embrace, id: \.self) { item in
                                        Text("• \(item)")
                                            .font(.caption)
                                    }
                                }
                            }
                            
                            if !section.avoid.isEmpty {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("ui.readingResult.7".localized)
                                        .font(.caption.weight(.medium))
                                        .foregroundStyle(.orange)
                                    ForEach(section.avoid, id: \.self) { item in
                                        Text("• \(item)")
                                            .font(.caption)
                                    }
                                }
                            }
                        }
                    }
                    .staggeredReveal(index: index, isRevealing: isRevealing, baseDelay: 0.1, staggerDelay: 0.08)
                }
                
                // Share Button
                SecondaryButton("action.share".localized, icon: "square.and.arrow.up") {
                    showShareSheet = true
                }
                .padding(.top)
                .slideUpReveal(isRevealing: isRevealing, offset: 20, delay: 0.3)
            }
            .padding()
            .readableContainer()
        }
        .onAppear {
            // Trigger reveal animation
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
                isRevealing = false
                HapticManager.notification(.success)
            }
        }
        .sheet(isPresented: $showShareSheet) {
            if let image = ShareCardGenerator.generateImage(for: data) {
                ShareSheet(items: [image, generateShareText()])
            } else {
                ShareSheet(items: [generateShareText()])
            }
        }
        .sheet(isPresented: $showExplanation) {
            if let explanation = aiExplanation {
                AIInsightsSheetView(
                    markdown: explanation,
                    source: aiExplanationSource,
                    generatedAt: aiGeneratedAt,
                    onRegenerate: {
                        Task { await generateFullExplanation(forceRefresh: true) }
                    }
                )
            }
        }
        .refreshable {
            if let onRefresh {
                await onRefresh()
            }
        }
    }

    private func insightPill(title: String, body: String, color: Color) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(color)
            Text(body)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(color.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 14))
    }

    // MARK: - Monthly Zodiac Helpers

    private var derivedZodiacSign: ZodiacSign? {
        guard let dob = data.profile?.dateOfBirth else { return nil }
        return ZodiacSign.from(dateOfBirth: dob)
    }

    private var readingDrivers: [ReadingDriver] {
        var drivers: [ReadingDriver] = []

        if let sign = derivedZodiacSign {
            drivers.append(
                ReadingDriver(
                    title: "Birth Signature",
                    detail: "\(sign.emoji) \(sign.displayName) sun with \(sign.element.lowercased()) \(sign.modality.lowercased()) emphasis."
                )
            )
        }

        if let personalDay = personalDayNumber {
            drivers.append(
                ReadingDriver(
                    title: "Personal Day",
                    detail: "\(personalDay) - \(personalDayDescription(for: personalDay))"
                )
            )
        }

        let themes = strongestThemes(limit: 2)
        if !themes.isEmpty {
            drivers.append(
                ReadingDriver(
                    title: "Top Forecast Themes",
                    detail: themes.joined(separator: " + ")
                )
            )
        }

        drivers.append(
            ReadingDriver(
                title: "Delivery Style",
                detail: "\(AppStore.shared.readingTone.label) - \(AppStore.shared.readingTone.framingDescription)"
            )
        )

        return drivers
    }

    private var personalDayNumber: Int? {
        guard let profile = data.profile,
              let readingDate = parsedReadingDate,
              let birthMonthDay = birthMonthDay(from: profile.dateOfBirth)
        else { return nil }

        let tz = TimeZone(identifier: profile.timezone ?? "") ?? TimeZone(identifier: "UTC")!
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = tz

        let components = calendar.dateComponents([.year, .month, .day], from: readingDate)
        guard let year = components.year,
              let month = components.month,
              let day = components.day
        else { return nil }

        let personalYear = reduceNumber(birthMonthDay.month + birthMonthDay.day + year)
        let personalMonth = reduceNumber(personalYear + month)
        return reduceNumber(personalMonth + day)
    }

    private var todayMeaningSummary: String {
        if let firstSection = data.sections.first {
            return firstSection.summary
        }

        return "Today is less about doing everything and more about acting on the strongest signal in your chart."
    }

    private var todayBestMove: String {
        data.sections.lazy.flatMap(\ .embrace).first ?? "Choose one meaningful action and follow through on it before the day gets noisy."
    }

    private var todayWatchFor: String {
        data.sections.lazy.flatMap(\ .avoid).first ?? "Overcommitting or splitting your attention across too many priorities."
    }

    private var parsedReadingDate: Date? {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: data.date)
    }

    private func monthlyHoroscopeSummaryCard(sign: ZodiacSign) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 14) {
                // Header
                HStack(spacing: 10) {
                    ZStack {
                        Circle()
                            .fill(Color.purple.opacity(0.18))
                            .frame(width: 48, height: 48)
                        Text(sign.emoji)
                            .font(.system(.title2))
                    }

                    VStack(alignment: .leading, spacing: 2) {
                        Text(String(format: "fmt.readingResult.0".localized, "\(sign.displayName)"))
                            .font(.headline)
                        Text(sign.element)
                            .font(.caption)
                            .foregroundStyle(Color.textSecondary)
                    }
                    Spacer()
                }

                Divider()
                    .background(Color.borderSubtle)

                // Narrative built from reading sections
                VStack(alignment: .leading, spacing: 8) {
                    Text(monthlyNarrative(sign: sign))
                        .font(.subheadline)
                        .foregroundStyle(.primary)
                        .lineSpacing(5)
                }

                // Key themes pills
                if !data.sections.isEmpty {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            ForEach(data.sections.prefix(4), id: \.id) { section in
                                Text(section.title)
                                    .font(.caption.weight(.medium))
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color.purple.opacity(0.15))
                                    .foregroundStyle(.purple)
                                    .clipShape(Capsule())
                            }
                        }
                    }
                }
            }
        }
    }

    private func monthlyNarrative(sign: ZodiacSign) -> String {
        let cal = Calendar.current
        let monthName = DateFormatter().monthSymbols[cal.component(.month, from: Date()) - 1]
        let year = cal.component(.year, from: Date())

        let topSection = data.sections.first?.summary ?? "a period of reflection and growth"
        let secondSection = data.sections.dropFirst().first?.summary ?? ""

        var narrative = "For \(monthName) \(year), \(sign.displayName) enters a \(sign.modality.lowercased()) phase shaped by \(sign.element.components(separatedBy: " ").first?.lowercased() ?? "cosmic") energy. "
        narrative += topSection
        if !secondSection.isEmpty {
            narrative += " " + secondSection
        }
        narrative += " This is a time to honour your natural gifts while staying open to what the cosmos is activating."
        return narrative
    }

    private func readingDriverRow(_ driver: ReadingDriver) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(driver.title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(Color.textSecondary)

            Text(driver.detail)
                .font(.subheadline.weight(.medium))
                .foregroundStyle(.primary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.surfaceElevated)
        )
    }

    private func topTopics(for section: ForecastSection, limit: Int = 3) -> [(key: String, value: Float)] {
        section.topics
            .sorted { $0.value > $1.value }
            .prefix(limit)
            .map { ($0.key, $0.value) }
    }

    private func strongestThemes(limit: Int) -> [String] {
        let themeTotals = data.sections.reduce(into: [String: Float]()) { partialResult, section in
            for (topic, weight) in section.topics {
                partialResult[topic, default: 0] += weight
            }
        }

        return themeTotals
            .sorted { $0.value > $1.value }
            .prefix(limit)
            .map { displayTopicName($0.key) }
    }

    private func displayTopicName(_ key: String) -> String {
        key
            .replacingOccurrences(of: "_", with: " ")
            .localizedCapitalized
    }

    private func topicWeightLabel(_ weight: Float) -> String {
        let percent = weight <= 1 ? weight * 100 : weight
        let clamped = max(0, min(percent, 100))
        return "\(Int(clamped.rounded()))%"
    }

    private func birthMonthDay(from dateOfBirth: String) -> (month: Int, day: Int)? {
        let parts = dateOfBirth.split(separator: "-")
        guard parts.count == 3,
              let month = Int(parts[1]),
              let day = Int(parts[2]) else {
            return nil
        }

        return (month, day)
    }

    private func reduceNumber(_ number: Int) -> Int {
        var value = number
        while value > 9 {
            var sum = 0
            var remainder = value
            while remainder > 0 {
                sum += remainder % 10
                remainder /= 10
            }
            value = sum
        }
        return value
    }

    private func personalDayDescription(for number: Int) -> String {
        switch number {
        case 1: return "New starts and independent moves."
        case 2: return "Partnership, patience, and emotional reading."
        case 3: return "Expression, visibility, and creative flow."
        case 4: return "Structure, systems, and practical follow-through."
        case 5: return "Movement, experimentation, and change."
        case 6: return "Care, duty, and relationship maintenance."
        case 7: return "Reflection, analysis, and inner work."
        case 8: return "Power, execution, and material traction."
        case 9: return "Completion, release, and bigger-picture thinking."
        default: return "Numerology context is still loading."
        }
    }

    private var monthlyLuckyNumbersCard: some View {
        let cal = Calendar.current
        let month = cal.component(.month, from: Date())
        let year = cal.component(.year, from: Date())
        let dob = data.profile?.dateOfBirth ?? ""
        let numbers = dob.isEmpty
            ? [3, 6, 9, 12, 21]
            : ZodiacSign.monthlyLuckyNumbers(dateOfBirth: dob, month: month, year: year)

        return CardView {
            VStack(spacing: 12) {
                HStack {
                    Text("🍀")
                        .font(.title)
                    Text("ui.readingResult.8".localized)
                        .font(.headline)
                    Spacer()
                }

                HStack(spacing: 10) {
                    ForEach(numbers.prefix(5), id: \.self) { number in
                        ZStack {
                            Circle()
                                .fill(
                                    LinearGradient(
                                        colors: [Color.green.opacity(0.3), Color.teal.opacity(0.2)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(width: 52, height: 52)
                            Text("\(number)")
                                .font(.title3.bold())
                                .foregroundStyle(.green)
                        }
                    }
                }

                Text("ui.readingResult.9".localized)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)
            }
        }
    }
    
    // MARK: - AI Explanation Generator
    
    @MainActor
    private func generateFullExplanation(forceRefresh: Bool) async {
        isExplaining = true
        defer { isExplaining = false }
        
        // Simulate brief delay for UX
        try? await Task.sleep(nanoseconds: 300_000_000)
        
        // 1) Try real backend AI explain (if available / user is authed)
        let request = AIExplainRequest(
            scope: data.scope,
            headline: "Overall Energy: \(String(format: "%.1f", data.overallScore))/10",
            theme: nil,
            sections: data.sections.map { section in
                var highlights: [String] = [section.summary]
                if let first = section.embrace.first, !first.isEmpty { highlights.append("Do: \(first)") }
                if let first = section.avoid.first, !first.isEmpty { highlights.append("Avoid: \(first)") }
                return SectionSummary(title: section.title, highlights: highlights)
            },
            numerologySummary: nil
        )

        do {
            let response: V2ApiResponse<AIExplainResponse> = try await api.fetch(
                .aiExplain(reading: request),
                cachePolicy: forceRefresh ? .networkOnly : .cacheFirst
            )
            aiExplanation = response.data.summary
            aiExplanationSource = AIInsightSource(provider: response.data.provider)
            aiGeneratedAt = Date()
        } catch {
            // 2) Fallback: local structured explanation
            let score = String(format: "%.1f", data.overallScore)
            let strongestSections = data.sections.prefix(3)

            var explanation = "## TL;DR\n\n"
            explanation += "Your overall energy today is **\(score)/10**. Pick **one main focus**, keep it simple, and follow through.\n\n"
            explanation += "---\n\n"
            explanation += "## Key takeaways\n"
            explanation += "- Date: **\(data.date)**\n"
            explanation += "- Overall energy: **\(score)/10**\n\n"
            explanation += "---\n\n"
            explanation += "## What this means\n\n"
            for section in strongestSections {
                explanation += "### \(section.title)\n"
                explanation += "\(section.summary)\n\n"

                if let embrace = section.embrace.first, !embrace.isEmpty {
                    explanation += "- ✅ Do: **\(embrace)**\n"
                }
                if let avoid = section.avoid.first, !avoid.isEmpty {
                    explanation += "- ⚠️ Avoid: **\(avoid)**\n"
                }
                explanation += "\n"
            }
            explanation += "---\n\n"
            explanation += "## Practical tip (10 minutes)\n\n"
            explanation += "Choose one section above and take a *small* action today. If you’re unsure, do a 10‑minute reset: water + a short walk + write one priority."
            aiExplanation = explanation
            aiExplanationSource = .fallback
            aiGeneratedAt = Date()
        }

        HapticManager.notification(.success)
        showExplanation = true
    }
    
    private func generateShareText() -> String {
        var text = "✨ My \(data.scope.capitalized) Reading\n\n"
        text += "Overall Score: \(String(format: "%.1f", data.overallScore))/10\n"
        text += "\n— Generated by AstroNumeric"
        return text
    }
}

private struct ReadingDriver: Identifiable {
    let id = UUID()
    let title: String
    let detail: String
}

// MARK: - Share Sheet

struct ShareSheet: UIViewControllerRepresentable {
    let items: [Any]
    
    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items, applicationActivities: nil)
    }
    
    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

// MARK: - AI Insights Sheet (inline to ensure SwiftPM/Xcode picks it up)

enum AIInsightSource: String {
    case ai = "AI"
    case structured = "Structured"
    case fallback = "Offline"

    init(provider: String?) {
        switch provider {
        case "gemini-flash", "gemini":
            self = .ai
        case "deterministic", "fallback":
            self = .structured
        default:
            self = .fallback
        }
    }
}

struct AIInsightsSheetView: View {
    let markdown: String
    let source: AIInsightSource
    let generatedAt: Date
    let onRegenerate: () -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var showShareSheet = false
    @State private var shareItems: [Any] = []
    @State private var expandAll = false

    private var parsed: ParsedMarkdownDoc {
        ParsedMarkdownDoc(markdown)
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    headerRow

                    if let tldr = parsed.tldr, !tldr.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        tldrBox(tldr)
                    }

                    ForEach(parsed.sections) { section in
                        CardView {
                            DisclosureGroup(isExpanded: bindingForSection(section)) {
                                markdownBlock(section.body)
                                    .padding(.top, 6)
                            } label: {
                                Text(section.title)
                                    .font(.headline)
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("screen.aiInsights".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("action.done".localized) { dismiss() }
                }

                ToolbarItemGroup(placement: .topBarTrailing) {
                    Button {
                        expandAll.toggle()
                    } label: {
                        Image(systemName: expandAll ? "tern.readingResult.1a".localized : "tern.readingResult.1b".localized)
                            .frame(width: 44, height: 44)
                            .contentShape(Rectangle())
                    }
                    .accessibilityLabel(expandAll ? "tern.readingResult.2a".localized : "tern.readingResult.2b".localized)

                    Button {
                        copyToClipboard(parsed.copyText)
                        HapticManager.notification(.success)
                    } label: {
                        Image(systemName: "doc.on.doc")
                            .frame(width: 44, height: 44)
                            .contentShape(Rectangle())
                    }
                    .accessibilityLabel("Copy")

                    Button {
                        shareItems = [parsed.copyText]
                        showShareSheet = true
                    } label: {
                        Image(systemName: "square.and.arrow.up")
                            .frame(width: 44, height: 44)
                            .contentShape(Rectangle())
                    }
                    .accessibilityLabel("Share")

                    Button {
                        onRegenerate()
                    } label: {
                        Image(systemName: "arrow.clockwise")
                            .frame(width: 44, height: 44)
                            .contentShape(Rectangle())
                    }
                    .accessibilityLabel("Regenerate")
                }
            }
            .sheet(isPresented: $showShareSheet) {
                ShareSheet(items: shareItems)
            }
        }
        .presentationDetents([.medium, .large])
    }

    private var headerRow: some View {
        HStack(spacing: 10) {
            Text(source.rawValue)
                .font(.caption.weight(.semibold))
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(
                    Capsule().fill(source == .ai ? Color.purple.opacity(0.18) : Color.borderSubtle)
                )
                .foregroundStyle(source == .ai ? .purple : Color.textSecondary)

            Text(relativeTime(generatedAt))
                .font(.caption)
                .foregroundStyle(Color.textSecondary)

            Spacer()

            PremiumSectionHeader(
                title: "section.readingResult.0.title".localized,
                subtitle: "section.readingResult.0.subtitle".localized
            )
        }
    }

    private func tldrBox(_ text: String) -> some View {
        VStack(spacing: 8) {
            Text("ui.readingResult.10".localized)
                .font(.caption.weight(.bold))
                .foregroundStyle(.purple)

            Text(text)
                .font(.subheadline)
                .multilineTextAlignment(.center)
                .foregroundStyle(.primary)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(
                    LinearGradient(
                        colors: [
                            Color.purple.opacity(0.2),
                            Color.purple.opacity(0.1),
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .strokeBorder(Color.purple.opacity(0.3), lineWidth: 1)
        )
        .overlay(alignment: .topLeading) {
            Text("ui.readingResult.11".localized)
                .font(.system(.caption2, design: .monospaced)).fontWeight(.bold)
                .foregroundStyle(.purple.opacity(0.7))
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
        }
    }

    private func markdownBlock(_ text: String) -> some View {
        Group {
            if let attributed = try? AttributedString(markdown: text) {
                Text(attributed)
            } else {
                Text(text)
            }
        }
        .font(.callout)
        .lineSpacing(6)
        .textSelection(.enabled)
    }

    private func bindingForSection(_ section: ParsedMarkdownSection) -> Binding<Bool> {
        Binding(
            get: { expandAll || section.isExpandedByDefault },
            set: { _ in }
        )
    }

    private func copyToClipboard(_ text: String) {
        UIPasteboard.general.string = text
    }

    private func relativeTime(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .short
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

// MARK: - Markdown parsing (lightweight)

struct ParsedMarkdownSection: Identifiable {
    let id = UUID()
    let title: String
    let body: String
    let isExpandedByDefault: Bool
}

struct ParsedMarkdownDoc {
    let tldr: String?
    let sections: [ParsedMarkdownSection]
    let copyText: String

    init(_ markdown: String) {
        self.copyText = markdown

        let normalized = markdown.replacingOccurrences(of: "\r\n", with: "\n")
        let parts = normalized.components(separatedBy: "\n## ")

        var sections: [ParsedMarkdownSection] = []
        var foundTLDR: String? = nil

        for (idx, raw) in parts.enumerated() {
            let chunk = idx == 0 ? raw : "## " + raw
            guard let headingRange = chunk.range(of: "## ") else {
                continue
            }

            let afterHeading = chunk[headingRange.upperBound...]
            let lines = afterHeading.components(separatedBy: "\n")
            let title = lines.first?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            let body = lines.dropFirst().joined(separator: "\n").trimmingCharacters(in: .whitespacesAndNewlines)

            if title.lowercased().hasPrefix("tl;dr") {
                foundTLDR = body
                continue
            }

            if !title.isEmpty {
                sections.append(
                    ParsedMarkdownSection(
                        title: title,
                        body: body,
                        isExpandedByDefault: title.lowercased().contains("practical") || title.lowercased().contains("tip") || title.lowercased().contains("key") || title.lowercased().contains("means")
                    )
                )
            }
        }

        if sections.isEmpty {
            sections = [
                ParsedMarkdownSection(title: "Full explanation", body: markdown, isExpandedByDefault: true)
            ]
        }

        self.tldr = foundTLDR
        self.sections = sections
    }
}

// MARK: - Preview

#Preview {
    ScrollView {
        ReadingResultView(
            scope: .daily,
            data: PredictionData(
                profile: nil,
                scope: "daily",
                date: "2024-01-15",
                sections: [
                    ForecastSection(title: "Love", summary: "Good day for connections", topics: ["love": 8.5], avoid: [], embrace: ["Open communication"]),
                    ForecastSection(title: "Career", summary: "Focus on planning", topics: ["career": 7.2], avoid: ["Hasty decisions"], embrace: [])
                ],
                overallScore: 7.8,
                generatedAt: "2024-01-15T10:00:00Z"
            )
        )
    }
    .background(Color.black)
    .preferredColorScheme(.dark)
}
