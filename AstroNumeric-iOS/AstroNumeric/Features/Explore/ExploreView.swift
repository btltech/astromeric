// ExploreView.swift
// Consolidated discovery view for Tools, Learn, Relationships, Habits

import SwiftUI

struct ExploreView: View {
    @Environment(AppStore.self) private var store
    @State private var selectedCategory: ExploreCategory = .tools
    @State private var searchText = ""
    private var progressManager = LearningProgressManager.shared
    
    enum ExploreCategory: String, CaseIterable {
        case tools = "Tools"
        case learn = "Learn"
        case habits = "Habits"
        case relationships = "Relations"
        
        var icon: String {
            switch self {
            case .tools: return "wand.and.stars"
            case .learn: return "book.fill"
            case .habits: return "checkmark.circle.fill"
            case .relationships: return "heart.circle.fill"
            }
        }
        
        var color: Color {
            switch self {
            case .tools: return .purple
            case .learn: return .blue
            case .habits: return .green
            case .relationships: return .pink
            }
        }
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Category picker
                    categoryPicker
                        .padding(.horizontal)
                        .padding(.top, 8)
                    
                    // Content based on category
                    ScrollView {
                        switch selectedCategory {
                        case .tools:
                            toolsContent
                        case .learn:
                            learnContent
                        case .habits:
                            habitsContent
                        case .relationships:
                            relationshipsContent
                        }
                    }
                }
            }
            .navigationTitle("Explore")
            .navigationBarTitleDisplayMode(.inline)
            .searchable(text: $searchText, prompt: "Search \(selectedCategory.rawValue.lowercased())...")
        }
    }
    
    // MARK: - Category Picker
    
    private var categoryPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(ExploreCategory.allCases, id: \.self) { category in
                    CategoryChip(
                        title: category.rawValue,
                        icon: category.icon,
                        color: category.color,
                        isSelected: selectedCategory == category
                    ) {
                        withAnimation(.spring(duration: 0.3)) {
                            selectedCategory = category
                        }
                        HapticManager.impact(.light)
                    }
                }
            }
            .padding(.vertical, 8)
        }
    }
    
    // MARK: - Tools Content
    
    private var filteredToolItems: [(title: String, icon: String, color: Color, description: String, destination: AnyView)] {
        let all: [(String, String, Color, String, AnyView)] = [
            ("Oracle", "questionmark.circle.fill", .blue, "Yes/No guidance", AnyView(OracleView())),
            ("Affirmation", "star.fill", .orange, "Daily inspiration", AnyView(AffirmationView())),
            ("Moon Phase", "moon.fill", .indigo, "Lunar guidance", AnyView(MoonPhaseView())),
            ("Timing", "clock.badge.checkmark", .green, "Best time for activities", AnyView(TimingAdvisorView())),
            ("Daily Guide", "sparkles", .yellow, "Cosmic features", AnyView(DailyFeaturesView())),
            ("Journal", "book.closed.fill", .purple, "Track outcomes", AnyView(JournalView())),
            ("Notifications", "bell.badge.fill", .orange, "Daily alerts", AnyView(NotificationSettingsView())),
            ("Year Ahead", "calendar", .blue, "Solar return", AnyView(YearAheadView())),
            ("Moon Events", "moon.stars.fill", .indigo, "Upcoming phases", AnyView(MoonEventsView())),
            ("Life Phase", "arrow.trianglehead.clockwise", Color(hue: 0.57, saturation: 0.7, brightness: 0.9), "Your cosmic cycle", AnyView(YearAheadView())),
        ]
        if searchText.isEmpty { return all.map { (title: $0.0, icon: $0.1, color: $0.2, description: $0.3, destination: $0.4) } }
        let q = searchText.lowercased()
        return all.filter { $0.0.lowercased().contains(q) || $0.3.lowercased().contains(q) }
                  .map { (title: $0.0, icon: $0.1, color: $0.2, description: $0.3, destination: $0.4) }
    }
    
    private var toolsContent: some View {
        VStack(spacing: 20) {
            // Featured tool — hide when filtering
            if searchText.isEmpty {
                FeaturedToolCard(
                    title: "Daily Tarot",
                    subtitle: "Draw your card for today",
                    icon: "suit.spade.fill",
                    gradient: [.purple, .pink]
                ) {
                    TarotView()
                }
                .padding(.horizontal)
            }
            
            // Tool grid — filtered when searching
            if filteredToolItems.isEmpty {
                VStack(spacing: 12) {
                    Image(systemName: "magnifyingglass")
                        .font(.largeTitle)
                        .foregroundStyle(Color.textSecondary)
                    Text("No tools match \"\(searchText)\"")
                        .font(.subheadline)
                        .foregroundStyle(Color.textSecondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 40)
            } else {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                    ForEach(filteredToolItems, id: \.title) { item in
                        ExploreToolCard(
                            title: item.title,
                            icon: item.icon,
                            color: item.color,
                            description: item.description
                        ) {
                            item.destination
                        }
                    }
                }
                .padding(.horizontal)
            }
        }
        .padding(.vertical)
    }
    
    // MARK: - Learn Content
    
    private var learnContent: some View {
        VStack(spacing: 16) {
            // Learning tracks
            VStack(alignment: .leading, spacing: 12) {
                Text("Learning Tracks")
                    .font(.headline)
                    .padding(.horizontal)
                
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        LearningTrackCard(
                            title: "Astrology 101",
                            emoji: "⭐️",
                            lessonCount: 12,
                            progress: progressManager.progress(for: LearningTrack.astrology101LessonIds),
                            color: .purple
                        )
                        
                        LearningTrackCard(
                            title: "Numerology Basics",
                            emoji: "🔢",
                            lessonCount: 8,
                            progress: progressManager.progress(for: LearningTrack.numerologyBasicsLessonIds),
                            color: .blue
                        )
                        
                        LearningTrackCard(
                            title: "Moon Wisdom",
                            emoji: "🌙",
                            lessonCount: 6,
                            progress: progressManager.progress(for: LearningTrack.moonWisdomLessonIds),
                            color: .indigo
                        )
                        
                        LearningTrackCard(
                            title: "Tarot Mastery",
                            emoji: "🃏",
                            lessonCount: 10,
                            progress: progressManager.progress(for: LearningTrack.tarotMasteryLessonIds),
                            color: .pink
                        )
                    }
                    .padding(.horizontal)
                }
            }
            
            // Full learn view
            NavigationLink {
                LearnView()
            } label: {
                CardView {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("📚 Browse All Lessons")
                                .font(.headline)
                            Text("Explore our full library of cosmic knowledge")
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .foregroundStyle(Color.textSecondary)
                    }
                }
            }
            .buttonStyle(.plain)
            .padding(.horizontal)
        }
        .padding(.vertical)
    }
    
    // MARK: - Habits Content
    
    private var habitsContent: some View {
        VStack(spacing: 16) {
            // Stats overview
            HStack(spacing: 16) {
                StatBox(value: "7", label: "Day Streak", icon: "🔥")
                StatBox(value: "4", label: "Active", icon: "✓")
                StatBox(value: "85%", label: "Rate", icon: "📈")
            }
            .padding(.horizontal)
            
            // Full habits view
            NavigationLink {
                HabitsView()
            } label: {
                CardView {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("🌙 Lunar Habits")
                                .font(.headline)
                            Text("Track habits aligned with moon phases")
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .foregroundStyle(Color.textSecondary)
                    }
                }
            }
            .buttonStyle(.plain)
            .padding(.horizontal)
            
            // Quick habit suggestions
            VStack(alignment: .leading, spacing: 12) {
                Text("Suggested Habits")
                    .font(.headline)
                    .padding(.horizontal)
                
                VStack(spacing: 8) {
                    SuggestedHabitRow(emoji: "🧘", name: "Morning Meditation", benefit: "Inner peace")
                    SuggestedHabitRow(emoji: "📖", name: "Daily Journaling", benefit: "Self-reflection")
                    SuggestedHabitRow(emoji: "🌿", name: "Nature Walk", benefit: "Grounding")
                }
                .padding(.horizontal)
            }
        }
        .padding(.vertical)
    }
    
    // MARK: - Relationships Content
    
    private var relationshipsContent: some View {
        VStack(spacing: 16) {

            // ── NEW: Cosmic Circle (Friends chart wall) ──
            FeaturedToolCard(
                title: "Cosmic Circle",
                subtitle: "See who you're most aligned with",
                icon: "person.3.sequence.fill",
                gradient: [.pink, .purple]
            ) {
                FriendsView()
            }
            .padding(.horizontal)

            // New compatibility check
            NavigationLink {
                CompatibilityView()
            } label: {
                CardView {
                    HStack(spacing: 16) {
                        ZStack {
                            Circle()
                                .fill(
                                    LinearGradient(
                                        colors: [.pink, .purple],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(width: 50, height: 50)
                            
                            Image(systemName: "heart.fill")
                                .font(.title2)
                                .foregroundStyle(.white)
                        }
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Check Compatibility")
                                .font(.headline)
                            Text("Compare your charts with someone special")
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .foregroundStyle(Color.textSecondary)
                    }
                }
            }
            .buttonStyle(.plain)
            .padding(.horizontal)
            
            // Saved relationships
            NavigationLink {
                RelationshipsView()
            } label: {
                CardView {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("💕 Saved Relationships")
                                .font(.headline)
                            Text("View your compatibility history")
                                .font(.label)
                                .foregroundStyle(Color.textSecondary)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .foregroundStyle(Color.textSecondary)
                    }
                }
            }
            .buttonStyle(.plain)
            .padding(.horizontal)
            
            // Relationship tips
            VStack(alignment: .leading, spacing: 12) {
                Text("Cosmic Connection Tips")
                    .font(.headline)
                    .padding(.horizontal)
                
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        TipCard(
                            emoji: "🌙",
                            title: "Moon Compatibility",
                            tip: "Emotional connection flows best when Moon signs harmonize"
                        )
                        TipCard(
                            emoji: "💬",
                            title: "Mercury Matters",
                            tip: "Communication style is shown by Mercury placement"
                        )
                        TipCard(
                            emoji: "❤️",
                            title: "Venus Connection",
                            tip: "Venus shows how you give and receive love"
                        )
                    }
                    .padding(.horizontal)
                }
            }
        }
        .padding(.vertical)
    }
}

