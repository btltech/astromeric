// EditProfileView.swift
// Profile editing form with location autocomplete

import SwiftUI

struct EditProfileView: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(AppStore.self) private var store
    @State private var viewModel: EditProfileVM
    @State private var showUnlocks = false
    @State private var isDateUnlocked = false
    
    /// Initialize with existing profile to edit, or nil to create new
    init(profile: Profile? = nil) {
        _viewModel = State(initialValue: EditProfileVM(profile: profile))
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Space.md) {
                        headerSection
                        unlocksSection
                        nameSection
                        birthDateSection
                        birthTimeSection
                        birthPlaceSection
                        saveButton
                    }
                    .padding()
                    .readableContainer()
                }
            }
            .navigationTitle(viewModel.isEditing ? "tern.editProfile.0a".localized : "tern.editProfile.0b".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("action.cancel".localized) {
                        dismiss()
                    }
                }
            }
            .alert("ui.editProfile.11".localized, isPresented: $viewModel.showError) {
                Button("action.ok".localized) {}
            } message: {
                Text(viewModel.errorMessage)
            }
        }
    }
    
    // MARK: - Header Section
    
    private var headerSection: some View {
        VStack(spacing: Space.sm) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.purple, .pink],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 80, height: 80)
                
                Text(viewModel.name.isEmpty ? "?" : String(viewModel.name.prefix(1)).uppercased())
                    .font(.largeTitle.bold())
                    .foregroundStyle(.white)
            }
            
            Text(viewModel.isEditing ? "tern.editProfile.1a".localized : "tern.editProfile.1b".localized)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
        }
        .padding(.top)
    }

    private var unlocksSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: Space.sm) {
                Button {
                    withAnimation(.spring(response: 0.25, dampingFraction: 0.85)) {
                        showUnlocks.toggle()
                    }
                } label: {
                    HStack(spacing: Space.sm) {
                        Image(systemName: "sparkles")
                            .foregroundStyle(Color.accentPrimary)
                            .frame(width: 30, height: 30)
                            .background(Circle().fill(Color.accentPrimary.opacity(0.14)))

                        VStack(alignment: .leading, spacing: 2) {
                            Text("ui.editProfile.0".localized)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(Color.textPrimary)
                            Text("profile.edit.unlocks.summary".localized)
                                .font(.caption)
                                .foregroundStyle(Color.textSecondary)
                        }

                        Spacer()

                        Image(systemName: showUnlocks ? "chevron.up" : "chevron.down")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(Color.textSecondary)
                    }
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)

                if showUnlocks {
                    PremiumDivider()
                    profileUnlockRow(icon: "sparkles.rectangle.stack.fill", title: "profile.edit.unlocks.chart.title".localized, detail: "profile.edit.unlocks.chart.detail".localized)
                    profileUnlockRow(icon: "number.square.fill", title: "profile.edit.unlocks.numerology.title".localized, detail: "profile.edit.unlocks.numerology.detail".localized)
                    profileUnlockRow(icon: "clock.badge.checkmark.fill", title: "profile.edit.unlocks.guidance.title".localized, detail: "profile.edit.unlocks.guidance.detail".localized)
                }
            }
        }
    }

    private func profileUnlockRow(icon: String, title: String, detail: String) -> some View {
        HStack(alignment: .top, spacing: Space.sm) {
            Image(systemName: icon)
                .foregroundStyle(Color.accentPrimary)
                .frame(width: 24)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                Text(detail)
                    .font(.caption)
                    .foregroundStyle(Color.textSecondary)
            }
        }
    }
    
    // MARK: - Name Section
    
    private var nameSection: some View {
        PremiumSettingsGroup(
            title: "ui.editProfile.4".localized,
            subtitle: "profile.edit.name.subtitle".localized,
            icon: "person.fill",
            accent: .accentPrimary
        ) {
            profileTextField("ui.editProfile.9".localized, text: $viewModel.name, accessibilityLabel: "Profile name")
        }
    }
    
    // MARK: - Birth Date Section
    
    private var birthDateSection: some View {
        PremiumSettingsGroup(
            title: "ui.editProfile.5".localized,
            subtitle: "profile.edit.birthDate.subtitle".localized,
            icon: "calendar",
            accent: .cosmicBlue
        ) {
            if store.hideSensitiveDetailsEnabled && viewModel.isEditing && !isDateUnlocked {
                HStack {
                    Text(PrivacyRedaction.maskedDate)
                        .font(.body.monospaced())
                        .foregroundStyle(Color.textSecondary)
                    
                    Spacer()
                    
                    Button {
                        withAnimation {
                            isDateUnlocked = true
                        }
                    } label: {
                        HStack(spacing: 4) {
                            Image(systemName: "lock.fill")
                            Text("Unlock")
                        }
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(Color.accentPrimary)
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel("Unlock birth date picker")
                }
                .padding(.vertical, 4)
            } else {
                DatePicker(
                    "form.dateOfBirth".localized,
                    selection: $viewModel.birthDate,
                    in: ...Date(),
                    displayedComponents: .date
                )
                .datePickerStyle(.compact)
                .tint(.cosmicBlue)
            }
        }
    }
    
    // MARK: - Birth Time Section
    
    private var birthTimeSection: some View {
        PremiumSettingsGroup(
            title: "ui.editProfile.6".localized,
            subtitle: "profile.edit.birthTime.subtitle".localized,
            icon: "clock.fill",
            accent: .warningOrange
        ) {
            VStack(alignment: .leading, spacing: Space.sm) {
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: Space.sm), count: 3), spacing: Space.sm) {
                    ForEach(TimeConfidence.allCases, id: \.self) { option in
                        TimeConfidenceChip(
                            title: option.displayTitle,
                            isSelected: viewModel.timeConfidence == option,
                            accent: .warningOrange
                        ) {
                            viewModel.timeConfidence = option
                        }
                    }
                }

                if viewModel.timeConfidence != .unknown {
                    PremiumDivider()
                    DatePicker(
                        "form.timeOfBirth".localized,
                        selection: $viewModel.birthTime,
                        displayedComponents: .hourAndMinute
                    )
                    .datePickerStyle(.compact)
                    .tint(.warningOrange)

                    if viewModel.timeConfidence == .approximate {
                        Label("ui.editProfile.7".localized, systemImage: "info.circle")
                            .font(.caption)
                            .foregroundStyle(.orange)
                    }
                } else {
                    Text("ui.editProfile.1".localized)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }
            }
        }
    }
    
    // MARK: - Birth Place Section
    
    private var birthPlaceSection: some View {
        PremiumSettingsGroup(
            title: "ui.editProfile.8".localized,
            subtitle: "profile.edit.birthPlace.subtitle".localized,
            icon: "mappin.circle.fill",
            accent: .accentSecondary
        ) {
            VStack(alignment: .leading, spacing: Space.sm) {
                HStack {
                    Text("profile.edit.birthPlace.current".localized)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)

                    Spacer()
                    
                    Button {
                        viewModel.useCurrentLocation()
                    } label: {
                        HStack(spacing: 4) {
                            if viewModel.isUsingCurrentLocation {
                                ProgressView()
                                    .scaleEffect(0.7)
                            } else {
                                Image(systemName: "location.fill")
                            }
                            Text("ui.editProfile.2".localized)
                                .font(.label)
                        }
                        .foregroundStyle(Color.accentSecondary)
                    }
                    .disabled(viewModel.isUsingCurrentLocation)
                }
                
                profileTextField("ui.editProfile.10".localized, text: $viewModel.placeQuery, accessibilityLabel: "Birth place")
                    .onChange(of: viewModel.placeQuery) { _, newValue in
                        viewModel.searchPlaces(query: newValue)
                    }
                
                if viewModel.isSearchingPlaces || viewModel.isGeocodingPlace {
                    HStack {
                        ProgressView()
                            .scaleEffect(0.8)
                        Text(viewModel.isGeocodingPlace ? "tern.editProfile.3a".localized : "tern.editProfile.3b".localized)
                            .font(.label)
                            .foregroundStyle(Color.textSecondary)
                    }
                } else if !viewModel.placeSuggestions.isEmpty {
                    VStack(spacing: 0) {
                        ForEach(viewModel.placeSuggestions, id: \.self) { completion in
                            Button {
                                viewModel.selectCompletion(completion)
                            } label: {
                                HStack {
                                    Image(systemName: "mappin")
                                        .foregroundStyle(Color.accentSecondary)
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(completion.title)
                                            .font(.subheadline)
                                            .foregroundStyle(.primary)
                                        if !completion.subtitle.isEmpty {
                                            Text(completion.subtitle)
                                                .font(.label)
                                                .foregroundStyle(Color.textSecondary)
                                        }
                                    }
                                    Spacer()
                                }
                                .padding(.vertical, 10)
                            }
                            
                            if completion != viewModel.placeSuggestions.last {
                                Divider()
                            }
                        }
                    }
                    .padding(.horizontal, Space.sm)
                    .background(Color.surfaceBase)
                    .clipShape(RoundedRectangle(cornerRadius: Radius.sm))
                }
                
                if viewModel.selectedPlace != nil {
                    PremiumStatusBanner(
                        title: "ui.editProfile.3".localized,
                        message: viewModel.timezoneDisplay,
                        tone: .success
                    )
                }
            }
        }
    }
    
    // MARK: - Save Button
    
    private var saveButton: some View {
        GradientButton(
            viewModel.isEditing ? "tern.editProfile.4a".localized : "tern.editProfile.4b".localized,
            icon: "checkmark.circle.fill"
        ) {
            Task {
                await viewModel.save(store: store)
                if !viewModel.showError {
                    dismiss()
                }
            }
        }
        .disabled(!viewModel.isValid || viewModel.isSaving)
        .opacity(viewModel.isValid ? 1 : 0.6)
        .padding(.top)
        .accessibilityLabel(viewModel.isEditing ? "Save profile" : "Create profile")
    }

    private func profileTextField(_ placeholder: String, text: Binding<String>, accessibilityLabel: String) -> some View {
        TextField(placeholder, text: text)
            .textFieldStyle(.plain)
            .padding(Space.sm)
            .background(
                RoundedRectangle(cornerRadius: Radius.sm)
                    .fill(Color.surfaceBase)
                    .overlay(
                        RoundedRectangle(cornerRadius: Radius.sm)
                            .stroke(Color.borderSubtle, lineWidth: Stroke.hairline)
                    )
            )
            .accessibilityLabel(accessibilityLabel)
    }
}

