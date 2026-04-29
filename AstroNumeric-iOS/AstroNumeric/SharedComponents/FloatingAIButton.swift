// FloatingAIButton.swift
// Floating action button for Cosmic Guide AI chat

import SwiftUI

struct FloatingAIButton: View {
    @State private var isShowingChat = false
    @State private var isPulsing = false
    @State private var isExpanded = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.horizontalSizeClass) private var hSizeClass
    @ScaledMetric(relativeTo: .body) private var bottomPadding: CGFloat = 96

    var body: some View {
        ZStack {
            // Outer aura ring – always visible, slow pulse
            if !reduceMotion {
                Circle()
                    .stroke(Color.cosmicPurple.opacity(0.35), lineWidth: 1.2)
                    .frame(width: isPulsing ? 70 : 54, height: isPulsing ? 70 : 54)
                    .opacity(isPulsing ? 0 : 0.9)
                    .animation(
                        .easeOut(duration: 2.4).repeatForever(autoreverses: false),
                        value: isPulsing
                    )
            }

            // Inner soft glow
            Circle()
                .fill(
                    RadialGradient(
                        colors: [Color.cosmicPurple.opacity(0.35), .clear],
                        center: .center,
                        startRadius: 4,
                        endRadius: 28
                    )
                )
                .frame(width: 44, height: 44)

            // Capsule pill that expands with sparkle + label
            Button {
                if isExpanded {
                    HapticManager.impact(.medium)
                    isShowingChat = true
                    isExpanded = false
                } else {
                    HapticManager.impact(.light)
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) {
                        isExpanded = true
                    }
                    Task {
                        try? await Task.sleep(for: .seconds(3))
                        withAnimation(.spring(response: 0.25, dampingFraction: 0.85)) {
                            isExpanded = false
                        }
                    }
                }
            } label: {
                HStack(spacing: 6) {
                    Image(systemName: "sparkles")
                        .font(.callout.weight(.semibold))
                        .symbolRenderingMode(.hierarchical)
                    if isExpanded {
                        Text("ui.floatingAIButton.0".localized)
                            .font(.footnote.weight(.semibold))
                            .transition(.opacity.combined(with: .scale(scale: 0.85)))
                    }
                }
                .foregroundStyle(.white)
                .padding(.horizontal, isExpanded ? 14 : 12)
                .padding(.vertical, 10)
                .background(
                    Capsule()
                        .fill(
                            LinearGradient(
                                colors: [
                                    Color.cosmicPurple,
                                    Color.cosmicPurple.opacity(0.75)
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .overlay(
                            Capsule().stroke(.white.opacity(0.25), lineWidth: Stroke.hairline)
                        )
                )
                .shadow(color: Color.cosmicPurple.opacity(0.45), radius: 14, y: 6)
                .contentShape(Capsule())
            }
            .buttonStyle(AccessibleButtonStyle())
            .accessibilityLabel(isExpanded ? "tern.floatingAIButton.0a".localized : "tern.floatingAIButton.0b".localized)
            .accessibilityHint("Tap to ask the Cosmic Guide")
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .bottomTrailing)
        .padding(.trailing, hSizeClass == .regular ? 28 : 16)
        // On iPad with `.sidebarAdaptable`, the bottom tab bar is gone — the FAB
        // only needs to clear the home indicator. On iPhone we add room for the
        // tab bar (~83pt) plus a comfortable visual gap, scaled with Dynamic Type.
        .padding(.bottom, hSizeClass == .regular ? 24 : bottomPadding)
        .onAppear { isPulsing = true }
        .fullScreenCover(isPresented: $isShowingChat) {
            CosmicGuideChatSheet(isPresented: $isShowingChat)
        }
    }
}

// MARK: - Cosmic Guide Chat Sheet

struct CosmicGuideChatSheet: View {
    @Binding var isPresented: Bool
    @Environment(AppStore.self) private var store
    
    @State private var messages: [FloatingChatMessage] = []
    @State private var inputText = ""
    @State private var isLoading = false
    
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil)
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                header
                
                // Messages
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            // Welcome message
                            if messages.isEmpty {
                                welcomeSection
                            }
                            
                            // Chat messages
                            ForEach(messages) { message in
                                FloatingChatBubbleView(message: message)
                                    .id(message.id)
                            }
                            
                            // Typing indicator
                            if isLoading {
                                FloatingTypingIndicator()
                                    .id("typing")
                            }
                        }
                        .padding()
                    }
                    .onChange(of: messages.count) { _, _ in
                        if let lastMessage = messages.last {
                            withAnimation {
                                proxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                }
                
                // Input
                chatInput
            }
        }
    }
    
    private var header: some View {
        HStack {
            Button {
                isPresented = false
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .font(.title2)
                    .foregroundStyle(Color.textSecondary)
            }
            .buttonStyle(AccessibleButtonStyle())
            .accessibilityLabel("Close Cosmic Guide")
            .accessibilityHint("Dismisses the chat sheet")
            
            Spacer()
            
            VStack(spacing: 2) {
                Text("ui.floatingAIButton.1".localized)
                    .font(.headline)
                Text("ui.floatingAIButton.2".localized)
                    .font(.label)
                    .foregroundStyle(Color.textSecondary)
            }
            
            Spacer()
            
            Button {
                messages.removeAll()
            } label: {
                Image(systemName: "arrow.counterclockwise.circle.fill")
                    .font(.title2)
                    .foregroundStyle(Color.textSecondary)
            }
            .buttonStyle(AccessibleButtonStyle())
            .accessibilityLabel("Clear messages")
            .accessibilityHint("Removes the current conversation")
        }
        .padding()
        .background(.ultraThinMaterial)
    }
    
    private var welcomeSection: some View {
        VStack(spacing: 16) {
            Text("🔮")
                .font(.system(.largeTitle))
            
            Text("ui.floatingAIButton.3".localized)
                .font(.title.bold())
            
            Text("ui.floatingAIButton.4".localized)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
            
            // Suggested prompts
            VStack(spacing: 8) {
                FloatingSuggestedPromptButton("What does today have in store?") {
                    sendMessage("What does today have in store for me?")
                }
                FloatingSuggestedPromptButton("Explain my life path number") {
                    sendMessage("What does my life path number mean?")
                }
                FloatingSuggestedPromptButton("Tell me about the current moon") {
                    sendMessage("Tell me about the current moon phase")
                }
            }
        }
        .padding(.top, 40)
    }
    
    private var chatInput: some View {
        HStack(spacing: 12) {
            TextField("ui.floatingAIButton.5".localized, text: $inputText, axis: .vertical)
                .textFieldStyle(.plain)
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(.ultraThinMaterial)
                )
                .lineLimit(1...4)
            
            Button {
                guard !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
                sendMessage(inputText)
                inputText = ""
            } label: {
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [.purple, .pink],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 44, height: 44)
                    
                    Image(systemName: "arrow.up")
                        .font(.body.bold())
                        .foregroundStyle(.white)
                }
            }
            .buttonStyle(AccessibleButtonStyle())
            .disabled(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isLoading)
            .accessibilityLabel("Send message")
            .accessibilityHint("Sends your message to Cosmic Guide")
        }
        .padding()
        .background(.ultraThinMaterial)
    }
    
    private func sendMessage(_ text: String) {
        let userMessage = FloatingChatMessage(id: UUID(), role: .user, content: text, timestamp: Date())
        messages.append(userMessage)
        
        HapticManager.impact(.light)
        
        Task {
            await fetchResponse(for: text)
        }
    }
    
    @MainActor
    private func fetchResponse(for query: String) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            // Build request with optional profile context
            let response: V2ApiResponse<ChatResponse> = try await APIClient.shared.fetch(
                .cosmicGuideChat(
                    message: query,
                    sunSign: store.selectedProfile?.sign,
                    moonSign: store.activeMoonSign,
                    risingSign: store.activeRisingSign,
                    history: nil
                )
            )
            
            let assistantMessage = FloatingChatMessage(
                id: UUID(),
                role: .assistant,
                content: response.data.response,
                timestamp: Date()
            )
            messages.append(assistantMessage)
            HapticManager.notification(.success)
        } catch {
            let errorMessage = FloatingChatMessage(
                id: UUID(),
                role: .assistant,
                content: "The cosmic signals are a bit fuzzy right now. Please try again in a moment! ✨",
                timestamp: Date()
            )
            messages.append(errorMessage)
        }
    }
}

