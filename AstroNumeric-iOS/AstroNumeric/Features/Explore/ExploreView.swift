// ExploreView.swift
// Consolidated discovery view for Tools, Learn, Relationships, Habits

import SwiftUI

struct ExploreView: View {
    @Environment(AppStore.self) private var store
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @State private var selectedCategory: ExploreCategory = .tools
    @State private var searchText = ""
    private var progressManager = LearningProgressManager.shared

    private var exploreToolColumns: [GridItem] {
        if dynamicTypeSize.isAccessibilitySize { return [GridItem(.flexible())] }
        if horizontalSizeClass == .regular { return Array(repeating: GridItem(.flexible(), spacing: 16), count: 3) }
        return [GridItem(.flexible()), GridItem(.flexible())]
    }
    
    enum ExploreCategory: CaseIterable {
        case tools
        case learn
        case habits
        case relationships

        var title: String {
            switch self {
            case .tools: return "explore.category.tools".localized
            case .learn: return "explore.category.learn".localized
            case .habits: return "explore.category.habits".localized
            case .relationships: return "explore.category.relationships".localized
            }
        }
        
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
                    PremiumScreenHeader(
                        eyebrow: "hero.explore.eyebrow".localized,
                        title: "hero.explore.title".localized,
                        subtitle: "hero.explore.body".localized,
                        accent: .accentPrimary,
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
                        Group {
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
                        // Same width rule for every category (it used to apply
                        // to Relationships only, so wide screens shifted).
                        .readableContainer()
                    }
                    // Switching category used to spring-animate one list into
                    // another of a different height, from the old scroll offset,
                    // which read as the page jumping. Each category now starts
                    // at its own top and swaps instantly; the chip still animates.
                    .id(selectedCategory)
                    .transaction(value: selectedCategory) { $0.animation = nil }
                }
            }
            .navigationTitle("nav.explore".localized)
            .navigationBarTitleDisplayMode(.inline)
            .searchable(text: $searchText, prompt: String(format: "fmt.explore.search".localized, selectedCategory.title.lowercased()))
        }
    }
    
    // MARK: - Category Picker
    
    private var categoryPicker: some View {
        ScrollViewReader { proxy in
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(ExploreCategory.allCases, id: \.self) { category in
                        CategoryChip(
                            title: category.title,
                            icon: category.icon,
                            color: category.color,
                            isSelected: selectedCategory == category
                        ) {
                            withAnimation(.spring(duration: 0.3)) {
                                selectedCategory = category
                                // Bring the chosen chip fully into view; the last
                                // one ("Relationships") stayed cut off at the edge.
                                proxy.scrollTo(category, anchor: .center)
                            }
                            HapticManager.impact(.light)
                        }
                        .id(category)
                    }
                }
                .padding(.vertical, 8)
            }
        }
    }
    
    // MARK: - Tools Content
    
    private var filteredToolItems: [ExploreToolItem] {
        // Everyone gets the Oracle: it answers on the device from the live sky,
        // and only the owner's device (with the AI code) adds the AI reading.
        let oracle = ExploreToolItem(title: "Oracle", icon: "questionmark.circle.fill", color: .blue, description: "Yes/no guidance from the Moon, the planetary hour and live transits.", provenance: AIAvailability.shared.isEnabled ? .hybrid : .calculated, destination: AnyView(OracleView()))
        let all: [ExploreToolItem] = [oracle] + [
            ExploreToolItem(title: "Affirmation", icon: "star.fill", color: .orange, description: "Supportive language tuned to today's mood.", provenance: .interpretive, destination: AnyView(AffirmationView())),
            ExploreToolItem(title: "Moon Phase", icon: "moon.fill", color: .indigo, description: "Current lunar phase, sign, and ritual timing.", provenance: .calculated, destination: AnyView(MoonPhaseView())),
            ExploreToolItem(title: "Timing", icon: "clock.badge.checkmark", color: .green, description: "Activity windows scored from the live sky.", provenance: .calculated, destination: AnyView(TimingAdvisorView())),
            ExploreToolItem(title: "Daily Guide", icon: "sparkles", color: .yellow, description: "Personal day, moon phase, retrogrades, and cues.", provenance: .calculated, destination: AnyView(DailyFeaturesView())),
            ExploreToolItem(title: "Journal", icon: "book.closed.fill", color: .purple, description: "Track outcomes against your readings.", provenance: nil, destination: AnyView(JournalView())),
            ExploreToolItem(title: "Notifications", icon: "bell.badge.fill", color: .orange, description: "Manage reminder and moon alert timing.", provenance: nil, destination: AnyView(NotificationSettingsView())),
            ExploreToolItem(title: "Year Ahead", icon: "calendar", color: .blue, description: "Long-range forecast from your solar and numerology cycle.", provenance: .calculated, destination: AnyView(YearAheadView())),
            ExploreToolItem(title: "Moon Events", icon: "moon.stars.fill", color: .indigo, description: "Upcoming lunar phases with exact timing.", provenance: .calculated, destination: AnyView(MoonEventsView())),
            ExploreToolItem(title: "Birthstone", icon: "diamond.fill", color: .mint, description: "Stones, signs, meanings, and practical ways to work with them.", provenance: .interpretive, destination: AnyView(BirthstoneGuidanceView())),
            ExploreToolItem(title: "Temporal Matrix", icon: "point.3.connected.trianglepath.dotted", color: .cyan, description: "A structured view of current life phase, cycles, and timing signals.", provenance: .hybrid, destination: AnyView(TemporalMatrixView())),
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
                LazyVGrid(columns: exploreToolColumns, spacing: 16) {
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
        .floatingAIButtonClearance()
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
                            lessonCount: LearningTrack.astrology101LessonIds.count,
                            progress: progressManager.progress(for: LearningTrack.astrology101LessonIds),
                            color: .purple
                        )

                        LearningTrackCard(
                            title: "Signs & Elements",
                            emoji: "🌗",
                            lessonCount: LearningTrack.signsAndElementsLessonIds.count,
                            progress: progressManager.progress(for: LearningTrack.signsAndElementsLessonIds),
                            color: .indigo
                        )

                        LearningTrackCard(
                            title: "Numerology Basics",
                            emoji: "🔢",
                            lessonCount: LearningTrack.numerologyBasicsLessonIds.count,
                            progress: progressManager.progress(for: LearningTrack.numerologyBasicsLessonIds),
                            color: .blue
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
            .buttonStyle(ScaleButtonStyle())
            .padding(.horizontal)
        }
        .padding(.vertical)
        .floatingAIButtonClearance()
    }
    
    // MARK: - Habits Content
    
    private var habitsContent: some View {
        VStack(spacing: 16) {
            // (A stats row here showed hard-coded 7 / 4 / 85% to everyone;
            // the real numbers are in HabitsView below.)

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
            .buttonStyle(ScaleButtonStyle())
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
        .floatingAIButtonClearance()
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
            .buttonStyle(ScaleButtonStyle())
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
            .buttonStyle(ScaleButtonStyle())
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
        .floatingAIButtonClearance()
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
        .buttonStyle(ScaleButtonStyle())
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
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
        .buttonStyle(ScaleButtonStyle())
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
                    .multilineTextAlignment(.center)
                    .fixedSize(horizontal: false, vertical: true)
            }
            // Full height of the grid row, so neighbouring cards line up.
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(.ultraThinMaterial)
            )
        }
        .buttonStyle(ScaleButtonStyle())
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
        // Same size for every track: a two-line title made one card taller
        // and offset from its neighbours.
        .frame(width: 150, height: 150, alignment: .topLeading)
        .background(
            RoundedRectangle(cornerRadius: 16)
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
            
            // Reserve the same lines on every card so the row lines up.
            Text(title)
                .font(.subheadline.weight(.semibold))
                .lineLimit(2, reservesSpace: true)

            Text(tip)
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
                .lineLimit(4, reservesSpace: true)
        }
        .padding()
        .frame(width: 160, alignment: .topLeading)
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
