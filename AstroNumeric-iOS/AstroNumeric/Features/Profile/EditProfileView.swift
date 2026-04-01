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
                }
            }
            .navigationTitle(viewModel.isEditing ? "Edit Profile" : "Create Profile")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .alert("Error", isPresented: $viewModel.showError) {
                Button("OK") {}
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
            
            Text(viewModel.isEditing ? "Update your birth details" : "Enter your birth details")
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
        }
        .padding(.top)
    }
    
    // MARK: - Name Section
    
    private var nameSection: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Label("Name", systemImage: "person.fill")
                    .font(.headline)
                    .foregroundStyle(.purple)
                
                TextField("Your name", text: $viewModel.name)
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
                Label("Birth Date", systemImage: "calendar")
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
                Label("Birth Time", systemImage: "clock.fill")
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
                                      ? "largecircle.fill.circle"
                                      : "circle")
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
                        Label("This time will be treated as approximate. Rising sign and houses will be shown as estimated.", systemImage: "info.circle")
                            .font(.caption)
                            .foregroundStyle(.orange)
                    }
                } else {
                    Text("Calculations will use noon as a default. Rising sign and houses will be marked as estimated.")
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
                    Label("Birth Place", systemImage: "mappin.circle.fill")
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
                            Text("Current")
                                .font(.label)
                        }
                        .foregroundStyle(.purple)
                    }
                    .disabled(viewModel.isUsingCurrentLocation)
                }
                
                TextField("City, Country", text: $viewModel.placeQuery)
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
                        Text(viewModel.isGeocodingPlace ? "Getting location details..." : "Searching...")
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
                        Text("Location confirmed")
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
            viewModel.isEditing ? "Save Changes" : "Create Profile",
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
        placeOfBirth: "Los Angeles, CA",
        latitude: 34.0522,
        longitude: -118.2437,
        timezone: "America/Los_Angeles",
        houseSystem: "placidus"
    ))
    .environment(AppStore.shared)
    .preferredColorScheme(.dark)
}
