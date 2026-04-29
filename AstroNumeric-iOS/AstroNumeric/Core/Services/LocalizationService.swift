// LocalizationService.swift
// Manages app localization and language switching

import SwiftUI

/// Supported languages in the app
enum AppLanguage: String, CaseIterable, Identifiable {
    case english = "en"
    case spanish = "es"
    case french = "fr"
    case romanian = "ro"
    case nepali = "ne"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .english: return "English"
        case .spanish: return "Español"
        case .french: return "Français"
        case .romanian: return "Română"
        case .nepali: return "नेपाली"
        }
    }
    
    var flag: String {
        switch self {
        case .english: return "🇺🇸"
        case .spanish: return "🇪🇸"
        case .french: return "🇫🇷"
        case .romanian: return "🇷🇴"
        case .nepali: return "🇳🇵"
        }
    }
}

/// Service for managing app localization
@Observable
final class LocalizationService {
    static let shared = LocalizationService()
    
    private let languageKey = "app_language"
    
    /// Refresh ID that changes when language changes - use this to force view re-renders
    var refreshID = UUID()
    
    /// Current app language
    var currentLanguage: AppLanguage {
        didSet {
            UserDefaults.standard.set(currentLanguage.rawValue, forKey: languageKey)
            updateBundle()
            // Force view refresh by changing the ID
            refreshID = UUID()
        }
    }
    
    /// Current localization bundle
    private(set) var bundle: Bundle = .main
    
    private init() {
        // Load saved language or detect system language
        if let savedCode = UserDefaults.standard.string(forKey: languageKey),
           let language = AppLanguage(rawValue: savedCode) {
            self.currentLanguage = language
        } else {
            // Use system language if supported, otherwise default to English
            let systemCode = Locale.current.language.languageCode?.identifier ?? "en"
            self.currentLanguage = AppLanguage(rawValue: systemCode) ?? .english
        }
        updateBundle()
    }
    
    /// Updates the localization bundle based on current language
    private func updateBundle() {
        if let path = Bundle.main.path(forResource: currentLanguage.rawValue, ofType: "lproj"),
           let bundle = Bundle(path: path) {
            self.bundle = bundle
        } else {
            self.bundle = .main
        }
    }
    
    /// Get localized string for key
    func localized(_ key: String, comment: String = "") -> String {
        // First try custom bundle, then fall back to main bundle NSLocalizedString
        let result = bundle.localizedString(forKey: key, value: nil, table: nil)
        // If bundle lookup returns the key itself, try NSLocalizedString with main bundle
        if result == key {
            return NSLocalizedString(key, bundle: .main, comment: comment)
        }
        return result
    }
    
    /// Get localized string with format arguments
    func localized(_ key: String, _ arguments: CVarArg...) -> String {
        let format = localized(key)
        return String(format: format, arguments: arguments)
    }
}

// MARK: - String Extension for Localization

extension String {
    /// Returns the localized version of this string key
    var localized: String {
        LocalizationService.shared.localized(self)
    }
    
    /// Returns the localized version with format arguments
    func localized(_ arguments: CVarArg...) -> String {
        let format = LocalizationService.shared.localized(self)
        return String(format: format, arguments: arguments)
    }
}

// MARK: - Environment Key

private struct LocalizationServiceKey: EnvironmentKey {
    static let defaultValue = LocalizationService.shared
}

extension EnvironmentValues {
    var localization: LocalizationService {
        get { self[LocalizationServiceKey.self] }
        set { self[LocalizationServiceKey.self] = newValue }
    }
}

// MARK: - Language Selector View

struct LanguageSelectorView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var localization = LocalizationService.shared
    @State private var selectedLanguage: AppLanguage
    
    init() {
        _selectedLanguage = State(initialValue: LocalizationService.shared.currentLanguage)
    }
    
    var body: some View {
        NavigationStack {
            List {
                ForEach(AppLanguage.allCases) { language in
                    Button {
                        selectedLanguage = language
                        localization.currentLanguage = language
                        HapticManager.selection()
                    } label: {
                        HStack {
                            Text(language.flag)
                                .font(.title2)
                            
                            Text(language.displayName)
                                .foregroundStyle(.primary)
                            
                            Spacer()
                            
                            if language == selectedLanguage {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundStyle(.purple)
                            }
                        }
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                }
            }
            .navigationTitle("settings.language".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("common.close".localized) {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - Compact Language Button

struct LanguageButton: View {
    @State private var showLanguageSelector = false
    private let localization = LocalizationService.shared
    
    var body: some View {
        Button {
            showLanguageSelector = true
            HapticManager.impact(.light)
        } label: {
            HStack(spacing: 4) {
                Text(localization.currentLanguage.flag)
                Image(systemName: "chevron.down")
                    .font(.caption2)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(
                Capsule()
                    .fill(.ultraThinMaterial)
            )
        }
        .sheet(isPresented: $showLanguageSelector) {
            LanguageSelectorView()
                .presentationDetents([.medium])
        }
    }
}

// MARK: - Language Selector Row (for settings)

struct LanguageSelectorRow: View {
    @State private var showLanguageSelector = false
    private let localization = LocalizationService.shared
    
    var body: some View {
        Button {
            showLanguageSelector = true
            HapticManager.impact(.light)
        } label: {
            HStack(spacing: 12) {
                Image(systemName: "globe")
                    .foregroundStyle(.blue)
                
                Text("settings.language".localized)
                    .font(.subheadline)
                    .foregroundStyle(.primary)
                
                Spacer()
                
                HStack(spacing: 4) {
                    Text(localization.currentLanguage.flag)
                    Text(localization.currentLanguage.displayName)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                    
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }
            }
        }
        .sheet(isPresented: $showLanguageSelector) {
            LanguageSelectorView()
                .presentationDetents([.medium])
        }
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 20) {
        LanguageButton()
        
        Text("common.loading".localized)
        Text("reading.title".localized("Daily"))
    }
    .padding()
    .preferredColorScheme(.dark)
}
