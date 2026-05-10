// ReadingView.swift
// Main reading screen

import SwiftUI

struct ReadingView: View {
    @Environment(AppStore.self) private var store
    @State private var vm = ReadingVM()
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.appBackground.ignoresSafeArea()
                
                Group {
                    if let profile = store.selectedProfile {
                        if let reading = vm.currentReading {
                            ReadingResultView(
                                scope: vm.selectedScope,
                                data: reading,
                                onRefresh: {
                                    await vm.fetchReading(for: profile)
                                }
                            )
                        } else if vm.isLoading {
                            VStack(spacing: Space.sm) {
                                SkeletonCard()
                                SkeletonCard()
                                SkeletonCard()
                            }
                            .padding(.horizontal, Space.sm)
                            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
                        } else if let error = vm.error {
                            ErrorStateView(message: error) {
                                await vm.fetchReading(for: profile)
                            }
                        } else {
                            VStack(spacing: Space.sm) {
                                SkeletonCard()
                                SkeletonCard()
                            }
                            .padding(.horizontal, Space.sm)
                            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
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
            .safeAreaInset(edge: .top) {
                if store.selectedProfile != nil {
                    scopeFilterBar
                        .padding(.horizontal, Space.sm)
                        .padding(.top, Space.xs)
                }
            }
        }
    }
    
    // MARK: - Components
    
    private var scopeFilterBar: some View {
        CardView(padding: Space.xs, cornerRadius: Radius.md, materialOpacity: 0.06) {
            HStack(spacing: 8) {
                ForEach(ReadingScope.allCases, id: \.self) { scope in
                    Button {
                        updateScope(scope)
                    } label: {
                        PremiumFilterChip(title: scope.displayName, isSelected: vm.selectedScope == scope)
                    }
                    .buttonStyle(ScaleButtonStyle())
                }
            }
        }
    }
    
    private var noProfileView: some View {
        PremiumActionCard(
            title: "ui.reading.0".localized,
            subtitle: "ui.reading.1".localized,
            icon: "person.crop.circle.badge.plus",
            label: "label.startHere".localized,
            accent: .accentPrimary,
            emphasized: true,
            showsChevron: false
        )
        .padding(.horizontal, Space.sm)
        .onTapGesture {
            NotificationCenter.default.post(
                name: .navigateToTab,
                object: nil,
                userInfo: ["tab": 3]
            )
        }
    }

    private func updateScope(_ scope: ReadingScope) {
        guard vm.selectedScope != scope else { return }

        vm.selectedScope = scope

        guard let profile = store.selectedProfile else { return }

        Task {
            await vm.changeScope(to: scope, for: profile)
        }
    }
}

// MARK: - Preview

#Preview {
    ReadingView()
        .environment(AppStore.shared)
        .preferredColorScheme(.dark)
}
