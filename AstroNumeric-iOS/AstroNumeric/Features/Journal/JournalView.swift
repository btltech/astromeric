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
    @State private var columnVisibility: NavigationSplitViewVisibility = .doubleColumn

    var body: some View {
        NavigationSplitView(columnVisibility: $columnVisibility) {
            sidebar
                .navigationTitle("screen.journal".localized)
                .navigationBarTitleDisplayMode(.inline)
                .task(id: store.activeProfile?.id) {
                    await vm.load(profile: store.activeProfile, isAuthenticated: store.isAuthenticated)
                }
                .refreshable {
                    await vm.load(profile: store.activeProfile, isAuthenticated: store.isAuthenticated, forceRefresh: true)
                }
        } detail: {
            NavigationStack {
                if let reading = selectedReading {
                    journalEditor(reading: reading)
                } else {
                    ContentUnavailableView(
                        "Pick an entry",
                        systemImage: "square.and.pencil",
                        description: Text("ui.journal.0".localized)
                    )
                }
            }
        }
        .navigationSplitViewStyle(.balanced)
    }

    private var sidebar: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        PremiumHeroCard(
                            eyebrow: "hero.journal.eyebrow".localized,
                            title: "hero.journal.title".localized,
                            bodyText: "hero.journal.body".localized,
                            accent: [Color(hex: "1a2038"), Color(hex: "4f4bb8"), Color(hex: "7a53b0")],
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
                subtitle: vm.isLocalMode
                                    ? "tern.journal.0a".localized : "tern.journal.0b".localized
            )

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
                                ProgressView("Loading journal...")
                                    .tint(.white)
                            } else if vm.readings.isEmpty {
                                CardView {
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text(vm.isLocalMode ? "tern.journal.1a".localized : "tern.journal.1b".localized)
                                            .font(.headline)
                                        Text(vm.isLocalMode
                                             ? "tern.journal.2a".localized : "tern.journal.2b".localized
                                        )
                                            .font(.caption)
                                            .foregroundStyle(Color.textSecondary)
                                    }
                                }
                            } else {
                                ForEach(vm.readings) { reading in
                                    Button {
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
                                    .buttonStyle(.plain)
                                }
                            }
                            
                            if vm.isLocalMode {
                                Button {
                                    let draft = vm.makeLocalDraft(profileId: profile.id)
                                    selectedReading = draft
                                    entryDraft = ""
                                    outcomeDraft = .neutral
                                } label: {
                                    Text("ui.journal.4".localized)
                                        .frame(maxWidth: .infinity)
                                }
                                .buttonStyle(.borderedProminent)
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
                        .frame(minHeight: 240)
                        .padding(8)
                        .background(Color.surfaceElevated)
                        .cornerRadius(12)

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
                                    .foregroundStyle(voiceRecorder.isRecording ? .red : .purple)
                                    .symbolEffect(.pulse, isActive: voiceRecorder.isRecording)

                                Text(voiceRecorder.isRecording ? "tern.journal.4a".localized : "tern.journal.4b".localized)
                                    .font(.subheadline.weight(.medium))
                            }
                        }
                        .buttonStyle(.plain)

                        if voiceRecorder.isRecording, !voiceRecorder.transcript.isEmpty {
                            Text(voiceRecorder.transcript)
                                .font(.caption)
                                .foregroundStyle(.white.opacity(0.6))
                                .lineLimit(2)
                        }

                        Spacer()
                    }

                    Button("ui.journal.6".localized) {
                        Task {
                            await vm.saveEntry(readingId: reading.id, entry: entryDraft)
                            await vm.saveOutcome(readingId: reading.id, outcome: outcomeDraft)
                            await vm.load(profile: store.activeProfile, isAuthenticated: store.isAuthenticated, forceRefresh: true)
                            selectedReading = nil
                        }
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
                .readableContainer()
            }
        }
        .navigationTitle("screen.journalEntry".localized)
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    JournalView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