private struct TimeConfidenceChip: View {
    let title: String
    let isSelected: Bool
    let accent: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Image(systemName: isSelected ? "checkmark.circle.fill" : "circle")
                    .font(.subheadline.weight(.semibold))
                Text(title)
                    .font(.caption.weight(.semibold))
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                    .minimumScaleFactor(0.8)
            }
            .frame(maxWidth: .infinity, minHeight: 64)
            .foregroundStyle(isSelected ? accent : Color.textSecondary)
            .background(
                RoundedRectangle(cornerRadius: Radius.sm)
                    .fill(isSelected ? accent.opacity(0.16) : Color.surfaceBase)
                    .overlay(
                        RoundedRectangle(cornerRadius: Radius.sm)
                            .stroke(isSelected ? accent.opacity(0.35) : Color.borderSubtle, lineWidth: Stroke.hairline)
                    )
            )
        }
        .buttonStyle(ScaleButtonStyle())
    }
}

// MARK: - Preview

#Preview {
    EditProfileView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}

#Preview("Edit Existing") {
    EditProfileView(profile: Profile(
        id: 1,
        name: "John",
        dateOfBirth: "1990-05-15",
        timeOfBirth: "14:30",
        timeConfidence: "exact",
        placeOfBirth: "Los Angeles, CA",
        latitude: 34.0522,
        longitude: -118.2437,
        timezone: "America/Los_Angeles",
        houseSystem: "placidus"
    ))
    .environment(AppStore.shared)
    .preferredColorScheme(.dark)
}
