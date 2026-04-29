// PrivacyView.swift
// In-app privacy policy and data practices

import SwiftUI

struct PrivacyView: View {
    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil).ignoresSafeArea()
            ScrollView {
                VStack(spacing: 16) {
                    PremiumHeroCard(
                            eyebrow: "hero.privacy.eyebrow".localized,
                            title: "hero.privacy.title".localized,
                            bodyText: "hero.privacy.body".localized,
                            accent: [Color(hex: "191d38"), Color(hex: "5d49b6"), Color(hex: "2f7ea0")],
                            chips: ["hero.privacy.chip.0".localized, "hero.privacy.chip.1".localized, "hero.privacy.chip.2".localized]
                        )

                    PremiumSectionHeader(
                title: "section.privacy.0.title".localized,
                subtitle: "section.privacy.0.subtitle".localized
            )

                    ForEach(privacySections, id: \.title) { section in
                        PrivacyCard(section: section)
                    }
                    contactCard
                    Spacer(minLength: 32)
                }
                .padding()
                .readableContainer()
            }
        }
        .navigationTitle("screen.privacy".localized)
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Contact

    private var contactCard: some View {
        CardView {
            VStack(alignment: .leading, spacing: 10) {
                Label("ui.privacy.1".localized, systemImage: "envelope.fill")
                    .font(.headline)
                    .foregroundStyle(.purple)
                Text("ui.privacy.0".localized)
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
                Link("privacy@astromeric.app", destination: URL(string: "mailto:privacy@astromeric.app")!)
                    .font(.subheadline.bold())
                    .foregroundStyle(.purple)
            }
        }
    }

    // MARK: - Data

    private let privacySections: [PrivacySectionData] = [
        PrivacySectionData(
            icon: "person.fill",
            iconColor: .blue,
            title: "Data You Enter",
            bullets: [
                "Birth profile data you type into the app, including name, date of birth, birth time, birthplace, and optional coordinates.",
                "Friend or partner birth profiles that you add for compatibility and Cosmic Circle features.",
                "Journal entries, outcome tracking, and optional voice-journal transcripts you create inside the app.",
                "Notification preferences and, if registration succeeds, an Apple push token when you enable notifications.",
            ]
        ),
        PrivacySectionData(
            icon: "xmark.shield.fill",
            iconColor: .green,
            title: "What We Never Collect",
            bullets: [
                "We do not embed ad-tech or cross-app tracking SDKs in the iOS app.",
                "We do not sell or rent your profile data to advertisers.",
                "We do not pull your contacts, photos, or calendars unless you explicitly use a feature that asks for that permission.",
                "We do not write data into HealthKit.",
            ]
        ),
        PrivacySectionData(
            icon: "internaldrive.fill",
            iconColor: .orange,
            title: "How Data Is Stored",
            bullets: [
                "In the current personal-mode build, profiles, app preferences, local relationship history, habits, and most journal entries are stored on-device using app storage such as UserDefaults and local files.",
                "A local journal semantic index is stored on-device to support on-device recall inside Cosmic Guide.",
                "Widget data is copied into the app group container so the widget extension can read it.",
                "Response caches are stored locally on your device and expire after their configured TTL.",
                "Widget and notification freshness data is kept on-device so the app can refresh context without adding analytics tracking.",
                "If you export a backup file to iCloud Drive or another file provider, that exported copy is then governed by the service you chose.",
            ]
        ),
        PrivacySectionData(
            icon: "person.2.fill",
            iconColor: .pink,
            title: "Network Requests And Backend Use",
            bullets: [
                "Some features send profile data to the AstroMeric backend when you request server-backed forecasts, AI guidance, compatibility, friend sync, widget brief refresh, or notification registration.",
                "Production API traffic uses HTTPS.",
                "Friend records added in Cosmic Circle are stored by the backend so they can be retrieved later.",
                "The app currently does not include a dedicated third-party crash-reporting or analytics SDK such as Firebase or Mixpanel.",
            ]
        ),
        PrivacySectionData(
            icon: "hand.raised.fill",
            iconColor: .yellow,
            title: "Permissions",
            bullets: [
                "Notifications: if you allow notifications, the app may register a push token with the backend.",
                "Location: you can enter a place manually or ask the app to use current location to fill birth-place details.",
                "Calendar: calendar access is opt-in and only used by calendar-aware guidance features.",
                "HealthKit: biometric-aware guidance is opt-in and only requests read access when you enable that context inside Cosmic Guide. You can deny or revoke that permission in iOS Settings at any time.",
                "Microphone and Speech Recognition: only used when you record a voice journal entry.",
            ]
        ),
        PrivacySectionData(
            icon: "eye.slash.fill",
            iconColor: .purple,
            title: "Privacy Mode And Sharing",
            bullets: [
                "Hide Sensitive Details masks names, birth details, share cards, and some cached labels in the UI.",
                "Hide Sensitive Details is a presentation layer, not a separate local-only mode or a network kill switch.",
                "Privacy mode does not remove the underlying birth data needed to calculate charts or required server-backed results.",
                "Backup exports can still contain full birth details so the profile can be restored later, even when privacy mode is enabled.",
                "Plain-text copy and some share surfaces are redacted when privacy mode is on.",
            ]
        ),
        PrivacySectionData(
            icon: "trash.fill",
            iconColor: .red,
            title: "Deletion And Control",
            bullets: [
                "You can remove a profile from the app from the Profile screen.",
                "Because this build is local-first, the cleanest full device reset is removing the app and its data from your device.",
                "If you want to ask about backend-held data such as push tokens or synced friend records, email privacy@astromeric.app.",
                "This screen describes the app's current behavior and may change as storage and sync features evolve.",
            ]
        ),
    ]
}

// MARK: - Privacy Section Model

struct PrivacySectionData {
    let icon: String
    let iconColor: Color
    let title: String
    let bullets: [String]
}

// MARK: - Privacy Card

struct PrivacyCard: View {
    let section: PrivacySectionData

    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Label(section.title, systemImage: section.icon)
                    .font(.headline)
                    .foregroundStyle(section.iconColor)
                    .accessibilityAddTraits(.isHeader)
                    .labelStyle(.titleAndIcon)

                Divider()

                VStack(alignment: .leading, spacing: 10) {
                    ForEach(section.bullets, id: \.self) { bullet in
                        HStack(alignment: .top, spacing: 10) {
                            Circle()
                                .fill(section.iconColor.opacity(0.4))
                                .frame(width: 6, height: 6)
                                .padding(.top, 6)
                                .accessibilityHidden(true)
                            Text(bullet)
                                .font(.subheadline)
                                .foregroundStyle(Color.textPrimary)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }
            }
        }
    }
}
