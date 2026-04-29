// LessonDetailView.swift
// Detailed lesson content display

import SwiftUI

struct LessonDetailView: View {
    let module: LearningModule
    @State private var hasCompleted = false
    @State private var scrollProgress: CGFloat = 0
    
    private var progressManager: LearningProgressManager { .shared }
    
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
            
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    PremiumHeroCard(
                            eyebrow: module.difficulty.capitalized,
                            title: module.title,
                            bodyText: module.description,
                            accent: [Color(hex: "182039"), Color(hex: "4b5dbe"), Color(hex: "7b55b2")],
                            chips: [module.formattedDuration, module.category.capitalized]
                        )

                    // Header
                    headerSection
                    
                    // Content
                    contentSection
                    
                    // Keywords
                    keywordsSection
                    
                    // Complete button
                    completeButton
                }
                .padding()
            }
        }
        .navigationTitle(module.title)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            hasCompleted = progressManager.isComplete(moduleId: module.id)
        }
    }
    
    private var headerSection: some View {
        VStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.purple, .indigo],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 80, height: 80)
                
                Image(systemName: module.icon)
                    .font(.system(.largeTitle))
                    .foregroundStyle(.white)
            }
            
            Text(module.title)
                .font(.title2.bold())
                .multilineTextAlignment(.center)
            
            HStack(spacing: 16) {
                Label(module.difficulty.capitalized, systemImage: "chart.bar")
                Label(module.formattedDuration, systemImage: "clock")
            }
            .font(.caption)
            .foregroundStyle(Color.textSecondary)
        }
        .frame(maxWidth: .infinity)
    }
    
    private var contentSection: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Main Content
            PremiumSectionHeader(
                title: "section.lessonDetail.0.title".localized,
                subtitle: "section.lessonDetail.0.subtitle".localized
            )

            sectionCard(
                title: "Lesson Content",
                content: module.content
            )
        }
    }
    
    @ViewBuilder
    private var keywordsSection: some View {
        if !module.keywords.isEmpty {
            VStack(alignment: .leading, spacing: 12) {
                PremiumSectionHeader(
                title: "section.lessonDetail.1.title".localized,
                subtitle: "section.lessonDetail.1.subtitle".localized
            )
                
                FlowLayout(spacing: 8) {
                    ForEach(module.keywords, id: \.self) { keyword in
                        Text(keyword)
                            .font(.caption)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.purple.opacity(0.2))
                            .clipShape(Capsule())
                    }
                }
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(.ultraThinMaterial)
            )
        }
    }
    
    private func sectionCard(title: String, content: String) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline)
            
            Text(content)
                .font(.body)
                .foregroundStyle(Color.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
                .lineSpacing(6)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }
    
    private var completeButton: some View {
        Button {
            withAnimation(.spring()) {
                hasCompleted = true
            }
            progressManager.markComplete(moduleId: module.id)
            HapticManager.notification(.success)
        } label: {
            HStack {
                Image(systemName: hasCompleted ? "tern.lessonDetail.0a".localized : "tern.lessonDetail.0b".localized)
                Text(hasCompleted ? "tern.lessonDetail.1a".localized : "tern.lessonDetail.1b".localized)
            }
            .font(.headline)
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                Capsule()
                    .fill(hasCompleted ? Color.green : Color.purple)
            )
        }
        .disabled(hasCompleted)
        .padding(.top, 8)
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        LessonDetailView(module: LearningModule(
            id: "astro-1",
            title: "What is Astrology?",
            description: "Understanding the cosmic language",
            category: "astrology",
            difficulty: "beginner",
            durationMinutes: 5,
            content: "Astrology is an ancient practice that studies the positions and movements of celestial bodies.",
            keywords: ["astrology", "basics", "introduction"],
            relatedModules: nil
        ))
        .environment(AppStore.shared)
    }
    .preferredColorScheme(.dark)
}

