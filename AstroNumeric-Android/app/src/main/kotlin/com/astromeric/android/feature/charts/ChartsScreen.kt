package com.astromeric.android.feature.charts

import android.content.Context
import androidx.annotation.StringRes
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
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
import com.astromeric.android.core.ui.PremiumSectionHeader
import com.astromeric.android.core.ui.PremiumStatusCard
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

internal enum class NumerologyMethod(
    val wireValue: String,
    @StringRes val labelRes: Int,
    @StringRes val descriptionRes: Int,
) {
    PYTHAGOREAN(
        wireValue = "pythagorean",
        labelRes = R.string.charts_method_pythagorean_label,
        descriptionRes = R.string.charts_method_pythagorean_description,
    ),
    CHALDEAN(
        wireValue = "chaldean",
        labelRes = R.string.charts_method_chaldean_label,
        descriptionRes = R.string.charts_method_chaldean_description,
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
    onOpenNumerology: () -> Unit,
    onOpenCompatibility: () -> Unit,
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
                numerologyError = it.message ?: context.getString(R.string.charts_numerology_error_load)
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
        ChartsHubSection(
            title = stringResource(R.string.charts_tab_birth_label),
            subtitle = stringResource(R.string.charts_tab_birth_subtitle),
        ) {
            BirthChartTab(
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
        }

        ChartsHubSection(
            title = stringResource(R.string.charts_tab_numerology_label),
            subtitle = stringResource(R.string.charts_tab_numerology_subtitle),
        ) {
            NumerologyTab(
                selectedProfile = selectedProfile,
                selectedMethod = selectedMethod,
                onSelectMethod = { selectedMethod = it },
                isLoading = isLoadingNumerology,
                errorMessage = numerologyError,
                numerology = numerologyData,
                isExplaining = isExplainingNumerology,
                onExplain = { isExplainingNumerology = true },
                onOpenFullScreen = onOpenNumerology,
            )
        }

        ChartsHubSection(
            title = stringResource(R.string.charts_tab_compatibility_label),
            subtitle = stringResource(R.string.charts_tab_compatibility_subtitle),
        ) {
            CompatibilityTab(
                selectedProfile = selectedProfile,
                partnerProfiles = partnerProfiles,
                onOpenCompatibility = onOpenCompatibility,
                onOpenRelationships = onOpenRelationships,
                onOpenSynastry = onOpenSynastry,
            )
        }

        ChartsHubSection(
            title = stringResource(R.string.charts_tab_advanced_label),
            subtitle = stringResource(R.string.charts_tab_advanced_subtitle),
        ) {
            AdvancedChartsTab(
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

        val explainResult = remoteDataSource.fetchAIExplain(
            authToken = authAccessToken.takeIf { it.isNotBlank() },
            request = buildNumerologyExplainRequest(context, profile, loadedNumerology),
        ).getOrNull()

        numerologyExplanationSummary = explainResult?.summary ?: buildNumerologyFallbackSummary(context, profile, loadedNumerology)
        numerologyExplanationProvider = explainResult?.provider ?: "fallback"
        numerologyExplanationGeneratedAt = Instant.now()
        showNumerologyExplanationSheet = true
        isExplainingNumerology = false
    }
}

@Composable
private fun ChartsStudioHeroCard() {
    PremiumHeroCard(
        eyebrow = stringResource(R.string.charts_hero_eyebrow),
        title = stringResource(R.string.charts_hero_title),
        body = stringResource(R.string.charts_hero_body),
        chips = listOf(
            stringResource(R.string.charts_hero_chip_birth),
            stringResource(R.string.charts_hero_chip_numerology),
            stringResource(R.string.charts_hero_chip_compatibility),
            stringResource(R.string.charts_hero_chip_advanced),
        ),
    )
}

@Composable
private fun ChartsHubSection(
    title: String,
    subtitle: String,
    content: @Composable () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        PremiumSectionHeader(
            title = title,
            subtitle = subtitle,
        )
        content()
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
        title = if (isError) stringResource(R.string.charts_status_unavailable) else stringResource(R.string.charts_status_normal),
        message = message,
        isError = isError,
    )
}

@Composable
fun PlanetPlacementRow(placement: PlanetPlacement) {
    val houseLabel = placement.house?.let { stringResource(R.string.charts_row_house, it) }
    val retrogradeLabel = if (placement.retrograde == true) stringResource(R.string.charts_row_retrograde) else null
    Text(
        text = buildString {
            append("${placement.name}: ${placement.sign} ${"%.1f".format(placement.degree)}°")
            houseLabel?.let { append(" · $it") }
            placement.dignity?.takeIf { it.isNotBlank() }?.let { append(" · $it") }
            retrogradeLabel?.let { append(" · $it") }
        },
        style = MaterialTheme.typography.bodyMedium,
    )
}

@Composable
fun HousePlacementRow(house: HousePlacement) {
    val text = house.degree?.let { degree ->
        stringResource(R.string.charts_house_placement_format_degree, house.house, house.sign, degree)
    } ?: stringResource(R.string.charts_house_placement_format, house.house, house.sign)
    Text(
        text = text,
        style = MaterialTheme.typography.bodyMedium,
    )
}

@Composable
fun AspectRow(aspect: ChartAspect) {
    val orbLabel = aspect.orb?.let { stringResource(R.string.charts_row_orb, it) }
    val strengthLabel = aspect.strength?.let { stringResource(R.string.charts_row_strength, (it * 100).toInt()) }
    Text(
        text = buildString {
            append("${aspect.planetA} ${aspect.type} ${aspect.planetB}")
            orbLabel?.let { append(" · $it") }
            strengthLabel?.let { append(" · $it") }
        },
        style = MaterialTheme.typography.bodyMedium,
    )
}

@Composable
fun SynastryAspectRow(aspect: SynastryAspectData) {
    val applyingSuffix = if (aspect.applying) " · ${stringResource(R.string.charts_row_applying)}" else ""
    Text(
        text = stringResource(
            R.string.charts_synastry_aspect_row,
            aspect.planet1,
            aspect.aspect,
            aspect.planet2,
            aspect.orb,
            applyingSuffix,
        ),
        style = MaterialTheme.typography.bodyMedium,
    )
}

@Composable
fun CompositePlanetRow(planet: ChartPoint) {
    Text(
        text = stringResource(R.string.charts_composite_planet_row, planet.name, planet.sign, planet.degree),
        style = MaterialTheme.typography.bodyMedium,
    )
}

internal fun buildNumerologyExplainRequest(
    context: Context,
    profile: AppProfile,
    numerology: NumerologyData,
): AIExplainRequestData {
    val sections = buildList {
        add(
            AIExplainSectionData(
                title = context.getString(R.string.charts_numerology_ai_title_life_path, numerology.lifePath.number),
                highlights = listOfNotNull(numerology.lifePath.meaning, numerology.lifePath.lifePurpose).take(3),
            ),
        )
        add(
            AIExplainSectionData(
                title = context.getString(R.string.charts_numerology_ai_title_core_numbers),
                highlights = buildList {
                    add(context.getString(R.string.charts_numerology_ai_destiny_highlight, numerology.destinyNumber, numerology.destinyInterpretation))
                    add(context.getString(R.string.charts_numerology_ai_personal_year_highlight, numerology.personalYear.cycleNumber, numerology.personalYear.interpretation))
                    numerology.numerologyInsights["soul_urge"]?.takeIf { it.isNotBlank() }?.let {
                        add(context.getString(R.string.charts_numerology_ai_soul_urge_highlight, it))
                    }
                    numerology.numerologyInsights["personality"]?.takeIf { it.isNotBlank() }?.let {
                        add(context.getString(R.string.charts_numerology_ai_personality_highlight, it))
                    }
                },
            ),
        )
        if (numerology.personalYear.focusAreas.isNotEmpty()) {
            add(
                AIExplainSectionData(
                    title = context.getString(R.string.charts_numerology_ai_title_current_focus),
                    highlights = numerology.personalYear.focusAreas.take(5),
                ),
            )
        }
        numerology.synthesis?.let { synthesis ->
            if (synthesis.dominantNumbers.isNotEmpty()) {
                add(
                    AIExplainSectionData(
                        title = context.getString(R.string.charts_numerology_ai_title_dominant_numbers),
                        highlights = synthesis.dominantNumbers.take(4).map {
                            context.getString(R.string.charts_numerology_dominant_highlight_format, it.label, it.number, it.meaning)
                        },
                    ),
                )
            }
            if (synthesis.strengths.isNotEmpty()) {
                add(
                    AIExplainSectionData(
                        title = context.getString(R.string.charts_numerology_ai_title_strengths),
                        highlights = synthesis.strengths.take(4),
                    ),
                )
            }
            if (synthesis.growthEdges.isNotEmpty()) {
                add(
                    AIExplainSectionData(
                        title = context.getString(R.string.charts_numerology_ai_title_growth_edges),
                        highlights = synthesis.growthEdges.take(4),
                    ),
                )
            }
        }
    }

    return AIExplainRequestData(
        scope = "numerology",
        headline = context.getString(
            R.string.charts_numerology_headline,
            profile.displayName(false, PrivacyDisplayRole.ACTIVE_USER),
            numerology.lifePath.number,
        ),
        theme = numerology.synthesis?.currentFocus ?: numerology.lifePath.meaning,
        sections = sections,
        numerologySummary = numerology.synthesis?.summary,
        simpleLanguage = true,
    )
}

internal fun buildNumerologyFallbackSummary(
    context: Context,
    profile: AppProfile,
    numerology: NumerologyData,
): String {
    val strengths = numerology.synthesis?.strengths?.take(3).orEmpty()
    val growthEdges = numerology.synthesis?.growthEdges?.take(2).orEmpty()
    val focusAreas = numerology.personalYear.focusAreas.take(3)
    return buildString {
        appendLine(context.getString(R.string.charts_numerology_fallback_tldr))
        appendLine()
        appendLine(
            context.getString(
                R.string.charts_numerology_fallback_story,
                profile.displayName(false, PrivacyDisplayRole.ACTIVE_USER),
                numerology.lifePath.number,
                numerology.personalYear.interpretation.lowercase(),
                numerology.personalYear.cycleNumber,
            ),
        )
        appendLine()
        appendLine("---")
        appendLine()
        appendLine(context.getString(R.string.charts_numerology_fallback_core_thread))
        appendLine(context.getString(R.string.charts_numerology_fallback_life_path_line, numerology.lifePath.number, numerology.lifePath.meaning))
        appendLine(context.getString(R.string.charts_numerology_fallback_destiny_line, numerology.destinyNumber, numerology.destinyInterpretation))
        numerology.numerologyInsights["soul_urge"]?.takeIf { it.isNotBlank() }?.let {
            appendLine("- ${context.getString(R.string.charts_numerology_ai_soul_urge_highlight, it)}")
        }
        numerology.numerologyInsights["personality"]?.takeIf { it.isNotBlank() }?.let {
            appendLine("- ${context.getString(R.string.charts_numerology_ai_personality_highlight, it)}")
        }
        if (focusAreas.isNotEmpty()) {
            appendLine()
            appendLine(context.getString(R.string.charts_numerology_fallback_current_focus))
            focusAreas.forEach { focusArea -> appendLine("- $focusArea") }
        }
        if (strengths.isNotEmpty()) {
            appendLine()
            appendLine(context.getString(R.string.charts_numerology_fallback_strengths))
            strengths.forEach { strength -> appendLine("- $strength") }
        }
        if (growthEdges.isNotEmpty()) {
            appendLine()
            appendLine(context.getString(R.string.charts_numerology_fallback_growth_edge))
            growthEdges.forEach { edge -> appendLine("- $edge") }
        }
        appendLine()
        appendLine(context.getString(R.string.charts_numerology_fallback_practical_next_step_heading))
        append(context.getString(R.string.charts_numerology_fallback_practical_next_step_body))
    }.trim()
}

internal fun formatChartCacheTimestamp(epochMillis: Long): String =
    DateTimeFormatter.ofPattern("MMM d, h:mm a", Locale.getDefault())
        .withZone(ZoneId.systemDefault())
        .format(Instant.ofEpochMilli(epochMillis))
