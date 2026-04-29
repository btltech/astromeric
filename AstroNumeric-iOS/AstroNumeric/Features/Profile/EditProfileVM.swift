// EditProfileVM.swift
// ViewModel for profile editing with location search

import SwiftUI
import MapKit
import CoreLocation
import Observation

enum TimeConfidence: String, CaseIterable {
    case exact = "exact"
    case approximate = "approximate"
    case unknown = "unknown"

    var displayTitle: String {
        switch self {
        case .exact: return "I know my exact birth time"
        case .approximate: return "I have an approximate time"
        case .unknown: return "I don't know my birth time"
        }
    }

    var shortLabel: String {
        switch self {
        case .exact: return "Exact"
        case .approximate: return "Approximate"
        case .unknown: return "Unknown"
        }
    }
}

@Observable
final class EditProfileVM: NSObject {
    // MARK: - Form Fields
    
    var name: String = ""
    var birthDate: Date = Date()
    var birthTime: Date = Date()
    var timeConfidence: TimeConfidence = .unknown
    var placeQuery: String = ""

    // Convenience accessor for legacy callers
    var knowsBirthTime: Bool {
        get { timeConfidence != .unknown }
        set { timeConfidence = newValue ? .exact : .unknown }
    }
    
    // MARK: - Location Search
    
    var placeSuggestions: [MKLocalSearchCompletion] = []
    var selectedPlace: PlaceSuggestion?
    var isSearchingPlaces: Bool = false
    var isGeocodingPlace: Bool = false
    var isUsingCurrentLocation: Bool = false
    var locationPermissionDenied: Bool = false
    
    // MARK: - State
    
    var isSaving: Bool = false
    var showError: Bool = false
    var errorMessage: String = ""
    var isEditing: Bool = false
    
    // MARK: - Private
    
    private let existingProfile: Profile?
    private let searchCompleter = MKLocalSearchCompleter()
    private var searchDebounceTask: Task<Void, Never>?
    private let locationManager = CLLocationManager()
    
    // MARK: - Computed Properties
    
    var isValid: Bool {
        !name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        selectedPlace != nil
    }
    
    var timezoneDisplay: String {
        selectedPlace?.timezone ?? "Unknown timezone"
    }
    
    // MARK: - Initialization
    
    init(profile: Profile? = nil) {
        self.existingProfile = profile
        self.isEditing = profile != nil
        
        super.init()
        
        searchCompleter.delegate = self
        searchCompleter.resultTypes = .address
        locationManager.delegate = self
        
        if let profile = profile {
            populateFromProfile(profile)
        }
    }
    
    private func populateFromProfile(_ profile: Profile) {
        name = profile.name
        
        // Parse date
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        if let date = dateFormatter.date(from: profile.dateOfBirth) {
            birthDate = date
        }
        
        // Parse time
        if let timeString = profile.timeOfBirth {
            timeConfidence = TimeConfidence(rawValue: profile.timeConfidence ?? "exact") ?? .exact
            if let time = Self.parseBirthTime(timeString) {
                // Combine date and time
                let calendar = Calendar.current
                let timeComponents = calendar.dateComponents([.hour, .minute, .second], from: time)
                if let combinedTime = calendar.date(bySettingHour: timeComponents.hour ?? 12,
                                                     minute: timeComponents.minute ?? 0,
                                                     second: timeComponents.second ?? 0,
                                                     of: Date()) {
                    birthTime = combinedTime
                }
            }
        } else {
            timeConfidence = .unknown
        }
        
        // Set place
        if let placeName = profile.placeOfBirth,
           let lat = profile.latitude,
           let lng = profile.longitude {
            placeQuery = placeName
            selectedPlace = PlaceSuggestion(
                id: UUID().uuidString,
                displayName: placeName,
                latitude: lat,
                longitude: lng,
                timezone: profile.timezone ?? TimeZone.current.identifier
            )
        }
    }
    
    // MARK: - Location Search
    
    func searchPlaces(query: String) {
        searchDebounceTask?.cancel()
        
        guard query.count >= 2 else {
            placeSuggestions = []
            isSearchingPlaces = false
            return
        }
        
        // Don't search if we already have a selected place with this name
        if selectedPlace != nil && query == selectedPlace?.displayName {
            return
        }
        
        // Clear selection when user starts typing new query
        selectedPlace = nil
        isSearchingPlaces = true
        
        searchDebounceTask = Task {
            try? await Task.sleep(nanoseconds: 150_000_000) // 150ms debounce
            guard !Task.isCancelled else { return }
            
            // Start completer search
            searchCompleter.queryFragment = query
            
            // Add 3-second timeout - if no results, try fallback geocoding
            try? await Task.sleep(nanoseconds: 3_000_000_000) // 3s timeout
            guard !Task.isCancelled else { return }
            
            // If still searching with no results, try fallback
            await MainActor.run {
                if self.isSearchingPlaces && self.placeSuggestions.isEmpty {
                    DebugLog.log("MKLocalSearchCompleter timeout, using fallback geocoding")
                    Task {
                        await self.fallbackGeocode(query: query)
                    }
                }
            }
        }
    }
    
