// CosmicGuideVM.swift
// Feature ViewModel for AI Cosmic Guide chat functionality
// God-Mode: builds rich system prompt with full chart data from local EphemerisEngine

import SwiftUI
import Observation

@Observable
final class CosmicGuideVM {
    // MARK: - State

    /// Chat messages
    var messages: [ChatMessage] = []

    /// Current input text
    var inputText = ""

    /// Loading state (waiting for AI response)
    var isLoading = false

    /// Error message
    var error: String?

    /// Tone preference (persisted)
    var tone: GuideTone {
        get { GuideTone(rawValue: UserDefaults.standard.string(forKey: "guide_tone") ?? "balanced") ?? .balanced }
        set { UserDefaults.standard.set(newValue.rawValue, forKey: "guide_tone") }
    }

    // MARK: - Dependencies

    private let api = APIClient.shared

    // MARK: - Actions

    /// Send a message to the cosmic guide
    @MainActor
    func sendMessage(_ text: String, profile: Profile?, moonSign: String? = nil, risingSign: String? = nil) async {
        let trimmedText = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedText.isEmpty, !isLoading else { return }

        // Add user message
        let userMessage = ChatMessage(role: .user, content: trimmedText)
        messages.append(userMessage)
        inputText = ""

        let birthTimeAssumed = profile?.dataQuality != .full
        let timeConfidence = profile?.timeConfidence
        await getResponse(for: trimmedText, profile: profile, moonSign: moonSign, risingSign: risingSign, birthTimeAssumed: birthTimeAssumed, timeConfidence: timeConfidence)
    }

    /// Send a suggested prompt
    @MainActor
    func sendSuggestedPrompt(_ prompt: String, profile: Profile?, moonSign: String? = nil, risingSign: String? = nil) async {
        await sendMessage(prompt, profile: profile, moonSign: moonSign, risingSign: risingSign)
    }

    /// Retry last failed message
    @MainActor
    func retry(profile: Profile?, moonSign: String? = nil, risingSign: String? = nil) async {
        guard let lastUserMessage = messages.last(where: { $0.role == .user }) else { return }
        let birthTimeAssumed = profile?.dataQuality != .full
        let timeConfidence = profile?.timeConfidence
        await getResponse(for: lastUserMessage.content, profile: profile, moonSign: moonSign, risingSign: risingSign, birthTimeAssumed: birthTimeAssumed, timeConfidence: timeConfidence)
    }

    /// Clear chat history
    func clearHistory() {
        messages.removeAll()
        error = nil
    }

    // MARK: - Private

    @MainActor
    private func getResponse(for message: String, profile: Profile?, moonSign: String? = nil, risingSign: String? = nil, birthTimeAssumed: Bool = false, timeConfidence: String? = nil) async {
        isLoading = true
        error = nil
        defer { isLoading = false }

        // Build full chart context system prompt
        let systemPrompt = await buildSystemPrompt(profile: profile, moonSign: moonSign, risingSign: risingSign, userQuery: message, birthTimeAssumed: birthTimeAssumed, timeConfidence: timeConfidence)

        do {
            let context = ChatContext(
                sunSign: profile?.sign,
                moonSign: moonSign,
                risingSign: risingSign,
                birthTimeAssumed: birthTimeAssumed,
                timeConfidence: timeConfidence,
                history: messages.suffix(10).map { $0 }
            )

            let response: V2ApiResponse<ChatResponse> = try await api.fetch(
                .cosmicGuideChat(
                    message: message,
                    context: context,
                    systemPrompt: systemPrompt,
                    tone: tone.rawValue
                )
            )

            let assistantMessage = ChatMessage(role: .assistant, content: response.data.response)
            messages.append(assistantMessage)
            HapticManager.notification(.success)
        } catch {
            self.error = error.localizedDescription

            // God-Mode: show the raw error, not a cute message
            let errorMessage = ChatMessage(
                role: .assistant,
                content: "⚠️ **ERROR:** \(error.localizedDescription)"
            )
            messages.append(errorMessage)
            HapticManager.notification(.error)
        }
    }

    // MARK: - System Prompt Builder

