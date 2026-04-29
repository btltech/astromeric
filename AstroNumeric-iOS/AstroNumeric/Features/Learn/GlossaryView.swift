// GlossaryView.swift
// Browse key astrology/numerology terms for clarity

import SwiftUI

struct GlossaryView: View {
    @State private var entries: [GlossaryEntry] = []
    @State private var isLoading = false
    @State private var error: String?
    @State private var searchText = ""
    @State private var selectedCategory: String = "all"
    @State private var selectedEntry: GlossaryEntry?
    @State private var columnVisibility: NavigationSplitViewVisibility = .doubleColumn

    private var categories: [String] {
        let cats = Set(entries.map(\.category)).sorted()
        return ["all"] + cats
    }

    private var filteredEntries: [GlossaryEntry] {
        entries
            .filter { selectedCategory == "all" ? true : $0.category == selectedCategory }
            .filter { searchText.isEmpty ? true : ($0.term.localizedCaseInsensitiveContains(searchText) || $0.definition.localizedCaseInsensitiveContains(searchText)) }
            .sorted { $0.term.localizedCaseInsensitiveCompare($1.term) == .orderedAscending }
    }

    var body: some View {
        NavigationSplitView(columnVisibility: $columnVisibility) {
            sidebar
                .navigationTitle("screen.glossary".localized)
                .navigationBarTitleDisplayMode(.inline)
                .searchable(text: $searchText, prompt: "Search terms…")
                .task { await load() }
        } detail: {
            NavigationStack {
                if let entry = selectedEntry {
                    GlossaryDetailView(entry: entry)
                } else {
                    ContentUnavailableView(
                        "Pick a term",
                        systemImage: "book.closed",
                        description: Text("ui.glossary.0".localized)
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

            Group {
                if isLoading && entries.isEmpty {
                    VStack(spacing: 16) {
                        SkeletonCard()
                        SkeletonCard()
                    }
                    .padding()
                } else if let error, entries.isEmpty {
                    ErrorStateView(message: error) {
                        await load()
                    }
                } else {
                    ScrollView {
                        VStack(spacing: 16) {
                            PremiumHeroCard(
                            eyebrow: "hero.glossary.eyebrow".localized,
                            title: "hero.glossary.title".localized,
                            bodyText: "hero.glossary.body".localized,
                            accent: [Color(hex: "13233b"), Color(hex: "3f69bf"), Color(hex: "1f8ca3")],
                            chips: ["hero.glossary.chip.0".localized, "hero.glossary.chip.1".localized, "hero.glossary.chip.2".localized]
                        )

                            categoryPicker

                            PremiumSectionHeader(
                title: "section.glossary.0.title".localized,
                subtitle: "section.glossary.0.subtitle".localized
            )

                            ForEach(filteredEntries) { entry in
                                Button {
                                    selectedEntry = entry
                                } label: {
                                    CardView {
                                        VStack(alignment: .leading, spacing: 8) {
                                            HStack {
                                                Text(entry.term)
                                                    .font(.headline)
                                                Spacer()
                                                Text(entry.category.capitalized)
                                                    .font(.caption.weight(.medium))
                                                    .padding(.horizontal, 10)
                                                    .padding(.vertical, 4)
                                                    .background(Color.purple.opacity(0.2))
                                                    .clipShape(Capsule())
                                                    .foregroundStyle(.purple)
                                            }
                                            Text(entry.definition)
                                                .font(.subheadline)
                                                .foregroundStyle(Color.textSecondary)
                                                .lineLimit(3)
                                        }
                                    }
                                }
                                .buttonStyle(.plain)
                            }

                            if filteredEntries.isEmpty {
                                CardView {
                                    VStack(spacing: 8) {
                                        Image(systemName: "magnifyingglass")
                                            .font(.title2)
                                            .foregroundStyle(Color.textSecondary)
                                        Text("ui.glossary.1".localized)
                                            .font(.headline)
                                        Text("ui.glossary.2".localized)
                                            .font(.caption)
                                            .foregroundStyle(Color.textSecondary)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 8)
                                }
                            }
                        }
                        .padding()
                        .readableContainer()
                    }
                }
            }
        }
    }

    private var categoryPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(categories, id: \.self) { cat in
                    Button {
                        withAnimation(.spring(duration: 0.25)) { selectedCategory = cat }
                    } label: {
                        Text(cat == "all" ? "All" : cat.capitalized)
                            .font(.caption.weight(.medium))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 10)
                            .frame(minHeight: 44)
                            .background(
                                Capsule().fill(selectedCategory == cat ? Color.purple : Color.white.opacity(0.1))
                            )
                            .foregroundStyle(selectedCategory == cat ? .white : .primary)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    @MainActor
    private func load() async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            let response: PaginatedGlossaryEntries = try await APIClient.shared.fetch(.glossary)
            entries = response.data
        } catch {
            self.error = error.localizedDescription
        }
    }
}

private struct GlossaryDetailView: View {
    let entry: GlossaryEntry

    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    PremiumSectionHeader(
                title: "section.glossary.1.title".localized,
                subtitle: "section.glossary.1.subtitle".localized
            )

                    Text(entry.term)
                        .font(.title2.bold())

                    Text(entry.definition)
                        .font(.body)

                    CardView {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("ui.glossary.3".localized)
                                .font(.headline)
                            Text(entry.usageExample)
                                .font(.subheadline)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }

                    if let related = entry.relatedTerms, !related.isEmpty {
                        CardView {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("ui.glossary.4".localized)
                                    .font(.headline)
                                ForEach(related, id: \.self) { term in
                                    Text("• \(term)")
                                        .font(.subheadline)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }
                        }
                    }
                }
                .padding()
                .readableContainer()
            }
        }
        .navigationTitle(entry.term)
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    GlossaryView()
        .preferredColorScheme(.dark)
}
