package com.astromeric.android.feature.charts

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.local.NatalChartCacheStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.ephemeris.LocalSwissEphemerisEngine
import com.astromeric.android.core.data.repository.loadNatalChartWithCacheFallback
import com.astromeric.android.core.model.AIExplainRequestData
import com.astromeric.android.core.model.AIExplainSectionData
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.ChartAspect
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.ChartPoint
import com.astromeric.android.core.model.HousePlacement
import com.astromeric.android.core.model.NumerologyData
import com.astromeric.android.core.model.PlanetPlacement
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.SynastryAspectData
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PremiumAction
import com.astromeric.android.core.ui.PremiumActionRow
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumHeroCard
import com.astromeric.android.core.ui.PremiumLoadingCard
import com.astromeric.android.core.ui.PremiumStatusCard
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

private enum class ChartsStudioTab(
    val label: String,
    val subtitle: String,
) {
    BIRTH(
        label = "Birth Chart",
        subtitle = "Read the natal structure first, then branch into timing or compatibility when the base pattern is clear.",
    ),
    NUMEROLOGY(
        label = "Numerology",
        subtitle = "Use numbers as a parallel system for identity, timing, and motivation instead of treating them like detached trivia.",
    ),
    COMPATIBILITY(
        label = "Compatibility",
        subtitle = "Move from general chemistry into relationship timing and aspect-level comparison when you need more precision.",
    ),
    ADVANCED(
        label = "Advanced",
        subtitle = "Choose the chart layer that matches the question: year-ahead timing, inner development, or relational structure.",
    ),
}

internal enum class NumerologyMethod(
    val wireValue: String,
    val label: String,
    val description: String,
) {
    PYTHAGOREAN(
        wireValue = "pythagorean",
        label = "Pythagorean",
        description = "Default Western system with familiar 1-9 number reduction.",
    ),
    CHALDEAN(
        wireValue = "chaldean",
        label = "Chaldean",
        description = "Older 1-8 system that shifts name-number emphasis and tone.",
    ),
}

