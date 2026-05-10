package com.astromeric.android.feature.home

import android.content.Context
import android.content.Intent
import androidx.annotation.StringRes
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.R
import com.astromeric.android.app.MorningBriefWidgetProvider
import com.astromeric.android.app.MorningBriefWidgetSnapshotStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.HabitRepository
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.MoonPhaseInfoData
import com.astromeric.android.core.model.MorningBriefData
import com.astromeric.android.core.model.DailyForecastData
import com.astromeric.android.core.model.ForecastSectionData
import com.astromeric.android.core.model.LocalHabitData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.zodiacSignName
import com.astromeric.android.core.ui.PremiumBentoCard
import com.astromeric.android.core.ui.PremiumHeroCard
import com.astromeric.android.core.ui.scaleReveal

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun HomeScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    habitRepository: HabitRepository,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenTools: () -> Unit,
    onOpenCharts: () -> Unit,
    onCreateProfile: () -> Unit,
    onOpenWeeklyVibe: () -> Unit = {},
    onOpenReading: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val localHabits by habitRepository.localHabits.collectAsStateWithLifecycle(initialValue = emptyList())
    var refreshVersion by remember(selectedProfile?.id) { mutableStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var morningBrief by remember(selectedProfile?.id) { mutableStateOf<MorningBriefData?>(null) }
    var dailyForecast by remember(selectedProfile?.id) { mutableStateOf<DailyForecastData?>(null) }
    var moonPhase by remember(selectedProfile?.id) { mutableStateOf<MoonPhaseInfoData?>(null) }
    var morningBriefError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var forecastError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var moonPhaseError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    val moonPhaseLoadError = stringResource(R.string.home_load_error_moon_phase)
    val morningBriefLoadError = stringResource(R.string.home_load_error_morning_brief)
    val dailyForecastLoadError = stringResource(R.string.home_load_error_daily_forecast)

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        moonPhaseError = null
        moonPhase = remoteDataSource.fetchMoonPhase()
            .onFailure { moonPhaseError = it.message ?: moonPhaseLoadError }
            .getOrNull()

        if (selectedProfile != null) {
            isLoading = true
            morningBriefError = null
            forecastError = null
            val widgetSnapshotStore = MorningBriefWidgetSnapshotStore(context)

            morningBrief = remoteDataSource.fetchMorningBrief(selectedProfile)
                .onFailure { morningBriefError = it.message ?: morningBriefLoadError }
                .getOrNull()

            widgetSnapshotStore.writeSnapshot(
                morningBrief = morningBrief,
                moonPhaseName = moonPhase?.phase,
                moonGuidance = moonPhase?.influence,
            )
            MorningBriefWidgetProvider.refreshAllWidgets(context)

            dailyForecast = if (selectedProfile.canRequestForecast) {
                remoteDataSource.fetchDailyForecast(selectedProfile)
                    .onFailure { forecastError = it.message ?: dailyForecastLoadError }
                    .getOrNull()
            } else {
                null
            }

            isLoading = false
        } else {
            morningBrief = null
            dailyForecast = null
            morningBriefError = null
            forecastError = null
            isLoading = false
        }
    }

    val completedHabits = localHabits.count { it.isCompletedToday }
    val openHabits = localHabits.filterNot { it.isCompletedToday }.take(3)
    var bentoRevealed by remember(selectedProfile?.id) { mutableStateOf(false) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Box {
            PremiumHeroCard(
                eyebrow = stringResource(R.string.home_hero_eyebrow),
                title = if (selectedProfile == null) stringResource(R.string.home_hero_title_no_profile) else stringResource(R.string.home_hero_title_profile),
                body = if (selectedProfile == null) {
                    stringResource(R.string.home_hero_body_no_profile)
                } else {
                    stringResource(R.string.home_hero_body_profile)
                },
                chips = listOfNotNull(
                    selectedProfile?.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)?.let {
                        stringResource(R.string.home_active_profile_chip, it)
                    },
                    morningBrief?.personalDay?.let { stringResource(R.string.home_personal_day_chip, it) },
                    moonPhase?.phase,
                ),
            )
            if (selectedProfile != null) {
                val ctx = LocalContext.current
                val shareLabel = stringResource(R.string.home_share_cosmic_id)
                IconButton(
                    onClick = {
                        shareCosmicID(
                            context = ctx,
                            profile = selectedProfile,
                            personalDay = morningBrief?.personalDay,
                            hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                            shareLabel = shareLabel,
                        )
                    },
                    modifier = Modifier.align(Alignment.TopEnd),
                ) {
                    Icon(
                        imageVector = Icons.Filled.Share,
                        contentDescription = shareLabel,
                    )
                }
            }
        }

        if (selectedProfile == null) {
            NoProfileHeroCard(
                onCreateProfile = onCreateProfile,
                onOpenTools = onOpenTools,
            )
        } else {
            LaunchedEffect(morningBrief, dailyForecast) {
                if (morningBrief != null || dailyForecast != null) bentoRevealed = true
            }

            HomeHeroCard(
                selectedProfile = selectedProfile,
                morningBrief = morningBrief,
                dailyForecast = dailyForecast,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenTools = onOpenTools,
                onOpenCharts = onOpenCharts,
            )

            HomeBentoGrid(
                dailyForecast = dailyForecast,
                moonPhase = moonPhase,
                completedHabits = completedHabits,
                totalHabits = localHabits.size,
                onOpenReading = onOpenReading,
                onOpenWeeklyVibe = onOpenWeeklyVibe,
                onOpenTools = onOpenTools,
                onOpenCharts = onOpenCharts,
                modifier = Modifier.scaleReveal(visible = bentoRevealed),
            )

            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                DashboardMetricCard(
                    label = stringResource(R.string.home_metric_personal_day),
                    value = morningBrief?.personalDay?.toString() ?: "--",
                )
                DashboardMetricCard(
                    label = stringResource(R.string.home_metric_forecast),
                    value = when {
                        selectedProfile.canRequestForecast && dailyForecast?.overallScore != null -> "${(dailyForecast?.overallScore?.times(100) ?: 0f).toInt()}%"
                        selectedProfile.canRequestForecast -> stringResource(R.string.home_metric_forecast_syncing)
                        else -> stringResource(R.string.home_metric_forecast_needs_time)
                    },
                )
                DashboardMetricCard(
                    label = stringResource(R.string.home_metric_moon),
                    value = moonPhase?.phase?.let(::moonPhaseEmoji) ?: "🌙",
                )
                DashboardMetricCard(
                    label = stringResource(R.string.home_metric_profile),
                    value = selectedProfile.dataQuality.label,
                )
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = stringResource(R.string.home_todays_pulse_title),
                        style = MaterialTheme.typography.titleMedium,
                    )

                    when {
                        isLoading && morningBrief == null -> CircularProgressIndicator()

                        morningBriefError != null -> Text(
                            text = morningBriefError.orEmpty(),
                            color = MaterialTheme.colorScheme.error,
                        )

                        morningBrief != null -> {
                            morningBrief?.greeting?.takeIf { it.isNotBlank() }?.let { greeting ->
                                Text(
                                    text = greeting,
                                    style = MaterialTheme.typography.bodyLarge,
                                )
                            }
                            morningBrief?.vibe?.takeIf { it.isNotBlank() }?.let { vibe ->
                                Text(
                                    text = vibe,
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                            morningBrief?.bullets?.take(3)?.forEach { bullet ->
                                Text(
                                    text = listOfNotNull(bullet.emoji, bullet.text.takeIf { it.isNotBlank() }).joinToString(" "),
                                    style = MaterialTheme.typography.bodyMedium,
                                )
                            }
                        }

                        else -> {
                            Text(
                                text = stringResource(R.string.home_no_brief_message),
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }

                    Button(
                        onClick = {
                            refreshVersion += 1
                        },
                        enabled = !isLoading,
                    ) {
                        Text(stringResource(R.string.home_refresh_dashboard))
                    }
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                        text = stringResource(R.string.home_live_sky_title),
                    style = MaterialTheme.typography.titleMedium,
                )

                when {
                    isLoading && moonPhase == null -> CircularProgressIndicator()

                    moonPhaseError != null -> Text(
                        text = moonPhaseError.orEmpty(),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.error,
                    )

                    moonPhase != null -> {
                        Text(
                            text = "${moonPhaseEmoji(moonPhase?.phase)} ${moonPhase?.phase.orEmpty()}",
                            style = MaterialTheme.typography.titleLarge,
                        )
                        Text(
                            text = stringResource(R.string.home_illumination, (moonPhase?.illumination ?: 0f).toInt()),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Text(
                            text = moonPhase?.influence.orEmpty(),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }

                    else -> Text(
                        text = stringResource(R.string.home_moon_snapshot_missing),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

                TextButton(onClick = onOpenTools) {
                    Text(stringResource(R.string.home_open_moon_tools))
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text(
                    text = stringResource(R.string.home_todays_habits_title),
                    style = MaterialTheme.typography.titleMedium,
                )
                when {
                    localHabits.isEmpty() -> {
                        Text(
                            text = stringResource(R.string.home_habits_empty),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }

                    else -> {
                        Text(
                            text = stringResource(R.string.home_habits_progress, completedHabits, localHabits.size),
                            style = MaterialTheme.typography.bodyLarge,
                        )
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            openHabits.forEach { habit ->
                                AssistChip(
                                    onClick = onOpenTools,
                                    label = { Text("${habit.emoji} ${habit.name}") },
                                )
                            }
                        }
                    }
                }
                TextButton(onClick = onOpenTools) {
                    Text(stringResource(R.string.home_open_habits_workspace))
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = stringResource(R.string.home_forecast_spotlight_title),
                    style = MaterialTheme.typography.titleMedium,
                )

                when {
                    selectedProfile == null -> Text(
                        text = stringResource(R.string.home_forecast_requires_profile),
                        style = MaterialTheme.typography.bodyMedium,
                    )

                    isLoading && dailyForecast == null && selectedProfile.canRequestForecast -> CircularProgressIndicator()

                    !selectedProfile.canRequestForecast -> Text(
                        text = stringResource(R.string.home_forecast_requires_details),
                        style = MaterialTheme.typography.bodyMedium,
                    )

                    forecastError != null -> Text(
                        text = forecastError.orEmpty(),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.error,
                    )

                    dailyForecast != null -> {
                        dailyForecast?.overallScore?.let { score ->
                            AssistChip(
                                onClick = {},
                                label = { Text(stringResource(R.string.home_forecast_overall_score, (score * 100).toInt())) },
                            )
                        }
                        dailyForecast?.sections?.take(2)?.forEach { section ->
                            ForecastSectionCard(section = section)
                        }
                    }

                    else -> Text(
                        text = stringResource(R.string.home_forecast_none),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text(
                    text = stringResource(R.string.home_quick_tools_title),
                    style = MaterialTheme.typography.titleMedium,
                )
                Text(
                    text = stringResource(R.string.home_quick_tools_body),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    homeQuickTools.forEach { tool ->
                        AssistChip(
                            onClick = onOpenTools,
                            label = { Text("${tool.emoji} ${stringResource(tool.titleRes)}") },
                        )
                    }
                }
                Text(
                    text = stringResource(R.string.home_quick_tools_footer),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
private fun HomeBentoGrid(
    dailyForecast: DailyForecastData?,
    moonPhase: MoonPhaseInfoData?,
    completedHabits: Int,
    totalHabits: Int,
    onOpenReading: () -> Unit,
    onOpenWeeklyVibe: () -> Unit,
    onOpenTools: () -> Unit,
    onOpenCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier, verticalArrangement = Arrangement.spacedBy(12.dp)) {
        PremiumBentoCard(
            title = stringResource(R.string.home_bento_daily_reading_title),
            body = dailyForecast?.sections?.firstOrNull()?.summary
                ?: stringResource(R.string.home_bento_daily_reading_body),
            icon = "☀",
            badge = dailyForecast?.overallScore?.let {
                stringResource(R.string.home_bento_daily_reading_badge, (it * 100).toInt())
            } ?: stringResource(R.string.home_bento_daily_reading_badge_fallback),
            minHeight = 132,
            onClick = onOpenReading,
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            PremiumBentoCard(
                title = stringResource(R.string.home_bento_chart_studio_title),
                body = stringResource(R.string.home_bento_chart_studio_body),
                icon = "◎",
                badge = stringResource(R.string.home_bento_chart_studio_badge),
                modifier = Modifier.weight(1f),
                onClick = onOpenCharts,
            )
            PremiumBentoCard(
                title = stringResource(R.string.home_bento_daily_guide_title),
                body = stringResource(R.string.home_bento_daily_guide_body),
                icon = "✦",
                badge = stringResource(R.string.home_bento_daily_guide_badge),
                modifier = Modifier.weight(1f),
                onClick = onOpenTools,
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            PremiumBentoCard(
                title = stringResource(R.string.home_bento_weekly_vibe_title),
                body = stringResource(R.string.home_bento_weekly_vibe_body),
                icon = "↗",
                badge = stringResource(R.string.home_bento_weekly_vibe_badge),
                modifier = Modifier.weight(1f),
                onClick = onOpenWeeklyVibe,
            )
            PremiumBentoCard(
                title = stringResource(R.string.home_bento_moon_title),
                body = moonPhase?.influence?.takeIf { it.isNotBlank() }
                    ?: stringResource(R.string.home_bento_moon_body),
                icon = moonPhaseEmoji(moonPhase?.phase),
                badge = moonPhase?.phase ?: stringResource(R.string.home_bento_moon_badge_fallback),
                modifier = Modifier.weight(1f),
                onClick = onOpenTools,
            )
        }
        PremiumBentoCard(
            title = stringResource(R.string.home_bento_habits_title),
            body = if (totalHabits == 0) {
                stringResource(R.string.home_bento_habits_empty_body)
            } else {
                stringResource(R.string.home_bento_habits_progress_body, completedHabits, totalHabits)
            },
            icon = "✓",
            badge = stringResource(R.string.home_bento_habits_badge),
            minHeight = 132,
            onClick = onOpenTools,
        )
    }
}

@Composable
private fun NoProfileHeroCard(
    onCreateProfile: () -> Unit,
    onOpenTools: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.Transparent),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.linearGradient(
                        listOf(
                            MaterialTheme.colorScheme.primaryContainer,
                            MaterialTheme.colorScheme.surfaceVariant,
                        ),
                    ),
                    shape = RoundedCornerShape(28.dp),
                )
                .padding(20.dp),
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(
                    text = stringResource(R.string.home_no_profile_title),
                    style = MaterialTheme.typography.headlineSmall,
                )
                Text(
                    text = stringResource(R.string.home_no_profile_body),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Button(
                        onClick = onCreateProfile,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text(stringResource(R.string.home_create_profile))
                    }
                    TextButton(
                        onClick = onOpenTools,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text(stringResource(R.string.home_open_tools))
                    }
                }
            }
        }
    }
}

@Composable
private fun HomeHeroCard(
    selectedProfile: AppProfile,
    morningBrief: MorningBriefData?,
    dailyForecast: DailyForecastData?,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenTools: () -> Unit,
    onOpenCharts: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.Transparent),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.linearGradient(
                        listOf(
                            MaterialTheme.colorScheme.primaryContainer,
                            MaterialTheme.colorScheme.tertiaryContainer,
                        ),
                    ),
                    shape = RoundedCornerShape(28.dp),
                )
                .padding(20.dp),
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(
                    text = selectedProfile.displayName(
                        hideSensitive = hideSensitiveDetailsEnabled,
                        role = PrivacyDisplayRole.ACTIVE_USER,
                    ),
                    style = MaterialTheme.typography.titleLarge,
                )
                Text(
                    text = morningBrief?.vibe?.takeIf { it.isNotBlank() }
                        ?: dailyForecast?.sections?.firstOrNull()?.summary
                        ?: stringResource(R.string.home_profile_default_vibe),
                    style = MaterialTheme.typography.headlineSmall,
                )
                Text(
                    text = morningBrief?.greeting?.takeIf { it.isNotBlank() }
                        ?: stringResource(
                            R.string.home_profile_details_fallback,
                            selectedProfile.dataQuality.label,
                            selectedProfile.timezone ?: stringResource(R.string.home_timezone_missing),
                        ),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Button(
                        onClick = onOpenTools,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text(stringResource(R.string.home_open_tools))
                    }
                    TextButton(
                        onClick = onOpenCharts,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text(stringResource(R.string.home_open_charts))
                    }
                }
            }
        }
    }
}

@Composable
private fun DashboardMetricCard(
    label: String,
    value: String,
) {
    Card(modifier = Modifier.widthIn(min = 116.dp)) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
            )
        }
    }
}

