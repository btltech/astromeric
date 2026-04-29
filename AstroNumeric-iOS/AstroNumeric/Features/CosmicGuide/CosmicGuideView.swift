// CosmicGuideView.swift
// AI chat interface for cosmic guidance with tone control.

import SwiftUI

struct CosmicGuideView: View {
    @Environment(AppStore.self) private var store
    @State private var vm = CosmicGuideVM()
    @State private var showTonePicker = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Messages
                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: 16) {
                                // Welcome message
                                if vm.messages.isEmpty {
                                    welcomeSection
                                }

                                if let error = vm.error, !error.isEmpty {
                                    errorBanner(error)
                                }
                                
                                // Chat messages
                                ForEach(vm.messages) { message in
                                    ChatBubbleView(message: message)
                                        .id(message.id)
                                }
                                
                                // Typing indicator
                                if vm.isLoading {
                                    TypingIndicator()
                                        .id("typing")
                                }
                            }
                            .padding()
                        }
                        .onChange(of: vm.messages.count) { _, _ in
                            if let lastMessage = vm.messages.last {
                                withAnimation {
                                    proxy.scrollTo(lastMessage.id, anchor: .bottom)
                                }
                            }
                        }
                    }
                    
                    // Tone picker (slides in above input)
                    if showTonePicker {
                        tonePicker
                            .transition(.move(edge: .bottom).combined(with: .opacity))
                    }
                    
                    // Input
                    chatInput
                }
            }
            .navigationTitle("screen.cosmicGuide".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        vm.clearHistory()
                    } label: {
                        Image(systemName: "trash")
                            .foregroundStyle(.white.opacity(0.7))
                    }
                    .buttonStyle(AccessibleButtonStyle())
                    .disabled(vm.messages.isEmpty)
                    .accessibilityLabel("Clear conversation")
                    .accessibilityHint("Deletes the current Cosmic Guide chat history")
                }
            }
        }
    }
    
    // MARK: - Welcome Section
    
    private var welcomeSection: some View {
        VStack(spacing: 16) {
            PremiumHeroCard(
                            eyebrow: "hero.cosmicGuide.eyebrow".localized,
                            title: "hero.cosmicGuide.title".localized,
                            bodyText: "hero.cosmicGuide.body".localized,
                            accent: [Color(hex: "1d0f33"), Color(hex: "5f33b1"), Color(hex: "c05b78")],
                            chips: ["hero.cosmicGuide.chip.0".localized, "hero.cosmicGuide.chip.1".localized, "hero.cosmicGuide.chip.2".localized, "hero.cosmicGuide.chip.3".localized]
                        )
            
            // Tone badge
            Button {
                withAnimation(.spring(response: 0.3)) {
                    showTonePicker.toggle()
                }
            } label: {
                HStack(spacing: 4) {
                    Text(vm.tone.emoji)
                    Text(vm.tone.label)
                        .font(.caption.weight(.medium))
                }
                .padding(.horizontal, 12)
                .frame(minHeight: 44)
                .background(Capsule().fill(.ultraThinMaterial))
            }
            .buttonStyle(.plain)
            
            // Suggested prompts
            VStack(spacing: 8) {
                ForEach(vm.suggestedPrompts, id: \.self) { prompt in
                    SuggestedPromptButton(prompt) {
                        send(prompt)
                    }
                }
            }

            VStack(spacing: 12) {
                calendarConsentCard
                biometricConsentCard
            }
        }
        .padding(.top, 40)
    }
    
    // MARK: - Tone Picker
    
    private var tonePicker: some View {
        HStack(spacing: 12) {
            ForEach(GuideTone.allCases) { tone in
                Button {
                    vm.tone = tone
                    withAnimation(.spring(response: 0.3)) {
                        showTonePicker = false
                    }
                    HapticManager.impact(.light)
                } label: {
                    VStack(spacing: 4) {
                        Text(tone.emoji)
                            .font(.title2)
                        Text(tone.label)
                            .font(.caption2.weight(.medium))
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(vm.tone == tone ? Color.purple.opacity(0.3) : Color.clear)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .strokeBorder(vm.tone == tone ? Color.purple : Color.white.opacity(0.2), lineWidth: 1)
                    )
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(.ultraThinMaterial)
    }
    
    // MARK: - Chat Input
    
    private var chatInput: some View {
        HStack(spacing: 12) {
            // Tone toggle
            Button {
                withAnimation(.spring(response: 0.3)) {
                    showTonePicker.toggle()
                }
            } label: {
                Text(vm.tone.emoji)
                    .font(.title3)
            }
            .buttonStyle(AccessibleButtonStyle())
            .accessibilityLabel("Guide tone")
            .accessibilityValue(vm.tone.label)
            .accessibilityHint("Changes how Cosmic Guide responds")

            Button {
                Task {
                    await vm.setCalendarContextEnabled(!vm.isCalendarContextEnabled)
                }
            } label: {
                Image(systemName: vm.isCalendarContextEnabled ? "tern.cosmicGuide.0a".localized : "tern.cosmicGuide.0b".localized)
                    .font(.title3)
                    .foregroundStyle(vm.isCalendarContextEnabled ? .green : .white.opacity(0.7))
            }
            .buttonStyle(AccessibleButtonStyle())
            .disabled(vm.isUpdatingCalendarContext)
            .accessibilityLabel("Calendar-aware guidance")
            .accessibilityValue(vm.isCalendarContextEnabled ? "tern.cosmicGuide.1a".localized : "tern.cosmicGuide.1b".localized)
            .accessibilityHint("Turns calendar context on or off for Cosmic Guide")

            Button {
                Task {
                    await vm.setBiometricContextEnabled(!vm.isBiometricContextEnabled)
                }
            } label: {
                Image(systemName: vm.isBiometricContextEnabled ? "tern.cosmicGuide.2a".localized : "tern.cosmicGuide.2b".localized)
                    .font(.title3)
                    .foregroundStyle(vm.isBiometricContextEnabled ? .pink : .white.opacity(0.7))
            }
            .buttonStyle(AccessibleButtonStyle())
            .disabled(vm.isUpdatingBiometricContext)
            .accessibilityLabel("Biometric-aware guidance")
            .accessibilityValue(vm.isBiometricContextEnabled ? "tern.cosmicGuide.3a".localized : "tern.cosmicGuide.3b".localized)
            .accessibilityHint("Turns optional Health data context on or off for Cosmic Guide")
            
            TextField("ui.cosmicGuide.6".localized, text: $vm.inputText, axis: .vertical)
                .textFieldStyle(.plain)
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(
                    RoundedRectangle(cornerRadius: 24)
                        .fill(.ultraThinMaterial)
                )
                .lineLimit(1...4)
            
            Button {
                send(vm.inputText)
            } label: {
                Image(systemName: "arrow.up.circle.fill")
                    .font(.title)
                    .foregroundStyle(.purple)
            }
            .buttonStyle(AccessibleButtonStyle())
            .disabled(!vm.canSend)
            .accessibilityLabel("Send message")
            .accessibilityHint("Sends your message to Cosmic Guide")
        }
        .padding(.horizontal)
        .padding(.vertical, 12)
        .background(.ultraThinMaterial)
    }
    
    // MARK: - Actions

    private var calendarConsentCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: vm.isCalendarContextEnabled ? "tern.cosmicGuide.4a".localized : "tern.cosmicGuide.4b".localized)
                    .foregroundStyle(vm.isCalendarContextEnabled ? .green : .cyan)
                    .font(.headline)

                VStack(alignment: .leading, spacing: 4) {
                    Text("ui.cosmicGuide.0".localized)
                        .font(.subheadline.bold())
                    Text("ui.cosmicGuide.1".localized)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }

                Spacer()

                Button(vm.isCalendarContextEnabled ? "tern.cosmicGuide.5a".localized : "tern.cosmicGuide.5b".localized) {
                    Task {
                        await vm.setCalendarContextEnabled(!vm.isCalendarContextEnabled)
                    }
                }
                .buttonStyle(.borderedProminent)
                .tint(vm.isCalendarContextEnabled ? .green : .cyan)
                .disabled(vm.isUpdatingCalendarContext)
            }

            if vm.isCalendarContextEnabled {
                Text("ui.cosmicGuide.2".localized)
                    .font(.caption2)
                    .foregroundStyle(.green.opacity(0.9))
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }

    private var biometricConsentCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: vm.isBiometricContextEnabled ? "tern.cosmicGuide.6a".localized : "tern.cosmicGuide.6b".localized)
                    .foregroundStyle(vm.isBiometricContextEnabled ? .pink : .red)
                    .font(.headline)

                VStack(alignment: .leading, spacing: 4) {
                    Text("ui.cosmicGuide.3".localized)
                        .font(.subheadline.bold())
                    Text("ui.cosmicGuide.4".localized)
                        .font(.caption)
                        .foregroundStyle(Color.textSecondary)
                }

                Spacer()

                Button(vm.isBiometricContextEnabled ? "tern.cosmicGuide.7a".localized : "tern.cosmicGuide.7b".localized) {
                    Task {
                        await vm.setBiometricContextEnabled(!vm.isBiometricContextEnabled)
                    }
                }
                .buttonStyle(.borderedProminent)
                .tint(vm.isBiometricContextEnabled ? .pink : .red)
                .disabled(vm.isUpdatingBiometricContext)
            }

            if vm.isBiometricContextEnabled {
                Text("ui.cosmicGuide.5".localized)
                    .font(.caption2)
                    .foregroundStyle(.pink.opacity(0.9))
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        )
    }

    private func errorBanner(_ text: String) -> some View {
        Text(text)
            .font(.caption)
            .foregroundStyle(.orange)
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.orange.opacity(0.12))
            )
    }

    private func send(_ text: String) {
        Task {
            await vm.sendMessage(
                text,
                profile: store.selectedProfile,
                moonSign: store.activeMoonSign,
                risingSign: store.activeRisingSign
            )
        }
    }
}

