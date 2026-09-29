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
                    PremiumScreenHeader(
                        eyebrow: module.difficulty.capitalized,
                        title: module.title,
                        subtitle: module.description,
                        accent: .accentPrimary,
                        chips: [module.formattedDuration, module.category.capitalized]
                    )

                    LessonBody(content: module.content)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(
                            RoundedRectangle(cornerRadius: 16)
                                .fill(.ultraThinMaterial)
                        )
                    
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



/// Renders lesson text: blank-line-separated blocks, where a block starting
/// "## " is a heading, a block of "• " lines is a bullet list, and anything
/// else is a paragraph. (lessons.json uses exactly this markup.)
struct LessonBody: View {
    let content: String

    private enum Block: Hashable {
        case heading(String)
        case bullets([String])
        case paragraph(String)
    }

    private var blocks: [Block] {
        content.components(separatedBy: "\n\n").compactMap { raw in
            let block = raw.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !block.isEmpty else { return nil }
            if block.hasPrefix("## ") {
                return .heading(String(block.dropFirst(3)))
            }
            let lines = block.components(separatedBy: "\n")
            if lines.allSatisfy({ $0.hasPrefix("• ") }) {
                return .bullets(lines.map { String($0.dropFirst(2)) })
            }
            return .paragraph(block)
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            ForEach(Array(blocks.enumerated()), id: \.offset) { _, block in
                switch block {
                case .heading(let text):
                    Text(text)
                        .font(.headline)
                        .foregroundStyle(Color.textPrimary)
                        .padding(.top, 6)
                        .accessibilityAddTraits(.isHeader)
                case .bullets(let items):
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(Array(items.enumerated()), id: \.offset) { _, item in
                            HStack(alignment: .firstTextBaseline, spacing: 8) {
                                Text("•")
                                Text(item)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                    .font(.body)
                    .foregroundStyle(Color.textSecondary)
                case .paragraph(let text):
                    Text(text)
                        .font(.body)
                        .foregroundStyle(Color.textSecondary)
                        .lineSpacing(6)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
