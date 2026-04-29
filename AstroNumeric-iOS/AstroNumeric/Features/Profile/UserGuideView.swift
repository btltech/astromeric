// UserGuideView.swift
// Comprehensive in-app user guide for AstroNumeric

import SwiftUI

struct UserGuideView: View {
    @State private var expandedSection: String? = nil

    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil).ignoresSafeArea()
            ScrollView {
                VStack(spacing: 16) {
                    PremiumHeroCard(
                            eyebrow: "hero.userGuide.eyebrow".localized,
                            title: "hero.userGuide.title".localized,
                            bodyText: "hero.userGuide.body".localized,
                            accent: [Color(hex: "191f39"), Color(hex: "4660be"), Color(hex: "7a58b3")],
                            chips: ["hero.userGuide.chip.0".localized, "hero.userGuide.chip.1".localized, "hero.userGuide.chip.2".localized]
                        )

                    PremiumSectionHeader(
                title: "section.userGuide.0.title".localized,
                subtitle: "section.userGuide.0.subtitle".localized
            )

                    ForEach(guide, id: \.title) { section in
                        GuideSection(
                            section: section,
                            isExpanded: expandedSection == section.title,
                            onTap: {
                                withAnimation(.spring(response: 0.35)) {
                                    expandedSection = expandedSection == section.title ? nil : section.title
                                }
                                HapticManager.impact(.light)
                            }
                        )
                    }
                    Spacer(minLength: 32)
                }
                .padding()
                .readableContainer()
            }
        }
        .navigationTitle("screen.userGuide".localized)
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Guide Data

    private let guide: [GuideSectionData] = [
        GuideSectionData(
            title: "Getting Started",
            icon: "star.circle.fill",
            iconColor: .purple,
            items: [
                GuideItem(heading: "Create your profile",
                          body: "Go to Profile → Create Profile. Enter your full name, exact birth date, birth time (if known), and birthplace. The more accurate your data, the more precise your readings."),
                GuideItem(heading: "Why birth time matters",
                          body: "Birth time determines your Ascendant (Rising sign) and house cusps — two of the most personal layers of your chart. Without it, AstroNumeric uses noon as a default and hides house-dependent features."),
                GuideItem(heading: "Multi-profile support",
                          body: "You can add multiple profiles — for yourself, your partner, family members, or celebrities. Switch between them with a single tap in the Profile screen."),
            ]
        ),
        GuideSectionData(
            title: "Home & Daily Reading",
            icon: "sun.max.fill",
            iconColor: .orange,
            items: [
                GuideItem(heading: "What is a daily reading?",
                          body: "Every day, AstroNumeric combines forecast scoring, your personal day number, and current lunar context into a reading with section-by-section themes. Refresh by pulling down on the Home screen."),
                GuideItem(heading: "Morning Brief",
                          body: "Morning Brief is a short bullet summary used in Daily Guide, widgets, and the brief notification. The app refreshes it on launch and when returning to the foreground, while widget refresh timing is still partly controlled by iOS."),
                GuideItem(heading: "Personal Day Number",
                          body: "Calculated from your birth month/day plus today's date. It sets the numerology tone for the day: a 1 day favors new starts, a 6 day favors care and responsibility, and so on."),
            ]
        ),
        GuideSectionData(
            title: "Numerology",
            icon: "number.circle.fill",
            iconColor: .indigo,
            items: [
                GuideItem(heading: "Life Path Number",
                          body: "Your most important number — derived from your full birth date. It describes your core purpose and the broad themes you'll encounter throughout life."),
                GuideItem(heading: "Expression Number",
                          body: "Derived from all the letters in your full birth name using the Pythagorean or Chaldean chart. It reveals your natural talents and how you express yourself to the world."),
                GuideItem(heading: "Soul Urge Number",
                          body: "Calculated from the vowels in your name. This is your inner motivation — the desires that drive you even when you can't fully articulate them."),
                GuideItem(heading: "Personality Number",
                          body: "Derived from the consonants in your name. It describes the face you show the world — your social mask."),
                GuideItem(heading: "Pythagorean vs Chaldean",
                          body: "Pythagorean (1–9) is the modern Western standard. Chaldean (1–8, no 9) is the ancient Babylonian system that treats 9 as sacred. Toggle between them using the switch at the top of the Numerology screen — each produces different calculations."),
                GuideItem(heading: "Personal Year & Month",
                          body: "Your personal year resets every birthday. Add your birth month + birth day + current year and reduce to a single digit. Your personal month adds the calendar month on top."),
            ]
        ),
        GuideSectionData(
            title: "Birth Chart",
            icon: "moon.stars.fill",
            iconColor: .blue,
            items: [
                GuideItem(heading: "Reading your chart",
                          body: "The wheel shows all 10 planets plus the Ascendant placed in signs and houses. Tap any planet to see its sign, house, and interpretation."),
                GuideItem(heading: "Planets",
                          body: "Sun = identity, Moon = emotions, Mercury = communication, Venus = love & beauty, Mars = drive, Jupiter = expansion, Saturn = discipline, Uranus = innovation, Neptune = dreams, Pluto = transformation."),
                GuideItem(heading: "Signs",
                          body: "The 12 zodiac signs each carry a unique energy. The sign a planet is in colours how that planet expresses itself — Mars in Aries is direct and combative; Mars in Libra is diplomatic and indirect."),
                GuideItem(heading: "Houses",
                          body: "The 12 houses represent areas of life. House 1 = self & appearance, 2 = money, 3 = communication, 4 = home, 5 = creativity, 6 = health, 7 = partnerships, 8 = transformation, 9 = philosophy, 10 = career, 11 = communities, 12 = hidden realms."),
                GuideItem(heading: "Aspects",
                          body: "Aspects are angular relationships between planets. Conjunctions (0°) merge energies. Trines (120°) are harmonious. Squares (90°) create tension. Oppositions (180°) require balance. Sextiles (60°) offer opportunities."),
            ]
        ),
        GuideSectionData(
            title: "Compatibility",
            icon: "heart.fill",
            iconColor: .pink,
            items: [
                GuideItem(heading: "Synastry",
                          body: "Synastry overlays two birth charts to reveal how two people's energies interact. Strong conjunctions between one person's Sun and another's Moon, for example, suggest deep emotional resonance."),
                GuideItem(heading: "Cosmic Circle",
                          body: "Add friends and family in the Relationships tab. Cosmic Circle friend records sync through the backend so they can be fetched again later, while saved compatibility history in Relationships stays on this device. AstroNumeric calculates an overall compatibility score based on key synastry aspects, life path resonance, and element balance."),
                GuideItem(heading: "What the score means",
                          body: "80–100%: Exceptional cosmic alignment. 60–80%: Strong compatibility with some growth areas. Below 60%: Challenging but growth-oriented connections. No score predicts relationship success — only your choices do."),
            ]
        ),
        GuideSectionData(
            title: "Year Ahead",
            icon: "calendar.circle.fill",
            iconColor: .teal,
            items: [
                GuideItem(heading: "Solar Return",
                          body: "Your solar return is the moment the Sun returns to its exact birth position each year — roughly your birthday. AstroNumeric shows the solar return chart and its themes for the year ahead."),
                GuideItem(heading: "Life Phase",
                          body: "Based on key astrological cycles (Saturn Return at ~29, Uranus Opposition at ~42, Chiron Return at ~50), AstroNumeric places you in your current cosmic chapter with a narrative about what this phase calls for."),
                GuideItem(heading: "Eclipses",
                          body: "Eclipses are supercharged New and Full Moons that tend to trigger significant changes in the houses they fall in. AstroNumeric shows which of your natal planets are activated."),
                GuideItem(heading: "Monthly Forecast",
                          body: "12 months are laid out ahead of you, each showing your personal month number, key planetary transits, and seasonal themes."),
            ]
        ),
        GuideSectionData(
            title: "Tools & Features",
            icon: "wand.and.stars",
            iconColor: .mint,
            items: [
                GuideItem(heading: "Calculated vs interpretive",
                          body: "Tools labeled Calculated are driven directly by astrology or numerology math. Hybrid tools mix calculated signals with guidance. Interpretive tools are reflective prompts rather than direct chart calculations."),
                GuideItem(heading: "Tarot",
                          body: "Daily single-card pulls or three-card spreads for reflection. Tarot is an interpretive tool, not a chart calculation."),
                GuideItem(heading: "Oracle",
                          body: "Short yes/no-style guidance shaped by your personal day number and the current moon phase."),
                GuideItem(heading: "Birthstone",
                          body: "Shows birthstones based on birth month and sign traditions. This is a reference guide rather than a live calculation."),
                GuideItem(heading: "Cosmic Habits",
                          body: "Daily habit tracker backed by numerological timing — certain days in your personal cycle are more suitable for making vs. breaking habits."),
                GuideItem(heading: "Journal",
                          body: "In the current personal-mode build, journal entries live on your device. A local semantic index helps Cosmic Guide surface relevant past entries when useful."),
                GuideItem(heading: "Widgets",
                          body: "Lock Screen and Home Screen widgets show your personal day number, moon context, and morning brief. They read data prepared by the main app, so opening the app occasionally helps keep them fresh. iOS still chooses the final refresh timing."),
            ]
        ),
        GuideSectionData(
            title: "Notifications",
            icon: "bell.fill",
            iconColor: .yellow,
            items: [
                GuideItem(heading: "Daily Reading Reminder",
                          body: "A daily reminder can be toggled quickly from Profile, and exact alert times can be managed from the Notifications screen. The app schedules these alerts, while iOS permission, Focus, and notification delivery rules still apply."),
                GuideItem(heading: "Morning Brief",
                          body: "The brief notification is scheduled after the app successfully refreshes a morning brief. In the current build it is scheduled for 7 AM, subject to iOS notification permission, Focus, and delivery rules."),
                GuideItem(heading: "Disabling notifications",
                          body: "Use the in-app Notifications screen to turn individual alert categories on or off. iOS Settings still controls whether the app is allowed to deliver notifications at all."),
            ]
        ),
        GuideSectionData(
            title: "Tips & Tricks",
            icon: "lightbulb.fill",
            iconColor: .orange,
            items: [
                GuideItem(heading: "Pull to refresh",
                          body: "All main screens support pull-to-refresh to force a network fetch, bypassing the cache."),
                GuideItem(heading: "Long press profiles",
                          body: "Long press any profile in the Profiles list to edit or delete it."),
                GuideItem(heading: "Context-aware AI",
                          body: "Cosmic Guide builds each response from your active profile, current chart context, and optional local context such as journal recall, calendar summaries, and biometrics when available."),
                GuideItem(heading: "Hide Sensitive Details",
                          body: "Enable this in Profile when you want names and birth details masked across the UI and share surfaces. It is a display/privacy layer, not a separate local-only mode, and server-backed features still use the profile data required to compute results."),
                GuideItem(heading: "Chaldean toggle",
                          body: "On the Numerology screen, tap the system toggle at the top to switch between Pythagorean and Chaldean calculations. Both sets of numbers are cached separately."),
            ]
        ),
    ]
}