// MARK: - Chat Message Model (Floating Button specific)

struct FloatingChatMessage: Identifiable {
    let id: UUID
    let role: FloatingMessageRole
    let content: String
    let timestamp: Date
    
    enum FloatingMessageRole {
        case user
        case assistant
    }
}

// MARK: - Chat Bubble View (Floating Button specific)

struct FloatingChatBubbleView: View {
    let message: FloatingChatMessage
    
    var body: some View {
        HStack {
            if message.role == .user { Spacer(minLength: 60) }
            
            VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 4) {
                Text(message.content)
                    .font(.body)
                    .padding(12)
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(message.role == .user ? 
                                  AnyShapeStyle(LinearGradient(colors: [.purple, .pink], startPoint: .leading, endPoint: .trailing)) : 
                                  AnyShapeStyle(Color.white.opacity(0.1)))
                    )
                    .foregroundStyle(message.role == .user ? .white : .primary)
                
                Text(message.timestamp, style: .time)
                    .font(.meta)
                    .foregroundStyle(Color.textSecondary)
            }
            
            if message.role == .assistant { Spacer(minLength: 60) }
        }
    }
}

// MARK: - Supporting Views (Floating Button specific)

struct FloatingSuggestedPromptButton: View {
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
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .frame(minHeight: 44) // Apple HIG minimum tap target
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(.ultraThinMaterial)
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .strokeBorder(Color.purple.opacity(0.3), lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
    }
}

struct FloatingTypingIndicator: View {
    @State private var dotCount = 0
    
    var body: some View {
        HStack {
            HStack(spacing: 4) {
                ForEach(0..<3) { index in
                    Circle()
                        .fill(Color.purple)
                        .frame(width: 8, height: 8)
                        .opacity(dotCount > index ? 1 : 0.3)
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
            Timer.scheduledTimer(withTimeInterval: 0.4, repeats: true) { timer in
                dotCount = (dotCount + 1) % 4
            }
        }
    }
}

// MARK: - Preview

#Preview {
    FloatingAIButton()
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .bottomTrailing)
        .padding()
        .background(Color.black)
        .environment(AppStore.shared)
}
