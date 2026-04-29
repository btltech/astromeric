// FriendsView.swift
// Social friend comparison — "Who are your most compatible people?"

import SwiftUI

// MARK: - Models

struct FriendProfile: Codable, Identifiable {
    let id: String
    var name: String
    var dateOfBirth: String
    var avatarEmoji: String
    var relationshipType: String
    var notes: String?
    var addedAt: String?

    enum CodingKeys: String, CodingKey {
        case id, name, notes
        case dateOfBirth = "date_of_birth"
        case avatarEmoji = "avatar_emoji"
        case relationshipType = "relationship_type"
        case addedAt = "added_at"
    }
}

struct FriendCompatibility: Codable, Identifiable {
    var id: String { friendId }
    let friendId: String
    let friendName: String
    let overallScore: Double
    let headline: String
    let emoji: String
    let relationshipType: String
    let strengths: [String]
    let recommendations: [String]

    enum CodingKeys: String, CodingKey {
        case emoji, headline, strengths, recommendations
        case friendId = "friend_id"
        case friendName = "friend_name"
        case overallScore = "overall_score"
        case relationshipType = "relationship_type"
    }
}

// MARK: - View

struct FriendsView: View {
    @Environment(AppStore.self) private var store
    @State private var friends: [FriendProfile] = []
    @State private var compatibilities: [FriendCompatibility] = []
    @State private var isLoading = false
    @State private var showingAddFriend = false
    @State private var selectedFriend: FriendCompatibility?

    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil).ignoresSafeArea()

            ScrollView {
                VStack(spacing: 20) {
                    PremiumHeroCard(
                            eyebrow: "hero.friends.eyebrow".localized,
                            title: "hero.friends.title".localized,
                            bodyText: "hero.friends.body".localized,
                            accent: [Color(hex: "2c1331"), Color(hex: "9a427a"), Color(hex: "4f56ba")],
                            chips: ["hero.friends.chip.0".localized, "hero.friends.chip.1".localized, "hero.friends.chip.2".localized]
                        )

                    CardView {
                        VStack(alignment: .leading, spacing: 10) {
                            Label("ui.friends.9".localized, systemImage: "arrow.triangle.2.circlepath.circle.fill")
                                .font(.headline)
                                .foregroundStyle(.pink)
                            Text("ui.friends.0".localized)
                                .font(.subheadline)
                                .foregroundStyle(Color.textSecondary)
                            Text("ui.friends.1".localized)
                                .font(.subheadline)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }

                    PremiumSectionHeader(
                title: "section.friends.0.title".localized,
                subtitle: "section.friends.0.subtitle".localized
            )

                    // Add friend button
                    Button {
                        showingAddFriend = true
                    } label: {
                        HStack(spacing: 10) {
                            Image(systemName: "person.badge.plus")
                                .font(.title3)
                                .accessibilityHidden(true)
                            Text("ui.friends.2".localized)
                                .font(.headline)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.accentColor)
                        .foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 16))
                    }
                    .accessibilityLabel("Add a Friend")
                    .accessibilityHint("Opens a form to add a friend's birth date for compatibility analysis")

                    if isLoading {
                        SkeletonCard()
                        SkeletonCard()
                    } else if compatibilities.isEmpty && !friends.isEmpty {
                        CardView {
                            VStack(spacing: 8) {
                                Text("✨")
                                    .font(.largeTitle)
                                Text("ui.friends.3".localized)
                                    .font(.subheadline)
                                    .foregroundStyle(Color.textSecondary)
                            }
                        }
                    } else if friends.isEmpty {
                        CardView {
                            VStack(spacing: 16) {
                                Text("🌌")
                                    .font(.system(.largeTitle))
                                Text("ui.friends.4".localized)
                                    .font(.headline)
                                Text("ui.friends.5".localized)
                                    .font(.subheadline)
                                    .multilineTextAlignment(.center)
                                    .foregroundStyle(Color.textSecondary)
                            }
                            .padding(.vertical, 8)
                        }
                    } else {
                        // Ranked compatibility list
                        ForEach(compatibilities) { compat in
                            Button {
                                selectedFriend = compat
                            } label: {
                                compatibilityRow(compat)
                            }
                            .buttonStyle(.plain)
                            .accessibilityLabel("\(compat.displayName(hideSensitive: store.hideSensitiveDetailsEnabled)), \(Int(compat.overallScore))% compatible. \(compat.headline)")
                            .accessibilityHint("Tap to view full compatibility report")
                        }
                    }
                }
                .padding()
                .readableContainer()
            }
        }
        .navigationTitle("screen.cosmicCircle".localized)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showingAddFriend) {
            AddFriendSheet { newFriend in
                friends.append(newFriend)
                Task { await loadCompatibilities() }
            }
        }
        .sheet(item: $selectedFriend) { compat in
            FriendDetailSheet(compat: compat)
        }
        .task { await loadFriends() }
    }

    // MARK: - Row

    @ViewBuilder
    private func compatibilityRow(_ compat: FriendCompatibility) -> some View {
        CardView {
            HStack(spacing: 14) {
                // Score circle
                ZStack {
                    Circle()
                        .fill(scoreColor(compat.overallScore).opacity(0.15))
                        .frame(width: 56, height: 56)
                    VStack(spacing: 0) {
                        Text("\(Int(compat.overallScore))")
                            .font(.title3.bold())
                            .foregroundStyle(scoreColor(compat.overallScore))
                        Text("%")
                            .font(.caption2)
                            .foregroundStyle(Color.textSecondary)
                    }
                }
                .accessibilityHidden(true)  // announced on the parent button

                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text(compat.emoji)
                            .accessibilityHidden(true)
                        Text(compat.displayName(hideSensitive: store.hideSensitiveDetailsEnabled))
                            .font(.headline)
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundStyle(Color.textMuted)
                            .accessibilityHidden(true)
                    }
                    Text(compat.headline)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                        .lineLimit(2)

                    // Type badge
                    HStack(spacing: 6) {
                        Text("ui.friends.6".localized)
                            .font(.caption2.bold())
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(.pink.opacity(0.16))
                            .clipShape(Capsule())
                        Text(compat.relationshipType.capitalized)
                            .font(.caption2.bold())
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(Color.surfaceElevated)
                            .clipShape(Capsule())
                            .accessibilityLabel("Relationship type: \(compat.relationshipType)")
                    }
                }
            }
        }
    }

    private func scoreColor(_ score: Double) -> Color {
        if score >= 80 { return .green }
        if score >= 60 { return Color(hue: 0.1, saturation: 0.8, brightness: 0.9) } // orange
        return .purple
    }

    // MARK: - Actions

    private func toPayload(_ profile: Profile) -> ProfilePayload {
        profile.privacySafePayload(hideSensitive: store.hideSensitiveDetailsEnabled)
    }

    private func loadFriends() async {
        guard let profile = store.activeProfile else { return }
        isLoading = true
        defer { isLoading = false }
        do {
            let response: V2ApiResponse<[FriendProfile]> = try await APIClient.shared.fetch(
                .listFriends(ownerId: String(profile.id)),
                cachePolicy: .networkFirst
            )
            friends = response.data
            if !friends.isEmpty { await loadCompatibilities() }
        } catch { /* silent */ }
    }

    private func loadCompatibilities() async {
        guard let p = store.activeProfile else { return }
        let profile = toPayload(p)
        do {
            let response: V2ApiResponse<[FriendCompatibility]> = try await APIClient.shared.fetch(
                .compareAllFriends(ownerId: String(p.id), profile: profile),
                cachePolicy: .networkFirst
            )
            await MainActor.run { compatibilities = response.data }
        } catch { /* silent */ }
    }
}