@Composable
@OptIn(ExperimentalMaterial3Api::class)
fun ChartsScreen(
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    authAccessToken: String,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenRelationships: () -> Unit,
    onOpenYearAhead: () -> Unit,
    onOpenBirthChart: () -> Unit,
    onOpenProgressions: () -> Unit,
    onOpenSynastry: () -> Unit,
    onOpenComposite: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val chartCacheStore = remember(context) { NatalChartCacheStore(context.applicationContext) }
    val localEphemerisEngine = remember(context) { LocalSwissEphemerisEngine.getInstance(context.applicationContext) }
    val partnerProfiles = remember(profiles, selectedProfile?.id) {
        profiles.filter { profile -> profile.id != selectedProfile?.id }
    }
    var selectedTab by rememberSaveable { mutableStateOf(ChartsStudioTab.BIRTH) }

    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoadingBirthChart by remember(selectedProfile?.id) { mutableStateOf(false) }
    var natalChart by remember(selectedProfile?.id) { mutableStateOf<ChartData?>(null) }
    var birthChartError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var birthChartSource by remember(selectedProfile?.id) { mutableStateOf<AstroDataSource?>(null) }
    var cachedChartActive by remember(selectedProfile?.id) { mutableStateOf(false) }
    var cachedAtEpochMillis by remember(selectedProfile?.id) { mutableStateOf<Long?>(null) }

    var selectedMethod by rememberSaveable { mutableStateOf(NumerologyMethod.PYTHAGOREAN) }
    var isLoadingNumerology by remember(selectedProfile?.id, selectedMethod) { mutableStateOf(false) }
    var numerologyData by remember(selectedProfile?.id, selectedMethod) { mutableStateOf<NumerologyData?>(null) }
    var numerologyError by remember(selectedProfile?.id, selectedMethod) { mutableStateOf<String?>(null) }
    var isExplainingNumerology by remember(selectedProfile?.id, selectedMethod) { mutableStateOf(false) }
    var numerologyExplanationSummary by remember(selectedProfile?.id, selectedMethod, refreshVersion) { mutableStateOf<String?>(null) }
    var numerologyExplanationProvider by remember(selectedProfile?.id, selectedMethod, refreshVersion) { mutableStateOf<String?>(null) }
    var numerologyExplanationGeneratedAt by remember(selectedProfile?.id, selectedMethod, refreshVersion) { mutableStateOf<Instant?>(null) }
    var showNumerologyExplanationSheet by remember(selectedProfile?.id, selectedMethod, refreshVersion) { mutableStateOf(false) }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile
        if (profile?.canRequestNatalChart == true) {
            isLoadingBirthChart = true
            birthChartError = null
            birthChartSource = null
            cachedChartActive = false
            cachedAtEpochMillis = null

            val result = loadNatalChartWithCacheFallback(
                profile = profile,
                remoteDataSource = remoteDataSource,
                chartCacheStore = chartCacheStore,
                localEphemerisEngine = localEphemerisEngine,
            )
            natalChart = result.chart
            birthChartSource = result.source
            cachedChartActive = result.isCached
            cachedAtEpochMillis = result.cachedAtEpochMillis
            birthChartError = if (result.chart == null) result.errorMessage else null
            isLoadingBirthChart = false
        } else {
            natalChart = null
            birthChartError = null
            birthChartSource = null
            cachedChartActive = false
            cachedAtEpochMillis = null
            isLoadingBirthChart = false
        }
    }

    LaunchedEffect(selectedProfile?.id, selectedMethod) {
        val profile = selectedProfile
        if (profile == null) {
            numerologyData = null
            numerologyError = null
            isLoadingNumerology = false
            return@LaunchedEffect
        }

        isLoadingNumerology = true
        numerologyError = null
        remoteDataSource.fetchNumerology(profile = profile, method = selectedMethod.wireValue)
            .onSuccess { numerologyData = it }
            .onFailure {
                numerologyData = null
                numerologyError = it.message ?: "Numerology profile could not be loaded."
            }
        isLoadingNumerology = false
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        ChartsStudioHeroCard()
        ChartStudioTabRow(selectedTab = selectedTab, onSelected = { selectedTab = it })
        Text(
            text = selectedTab.subtitle,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        when (selectedTab) {
            ChartsStudioTab.BIRTH -> BirthChartTab(
                selectedProfile = selectedProfile,
                natalChart = natalChart,
                isLoading = isLoadingBirthChart,
                errorMessage = birthChartError,
                chartSource = birthChartSource,
                cachedChartActive = cachedChartActive,
                cachedAtEpochMillis = cachedAtEpochMillis,
                onRefresh = { refreshVersion += 1 },
                onOpenBirthChart = onOpenBirthChart,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            )

            ChartsStudioTab.NUMEROLOGY -> NumerologyTab(
                selectedProfile = selectedProfile,
                selectedMethod = selectedMethod,
                onSelectMethod = { selectedMethod = it },
                isLoading = isLoadingNumerology,
                errorMessage = numerologyError,
                numerology = numerologyData,
                isExplaining = isExplainingNumerology,
                onExplain = { isExplainingNumerology = true },
            )

            ChartsStudioTab.COMPATIBILITY -> CompatibilityTab(
                selectedProfile = selectedProfile,
                partnerProfiles = partnerProfiles,
                onOpenRelationships = onOpenRelationships,
                onOpenSynastry = onOpenSynastry,
            )

            ChartsStudioTab.ADVANCED -> AdvancedChartsTab(
                selectedProfile = selectedProfile,
                partnerProfiles = partnerProfiles,
                onOpenYearAhead = onOpenYearAhead,
                onOpenProgressions = onOpenProgressions,
                onOpenSynastry = onOpenSynastry,
                onOpenComposite = onOpenComposite,
            )
        }
    }

    if (showNumerologyExplanationSheet && numerologyExplanationSummary != null) {
        ModalBottomSheet(
            onDismissRequest = { showNumerologyExplanationSheet = false },
        ) {
            NumerologyExplanationSheet(
                markdown = numerologyExplanationSummary.orEmpty(),
                provider = numerologyExplanationProvider,
                generatedAt = numerologyExplanationGeneratedAt,
                isExplaining = isExplainingNumerology,
                onRegenerate = { isExplainingNumerology = true },
            )
        }
    }

    LaunchedEffect(isExplainingNumerology) {
        if (!isExplainingNumerology) return@LaunchedEffect

        val loadedNumerology = numerologyData ?: run {
            isExplainingNumerology = false
            return@LaunchedEffect
        }
        val profile = selectedProfile ?: run {
            isExplainingNumerology = false
            return@LaunchedEffect
        }

        val fallback = buildNumerologyFallbackSummary(profile, loadedNumerology)
        val explainResult = remoteDataSource.fetchAIExplain(
            authToken = authAccessToken.takeIf { it.isNotBlank() },
            request = buildNumerologyExplainRequest(profile, loadedNumerology),
        ).getOrNull()

        numerologyExplanationSummary = explainResult?.summary ?: fallback
        numerologyExplanationProvider = explainResult?.provider ?: "fallback"
        numerologyExplanationGeneratedAt = Instant.now()
        showNumerologyExplanationSheet = true
        isExplainingNumerology = false
    }
}

