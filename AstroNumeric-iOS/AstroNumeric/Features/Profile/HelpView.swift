// HelpView.swift
// In-app help & FAQ

import SwiftUI

struct HelpView: View {
    @State private var expandedQuestion: String? = nil
    @State private var searchText = ""

    var filteredFAQ: [FAQSection] {
        if searchText.isEmpty { return faq }
        let q = searchText.lowercased()
        return faq.compactMap { section in
            let matchedItems = section.items.filter {
                $0.question.lowercased().contains(q) ||
                $0.answer.lowercased().contains(q)
            }
            return matchedItems.isEmpty ? nil : FAQSection(title: section.title, icon: section.icon, iconColor: section.iconColor, items: matchedItems)
        }
    }

    var body: some View {
        ZStack {
            CosmicBackgroundView(element: nil).ignoresSafeArea()
            VStack(spacing: 0) {
                // Search bar
                HStack(spacing: 10) {
                    Image(systemName: "magnifyingglass")
                        .foregroundStyle(Color.textSecondary)
                        .accessibilityHidden(true)
                    TextField("Search help topics…", text: $searchText)
                        .font(.subheadline)
                        .accessibilityLabel("Search help topics")
                    if !searchText.isEmpty {
                        Button {
                            searchText = ""
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundStyle(Color.textSecondary)
                        }
                        .accessibilityLabel("Clear search")
                    }
                }
                .padding(12)
                .background(.ultraThinMaterial)
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .padding([.horizontal, .top])

                ScrollView {
                    VStack(spacing: 16) {
                        if filteredFAQ.isEmpty {
                            emptySearch
                        } else {
                            ForEach(filteredFAQ, id: \.title) { section in
                                FAQSectionView(
                                    section: section,
                                    expandedQuestion: $expandedQuestion
                                )
                            }
                        }

                        supportCard
                        Spacer(minLength: 32)
                    }
                    .padding()
                }
            }
        }
        .navigationTitle("Help & FAQ")
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Empty state

    private var emptySearch: some View {
        CardView {
            VStack(spacing: 10) {
                Image(systemName: "questionmark.circle.fill")
                    .font(.system(size: 36))
                    .foregroundStyle(Color.textSecondary)
                    .accessibilityHidden(true)
                Text("No results for \"\(searchText)\"")
                    .font(.subheadline)
                    .foregroundStyle(Color.textSecondary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)
        }
    }

    // MARK: - Support card

    private var supportCard: some View {
        CardView {
            VStack(spacing: 12) {
                Label("Still need help?", systemImage: "bubble.left.and.bubble.right.fill")
                    .font(.headline)
                    .foregroundStyle(.purple)

                Text("Couldn't find what you were looking for? Our support team usually responds within 24 hours.")
                    .font(.subheadline)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(Color.textSecondary)

                Link(destination: URL(string: "mailto:support@astromeric.app")!) {
                    HStack {
                        Image(systemName: "envelope.fill")
                            .accessibilityHidden(true)
                        Text("Email Support")
                    }
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(Color.accentColor)
                    .foregroundStyle(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .accessibilityLabel("Email support at support@astromeric.app")
            }
        }
    }

    // MARK: - FAQ Data

    private let faq: [FAQSection] = [
        FAQSection(title: "Account & Profile", icon: "person.circle.fill", iconColor: .purple, items: [
            FAQItem(question: "How do I create a profile?",
                    answer: "Go to the Profile tab and tap 'Create Profile'. Enter your name, birth date, birth time (if known), and birthplace. The more accurate your data, the more precise your readings."),
            FAQItem(question: "Can I have multiple profiles?",
                    answer: "Yes! Tap the '+' button in the Profiles section to add another person. You might add a partner, family member, or even a celebrity to compare charts. Switch between profiles with a single tap."),
            FAQItem(question: "I don't know my birth time — what should I do?",
                    answer: "Toggle off 'I know my birth time' in the profile form. AstroNumeric will use noon as a default. Your Rising sign and house placements will be marked as estimated — they could be off by several signs depending on when you were born. Your Sun sign and all Numerology readings remain fully accurate. If you have an approximate time (e.g. 'early morning'), you can enter it and select Approximate — this is treated differently from a completely unknown time."),
            FAQItem(question: "How do I edit my birth details?",
                    answer: "Go to Profile, tap 'Edit' in the Birth Details card, make your changes, and tap Save. All your readings will automatically recalculate."),
            FAQItem(question: "How do I delete my data?",
                    answer: "To delete a profile from your device, long press it in the Profiles list and tap Delete. For server-side deletion of all data, email privacy@astromeric.app with 'Data Deletion Request'."),
        ]),
        FAQSection(title: "Readings & Accuracy", icon: "sparkles", iconColor: .orange, items: [
            FAQItem(question: "Why does my reading look the same as yesterday?",
                    answer: "If you're seeing cached data, pull down on the screen to force a refresh. Readings update each day — if the date hasn't changed since your last fetch, the content will be the same."),
            FAQItem(question: "How accurate are the astrological calculations?",
                    answer: "AstroNumeric uses the Swiss Ephemeris library, which is also used by professional astrological software. Planetary positions are accurate to within an arc-minute. However, the Rising sign and house cusps change by roughly 1° every 4 minutes — so their precision depends entirely on how accurate your birth time is. With an exact birth time, you get full professional-grade precision. Without one, planetary positions are still accurate, but Rising sign and houses are estimated."),
            FAQItem(question: "What is Chaldean numerology? How does it differ from Pythagorean?",
                    answer: "Pythagorean numerology (the modern standard) assigns values 1–9 to the alphabet in sequence. Chaldean (ancient Babylonian) uses a different 1–8 table and considers 9 sacred, never assigning it to a letter. Switch between them on the Numerology screen — they often produce different results for names."),
            FAQItem(question: "My life path number seems wrong.",
                    answer: "Check that your birth date is entered correctly (format YYYY-MM-DD). Pythagorean life path reduces each component (day, month, year) separately before adding — this is different from simply summing all digits. Chaldean sums all digits directly. If you've switched systems, your displayed number will change."),
        ]),
        FAQSection(title: "Charts & Astrology", icon: "moon.stars.fill", iconColor: .blue, items: [
            FAQItem(question: "Why do two people born on the same day have different astrological profiles?",
                    answer: "The Sun sign is the same for everyone born the same day (unless they're on a cusp). But the Rising sign (Ascendant) shifts by a full sign roughly every 2 hours. Someone born at 6am has a completely different Rising and house layout than someone born at 8pm on the same day. Birth location also matters — the same moment in London and Tokyo produces different Rising signs. That's why your exact birth time and place are so important for a complete picture."),
            FAQItem(question: "The chart wheel isn't showing house lines.",
                    answer: "House cusps require a birth time. If you haven't entered one, houses aren't calculated. Go to Profile → Edit and add your birth time to unlock full chart features."),
            FAQItem(question: "What house system does AstroNumeric use?",
                    answer: "The default is Placidus, the most widely used system in Western astrology. You can change to Whole Sign in your profile settings. Whole Sign places the Ascendant sign's 0° as the entire first house."),
            FAQItem(question: "Why is my Sun sign different from what I've always been told?",
                    answer: "If you were born near the 'cusp' (the last degree of one sign or first of another), your precise birth time and location affect which sign the Sun was actually in. AstroNumeric uses exact Swiss Ephemeris calculations — these are more precise than pop-astrology sun sign tables."),
        ]),
        FAQSection(title: "Notifications & Widgets", icon: "bell.circle.fill", iconColor: .yellow, items: [
            FAQItem(question: "How do I enable the daily reminder?",
                    answer: "Go to Profile → Settings and toggle on 'Daily Reading Reminder'. If prompted, allow notifications. You can set the reminder time in iOS Settings → Notifications → AstroNumeric."),
            FAQItem(question: "The morning brief widget shows old data.",
                    answer: "Open the app and fetch the Daily Brief at least once — this pushes fresh data to the widget. Widgets update on a system schedule (roughly every 15 minutes) so there may be a short delay."),
            FAQItem(question: "How do I add the widget to my Lock Screen?",
                    answer: "Long press your Lock Screen, tap Customize, then tap the Lock Screen. Tap the '+' button and search for 'AstroNumeric'. Choose the brief widget or personal day widget."),
        ]),
        FAQSection(title: "Compatibility & Friends", icon: "heart.circle.fill", iconColor: .pink, items: [
            FAQItem(question: "How do I add a friend for compatibility?",
                    answer: "Go to the Relationships tab → Cosmic Circle, then tap 'Add a Friend'. Enter their name, birth date, and relationship type. AstroNumeric will calculate your compatibility score."),
            FAQItem(question: "What does the compatibility percentage mean?",
                    answer: "The score combines synastry aspects (how your planets interact), life path resonance, and element balance. 80%+ is exceptional alignment. 60–80% is strong. Below 60% indicates more friction — which can drive growth. No score predicts a relationship's success."),
            FAQItem(question: "My friend data disappeared after an app update.",
                    answer: "Friend data is now stored on a persistent server-side volume and should survive updates. If you lost data, it may have been stored before this feature was added. Re-add your friends — future updates won't affect them."),
        ]),
        FAQSection(title: "Troubleshooting", icon: "wrench.and.screwdriver.fill", iconColor: .red, items: [
            FAQItem(question: "The app shows 'Unable to load' errors.",
                    answer: "Check your internet connection. If connected, the server may be temporarily down — try again in a minute. You can also pull down to retry. If the issue persists, email support@astromeric.app."),
            FAQItem(question: "How do I clear the cache?",
                    answer: "Go to Profile → System Diagnostics. You'll see the current cache sizes there. Currently, caches clear automatically after their TTL. A full cache flush can be done by reinstalling the app."),
            FAQItem(question: "The app crashed. How do I report it?",
                    answer: "Crash logs are automatically submitted to our crash reporting system. If you'd like to describe what happened, email support@astromeric.app with 'Crash Report' in the subject and the steps that led to the crash."),
            FAQItem(question: "Readings aren't updating.",
                    answer: "Try pulling down to refresh. If still stale, check your internet connection. Daily readings cache for 1 hour — if you've already fetched today's reading, you'll see it again until the hour expires or you force-refresh."),
        ]),
    ]
}

// MARK: - Models

struct FAQSection {
    let title: String
    let icon: String
    let iconColor: Color
    let items: [FAQItem]
}

struct FAQItem {
    let question: String
    let answer: String
}

// MARK: - FAQ Section View

struct FAQSectionView: View {
    let section: FAQSection
    @Binding var expandedQuestion: String?

    var body: some View {
        CardView {
            VStack(alignment: .leading, spacing: 12) {
                Label(section.title, systemImage: section.icon)
                    .font(.headline)
                    .foregroundStyle(section.iconColor)
                    .accessibilityAddTraits(.isHeader)

                Divider()

                VStack(alignment: .leading, spacing: 0) {
                    ForEach(section.items, id: \.question) { item in
                        VStack(alignment: .leading, spacing: 0) {
                            // Question row
                            Button {
                                withAnimation(.spring(response: 0.3)) {
                                    expandedQuestion = expandedQuestion == item.question ? nil : item.question
                                    HapticManager.impact(.light)
                                }
                            } label: {
                                HStack(alignment: .top, spacing: 10) {
                                    Text("Q")
                                        .font(.caption.bold())
                                        .foregroundStyle(section.iconColor)
                                        .frame(width: 16)
                                        .accessibilityHidden(true)
                                    Text(item.question)
                                        .font(.subheadline.weight(.medium))
                                        .foregroundStyle(Color.primary)
                                        .multilineTextAlignment(.leading)
                                    Spacer()
                                    Image(systemName: expandedQuestion == item.question ? "chevron.up" : "chevron.down")
                                        .font(.caption)
                                        .foregroundStyle(Color.textSecondary)
                                        .accessibilityHidden(true)
                                }
                                .padding(.vertical, 10)
                            }
                            .buttonStyle(.plain)
                            .accessibilityLabel(item.question)
                            .accessibilityHint(expandedQuestion == item.question ? "Collapse answer" : "Expand answer")

                            // Answer
                            if expandedQuestion == item.question {
                                HStack(alignment: .top, spacing: 10) {
                                    Text("A")
                                        .font(.caption.bold())
                                        .foregroundStyle(Color.textSecondary)
                                        .frame(width: 16)
                                        .accessibilityHidden(true)
                                    Text(item.answer)
                                        .font(.subheadline)
                                        .foregroundStyle(Color.textSecondary)
                                        .fixedSize(horizontal: false, vertical: true)
                                        .padding(.bottom, 10)
                                }
                                .transition(.opacity.combined(with: .move(edge: .top)))
                                .accessibilityLabel("Answer: \(item.answer)")
                            }

                            if item.question != section.items.last?.question {
                                Divider().padding(.leading, 26)
                            }
                        }
                    }
                }
            }
        }
    }
}
