// SectionGridView.swift
// Grid display of reading sections

import SwiftUI

struct SectionGridView: View {
    let sections: [ReadingSection]
    
    @State private var expandedSection: String?
    
    var body: some View {
        VStack(spacing: 12) {
            ForEach(sections) { section in
                SectionCardView(
                    section: section,
                    isExpanded: expandedSection == section.id
                ) {
                    withAnimation(.spring(response: 0.3)) {
                        if expandedSection == section.id {
                            expandedSection = nil
                        } else {
                            expandedSection = section.id
                        }
                    }
                    HapticManager.impact(.light)
                }
            }
        }
    }
}

// MARK: - Section Card View

struct SectionCardView: View {
    let section: ReadingSection
    let isExpanded: Bool
    let onTap: () -> Void
    
    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                // Header (always visible)
                Button(action: onTap) {
                    HStack {
                        ZStack {
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.purple.opacity(0.14))
                                .frame(width: 40, height: 40)
                            Text(section.icon ?? "✨")
                                .font(.title3)
                        }
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text(section.title)
                                .font(.headline)
                            Text(isExpanded ? "tern.sectionGrid.0a".localized : "tern.sectionGrid.0b".localized)
                                .font(.caption2)
                                .foregroundStyle(Color.textSecondary)
                        }
                        
                        Spacer()
                        
                        Image(systemName: isExpanded ? "tern.sectionGrid.1a".localized : "tern.sectionGrid.1b".localized)
                            .font(.caption)
                            .foregroundStyle(Color.subtleText)
                    }
                }
                .buttonStyle(.plain)
                
                // Expanded content
                if isExpanded {
                    VStack(alignment: .leading, spacing: 8) {
                        // Highlights
                        if let highlights = section.highlights {
                            ForEach(highlights, id: \.self) { highlight in
                                HStack(alignment: .top, spacing: 8) {
                                    Text("•")
                                        .foregroundStyle(.purple)
                                    Text(highlight)
                                        .font(.subheadline)
                                        .foregroundStyle(Color.textMuted)
                                }
                            }
                        }
                        
                        // Full text
                        if let text = section.text {
                            Text(text)
                                .font(.subheadline)
                                .foregroundStyle(Color.textSecondary)
                                .padding(.top, 4)
                        }
                    }
                    .transition(.opacity.combined(with: .move(edge: .top)))
                }
            }
        }
    }
}

// MARK: - Preview

#Preview {
    ScrollView {
        SectionGridView(sections: [
            ReadingSection(
                title: "Love & Relationships",
                icon: "❤️",
                highlights: [
                    "Venus favors meaningful connections today",
                    "Good time for heart-to-heart conversations"
                ],
                text: "Romance is in the air as Venus aspects your chart favorably."
            ),
            ReadingSection(
                title: "Career & Finance",
                icon: "💼",
                highlights: [
                    "Focus on long-term planning",
                    "Avoid major financial decisions"
                ],
                text: nil
            ),
            ReadingSection(
                title: "Health & Wellness",
                icon: "💪",
                highlights: [
                    "Energy levels are high",
                    "Good day for physical activity"
                ],
                text: nil
            )
        ])
        .padding()
    }
    .background(Color.black)
    .preferredColorScheme(.dark)
}