private val homeQuickTools = listOf(
    HomeQuickTool(titleRes = R.string.home_quick_tool_tarot, emoji = "♠"),
    HomeQuickTool(titleRes = R.string.home_quick_tool_oracle, emoji = "?"),
    HomeQuickTool(titleRes = R.string.home_quick_tool_affirmation, emoji = "★"),
    HomeQuickTool(titleRes = R.string.home_quick_tool_moon, emoji = "☾"),
    HomeQuickTool(titleRes = R.string.home_quick_tool_timing, emoji = "◷"),
)

private data class HomeQuickTool(
    @StringRes val titleRes: Int,
    val emoji: String,
)

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

@Composable
private fun ForecastSectionCard(section: ForecastSectionData) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = section.title,
                style = MaterialTheme.typography.titleSmall,
            )
            Text(
                text = section.summary,
                style = MaterialTheme.typography.bodyMedium,
            )

            if (section.topics.isNotEmpty()) {
                val topTopics = section.topics.entries.sortedByDescending { it.value }.take(3)
                topTopics.forEach { topic ->
                    Text(
                        text = "${topic.key}: ${(topic.value * 100).toInt()}%",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }

            if (section.embrace.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.home_forecast_embrace, section.embrace.joinToString()),
                    style = MaterialTheme.typography.bodySmall,
                )
            }

            if (section.avoid.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.home_forecast_avoid, section.avoid.joinToString()),
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        }
    }
}

