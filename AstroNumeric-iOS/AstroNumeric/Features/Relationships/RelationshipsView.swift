// RelationshipsView.swift
// Saved relationships and compatibility history

import SwiftUI

struct RelationshipsView: View {
    @Environment(AppStore.self) private var store
    @State private var viewModel = RelationshipsVM()
    @State private var selectedRelationship: SavedRelationship?
    @State private var filterType: RelationshipType?
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Stats header
                        if !viewModel.savedRelationships.isEmpty {
                            statsCard
                        }
                        
                        // Filter chips
                        if !viewModel.savedRelationships.isEmpty {
                            filterChips
                        }
                        
                        // Relationships list
                        relationshipsList
                    }
                    .padding()
                }
            }
            .navigationTitle("Relationships")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    NavigationLink {
                        CompatibilityView()
                    } label: {
                        Image(systemName: "plus.circle.fill")
                            .font(.title2)
                            .foregroundStyle(.purple)
                    }
                }
            }
            .sheet(item: $selectedRelationship) { relationship in
                RelationshipDetailSheet(relationship: relationship, viewModel: viewModel)
            }
            .task {
                await viewModel.loadRelationships()
            }
        }
    }
    
    // MARK: - Stats Card
    
    private var statsCard: some View {
        HStack(spacing: 16) {
            VStack(spacing: 4) {
                Text("\(viewModel.savedRelationships.count)")
                    .font(.title.bold())
                Text("Saved")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity)
            
            Divider()
                .frame(height: 40)
            
            VStack(spacing: 4) {
                Text("\(Int(viewModel.averageCompatibility * 100))%")
                    .font(.title.bold())
                    .foregroundStyle(.purple)
                Text("Avg Score")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity)
            
            Divider()
                .frame(height: 40)
            
            VStack(spacing: 4) {
                Text(highestScoreEmoji)
                    .font(.title)
                Text("Best Match")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }
    
    private var highestScoreEmoji: String {
        guard let highest = viewModel.savedRelationships.max(by: { $0.overallScore < $1.overallScore }) else {
            return "💫"
        }
        if highest.overallScore >= 0.85 { return "💯" }
        if highest.overallScore >= 0.70 { return "🔥" }
        if highest.overallScore >= 0.55 { return "✨" }
        return "💫"
    }
    
    // MARK: - Filter Chips
    
    private var filterChips: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                filterChip(type: nil, name: "All", emoji: "✨")
                
                ForEach(RelationshipType.allCases, id: \.self) { type in
                    filterChip(type: type, name: type.displayName, emoji: type.emoji)
                }
            }
        }
    }
    
    private func filterChip(type: RelationshipType?, name: String, emoji: String) -> some View {
        let isSelected = filterType == type
        
        return Button {
            withAnimation(.spring(duration: 0.3)) {
                filterType = type
            }
            HapticManager.impact(.light)
        } label: {
            HStack(spacing: 4) {
                Text(emoji)
                Text(name)
                    .font(.caption)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .frame(minHeight: 44) // Apple HIG minimum tap target
            .background(
                Capsule()
                    .fill(isSelected ? (type?.color ?? .purple) : Color.white.opacity(0.1))
            )
            .foregroundStyle(isSelected ? .white : .secondary)
        }
    }
    
    // MARK: - Relationships List
    
    private var relationshipsList: some View {
        VStack(spacing: 12) {
            let filtered = filteredRelationships
            
            if filtered.isEmpty {
                emptyStateCard
            } else {
                ForEach(filtered) { relationship in
                    RelationshipCard(relationship: relationship) {
                        selectedRelationship = relationship
                    }
                    .contextMenu {
                        Button(role: .destructive) {
                            viewModel.deleteRelationship(relationship)
                        } label: {
                            Label("Delete", systemImage: "trash")
                        }
                    }
                }
            }
        }
    }
    
    private var filteredRelationships: [SavedRelationship] {
        guard let type = filterType else {
            return viewModel.savedRelationships
        }
        return viewModel.savedRelationships.filter { $0.type == type }
    }
    
    private var emptyStateCard: some View {
        CardView {
            VStack(spacing: 16) {
                Image(systemName: "heart.circle")
                    .font(.system(size: 48))
                    .foregroundStyle(.secondary)
                
                Text("No relationships saved")
                    .font(.headline)
                
                Text("Calculate compatibility and save relationships to track them here")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                
                NavigationLink {
                    CompatibilityView()
                } label: {
                    HStack {
                        Image(systemName: "heart.fill")
                        Text("Check Compatibility")
                    }
                    .font(.subheadline.bold())
                    .foregroundStyle(.white)
                    .padding(.horizontal, 20)
                    .padding(.vertical, 10)
                    .background(Capsule().fill(.pink))
                }
            }
            .frame(maxWidth: .infinity)
            .padding()
        }
    }
}

// MARK: - Relationship Card