// NOTE: Profile.sign computed property is defined in Profile+Astrology.swift

// MARK: - Chat Bubble View

struct ChatBubbleView: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.role == .user {
                Spacer(minLength: 60)
            }
            
            Text(message.content)
                .padding(12)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(message.role == .user ?
                              Color.purple.opacity(0.3) :
                              Color.white.opacity(0.1))
                )
            
            if message.role == .assistant {
                Spacer(minLength: 60)
            }
        }
    }
}

// MARK: - Typing Indicator

struct TypingIndicator: View {
    @State private var animationPhase = 0
    
    var body: some View {
        HStack {
            HStack(spacing: 4) {
                ForEach(0..<3, id: \.self) { index in
                    Circle()
                        .fill(Color.purple.opacity(0.8))
                        .frame(width: 8, height: 8)
                        .scaleEffect(animationPhase == index ? 1.3 : 1.0)
                        .animation(.easeInOut(duration: 0.3), value: animationPhase)
                }
            }
            .padding(12)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.white.opacity(0.1))
            )
            Spacer()
        }
        .onAppear {
            Timer.scheduledTimer(withTimeInterval: 0.3, repeats: true) { _ in
                animationPhase = (animationPhase + 1) % 3
            }
        }
    }
}

// MARK: - Suggested Prompt Button

struct SuggestedPromptButton: View {
    let text: String
    let action: () -> Void
    
    init(_ text: String, action: @escaping () -> Void) {
        self.text = text
        self.action = action
    }
    
    var body: some View {
        Button(action: action) {
            Text(text)
                .font(.subheadline)
                .foregroundStyle(.white.opacity(0.9))
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .strokeBorder(Color.purple.opacity(0.5), lineWidth: 1)
                )
        }
    }
}

// MARK: - Preview

#Preview {
    CosmicGuideView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