// MARK: - Add Friend Sheet

struct AddFriendSheet: View {
    let onAdd: (FriendProfile) -> Void
    @Environment(\.dismiss) var dismiss

    @State private var name = ""
    @State private var dob = Date()
    @State private var relationshipType = "friendship"
    @State private var avatarEmoji = "👤"
    @State private var isSaving = false
    @Environment(AppStore.self) private var store

    let emojis = ["👤", "👩", "👨", "🧑", "👫", "💃", "🕺", "🦋", "🌟", "🔥"]
    let types = ["friendship", "romantic", "professional"]

    var body: some View {
        NavigationStack {
            Form {
                Section("ui.friends.12".localized) {
                    TextField("ui.friends.10".localized, text: $name)
                    DatePicker("Date of Birth", selection: $dob, displayedComponents: .date)
                }
                Section("ui.friends.13".localized) {
                    Picker("ui.friends.11".localized, selection: $relationshipType) {
                        ForEach(types, id: \.self) { t in Text(t.capitalized).tag(t) }
                    }
                    .pickerStyle(.segmented)
                }
                Section("ui.friends.14".localized) {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack {
                            ForEach(emojis, id: \.self) { e in
                                Button(e) { avatarEmoji = e }
                                    .font(.title)
                                    .padding(6)
                                    .background(avatarEmoji == e ? Color.accentColor.opacity(0.2) : Color.clear)
                                    .clipShape(Circle())
                            }
                        }
                    }
                }
            }
            .navigationTitle("screen.addFriend".localized)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("action.cancel".localized) { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("action.save".localized) { save() }.disabled(name.isEmpty || isSaving)
                }
            }
        }
    }

    private func save() {
        isSaving = true
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let friend = FriendProfile(
            id: UUID().uuidString,
            name: name,
            dateOfBirth: formatter.string(from: dob),
            avatarEmoji: avatarEmoji,
            relationshipType: relationshipType
        )
        Task {
            guard let p = store.activeProfile else { return }
            do {
                let _: V2ApiResponse<FriendProfile> = try await APIClient.shared.fetch(
                    .addFriend(ownerId: String(p.id), friend: friend),
                    cachePolicy: .networkOnly
                )
                await MainActor.run {
                    onAdd(friend)
                    dismiss()
                }
            } catch {
                await MainActor.run { isSaving = false }
            }
        }
    }
}

