// ProfileExporter.swift
// Export and import profile data as JSON for backup and sharing

import SwiftUI
import UniformTypeIdentifiers

// MARK: - Export Format

struct ProfileExport: Codable {
    let version: String
    let exportedAt: Date
    let profile: ExportedProfile
    
    static let currentVersion = "1.0"
}

struct ExportedProfile: Codable {
    let name: String
    let dateOfBirth: String
    let timeOfBirth: String?
    let placeOfBirth: String?
    let latitude: Double?
    let longitude: Double?
    let timezone: String?
    let houseSystem: String?
    
    init(from profile: Profile) {
        self.name = profile.name
        self.dateOfBirth = profile.dateOfBirth
        self.timeOfBirth = profile.timeOfBirth
        self.placeOfBirth = profile.placeOfBirth
        self.latitude = profile.latitude
        self.longitude = profile.longitude
        self.timezone = profile.timezone
        self.houseSystem = profile.houseSystem
    }
    
    /// Creates a Profile with sentinel ID (-1) for imported profiles that need API creation
    func toProfile() -> Profile {
        Profile(
            id: -1, // Sentinel ID - indicates this needs to be created via API
            name: name,
            dateOfBirth: dateOfBirth,
            timeOfBirth: timeOfBirth,
            timeConfidence: nil,
            placeOfBirth: placeOfBirth,
            latitude: latitude,
            longitude: longitude,
            timezone: timezone,
            houseSystem: houseSystem ?? "Placidus"
        )
    }
}

// MARK: - Profile Exporter

@MainActor
class ProfileExporter: ObservableObject {
    @Published var exportError: String?
    @Published var importError: String?
    @Published var importedProfile: Profile?
    @Published var showImportConfirmation = false
    
    // MARK: - Export
    
    func exportProfile(_ profile: Profile) -> Data? {
        let exportData = ProfileExport(
            version: ProfileExport.currentVersion,
            exportedAt: Date(),
            profile: ExportedProfile(from: profile)
        )
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        
        do {
            return try encoder.encode(exportData)
        } catch {
            exportError = "Failed to export profile: \(error.localizedDescription)"
            return nil
        }
    }
    
    func exportAsFile(_ profile: Profile) -> URL? {
        guard let data = exportProfile(profile) else { return nil }
        
        let fileName = "\(profile.name.replacingOccurrences(of: " ", with: "_"))_profile.json"
        let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent(fileName)
        
        do {
            try data.write(to: tempURL)
            return tempURL
        } catch {
            exportError = "Failed to save export file: \(error.localizedDescription)"
            return nil
        }
    }
    
    // MARK: - Import
    
    func importProfile(from url: URL) -> Profile? {
        do {
            let data = try Data(contentsOf: url)
            return importProfile(from: data)
        } catch {
            importError = "Failed to read file: \(error.localizedDescription)"
            return nil
        }
    }
    
    func importProfile(from data: Data) -> Profile? {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        do {
            let export = try decoder.decode(ProfileExport.self, from: data)
            
            // Version check
            if export.version != ProfileExport.currentVersion {
                importError = "Profile format version mismatch (got \(export.version), expected \(ProfileExport.currentVersion))"
                // Still try to import - might be compatible
            }
            
            return export.profile.toProfile()
        } catch {
            importError = "Invalid profile format: \(error.localizedDescription)"
            return nil
        }
    }
    
    func validateImport(_ profile: Profile) -> [String] {
        var issues: [String] = []
        
        if profile.name.isEmpty {
            issues.append("Name is required")
        }
        
        if profile.dateOfBirth.isEmpty {
            issues.append("Date of birth is required")
        }
        
        // Validate date format
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        if dateFormatter.date(from: profile.dateOfBirth) == nil {
            issues.append("Invalid date format (expected YYYY-MM-DD)")
        }
        
        // Validate time format if present
        if let time = profile.timeOfBirth, !time.isEmpty {
            let timeFormatter = DateFormatter()
            timeFormatter.dateFormat = "HH:mm"
            if timeFormatter.date(from: time) == nil {
                timeFormatter.dateFormat = "HH:mm:ss"
                if timeFormatter.date(from: time) == nil {
                    issues.append("Invalid time format (expected HH:MM or HH:MM:SS)")
                }
            }
        }
        
        return issues
    }
    
    // MARK: - Export as Text
    
    func exportAsText(_ profile: Profile) -> String {
        var text = """
        🌟 AstroNumeric Profile
        
        Name: \(profile.name)
        Date of Birth: \(profile.dateOfBirth)
        """
        
        if let time = profile.timeOfBirth {
            text += "\nTime of Birth: \(time)"
        } else {
            text += "\nTime of Birth: Unknown (noon used for chart calculations)"
        }
        
        if let place = profile.placeOfBirth {
            text += "\nPlace of Birth: \(place)"
        }

        // Add data quality disclaimer
        switch profile.dataQuality {
        case .full:
            text += "\n\nChart Accuracy: Full — calculated from exact birth time and place."
        case .dateAndPlace:
            text += "\n\n⚠️ Chart Accuracy: Estimated — birth time unknown. Rising sign and house placements use noon as default and may be inaccurate."
        case .dateOnly:
            text += "\n\n⚠️ Chart Accuracy: Limited — only Sun sign is reliable. Birth place and time unknown."
        }
        
        text += "\n\n✨ Generated with AstroNumeric"
        
        return text
    }
}

