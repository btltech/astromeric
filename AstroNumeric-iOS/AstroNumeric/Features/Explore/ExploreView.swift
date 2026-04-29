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

    private struct ExploreToolItem: Identifiable {
        let title: String
        let icon: String
        let color: Color
        let description: String
        let provenance: FeatureProvenance?
        let destination: AnyView

        var id: String { title }
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    PremiumHeroCard(
                            eyebrow: "hero.explore.eyebrow".localized,
                            title: "hero.explore.title".localized,
                            bodyText: "hero.explore.body".localized,
                            accent: [Color(hex: "1f1038"), Color(hex: "5f35b5"), Color(hex: "0f7c8a")],
                            chips: ["hero.explore.chip.0".localized, "hero.explore.chip.1".localized, "hero.explore.chip.2".localized, "hero.explore.chip.3".localized]
                        )
                    .padding(.horizontal)
                    .padding(.top, 8)

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
                            .readableContainer()
                        }
                    }
                }
            }
            .navigationTitle("nav.explore".localized)
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
    
    private var filteredToolItems: [ExploreToolItem] {
        let all: [ExploreToolItem] = [
            ExploreToolItem(title: "Oracle", icon: "questionmark.circle.fill", color: .blue, description: "Yes/no guidance using your day number and moon phase.", provenance: .hybrid, destination: AnyView(OracleView())),
            ExploreToolItem(title: "Affirmation", icon: "star.fill", color: .orange, description: "Supportive language tuned to today's mood.", provenance: .interpretive, destination: AnyView(AffirmationView())),
            ExploreToolItem(title: "Moon Phase", icon: "moon.fill", color: .indigo, description: "Current lunar phase, sign, and ritual timing.", provenance: .calculated, destination: AnyView(MoonPhaseView())),
            ExploreToolItem(title: "Timing", icon: "clock.badge.checkmark", color: .green, description: "Activity windows scored from the live sky.", provenance: .calculated, destination: AnyView(TimingAdvisorView())),
            ExploreToolItem(title: "Daily Guide", icon: "sparkles", color: .yellow, description: "Personal day, moon phase, retrogrades, and cues.", provenance: .calculated, destination: AnyView(DailyFeaturesView())),
            ExploreToolItem(title: "Journal", icon: "book.closed.fill", color: .purple, description: "Track outcomes against your readings.", provenance: nil, destination: AnyView(JournalView())),
            ExploreToolItem(title: "Notifications", icon: "bell.badge.fill", color: .orange, description: "Manage reminder and moon alert timing.", provenance: nil, destination: AnyView(NotificationSettingsView())),
            ExploreToolItem(title: "Year Ahead", icon: "calendar", color: .blue, description: "Long-range forecast from your solar and numerology cycle.", provenance: .calculated, destination: AnyView(YearAheadView())),
            ExploreToolItem(title: "Moon Events", icon: "moon.stars.fill", color: .indigo, description: "Upcoming lunar phases with exact timing.", provenance: .calculated, destination: AnyView(MoonEventsView())),
            ExploreToolItem(title: "Life Phase", icon: "arrow.trianglehead.clockwise", color: Color(hue: 0.57, saturation: 0.7, brightness: 0.9), description: "Your current cycle interpreted from annual timing.", provenance: .hybrid, destination: AnyView(YearAheadView())),
        ]
        if searchText.isEmpty { return all }
        let q = searchText.lowercased()
        return all.filter { $0.title.lowercased().contains(q) || $0.description.lowercased().contains(q) }
    }
    
    private var toolsContent: some View {
        VStack(spacing: 20) {
            PremiumSectionHeader(
                title: "section.explore.0.title".localized,
                subtitle: "section.explore.0.subtitle".localized
            )
            .padding(.horizontal)

            // Featured tool — hide when filtering
            if searchText.isEmpty {
                FeaturedToolCard(
                    title: "Daily Tarot",
                    subtitle: "Interpretive card pull for symbolic reflection",
                    icon: "suit.spade.fill",
                    gradient: [.purple, .pink],
                    provenance: .interpretive
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
                    Text(String(format: "fmt.explore.1".localized, "\(searchText)"))
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
                            description: item.description,
                            provenance: item.provenance
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
            PremiumSectionHeader(
                title: "section.explore.1.title".localized,
                subtitle: "section.explore.1.subtitle".localized
            )
            .padding(.horizontal)

            // Learning tracks
            VStack(alignment: .leading, spacing: 12) {
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
                            Text("ui.explore.0".localized)
                                .font(.headline)
                            Text("ui.explore.1".localized)
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
                            Text("ui.explore.2".localized)
                                .font(.headline)
                            Text("ui.explore.3".localized)
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
                Text("ui.explore.4".localized)
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
                            Text("ui.explore.5".localized)
                                .font(.headline)
                            Text("ui.explore.6".localized)
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
                            Text("ui.explore.7".localized)
                                .font(.headline)
                            Text("ui.explore.8".localized)
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
                Text("ui.explore.9".localized)
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
    let provenance: FeatureProvenance?
    @ViewBuilder let destination: () -> Destination

    init(
        title: String,
        subtitle: String,
        icon: String,
        gradient: [Color],
        provenance: FeatureProvenance? = nil,
        @ViewBuilder destination: @escaping () -> Destination
    ) {
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.gradient = gradient
        self.provenance = provenance
        self.destination = destination
    }
    
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
                    if let provenance {
                        FeatureProvenanceBadge(provenance: provenance, compact: true)
                    }
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
    let provenance: FeatureProvenance?
    @ViewBuilder let destination: () -> Destination

    init(
        title: String,
        icon: String,
        color: Color,
        description: String,
        provenance: FeatureProvenance? = nil,
        @ViewBuilder destination: @escaping () -> Destination
    ) {
        self.title = title
        self.icon = icon
        self.color = color
        self.description = description
        self.provenance = provenance
        self.destination = destination
    }
    
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

                if let provenance {
                    FeatureProvenanceBadge(provenance: provenance, compact: true)
                }
                
                Text(description)
                    .font(.label)
                    .foregroundStyle(Color.textSecondary)
                    .lineLimit(3)
                    .multilineTextAlignment(.center)
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
            
            Text(String(format: "fmt.explore.0".localized, "\(lessonCount)"))
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