// MARK: - Section Model

struct GuideSectionData {
    let title: String
    let icon: String
    let iconColor: Color
    let items: [GuideItem]
}

struct GuideItem {
    let heading: String
    let body: String
}

// MARK: - Guide Section View

struct GuideSection: View {
    let section: GuideSectionData
    let isExpanded: Bool
    let onTap: () -> Void

    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 0) {
                // Header row
                Button(action: onTap) {
                    HStack(spacing: 12) {
                        Image(systemName: section.icon)
                            .font(.title3)
                            .foregroundStyle(section.iconColor)
                            .frame(width: 28)
                            .accessibilityHidden(true)
                        Text(section.title)
                            .font(.headline)
                            .foregroundStyle(Color.primary)
                        Spacer()
                        Image(systemName: isExpanded ? "tern.userGuide.0a".localized : "tern.userGuide.0b".localized)
                            .font(.caption.bold())
                            .foregroundStyle(Color.textSecondary)
                            .accessibilityHidden(true)
                    }
                }
                .buttonStyle(.plain)
                .accessibilityLabel(section.title)
                .accessibilityHint(isExpanded ? "tern.userGuide.1a".localized : "tern.userGuide.1b".localized)
                .accessibilityAddTraits(.isButton)

                if isExpanded {
                    Divider().padding(.top, 12)
                    VStack(alignment: .leading, spacing: 16) {
                        ForEach(section.items, id: \.heading) { item in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.heading)
                                    .font(.subheadline.bold())
                                    .foregroundStyle(section.iconColor)
                                Text(item.body)
                                    .font(.subheadline)
                                    .foregroundStyle(Color.textPrimary)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                    .padding(.top, 12)
                    .transition(.opacity.combined(with: .move(edge: .top)))
                }
            }
        }
    }
}
