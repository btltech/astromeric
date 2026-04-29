// CompatibilityView.swift
// Synastry/compatibility display and input

import SwiftUI

struct CompatibilityView: View {
    @Environment(AppStore.self) private var store
    @State private var viewModel = CompatibilityVM()
    @State private var relationshipsVM = RelationshipsVM()
    @State private var hasSaved = false
    @State private var showDatePicker = false
    @State private var showTimePicker = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        PremiumHeroCard(
                            eyebrow: "hero.compatibility.eyebrow".localized,
                            title: "hero.compatibility.title".localized,
                            bodyText: "hero.compatibility.body".localized,
                            accent: [Color(hex: "2d102d"), Color(hex: "a53d79"), Color(hex: "4d3ca6")],
                            chips: ["hero.compatibility.chip.0".localized, "hero.compatibility.chip.1".localized, "hero.compatibility.chip.2".localized, "hero.compatibility.chip.3".localized]
                        )

                        if viewModel.hasData {
                            resultsSection
                        } else {
                            inputSection
                        }
                    }
                    .padding()
                    .readableContainer()
                }
            }
            .navigationTitle("charts.compatibility".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if viewModel.hasData {
                    ToolbarItem(placement: .topBarLeading) {
                        Button(hasSaved ? "tern.compatibility.0a".localized : "tern.compatibility.0b".localized) {
                            guard let personA = store.activeProfile,
                                  let result = viewModel.compatibilityData else { return }
                            
                            let relationship = SavedRelationship.from(
                                personA: personA,
                                personBName: viewModel.resolvedPersonBName(store: store),
                                personBDOB: viewModel.resolvedPersonBDOBString(store: store),
                                result: result,
                                type: .romantic,
                                hideSensitive: store.hideSensitiveDetailsEnabled
                            )
                            relationshipsVM.saveRelationship(relationship)
                            hasSaved = true
                        }
                        .disabled(hasSaved)
                    }
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("action.reset".localized) {
                            withAnimation {
                                viewModel.reset()
                                hasSaved = false
                            }
                        }
                    }
                }
            }
        }
    }

    private var personBCandidates: [Profile] {
        guard let activeId = store.activeProfile?.id else { return store.profiles }
        return store.profiles.filter { $0.id != activeId }
    }
    
    // MARK: - Input Section
    
    private var inputSection: some View {
        VStack(spacing: 20) {
            PremiumSectionHeader(
                title: "section.compatibility.0.title".localized,
                subtitle: "section.compatibility.0.subtitle".localized
            )

            // Your profile (Person A)
            CardView {
                VStack(alignment: .leading, spacing: 12) {
                    Text("ui.compatibility.0".localized)
                        .font(.headline)
                    
                    if let profile = store.activeProfile {
                        HStack {
                            Image(systemName: "person.fill")
                                .foregroundStyle(.purple)
                            Text(profile.displayName(
                                hideSensitive: store.hideSensitiveDetailsEnabled,
                                role: .activeUser
                            ))
                            Spacer()
                            Text(store.hideSensitiveDetailsEnabled ? PrivacyRedaction.maskedDate : profile.dateOfBirth)
                                .foregroundStyle(Color.textSecondary)
                        }
                    } else {
                        Text("ui.compatibility.1".localized)
                            .foregroundStyle(Color.textMuted)
                    }
                }
            }
            
            // Person B input
            CardView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("ui.compatibility.2".localized)
                        .font(.headline)

                    if !personBCandidates.isEmpty {
                        Toggle("ui.compatibility.13".localized, isOn: $viewModel.useSavedProfileForPersonB)
                            .tint(.pink)
                            .onChange(of: viewModel.useSavedProfileForPersonB) { _, newValue in
                                if newValue, viewModel.selectedPersonBProfileId == nil {
                                    viewModel.selectedPersonBProfileId = personBCandidates.first?.id
                                }
                            }

                        if viewModel.useSavedProfileForPersonB {
                            Picker("ui.compatibility.15".localized, selection: $viewModel.selectedPersonBProfileId) {
                                Text("ui.compatibility.3".localized).tag(Optional<Int>(nil))
                                ForEach(Array(personBCandidates.enumerated()), id: \.element.id) { index, profile in
                                    Text(profile.displayName(
                                        hideSensitive: store.hideSensitiveDetailsEnabled,
                                        role: .genericProfile,
                                        index: index
                                    ))
                                    .tag(Optional(profile.id))
                                }
                            }
                            .pickerStyle(.menu)
                            Divider()
                        }
                    }
                    
                    // Name
                    VStack(alignment: .leading, spacing: 4) {
                        Text("ui.compatibility.4".localized)
                            .font(.caption)
                            .foregroundStyle(Color.textMuted)
                        TextField("ui.compatibility.14".localized, text: $viewModel.personBName)
                            .textFieldStyle(.roundedBorder)
                            .disabled(viewModel.useSavedProfileForPersonB)
                    }
                    
                    // Birth date
                    VStack(alignment: .leading, spacing: 4) {
                        Text("ui.compatibility.5".localized)
                            .font(.caption)
                            .foregroundStyle(Color.textMuted)
                        DatePicker(
                            "Birth Date",
                            selection: $viewModel.personBDOB,
                            displayedComponents: .date
                        )
                        .datePickerStyle(.compact)
                        .labelsHidden()
                        .disabled(viewModel.useSavedProfileForPersonB)
                    }
                    
                    // Birth time (optional)
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text("ui.compatibility.6".localized)
                                .font(.caption)
                                .foregroundStyle(Color.textMuted)
                            Text("ui.compatibility.7".localized)
                                .font(.caption2)
                                .foregroundStyle(Color.textMuted)
                        }
                        
                        if let time = viewModel.personBTime {
                            HStack {
                                Text(time, style: .time)
                                Spacer()
                                Button("ui.compatibility.16".localized) {
                                    viewModel.personBTime = nil
                                }
                                .font(.caption)
                            }
                        } else {
                            DatePicker(
                                "Birth Time",
                                selection: Binding(
                                    get: { viewModel.personBTime ?? Date() },
                                    set: { viewModel.personBTime = $0 }
                                ),
                                displayedComponents: .hourAndMinute
                            )
                            .datePickerStyle(.compact)
                            .labelsHidden()
                        }
                    }
                    .disabled(viewModel.useSavedProfileForPersonB)
                }
            }
            
            // Calculate button
            GradientButton("Calculate Compatibility", icon: "heart.fill") {
                Task {
                    guard let profile = store.activeProfile else { return }
                    hasSaved = false
                    let personB = viewModel.resolvedPersonBPayload(store: store)
                    await viewModel.fetchCompatibility(personA: profile, personB: personB)
                }
            }
            .disabled(!viewModel.canCalculate(store: store) || viewModel.isLoading)
            
            if viewModel.isLoading {
                ProgressView("Calculating...")
            }
            
            if let error = viewModel.error {
                Text(error)
                    .font(.caption)
                    .foregroundStyle(.red)
            }
        }
    }
    
    // MARK: - Results Section
    
    private var resultsSection: some View {
        VStack(spacing: 20) {
            PremiumSectionHeader(
                title: "section.compatibility.1.title".localized,
                subtitle: "section.compatibility.1.subtitle".localized
            )

            // Names header
            CardView {
                HStack {
                    VStack {
                        Image(systemName: "person.fill")
                            .font(.title2)
                            .foregroundStyle(.purple)
                        Text(
                            store.activeProfile?.displayName(
                                hideSensitive: store.hideSensitiveDetailsEnabled,
                                role: .activeUser
                            ) ?? "You"
                        )
                            .font(.caption)
                    }
                    
                    Spacer()
                    
                    Image(systemName: "heart.fill")
                        .font(.title)
                        .foregroundStyle(.pink)
                    
                    Spacer()
                    
                    VStack {
                        Image(systemName: "person.fill")
                            .font(.title2)
                            .foregroundStyle(.pink)
                        Text(viewModel.resolvedPersonBDisplayName(
                            store: store,
                            hideSensitive: store.hideSensitiveDetailsEnabled
                        ))
                            .font(.caption)
                    }
                }
                .padding(.vertical, 8)
            }
            
            // Overall score
            CardView {
                VStack(spacing: 16) {
                    Text("ui.compatibility.8".localized)
                        .font(.headline)
                    
                    ZStack {
                        Circle()
                            .stroke(Color.cosmicSecondary.opacity(0.5), lineWidth: 12)
                            .frame(width: 120, height: 120)
                        
                        Circle()
                            .trim(from: 0, to: viewModel.overallScore / 100)
                            .stroke(
                                LinearGradient(
                                    colors: [.pink, .purple],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                ),
                                style: StrokeStyle(lineWidth: 12, lineCap: .round)
                            )
                            .frame(width: 120, height: 120)
                            .rotationEffect(.degrees(-90))
                            .animation(.easeInOut(duration: 1), value: viewModel.overallScore)
                        
                        VStack {
                            Text(String(format: "%.0f%%", viewModel.overallScore))
                                .font(.title.bold())
                            Text(compatibilityRating)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }

                    // Confidence note when birth times are missing
                    if let note = viewModel.confidenceNote {
                        DataQualityBanner(
                            icon: "clock.badge.questionmark",
                            message: "Confidence \(Int(viewModel.confidenceScore))% — \(note)",
                            color: .yellow
                        )
                    }
                }
            }
            
            // Dimension breakdown
            CardView {
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Image(systemName: "chart.bar.fill")
                            .foregroundStyle(.purple)
                        Text("ui.compatibility.9".localized)
                            .font(.headline)
                    }
                    
                    ForEach(viewModel.categories, id: \.name) { category in
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text(categoryEmoji(category.name))
                                Text(category.name)
                                    .font(.subheadline.bold())
                                Spacer()
                                Text(String(format: "%.0f%%", category.score))
                                    .font(.subheadline.bold())
                                    .foregroundStyle(scoreColor(category.score))
                            }
                            
                            GeometryReader { geo in
                                ZStack(alignment: .leading) {
                                    Capsule()
                                        .fill(Color.cosmicSecondary.opacity(0.4))
                                        .frame(height: 8)
                                    Capsule()
                                        .fill(scoreColor(category.score))
                                        .frame(width: geo.size.width * (category.score / 100), height: 8)
                                }
                            }
                            .frame(height: 8)
                            
                            if let description = category.description {
                                Text(description)
                                    .font(.caption)
                                    .foregroundStyle(Color.textMuted)
                            }
                        }
                        
                        if category.name != viewModel.categories.last?.name {
                            Divider()
                        }
                    }
                }
            }
            
            // Strengths
            if !viewModel.strengths.isEmpty {
                CardView {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "star.fill")
                                .foregroundStyle(.green)
                            Text("ui.compatibility.10".localized)
                                .font(.headline)
                        }
                        
                        ForEach(viewModel.strengths, id: \.self) { strength in
                            HStack(alignment: .top, spacing: 10) {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundStyle(.green)
                                    .font(.subheadline)
                                Text(strength)
                                    .font(.subheadline)
                            }
                        }
                    }
                }
            }
            
            // Challenges
            if !viewModel.challenges.isEmpty {
                CardView {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundStyle(.orange)
                            Text("ui.compatibility.11".localized)
                                .font(.headline)
                        }
                        
                        ForEach(viewModel.challenges, id: \.self) { challenge in
                            HStack(alignment: .top, spacing: 10) {
                                Image(systemName: "arrow.triangle.2.circlepath")
                                    .foregroundStyle(.orange)
                                    .font(.subheadline)
                                Text(challenge)
                                    .font(.subheadline)
                            }
                        }
                    }
                }
            }
            
            // Advice
            if !viewModel.advice.isEmpty {
                CardView {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "lightbulb.fill")
                                .foregroundStyle(.yellow)
                            Text("ui.compatibility.12".localized)
                                .font(.headline)
                        }
                        
                        ForEach(viewModel.advice, id: \.self) { tip in
                            HStack(alignment: .top, spacing: 10) {
                                Image(systemName: "heart.circle.fill")
                                    .foregroundStyle(.pink)
                                    .font(.subheadline)
                                Text(tip)
                                    .font(.subheadline)
                            }
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - Helpers
    
    private var compatibilityRating: String {
        let score = viewModel.overallScore
        if score >= 90 { return "Soul Mates" }
        if score >= 75 { return "Highly Compatible" }
        if score >= 60 { return "Good Match" }
        if score >= 40 { return "Mixed Signals" }
        return "Challenging"
    }
    
    private func scoreColor(_ score: Double) -> Color {
        if score >= 75 { return .green }
        if score >= 50 { return .purple }
        if score >= 25 { return .orange }
        return .red
    }
    
    private func categoryEmoji(_ name: String) -> String {
        switch name.lowercased() {
        case "emotional": return "💜"
        case "communication": return "💬"
        case "physical": return "🔥"
        case "intellectual": return "🧠"
        case "spiritual": return "✨"
        case "values": return "🎯"
        case "growth": return "🌱"
        default: return "💫"
        }
    }
}

// MARK: - Preview

#Preview {
    CompatibilityView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
