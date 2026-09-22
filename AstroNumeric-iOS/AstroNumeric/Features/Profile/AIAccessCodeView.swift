// AIAccessCodeView.swift
// Owner-only sheet for entering the private AI access code.

import SwiftUI

/// Reached by tapping the version line seven times in Support. Everyone else
/// keeps the built-in responses, so their questions never reach the AI provider.
struct AIAccessCodeView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var code = ""
    @State private var saveFailed = false

    private var isEnabled: Bool { AIAccessCode.current() != nil }

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    SecureField("Access code", text: $code)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                } header: {
                    Text("AI access")
                } footer: {
                    Text(isEnabled
                         ? "Live AI is on for this device. Clearing the code returns it to the built-in answers."
                         : "Without a code this device uses the built-in answers and sends nothing to the AI provider.")
                }

                if saveFailed {
                    Text("Couldn't save the code to the Keychain.")
                        .foregroundStyle(.red)
                        .font(.footnote)
                }

                if isEnabled {
                    Button("Turn off live AI", role: .destructive) {
                        AIAccessCode.clear()
                        code = ""
                        dismiss()
                    }
                }
            }
            .navigationTitle("AI access")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        if AIAccessCode.set(code) {
                            dismiss()
                        } else {
                            saveFailed = true
                        }
                    }
                    .disabled(code.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
        }
    }
}

#Preview {
    AIAccessCodeView()
}
