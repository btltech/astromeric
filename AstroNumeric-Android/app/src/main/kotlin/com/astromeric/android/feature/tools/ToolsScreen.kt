package com.astromeric.android.feature.tools

import android.content.Context
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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
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
    val affirmationLoadError = stringResource(R.string.affirmation_error_load)
    val tarotLoadError = stringResource(R.string.tarot_error_load)
    val dailyGuideLoadError = stringResource(R.string.tools_daily_guide_error_load)
    val timingLoadError = stringResource(R.string.timing_advisor_error_load)
    val oracleProfileRequiredError = stringResource(R.string.tools_oracle_profile_required)
    val oracleLoadError = stringResource(R.string.tools_oracle_error_load)
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
                ?.onFailure { affirmationError = it.message ?: affirmationLoadError }
                ?.getOrNull()

            tarotCard = tarotRequest.await()
                .onFailure { tarotError = it.message ?: tarotLoadError }
                .getOrNull()

            doDont = doDontRequest.await()
                ?.onFailure { doDontError = it.message ?: dailyGuideLoadError }
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
                    timingError = result.errorMessage ?: timingLoadError
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
            eyebrow = stringResource(R.string.tools_eyebrow),
            title = stringResource(R.string.tools_title),
            body = stringResource(R.string.tools_hero_body),
            chips = ToolProvenance.entries.map { it.label },
        ) {
            selectedProfile?.let { profile ->
                Text(
                    text = stringResource(
                        R.string.tools_active_profile,
                        profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                    ),
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
            Text(
                if (isRefreshing) {
                    stringResource(R.string.tools_refreshing)
                } else {
                    stringResource(R.string.tools_refresh)
                },
            )
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
                    yesNoError = oracleProfileRequiredError
                } else {
                    scope.launch {
                        isConsultingOracle = true
                        yesNoError = null
                        yesNoGuidance = remoteDataSource.fetchYesNoGuidance(
                            question = oracleQuestion.trim(),
                            profile = selectedProfile,
                        )
                            .onFailure { yesNoError = it.message ?: oracleLoadError }
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
                text = stringResource(R.string.tools_profile_context_title),
                style = MaterialTheme.typography.titleMedium,
            )
            Text(
                text = if (selectedProfile != null) {
                    "${selectedProfile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)} · ${selectedProfile.dataQuality.label}"
                } else {
                    stringResource(R.string.tools_no_profile_selected)
                },
                style = MaterialTheme.typography.bodyMedium,
            )
            Text(
                text = selectedProfile?.dataQuality?.description
                    ?: stringResource(R.string.tools_profile_context_empty_body),
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
    val retrogradeLabels = buildList {
        if (doDont?.mercuryRetrograde == true) add(stringResource(R.string.tools_mercury_retrograde))
        if (doDont?.venusRetrograde == true) add(stringResource(R.string.tools_venus_retrograde))
    }

    ToolDataCard(title = stringResource(R.string.tools_daily_guide_title), error = error) {
        val guide = doDont
        if (guide != null) {
            AssistChip(
                onClick = {},
                label = { Text(stringResource(R.string.home_personal_day_chip, guide.personalDay)) },
            )
            Text(
                text = stringResource(R.string.tools_moon_phase_format, guide.moonPhase),
                style = MaterialTheme.typography.bodyMedium,
            )
            if (retrogradeLabels.isNotEmpty()) {
                Text(
                    text = retrogradeLabels.joinToString(" · "),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Text(
                text = stringResource(R.string.tools_do_format, guide.dos.joinToString()),
                style = MaterialTheme.typography.bodyMedium,
            )
            Text(
                text = stringResource(R.string.tools_avoid_format, guide.donts.joinToString()),
                style = MaterialTheme.typography.bodyMedium,
            )
        } else if (selectedProfile == null) {
            Text(
                text = stringResource(R.string.tools_daily_guide_profile_required),
                style = MaterialTheme.typography.bodyMedium,
            )
        } else {
            Text(text = stringResource(R.string.tools_daily_guide_not_loaded), style = MaterialTheme.typography.bodyMedium)
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
    val context = LocalContext.current

    ToolDataCard(title = stringResource(R.string.tools_timing_title), error = error) {
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
                    AssistChip(onClick = {}, label = { Text(stringResource(R.string.timing_advisor_cached_snapshot)) })
                }
            }
            if (timingResultIsCached) {
                Text(
                    text = timingResultCachedAtEpochMillis?.let { formatTimingCacheTimestamp(context, it) }
                        ?: stringResource(R.string.timing_advisor_saved_snapshot_in_use),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            result.advice.takeIf { it.isNotBlank() }?.let { advice ->
                Text(text = advice, style = MaterialTheme.typography.bodyMedium)
            }
            if (result.bestTimes.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.tools_timing_best_windows_format, result.bestTimes.joinToString()),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            if (result.avoidTimes.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.tools_timing_avoid_windows_format, result.avoidTimes.joinToString()),
                    style = MaterialTheme.typography.bodyMedium,
                )
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
                text = stringResource(R.string.tools_timing_profile_required),
                style = MaterialTheme.typography.bodyMedium,
            )
        } else {
            Text(text = stringResource(R.string.tools_timing_not_loaded), style = MaterialTheme.typography.bodyMedium)
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
    ToolDataCard(title = stringResource(R.string.tools_oracle_title), error = error) {
        OutlinedTextField(
            value = question,
            onValueChange = onQuestionChange,
            label = { Text(stringResource(R.string.tools_oracle_question_label)) },
            modifier = Modifier.fillMaxWidth(),
            maxLines = 3,
        )
        Button(onClick = onConsult, enabled = question.isNotBlank() && !isConsulting) {
            Text(
                if (isConsulting) {
                    stringResource(R.string.tools_oracle_consulting)
                } else {
                    stringResource(R.string.tools_oracle_consult)
                },
            )
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
            Text(text = stringResource(R.string.tools_oracle_profile_required), style = MaterialTheme.typography.bodyMedium)
        } else {
            Text(
                text = stringResource(R.string.tools_oracle_prompt),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
private fun TarotDataCard(tarotCard: TarotCardData?, error: String?) {
    ToolDataCard(title = stringResource(R.string.tools_tarot_title), error = error) {
        if (tarotCard != null) {
            Text(text = tarotCard.name, style = MaterialTheme.typography.titleMedium)
            Text(
                text = stringResource(
                    R.string.tools_tarot_orientation_format,
                    tarotCard.suit,
                    if (tarotCard.upright) {
                        stringResource(R.string.tools_tarot_upright)
                    } else {
                        stringResource(R.string.tools_tarot_reversed)
                    },
                ),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(text = tarotCard.meaning, style = MaterialTheme.typography.bodyMedium)
            Text(text = tarotCard.interpretation, style = MaterialTheme.typography.bodyMedium)
        } else {
            Text(text = stringResource(R.string.tools_tarot_empty), style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun AffirmationDataCard(
    affirmation: AffirmationData?,
    error: String?,
    selectedProfile: AppProfile?,
) {
    ToolDataCard(title = stringResource(R.string.tools_affirmation_title), error = error) {
        if (affirmation != null) {
            Text(text = affirmation.affirmation, style = MaterialTheme.typography.bodyLarge)
        } else if (selectedProfile == null) {
            Text(
                text = stringResource(R.string.tools_affirmation_profile_required),
                style = MaterialTheme.typography.bodyMedium,
            )
        } else {
            Text(text = stringResource(R.string.tools_affirmation_not_loaded), style = MaterialTheme.typography.bodyMedium)
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
    ToolDataCard(title = stringResource(R.string.tools_compatibility_title), error = null) {
        AssistChip(
            onClick = {},
            label = {
                Text(
                    if (savedRelationshipCount == 0) {
                        stringResource(R.string.tools_compatibility_empty_summary)
                    } else {
                        stringResource(
                            R.string.tools_compatibility_summary_format,
                            savedRelationshipCount,
                            averageCompatibilityScore,
                        )
                    },
                )
            },
        )
        Text(
            text = stringResource(R.string.tools_compatibility_body),
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = if (selectedProfile == null) {
                stringResource(R.string.tools_compatibility_profile_required)
            } else {
                stringResource(R.string.tools_compatibility_ready)
            },
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Button(onClick = onOpenRelationships) {
            Text(stringResource(R.string.action_open_relationships))
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
            text = stringResource(R.string.tools_choose_next_tool),
            style = MaterialTheme.typography.titleMedium,
        )
        PremiumBentoCard(
            title = stringResource(R.string.tools_launcher_explore_title),
            body = stringResource(R.string.tools_launcher_explore_body),
            icon = "✦",
            badge = ToolProvenance.REFERENCE.label,
            minHeight = 132,
            onClick = onOpenExplore,
        )
        BentoRow {
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_daily_guide_title),
                body = stringResource(R.string.tools_launcher_daily_guide_body),
                icon = "☀",
                badge = ToolProvenance.CALCULATED.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenDailyFeatures,
            )
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_timing_title),
                body = stringResource(R.string.tools_launcher_timing_body),
                icon = "◷",
                badge = ToolProvenance.CALCULATED.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenTimingAdvisor,
            )
        }
        PremiumBentoCard(
            title = stringResource(R.string.tools_launcher_temporal_matrix_title),
            body = stringResource(R.string.tools_launcher_temporal_matrix_body),
            icon = "◫",
            badge = ToolProvenance.HYBRID.label,
            minHeight = 132,
            onClick = onOpenTemporalMatrix,
        )
        BentoRow {
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_tarot_title),
                body = stringResource(R.string.tools_launcher_tarot_body),
                icon = "♠",
                badge = ToolProvenance.INTERPRETIVE.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenTarot,
            )
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_oracle_title),
                body = stringResource(R.string.tools_launcher_oracle_body),
                icon = "?",
                badge = ToolProvenance.HYBRID.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenOracle,
            )
        }
        BentoRow {
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_affirmation_title),
                body = stringResource(R.string.tools_launcher_affirmation_body),
                icon = "★",
                badge = ToolProvenance.INTERPRETIVE.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenAffirmation,
            )
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_moon_phase_title),
                body = stringResource(R.string.tools_launcher_moon_phase_body),
                icon = "☾",
                badge = ToolProvenance.CALCULATED.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenMoon,
            )
        }
        BentoRow {
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_moon_events_title),
                body = stringResource(R.string.tools_launcher_moon_events_body),
                icon = "◐",
                badge = ToolProvenance.CALCULATED.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenMoonEvents,
            )
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_year_ahead_title),
                body = stringResource(R.string.tools_launcher_year_ahead_body),
                icon = "↻",
                badge = ToolProvenance.HYBRID.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenYearAhead,
            )
        }
        BentoRow {
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_compatibility_title),
                body = stringResource(R.string.tools_launcher_compatibility_body),
                icon = "♡",
                badge = ToolProvenance.HYBRID.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenRelationships,
            )
            PremiumBentoCard(
                title = stringResource(R.string.tools_launcher_birthstones_title),
                body = stringResource(R.string.tools_launcher_birthstones_body),
                icon = "◇",
                badge = ToolProvenance.REFERENCE.label,
                modifier = Modifier.weight(1f),
                onClick = onOpenBirthstones,
            )
        }
        PremiumBentoCard(
            title = stringResource(R.string.tools_launcher_learning_title),
            body = stringResource(R.string.tools_launcher_learning_body),
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

private fun formatTimingCacheTimestamp(context: Context, epochMillis: Long): String {
    val formatted = TimingCacheFormatter.format(
        Instant.ofEpochMilli(epochMillis).atZone(ZoneId.systemDefault()),
    )
    return context.getString(R.string.tools_timing_snapshot_from, formatted)
}

private val TimingCacheFormatter: DateTimeFormatter =
    DateTimeFormatter.ofPattern("MMM d, HH:mm", Locale.getDefault())
