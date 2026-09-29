// OracleView.swift
// Horary Oracle — Yes/No answers grounded in real-time planetary math.
// With the owner's AI access code it routes through the Cosmic Guide chat
// pipeline with EphemerisEngine telemetry; otherwise it answers on-device
// from the Horary rules alone and the question never leaves the phone.

import CoreLocation
import SwiftUI
import UIKit

struct OracleView: View {
    @Environment(AppStore.self) private var store
    @State private var question = ""
    @State private var answer: YesNoAnswer?
    @State private var telemetry: String?
    @State private var isLoading = false
    @State private var pendulumAngle: Double = 0
    @State private var errorMessage: String?
    @FocusState private var questionFocused: Bool
    
    private let cosmicGuide: CosmicGuideRepository = DefaultCosmicGuideRepository()
    
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
            
            ScrollViewReader { proxy in
            ScrollView {
                VStack(spacing: 24) {
                    PremiumScreenHeader(
                        eyebrow: "hero.oracle.eyebrow".localized,
                        title: "hero.oracle.title".localized,
                        subtitle: "hero.oracle.body".localized,
                        accent: .accentPrimary,
                        chips: ["hero.oracle.chip.0".localized, "hero.oracle.chip.1".localized, "hero.oracle.chip.2".localized]
                    )

                    PremiumSectionHeader(
                        title: "section.oracle.0.title".localized,
                        subtitle: "section.oracle.0.subtitle".localized
                    )

                    // Pendulum
                    pendulumSection
                        .id(Self.pendulumAnchor)
                    
                    // Question input
                    questionInput
                    
                    // Ask button
                    askButton
                    
                    resultsArea
                        .id(Self.resultsAnchor)
                }
                .padding()
                .readableContainer()
            }
            .scrollDismissesKeyboard(.interactively)
            // While the oracle thinks, keep the swinging pendulum in view;
            // once it answers, bring the answer (or the error) up to the top.
            .scrollsIntoView(Self.pendulumAnchor, using: proxy, onChangeOf: resultState) { $0 == .loading }
            .scrollsIntoView(Self.resultsAnchor, using: proxy, onChangeOf: resultState) { $0.isFinished }
            }
        }
        .navigationTitle("screen.oracle".localized)
        .navigationBarTitleDisplayMode(.inline)
    }
    
    private static let pendulumAnchor = "oracle-pendulum"
    private static let resultsAnchor = "oracle-results"

    private enum ResultState: Equatable {
        case none, loading, answered, failed

        var isFinished: Bool { self == .answered || self == .failed }
    }

    /// Error, answer and telemetry: everything that shows up after Ask.
    private var resultsArea: some View {
        VStack(spacing: 24) {
            // Error
            if let errorMessage {
                errorCard(errorMessage)
            }

            // Answer
            if let answer {
                PremiumSectionHeader(
                    title: "section.oracle.1.title".localized,
                    subtitle: "section.oracle.1.subtitle".localized
                )

                answerSection(answer)
            }

            // Telemetry citation
            if let telemetry {
                telemetrySection(telemetry)
            }
        }
    }

    private var resultState: ResultState {
        if isLoading { return .loading }
        if answer != nil { return .answered }
        if errorMessage != nil { return .failed }
        return .none
    }

    // MARK: - Pendulum
    
    private var pendulumSection: some View {
        ZStack {
            // String
            Rectangle()
                .fill(.white.opacity(0.3))
                .frame(width: 2, height: 100)
                .offset(y: -50)
            
            // Crystal
            Circle()
                .fill(
                    RadialGradient(
                        colors: [.purple, .indigo, .blue],
                        center: .center,
                        startRadius: 0,
                        endRadius: 30
                    )
                )
                .frame(width: 40, height: 40)
                .shadow(color: .purple.opacity(0.5), radius: 10)
                .offset(y: 50)
        }
        .rotationEffect(.degrees(pendulumAngle), anchor: .top)
        .animation(
            isLoading ?
                Animation.easeInOut(duration: 1).repeatForever(autoreverses: true) :
                .spring(),
            value: pendulumAngle
        )
        .frame(height: 160)
        .onChange(of: isLoading) { _, loading in
            pendulumAngle = loading ? 30 : 0
        }
    }
    
    // MARK: - Input
    
    private var questionInput: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("ui.oracle.0".localized)
                .font(.headline)
            
            TextField("ui.oracle.5".localized, text: $question, axis: .vertical)
                .textFieldStyle(.plain)
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: Radius.sm)
                        .fill(Color.surfaceBase)
                        .overlay(
                            RoundedRectangle(cornerRadius: Radius.sm)
                                .stroke(Color.borderSubtle, lineWidth: Stroke.hairline)
                        )
                )
                .lineLimit(2...4)
                .focused($questionFocused)
                .submitLabel(.go)
                // A wrapping field turns Return into a newline; treat it as
                // "ask" instead, since the keyboard hides the button below.
                .onChange(of: question) { _, newValue in
                    guard newValue.contains("\n") else { return }
                    question = newValue.replacingOccurrences(of: "\n", with: "")
                    submitQuestion()
                }
                .toolbar {
                    ToolbarItemGroup(placement: .keyboard) {
                        Spacer()
                        Button("ui.oracle.1".localized) { submitQuestion() }
                            .fontWeight(.semibold)
                            .disabled(!canAsk)
                    }
                }
        }
    }

    private var canAsk: Bool {
        !question.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !isLoading
    }

    private func submitQuestion() {
        guard canAsk else { return }
        // Put the keyboard away so it doesn't cover the answer.
        questionFocused = false
        Task { await askOracle() }
    }
    
    // MARK: - Ask Button
    
    private var askButton: some View {
        GradientButton("ui.oracle.1".localized, icon: "sparkle", isLoading: isLoading) {
            submitQuestion()
        }
        .disabled(!canAsk)
    }
    
    // MARK: - Error Card
    
    private func errorCard(_ message: String) -> some View {
        PremiumStatusBanner(
            title: "common.error".localized,
            message: message,
            tone: .warning
        )
    }
    
    // MARK: - Answer
    
    private func answerSection(_ answer: YesNoAnswer) -> some View {
        CardView {
            VStack(spacing: 16) {
                Text(answer.answer.uppercased())
                    .font(.largeTitle.bold())
                    .foregroundStyle(answer.answer.lowercased() == "yes" ? Color.positiveGreen : Color.warningOrange)

                HStack {
                    Text("ui.oracle.2".localized)
                    ProgressView(value: answer.confidence)
                        .tint(answer.answer.lowercased() == "yes" ? Color.positiveGreen : Color.warningOrange)
                    Text("\(Int(answer.confidence * 100))%")
                }
                .font(.caption)

                Text(answer.reasoning)
                    .font(.body)
                    .foregroundStyle(Color.textSecondary)
                    .multilineTextAlignment(.center)

                if let factors = answer.factors, !factors.isEmpty {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("How it was decided")
                            .font(.headline)

                        ForEach(factors, id: \.self) { factor in
                            HStack(alignment: .top, spacing: 10) {
                                Image(systemName: factor.helps ? "plus.circle.fill" : "minus.circle.fill")
                                    .foregroundStyle(factor.helps ? Color.positiveGreen : Color.warningOrange)
                                    .accessibilityLabel(factor.helps ? "In favour" : "Against")
                                Text(factor.text)
                                    .font(.subheadline)
                                    .foregroundStyle(Color.textSecondary)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                if !answer.guidance.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("ui.oracle.3".localized)
                            .font(.headline)

                        ForEach(answer.guidance, id: \.self) { tip in
                            HStack(alignment: .top) {
                                Text("•")
                                Text(tip)
                            }
                            .font(.subheadline)
                            .foregroundStyle(Color.textSecondary)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
        }
        .transition(.scale.combined(with: .opacity))
    }
    
    // MARK: - Telemetry Citation
    
    private func telemetrySection(_ citation: String) -> some View {
        VStack(spacing: 4) {
            Text("ui.oracle.4".localized)
                .font(.caption2.bold())
                .foregroundStyle(.cyan.opacity(0.6))
            Text(citation)
                .font(.system(.caption, design: .monospaced))
                .foregroundStyle(.cyan.opacity(0.8))
                .multilineTextAlignment(.center)
        }
        .padding(10)
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: Radius.sm)
                .fill(Color.surfaceBase)
                .overlay(
                    RoundedRectangle(cornerRadius: Radius.sm)
                        .stroke(.cyan.opacity(0.2), lineWidth: Stroke.hairline)
                )
        )
    }
    
    // MARK: - Horary Oracle Logic
    
    private func askOracle() async {
        guard let profile = store.activeProfile else { return }
        let hideSensitive = store.hideSensitiveDetailsEnabled
        let trimmedQuestion = question.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedQuestion.isEmpty else { return }
        
        isLoading = true
        answer = nil
        telemetry = nil
        errorMessage = nil
        
        defer { isLoading = false }
        
        // 1. Capture cosmic state at this exact moment. Planetary hours run
        //    from local sunrise and sunset, so time them to where the phone
        //    is; fall back to the birthplace if location isn't allowed.
        let now = Date()
        let here = await OracleLocation.shared.current()
        let latitude = here?.coordinate.latitude ?? profile.latitude
        let longitude = here?.coordinate.longitude ?? profile.longitude
        let snapshot = await CalendarOracle.shared.snapshot(at: now, latitude: latitude, longitude: longitude)

        // 2. Judge it. With a place, cast a full horary chart for this moment
        //    and read it the classical way; without one, fall back to the
        //    simpler reading of the topic's planet.
        let builtIn: YesNoAnswer
        let skySummary: String
        if let latitude, let longitude,
           let chart = try? await EphemerisEngine.shared.calculateHoraryChart(date: now, latitude: latitude, longitude: longitude) {
            let reading = await HoraryJudge.judge(question: trimmedQuestion, chart: chart) { name, days in
                let later = try? await EphemerisEngine.shared.calculateHoraryChart(
                    date: now.addingTimeInterval(days * 86_400), latitude: latitude, longitude: longitude
                )
                return later?.bodies.first { $0.name == name }?.speed
            }
            builtIn = YesNoAnswer(
                question: trimmedQuestion,
                answer: reading.answer,
                confidence: reading.confidence,
                reasoning: reading.reasoning,
                guidance: HoraryOracle.guidance(for: reading.topic, decision: reading.answer, voidOfCourse: reading.voidOfCourse),
                factors: reading.points
            )
            skySummary = reading.summary
        } else {
            builtIn = HoraryOracle.read(question: trimmedQuestion, snapshot: snapshot)
            skySummary = snapshot.citation
        }

        // Without the owner's AI access, the built-in judgement is the answer.
        // This is the normal path there, not a failure, so no error.
        guard AIAvailability.shared.isEnabled else {
            withAnimation(.spring()) {
                answer = builtIn
                telemetry = skySummary
            }
            UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
            return
        }

        // 3. Build the Horary system prompt, anchored on the built-in reading
        //    so the AI explains the same judgement rather than inventing one.
        let topic = OracleTopic.detect(in: trimmedQuestion)
        let systemPrompt = """
        You are a precise Horary Astrologer. The user has asked a Yes/No question. \
        Answer STRICTLY based on the following exact celestial telemetry captured at the \
        moment the question was asked.

        TELEMETRY:
        - Time: \(ISO8601DateFormatter().string(from: snapshot.timestamp))
        - Planetary Hour: \(snapshot.planetaryHour)
        - Moon: \(String(format: "%.1f", snapshot.moonDegree))° \(snapshot.moonSign)
        - Moon Phase: \(snapshot.moonPhase)
        - Void of Course: \(snapshot.isVoidOfCourse ? "YES — advise extreme caution" : "No")
        - Active Transits: \(snapshot.keyTransits.isEmpty ? "None notable" : snapshot.keyTransits.joined(separator: ", "))
        - Question topic: \(topic.label), read from \(topic.houseDescription)
        - Horary chart: \(skySummary)
        - Rule-based reading: \(builtIn.answer.uppercased()) — \(builtIn.reasoning) \((builtIn.factors ?? []).map(\.text).joined(separator: " "))
        
        USER'S NATAL DATA:
        - Name: \(profile.promptName(hideSensitive: hideSensitive))
        - Sun Sign: \(profile.sign ?? "unknown")
        - Birth Date: \(profile.promptBirthDate(hideSensitive: hideSensitive))
        
        RULES:
        1. If the Moon is Void of Course, strongly lean toward NO or caution.
        2. Malefic planetary hours (Saturn, Mars) add restriction. Benefic hours (Venus, Jupiter) add support.
        3. Keep the decision consistent with the rule-based reading unless the telemetry clearly says otherwise, and speak to the question's topic.
        4. For health, legal or large financial questions, remind the user to consult a professional.
        5. Be direct and specific. No vague hedging.
        6. You MUST respond with ONLY valid JSON, no markdown, no explanation outside the JSON.
        
        Respond in this exact JSON format:
        {"decision":"YES or NO","confidence":0.0 to 1.0,"reasoning":"2-3 sentences explaining WHY based on the telemetry","guidance":["actionable tip 1","actionable tip 2"]}
        """
        
        // 3. Send through Cosmic Guide chat pipeline
        do {
            let context = ChatContext(
                sunSign: profile.sign,
                moonSign: nil,
                risingSign: nil,
                birthTimeAssumed: nil,
                timeConfidence: nil,
                history: nil
            )
            let response = try await cosmicGuide.chat(
                message: "HORARY QUESTION: \(trimmedQuestion)",
                context: context,
                systemPrompt: systemPrompt,
                tone: "direct"
            )
            
            // 4. Parse the JSON response from the LLM
            let rawResponse = response.response
            if let parsed = parseOracleJSON(rawResponse, question: trimmedQuestion) {
                var explained = parsed
                explained.factors = builtIn.factors
                withAnimation(.spring()) {
                    answer = explained
                    telemetry = skySummary
                }
                // Heavy haptic — somatic anchor
                UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
            } else {
                // LLM returned text but not valid JSON — use it as reasoning
                withAnimation(.spring()) {
                    // Keep the built-in decision and use the AI's prose as the explanation.
                    answer = YesNoAnswer(
                        question: trimmedQuestion,
                        answer: builtIn.answer,
                        confidence: builtIn.confidence,
                        reasoning: rawResponse,
                        guidance: builtIn.guidance,
                        factors: builtIn.factors
                    )
                    telemetry = skySummary
                }
                UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
            }
        } catch {
            // Network failed — fall back to pure Horary math (no LLM)
            withAnimation(.spring()) {
                answer = builtIn
                telemetry = skySummary
            }
            errorMessage = "Couldn't reach the AI, so this is the built-in reading from the sky."
            UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
        }
    }
    
    // MARK: - JSON Parser
    
    private func parseOracleJSON(_ raw: String, question: String) -> YesNoAnswer? {
        // Strip markdown code fences if Gemini wraps them
        var cleaned = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        if cleaned.hasPrefix("```json") {
            cleaned = String(cleaned.dropFirst(7))
        } else if cleaned.hasPrefix("```") {
            cleaned = String(cleaned.dropFirst(3))
        }
        if cleaned.hasSuffix("```") {
            cleaned = String(cleaned.dropLast(3))
        }
        cleaned = cleaned.trimmingCharacters(in: .whitespacesAndNewlines)
        
        guard let data = cleaned.data(using: .utf8) else { return nil }
        
        struct OracleJSON: Decodable {
            let decision: String
            let confidence: Double
            let reasoning: String
            let guidance: [String]?
        }
        
        guard let parsed = try? JSONDecoder().decode(OracleJSON.self, from: data) else { return nil }
        
        return YesNoAnswer(
            question: question,
            answer: parsed.decision,
            confidence: min(max(parsed.confidence, 0), 1),
            reasoning: parsed.reasoning,
            guidance: parsed.guidance ?? []
        )
    }
    
}

// MARK: - Where the phone is

/// Finds the phone's approximate location once, to time the Oracle's
/// planetary hours to local sunrise and sunset. Asks permission the first
/// time; the location is used on the device and never sent anywhere.
@MainActor
final class OracleLocation: NSObject, CLLocationManagerDelegate {
    static let shared = OracleLocation()

    private let manager = CLLocationManager()
    private var locationWaiter: CheckedContinuation<CLLocation?, Never>?
    private var permissionWaiter: CheckedContinuation<Void, Never>?

    override private init() {
        super.init()
        manager.delegate = self
        // City-level is plenty for sunrise and sunset, and quicker to get.
        manager.desiredAccuracy = kCLLocationAccuracyKilometer
    }

    func current() async -> CLLocation? {
        if manager.authorizationStatus == .notDetermined {
            await withCheckedContinuation { waiter in
                permissionWaiter = waiter
                manager.requestWhenInUseAuthorization()
            }
        }
        let status = manager.authorizationStatus
        guard status == .authorizedWhenInUse || status == .authorizedAlways else { return nil }
        // Sunrise barely moves within an hour or a few miles, so reuse a recent fix.
        if let recent = manager.location, recent.timestamp.timeIntervalSinceNow > -3600 {
            return recent
        }
        guard locationWaiter == nil else { return manager.location }
        return await withCheckedContinuation { waiter in
            locationWaiter = waiter
            manager.requestLocation()
        }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        let status = manager.authorizationStatus
        Task { @MainActor in
            guard status != .notDetermined else { return }
            permissionWaiter?.resume()
            permissionWaiter = nil
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        let latest = locations.last
        Task { @MainActor in
            locationWaiter?.resume(returning: latest)
            locationWaiter = nil
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor in
            locationWaiter?.resume(returning: nil)
            locationWaiter = nil
        }
    }
}

// MARK: - Built-in horary reading

/// What a yes/no question is about: its horary house, and the planets that
/// traditionally rule it (used when a full chart can't be cast).
enum OracleTopic: String, CaseIterable {
    case love, money, career, communication, travel, home, children, wellbeing, friends, action, general

    /// The house horary reads the matter from.
    var house: Int {
        switch self {
        case .love: return 7
        case .money: return 2
        case .career: return 10
        case .communication: return 3
        case .travel: return 9
        case .home: return 4
        case .children: return 5
        case .wellbeing: return 6
        case .friends: return 11
        case .action, .general: return 1
        }
    }

    var houseOrdinal: String {
        switch house {
        case 1: return "1st"
        case 2: return "2nd"
        case 3: return "3rd"
        default: return "\(house)th"
        }
    }

    /// "the 7th house (partners and relationships)"
    var houseDescription: String {
        let covers: String
        switch self {
        case .love: covers = "partners and relationships"
        case .money: covers = "money and possessions"
        case .career: covers = "career and reputation"
        case .communication: covers = "messages, paperwork and short trips"
        case .travel: covers = "long journeys, study and the law"
        case .home: covers = "home, property and family"
        case .children: covers = "children, pleasure and romance"
        case .wellbeing: covers = "health"
        case .friends: covers = "friends, groups and hopes"
        case .action, .general: covers = "you and your own plans"
        }
        return "the \(houseOrdinal) house (\(covers))"
    }

    /// The question's key planet first, then a supporting one.
    var significators: [String] {
        switch self {
        case .love: return ["Venus", "Moon"]
        case .money: return ["Jupiter", "Venus"]
        case .career: return ["Sun", "Saturn"]
        case .communication: return ["Mercury", "Moon"]
        case .travel: return ["Jupiter", "Mercury"]
        case .home: return ["Moon", "Saturn"]
        case .children: return ["Jupiter", "Venus"]
        case .action: return ["Mars", "Sun"]
        case .wellbeing: return ["Sun", "Moon"]
        case .friends: return ["Jupiter", "Venus"]
        case .general: return ["Moon"]
        }
    }

    /// What a strong key planet suggests for this topic.
    var strongMeaning: String {
        switch self {
        case .love: return "affection and harmony come easily"
        case .money: return "growth and good fortune are well supported"
        case .career: return "effort tends to turn into lasting results"
        case .communication: return "messages and paperwork tend to go smoothly"
        case .travel: return "journeys and studies tend to go well"
        case .home: return "home life feels settled"
        case .children: return "warmth and fruitfulness are well supported"
        case .action: return "courage and drive are running high"
        case .wellbeing: return "vitality is strong"
        case .friends: return "friends and allies are helpful"
        case .general: return "things tend to flow"
        }
    }

    /// What a weak key planet suggests for this topic.
    var weakMeaning: String {
        switch self {
        case .love: return "feelings may be guarded, intense or complicated"
        case .money: return "gains may come slower or smaller than hoped"
        case .career: return "commitments may feel heavy or slow to pay off"
        case .communication: return "details are more likely to go astray"
        case .travel: return "plans may be delayed or rerouted"
        case .home: return "home matters may feel unsettled"
        case .children: return "things may need more patience than hoped"
        case .action: return "energy may scatter or turn into conflict"
        case .wellbeing: return "energy may run lower than usual"
        case .friends: return "support may be thinner than expected"
        case .general: return "moods and plans may be unsettled"
        }
    }

    var label: String {
        switch self {
        case .love: return "love and relationships"
        case .money: return "money"
        case .career: return "work and career"
        case .communication: return "messages and agreements"
        case .travel: return "travel, study and legal matters"
        case .home: return "home and family"
        case .children: return "children"
        case .wellbeing: return "health and wellbeing"
        case .friends: return "friends and groups"
        case .action: return "your own plans"
        case .general: return "general"
        }
    }

    private var keywords: Set<String> {
        switch self {
        case .love:
            return ["love", "date", "dating", "relationship", "partner", "boyfriend", "girlfriend",
                    "husband", "wife", "marry", "marriage", "married", "crush", "ex", "romance",
                    "romantic", "kiss", "propose", "proposal", "wedding", "breakup", "divorce",
                    "soulmate", "flirt", "reconcile", "spouse", "fiance", "fiancee"]
        case .money:
            return ["money", "invest", "investment", "investing", "buy", "purchase", "sell",
                    "loan", "debt", "salary", "raise", "pay", "price", "mortgage", "stock",
                    "stocks", "crypto", "afford", "spend", "save", "savings", "bonus", "budget",
                    "profit", "bet", "lottery", "inheritance"]
        case .career:
            return ["job", "work", "career", "boss", "promotion", "interview", "hire", "hired",
                    "quit", "resign", "business", "company", "project", "client", "clients",
                    "apply", "application", "office", "colleague", "launch", "startup", "manager"]
        case .communication:
            return ["call", "text", "message", "email", "reply", "send", "sign", "contract",
                    "write", "post", "tell", "contact", "agreement", "deal", "negotiate",
                    "letter", "paperwork", "sibling", "brother", "sister", "neighbour", "neighbor"]
        case .travel:
            return ["travel", "trip", "flight", "fly", "abroad", "visa", "holiday", "vacation",
                    "study", "exam", "university", "college", "course", "degree", "school",
                    "court", "lawyer", "lawsuit", "legal", "publish", "journey", "emigrate"]
        case .home:
            return ["home", "house", "flat", "apartment", "move", "moving", "property", "rent",
                    "landlord", "tenant", "family", "parents", "mother", "father", "mum", "mom",
                    "dad", "renovate", "garden"]
        case .children:
            return ["child", "children", "kid", "kids", "baby", "pregnant", "pregnancy", "son",
                    "daughter", "fertility", "ivf", "conceive"]
        case .wellbeing:
            return ["health", "doctor", "medication", "medicine", "surgery", "diet", "therapy",
                    "therapist", "sick", "hospital", "treatment", "exercise", "sleep", "weight",
                    "illness", "ill", "pain", "operation", "recover", "recovery"]
        case .friends:
            return ["friend", "friends", "friendship", "group", "club", "community", "network",
                    "wish", "hope", "team"]
        case .action:
            return ["start", "begin", "fight", "confront", "compete", "competition", "race",
                    "risk", "leap", "challenge", "attempt", "change", "try"]
        case .general:
            return []
        }
    }

    /// The topic whose keywords appear most in the question. Ties go to the
    /// earlier topic in this list, so health and money questions keep their
    /// "talk to a professional" note even when other words also match.
    static func detect(in question: String) -> OracleTopic {
        let words = Set(
            question.lowercased()
                .components(separatedBy: CharacterSet.letters.inverted)
                .filter { !$0.isEmpty }
        )
        let ranked: [OracleTopic] = [.wellbeing, .money, .children, .love, .home, .career,
                                     .travel, .communication, .friends, .action]
        var best: OracleTopic = .general
        var bestHits = 0
        for topic in ranked {
            let hits = topic.keywords.intersection(words).count
            if hits > bestHits {
                best = topic
                bestHits = hits
            }
        }
        return best
    }
}

/// Answers a yes/no question from the sky at the moment it is asked, weighted
/// towards the planet that rules the question's topic. Runs on the device, so
/// the question never leaves the phone, and the same sky and question always
/// give the same answer. Every point it weighs is explained in plain words.
enum HoraryOracle {
    private struct Factor {
        let weight: Double
        let text: String
    }

    private static let helpfulPlanets: Set<String> = ["Venus", "Jupiter"]
    private static let harshPlanets: Set<String> = ["Saturn", "Mars", "Pluto"]
    /// Planets that stay in one sign, or one retrograde spell, for months.
    /// Their state counts half, so a question isn't stuck on one answer for
    /// weeks while the fast-moving Moon and planetary hour keep changing.
    private static let slowPlanets: Set<String> = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

    static func read(question: String, snapshot: CalendarOracle.HorarySnapshot) -> YesNoAnswer {
        let topic = OracleTopic.detect(in: question)
        let key = topic.significators[0]
        let bodies = Dictionary(snapshot.bodies.map { ($0.name, $0) }, uniquingKeysWith: { first, _ in first })
        let opening = topic == .general
            ? "No clear topic, so the Moon speaks for your question: it rules the everyday flow of events."
            : "This is a question about \(topic.label), which traditional astrology reads through \(key)."

        // A void-of-course Moon overrides everything in traditional horary.
        if snapshot.isVoidOfCourse {
            let line = OracleFactorLine(
                helps: false,
                text: "The Moon is \"void of course\": it will make no more contact with other planets before it changes sign. Traditionally, nothing started in this gap comes to much."
            )
            return YesNoAnswer(
                question: question,
                answer: "No",
                confidence: 0.85,
                reasoning: "\(opening) But the Moon is void of course right now, which traditional astrology treats as a firm no until it moves into its next sign.",
                guidance: guidance(for: topic, decision: "No", voidOfCourse: true),
                factors: [line]
            )
        }

        var factors: [Factor] = []

        // 1. The planetary hour.
        let hour = snapshot.planetaryHour
        if hour == key {
            factors.append(Factor(weight: 2, text: "It's the hour of \(key). Astrologers split each day into 12 planetary hours, and asking in the hour of the planet that rules your question is the strongest sign in favour."))
        } else if helpfulPlanets.contains(hour) {
            factors.append(Factor(weight: 1, text: "It's the hour of \(hour), one of the two traditionally helpful planets, which tips things towards yes."))
        } else if harshPlanets.contains(hour) {
            factors.append(Factor(weight: -1, text: "It's the hour of \(hour), a traditionally harsh planet linked with delays and obstacles."))
        }

        if let planet = bodies[key] {
            let slowWeight: Double = slowPlanets.contains(key) ? 0.5 : 1

            // 2. How strong the key planet is in its sign.
            switch planet.dignity {
            case "domicile":
                factors.append(Factor(weight: slowWeight, text: "\(key) is in \(planet.sign), one of its home signs, where it works at full strength: \(topic.strongMeaning)."))
            case "exaltation":
                factors.append(Factor(weight: slowWeight, text: "\(key) is exalted in \(planet.sign), one of its best placements: \(topic.strongMeaning)."))
            case "detriment":
                factors.append(Factor(weight: -slowWeight, text: "\(key) is in \(planet.sign), the sign opposite its home, where it struggles: \(topic.weakMeaning)."))
            case "fall":
                factors.append(Factor(weight: -slowWeight, text: "\(key) is in its \"fall\" in \(planet.sign), one of its weakest placements: \(topic.weakMeaning)."))
            default:
                break
            }

            // 3. Retrograde: review, don't start.
            if planet.retrograde == true, key != "Sun", key != "Moon" {
                factors.append(Factor(weight: -slowWeight, text: "\(key) is retrograde: seen from Earth it appears to move backwards. Traditionally that's a time to review and revisit, not to start something new."))
            }

            // 4. The Moon's aspect to the key planet.
            if key != "Moon", let moon = bodies["Moon"],
               let aspect = aspect(between: moon, and: planet, orb: 6) {
                let angle = aspectDescription(aspect)
                switch aspect {
                case "trine", "sextile":
                    factors.append(Factor(weight: 1.5, text: "The Moon, which shows how events unfold, is at a friendly angle to \(key) (\(angle)), a sign things can move with ease."))
                case "conjunction":
                    factors.append(Factor(weight: 1.5, text: "The Moon, which shows how events unfold, is travelling alongside \(key) (\(angle)), putting your question in focus."))
                default:
                    factors.append(Factor(weight: -1.5, text: "The Moon, which shows how events unfold, is at a tense angle to \(key) (\(angle)), a sign of friction along the way."))
                }
            }

            // 5. Close aspects from helpful or harsh planets.
            for other in snapshot.bodies where other.name != key && other.name != "Moon" {
                guard helpfulPlanets.contains(other.name) || harshPlanets.contains(other.name),
                      let aspect = aspect(between: other, and: planet, orb: 3) else { continue }
                let tense = aspect == "square" || aspect == "opposition"
                let angle = aspectDescription(aspect)
                let aspectWeight: Double = slowPlanets.contains(other.name) && slowPlanets.contains(key) ? 0.5 : 1
                if harshPlanets.contains(other.name), tense || aspect == "conjunction" {
                    factors.append(Factor(weight: -aspectWeight, text: "\(other.name) is pressing on \(key) (\(angle)), adding pressure, haste or obstacles."))
                } else if helpfulPlanets.contains(other.name), !tense {
                    factors.append(Factor(weight: aspectWeight, text: "\(other.name) is supporting \(key) (\(angle)), which adds goodwill and luck."))
                }
            }
        }

        // 6. The Moon's phase.
        let phase = snapshot.moonPhase
        if phase.hasPrefix("Waxing") || phase == "New Moon" || phase == "First Quarter" {
            factors.append(Factor(weight: 0.5, text: "The Moon is growing (\(phase)), which traditionally favours new beginnings."))
        } else if phase.hasPrefix("Waning") || phase == "Last Quarter" {
            factors.append(Factor(weight: -0.5, text: "The Moon is shrinking (\(phase)), which favours finishing things over starting them."))
        }

        let score = factors.reduce(0) { $0 + $1.weight }
        let decision = score > 0 ? "Yes" : (score < 0 ? "No" : "Wait")
        let confidence = decision == "Wait" ? 0.5 : min(0.88, 0.55 + 0.08 * abs(score))
        let forCount = factors.filter { $0.weight > 0 }.count
        let againstCount = factors.filter { $0.weight < 0 }.count

        let summary: String
        switch decision {
        case "Yes":
            summary = againstCount == 0
                ? "Everything the Oracle checked points the same way, so the answer is yes."
                : "The signs in favour outweigh the \(againstCount == 1 ? "one" : "\(againstCount)") against, so the answer is yes."
        case "No":
            summary = forCount == 0
                ? "Nothing the Oracle checked is working in your favour right now, so the answer is no."
                : "The signs against outweigh the \(forCount == 1 ? "one" : "\(forCount)") in favour, so the answer is no for now."
        default:
            summary = factors.isEmpty
                ? "The sky gives no clear signal for this question right now. Try again when the hour changes."
                : "The signs for and against are evenly balanced, so the Oracle says wait."
        }

        return YesNoAnswer(
            question: question,
            answer: decision,
            confidence: confidence,
            reasoning: "\(opening) \(summary)",
            guidance: guidance(for: topic, decision: decision, voidOfCourse: false),
            factors: factors
                .sorted { abs($0.weight) > abs($1.weight) }
                .map { OracleFactorLine(helps: $0.weight > 0, text: $0.text) }
        )
    }

    private static func aspectDescription(_ aspect: String) -> String {
        switch aspect {
        case "conjunction": return "a conjunction, side by side"
        case "sextile": return "a sextile, 60°"
        case "square": return "a square, 90°"
        case "trine": return "a trine, 120°"
        default: return "an opposition, 180°"
        }
    }

    /// The aspect between two bodies within `orb` degrees, if any.
    private static func aspect(between a: PlanetPlacement, and b: PlanetPlacement, orb: Double) -> String? {
        guard let aDeg = a.absoluteDegree, let bDeg = b.absoluteDegree else { return nil }
        var diff = abs(aDeg - bDeg).truncatingRemainder(dividingBy: 360)
        if diff > 180 { diff = 360 - diff }
        let aspects: [(String, Double)] = [
            ("conjunction", 0), ("sextile", 60), ("square", 90), ("trine", 120), ("opposition", 180),
        ]
        return aspects.first { abs(diff - $0.1) <= orb }?.0
    }

    static func guidance(for topic: OracleTopic, decision: String, voidOfCourse: Bool) -> [String] {
        var tips: [String] = []
        if voidOfCourse {
            tips.append("Ask again once the Moon enters its next sign, usually within a day.")
        } else {
            switch (topic, decision) {
            case (.love, "Yes"): tips.append("Reach out warmly, and let them answer in their own time.")
            case (.love, _): tips.append("Give it a few days and notice how you feel before raising it.")
            case (.money, "Yes"): tips.append("Go ahead in a size you could comfortably lose.")
            case (.money, _): tips.append("Hold off on big purchases or investments for now.")
            case (.career, "Yes"): tips.append("Put it in writing and commit to a first step this week.")
            case (.career, _): tips.append("Prepare now and move when the timing is clearer.")
            case (.communication, "Yes"): tips.append("Send it, but read it through once before you do.")
            case (.communication, _): tips.append("Double-check the details, and delay signing if you can.")
            case (.action, "Yes"): tips.append("Start while the energy is behind you.")
            case (.action, _): tips.append("Channel the urge into planning rather than acting today.")
            case (.travel, "Yes"): tips.append("Book or apply, and leave a little slack in the plan.")
            case (.travel, _): tips.append("Keep options open and check the details twice.")
            case (.home, "Yes"): tips.append("Go ahead, and get the practical details in writing.")
            case (.home, _): tips.append("Hold off on big home decisions until things settle.")
            case (.children, "Yes"): tips.append("Stay hopeful, and look after yourself along the way.")
            case (.children, _): tips.append("Be patient with yourself; timing often shifts.")
            case (.friends, "Yes"): tips.append("Reach out; people are more open than you think.")
            case (.friends, _): tips.append("Give it time, and invest in the friendships that already work.")
            case (.wellbeing, _): tips.append("Look after the basics today: rest, water and a steady routine.")
            case (_, "Yes"): tips.append("Take one concrete step today.")
            case (_, "Wait"): tips.append("Ask again in an hour, when the planetary hour changes.")
            default: tips.append("Give it time and ask again later.")
            }
        }
        switch topic {
        case .wellbeing:
            tips.append("This is for reflection. For health decisions, talk to a doctor.")
        case .money:
            tips.append("This is for reflection. For big financial decisions, talk to a qualified adviser.")
        default:
            tips.append("Treat this as one signal among many, and trust your own judgement.")
        }
        return tips
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        OracleView()
            .environment(AppStore.shared)
    }
    .preferredColorScheme(.dark)
}