    /// Fallback geocoding using CLGeocoder when MKLocalSearchCompleter hangs
    private func fallbackGeocode(query: String) async {
        let geocoder = CLGeocoder()
        
        do {
            let placemarks = try await geocoder.geocodeAddressString(query)
            
            await MainActor.run {
                isSearchingPlaces = false
                
                if let placemark = placemarks.first,
                   let location = placemark.location {
                    // Create a suggestion directly
                    let displayName = [
                        placemark.locality,
                        placemark.administrativeArea,
                        placemark.country
                    ].compactMap { $0 }.joined(separator: ", ")
                    
                    let place = PlaceSuggestion(
                        id: UUID().uuidString,
                        displayName: displayName.isEmpty ? query : displayName,
                        latitude: location.coordinate.latitude,
                        longitude: location.coordinate.longitude,
                        timezone: placemark.timeZone?.identifier ?? TimeZone.current.identifier
                    )
                    
                    // Auto-select the geocoded result
                    self.selectedPlace = place
                    self.placeQuery = place.displayName
                    HapticManager.notification(.success)
                }
            }
        } catch {
            await MainActor.run {
                isSearchingPlaces = false
                DebugLog.log("Fallback geocoding error: \(error)")
            }
        }
    }
    
    /// Select a search completion and geocode it to get coordinates
    func selectCompletion(_ completion: MKLocalSearchCompletion) {
        placeSuggestions = []
        isGeocodingPlace = true
        
        let displayName = [completion.title, completion.subtitle]
            .filter { !$0.isEmpty }
            .joined(separator: ", ")
        
        placeQuery = displayName
        
        Task {
            if let place = await geocodeCompletion(completion) {
                await MainActor.run {
                    selectedPlace = place
                    isGeocodingPlace = false
                    HapticManager.notification(.success)
                }
            } else {
                await MainActor.run {
                    isGeocodingPlace = false
                    showError = true
                    errorMessage = "Could not find location details. Please try again."
                }
            }
        }
    }
    
    private func geocodeCompletion(_ completion: MKLocalSearchCompletion) async -> PlaceSuggestion? {
        let request = MKLocalSearch.Request(completion: completion)
        let search = MKLocalSearch(request: request)
        
        do {
            let response = try await search.start()
            guard let item = response.mapItems.first else { return nil }
            
            let coordinate = item.placemark.coordinate
            let displayName = [completion.title, completion.subtitle]
                .filter { !$0.isEmpty }
                .joined(separator: ", ")
            
            return PlaceSuggestion(
                id: UUID().uuidString,
                displayName: displayName,
                latitude: coordinate.latitude,
                longitude: coordinate.longitude,
                timezone: item.timeZone?.identifier ?? TimeZone.current.identifier
            )
        } catch {
            DebugLog.log("Geocoding error: \(error)")
            return nil
        }
    }
    
    // MARK: - Current Location
    
    func useCurrentLocation() {
        let status = locationManager.authorizationStatus
        
        switch status {
        case .notDetermined:
            isUsingCurrentLocation = true
            locationPermissionDenied = false
            locationManager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways:
            isUsingCurrentLocation = true
            locationPermissionDenied = false
            locationManager.requestLocation()
        case .denied, .restricted:
            locationPermissionDenied = true
            showError = true
            errorMessage = "Location access denied. Please enable it in Settings to use this feature."
        @unknown default:
            break
        }
    }
    
    private func reverseGeocodeLocation(_ location: CLLocation) async {
        let geocoder = CLGeocoder()
        
        do {
            let placemarks = try await geocoder.reverseGeocodeLocation(location)
            guard let placemark = placemarks.first else {
                await MainActor.run {
                    isUsingCurrentLocation = false
                    showError = true
                    errorMessage = "Could not determine location name"
                }
                return
            }
            
            // Build display name
            var components: [String] = []
            if let city = placemark.locality {
                components.append(city)
            }
            if let state = placemark.administrativeArea {
                components.append(state)
            }
            if let country = placemark.country {
                components.append(country)
            }
            
            let displayName = components.joined(separator: ", ")
            
            await MainActor.run {
                placeQuery = displayName
                selectedPlace = PlaceSuggestion(
                    id: UUID().uuidString,
                    displayName: displayName,
                    latitude: location.coordinate.latitude,
                    longitude: location.coordinate.longitude,
                    timezone: placemark.timeZone?.identifier ?? TimeZone.current.identifier
                )
                isUsingCurrentLocation = false
                HapticManager.notification(.success)
            }
        } catch {
            await MainActor.run {
                isUsingCurrentLocation = false
                showError = true
                errorMessage = "Could not determine location: \(error.localizedDescription)"
            }
        }
    }
    
    // MARK: - Save
    
