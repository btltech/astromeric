// MoonEventsView.swift
// Upcoming moon events

import SwiftUI

struct MoonEventsView: View {
    @State private var events: [UpcomingMoonEvent] = []
    @State private var isLoading = false
    @State private var error: String?
    
    var body: some View {
        NavigationStack {
            ZStack {
                CosmicBackgroundView(element: nil)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        PremiumHeroCard(
                            eyebrow: "hero.moonEvents.eyebrow".localized,
                            title: "hero.moonEvents.title".localized,
                            bodyText: "hero.moonEvents.body".localized,
                            accent: [Color(hex: "13203a"), Color(hex: "4a63bb"), Color(hex: "6790b8")],
                            chips: ["hero.moonEvents.chip.0".localized, "hero.moonEvents.chip.1".localized, "hero.moonEvents.chip.2".localized]
                        )

                        if isLoading {
                            ProgressView("Loading moon events...")
                                .tint(.white)
                        } else if events.isEmpty {
                            CardView {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("ui.moonEvents.0".localized)
                                        .font(.headline)
                                    Text("ui.moonEvents.1".localized)
                                        .font(.caption)
                                        .foregroundStyle(Color.textSecondary)
                                }
                            }
                        } else {
                            PremiumSectionHeader(
                title: "section.moonEvents.0.title".localized,
                subtitle: "section.moonEvents.0.subtitle".localized
            )

                            ForEach(events) { event in
                                CardView {
                                    VStack(alignment: .leading, spacing: 6) {
                                        HStack {
                                            Text(event.type)
                                                .font(.headline)
                                            Spacer()
                                            Text(event.date)
                                                .font(.caption)
                                                .foregroundStyle(Color.textSecondary)
                                        }
                                        Text(event.phase)
                                            .font(.subheadline)
                                        Text(event.description)
                                            .font(.caption)
                                            .foregroundStyle(Color.textSecondary)
                                    }
                                }
                            }
                        }
                    }
                    .padding()
                    .readableContainer()
                }
            }
            .navigationTitle("screen.moonEvents".localized)
            .navigationBarTitleDisplayMode(.inline)
            .task {
                await load()
            }
        }
    }
    
    @MainActor
    private func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let response: V2ApiResponse<UpcomingMoonEventsResponse> = try await APIClient.shared.fetch(.upcomingMoonEvents)
            events = response.data.events
        } catch {
            self.error = error.localizedDescription
        }
    }
}

#Preview {
    MoonEventsView()
        .preferredColorScheme(.dark)
}