// MARK: - Supporting Views

struct CategoryChip: View {
    let title: String
    let icon: String
    let color: Color
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.label)
                Text(title)
                    .font(.subheadline.weight(.medium))
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 8)
            .frame(minHeight: 44) // Apple HIG minimum tap target
            .background(
                Capsule()
                    .fill(isSelected ? color : Color.white.opacity(0.1))
            )
            .foregroundStyle(isSelected ? .white : .primary)
        }
        .buttonStyle(.plain)
    }
}

struct FeaturedToolCard<Destination: View>: View {
    let title: String
    let subtitle: String
    let icon: String
    let gradient: [Color]
    @ViewBuilder let destination: () -> Destination
    
    var body: some View {
        NavigationLink {
            destination()
        } label: {
            HStack(spacing: 16) {
                ZStack {
                    Circle()
                        .fill(Color.white.opacity(0.2))
                        .frame(width: 60, height: 60)
                    
                    Image(systemName: icon)
                        .font(.title)
                        .foregroundStyle(.white)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.title3.bold())
                    Text(subtitle)
                        .font(.subheadline)
                        .opacity(0.8)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right.circle.fill")
                    .font(.title2)
                    .opacity(0.8)
            }
            .foregroundStyle(.white)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 20)
                    .fill(
                        LinearGradient(
                            colors: gradient,
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
            )
        }
        .buttonStyle(.plain)
    }
}

