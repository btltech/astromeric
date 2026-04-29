package com.astromeric.android.feature.profile

import android.content.Intent
import android.net.Uri
import android.os.Build
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.BuildConfig
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumEmptyStateCard
import com.astromeric.android.core.ui.PremiumHeroCard

@Composable
fun HelpFaqScreen(
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var searchQuery by rememberSaveable { mutableStateOf("") }
    var expandedQuestion by rememberSaveable { mutableStateOf<String?>(null) }
    val filteredSections = remember(searchQuery) {
        filterFaqSections(searchQuery)
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = "Help",
            title = "Find the answer fast enough that friction does not build.",
            body = "Search when you know the issue. Browse by section when you need orientation or context.",
            chips = listOf("FAQ", "Search", "Support"),
        )

        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Search help topics") },
            singleLine = true,
        )

        if (filteredSections.isEmpty()) {
            PremiumEmptyStateCard(
                title = "No results for \"$searchQuery\"",
                message = "Try a feature name, notification, widget, chart, or privacy keyword.",
            )
        } else {
            filteredSections.forEach { section ->
                HelpSectionCard(
                    section = section,
                    expandedQuestion = expandedQuestion,
                    onToggle = { question ->
                        expandedQuestion = if (expandedQuestion == question) null else question
                    },
                )
            }
        }

        PremiumContentCard(
            title = "Still need help?",
            body = "Email support and include the screen, feature, and steps you were taking. No birth date, birth time, birthplace, journal text, or chart data is added automatically.",
        ) {
                Button(
                    onClick = {
                        launchSupportEmail(
                            context = context,
                            subject = "AstroNumeric Android Support",
                        )
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Email support")
                }
        }
    }
}

@Composable
fun UserGuideScreen(
    modifier: Modifier = Modifier,
) {
    var expandedSection by rememberSaveable { mutableStateOf<String?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = "Guide",
            title = "Understand AstroNumeric with confidence.",
            body = "Open the section that matches the question you have now instead of reading front to back.",
            chips = listOf("Getting started", "Tools", "Privacy"),
        )

        userGuideSections.forEach { section ->
            UserGuideSectionCard(
                section = section,
                expanded = expandedSection == section.title,
                onToggle = {
                    expandedSection = if (expandedSection == section.title) null else section.title
                },
            )
        }
    }
}

