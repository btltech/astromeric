// LearnView.swift
// Educational content hub - Astrology & Numerology lessons

import SwiftUI

struct LearnView: View {
    @State private var viewModel = LearnVM()
    @State private var selectedModule: LearningModule?
    @State private var showGlossary = false
    @State private var columnVisibility: NavigationSplitViewVisibility = .doubleColumn

    var body: some View {
        NavigationSplitView(columnVisibility: $columnVisibility) {
            sidebar
                .navigationTitle("screen.learn".localized)
                .navigationBarTitleDisplayMode(.inline)
                .task { await viewModel.fetchModules() }
                .sheet(isPresented: $showGlossary) {
                    GlossaryView()
                }
        } detail: {
            NavigationStack {
                if let module = selectedModule {
                    LessonDetailView(module: module)
                } else {
                    ContentUnavailableView(
                        "Pick a lesson",
                        systemImage: "book",
                        description: Text("ui.learn.0".localized)
                    )
                }
            }
        }
        .navigationSplitViewStyle(.balanced)
    }

    private var sidebar: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()

            ScrollView {
                VStack(spacing: 24) {
                    PremiumHeroCard(
                            eyebrow: "hero.learn.eyebrow".localized,
                            title: "hero.learn.title".localized,
                            bodyText: "hero.learn.body".localized,
                            accent: [Color(hex: "142341"), Color(hex: "315cc4"), Color(hex: "4e8ea3")],
                            chips: ["hero.learn.chip.0".localized, "hero.learn.chip.1".localized, "hero.learn.chip.2".localized]
                        )

                    // Glossary shortcut (clarifies reading terminology)
                    Button {
                        showGlossary = true
                    } label: {
                        CardView {
                            HStack(spacing: 12) {
                                Image(systemName: "text.book.closed")
                                    .font(.title2)
                                    .foregroundStyle(.purple)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("ui.learn.1".localized)
                                        .font(.headline)
                                    Text("ui.learn.2".localized)
                                        .font(.caption)
                                        .foregroundStyle(Color.textSecondary)
                                }
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                    }
                    .buttonStyle(.plain)

                    PremiumSectionHeader(
                title: "section.learn.0.title".localized,
                subtitle: "section.learn.0.subtitle".localized
            )

                    // Category picker
                    categoryPicker

                    // Lessons section
                    lessonsSection
                }
                .padding()
                .readableContainer()
            }
        }
    }
    
    private var categoryPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(viewModel.categories, id: \.id) { category in
                    categoryChip(category)
                }
            }
        }
    }
    
    private func categoryChip(_ category: (id: String, title: String, icon: String)) -> some View {
        Button {
            withAnimation(.spring(duration: 0.3)) {
                viewModel.switchCategory(category.id)
            }
        } label: {
            HStack(spacing: 6) {
                Image(systemName: category.icon)
                Text(category.title)
            }
            .font(.subheadline.weight(.medium))
            .foregroundStyle(viewModel.selectedCategory == category.id ? .white : Color.textSecondary)
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .frame(minHeight: 44)
            .background(
                Capsule()
                    .fill(viewModel.selectedCategory == category.id ? Color.purple : Color.white.opacity(0.1))
            )
        }
        .buttonStyle(AccessibleButtonStyle())
        .accessibilityLabel(category.title)
        .accessibilityValue(viewModel.selectedCategory == category.id ? "tern.learn.0a".localized : "tern.learn.0b".localized)
        .accessibilityHint("Filters lessons by category")
    }
    
    private var lessonsSection: some View {
        Group {
            if viewModel.isLoading && viewModel.modules.isEmpty {
                VStack(spacing: 16) {
                    ForEach(0..<3, id: \.self) { _ in
                        SkeletonCard()
                    }
                }
            } else if viewModel.modules.isEmpty {
                CardView {
                    VStack(spacing: 12) {
                        Image(systemName: "book.closed")
                            .font(.largeTitle)
                            .foregroundStyle(Color.textSecondary)
                        Text("ui.learn.3".localized)
                            .foregroundStyle(Color.textSecondary)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                }
            } else {
                LazyVStack(spacing: 16) {
                    ForEach(viewModel.modules) { module in
                        Button {
                            selectedModule = module
                        } label: {
                            LessonCard(module: module)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
    }
}

// MARK: - Lesson Card

struct LessonCard: View {
    let module: LearningModule
    
    var body: some View {
        HStack(spacing: 16) {
            // Icon
            ZStack {
                Circle()
                    .fill(Color.purple.opacity(0.2))
                    .frame(width: 50, height: 50)
                
                Image(systemName: module.icon)
                    .font(.title3)
                    .foregroundStyle(.purple)
            }
            
            // Content
            VStack(alignment: .leading, spacing: 4) {
                Text(module.title)
                    .font(.headline)
                    .foregroundStyle(.primary)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(module.description)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
                
                // Difficulty badge
                HStack(spacing: 8) {
                    Text(module.difficulty.capitalized)
                        .font(.caption2)
                        .foregroundStyle(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(difficultyColor.opacity(0.8))
                        .clipShape(Capsule())
                    
                    Text(module.formattedDuration)
                        .font(.caption2)
                        .foregroundStyle(Color.textSecondary)
                }
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundStyle(Color.textSecondary)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color.white.opacity(0.08), lineWidth: 1)
                )
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(module.title)
        .accessibilityHint(module.description)
    }
    
    private var difficultyColor: Color {
        switch module.difficulty.lowercased() {
        case "beginner": return .green
        case "intermediate": return .orange
        case "advanced": return .red
        default: return Color.textMuted
        }
    }
}

// MARK: - Flow Layout for Keywords

struct FlowLayout: Layout {
    var spacing: CGFloat = 8
    
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(in: proposal.width ?? 0, subviews: subviews, spacing: spacing)
        return result.size
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(in: bounds.width, subviews: subviews, spacing: spacing)
        for (index, subview) in subviews.enumerated() {
            subview.place(at: CGPoint(x: bounds.minX + result.positions[index].x, y: bounds.minY + result.positions[index].y), proposal: .unspecified)
        }
    }
    
    struct FlowResult {
        var size: CGSize = .zero
        var positions: [CGPoint] = []
        
        init(in maxWidth: CGFloat, subviews: Subviews, spacing: CGFloat) {
            var currentPosition = CGPoint.zero
            var lineHeight: CGFloat = 0
            
            for subview in subviews {
                let size = subview.sizeThatFits(.unspecified)
                
                if currentPosition.x + size.width > maxWidth, currentPosition.x > 0 {
                    currentPosition.x = 0
                    currentPosition.y += lineHeight + spacing
                    lineHeight = 0
                }
                
                positions.append(currentPosition)
                lineHeight = max(lineHeight, size.height)
                currentPosition.x += size.width + spacing
                
                self.size.width = max(self.size.width, currentPosition.x - spacing)
                self.size.height = currentPosition.y + lineHeight
            }
        }
    }
}

// MARK: - Preview

#Preview {
    LearnView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