@Composable
private fun ChartsStudioHeroCard() {
    PremiumHeroCard(
        eyebrow = "Charts",
        title = "Charts Studio",
        body = "See your structure, not just isolated symbols. Move between birth chart, numerology, compatibility, and advanced timing without losing the thread.",
        chips = listOf("Birth chart", "Numerology", "Compatibility", "Advanced timing"),
    )
}

@Composable
private fun ChartStudioTabRow(
    selectedTab: ChartsStudioTab,
    onSelected: (ChartsStudioTab) -> Unit,
) {
    Row(
        modifier = Modifier.horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        ChartsStudioTab.entries.forEach { tab ->
            FilterChip(
                selected = selectedTab == tab,
                onClick = { onSelected(tab) },
                label = { Text(tab.label) },
            )
        }
    }
}

@Composable
fun StudioSectionCard(
    title: String,
    subtitle: String,
    content: @Composable () -> Unit,
) {
    PremiumContentCard(
        title = title,
        body = subtitle,
    ) {
        content()
    }
}

@Composable
internal fun StudioActionCard(
    title: String,
    subtitle: String,
    buttonLabel: String,
    onClick: () -> Unit,
    enabled: Boolean = true,
    note: String? = null,
) {
    PremiumContentCard(
        title = title,
        body = subtitle,
        footer = note,
    ) {
        PremiumActionRow(
            actions = listOf(
                PremiumAction(
                    label = buttonLabel,
                    onClick = onClick,
                    primary = true,
                    enabled = enabled,
                ),
            ),
        )
    }
}

@Composable
fun StatusCard(
    message: String,
    isError: Boolean,
) {
    PremiumStatusCard(
        title = if (isError) "Charts unavailable" else "Charts status",
        message = message,
        isError = isError,
    )
}

@Composable
fun PlanetPlacementRow(placement: PlanetPlacement) {
    Text(
        text = buildString {
            append("${placement.name}: ${placement.sign} ${"%.1f".format(placement.degree)}°")
            placement.house?.let { append(" · House $it") }
            placement.dignity?.takeIf { it.isNotBlank() }?.let { append(" · $it") }
            if (placement.retrograde == true) {
                append(" · Rx")
            }
        },
        style = MaterialTheme.typography.bodyMedium,
    )
}

@Composable
fun HousePlacementRow(house: HousePlacement) {
    Text(
        text = "House ${house.house}: ${house.sign}${house.degree?.let { " ${"%.1f".format(it)}°" } ?: ""}",
        style = MaterialTheme.typography.bodyMedium,
    )
}

@Composable
fun AspectRow(aspect: ChartAspect) {
    Text(
        text = buildString {
            append("${aspect.planetA} ${aspect.type} ${aspect.planetB}")
            aspect.orb?.let { append(" · orb ${"%.1f".format(it)}°") }
            aspect.strength?.let { append(" · ${(it * 100).toInt()}%") }
        },
        style = MaterialTheme.typography.bodyMedium,
    )
}

@Composable
fun SynastryAspectRow(aspect: SynastryAspectData) {
    Text(
        text = "${aspect.planet1} ${aspect.aspect} ${aspect.planet2} · orb ${"%.1f".format(aspect.orb)}°${if (aspect.applying) " · applying" else ""}",
        style = MaterialTheme.typography.bodyMedium,
    )
}

@Composable
fun CompositePlanetRow(planet: ChartPoint) {
    Text(
        text = "${planet.name}: ${planet.sign} ${"%.1f".format(planet.degree)}°",
        style = MaterialTheme.typography.bodyMedium,
    )
}

