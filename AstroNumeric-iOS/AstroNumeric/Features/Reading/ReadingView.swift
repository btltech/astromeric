// ReadingView.swift
// Main reading screen

import SwiftUI

struct ReadingView: View {
    @Environment(AppStore.self) private var store
    @State private var vm = ReadingVM()
    
    var body: some View {
        NavigationStack {
            ZStack {
                // Cosmic background with element tint
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                Group {
                    if let profile = store.selectedProfile {
                        if let reading = vm.currentReading {
                            // Show reading result
                            ReadingResultView(
                                scope: vm.selectedScope,
                                data: reading,
                                onRefresh: {
                                    await vm.fetchReading(for: profile)
                                }
                            )
                        } else if vm.isLoading {
                            // Loading state
                            VStack(spacing: 16) {
                                SkeletonCard()
                                SkeletonCard()
                                SkeletonCard()
                            }
                            .padding()
                        } else if let error = vm.error {
                            // Error state
                            ErrorStateView(message: error) {
                                await vm.fetchReading(for: profile)
                            }
                        } else {
                            // Initial state - show loading and fetch
                            VStack(spacing: 16) {
                                SkeletonCard()
                                SkeletonCard()
                            }
                            .padding()
                            .onAppear {
                                Task.detached { @MainActor in
                                    await vm.fetchReading(for: profile)
                                }
                            }
                        }
                    } else {
                        // No profile selected
                        noProfileView
                    }
                }
            }
            .navigationTitle("screen.reading".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if store.selectedProfile != nil {
                    ToolbarItem(placement: .principal) {
                        scopePicker
                    }
                }
            }
        }
    }
    
    // MARK: - Components
    
    private var scopePicker: some View {
        Picker("ui.reading.2".localized, selection: $vm.selectedScope) {
            ForEach(ReadingScope.allCases, id: \.self) { scope in
                Text(scope.displayName).tag(scope)
            }
        }
        .pickerStyle(.segmented)
        .frame(width: 220)
        .onChange(of: vm.selectedScope) { _, newScope in
            if let profile = store.selectedProfile {
                Task {
                    await vm.changeScope(to: newScope, for: profile)
                }
            }
        }
    }
    
    private var noProfileView: some View {
        VStack(spacing: 20) {
            Text("🌟")
                .font(.system(.largeTitle))
            
            Text("ui.reading.0".localized)
                .font(.title2.bold())
            
            Text("ui.reading.1".localized)
                .font(.subheadline)
                .foregroundStyle(Color.textSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            GradientButton("Get Started", icon: "plus") {
                NotificationCenter.default.post(
                    name: .navigateToTab,
                    object: nil,
                    userInfo: ["tab": 3]
                )
            }
            .frame(width: 200)
        }
        .padding()
    }
}

// MARK: - Preview

#Preview {
    ReadingView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
