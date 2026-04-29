// HabitsView.swift
// Lunar-aligned habit tracking view

import SwiftUI

struct HabitsView: View {
    @Environment(AppStore.self) private var store
    @State private var viewModel = HabitsVM()
    @State private var showCreateSheet = false
    @State private var selectedHabit: Habit?
    @State private var showCelebration = false
    @State private var hasCelebratedAllDone = false

    private var selectedTotal: Int {
        viewModel.totalCount(for: viewModel.selectedCategory)
    }

    private var selectedCompleted: Int {
        viewModel.completedCount(for: viewModel.selectedCategory)
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        PremiumHeroCard(
                            eyebrow: "hero.habits.eyebrow".localized,
                            title: "hero.habits.title".localized,
                            bodyText: "hero.habits.body".localized,
                            accent: [Color(hex: "13283b"), Color(hex: "1d7b83"), Color(hex: "66a65f")],
                            chips: ["hero.habits.chip.0".localized, "hero.habits.chip.1".localized, "hero.habits.chip.2".localized]
                        )

                        // Lunar guidance card
                        if let guidance = viewModel.lunarGuidance {
                            lunarGuidanceCard(guidance)
                        }
                        
                        // Stats overview
                        statsOverview

                        // Suggested next action
                        suggestedNextCard

                        PremiumSectionHeader(
                title: "section.habits.0.title".localized,
                subtitle: "section.habits.0.subtitle".localized
            )
                        
                        // Category filter
                        categoryPicker
                        
                        // Habits list
                        habitsSection
                    }
                    .padding()
                    .readableContainer()
                }
                
                if viewModel.isLoading && viewModel.habits.isEmpty {
                    LoadingOverlay()
                }

                if showCelebration {
                    CelebrationBannerView(
                        title: "All done for today!",
                        subtitle: viewModel.selectedCategory == "all"
                            ? "You completed \(selectedCompleted)/\(max(1, selectedTotal)) habits"
                            : "You completed \(selectedCompleted)/\(max(1, selectedTotal)) in \(viewModel.selectedCategory.capitalized)"
                    )
                    .padding(.top, 8)
                    .transition(.move(edge: .top).combined(with: .opacity))
                }
            }
            .navigationTitle("screen.habits".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showCreateSheet = true
                    } label: {
                        Image(systemName: "plus.circle.fill")
                            .font(.title2)
                            .foregroundStyle(.purple)
                    }
                    .buttonStyle(AccessibleButtonStyle())
                    .accessibilityLabel("Create habit")
                    .accessibilityHint("Opens the create habit form")
                }
            }
            .sheet(isPresented: $showCreateSheet) {
                CreateHabitSheet(viewModel: viewModel, isPresented: $showCreateSheet)
            }
            .task {
                await viewModel.loadData()
            }
            .onChange(of: viewModel.selectedCategory) { _, _ in
                // Reset celebration when switching filters.
                hasCelebratedAllDone = false
                showCelebration = false
            }
            .onChange(of: viewModel.habits) { _, _ in
                let total = selectedTotal
                let completed = selectedCompleted

                guard total > 0 else {
                    hasCelebratedAllDone = false
                    return
                }

                if completed >= total {
                    guard !hasCelebratedAllDone else { return }
                    hasCelebratedAllDone = true
                    withAnimation(.spring(duration: 0.35)) {
                        showCelebration = true
                    }
                    HapticManager.notification(.success)

                    Task {
                        try? await Task.sleep(nanoseconds: 2_200_000_000)
                        await MainActor.run {
                            withAnimation(.easeOut(duration: 0.25)) {
                                showCelebration = false
                            }
                        }
                    }
                } else {
                    hasCelebratedAllDone = false
                }
            }
        }
    }
    
    // MARK: - Lunar Guidance Card
    
    private func lunarGuidanceCard(_ guidance: LunarHabitGuidance) -> some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text(guidance.emoji)
                        .font(.largeTitle)
                    
                    VStack(alignment: .leading) {
                        Text(guidance.phaseName)
                            .font(.headline)
                        Text(guidance.theme)
                            .font(.subheadline)
                            .foregroundStyle(Color.textSecondary)
                    }
                    
                    Spacer()
                    
                    Text("×\(String(format: "%.1f", guidance.powerScoreModifier))")
                        .font(.caption.bold())
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(guidance.powerScoreModifier >= 1.0 ? Color.green.opacity(0.2) : Color.orange.opacity(0.2))
                        .foregroundStyle(guidance.powerScoreModifier >= 1.0 ? .green : .orange)
                        .clipShape(Capsule())
                }
                
                Divider()
                
                Text("ui.habits.0".localized)
                    .font(.label)
                    .foregroundStyle(Color.textSecondary)
                
                HStack(spacing: 8) {
                    ForEach(guidance.idealHabits.prefix(4), id: \.self) { habit in
                        Text(habitEmoji(for: habit))
                            .font(.title3)
                            .padding(6)
                            .background(Color.purple.opacity(0.2))
                            .clipShape(Circle())
                    }
                }
            }
        }
    }
    
    // MARK: - Stats Overview
    
    private var statsOverview: some View {
        VStack(spacing: 12) {
            HStack(spacing: 16) {
                StatCard(
                    title: "Today",
                    value: "\(selectedCompleted)/\(selectedTotal)",
                    icon: "checkmark.circle.fill",
                    color: .green
                )

                StatCard(
                    title: "Best Streak",
                    value: "\(viewModel.overallStreak)d",
                    icon: "flame.fill",
                    color: .orange
                )
            }

            TodayProgressView(
                title: viewModel.selectedCategory == "all" ? "Today" : "Today (\(viewModel.selectedCategory.capitalized))",
                completed: selectedCompleted,
                total: selectedTotal
            )
        }
    }
    
    // MARK: - Category Picker
    
    private var categoryPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                categoryChip(id: "all", name: "All", emoji: "✨")
                
                ForEach(viewModel.categories) { category in
                    categoryChip(id: category.id, name: category.name, emoji: category.emoji)
                }
            }
        }
    }
    
    private func categoryChip(id: String, name: String, emoji: String) -> some View {
        Button {
            withAnimation(.spring(duration: 0.3)) {
                viewModel.selectedCategory = id
            }
            HapticManager.impact(.light)
        } label: {
            HStack(spacing: 4) {
                let total = viewModel.totalCount(for: id)
                let done = viewModel.completedCount(for: id)

                if total > 0 {
                    ProgressRing(progress: Double(done) / Double(total))
                        .frame(width: 14, height: 14)
                        .padding(.trailing, 2)
                }

                Text(emoji)
                Text(name)
                    .font(.label)

                // Progress badge (completed/total)
                if total > 0 {
                    Text("\(done)/\(total)")
                        .font(.caption2.weight(.semibold))
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(
                            Capsule().fill(Color.white.opacity(viewModel.selectedCategory == id ? 0.25 : 0.12))
                        )
                        .foregroundStyle(viewModel.selectedCategory == id ? .white : .secondary)
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .frame(minHeight: 44)
            .background(
                Capsule()
                    .fill(viewModel.selectedCategory == id ? Color.purple : Color.white.opacity(0.1))
            )
            .foregroundStyle(viewModel.selectedCategory == id ? .white : .secondary)
        }
        .buttonStyle(AccessibleButtonStyle())
        .accessibilityLabel(name)
        .accessibilityValue(viewModel.selectedCategory == id ? "tern.habits.0a".localized : "tern.habits.0b".localized)
        .accessibilityHint("Filters habits by category")
    }

    // MARK: - Suggested Next

    private var suggestedNextCard: some View {
        Group {
            if let suggestion = viewModel.suggestedNextHabit {
                CardView {
                    VStack(alignment: .leading, spacing: 10) {
                        HStack(spacing: 10) {
                            Text("🎯")
                                .font(.title2)

                            VStack(alignment: .leading, spacing: 2) {
                                Text("ui.habits.1".localized)
                                    .font(.headline)

                                if let guidance = viewModel.lunarGuidance {
                                    Text(String(format: "fmt.habits.2".localized, "\(guidance.phaseName)"))
                                        .font(.label)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }

                            Spacer()

                            Button {
                                Task { await viewModel.toggleHabitCompletion(suggestion) }
                            } label: {
                                Text(suggestion.isCompletedToday ? "tern.habits.1a".localized : "tern.habits.1b".localized)
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(.white)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 8)
                                    .background(Capsule().fill(suggestion.isCompletedToday ? Color.green : Color.purple))
                            }
                            .buttonStyle(AccessibleButtonStyle())
                            .disabled(suggestion.isCompletedToday)
                            .accessibilityLabel(suggestion.isCompletedToday ? "Habit completed" : "Mark \(suggestion.name) done")
                            .accessibilityHint("Updates the completion state for the suggested habit")
                        }

                        HStack(spacing: 10) {
                            Text(suggestion.emoji)
                                .font(.title2)

                            VStack(alignment: .leading, spacing: 2) {
                                Text(suggestion.name)
                                    .font(.subheadline.weight(.semibold))
                                Text(String(format: "fmt.habits.1".localized, "\(suggestion.currentStreak)", "\(Int(suggestion.completionRate * 100))"))
                                    .font(.label)
                                    .foregroundStyle(Color.textSecondary)
                            }

                            Spacer()

                            Image(systemName: "chevron.right")
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
    }
    
    // MARK: - Habits Section
    
    private var habitsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            if viewModel.filteredHabits.isEmpty {
                emptyHabitsCard
            } else {
                let upNext = viewModel.filteredHabits.filter { !$0.isCompletedToday }
                let completed = viewModel.filteredHabits.filter { $0.isCompletedToday }

                if !upNext.isEmpty {
                    sectionHeader("Up Next", subtitle: "\(upNext.count) remaining")
                    ForEach(upNext) { habit in
                        HabitRow(
                            habit: habit,
                            isPhaseGood: viewModel.isPhaseGoodFor(category: habit.category),
                            onToggle: {
                                Task { await viewModel.toggleHabitCompletion(habit) }
                            },
                            onDelete: {
                                viewModel.deleteHabit(habit)
                            }
                        )
                    }
                }

                if !completed.isEmpty {
                    sectionHeader("Completed", subtitle: "Nice work")
                        .padding(.top, 6)
                    ForEach(completed) { habit in
                        HabitRow(
                            habit: habit,
                            isPhaseGood: viewModel.isPhaseGoodFor(category: habit.category),
                            onToggle: {
                                Task { await viewModel.toggleHabitCompletion(habit) }
                            },
                            onDelete: {
                                viewModel.deleteHabit(habit)
                            }
                        )
                    }
                }
            }
        }
    }
    
    private var emptyHabitsCard: some View {
        CardView {
            VStack(spacing: 16) {
                Image(systemName: "leaf.circle")
                    .font(.system(.largeTitle))
                    .foregroundStyle(Color.textSecondary)
                
                Text("ui.habits.2".localized)
                    .font(.headline)
                
                Text("ui.habits.3".localized)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
                
                VStack(spacing: 10) {
                    Text("ui.habits.4".localized)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color.textSecondary)

                    HStack(spacing: 10) {
                        quickTemplateButton(title: "Exercise", emoji: "🏃", name: "Daily Exercise", category: "exercise")
                        quickTemplateButton(title: "Meditate", emoji: "🧘", name: "10m Meditation", category: "meditation")
                        quickTemplateButton(title: "Journal", emoji: "✨", name: "Gratitude Journal", category: "spiritual")
                    }
                }

                Button {
                    showCreateSheet = true
                } label: {
                    HStack {
                        Image(systemName: "plus")
                        Text("ui.habits.5".localized)
                    }
                    .font(.subheadline.bold())
                    .foregroundStyle(.white)
                    .padding(.horizontal, 20)
                    .padding(.vertical, 10)
                        .background(Capsule().fill(.purple))
                }
                .buttonStyle(AccessibleButtonStyle())
                .accessibilityHint("Opens the create habit form")
            }
            .frame(maxWidth: .infinity)
            .padding()
        }
    }

    private func sectionHeader(_ title: String, subtitle: String) -> some View {
        HStack {
            Text(title)
                .font(.headline)
            Spacer()
            Text(subtitle)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
        }
        .padding(.horizontal, 4)
    }

    private func quickTemplateButton(title: String, emoji: String, name: String, category: String) -> some View {
        Button {
            Task {
                _ = await viewModel.createHabit(name: name, category: category)
            }
        } label: {
            VStack(spacing: 6) {
                Text(emoji)
                    .font(.title3)
                Text(title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.primary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.white.opacity(0.10))
            )
        }
        .buttonStyle(AccessibleButtonStyle())
        .accessibilityLabel("Quick add \(title)")
        .accessibilityHint("Creates the \(name) habit")
    }
    
    // MARK: - Helpers
    
    private func habitEmoji(for category: String) -> String {
        let emojis: [String: String] = [
            "exercise": "🏃",
            "meditation": "🧘",
            "learning": "📚",
            "creative": "🎨",
            "social": "👥",
            "productivity": "💼",
            "health": "🥗",
            "rest": "😴",
            "financial": "💰",
            "spiritual": "✨"
        ]
        return emojis[category] ?? "✅"
    }
}

// MARK: - Habit Row

struct HabitRow: View {
    let habit: LocalHabit
    let isPhaseGood: Bool
    let onToggle: () -> Void
    let onDelete: () -> Void
    
    @State private var offset: CGFloat = 0
    
    var body: some View {
        ZStack(alignment: .trailing) {
            // Delete background
            HStack {
                Spacer()
                Button(action: onDelete) {
                    Image(systemName: "trash.fill")
                        .foregroundStyle(.white)
                        .padding()
                        .background(Circle().fill(.red))
                }
                .buttonStyle(AccessibleButtonStyle())
                .accessibilityLabel("Delete \(habit.name)")
                .accessibilityHint("Removes this habit")
                .padding(.trailing, 16)
            }
            
            // Main row
            HStack(spacing: 12) {
                // Completion button
                Button(action: onToggle) {
                    ZStack {
                        Circle()
                            .stroke(habit.isCompletedToday ? Color.green : Color.borderSubtle, lineWidth: 2)
                            .frame(width: 36, height: 36)
                        
                        if habit.isCompletedToday {
                            Circle()
                                .fill(Color.green)
                                .frame(width: 28, height: 28)
                            Image(systemName: "checkmark")
                                .font(.caption.bold())
                                .foregroundStyle(.white)
                        }
                    }
                }
                .buttonStyle(AccessibleButtonStyle())
                .accessibilityLabel(habit.name)
                .accessibilityValue(habit.isCompletedToday ? "tern.habits.2a".localized : "tern.habits.2b".localized)
                .accessibilityHint("Toggles completion for this habit")
                
                // Emoji
                Text(habit.emoji)
                    .font(.title2)
                
                // Details
                VStack(alignment: .leading, spacing: 2) {
                    HStack {
                        Text(habit.name)
                            .font(.subheadline.bold())
                            .strikethrough(habit.isCompletedToday, color: .secondary)
                        
                        if isPhaseGood {
                            Image(systemName: "moon.stars.fill")
                                .font(.meta)
                                .foregroundStyle(.purple)
                        }
                    }
                    
                    HStack(spacing: 8) {
                        // Streak
                        HStack(spacing: 2) {
                            Image(systemName: "flame.fill")
                                .foregroundStyle(.orange)
                            Text("\(habit.currentStreak)")
                        }
                        .font(.meta)
                        
                        // Completion rate
                        Text("\(Int(habit.completionRate * 100))%")
                            .font(.meta)
                            .foregroundStyle(Color.textSecondary)
                    }
                }
                
                Spacer()
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(.ultraThinMaterial)
            )
            .contentShape(Rectangle())
            .onTapGesture {
                onToggle()
            }
            .offset(x: offset)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        if value.translation.width < 0 {
                            offset = value.translation.width
                        }
                    }
                    .onEnded { value in
                        withAnimation(.spring()) {
                            if value.translation.width < -100 {
                                offset = -80
                            } else {
                                offset = 0
                            }
                        }
                    }
            )
        }
    }
}

// MARK: - Stat Card

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundStyle(color)
            
            Text(value)
                .font(.title2.bold())
            
            Text(title)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(.ultraThinMaterial)
        )
    }
}