private fun shareCosmicID(
    context: Context,
    profile: AppProfile,
    personalDay: Int?,
    hideSensitiveDetailsEnabled: Boolean,
    shareLabel: String,
) {
    val name = if (hideSensitiveDetailsEnabled) "Cosmic Traveler" else profile.name
    val sunSign = profile.zodiacSignName()?.replaceFirstChar { it.uppercase() } ?: "—"
    val lifePath = homeLifePathNumber(profile)?.toString() ?: "—"
    val text = buildString {
        appendLine("✦ ASTRONUMERIC")
        appendLine()
        appendLine(name.uppercase())
        appendLine("☀ Sun Sign: $sunSign")
        appendLine("🔢 Life Path: $lifePath")
        if (personalDay != null) appendLine("📅 Personal Day: $personalDay")
    }
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, text.trim())
    }
    context.startActivity(Intent.createChooser(intent, shareLabel))
}

private fun homeLifePathNumber(profile: AppProfile): Int? = runCatching {
    homeReduceLifePathNumber(profile.dateOfBirth.filter(Char::isDigit).sumOf(Char::digitToInt))
}.getOrNull()

private fun homeReduceLifePathNumber(value: Int): Int {
    var current = value
    while (current !in setOf(11, 22, 33) && current > 9) {
        current = current.toString().sumOf(Char::digitToInt)
    }
    return current
}
