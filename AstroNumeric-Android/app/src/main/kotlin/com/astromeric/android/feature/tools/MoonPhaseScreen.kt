package com.astromeric.android.feature.tools

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.MoonEventData
import com.astromeric.android.core.model.MoonEventsData
import com.astromeric.android.core.model.MoonPhaseInfoData
import com.astromeric.android.core.model.MoonRitualSummary
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumLoadingCard
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import java.util.Calendar

@Composable
fun MoonPhaseScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    modifier: Modifier = Modifier,
) {
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var moonError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var moonPhase by remember(selectedProfile?.id) { mutableStateOf<MoonPhaseInfoData?>(null) }
    var moonRitual by remember(selectedProfile?.id) { mutableStateOf<MoonRitualSummary?>(null) }
    var moonEvents by remember(selectedProfile?.id) { mutableStateOf<MoonEventsData?>(null) }
    val phasePresentation = buildMoonPhasePresentation(moonPhase)

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        isLoading = true
        moonError = null

        coroutineScope {
            val moonRequest = async { remoteDataSource.fetchMoonPhase() }
            val ritualRequest = async { remoteDataSource.fetchMoonRitual(selectedProfile) }
            val eventsRequest = async { remoteDataSource.fetchUpcomingMoonEvents() }

            moonPhase = moonRequest.await()
                .onFailure { moonError = it.message ?: "Moon phase could not be loaded." }
                .getOrNull()

            moonRitual = ritualRequest.await()
                .onFailure { moonError = moonError ?: it.message ?: "Moon ritual could not be loaded." }
                .getOrNull()

            moonEvents = eventsRequest.await()
                .onFailure { moonError = moonError ?: it.message ?: "Upcoming moon events could not be loaded." }
                .getOrNull()
        }

        isLoading = false
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        MoonSectionCard(
            title = "Moon Phase",
            body = "Read the lunar weather before you decide how to use your energy. This destination now owns both the phase read and the ritual layer, matching the way iOS treats them as one lunar workflow.",
        ) {
            selectedProfile?.let { profile ->
                AssistChip(
                    onClick = {},
                    label = {
                        Text(
                            "Active profile: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)}",
                        )
                    },
                )
            }
            OutlinedButton(onClick = { refreshVersion += 1 }, enabled = !isLoading) {
                Text(if (isLoading) "Refreshing..." else "Refresh lunar weather")
            }
        }

        if (isLoading && moonPhase == null && moonRitual == null) {
            PremiumLoadingCard(title = "Loading lunar weather")
        } else {
                MoonSectionCard(
                    title = "${phasePresentation.emoji} ${phasePresentation.phaseName}",
                    body = phasePresentation.influence,
                ) {
                    Text(
                        text = "Illumination ${phasePresentation.illuminationPercent}%",
                        style = MaterialTheme.typography.titleMedium,
                    )
                    if (phasePresentation.isFallback) {
                        AssistChip(
                            onClick = {},
                            label = { Text("Approximate local fallback") },
                        )
                        moonError?.takeIf { it.isNotBlank() }?.let { message ->
                            Text(
                                text = message,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                    phasePresentation.nextNewMoon?.takeIf { it.isNotBlank() }?.let { nextNewMoon ->
                        Text(
                            text = "Next new moon: $nextNewMoon",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    phasePresentation.nextFullMoon?.takeIf { it.isNotBlank() }?.let { nextFullMoon ->
                        Text(
                            text = "Next full moon: $nextFullMoon",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }

                MoonSectionCard(
                    title = "Work with the phase",
                    body = phasePresentation.guidance,
                ) {
                    Row(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Best For",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                            Text(
                                text = phasePresentation.bestFor,
                                style = MaterialTheme.typography.titleMedium,
                            )
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Avoid",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                            Text(
                                text = phasePresentation.avoid,
                                style = MaterialTheme.typography.titleMedium,
                            )
                        }
                }

                moonRitual?.ritual?.let { ritual ->
                    MoonSectionCard(
                        title = "Moon Ritual",
                        body = ritual.theme ?: "Use the lunar weather to choose a ritual focus.",
                    ) {
                        ritual.energy?.takeIf { it.isNotBlank() }?.let { energy ->
                            Text(
                                text = energy,
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                        ritual.signFocus?.takeIf { it.isNotBlank() }?.let { signFocus ->
                            Text(
                                text = signFocus,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                        ritual.activities.forEachIndexed { index, step ->
                            Text(
                                text = "${index + 1}. $step",
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                        if (ritual.avoid.isNotEmpty()) {
                            Text(
                                text = "Avoid: ${ritual.avoid.joinToString()}",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                        if (ritual.crystals.isNotEmpty()) {
                            Text(
                                text = "Crystals: ${ritual.crystals.joinToString()}",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                        if (ritual.colors.isNotEmpty()) {
                            Text(
                                text = "Colors: ${ritual.colors.joinToString()}",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                        ritual.affirmation?.takeIf { it.isNotBlank() }?.let { affirmation ->
                            Text(
                                text = affirmation,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }

                val upcomingEvents = moonEvents?.events.orEmpty().ifEmpty { moonRitual?.upcomingEvents.orEmpty() }
                if (upcomingEvents.isNotEmpty()) {
                    MoonSectionCard(
                        title = "Upcoming Moon Events",
                        body = "Use these to see when the next lunar shifts will change the tone.",
                    ) {
                        upcomingEvents.take(5).forEach { event ->
                            MoonEventLine(event)
                        }
                    }
                }
            }
        }
    }
}

private data class MoonPhasePresentation(
    val phaseName: String,
    val emoji: String,
    val illuminationPercent: Int,
    val influence: String,
    val guidance: String,
    val bestFor: String,
    val avoid: String,
    val nextNewMoon: String? = null,
    val nextFullMoon: String? = null,
    val isFallback: Boolean = false,
)

private enum class LocalMoonPhaseGuide(
    val displayName: String,
    val emoji: String,
    val guidance: String,
    val bestFor: String,
    val avoid: String,
) {
    NEW_MOON(
        displayName = "New Moon",
        emoji = "🌑",
        guidance = "A time for new beginnings and setting intentions. Plant seeds for what you want to manifest.",
        bestFor = "Planning",
        avoid = "Big launches",
    ),
    WAXING_CRESCENT(
        displayName = "Waxing Crescent",
        emoji = "🌒",
        guidance = "Build momentum toward your goals. Take small, consistent actions.",
        bestFor = "Starting",
        avoid = "Overthinking",
    ),
    FIRST_QUARTER(
        displayName = "First Quarter",
        emoji = "🌓",
        guidance = "Time to make decisions and take action. Push through challenges.",
        bestFor = "Action",
        avoid = "Indecision",
    ),
    WAXING_GIBBOUS(
        displayName = "Waxing Gibbous",
        emoji = "🌔",
        guidance = "Refine and adjust your approach. Pay attention to details.",
        bestFor = "Refining",
        avoid = "Rushing",
    ),
    FULL_MOON(
        displayName = "Full Moon",
        emoji = "🌕",
        guidance = "Peak energy time. Celebrate achievements and release what no longer serves you.",
        bestFor = "Manifesting",
        avoid = "New starts",
    ),
    WANING_GIBBOUS(
        displayName = "Waning Gibbous",
        emoji = "🌖",
        guidance = "Share your wisdom with others. Practice gratitude.",
        bestFor = "Sharing",
        avoid = "Holding on",
    ),
    LAST_QUARTER(
        displayName = "Last Quarter",
        emoji = "🌗",
        guidance = "Time for reflection and letting go. Clear out old energy.",
        bestFor = "Releasing",
        avoid = "Clinging",
    ),
    WANING_CRESCENT(
        displayName = "Waning Crescent",
        emoji = "🌘",
        guidance = "Rest and recharge. Prepare for the new cycle ahead.",
        bestFor = "Resting",
        avoid = "Overexertion",
    );

    companion object {
        fun fromApiString(value: String?): LocalMoonPhaseGuide? {
            val normalized = value
                ?.trim()
                ?.lowercase()
                ?.replace("_", " ")
                ?.replace("-", " ")
                ?: return null
            return when (normalized) {
                "new moon", "new" -> NEW_MOON
                "waxing crescent" -> WAXING_CRESCENT
                "first quarter" -> FIRST_QUARTER
                "waxing gibbous" -> WAXING_GIBBOUS
                "full moon", "full" -> FULL_MOON
                "waning gibbous" -> WANING_GIBBOUS
                "last quarter", "third quarter" -> LAST_QUARTER
                "waning crescent" -> WANING_CRESCENT
                else -> null
            }
        }
    }
}

private fun buildMoonPhasePresentation(moonPhase: MoonPhaseInfoData?): MoonPhasePresentation {
    val fallback = calculateLocalMoonPhaseFallback()
    val guide = LocalMoonPhaseGuide.fromApiString(moonPhase?.phase) ?: fallback.first
    return if (moonPhase != null) {
        MoonPhasePresentation(
            phaseName = moonPhase.phase,
            emoji = guide.emoji,
            illuminationPercent = moonPhase.illumination.toInt(),
            influence = moonPhase.influence.ifBlank { guide.guidance },
            guidance = guide.guidance,
            bestFor = guide.bestFor,
            avoid = guide.avoid,
            nextNewMoon = moonPhase.nextNewMoon,
            nextFullMoon = moonPhase.nextFullMoon,
            isFallback = false,
        )
    } else {
        MoonPhasePresentation(
            phaseName = guide.displayName,
            emoji = guide.emoji,
            illuminationPercent = fallback.second,
            influence = "Using an approximate on-device lunar cycle because live moon data is unavailable right now.",
            guidance = guide.guidance,
            bestFor = guide.bestFor,
            avoid = guide.avoid,
            isFallback = true,
        )
    }
}

private fun calculateLocalMoonPhaseFallback(): Pair<LocalMoonPhaseGuide, Int> {
    val cycleDay = Calendar.getInstance().get(Calendar.DAY_OF_MONTH) % 30
    return when (cycleDay) {
        in 0..3 -> LocalMoonPhaseGuide.NEW_MOON to 5
        in 4..7 -> LocalMoonPhaseGuide.WAXING_CRESCENT to 25
        in 8..10 -> LocalMoonPhaseGuide.FIRST_QUARTER to 50
        in 11..14 -> LocalMoonPhaseGuide.WAXING_GIBBOUS to 75
        in 15..17 -> LocalMoonPhaseGuide.FULL_MOON to 100
        in 18..21 -> LocalMoonPhaseGuide.WANING_GIBBOUS to 75
        in 22..24 -> LocalMoonPhaseGuide.LAST_QUARTER to 50
        else -> LocalMoonPhaseGuide.WANING_CRESCENT to 25
    }
}

@Composable
private fun MoonSectionCard(
    title: String,
    body: String?,
    content: @Composable ColumnScope.() -> Unit,
) {
    PremiumContentCard(
        title = title,
        body = body,
    ) {
        content()
    }
}

@Composable
private fun MoonEventLine(event: MoonEventData) {
    Text(
        text = buildString {
            append(listOfNotNull(event.emoji, event.type).joinToString(" "))
            append(" · ${event.date}")
            event.sign?.takeIf { it.isNotBlank() }?.let { append(" · $it") }
            event.daysAway?.let { append(" · ${it.toInt()}d") }
        },
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

private fun moonPhaseEmoji(phase: String?): String = when {
    phase.isNullOrBlank() -> "🌙"
    phase.contains("new", ignoreCase = true) -> "🌑"
    phase.contains("waxing crescent", ignoreCase = true) -> "🌒"
    phase.contains("first quarter", ignoreCase = true) -> "🌓"
    phase.contains("waxing gibbous", ignoreCase = true) -> "🌔"
    phase.contains("full", ignoreCase = true) -> "🌕"
    phase.contains("waning gibbous", ignoreCase = true) -> "🌖"
    phase.contains("last quarter", ignoreCase = true) -> "🌗"
    phase.contains("waning crescent", ignoreCase = true) -> "🌘"
    else -> "🌙"
}