// JournalView.swift
// Reading journal and accountability

import SwiftUI

struct JournalView: View {
    @Environment(AppStore.self) private var store
    @State private var vm = JournalVM()
    @State private var selectedReading: JournalReading?
    @State private var entryDraft: String = ""
    @State private var outcomeDraft: JournalOutcome = .neutral
    @State private var voiceRecorder = VoiceRecorder()

    var body: some View {
        // Journal is pushed onto the caller's NavigationStack. A split view
        // nested inside it doubled the nav bar and swallowed the push, so
        // "New Entry" and existing entries never opened the editor.
        sidebar
            .navigationTitle("screen.journal".localized)
            .navigationBarTitleDisplayMode(.inline)
            .task(id: store.activeProfile?.id) {
                await vm.load(profile: store.activeProfile, isAuthenticated: store.isAuthenticated)
            }
            .refreshable {
                await vm.load(profile: store.activeProfile, isAuthenticated: store.isAuthenticated, forceRefresh: true)
            }
            .toolbar {
                // Always reachable, however long the list of entries gets.
                if vm.isLocalMode, let profile = store.activeProfile {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button {
                            startNewEntry(profileId: profile.id)
                        } label: {
                            Image(systemName: "square.and.pencil")
                        }
                        .accessibilityLabel("ui.journal.4".localized)
                    }
                }
            }
            .navigationDestination(isPresented: Binding(
                get: { selectedReading != nil },
                set: { if !$0 { selectedReading = nil } }
            )) {
                if let reading = selectedReading {
                    journalEditor(reading: reading)
                }
            }
    }

    private var sidebar: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        PremiumScreenHeader(
                            eyebrow: "hero.journal.eyebrow".localized,
                            title: "hero.journal.title".localized,
                            subtitle: "hero.journal.body".localized,
                            accent: .accentPrimary,
                            chips: ["hero.journal.chip.0".localized, "hero.journal.chip.1".localized, "hero.journal.chip.2".localized]
                        )

                        if store.activeProfile == nil {
                            CardView {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("ui.journal.1".localized)
                                        .font(.headline)
                                    Text("ui.journal.2".localized)
                                        .font(.caption)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }
                        } else if let profile = store.activeProfile {
                            PremiumSectionHeader(
                                title: "section.journal.0.title".localized,
                                subtitle: vm.isLocalMode ? "tern.journal.0a".localized : "tern.journal.0b".localized
                            )

                            // Above the entries, so writing one never means
                            // scrolling past everything already written.
                            if vm.isLocalMode {
                                GradientButton("ui.journal.4".localized, icon: "plus") {
                                    startNewEntry(profileId: profile.id)
                                }
                            }

                            if let error = vm.error, !vm.isLoading {
                                PremiumStatusBanner(
                                    title: "Couldn't load your journal",
                                    message: error,
                                    tone: .critical,
                                    actionTitle: "Try again",
                                    action: {
                                        Task {
                                            await vm.load(profile: store.activeProfile, isAuthenticated: store.isAuthenticated, forceRefresh: true)
                                        }
                                    }
                                )
                            }

                            if !vm.prompts.isEmpty {
                                CardView {
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text("ui.journal.3".localized)
                                            .font(.headline)
                                        ForEach(vm.prompts, id: \.self) { prompt in
                                            Text("• \(prompt)")
                                                .font(.caption)
                                                .foregroundStyle(Color.textSecondary)
                                        }
                                    }
                                }
                            }
                            
                            if vm.isLoading {
                                PremiumStatusBanner(
                                    title: "common.loading".localized,
                                    message: "journal.loading.body".localized,
                                    tone: .info
                                )
                            } else if vm.readings.isEmpty {
                                PremiumStatusBanner(
                                    title: vm.isLocalMode ? "tern.journal.1a".localized : "tern.journal.1b".localized,
                                    message: vm.isLocalMode ? "tern.journal.2a".localized : "tern.journal.2b".localized,
                                    tone: .info
                                )
                            } else {
                                ForEach(vm.readings) { reading in
                                    Button {
                                        vm.saveError = nil
                                        selectedReading = reading
                                        entryDraft = reading.journalFull ?? ""
                                        outcomeDraft = JournalOutcome.from(reading.feedback)
                                    } label: {
                                        CardView {
                                            VStack(alignment: .leading, spacing: 8) {
                                                HStack {
                                                    Text(reading.scopeLabel ?? "Reading")
                                                        .font(.headline)
                                                    Spacer()
                                                    if let emoji = reading.feedbackEmoji, !emoji.isEmpty {
                                                        Text(emoji)
                                                    }
                                                }
                                                
                                                Text(reading.formattedDate ?? reading.date ?? "")
                                                    .font(.caption)
                                                    .foregroundStyle(Color.textSecondary)
                                                
                                                if let summary = reading.contentSummary, !summary.isEmpty {
                                                    Text(summary)
                                                        .font(.subheadline)
                                                        .lineLimit(2)
                                                }
                                                
                                                if let preview = reading.journalPreview, !preview.isEmpty {
                                                    Text(preview)
                                                        .font(.caption)
                                                        .foregroundStyle(Color.textSecondary)
                                                        .lineLimit(2)
                                                }
                                            }
                                        }
                                    }
                                    .buttonStyle(ScaleButtonStyle())
                                }
                            }
                        }
                    }
                    .padding()
                    .readableContainer()
                }
        }
    }

    @ViewBuilder
    private func journalEditor(reading: JournalReading) -> some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()

            ScrollView {
                VStack(spacing: 16) {
                    PremiumSectionHeader(
                        title: "section.journal.1.title".localized,
                        subtitle: "section.journal.1.subtitle".localized
                    )

                    Text(reading.scopeLabel ?? "Reading")
                        .font(.headline)

                    Text(reading.formattedDate ?? reading.date ?? "")
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)

                    Picker("ui.journal.5".localized, selection: $outcomeDraft) {
                        ForEach(JournalOutcome.allCases, id: \.self) { outcome in
                            Text(outcome.label).tag(outcome)
                        }
                    }
                    .pickerStyle(.segmented)

                    TextEditor(text: $entryDraft)
                        // TextEditor paints an opaque system background over
                        // the card styling below, leaving a black box.
                        .scrollContentBackground(.hidden)
                        .frame(minHeight: 240)
                        .padding(Space.sm)
                        .background(
                            RoundedRectangle(cornerRadius: Radius.sm)
                                .fill(Color.surfaceElevated)
                                .overlay(
                                    RoundedRectangle(cornerRadius: Radius.sm)
                                        .stroke(Color.borderSubtle, lineWidth: Stroke.hairline)
                                )
                        )

                    // Voice recording
                    HStack(spacing: 12) {
                        Button {
                            Task {
                                if !voiceRecorder.isAuthorized {
                                    await voiceRecorder.requestAuthorization()
                                }
                                if let text = voiceRecorder.toggle() {
                                    if !entryDraft.isEmpty && !entryDraft.hasSuffix(" ") {
                                        entryDraft += " "
                                    }
                                    entryDraft += text
                                }
                            }
                        } label: {
                            HStack(spacing: 6) {
                                Image(systemName: voiceRecorder.isRecording ? "tern.journal.3a".localized : "tern.journal.3b".localized)
                                    .font(.title2)
                                    .foregroundStyle(voiceRecorder.isRecording ? Color.negativeRed : Color.accentPrimary)
                                    .symbolEffect(.pulse, isActive: voiceRecorder.isRecording)

                                Text(voiceRecorder.isRecording ? "tern.journal.4a".localized : "tern.journal.4b".localized)
                                    .font(.subheadline.weight(.medium))
                            }
                        }
                        .buttonStyle(ScaleButtonStyle())

                        if voiceRecorder.isRecording, !voiceRecorder.transcript.isEmpty {
                            Text(voiceRecorder.transcript)
                                .font(.caption)
                                .foregroundStyle(.white.opacity(0.6))
                                .lineLimit(2)
                        }

                        Spacer()
                    }

                    // A failed save keeps the editor (and the words) open
                    // and says why, instead of closing as if it had worked.
                    if let saveError = vm.saveError {
                        PremiumStatusBanner(
                            title: "Couldn't save this entry",
                            message: saveError,
                            tone: .critical
                        )
                    }

                    GradientButton("ui.journal.6".localized, icon: "checkmark.circle.fill", isLoading: vm.isSaving) {
                        Task {
                            let saved = await vm.save(readingId: reading.id, entry: entryDraft, outcome: outcomeDraft)
                            guard saved else {
                                HapticManager.notification(.error)
                                return
                            }
                            HapticManager.notification(.success)
                            selectedReading = nil
                            await vm.load(profile: store.activeProfile, isAuthenticated: store.isAuthenticated, forceRefresh: true)
                        }
                    }
                    .disabled(vm.isSaving)
                }
                .padding()
                .readableContainer()
            }
        }
        .navigationTitle("screen.journalEntry".localized)
        .navigationBarTitleDisplayMode(.inline)
    }

    private func startNewEntry(profileId: Int) {
        Task {
            let draft = await vm.makeLocalDraft(profileId: profileId)
            vm.saveError = nil
            selectedReading = draft
            entryDraft = ""
            outcomeDraft = .neutral
        }
    }
}

#Preview {
    JournalView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