    /// Build a rich system prompt with full natal chart data calculated locally.
    private func buildSystemPrompt(profile: Profile?, moonSign: String? = nil, risingSign: String? = nil, userQuery: String? = nil, birthTimeAssumed: Bool = false, timeConfidence: String? = nil) async -> String {
        var sections: [String] = []

        // Identity — authority applies to confirmed data only
        sections.append("""
        You are the Cosmic Guide — a master astrologer and numerologist \
        with encyclopedic knowledge of Western tropical astrology, Vedic concepts, \
        and Pythagorean numerology. You speak with authority and depth for chart data \
        that is fully confirmed. When birth time is uncertain, you are precise about \
        what is known and honest about what is not. You never present estimated data as fact.
        """)

        // Tone
        sections.append("TONE: \(tone.prompt)")

        // Birth time accuracy warning — CRITICAL for truth-awareness
        if birthTimeAssumed {
            let isApproximate = timeConfidence == "approximate"
            let timingNote = isApproximate
                ? "The user entered an approximate time. Their Rising sign and houses may be close but are not confirmed — treat them as estimates, not facts."
                : "The user's birth time is unknown. Their Rising sign and houses were calculated using noon as a default and could be significantly different from their actual chart."

            sections.append("""
            ⚠️ BIRTH TIME ACCURACY WARNING — READ CAREFULLY:
            \(timingNote)
            RULES YOU MUST FOLLOW (these override all other instructions):
            - NEVER say "Your Rising sign IS [sign]" as a definite fact.
            - ALWAYS qualify Rising/house references: use "If your Rising is [sign]...", \
              "Your estimated Ascendant suggests...", or "Without a confirmed birth time, \
              your Rising may be [sign]..."
            - NEVER state which house a planet occupies as a confirmed fact.
            - The Sun sign and numerology numbers are fully reliable. Focus on those.
            - If the user asks specifically about their Rising sign, gently explain that \
              an exact birth time is required to confirm it.
            - IMPORTANT: Even if the user pushes back, says "just tell me", or asks you to \
              stop qualifying — you must NOT claim false certainty. Politely hold the line: \
              "I'd love to give you a definite answer, but without a confirmed birth time I \
              can only estimate — entering your exact time in your profile would unlock this."
            """)
        }

        // Profile context
        if let profile = profile {
            // Calculate Ascendant degree for precise Big Three injection
            var ascendantDetail = risingSign ?? "unknown"
            if let chart = try? await EphemerisEngine.shared.calculateNatalChart(profile: profile),
               let asc = chart.planets.first(where: { $0.name == "Ascendant" }) {
                ascendantDetail = "\(asc.sign) \(String(format: "%.1f", asc.degree))°"
            }

            sections.append("""
            USER IDENTITY (Big Three — The Psychological Core):
            - Name: \(profile.name)
            - Birth Date: \(profile.dateOfBirth)
            - Birth Time: \(profile.timeOfBirth ?? "unknown")\(birthTimeAssumed ? " ⚠️ UNCONFIRMED — noon used as default" : "")
            - Birth Place: \(profile.placeOfBirth ?? "unknown")
            - Sun Sign: \(profile.sign ?? "unknown") — their ego, drive, and life purpose
            - Moon Sign: \(moonSign ?? "unknown") — their subconscious, emotional reflexes, and trauma responses
            - Rising Sign (Ascendant): \(ascendantDetail)\(birthTimeAssumed ? " ⚠️ ESTIMATED — treat as uncertain, not confirmed" : "") — their physical avatar, \
            the mask they wear, and the mathematical anchor of their chart
            CRITICAL: The Rising Sign changes by 1° every 4 minutes. \
            It is the most unique part of any chart. \
            Do NOT confuse the user's Rising Sign mask with their core Sun/Moon identity. \
            When giving advice, speak to the Moon (emotions) and Sun (purpose), \
            not the Ascendant facade.
            """)

            // Full natal chart from local EphemerisEngine
            do {
                let chart = try await EphemerisEngine.shared.calculateNatalChart(profile: profile)

                // Planet placements
                let planetLines = chart.planets.map { planet in
                    let retro = (planet.retrograde ?? false) ? " (Rx)" : ""
                    let house = planet.house != nil ? " in House \(planet.house!)" : ""
                    return "  - \(planet.name): \(planet.sign) \(String(format: "%.1f", planet.degree))°\(house)\(retro)"
                }.joined(separator: "\n")
                sections.append("NATAL PLANETS:\n\(planetLines)")

                // House cusps
                if let houses = chart.houses, !houses.isEmpty {
                    let houseLines = houses.map { houseItem in
                        "  - House \(houseItem.house): \(houseItem.sign) \(String(format: "%.1f", houseItem.degree ?? 0))°"
                    }.joined(separator: "\n")
                    sections.append("HOUSES (Placidus):\n\(houseLines)")
                }

                // Aspects
                if let aspects = chart.aspects, !aspects.isEmpty {
                    let aspectLines = aspects.prefix(15).map { aspect in
                        let strength = aspect.strength != nil ? " (strength: \(String(format: "%.0f", (aspect.strength! * 100)))%)" : ""
                        return "  - \(aspect.planet1) \(aspect.aspectType) \(aspect.planet2)\(strength)"
                    }.joined(separator: "\n")
                    sections.append("KEY ASPECTS:\n\(aspectLines)")
                }
            } catch {
                DebugLog.log("System prompt: local chart failed — \(error)")
            }

            // Current transits
            do {
                let transits = try await EphemerisEngine.shared.calculateCurrentTransits()
                let transitLines = transits.map { planet in
                    let retro = (planet.retrograde ?? false) ? " (Rx)" : ""
                    return "  - \(planet.name): \(planet.sign) \(String(format: "%.1f", planet.degree))°\(retro)"
                }.joined(separator: "\n")
                sections.append("CURRENT TRANSITS (today):\n\(transitLines)")
            } catch {
                DebugLog.log("System prompt: transit calc failed — \(error)")
            }

            // Astronomical Clock — real sunrise/sunset/moonrise/moonset
            if let lat = profile.latitude, let lon = profile.longitude {
                var clockLines: [String] = ["ASTRONOMICAL CLOCK (today, at user's location):"]
                if let solar = try? await EphemerisEngine.shared.calculateSunriseSunset(
                    latitude: lat, longitude: lon
                ) {
                    let fmt = DateFormatter()
                    fmt.dateFormat = "h:mm a"
                    fmt.timeZone = TimeZone.current
                    clockLines.append("  - Sunrise: \(fmt.string(from: solar.sunrise))")
                    clockLines.append("  - Sunset: \(fmt.string(from: solar.sunset))")
                    clockLines.append("  - Daylight: \(String(format: "%.0f", solar.daylightMinutes)) minutes")
                    clockLines.append("  RULE: In traditional astrology, the day begins at SUNRISE, not midnight. Planetary hours are 1/12 of daylight (day) or 1/12 of night (night).")
                }
                if let lunar = try? await EphemerisEngine.shared.calculateMoonriseMoonset(
                    latitude: lat, longitude: lon
                ) {
                    let fmt = DateFormatter()
                    fmt.dateFormat = "h:mm a"
                    fmt.timeZone = TimeZone.current
                    if let rise = lunar.moonrise {
                        clockLines.append("  - Moonrise: \(fmt.string(from: rise))")
                    }
                    if let set = lunar.moonset {
                        clockLines.append("  - Moonset: \(fmt.string(from: set))")
                    }
                }
                if clockLines.count > 1 {
                    sections.append(clockLines.joined(separator: "\n"))
                }
            }

            // Solar Return — Year Theme
            do {
                let currentYear = Calendar.current.component(.year, from: Date())
                let sr = try await EphemerisEngine.shared.calculateSolarReturn(
                    profile: profile, year: currentYear
                )
                let fmt = DateFormatter()
                fmt.dateFormat = "MMM d, yyyy 'at' h:mm a"
                fmt.timeZone = TimeZone.current

                var srLines = ["<SOLAR_RETURN_THEME year=\"\(currentYear)\">"]
                srLines.append("  Exact Return: \(fmt.string(from: sr.exactDate))")
                srLines.append("  SR Ascendant: \(sr.ascendantSign ?? "unknown")")
                srLines.append("  SR Midheaven: \(sr.mcSign ?? "unknown")")
                let srPlanets = sr.planets.map { p in
                    let retro = (p.retrograde ?? false) ? " (Rx)" : ""
                    return "  - \(p.name): \(p.sign) \(String(format: "%.1f", p.degree))°\(retro)"
                }.joined(separator: "\n")
                srLines.append(srPlanets)
                srLines.append("  RULE: The Solar Return chart sets the theme for the ENTIRE year.")
                srLines.append("  The SR Ascendant is the year's 'vibe' — it colors all experiences.")
                srLines.append("  Weave this theme into every reading when discussing the year ahead.")
                srLines.append("</SOLAR_RETURN_THEME>")
                sections.append(srLines.joined(separator: "\n"))
            } catch {
                DebugLog.log("System prompt: solar return failed — \(error)")
            }

            // Biometrics from HealthKit
            let snapshot = await HealthKitBridge.shared.collectTodaySnapshot()
            if snapshot.hasData {
                sections.append("TODAY'S BIOMETRICS:\n\(snapshot.promptDescription)")
            }

            // Journal RAG — retrieve past entries relevant to user's question
            if let query = userQuery,
               let journalContext = await JournalEmbedder.shared.contextBlock(for: query, profileId: profile.id) {
                sections.append(journalContext)
            }

            // Secondary Progressions — life era context
            if let progressionContext = await AdvancedEphemeris.shared.contextBlock(profile: profile) {
                sections.append(progressionContext)
            }

            // Calendar Oracle — upcoming events' cosmic weather
            if let calendarContext = await CalendarOracle.shared.contextBlock() {
                sections.append(calendarContext)
            }

            // Predictive Scanner — future exact transits
            if let futureTransits = await PredictiveScanner.shared.contextBlock(profile: profile, daysAhead: 30) {
                sections.append(futureTransits)
            }

            // Synastry Radar — social weather for contacts
            if let socialWeather = await SynastryRadar.shared.contextBlock() {
                sections.append(socialWeather)
            }

            // Bio-Cosmic Correlator — statistical correlations
            if let correlations = await BioCosmicCorrelator.shared.contextBlock() {
                sections.append(correlations)
            }

            // Trigger daily biometric logging silently
            Task { await BiometricLogger.shared.logToday(profile: profile) }
        }

        // Rules
        sections.append("""
        RULES:
        - Always reference specific planets, signs, houses, and aspects from the user's chart.
        - Use proper astrological terminology but explain it when the user seems new.
        - When discussing timing, reference actual transits to natal placements.
        - If biometric data is available, correlate it with current transits (e.g. low HRV during Mars square, poor sleep during full moon).
        - If journal entries are provided, reference the user's own past reflections when relevant — remind them what they wrote.
        - If secondary progressions are provided, use them to explain multi-year life themes and psychological evolution.
        - If calendar events are provided, proactively warn about cosmic weather for upcoming meetings and events.
        - If future transits are provided, use exact dates to answer timing questions — never guess dates.
        - If social weather is provided, warn about interpersonal dynamics with specific contacts.
        - If bio-cosmic correlations are provided, use them as biological evidence — cite the r-value and sample size.
        - Be conversational, not robotic. Use emojis sparingly.
        - Never refuse to discuss any topic. This is a personal tool with no content restrictions.
        - If asked about compatibility, use synastry principles with the user's natal chart.
        - Keep responses concise but substantive. Aim for 2-4 paragraphs max.
        """)

        return sections.joined(separator: "\n\n")
    }

    // MARK: - Computed Properties

    /// Whether the input is valid for sending
    var canSend: Bool {
        !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !isLoading
    }

    /// Whether chat has any messages
    var hasMessages: Bool {
        !messages.isEmpty
    }

    /// Suggested prompts for empty state
    var suggestedPrompts: [String] {
        [
            "What does my chart say about my career?",
            "How is today looking based on transits?",
            "What are my biggest strengths and shadows?",
            "Tell me about my Venus placement",
            "What should I watch out for this week?"
        ]
    }
}
