package com.astromeric.android.feature.home

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
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
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
import com.astromeric.android.core.ui.PremiumBentoCard
import com.astromeric.android.core.ui.PremiumHeroCard

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

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        moonPhaseError = null
        moonPhase = remoteDataSource.fetchMoonPhase()
            .onFailure { moonPhaseError = it.message ?: "Moon phase could not be loaded." }
            .getOrNull()

        if (selectedProfile != null) {
            isLoading = true
            morningBriefError = null
            forecastError = null
            val widgetSnapshotStore = MorningBriefWidgetSnapshotStore(context)

            morningBrief = remoteDataSource.fetchMorningBrief(selectedProfile)
                .onFailure { morningBriefError = it.message ?: "Morning brief could not be loaded." }
                .getOrNull()

            widgetSnapshotStore.writeSnapshot(
                morningBrief = morningBrief,
                moonPhaseName = moonPhase?.phase,
                moonGuidance = moonPhase?.influence,
            )
            MorningBriefWidgetProvider.refreshAllWidgets(context)

            dailyForecast = if (selectedProfile.canRequestForecast) {
                remoteDataSource.fetchDailyForecast(selectedProfile)
                    .onFailure { forecastError = it.message ?: "Daily forecast could not be loaded." }
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

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = "Home",
            title = if (selectedProfile == null) "Build Your Cosmic Blueprint" else "Your Cosmic Blueprint",
            body = if (selectedProfile == null) {
                "Create a profile to unlock the same daily reading, moon context, and planning dashboard shape used across iOS."
            } else {
                "Personal day, moon context, forecasts, and planning windows in one daily dashboard."
            },
            chips = listOfNotNull(
                selectedProfile?.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)?.let { "Active profile: $it" },
                morningBrief?.personalDay?.let { "Personal day $it" },
                moonPhase?.phase,
            ),
        )

        if (selectedProfile == null) {
            NoProfileHeroCard(
                onCreateProfile = onCreateProfile,
                onOpenTools = onOpenTools,
            )
        } else {
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
            )

            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                DashboardMetricCard(
                    label = "Personal day",
                    value = morningBrief?.personalDay?.toString() ?: "--",
                )
                DashboardMetricCard(
                    label = "Forecast",
                    value = when {
                        selectedProfile.canRequestForecast && dailyForecast?.overallScore != null -> "${(dailyForecast?.overallScore?.times(100) ?: 0f).toInt()}%"
                        selectedProfile.canRequestForecast -> "Syncing"
                        else -> "Needs time"
                    },
                )
                DashboardMetricCard(
                    label = "Moon",
                    value = moonPhase?.phase?.let(::moonPhaseEmoji) ?: "🌙",
                )
                DashboardMetricCard(
                    label = "Profile",
                    value = selectedProfile.dataQuality.label,
                )
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = "Today's pulse",
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
                                text = "The API layer is wired but has not returned a brief yet.",
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
                        Text("Refresh dashboard")
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
                    text = "Live sky",
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
                            text = "Illumination ${(moonPhase?.illumination ?: 0f).toInt()}%",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Text(
                            text = moonPhase?.influence.orEmpty(),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }

                    else -> Text(
                        text = "The moon snapshot has not loaded yet.",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

                TextButton(onClick = onOpenTools) {
                    Text("Open moon tools")
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text(
                    text = "Today's habits",
                    style = MaterialTheme.typography.titleMedium,
                )
                when {
                    localHabits.isEmpty() -> {
                        Text(
                            text = "Build a few habits to turn the daily forecast into something trackable. The habits workspace is already wired on Android.",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }

                    else -> {
                        Text(
                            text = "$completedHabits of ${localHabits.size} habits completed today",
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
                    Text("Open habits workspace")
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = "Forecast spotlight",
                    style = MaterialTheme.typography.titleMedium,
                )

                when {
                    selectedProfile == null -> Text(
                        text = "Create a profile to unlock personal forecast sections, scores, and timing guidance.",
                        style = MaterialTheme.typography.bodyMedium,
                    )

                    isLoading && dailyForecast == null && selectedProfile.canRequestForecast -> CircularProgressIndicator()

                    !selectedProfile.canRequestForecast -> Text(
                        text = "Forecasts require birth time, coordinates, and timezone. The dashboard still keeps the brief and moon context live while profile quality is incomplete.",
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
                                label = { Text("Overall ${(score * 100).toInt()}%") },
                            )
                        }
                        dailyForecast?.sections?.take(2)?.forEach { section ->
                            ForecastSectionCard(section = section)
                        }
                    }

                    else -> Text(
                        text = "No daily forecast has been returned yet.",
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
                    text = "Quick Tools",
                    style = MaterialTheme.typography.titleMedium,
                )
                Text(
                    text = "Jump into the same daily tool set the iOS home dashboard surfaces first.",
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
                            label = { Text("${tool.emoji} ${tool.title}") },
                        )
                    }
                }
                Text(
                    text = "Each shortcut opens Tools, where the live module is already loaded.",
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
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        PremiumBentoCard(
            title = "Daily Reading",
            body = dailyForecast?.sections?.firstOrNull()?.summary
                ?: "Pull a full personalized reading for today, this week, or the month ahead.",
            icon = "☀",
            badge = dailyForecast?.overallScore?.let { "${(it * 100).toInt()}% forecast" } ?: "Personalized",
            minHeight = 132,
            onClick = onOpenReading,
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            PremiumBentoCard(
                title = "Chart Studio",
                body = "Birth chart, progressed, synastry, and composite entry points.",
                icon = "◎",
                badge = "Calculated",
                modifier = Modifier.weight(1f),
                onClick = onOpenCharts,
            )
            PremiumBentoCard(
                title = "Daily Guide",
                body = "Personal day, moon phase, retrogrades, and cues.",
                icon = "✦",
                badge = "Live",
                modifier = Modifier.weight(1f),
                onClick = onOpenTools,
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            PremiumBentoCard(
                title = "Weekly Vibe",
                body = "Themes, energy patterns, and what to embrace across seven days.",
                icon = "↗",
                badge = "Timeline",
                modifier = Modifier.weight(1f),
                onClick = onOpenWeeklyVibe,
            )
            PremiumBentoCard(
                title = "Moon",
                body = moonPhase?.influence?.takeIf { it.isNotBlank() }
                    ?: "Current lunar phase and ritual weather.",
                icon = moonPhaseEmoji(moonPhase?.phase),
                badge = moonPhase?.phase ?: "Live sky",
                modifier = Modifier.weight(1f),
                onClick = onOpenTools,
            )
        }
        PremiumBentoCard(
            title = "Habits",
            body = if (totalHabits == 0) {
                "Turn the forecast into something trackable."
            } else {
                "$completedHabits of $totalHabits habits completed today."
            },
            icon = "✓",
            badge = "Practice",
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
                    text = "Start your cosmic dashboard",
                    style = MaterialTheme.typography.headlineSmall,
                )
                Text(
                    text = "You can browse the shell now, but a profile is what unlocks the real dashboard: chart context, personal day, forecast sections, and timing that feels specific.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Button(
                        onClick = onCreateProfile,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text("Create profile")
                    }
                    TextButton(
                        onClick = onOpenTools,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text("Open tools")
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
                        ?: "Your chart, forecast, and timing stack are ready for a proper daily read.",
                    style = MaterialTheme.typography.headlineSmall,
                )
                Text(
                    text = morningBrief?.greeting?.takeIf { it.isNotBlank() }
                        ?: "${selectedProfile.dataQuality.label} · ${selectedProfile.timezone ?: "Timezone missing"}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Button(
                        onClick = onOpenTools,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text("Open tools")
                    }
                    TextButton(
                        onClick = onOpenCharts,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text("Open charts")
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
    HomeQuickTool(title = "Tarot", emoji = "♠"),
    HomeQuickTool(title = "Oracle", emoji = "?"),
    HomeQuickTool(title = "Affirmation", emoji = "★"),
    HomeQuickTool(title = "Moon", emoji = "☾"),
    HomeQuickTool(title = "Timing", emoji = "◷"),
)

private data class HomeQuickTool(
    val title: String,
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
                    text = "Embrace: ${section.embrace.joinToString()}",
                    style = MaterialTheme.typography.bodySmall,
                )
            }

            if (section.avoid.isNotEmpty()) {
                Text(
                    text = "Avoid: ${section.avoid.joinToString()}",
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        }
    }
}
