// ProfileExporter.swift
// Export and import profile data as JSON for backup and sharing

import SwiftUI
import UniformTypeIdentifiers

// MARK: - Export Format

struct ProfileExport: Codable {
    let version: String
    let exportedAt: Date
    let isRedacted: Bool?
    let profile: ExportedProfile
    
    static let currentVersion = "1.1"
}

struct ExportedProfile: Codable {
    let name: String
    let dateOfBirth: String
    let timeOfBirth: String?
    let timeConfidence: String?
    let placeOfBirth: String?
    let latitude: Double?
    let longitude: Double?
    let timezone: String?
    let houseSystem: String?
    
    init(from profile: Profile) {
        self.name = profile.name
        self.dateOfBirth = profile.dateOfBirth
        self.timeOfBirth = profile.timeOfBirth
        self.timeConfidence = profile.timeConfidence
        self.placeOfBirth = profile.placeOfBirth
        self.latitude = profile.latitude
        self.longitude = profile.longitude
        self.timezone = profile.timezone
        self.houseSystem = profile.houseSystem
    }
    
    func toLocalProfile(id: Int) -> Profile {
        Profile(
            id: id,
            name: name,
            dateOfBirth: dateOfBirth,
            timeOfBirth: timeOfBirth,
            timeConfidence: timeConfidence ?? (timeOfBirth == nil ? "tern.profileExporter.0a".localized : "tern.profileExporter.0b".localized),
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

    func exportFileName(for profile: Profile) -> String {
        if AppStore.shared.hideSensitiveDetailsEnabled {
            return "private_profile.json"
        }

        let sanitizedName = profile.name
            .replacingOccurrences(of: " ", with: "_")
            .replacingOccurrences(of: "/", with: "-")
        return "\(sanitizedName)_profile.json"
    }
    
    func exportProfile(_ profile: Profile) -> Data? {
        let exportData = ProfileExport(
            version: ProfileExport.currentVersion,
            exportedAt: Date(),
            isRedacted: false,
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
        
        let fileName = exportFileName(for: profile)
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
            
            return export.profile.toLocalProfile(id: -1)
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
        let hideSensitive = AppStore.shared.hideSensitiveDetailsEnabled
        let exportedName = profile.displayName(
            hideSensitive: hideSensitive,
            role: .share
        )
        let exportedDOB = profile.maskedDateOfBirth(hideSensitive: hideSensitive)
        let exportedTime = profile.maskedBirthTime(hideSensitive: hideSensitive)
        let exportedPlace = profile.maskedBirthplace(hideSensitive: hideSensitive)

        var text = """
        🌟 AstroNumeric Profile
        
        Name: \(exportedName)
        Date of Birth: \(exportedDOB)
        """
        
        if profile.timeOfBirth != nil {
            text += "\nTime of Birth: \(exportedTime)"
        } else {
            text += "\nTime of Birth: Unknown (noon used for chart calculations)"
        }
        
        if profile.placeOfBirth != nil {
            text += "\nPlace of Birth: \(exportedPlace)"
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

        if hideSensitive {
            text += "\n\nSensitive details were hidden because privacy mode is enabled."
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
    @Environment(AppStore.self) private var store
    let profile: Profile?
    @StateObject private var exporter = ProfileExporter()
    @State private var showShareSheet = false
    @State private var showExportNotice = false
    @State private var showImportPicker = false
    @State private var showImportConfirm = false
    @State private var pendingImport: Profile?
    @State private var validationIssues: [String] = []
    
    var body: some View {
        VStack(spacing: 12) {
            if let profile {
                Button {
                    if store.hideSensitiveDetailsEnabled {
                        showExportNotice = true
                    } else if exporter.exportAsFile(profile) != nil {
                        showShareSheet = true
                    }
                } label: {
                    HStack {
                        Image(systemName: "square.and.arrow.up")
                        Text(store.hideSensitiveDetailsEnabled ? "tern.profileExporter.1a".localized : "tern.profileExporter.1b".localized)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(Color.purple.opacity(0.15))
                    .foregroundStyle(.purple)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                }
            }
            
            // Import button
            Button {
                showImportPicker = true
            } label: {
                HStack {
                    Image(systemName: "square.and.arrow.down")
                    Text("ui.profileExporter.0".localized)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(Color.blue.opacity(0.15))
                .foregroundStyle(.blue)
                .clipShape(RoundedRectangle(cornerRadius: 10))
            }
            
            if let profile {
                Button {
                    let text = exporter.exportAsText(profile)
                    UIPasteboard.general.string = text
                    HapticManager.notification(.success)
                } label: {
                    HStack {
                        Image(systemName: "doc.on.doc")
                        Text(store.hideSensitiveDetailsEnabled ? "tern.profileExporter.2a".localized : "tern.profileExporter.2b".localized)
                    }
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
                }
            }
        }
        .alert("ui.profileExporter.2".localized, isPresented: $showExportNotice) {
            Button("action.cancel".localized, role: .cancel) {}
            Button("ui.profileExporter.6".localized) {
                if let profile, exporter.exportAsFile(profile) != nil {
                    showShareSheet = true
                }
            }
        } message: {
            Text("ui.profileExporter.1".localized)
        }
        .sheet(isPresented: $showShareSheet) {
            if let profile, let url = exporter.exportAsFile(profile) {
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
        .alert("ui.profileExporter.3".localized, isPresented: $showImportConfirm) {
            Button("action.cancel".localized, role: .cancel) {
                pendingImport = nil
            }
            Button("ui.profileExporter.7".localized) {
                if let imported = pendingImport {
                    let importedProfile = Profile(
                        id: store.nextLocalProfileId(),
                        name: imported.name,
                        dateOfBirth: imported.dateOfBirth,
                        timeOfBirth: imported.timeOfBirth,
                        timeConfidence: imported.timeConfidence ?? (imported.timeOfBirth == nil ? "tern.profileExporter.3a".localized : "tern.profileExporter.3b".localized),
                        placeOfBirth: imported.placeOfBirth,
                        latitude: imported.latitude,
                        longitude: imported.longitude,
                        timezone: imported.timezone,
                        houseSystem: imported.houseSystem
                    )
                    store.upsertProfile(importedProfile, select: true)
                    HapticManager.notification(.success)
                }
                pendingImport = nil
            }
        } message: {
            if let imported = pendingImport {
                if validationIssues.isEmpty {
                    Text(String(format: "fmt.profileExporter.1".localized, "\(imported.name)"))
                } else {
                    Text(String(format: "fmt.profileExporter.0".localized, "\(imported.name)", "\(validationIssues.joined(separator: "\n"))"))
                }
            }
        }
        .alert("ui.profileExporter.4".localized, isPresented: .constant(exporter.exportError != nil)) {
            Button("action.ok".localized) {
                exporter.exportError = nil
            }
        } message: {
            Text(exporter.exportError ?? "")
        }
        .alert("ui.profileExporter.5".localized, isPresented: .constant(exporter.importError != nil)) {
            Button("action.ok".localized) {
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
    .environment(AppStore.shared)
    .preferredColorScheme(.dark)
}
