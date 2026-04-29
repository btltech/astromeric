package com.astromeric.android.feature.tools

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.core.data.local.TimingAdviceCacheStore
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.loadTimingAdviceWithCacheFallback
import com.astromeric.android.core.model.AffirmationData
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DoDontData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.TarotCardData
import com.astromeric.android.core.model.TimingActivity
import com.astromeric.android.core.model.TimingToolResult
import com.astromeric.android.core.model.ToolProvenance
import com.astromeric.android.core.model.YesNoGuidanceData
import com.astromeric.android.core.model.toToolResult
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PremiumBentoCard
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumHeroCard
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun ToolsScreen(
    selectedProfile: AppProfile?,
    preferencesStore: AppPreferencesStore,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenRelationships: () -> Unit,
    onOpenLearn: () -> Unit,
    onOpenExplore: () -> Unit,
    onOpenMoon: () -> Unit,
    onOpenTimingAdvisor: () -> Unit,
    onOpenTemporalMatrix: () -> Unit,
    onOpenYearAhead: () -> Unit,
    onOpenBirthstones: () -> Unit,
    onOpenDailyFeatures: () -> Unit = {},
    onOpenMoonEvents: () -> Unit = {},
    onOpenAffirmation: () -> Unit = {},
    onOpenOracle: () -> Unit = {},
    onOpenTarot: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val timingAdviceCacheStore = remember(context) { TimingAdviceCacheStore(context.applicationContext) }
    val scope = rememberCoroutineScope()
    val savedRelationships by preferencesStore.savedRelationships.collectAsStateWithLifecycle(initialValue = emptyList())
    var refreshVersion by remember(selectedProfile?.id) { mutableStateOf(0) }
    var selectedActivity by remember { mutableStateOf(TimingActivity.CREATIVE_WORK) }
    var isRefreshing by remember(selectedProfile?.id) { mutableStateOf(false) }
    var oracleQuestion by remember { mutableStateOf("") }
    var isConsultingOracle by remember { mutableStateOf(false) }
    var affirmation by remember(selectedProfile?.id) { mutableStateOf<AffirmationData?>(null) }
    var yesNoGuidance by remember(selectedProfile?.id) { mutableStateOf<YesNoGuidanceData?>(null) }
    var tarotCard by remember(selectedProfile?.id) { mutableStateOf<TarotCardData?>(null) }
    var doDont by remember(selectedProfile?.id) { mutableStateOf<DoDontData?>(null) }
    var timingResult by remember(selectedProfile?.id, selectedActivity) { mutableStateOf<TimingToolResult?>(null) }
    var affirmationError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var yesNoError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var tarotError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var doDontError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var timingError by remember(selectedProfile?.id, selectedActivity) { mutableStateOf<String?>(null) }
    var timingResultIsCached by remember(selectedProfile?.id, selectedActivity) { mutableStateOf(false) }
    var timingResultCachedAtEpochMillis by remember(selectedProfile?.id, selectedActivity) { mutableStateOf<Long?>(null) }
    val averageCompatibilityScore = if (savedRelationships.isEmpty()) 0 else (savedRelationships.sumOf { it.overallScore.toDouble() } / savedRelationships.size).toInt()

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        isRefreshing = true
        affirmationError = null
        yesNoError = null
        tarotError = null
        doDontError = null

        coroutineScope {
            val affirmationRequest = async {
                selectedProfile?.let { profile -> remoteDataSource.fetchAffirmation(profile) }
            }
            val tarotRequest = async { remoteDataSource.drawTarotCard() }
            val doDontRequest = async {
                selectedProfile?.let { profile -> remoteDataSource.fetchDoDont(profile) }
            }

            affirmation = affirmationRequest.await()
                ?.onFailure { affirmationError = it.message ?: "Affirmation could not be loaded." }
                ?.getOrNull()

            tarotCard = tarotRequest.await()
                .onFailure { tarotError = it.message ?: "Tarot card could not be loaded." }
                .getOrNull()

            doDont = doDontRequest.await()
                ?.onFailure { doDontError = it.message ?: "Daily guide could not be loaded." }
                ?.getOrNull()
        }

        isRefreshing = false
    }

    LaunchedEffect(selectedProfile?.id, selectedActivity, refreshVersion) {
        val profile = selectedProfile
        timingError = null
        timingResultIsCached = false
        timingResultCachedAtEpochMillis = null
        timingResult = if (profile != null) {
            val result = loadTimingAdviceWithCacheFallback(
                activity = selectedActivity,
                profile = profile,
                remoteDataSource = remoteDataSource,
                cacheStore = timingAdviceCacheStore,
            )
            timingResultIsCached = result.isCached
            timingResultCachedAtEpochMillis = result.cachedAtEpochMillis
            result.payload?.toToolResult(selectedActivity).also {
                if (it == null) {
                    timingError = result.errorMessage ?: "Timing advice could not be loaded."
                }
            }
        } else {
            null
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = "Tools",
            title = "Cosmic Tools",
            body = "Calculated tools help you decide. Interpretive tools help you feel, frame, or process what the day is bringing.",
            chips = ToolProvenance.entries.map { it.label },
        ) {
            selectedProfile?.let { profile ->
                Text(
                    text = "Active profile: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        ToolsBentoGrid(
            onOpenExplore = onOpenExplore,
            onOpenDailyFeatures = onOpenDailyFeatures,
            onOpenTimingAdvisor = onOpenTimingAdvisor,
            onOpenTemporalMatrix = onOpenTemporalMatrix,
            onOpenTarot = onOpenTarot,
            onOpenOracle = onOpenOracle,
            onOpenAffirmation = onOpenAffirmation,
            onOpenMoon = onOpenMoon,
            onOpenMoonEvents = onOpenMoonEvents,
            onOpenYearAhead = onOpenYearAhead,
            onOpenRelationships = onOpenRelationships,
            onOpenBirthstones = onOpenBirthstones,
            onOpenLearn = onOpenLearn,
        )

        Button(
            onClick = { refreshVersion += 1 },
            enabled = !isRefreshing,
        ) {
            Text(if (isRefreshing) "Refreshing..." else "Refresh tools")
        }

        ProfileContextCard(
            selectedProfile = selectedProfile,
            hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
        )

        if (isRefreshing && tarotCard == null && affirmation == null && doDont == null) {
            CircularProgressIndicator()
        }

        DailyGuideDataCard(
            doDont = doDont,
            error = doDontError,
            selectedProfile = selectedProfile,
        )

        TimingDataCard(
            selectedProfile = selectedProfile,
            selectedActivity = selectedActivity,
            onSelectActivity = { selectedActivity = it },
            timingResult = timingResult,
            timingResultIsCached = timingResultIsCached,
            timingResultCachedAtEpochMillis = timingResultCachedAtEpochMillis,
            error = timingError,
        )

        OracleDataCard(
            selectedProfile = selectedProfile,
            question = oracleQuestion,
            onQuestionChange = { oracleQuestion = it },
            isConsulting = isConsultingOracle,
            guidance = yesNoGuidance,
            error = yesNoError,
            onConsult = {
                if (selectedProfile == null) {
                    yesNoError = "A saved profile is required for Oracle guidance."
                } else {
                    scope.launch {
                        isConsultingOracle = true
                        yesNoError = null
                        yesNoGuidance = remoteDataSource.fetchYesNoGuidance(
                            question = oracleQuestion.trim(),
                            profile = selectedProfile,
                        )
                            .onFailure { yesNoError = it.message ?: "Oracle guidance could not be loaded." }
                            .getOrNull()
                        isConsultingOracle = false
                    }
                }
            },
        )

        TarotDataCard(tarotCard = tarotCard, error = tarotError)

        AffirmationDataCard(
            affirmation = affirmation,
            error = affirmationError,
            selectedProfile = selectedProfile,
        )

        CompatibilitySummaryCard(
            savedRelationshipCount = savedRelationships.size,
            averageCompatibilityScore = averageCompatibilityScore,
            selectedProfile = selectedProfile,
            onOpenRelationships = onOpenRelationships,
        )
    }
}

@Composable
private fun ProfileContextCard(
    selectedProfile: AppProfile?,
    hideSensitiveDetailsEnabled: Boolean,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = "Profile context",
                style = MaterialTheme.typography.titleMedium,
            )
            Text(
                text = if (selectedProfile != null) {
                    "${selectedProfile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)} · ${selectedProfile.dataQuality.label}"
                } else {
                    "No profile selected"
                },
                style = MaterialTheme.typography.bodyMedium,
            )
            Text(
                text = selectedProfile?.dataQuality?.description
                    ?: "Create a profile to personalize timing, daily guidance, and reflections.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun DailyGuideDataCard(
    doDont: DoDontData?,
    error: String?,
    selectedProfile: AppProfile?,
) {
    ToolDataCard(title = "Daily Guide", error = error) {
        val guide = doDont
        if (guide != null) {
            AssistChip(onClick = {}, label = { Text("Personal Day ${guide.personalDay}") })
            Text(text = "Moon phase: ${guide.moonPhase}", style = MaterialTheme.typography.bodyMedium)
            if (guide.mercuryRetrograde || guide.venusRetrograde) {
                Text(
                    text = buildString {
                        if (guide.mercuryRetrograde) append("Mercury retrograde ")
                        if (guide.venusRetrograde) append("Venus retrograde")
                    }.trim(),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Text(text = "Do: ${guide.dos.joinToString()}", style = MaterialTheme.typography.bodyMedium)
            Text(text = "Avoid: ${guide.donts.joinToString()}", style = MaterialTheme.typography.bodyMedium)
        } else if (selectedProfile == null) {
            Text(
                text = "A saved profile is required for personalized daily guidance.",
                style = MaterialTheme.typography.bodyMedium,
            )
        } else {
            Text(text = "Daily guidance has not loaded yet.", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
private fun TimingDataCard(
    selectedProfile: AppProfile?,
    selectedActivity: TimingActivity,
    onSelectActivity: (TimingActivity) -> Unit,
    timingResult: TimingToolResult?,
    timingResultIsCached: Boolean,
    timingResultCachedAtEpochMillis: Long?,
    error: String?,
) {
    ToolDataCard(title = "Timing", error = error) {
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            TimingActivity.entries.forEach { activity ->
                FilterChip(
                    selected = selectedActivity == activity,
                    onClick = { onSelectActivity(activity) },
                    label = { Text("${activity.emoji} ${activity.displayName}") },
                )
            }
        }

        val result = timingResult
        if (result != null) {
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                AssistChip(onClick = {}, label = { Text("${(result.score * 100).toInt()}% ${result.rating}") })
                if (timingResultIsCached) {
                    AssistChip(onClick = {}, label = { Text("Cached snapshot") })
                }
            }
            if (timingResultIsCached) {
                Text(
                    text = timingResultCachedAtEpochMillis?.let(::formatTimingCacheTimestamp)
                        ?: "Saved timing snapshot in use.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            result.advice.takeIf { it.isNotBlank() }?.let { advice ->
                Text(text = advice, style = MaterialTheme.typography.bodyMedium)
            }
            if (result.bestTimes.isNotEmpty()) {
                Text(text = "Best windows: ${result.bestTimes.joinToString()}", style = MaterialTheme.typography.bodyMedium)
            }
            if (result.avoidTimes.isNotEmpty()) {
                Text(text = "Avoid windows: ${result.avoidTimes.joinToString()}", style = MaterialTheme.typography.bodyMedium)
            }
            result.tips.take(3).forEach { tip ->
                Text(
                    text = tip,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        } else if (selectedProfile == null) {
            Text(
                text = "A saved profile is required for personalized timing advice.",
                style = MaterialTheme.typography.bodyMedium,
            )
        } else {
            Text(text = "Timing advice has not loaded yet.", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun OracleDataCard(
    selectedProfile: AppProfile?,
    question: String,
    onQuestionChange: (String) -> Unit,
    isConsulting: Boolean,
    guidance: YesNoGuidanceData?,
    error: String?,
    onConsult: () -> Unit,
) {
    ToolDataCard(title = "Oracle", error = error) {
        OutlinedTextField(
            value = question,
            onValueChange = onQuestionChange,
            label = { Text("Ask a yes or no question") },
            modifier = Modifier.fillMaxWidth(),
            maxLines = 3,
        )
        Button(onClick = onConsult, enabled = question.isNotBlank() && !isConsulting) {
            Text(if (isConsulting) "Consulting..." else "Consult the Oracle")
        }

        if (guidance != null) {
            AssistChip(onClick = {}, label = { Text("${guidance.answer} ${(guidance.confidence * 100).toInt()}%") })
            Text(text = guidance.reasoning, style = MaterialTheme.typography.bodyMedium)
            guidance.guidance.forEach { tip ->
                Text(
                    text = tip,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        } else if (selectedProfile == null) {
            Text(text = "A saved profile is required for Oracle guidance.", style = MaterialTheme.typography.bodyMedium)
        } else {
            Text(
                text = "Ask a clear question about timing, readiness, or whether to proceed.",
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
private fun TarotDataCard(tarotCard: TarotCardData?, error: String?) {
    ToolDataCard(title = "Tarot", error = error) {
        if (tarotCard != null) {
            Text(text = tarotCard.name, style = MaterialTheme.typography.titleMedium)
            Text(
                text = "${tarotCard.suit} · ${if (tarotCard.upright) "Upright" else "Reversed"}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(text = tarotCard.meaning, style = MaterialTheme.typography.bodyMedium)
            Text(text = tarotCard.interpretation, style = MaterialTheme.typography.bodyMedium)
        } else {
            Text(text = "No tarot card has been drawn yet.", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun AffirmationDataCard(
    affirmation: AffirmationData?,
    error: String?,
    selectedProfile: AppProfile?,
) {
    ToolDataCard(title = "Affirmation", error = error) {
        if (affirmation != null) {
            Text(text = affirmation.affirmation, style = MaterialTheme.typography.bodyLarge)
        } else if (selectedProfile == null) {
            Text(
                text = "A saved profile is required for personalized affirmation text.",
                style = MaterialTheme.typography.bodyMedium,
            )
        } else {
            Text(text = "Affirmation text has not loaded yet.", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun CompatibilitySummaryCard(
    savedRelationshipCount: Int,
    averageCompatibilityScore: Int,
    selectedProfile: AppProfile?,
    onOpenRelationships: () -> Unit,
) {
    ToolDataCard(title = "Compatibility", error = null) {
        AssistChip(
            onClick = {},
            label = {
                Text(
                    if (savedRelationshipCount == 0) {
                        "No saved relationship history yet"
                    } else {
                        "$savedRelationshipCount saved · $averageCompatibilityScore% average"
                    },
                )
            },
        )
        Text(
            text = "Compatibility, saved matches, live relationship timing, timeline context, and Cosmic Circle now live in a dedicated destination instead of duplicating that depth inside Tools.",
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = if (selectedProfile == null) {
                "Create or select a profile first so the relationship workspace can personalize comparisons and timing."
            } else {
                "Open the relationship workspace when you want to compare profiles, revisit saved matches, or manage synced people."
            },
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Button(onClick = onOpenRelationships) {
            Text("Open Relationships")
        }
    }
}

@Composable
private fun ToolsBentoGrid(
    onOpenExplore: () -> Unit,
    onOpenDailyFeatures: () -> Unit,
    onOpenTimingAdvisor: () -> Unit,
    onOpenTemporalMatrix: () -> Unit,
    onOpenTarot: () -> Unit,
    onOpenOracle: () -> Unit,
    onOpenAffirmation: () -> Unit,
    onOpenMoon: () -> Unit,
    onOpenMoonEvents: () -> Unit,
    onOpenYearAhead: () -> Unit,
    onOpenRelationships: () -> Unit,
    onOpenBirthstones: () -> Unit,
    onOpenLearn: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text = "Choose your next tool",
            style = MaterialTheme.typography.titleMedium,
        )
        PremiumBentoCard(
            title = "Explore Workspace",
            body = "Learn, habits, relationships, and themed browsing without making Explore a root tab.",
            icon = "✦",
            badge = ToolProvenance.REFERENCE.label,
            minHeight = 132,
            onClick = onOpenExplore,
        )
        BentoRow {
            PremiumBentoCard(
                title = "Daily Guide",
                body = "Personal day, moon phase, retrogrades, and cues.",
                icon = "☀",
                badge = ToolProvenance.CALCULATED.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenDailyFeatures,
            )
            PremiumBentoCard(
                title = "Timing",
                body = "Activity windows scored from the live sky.",
                icon = "◷",
                badge = ToolProvenance.CALCULATED.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenTimingAdvisor,
            )
        }
        PremiumBentoCard(
            title = "Temporal Matrix",
            body = "Overlay the next 48 hours with calendar context and timing weather.",
            icon = "◫",
            badge = ToolProvenance.HYBRID.label,
            minHeight = 132,
            onClick = onOpenTemporalMatrix,
        )
        BentoRow {
            PremiumBentoCard(
                title = "Tarot",
                body = "Card pull for symbolic reflection.",
                icon = "♠",
                badge = ToolProvenance.INTERPRETIVE.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenTarot,
            )
            PremiumBentoCard(
                title = "Oracle",
                body = "Ask a clear yes/no question and read the guidance.",
                icon = "?",
                badge = ToolProvenance.HYBRID.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenOracle,
            )
        }
        BentoRow {
            PremiumBentoCard(
                title = "Affirmation",
                body = "Supportive language tuned to today's mood.",
                icon = "★",
                badge = ToolProvenance.INTERPRETIVE.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenAffirmation,
            )
            PremiumBentoCard(
                title = "Moon Phase",
                body = "Current lunar phase and ritual weather.",
                icon = "☾",
                badge = ToolProvenance.CALCULATED.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenMoon,
            )
        }
        BentoRow {
            PremiumBentoCard(
                title = "Moon Events",
                body = "Upcoming new moons, full moons, and milestones.",
                icon = "◐",
                badge = ToolProvenance.CALCULATED.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenMoonEvents,
            )
            PremiumBentoCard(
                title = "Year Ahead",
                body = "Current life phase and the next 12 months.",
                icon = "↻",
                badge = ToolProvenance.HYBRID.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenYearAhead,
            )
        }
        BentoRow {
            PremiumBentoCard(
                title = "Compatibility",
                body = "Relationship timing, saved history, and Cosmic Circle.",
                icon = "♡",
                badge = ToolProvenance.HYBRID.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenRelationships,
            )
            PremiumBentoCard(
                title = "Birthstones",
                body = "Gemstone guide matched to sign traditions.",
                icon = "◇",
                badge = ToolProvenance.REFERENCE.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenBirthstones,
            )
        }
        PremiumBentoCard(
            title = "Learning",
            body = "Lessons, glossary terms, and sign guidance in one reference path.",
            icon = "◇",
            badge = ToolProvenance.REFERENCE.label,
            minHeight = 132,
            onClick = onOpenLearn,
        )
    }
}

@Composable
private fun BentoRow(content: @Composable RowScope.() -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        content = content,
    )
}

@Composable
private fun ToolDefinitionCard(
    title: String,
    description: String,
    provenance: ToolProvenance,
    actionLabel: String? = null,
    onClick: (() -> Unit)? = null,
) {
    PremiumContentCard(
        title = title,
        body = description,
    ) {
            AssistChip(
                onClick = {},
                label = { Text(provenance.label) },
            )
            if (actionLabel != null && onClick != null) {
                Button(onClick = onClick) {
                    Text(actionLabel)
                }
            }
    }
}

@Composable
private fun ToolDataCard(
    title: String,
    error: String?,
    content: @Composable () -> Unit,
) {
    PremiumContentCard(
        title = title,
        body = error,
    ) {
        if (error == null) content()
    }
}

private fun formatTimingCacheTimestamp(epochMillis: Long): String {
    val formatted = TimingCacheFormatter.format(
        Instant.ofEpochMilli(epochMillis).atZone(ZoneId.systemDefault()),
    )
    return "Offline timing snapshot from $formatted"
}

private val TimingCacheFormatter: DateTimeFormatter =
    DateTimeFormatter.ofPattern("MMM d, HH:mm", Locale.getDefault())