struct ExploreToolCard<Destination: View>: View {
    let title: String
    let icon: String
    let color: Color
    let description: String
    @ViewBuilder let destination: () -> Destination
    
    var body: some View {
        NavigationLink {
            destination()
        } label: {
            VStack(spacing: 12) {
                ZStack {
                    Circle()
                        .fill(color.opacity(0.2))
                        .frame(width: 50, height: 50)
                    
                    Image(systemName: icon)
                        .font(.title2)
                        .foregroundStyle(color)
                }
                
                Text(title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.primary)
                
                Text(description)
                    .font(.label)
                    .foregroundStyle(Color.textSecondary)
                    .lineLimit(1)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(.ultraThinMaterial)
            )
        }
        .buttonStyle(.plain)
    }
}

struct LearningTrackCard: View {
    let title: String
    let emoji: String
    let lessonCount: Int
    let progress: Double
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(emoji)
                .font(.largeTitle)
            
            Text(title)
                .font(.subheadline.weight(.semibold))
            
            Text("\(lessonCount) lessons")
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
            
            // Progress bar
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 2)
                        .fill(Color.white.opacity(0.2))
                    
                    RoundedRectangle(cornerRadius: 2)
                        .fill(color)
                        .frame(width: geo.size.width * progress)
                }
            }
            .frame(height: 4)
        }
        .padding()
        .frame(width: 150)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }
}

struct StatBox: View {
    let value: String
    let label: String
    let icon: String
    
    var body: some View {
        VStack(spacing: 4) {
            Text(icon)
                .font(.title2)
            Text(value)
                .font(.title2.bold())
            Text(label)
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

struct SuggestedHabitRow: View {
    let emoji: String
    let name: String
    let benefit: String
    
    var body: some View {
        HStack(spacing: 12) {
            Text(emoji)
                .font(.title2)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(name)
                    .font(.subheadline.weight(.medium))
                Text(benefit)
                    .font(.label)
                    .foregroundStyle(Color.textSecondary)
            }
            
            Spacer()
            
            Button {
                // Add habit
            } label: {
                Image(systemName: "plus.circle.fill")
                    .font(.title2)
                    .foregroundStyle(.purple)
            }
            .buttonStyle(AccessibleButtonStyle())
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(.ultraThinMaterial)
        )
    }
}

struct TipCard: View {
    let emoji: String
    let title: String
    let tip: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(emoji)
                .font(.largeTitle)
            
            Text(title)
                .font(.subheadline.weight(.semibold))
            
            Text(tip)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
                .lineLimit(3)
        }
        .padding()
        .frame(width: 160)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }
}

// MARK: - Preview

#Preview {
    ExploreView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
