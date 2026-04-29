// EditProfileView.swift
// Profile editing form with location autocomplete

import SwiftUI

struct EditProfileView: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(AppStore.self) private var store
    @State private var viewModel: EditProfileVM
    
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
                    VStack(spacing: 24) {
                        // Header
                        headerSection

                        unlocksSection
                        
                        // Name field
                        nameSection
                        
                        // Birth date
                        birthDateSection
                        
                        // Birth time
                        birthTimeSection
                        
                        // Birth place
                        birthPlaceSection
                        
                        // Save button
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
        VStack(spacing: 12) {
            // Avatar
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
            VStack(alignment: .leading, spacing: 12) {
                Text("ui.editProfile.0".localized)
                    .font(.headline)

                profileUnlockRow(icon: "sparkles.rectangle.stack.fill", title: "Full birth chart", detail: "Big Three, placements, aspects, points, and dignity context.")
                profileUnlockRow(icon: "number.square.fill", title: "Flagship numerology", detail: "Life path, core numbers, cycles, pinnacles, and synthesis.")
                profileUnlockRow(icon: "clock.badge.checkmark.fill", title: "Practical daily guidance", detail: "Forecasts, timing windows, moon context, and a year-ahead view.")
            }
        }
    }

    private func profileUnlockRow(icon: String, title: String, detail: String) -> some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon)
                .foregroundStyle(.purple)
                .frame(width: 20)
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
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Label("ui.editProfile.4".localized, systemImage: "person.fill")
                    .font(.headline)
                    .foregroundStyle(.purple)
                
                TextField("ui.editProfile.9".localized, text: $viewModel.name)
                    .textFieldStyle(.plain)
                    .padding(12)
                    .background(.ultraThinMaterial)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
            }
        }
    }
    
    // MARK: - Birth Date Section
    
    private var birthDateSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Label("ui.editProfile.5".localized, systemImage: "calendar")
                    .font(.headline)
                    .foregroundStyle(.purple)
                
                DatePicker(
                    "Date of Birth",
                    selection: $viewModel.birthDate,
                    in: ...Date(),
                    displayedComponents: .date
                )
                .datePickerStyle(.graphical)
                .tint(.purple)
            }
        }
    }
    
    // MARK: - Birth Time Section
    
    private var birthTimeSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Label("ui.editProfile.6".localized, systemImage: "clock.fill")
                    .font(.headline)
                    .foregroundStyle(.purple)

                // 3-option picker
                VStack(spacing: 8) {
                    ForEach(TimeConfidence.allCases, id: \.self) { option in
                        Button {
                            viewModel.timeConfidence = option
                        } label: {
                            HStack {
                                Image(systemName: viewModel.timeConfidence == option
                                      ? "tern.editProfile.2a".localized : "tern.editProfile.2b".localized)
                                    .foregroundStyle(.purple)
                                Text(option.displayTitle)
                                    .font(.subheadline)
                                    .foregroundStyle(Color.textPrimary)
                                Spacer()
                            }
                        }
                        .buttonStyle(.plain)
                    }
                }

                if viewModel.timeConfidence != .unknown {
                    DatePicker(
                        "Time of Birth",
                        selection: $viewModel.birthTime,
                        displayedComponents: .hourAndMinute
                    )
                    .datePickerStyle(.wheel)
                    .labelsHidden()

                    if viewModel.timeConfidence == .approximate {
                        Label("ui.editProfile.7".localized, systemImage: "info.circle")
                            .font(.caption)
                            .foregroundStyle(.orange)
                    }
                } else {
                    Text("ui.editProfile.1".localized)
                        .font(.label)
                        .foregroundStyle(Color.textSecondary)
                }
            }
        }
    }
    
    // MARK: - Birth Place Section
    
    private var birthPlaceSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Label("ui.editProfile.8".localized, systemImage: "mappin.circle.fill")
                        .font(.headline)
                        .foregroundStyle(.purple)
                    
                    Spacer()
                    
                    // Use current location button (for those born where they currently are)
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
                        .foregroundStyle(.purple)
                    }
                    .disabled(viewModel.isUsingCurrentLocation)
                }
                
                TextField("ui.editProfile.10".localized, text: $viewModel.placeQuery)
                    .textFieldStyle(.plain)
                    .padding(12)
                    .background(.ultraThinMaterial)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .onChange(of: viewModel.placeQuery) { _, newValue in
                        viewModel.searchPlaces(query: newValue)
                    }
                
                // Location suggestions
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
                                        .foregroundStyle(.purple)
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
                    .padding(.horizontal, 12)
                    .background(.ultraThinMaterial)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                }
                
                // Selected location info
                if viewModel.selectedPlace != nil {
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                        Text("ui.editProfile.3".localized)
                            .font(.label)
                            .foregroundStyle(Color.textSecondary)
                        Spacer()
                        Text(viewModel.timezoneDisplay)
                            .font(.label)
                            .foregroundStyle(Color.textSecondary)
                    }
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