// MARK: - Progress Ring

struct ProgressRing: View {
    let progress: Double

    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.white.opacity(0.18), lineWidth: 2)
            Circle()
                .trim(from: 0, to: max(0, min(1, progress)))
                .stroke(Color.purple, style: StrokeStyle(lineWidth: 2, lineCap: .round))
                .rotationEffect(.degrees(-90))
        }
        .accessibilityLabel("Progress")
    }
}

// MARK: - Today Progress

struct TodayProgressView: View {
    let title: String
    let completed: Int
    let total: Int

    private var progress: Double {
        guard total > 0 else { return 0 }
        return Double(completed) / Double(total)
    }

    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text(title)
                        .font(.headline)
                    Spacer()
                    Text(total > 0 ? "\(completed)/\(total)" : "0/0")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color.textSecondary)
                }

                ProgressView(value: progress)
                    .tint(.purple)
                    .scaleEffect(x: 1, y: 1.15, anchor: .center)

                Text(total > 0 ? (completed >= total ? "tern.habits.3a".localized : "tern.habits.3b".localized) : "Create a habit to start tracking.")
                    .font(.label)
                    .foregroundStyle(Color.textSecondary)
            }
        }
    }
}

// MARK: - Celebration Banner

struct CelebrationBannerView: View {
    let title: String
    let subtitle: String

