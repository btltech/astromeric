// CompatibilityView.swift
// Synastry/compatibility display and input

import SwiftUI

struct CompatibilityView: View {
    @Environment(AppStore.self) private var store
    @State private var viewModel = CompatibilityVM()
    @State private var showDatePicker = false
    @State private var showTimePicker = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        if viewModel.hasData {
                            resultsSection
                        } else {
                            inputSection
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Compatibility")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if viewModel.hasData {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("Reset") {
                            withAnimation {
                                viewModel.reset()
                            }
                        }
                    }
                }
            }
        }
    }
    
    // MARK: - Input Section
    
    private var inputSection: some View {
        VStack(spacing: 20) {
            // Your profile (Person A)
            CardView {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Your Profile")
                        .font(.headline)
                    
                    if let profile = store.selectedProfile {
                        HStack {
                            Image(systemName: "person.fill")
                                .foregroundStyle(.purple)
                            Text(profile.name)
                            Spacer()
                            Text(profile.dateOfBirth)
                                .foregroundStyle(.textSecondary)
                        }
                    } else {
                        Text("No profile selected")
                            .foregroundStyle(.textMuted)
                    }
                }
            }
            
            // Person B input
            CardView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("Compare With")
                        .font(.headline)
                    
                    // Name
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Name")
                            .font(.caption)
                            .foregroundStyle(.textMuted)
                        TextField("Enter name", text: $viewModel.personBName)
                            .textFieldStyle(.roundedBorder)
                    }
                    
                    // Birth date
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Birth Date")
                            .font(.caption)
                            .foregroundStyle(.textMuted)
                        DatePicker(
                            "Birth Date",
                            selection: $viewModel.personBDOB,
                            displayedComponents: .date
                        )
                        .datePickerStyle(.compact)
                        .labelsHidden()
                    }
                    
                    // Birth time (optional)
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text("Birth Time")
                                .font(.caption)
                                .foregroundStyle(.textMuted)
                            Text("(optional)")
                                .font(.caption2)
                                .foregroundStyle(.tertiary)
                        }
                        
                        if let time = viewModel.personBTime {
                            HStack {
                                Text(time, style: .time)
                                Spacer()
                                Button("Clear") {
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
                }
            }
            
            // Calculate button
            GradientButton("Calculate Compatibility", icon: "heart.fill") {
                Task {
                    if let profile = store.selectedProfile {
                        let personB = viewModel.buildPersonB()
                        await viewModel.fetchCompatibility(personA: profile, personB: personB)
                    }
                }
            }
            .disabled(viewModel.personBName.isEmpty || viewModel.isLoading)
            
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
            // Names header
            CardView {
                HStack {
                    VStack {
                        Image(systemName: "person.fill")
                            .font(.title2)
                            .foregroundStyle(.purple)
                        Text(store.selectedProfile?.name ?? "You")
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
                        Text(viewModel.personBName)
                            .font(.caption)
                    }
                }
                .padding(.vertical, 8)
            }
            
            // Overall score
            CardView {
                VStack(spacing: 16) {
                    Text("Overall Compatibility")
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
                                .foregroundStyle(.textSecondary)
                        }
                    }
                }
            }
            
            // Dimension breakdown
            CardView {
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Image(systemName: "chart.bar.fill")
                            .foregroundStyle(.purple)
                        Text("Dimension Breakdown")
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
                                    .foregroundStyle(.textMuted)
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
                            Text("Strengths")
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
                            Text("Challenges")
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
                            Text("Relationship Advice")
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