@Composable
private fun HelpSectionCard(
    section: HelpSectionData,
    expandedQuestion: String?,
    onToggle: (String) -> Unit,
) {
    PremiumContentCard(title = section.title) {
            section.items.forEach { item ->
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                    ) {
                        Text(
                            text = item.question,
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.weight(1f),
                        )
                        IconButton(onClick = { onToggle(item.question) }) {
                            Icon(
                                imageVector = if (expandedQuestion == item.question) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                                contentDescription = if (expandedQuestion == item.question) "Collapse answer" else "Expand answer",
                            )
                        }
                    }
                    if (expandedQuestion == item.question) {
                        Text(
                            text = item.answer,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
    }
}

@Composable
private fun UserGuideSectionCard(
    section: UserGuideSectionData,
    expanded: Boolean,
    onToggle: () -> Unit,
) {
    PremiumContentCard {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = section.title,
                    style = MaterialTheme.typography.titleMedium,
                )
                IconButton(onClick = onToggle) {
                    Icon(
                        imageVector = if (expanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                        contentDescription = if (expanded) "Collapse section" else "Expand section",
                    )
                }
            }
            if (expanded) {
                section.items.forEach { item ->
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(
                            text = item.heading,
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.SemiBold,
                        )
                        Text(
                            text = item.body,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
    }
}

private fun launchSupportEmail(
    context: android.content.Context,
    subject: String,
) {
    val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
        data = Uri.parse("mailto:support@astromeric.app")
        putExtra(Intent.EXTRA_SUBJECT, subject)
        putExtra(Intent.EXTRA_TEXT, supportEmailBody())
    }
    if (emailIntent.resolveActivity(context.packageManager) != null) {
        context.startActivity(emailIntent)
    }
}

private fun supportEmailBody(): String = buildString {
    appendLine("Please describe what happened:")
    appendLine()
    appendLine("Screen or feature:")
    appendLine("Expected result:")
    appendLine("Actual result:")
    appendLine("Steps to reproduce:")
    appendLine()
    appendLine("---")
    appendLine("Diagnostics")
    appendLine("Version ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})")
    appendLine("Android ${Build.VERSION.RELEASE}")
    appendLine("Device: ${Build.MANUFACTURER} ${Build.MODEL}")
    appendLine()
    append("No birth date, birth time, birthplace, journal text, or chart data is included automatically.")
}

private data class HelpSectionData(
    val title: String,
    val items: List<HelpItemData>,
)

private data class HelpItemData(
    val question: String,
    val answer: String,
)

private data class UserGuideSectionData(
    val title: String,
    val items: List<UserGuideItemData>,
)

private data class UserGuideItemData(
    val heading: String,
    val body: String,
)

private val helpSections = listOf(
    HelpSectionData(
        title = "Account & Profile",
        items = listOf(
            HelpItemData(
                question = "How do I create a profile?",
                answer = "Go to the Profile tab and tap Create Profile. Enter your name, birth date, birth time if known, and birthplace. The more accurate your data, the more precise your readings.",
            ),
            HelpItemData(
                question = "Can I have multiple profiles?",
                answer = "Yes. Use the New profile action in Profile to add another person. Switch between profiles with a single tap from the profile list.",
            ),
            HelpItemData(
                question = "I don't know my birth time. What should I do?",
                answer = "Use the profile form to mark the time as unknown or approximate. Sun sign and numerology remain accurate, while Rising sign and house placements become estimated when the time is not exact.",
            ),
            HelpItemData(
                question = "How do I edit my birth details?",
                answer = "Open Profile, pick the profile you want, then tap Edit. Saving recalculates the profile-backed readings automatically.",
            ),
            HelpItemData(
                question = "How do I delete my data?",
                answer = "Delete a profile from the profile list to remove it from the local Android store. For backend-held data such as push tokens or synced friend records, email privacy@astromeric.app.",
            ),
            HelpItemData(
                question = "What does Hide Sensitive Details do?",
                answer = "It masks names, birth details, share cards, and some cached labels across the UI. It does not remove the underlying data needed for chart calculations, and backup files still retain full details for restore.",
            ),
        ),
    ),
    HelpSectionData(
        title = "Readings & Accuracy",
        items = listOf(
            HelpItemData(
                question = "Why does my reading look the same as yesterday?",
                answer = "If you are seeing cached data, pull down on the screen to force a refresh. Readings update each day, so the content will stay the same until the date or refreshed data changes.",
            ),
            HelpItemData(
                question = "How accurate are the astrological calculations?",
                answer = "AstroNumeric uses Swiss Ephemeris calculations. Planetary positions are precise, but Rising sign and house accuracy still depend on how exact the birth time is.",
            ),
            HelpItemData(
                question = "What is Chaldean numerology?",
                answer = "Pythagorean is the modern 1 to 9 system. Chaldean uses a different 1 to 8 mapping and treats 9 as sacred. Switching systems changes some name-based calculations.",
            ),
            HelpItemData(
                question = "My life path number seems wrong.",
                answer = "Check that the birth date is correct and that you have not switched numerology systems. Pythagorean and Chaldean calculations can produce different values.",
            ),
        ),
    ),
    HelpSectionData(
        title = "Charts & Astrology",
        items = listOf(
            HelpItemData(
                question = "Why do two people born on the same day have different astrological profiles?",
                answer = "Birth time and birthplace change the Ascendant and the house layout. The Sun sign may match, but the chart structure can still differ a lot.",
            ),
            HelpItemData(
                question = "The chart wheel isn't showing house lines.",
                answer = "House cusps require a birth time. Add one in Profile to unlock full house-based chart features.",
            ),
            HelpItemData(
                question = "What house system does AstroNumeric use?",
                answer = "The default is Placidus. You can switch to Whole Sign in the profile editor if you prefer that system.",
            ),
            HelpItemData(
                question = "Why is my Sun sign different from what I expected?",
                answer = "If you were born near a cusp, exact birth time and birthplace can shift the Sun's actual sign placement compared with broad pop-astrology tables.",
            ),
        ),
    ),
    HelpSectionData(
        title = "Notifications & Widgets",
        items = listOf(
            HelpItemData(
                question = "How do I enable the daily reminder?",
                answer = "Use the quick toggle in Profile or open Notification settings to manage daily, moon, habit, transit, and timing alerts more precisely. Android system permission still controls delivery.",
            ),
            HelpItemData(
                question = "The morning brief widget shows old data.",
                answer = "Bring the app to the foreground with an active profile so it can refresh the latest brief and pass updated data to the widget. A short delay is still normal.",
            ),
            HelpItemData(
                question = "How do I add the widget?",
                answer = "Long press the launcher home screen, open widgets, search for AstroNumeric, and place the brief or personal day widget.",
            ),
        ),
    ),
    HelpSectionData(
        title = "Compatibility & Friends",
        items = listOf(
            HelpItemData(
                question = "How do I add a friend for compatibility?",
                answer = "Go to Relationships and add a comparison profile or friend record there. The app can then calculate compatibility using synastry, numerology, and timing data.",
            ),
            HelpItemData(
                question = "What does the compatibility percentage mean?",
                answer = "The score blends synastry aspects, life path resonance, and element balance. It points to alignment and friction, not a guaranteed outcome.",
            ),
            HelpItemData(
                question = "My friend data disappeared after an update.",
                answer = "Friend records and local relationship history are handled separately. Refresh the relationships view first. If the data does not return, contact support.",
            ),
        ),
    ),
    HelpSectionData(
        title = "Troubleshooting",
        items = listOf(
            HelpItemData(
                question = "The app shows unable to load errors.",
                answer = "Check your internet connection and retry. If the backend is temporarily unavailable, try again in a minute. If it persists, email support.",
            ),
            HelpItemData(
                question = "How do I clear the cache?",
                answer = "Most caches expire automatically. There is no one-tap full cache wipe in the current Android build, so reinstalling is the cleanest local reset.",
            ),
            HelpItemData(
                question = "The app crashed. How do I report it?",
                answer = "Relaunch the app and email support with Crash Report in the subject, your device model, Android version, and the steps that led to the crash.",
            ),
            HelpItemData(
                question = "Readings aren't updating.",
                answer = "Pull down to refresh. If the content is still stale, confirm connectivity and try again after the cache window expires.",
            ),
        ),
    ),
)

private fun filterFaqSections(query: String): List<HelpSectionData> {
    if (query.isBlank()) {
        return helpSections
    }
    val lowered = query.trim().lowercase()
    return helpSections.mapNotNull { section ->
        val filteredItems = section.items.filter { item ->
            item.question.lowercase().contains(lowered) || item.answer.lowercase().contains(lowered)
        }
        filteredItems.takeIf { it.isNotEmpty() }?.let { section.copy(items = it) }
    }
}

private val userGuideSections = listOf(
    UserGuideSectionData(
        title = "Getting Started",
        items = listOf(
            UserGuideItemData(
                heading = "Create your profile",
                body = "Go to Profile and create a profile with full name, birth date, birth time if known, and birthplace. Better source data gives you better chart precision.",
            ),
            UserGuideItemData(
                heading = "Why birth time matters",
                body = "Birth time determines the Ascendant and house cusps. Without it, the app falls back to an estimated chart and hides some house-dependent features.",
            ),
            UserGuideItemData(
                heading = "Multi-profile support",
                body = "You can add more than one profile for yourself, a partner, family members, or comparison subjects and switch between them from the Profile tab.",
            ),
        ),
    ),
    UserGuideSectionData(
        title = "Home & Daily Reading",
        items = listOf(
            UserGuideItemData(
                heading = "What is a daily reading?",
                body = "The daily reading combines forecast scoring, your personal day number, and lunar context into a single daily interpretation. Pull to refresh on Home when you need a fresh fetch.",
            ),
            UserGuideItemData(
                heading = "Morning Brief",
                body = "Morning Brief is the short summary reused across the home surface, widgets, and notifications. Opening the app helps keep it current.",
            ),
            UserGuideItemData(
                heading = "Personal Day Number",
                body = "This numerology value is derived from your birth date plus today's date and helps frame the tone of the day.",
            ),
        ),
    ),
    UserGuideSectionData(
        title = "Numerology",
        items = listOf(
            UserGuideItemData(
                heading = "Life Path Number",
                body = "Derived from the full birth date. It represents the broad themes and core direction that repeat through life.",
            ),
            UserGuideItemData(
                heading = "Expression, Soul Urge, and Personality",
                body = "These name-based numbers describe how you express yourself, what drives you internally, and how you are perceived externally.",
            ),
            UserGuideItemData(
                heading = "Pythagorean vs Chaldean",
                body = "Pythagorean is the modern default. Chaldean uses a different mapping and can produce different name-based results.",
            ),
            UserGuideItemData(
                heading = "Personal Year & Month",
                body = "These cycles are built from your birth date and the current calendar period to explain the longer and shorter timing arcs you are in.",
            ),
        ),
    ),
    UserGuideSectionData(
        title = "Birth Chart",
        items = listOf(
            UserGuideItemData(
                heading = "Reading your chart",
                body = "The chart view places planets, signs, and houses into one wheel so you can inspect the structure of the natal chart and supporting interpretations.",
            ),
            UserGuideItemData(
                heading = "Planets, signs, houses, aspects",
                body = "Planets show what is acting, signs show how that energy expresses itself, houses show where it lands, and aspects show how those energies interact.",
            ),
        ),
    ),
    UserGuideSectionData(
        title = "Compatibility",
        items = listOf(
            UserGuideItemData(
                heading = "Synastry",
                body = "Synastry compares two charts to show resonance, friction, and recurring interaction patterns.",
            ),
            UserGuideItemData(
                heading = "Cosmic Circle",
                body = "Relationships lets you save and compare people. Some relationship data syncs through the backend, while local history stays on-device.",
            ),
            UserGuideItemData(
                heading = "What the score means",
                body = "Higher scores signal stronger alignment, but they do not predict the success of a relationship. They describe pattern intensity, not destiny.",
            ),
        ),
    ),
    UserGuideSectionData(
        title = "Year Ahead",
        items = listOf(
            UserGuideItemData(
                heading = "Solar Return",
                body = "The year-ahead flow uses the Sun returning to its natal position to frame your next year of themes and pressure points.",
            ),
            UserGuideItemData(
                heading = "Life Phase",
                body = "Long-cycle astrological milestones such as Saturn and Chiron periods help define your current life chapter.",
            ),
            UserGuideItemData(
                heading = "Eclipses and monthly forecast",
                body = "The app highlights major activation periods and lays out month-by-month themes to make the longer forecast easier to use.",
            ),
        ),
    ),
    UserGuideSectionData(
        title = "Tools & Features",
        items = listOf(
            UserGuideItemData(
                heading = "Calculated vs interpretive",
                body = "Some tools are direct calculations from astrology or numerology, while others are reflective or hybrid guidance layers.",
            ),
            UserGuideItemData(
                heading = "Tarot, Oracle, Birthstone",
                body = "These support reflection and reference use cases rather than strict natal chart computation.",
            ),
            UserGuideItemData(
                heading = "Cosmic Habits, Journal, Widgets",
                body = "Habits and Journal help you turn the readings into trackable behavior and reflection, while widgets reuse app-prepared daily context.",
            ),
        ),
    ),
    UserGuideSectionData(
        title = "Notifications",
        items = listOf(
            UserGuideItemData(
                heading = "Daily Reading Reminder",
                body = "Manage the quick reminder from Profile or use Notification settings for more granular alert control.",
            ),
            UserGuideItemData(
                heading = "Morning Brief",
                body = "The brief notification depends on successful brief refresh plus Android notification permission and delivery rules.",
            ),
            UserGuideItemData(
                heading = "Disabling notifications",
                body = "Use the in-app notification screen to disable categories and Android system settings to revoke permission entirely.",
            ),
        ),
    ),
    UserGuideSectionData(
        title = "Tips & Tricks",
        items = listOf(
            UserGuideItemData(
                heading = "Pull to refresh",
                body = "Main surfaces support pull-to-refresh when you want a fresh network-backed result instead of cached content.",
            ),
            UserGuideItemData(
                heading = "Long press profiles",
                body = "Use the profile list actions to edit or delete saved profiles quickly.",
            ),
            UserGuideItemData(
                heading = "Context-aware AI",
                body = "Cosmic Guide uses your active profile plus optional local context such as calendar and biometric consent when those features are enabled.",
            ),
            UserGuideItemData(
                heading = "Hide Sensitive Details",
                body = "This is a presentation privacy layer. It masks visible details and sharing surfaces without turning server-backed features off.",
            ),
            UserGuideItemData(
                heading = "Chaldean toggle",
                body = "Numerology can switch systems so you can compare Pythagorean and Chaldean results side by side.",
            ),
        ),
    ),
)