// MARK: - Friend Detail Sheet

struct FriendDetailSheet: View {
    @Environment(AppStore.self) private var store
    let compat: FriendCompatibility
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Score hero
                    CardView {
                        VStack(spacing: 12) {
                            Text(compat.emoji)
                                .font(.system(.largeTitle))
                                .accessibilityHidden(true)
                            Text(compat.displayName(hideSensitive: store.hideSensitiveDetailsEnabled))
                                .font(.title2.bold())
                            Text(String(format: "fmt.friends.0".localized, "\(Int(compat.overallScore))"))
                                .font(.title3)
                                .foregroundStyle(.purple)
                            Text(compat.headline)
                                .font(.subheadline)
                                .multilineTextAlignment(.center)
                                .foregroundStyle(Color.textSecondary)
                        }
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("\(compat.displayName(hideSensitive: store.hideSensitiveDetailsEnabled)), \(Int(compat.overallScore))% compatible. \(compat.headline)")

                    if !compat.strengths.isEmpty {
                        CardView {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("ui.friends.7".localized)
                                    .font(.headline)
                                ForEach(compat.strengths, id: \.self) {
                                    Text("• \($0)").font(.subheadline)
                                        .foregroundStyle(Color.textPrimary)
                                }
                            }
                        }
                    }

                    if !compat.recommendations.isEmpty {
                        CardView {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("ui.friends.8".localized)
                                    .font(.headline)
                                ForEach(compat.recommendations, id: \.self) {
                                    Text("• \($0)").font(.subheadline)
                                        .foregroundStyle(Color.textPrimary)
                                }
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("screen.cosmicMatch".localized)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("action.done".localized) { dismiss() }
                }
            }
            .background { CosmicBackgroundView(element: nil).ignoresSafeArea() }
        }
    }
}