// MARK: - Document Picker

struct ProfileImportPicker: UIViewControllerRepresentable {
    let onImport: (URL) -> Void
    
    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: [.json])
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIDocumentPickerViewController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(onImport: onImport)
    }
    
    class Coordinator: NSObject, UIDocumentPickerDelegate {
        let onImport: (URL) -> Void
        
        init(onImport: @escaping (URL) -> Void) {
            self.onImport = onImport
        }
        
        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            guard let url = urls.first else { return }
            
            // Access security-scoped resource
            guard url.startAccessingSecurityScopedResource() else { return }
            defer { url.stopAccessingSecurityScopedResource() }
            
            onImport(url)
        }
    }
}

// MARK: - Export/Import Buttons View

struct ProfileExportImportButtons: View {
    let profile: Profile
    @StateObject private var exporter = ProfileExporter()
    @State private var showShareSheet = false
    @State private var showImportPicker = false
    @State private var showImportConfirm = false
    @State private var pendingImport: Profile?
    @State private var validationIssues: [String] = []
    
    var body: some View {
        VStack(spacing: 12) {
            // Export button
            Button {
                if exporter.exportAsFile(profile) != nil {
                    showShareSheet = true
                }
            } label: {
                HStack {
                    Image(systemName: "square.and.arrow.up")
                    Text("Export Profile")
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(Color.purple.opacity(0.15))
                .foregroundStyle(.purple)
                .clipShape(RoundedRectangle(cornerRadius: 10))
            }
            
            // Import button
            Button {
                showImportPicker = true
            } label: {
                HStack {
                    Image(systemName: "square.and.arrow.down")
                    Text("Import Profile")
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(Color.blue.opacity(0.15))
                .foregroundStyle(.blue)
                .clipShape(RoundedRectangle(cornerRadius: 10))
            }
            
            // Copy as text
            Button {
                let text = exporter.exportAsText(profile)
                UIPasteboard.general.string = text
                HapticManager.notification(.success)
            } label: {
                HStack {
                    Image(systemName: "doc.on.doc")
                    Text("Copy as Text")
                }
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
            }
        }
        .sheet(isPresented: $showShareSheet) {
            if let url = exporter.exportAsFile(profile) {
                ShareSheet(items: [url])
            }
        }
        .sheet(isPresented: $showImportPicker) {
            ProfileImportPicker { url in
                if let imported = exporter.importProfile(from: url) {
                    validationIssues = exporter.validateImport(imported)
                    pendingImport = imported
                    showImportConfirm = true
                }
            }
        }
        .alert("Import Profile?", isPresented: $showImportConfirm) {
            Button("Cancel", role: .cancel) {
                pendingImport = nil
            }
            Button("Import") {
                if let imported = pendingImport {
                    // Copy profile data to clipboard for manual creation
                    // (Profile creation requires API call through onboarding flow)
                    let text = """
                    Imported Profile: \(imported.name)
                    Date of Birth: \(imported.dateOfBirth)
                    Time: \(imported.timeOfBirth ?? "Not set")
                    Place: \(imported.placeOfBirth ?? "Not set")
                    
                    Please create a new profile with these details.
                    """
                    UIPasteboard.general.string = text
                    HapticManager.notification(.success)
                }
                pendingImport = nil
            }
        } message: {
            if let imported = pendingImport {
                if validationIssues.isEmpty {
                    Text("Import profile for \(imported.name)?")
                } else {
                    Text("Import profile for \(imported.name)?\n\nWarnings:\n\(validationIssues.joined(separator: "\n"))")
                }
            }
        }
        .alert("Export Error", isPresented: .constant(exporter.exportError != nil)) {
            Button("OK") {
                exporter.exportError = nil
            }
        } message: {
            Text(exporter.exportError ?? "")
        }
        .alert("Import Error", isPresented: .constant(exporter.importError != nil)) {
            Button("OK") {
                exporter.importError = nil
            }
        } message: {
            Text(exporter.importError ?? "")
        }
    }
}

// MARK: - Preview

#Preview {
    ProfileExportImportButtons(profile: Profile(
        id: 1,
        name: "Test User",
        dateOfBirth: "1990-06-15",
        timeOfBirth: "14:30",
        timeConfidence: "exact",
        placeOfBirth: "New York, NY",
        latitude: 40.7128,
        longitude: -74.0060,
        timezone: "America/New_York",
        houseSystem: "Placidus"
    ))
    .padding()
    .preferredColorScheme(.dark)
}
