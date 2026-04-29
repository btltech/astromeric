// OracleView.swift
// Horary Oracle — Yes/No answers grounded in real-time planetary math
// Routes through Cosmic Guide chat pipeline with EphemerisEngine telemetry

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
    
    private let api = APIClient.shared
    
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 24) {
                    PremiumHeroCard(
                            eyebrow: "hero.oracle.eyebrow".localized,
                            title: "hero.oracle.title".localized,
                            bodyText: "hero.oracle.body".localized,
                            accent: [Color(hex: "101d3a"), Color(hex: "324fb9"), Color(hex: "7c45aa")],
                            chips: ["hero.oracle.chip.0".localized, "hero.oracle.chip.1".localized, "hero.oracle.chip.2".localized]
                        )

                    PremiumSectionHeader(
                title: "section.oracle.0.title".localized,
                subtitle: "section.oracle.0.subtitle".localized
            )

                    // Pendulum
                    pendulumSection
                    
                    // Question input
                    questionInput
                    
                    // Ask button
                    askButton
                    
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
                .padding()
                .readableContainer()
            }
        }
        .navigationTitle("screen.oracle".localized)
        .navigationBarTitleDisplayMode(.inline)
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
                    RoundedRectangle(cornerRadius: 12)
                        .fill(.ultraThinMaterial)
                )
                .lineLimit(2...4)
        }
    }
    
    // MARK: - Ask Button
    
    private var askButton: some View {
        Button {
            Task {
                await askOracle()
            }
        } label: {
            HStack {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    Image(systemName: "sparkle")
                    Text("ui.oracle.1".localized)
                }
            }
            .font(.headline)
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(
                Capsule()
                    .fill(
                        LinearGradient(
                            colors: [.blue, .purple],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
            )
        }
        .disabled(question.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isLoading)
    }
    
    // MARK: - Error Card
    
    private func errorCard(_ message: String) -> some View {
        VStack(spacing: 8) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.title2)
                .foregroundStyle(.red)
            Text(message)
                .font(.caption.monospaced())
                .foregroundStyle(.red.opacity(0.8))
                .multilineTextAlignment(.center)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(.red.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(.red.opacity(0.3), lineWidth: 1)
                )
        )
    }
    
    // MARK: - Answer
    
    private func answerSection(_ answer: YesNoAnswer) -> some View {
        VStack(spacing: 16) {
            // Main answer
            Text(answer.answer.uppercased())
                .font(.largeTitle.bold())
                .foregroundStyle(answer.answer.lowercased() == "yes" ? .green : .orange)
            
            // Confidence
            HStack {
                Text("ui.oracle.2".localized)
                ProgressView(value: answer.confidence)
                    .tint(answer.answer.lowercased() == "yes" ? .green : .orange)
                Text("\(Int(answer.confidence * 100))%")
            }
            .font(.caption)
            
            // Reasoning
            Text(answer.reasoning)
                .font(.body)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
            
            // Guidance
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
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
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
            RoundedRectangle(cornerRadius: 10)
                .fill(.black.opacity(0.4))
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(.cyan.opacity(0.2), lineWidth: 1)
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
        
        // 1. Capture cosmic state at this exact moment
        let snapshot = await CalendarOracle.shared.snapshot(
            at: Date(),
            latitude: profile.latitude,
            longitude: profile.longitude
        )
        
        // 2. Build the Horary system prompt
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
        
        USER'S NATAL DATA:
        - Name: \(profile.promptName(hideSensitive: hideSensitive))
        - Sun Sign: \(profile.sign ?? "unknown")
        - Birth Date: \(profile.promptBirthDate(hideSensitive: hideSensitive))
        
        RULES:
        1. If the Moon is Void of Course, strongly lean toward NO or caution.
        2. Malefic planetary hours (Saturn, Mars) add restriction. Benefic hours (Venus, Jupiter) add support.
        3. Be direct and specific. No vague hedging.
        4. You MUST respond with ONLY valid JSON, no markdown, no explanation outside the JSON.
        
        Respond in this exact JSON format:
        {"decision":"YES or NO","confidence":0.0 to 1.0,"reasoning":"2-3 sentences explaining WHY based on the telemetry","guidance":["actionable tip 1","actionable tip 2"]}
        """
        
        // 3. Send through Cosmic Guide chat pipeline
        do {
            let response: V2ApiResponse<ChatResponse> = try await api.fetch(
                .cosmicGuideChat(
                    message: "HORARY QUESTION: \(trimmedQuestion)",
                    sunSign: profile.sign,
                    moonSign: nil,
                    risingSign: nil,
                    history: nil,
                    systemPrompt: systemPrompt,
                    tone: "direct"
                )
            )
            
            // 4. Parse the JSON response from the LLM
            let rawResponse = response.data.response
            if let parsed = parseOracleJSON(rawResponse, question: trimmedQuestion) {
                withAnimation(.spring()) {
                    answer = parsed
                    telemetry = snapshot.citation
                }
                // Heavy haptic — somatic anchor
                UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
            } else {
                // LLM returned text but not valid JSON — use it as reasoning
                withAnimation(.spring()) {
                    answer = YesNoAnswer(
                        question: trimmedQuestion,
                        answer: snapshot.isVoidOfCourse ? "No" : (snapshot.threatLevel == .red ? "No" : "Yes"),
                        confidence: 0.65,
                        reasoning: rawResponse,
                        guidance: ["Response was interpreted from cosmic state"]
                    )
                    telemetry = snapshot.citation
                }
                UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
            }
        } catch {
            // Network failed — fall back to pure Horary math (no LLM)
            withAnimation(.spring()) {
                let decision = horaryColdRead(snapshot: snapshot)
                answer = decision
                telemetry = snapshot.citation
            }
            errorMessage = "Offline mode: \(error.localizedDescription)"
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
    
    // MARK: - Offline Cold Read
    
    /// Pure Horary math fallback when network is unavailable.
    private func horaryColdRead(snapshot: CalendarOracle.HorarySnapshot) -> YesNoAnswer {
        let isYes: Bool
        let confidence: Double
        var reasoning: String
        
        if snapshot.isVoidOfCourse {
            isYes = false
            confidence = 0.85
            reasoning = "The Moon is Void of Course — no new aspects will form before sign change. Traditional Horary strongly advises against initiating anything during VOC periods."
        } else if snapshot.threatLevel == .red {
            isYes = false
            confidence = 0.72
            reasoning = "The Hour of \(snapshot.planetaryHour) is a malefic hour, creating restriction and friction. The cosmic environment does not support this action right now."
        } else if snapshot.threatLevel == .green {
            isYes = true
            confidence = 0.78
            reasoning = "The Hour of \(snapshot.planetaryHour) is benefic, and the Moon in \(snapshot.moonSign) (\(snapshot.moonPhase)) supports forward momentum."
        } else {
            isYes = snapshot.moonPhase.contains("Waxing") || snapshot.moonPhase == "Full Moon"
            confidence = 0.6
            reasoning = "Neutral planetary hour. The \(snapshot.moonPhase) in \(snapshot.moonSign) leans \(isYes ? "toward action" : "toward patience")."
        }
        
        if !snapshot.keyTransits.isEmpty {
            reasoning += " Active transits: \(snapshot.keyTransits.joined(separator: ", "))."
        }
        
        return YesNoAnswer(
            question: question,
            answer: isYes ? "Yes" : "No",
            confidence: confidence,
            reasoning: reasoning,
            guidance: [
                snapshot.isVoidOfCourse ? "Wait until the Moon enters the next sign" : "Trust the timing",
                snapshot.threatLevel == .red ? "Delay major decisions to a benefic hour" : "Proceed with awareness"
            ]
        )
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