    @State private var animate = false

    var body: some View {
        VStack {
            HStack(spacing: 12) {
                Image(systemName: "sparkles")
                    .foregroundStyle(.yellow)
                    .symbolEffect(.pulse, value: animate)

                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.subheadline.weight(.semibold))
                    Text(subtitle)
                        .font(.label)
                        .foregroundStyle(Color.textSecondary)
                }

                Spacer()

                Image(systemName: "checkmark.seal.fill")
                    .foregroundStyle(.green)
                    .symbolEffect(.bounce, value: animate)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .strokeBorder(Color.purple.opacity(0.25), lineWidth: 1)
                    )
            )
            .padding(.horizontal)

            Spacer()
        }
        .onAppear {
            animate = true
        }
    }
}

// MARK: - Create Habit Sheet

struct CreateHabitSheet: View {
    @Bindable var viewModel: HabitsVM
    @Binding var isPresented: Bool
    
    @State private var name = ""
    @State private var selectedCategory = "meditation"
    @State private var description = ""
    @State private var isCreating = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.opacity(0.95).ignoresSafeArea()
                
                Form {
                    Section("ui.habits.11".localized) {
                        TextField("ui.habits.8".localized, text: $name)
                        
                        Picker("ui.habits.10".localized, selection: $selectedCategory) {
                            ForEach(LocalHabitCategory.fallbackCategories) { cat in
                                HStack {
                                    Text(cat.emoji)
                                    Text(cat.name)
                                }
                                .tag(cat.id)
                            }
                        }
                        
                        TextField("ui.habits.9".localized, text: $description, axis: .vertical)
                            .lineLimit(2...4)
                    }
                    
                    Section {
                        if let guidance = viewModel.lunarGuidance {
                            HStack {
                                Text(guidance.emoji)
                                VStack(alignment: .leading) {
                                    Text(String(format: "fmt.habits.0".localized, "\(guidance.phaseName)"))
                                        .font(.subheadline)
                                    Text(guidance.theme)
                                        .font(.label)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }
                            
                            if guidance.idealHabits.contains(selectedCategory) {
                                Label("ui.habits.7".localized, systemImage: "checkmark.circle.fill")
                                    .foregroundStyle(.green)
                                    .font(.label)
                            }
                        }
                    } header: {
                        Text("ui.habits.6".localized)
                    }
                }
                .scrollContentBackground(.hidden)
            }
            .navigationTitle("screen.newHabit".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("action.cancel".localized) {
                        isPresented = false
                    }
                }
                
                ToolbarItem(placement: .confirmationAction) {
                    Button("action.create".localized) {
                        Task {
                            isCreating = true
                            let success = await viewModel.createHabit(
                                name: name,
                                category: selectedCategory,
                                description: description
                            )
                            isCreating = false
                            if success {
                                isPresented = false
                            }
                        }
                    }
                    .disabled(name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isCreating)
                }
            }
        }
        .presentationDetents([.medium, .large])
    }
}

// MARK: - Preview

#Preview {
    HabitsView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