private fun buildNumerologyExplainRequest(
    profile: AppProfile,
    numerology: NumerologyData,
): AIExplainRequestData {
    val sections = buildList {
        add(
            AIExplainSectionData(
                title = "Life Path ${numerology.lifePath.number}",
                highlights = listOfNotNull(numerology.lifePath.meaning, numerology.lifePath.lifePurpose).take(3),
            ),
        )
        add(
            AIExplainSectionData(
                title = "Core Numbers",
                highlights = buildList {
                    add("Destiny ${numerology.destinyNumber}: ${numerology.destinyInterpretation}")
                    add("Personal Year ${numerology.personalYear.cycleNumber}: ${numerology.personalYear.interpretation}")
                    numerology.numerologyInsights["soul_urge"]?.takeIf { it.isNotBlank() }?.let { add("Soul Urge: $it") }
                    numerology.numerologyInsights["personality"]?.takeIf { it.isNotBlank() }?.let { add("Personality: $it") }
                },
            ),
        )
        if (numerology.personalYear.focusAreas.isNotEmpty()) {
            add(
                AIExplainSectionData(
                    title = "Current Focus",
                    highlights = numerology.personalYear.focusAreas.take(5),
                ),
            )
        }
        numerology.synthesis?.let { synthesis ->
            if (synthesis.dominantNumbers.isNotEmpty()) {
                add(
                    AIExplainSectionData(
                        title = "Dominant Numbers",
                        highlights = synthesis.dominantNumbers.take(4).map { "${it.label} ${it.number}: ${it.meaning}" },
                    ),
                )
            }
            if (synthesis.strengths.isNotEmpty()) {
                add(AIExplainSectionData(title = "Strengths", highlights = synthesis.strengths.take(4)))
            }
            if (synthesis.growthEdges.isNotEmpty()) {
                add(AIExplainSectionData(title = "Growth Edges", highlights = synthesis.growthEdges.take(4)))
            }
        }
    }

    return AIExplainRequestData(
        scope = "numerology",
        headline = "Numerology for ${profile.displayName(false, PrivacyDisplayRole.ACTIVE_USER)} • Life Path ${numerology.lifePath.number}",
        theme = numerology.synthesis?.currentFocus ?: numerology.lifePath.meaning,
        sections = sections,
        numerologySummary = numerology.synthesis?.summary,
        simpleLanguage = true,
    )
}

private fun buildNumerologyFallbackSummary(
    profile: AppProfile,
    numerology: NumerologyData,
): String {
    val strengths = numerology.synthesis?.strengths?.take(3).orEmpty()
    val growthEdges = numerology.synthesis?.growthEdges?.take(2).orEmpty()
    val focusAreas = numerology.personalYear.focusAreas.take(3)
    return buildString {
        appendLine("## TL;DR")
        appendLine()
        appendLine("${profile.displayName(false, PrivacyDisplayRole.ACTIVE_USER)} is moving through a **Life Path ${numerology.lifePath.number}** story. The current year emphasizes **${numerology.personalYear.interpretation.lowercase()}** through Personal Year ${numerology.personalYear.cycleNumber}.")
        appendLine()
        appendLine("---")
        appendLine()
        appendLine("## Core thread")
        appendLine("- Life Path ${numerology.lifePath.number}: ${numerology.lifePath.meaning}")
        appendLine("- Destiny ${numerology.destinyNumber}: ${numerology.destinyInterpretation}")
        numerology.numerologyInsights["soul_urge"]?.takeIf { it.isNotBlank() }?.let { appendLine("- Soul Urge: $it") }
        numerology.numerologyInsights["personality"]?.takeIf { it.isNotBlank() }?.let { appendLine("- Personality: $it") }
        if (focusAreas.isNotEmpty()) {
            appendLine()
            appendLine("## Current focus")
            focusAreas.forEach { focusArea -> appendLine("- $focusArea") }
        }
        if (strengths.isNotEmpty()) {
            appendLine()
            appendLine("## Strengths to lean on")
            strengths.forEach { strength -> appendLine("- $strength") }
        }
        if (growthEdges.isNotEmpty()) {
            appendLine()
            appendLine("## Growth edge")
            growthEdges.forEach { edge -> appendLine("- $edge") }
        }
        appendLine()
        appendLine("## Practical next step")
        append("Pick **one focus area** from this Personal Year and pair it with **one Life Path strength** you can practice consistently this week.")
    }.trim()
}

internal fun formatChartCacheTimestamp(epochMillis: Long): String =
    DateTimeFormatter.ofPattern("MMM d, h:mm a", Locale.getDefault())
        .withZone(ZoneId.systemDefault())
        .format(Instant.ofEpochMilli(epochMillis))