    func save(store: AppStore) async {
        guard isValid else {
            showError = true
            errorMessage = "Please fill in all required fields"
            return
        }
        
        await MainActor.run {
            isSaving = true
        }
        
        defer {
            Task { @MainActor in
                isSaving = false
            }
        }
        
        // Format date
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        let dateString = dateFormatter.string(from: birthDate)
        
        // Format time
        var timeString: String? = nil
        if timeConfidence != .unknown {
            let timeFormatter = DateFormatter()
            timeFormatter.dateFormat = "HH:mm:ss"
            timeString = timeFormatter.string(from: birthTime)
        }
        
        guard let place = selectedPlace else {
            await MainActor.run {
                showError = true
                errorMessage = "Please select a birth location"
            }
            return
        }
        
        let profileId: Int = {
            if let existingId = existingProfile?.id { return existingId }
            // In personal/guest mode generate a local-only id (negative).
            if AppConfig.personalMode || !store.isAuthenticated { return store.nextLocalProfileId() }
            // Authenticated creation uses server-generated ids, but we still need a placeholder.
            return Int.random(in: 1...999999)
        }()
        
        let newProfile = Profile(
            id: profileId,
            name: name.trimmingCharacters(in: .whitespacesAndNewlines),
            dateOfBirth: dateString,
            timeOfBirth: timeString,
            timeConfidence: timeConfidence.rawValue,
            placeOfBirth: place.displayName,
            latitude: place.latitude,
            longitude: place.longitude,
            timezone: place.timezone,
            houseSystem: existingProfile?.houseSystem ?? "Placidus"
        )
        
        do {
            if store.isAuthenticated && !AppConfig.personalMode {
                // Authenticated user - update via API
                if isEditing, let existingId = existingProfile?.id {
                    let request = UpdateProfileRequest(
                        name: newProfile.name,
                        timeOfBirth: newProfile.timeOfBirth,
                        timeConfidence: timeConfidence.rawValue,
                        placeOfBirth: newProfile.placeOfBirth,
                        latitude: newProfile.latitude,
                        longitude: newProfile.longitude,
                        timezone: newProfile.timezone,
                        houseSystem: newProfile.houseSystem
                    )
                    let _: V2ApiResponse<Profile> = try await APIClient.shared.fetch(.updateProfile(id: existingId, request))
                    
                    await MainActor.run {
                        store.upsertProfile(newProfile, select: true)
                    }
                } else {
                    // Create new profile
                    let request = CreateProfileRequest(
                        name: newProfile.name,
                        dateOfBirth: newProfile.dateOfBirth,
                        timeOfBirth: newProfile.timeOfBirth,
                        timeConfidence: timeConfidence.rawValue,
                        placeOfBirth: newProfile.placeOfBirth,
                        latitude: newProfile.latitude,
                        longitude: newProfile.longitude,
                        timezone: newProfile.timezone,
                        saveProfile: true
                    )
                    let response: V2ApiResponse<Profile> = try await APIClient.shared.fetch(.createProfile(request))
                    
                    await MainActor.run {
                        store.upsertProfile(response.data, select: true)
                    }
                }
            } else {
                // Personal/anonymous mode - store locally on-device
                await MainActor.run {
                    store.upsertProfile(newProfile, select: true)
                }
            }
            
            await MainActor.run {
                HapticManager.notification(.success)
            }
        } catch {
            await MainActor.run {
                showError = true
                errorMessage = "Failed to save profile: \(error.localizedDescription)"
            }
        }
    }
}

private extension EditProfileVM {
    static func parseBirthTime(_ timeString: String) -> Date? {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(identifier: "UTC")

        for format in ["HH:mm:ss", "HH:mm"] {
            formatter.dateFormat = format
            if let date = formatter.date(from: timeString) {
                return date
            }
        }

        return nil
    }
}

// MARK: - MKLocalSearchCompleterDelegate

extension EditProfileVM: MKLocalSearchCompleterDelegate {
    func completerDidUpdateResults(_ completer: MKLocalSearchCompleter) {
        // Show results immediately - no geocoding needed until user selects
        Task { @MainActor in
            self.placeSuggestions = Array(completer.results.prefix(5))
            self.isSearchingPlaces = false
        }
    }
    
    func completer(_ completer: MKLocalSearchCompleter, didFailWithError error: Error) {
        Task { @MainActor in
            isSearchingPlaces = false
            DebugLog.log("Search completer error: \(error)")
        }
    }
}

// MARK: - CLLocationManagerDelegate

extension EditProfileVM: CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.first else { return }
        
        Task {
            await reverseGeocodeLocation(location)
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor in
            isUsingCurrentLocation = false
            showError = true
            errorMessage = "Could not get your location: \(error.localizedDescription)"
        }
    }
    
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        let status = manager.authorizationStatus
        
        if status == .authorizedWhenInUse || status == .authorizedAlways {
            // Permission just granted, proceed with location request
            if isUsingCurrentLocation {
                manager.requestLocation()
            }
        } else if status == .denied || status == .restricted {
            Task { @MainActor in
                locationPermissionDenied = true
                isUsingCurrentLocation = false
            }
        }
    }
}

// MARK: - Place Suggestion Model

struct PlaceSuggestion: Identifiable, Equatable {
    let id: String
    let displayName: String
    let latitude: Double
    let longitude: Double
    let timezone: String
}