struct RelationshipCard: View {
    let relationship: SavedRelationship
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 12) {
                // Type badge
                ZStack {
                    Circle()
                        .fill(relationship.type.color.opacity(0.2))
                        .frame(width: 44, height: 44)
                    Text(relationship.type.emoji)
                        .font(.title3)
                }
                
                // Names
                VStack(alignment: .leading, spacing: 4) {
                    Text("\(relationship.personAName) & \(relationship.personBName)")
                        .font(.subheadline.bold())
                        .foregroundStyle(.primary)
                    
                    Text(relationship.type.displayName)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                
                Spacer()
                
                // Score
                VStack(alignment: .trailing, spacing: 2) {
                    Text(relationship.formattedScore)
                        .font(.title3.bold())
                        .foregroundStyle(relationship.scoreColor)
                    
                    // Mini score bar
                    GeometryReader { geo in
                        ZStack(alignment: .leading) {
                            Capsule()
                                .fill(.cosmicSecondary.opacity(0.4))
                            Capsule()
                                .fill(relationship.scoreColor)
                                .frame(width: geo.size.width * relationship.overallScore)
                        }
                    }
                    .frame(width: 50, height: 4)
                }
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(.ultraThinMaterial)
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Relationship Detail Sheet

struct RelationshipDetailSheet: View {
    let relationship: SavedRelationship
    @Bindable var viewModel: RelationshipsVM
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.opacity(0.95).ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        // Header
                        headerSection
                        
                        // Score ring
                        scoreRing
                        
                        // Categories
                        if !relationship.categories.isEmpty {
                            categoriesSection
                        }
                        
                        // Strengths
                        if !relationship.strengths.isEmpty {
                            strengthsSection
                        }
                        
                        // Challenges
                        if !relationship.challenges.isEmpty {
                            challengesSection
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .destructiveAction) {
                    Button(role: .destructive) {
                        viewModel.deleteRelationship(relationship)
                        dismiss()
                    } label: {
                        Image(systemName: "trash")
                    }
                }
            }
        }
        .presentationDetents([.medium, .large])
    }
    
    private var headerSection: some View {
        VStack(spacing: 8) {
            HStack(spacing: 16) {
                VStack {
                    Text("👤")
                        .font(.title)
                    Text(relationship.personAName)
                        .font(.subheadline.bold())
                    Text(relationship.personADOB)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
                
                Text(relationship.type.emoji)
                    .font(.largeTitle)
                
                VStack {
                    Text("👤")
                        .font(.title)
                    Text(relationship.personBName)
                        .font(.subheadline.bold())
                    Text(relationship.personBDOB)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
            
            Text(relationship.type.displayName)
                .font(.caption)
                .foregroundStyle(relationship.type.color)
                .padding(.horizontal, 12)
                .padding(.vertical, 4)
                .background(Capsule().fill(relationship.type.color.opacity(0.2)))
        }
    }
    
    private var scoreRing: some View {
        ZStack {
            Circle()
                .stroke(Color.cosmicSecondary.opacity(0.5), lineWidth: 12)
                .frame(width: 120, height: 120)
            
            Circle()
                .trim(from: 0, to: relationship.overallScore)
                .stroke(
                    relationship.scoreColor,
                    style: StrokeStyle(lineWidth: 12, lineCap: .round)
                )
                .frame(width: 120, height: 120)
                .rotationEffect(.degrees(-90))
            
            VStack(spacing: 0) {
                Text(relationship.formattedScore)
                    .font(.title.bold())
                    .foregroundStyle(relationship.scoreColor)
                Text("Overall")
                    .font(.caption)
                    .foregroundStyle(.textSecondary)
            }
        }
    }
    
    private var categoriesSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Text("Categories")
                    .font(.headline)
                
                ForEach(relationship.categories, id: \.name) { category in
                    HStack {
                        Text(category.emoji)
                        Text(category.name)
                            .font(.subheadline)
                        Spacer()
                        Text("\(Int(category.score * 100))%")
                            .font(.subheadline.bold())
                            .foregroundStyle(scoreColor(for: category.score))
                    }
                }
            }
        }
    }
    
    private var strengthsSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("💪")
                    Text("Strengths")
                        .font(.headline)
                }
                
                ForEach(relationship.strengths, id: \.self) { strength in
                    HStack(alignment: .top) {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                            .font(.caption)
                        Text(strength)
                            .font(.subheadline)
                    }
                }
            }
        }
    }
    
    private var challengesSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("⚡")
                    Text("Challenges")
                        .font(.headline)
                }
                
                ForEach(relationship.challenges, id: \.self) { challenge in
                    HStack(alignment: .top) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundStyle(.orange)
                            .font(.caption)
                        Text(challenge)
                            .font(.subheadline)
                    }
                }
            }
        }
    }
    
    private func scoreColor(for score: Double) -> Color {
        if score >= 0.75 { return .green }
        if score >= 0.50 { return .orange }
        return .red
    }
}

// MARK: - Preview

#Preview {
    RelationshipsView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
