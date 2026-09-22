package com.astromeric.android.feature.charts

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
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
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.CompositeChartData
import com.astromeric.android.core.model.SynastryChartData
import com.astromeric.android.core.model.DataQuality
import androidx.compose.material3.OutlinedTextField
import com.astromeric.android.core.model.DeclinationsData
import com.astromeric.android.core.model.FixedStarConjunction
import com.astromeric.android.core.model.FixedStarPlanetInput
import com.astromeric.android.core.model.ProfectionsData
import com.astromeric.android.core.ui.DataQualityBanner
import com.astromeric.android.core.ui.PremiumLoadingCard
import java.time.LocalDate
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.time.format.FormatStyle
import java.time.temporal.ChronoUnit

// ---------------------------------------------------------------------------
// Advanced charts: solar arc, lunar return, relocation, profections,
// declinations, fixed stars. All reuse the shared helpers defined in
// ChartsScreen.kt (StudioSectionCard, StatusCard, PlanetPlacementRow, AspectRow).
// ---------------------------------------------------------------------------

/** Shared loader/renderer for advanced charts that return a natal-style ChartData. */
@Composable
private fun AdvancedNatalStyleScreen(
    title: String,
    sectionTitle: String,
    sectionSubtitle: String,
    loadingLabel: String,
    selectedProfile: AppProfile?,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
    aspectsSubtitle: String = stringResource(R.string.charts_adv_aspects_subtitle),
    summary: @Composable (ChartData) -> String? = { null },
    fetch: suspend (AppProfile) -> Result<ChartData>,
) {
    val context = LocalContext.current
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var chart by remember(selectedProfile?.id) { mutableStateOf<ChartData?>(null) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile
        if (profile?.canRequestNatalChart != true) {
            chart = null
            errorMessage = null
            isLoading = false
            return@LaunchedEffect
        }
        isLoading = true
        errorMessage = null
        fetch(profile)
            .onSuccess { chart = it }
            .onFailure {
                chart = null
                errorMessage = it.message ?: context.getString(R.string.charts_adv_load_error)
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
        Text(text = title, style = MaterialTheme.typography.headlineMedium)
        if (selectedProfile != null && selectedProfile.dataQuality != DataQuality.FULL) {
            DataQualityBanner(quality = selectedProfile.dataQuality)
        }

        StudioSectionCard(title = sectionTitle, subtitle = sectionSubtitle) {
            TextButton(onClick = onBackToCharts) { Text(stringResource(R.string.charts_action_back_to_studio)) }
            when {
                selectedProfile == null -> Text(
                    text = stringResource(R.string.charts_adv_select_profile),
                    style = MaterialTheme.typography.bodyMedium,
                )

                !selectedProfile.canRequestNatalChart -> Text(
                    text = stringResource(R.string.charts_adv_require_location_timezone),
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> Button(onClick = { refreshVersion += 1 }, enabled = !isLoading) {
                    Text(
                        if (isLoading) {
                            stringResource(R.string.status_refreshing)
                        } else {
                            stringResource(R.string.charts_action_refresh_chart)
                        },
                    )
                }
            }
        }

        when {
            isLoading -> PremiumLoadingCard(title = loadingLabel)
            errorMessage != null -> StatusCard(message = errorMessage.orEmpty(), isError = true)
            chart?.metadata?.isApproximated == true -> StatusCard(
                message = approximatedChartMessage(chart?.metadata?.note),
                isError = true,
            )
            chart != null -> {
                val loaded = chart!!
                summary(loaded)?.let { StatusCard(message = it, isError = false) }
                if (loaded.planets.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_adv_planets_title),
                        subtitle = stringResource(R.string.charts_adv_planets_subtitle),
                    ) {
                        loaded.planets.take(12).forEach { PlanetPlacementRow(placement = it) }
                    }
                }
                if (loaded.aspects.isNotEmpty()) {
                    StudioSectionCard(title = stringResource(R.string.charts_adv_aspects_title), subtitle = aspectsSubtitle) {
                        loaded.aspects.take(10).forEach { AspectRow(aspect = it) }
                    }
                }
            }
        }
    }
}

/**
 * The backend substitutes approximated positions (provider "stub" / "polar-fallback")
 * when it can't calculate a real chart, e.g. houses near the poles. Never render those
 * as real placements.
 */
@Composable
private fun approximatedChartMessage(note: String?): String =
    note?.takeIf { it.isNotBlank() }
        ?.let { stringResource(R.string.charts_adv_approximated_with_note, it) }
        ?: stringResource(R.string.charts_adv_approximated)

private fun formatReturnMoment(iso: String?): String? {
    if (iso.isNullOrBlank()) return null
    return runCatching {
        OffsetDateTime.parse(iso)
            .format(DateTimeFormatter.ofLocalizedDateTime(FormatStyle.MEDIUM, FormatStyle.SHORT))
    }.getOrDefault(iso)
}

/** Error card with a Retry action that re-runs the screen's load. */
@Composable
private fun RetryableErrorCard(message: String, onRetry: () -> Unit) {
    StatusCard(
        message = message,
        isError = true,
        actionLabel = stringResource(R.string.action_retry),
        onAction = onRetry,
    )
}

@Composable
fun SolarArcChartScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    AdvancedNatalStyleScreen(
        title = stringResource(R.string.charts_solar_arc_title),
        sectionTitle = stringResource(R.string.charts_solar_arc_section_title),
        sectionSubtitle = stringResource(R.string.charts_solar_arc_section_subtitle),
        loadingLabel = stringResource(R.string.charts_solar_arc_loading),
        selectedProfile = selectedProfile,
        onBackToCharts = onBackToCharts,
        modifier = modifier,
        aspectsSubtitle = stringResource(R.string.charts_solar_arc_aspects_subtitle),
        summary = { chart ->
            val arc = chart.metadata?.solarArcDegrees
            val asOf = chart.metadata?.directedTo
            when {
                arc == null -> null
                asOf != null -> stringResource(R.string.charts_solar_arc_summary_as_of, arc, asOf)
                else -> stringResource(R.string.charts_solar_arc_summary, arc)
            }
        },
    ) { profile -> remoteDataSource.fetchSolarArcChart(profile = profile, targetDate = LocalDate.now().toString()) }
}

@Composable
fun LunarReturnChartScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    AdvancedNatalStyleScreen(
        title = stringResource(R.string.charts_lunar_return_title),
        sectionTitle = stringResource(R.string.charts_lunar_return_section_title),
        sectionSubtitle = stringResource(R.string.charts_lunar_return_section_subtitle),
        loadingLabel = stringResource(R.string.charts_lunar_return_loading),
        selectedProfile = selectedProfile,
        onBackToCharts = onBackToCharts,
        modifier = modifier,
        summary = { chart ->
            formatReturnMoment(chart.metadata?.returnDatetimeLocal)
                ?.let { stringResource(R.string.charts_lunar_return_summary, it) }
        },
    ) { profile ->
        // Send the current instant with its offset (not just the local date, which the
        // backend reads as 00:00 UTC) so "next" really means after now.
        remoteDataSource.fetchLunarReturnChart(
            profile = profile,
            targetDate = OffsetDateTime.now().truncatedTo(ChronoUnit.SECONDS).toString(),
        )
    }
}

@Composable
fun ProfectionsScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var data by remember(selectedProfile?.id) { mutableStateOf<ProfectionsData?>(null) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile ?: return@LaunchedEffect
        isLoading = true
        errorMessage = null
        // Pass the device date: the backend would otherwise use its own (UTC) date,
        // which is a different day for much of the world near a birthday.
        remoteDataSource.fetchProfections(profile = profile, refDate = LocalDate.now().toString())
            .onSuccess { data = it }
            .onFailure {
                data = null
                errorMessage = it.message ?: context.getString(R.string.charts_profections_load_error)
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
        Text(text = stringResource(R.string.charts_profections_title), style = MaterialTheme.typography.headlineMedium)
        TextButton(onClick = onBackToCharts) { Text(stringResource(R.string.charts_action_back_to_studio)) }
        when {
            selectedProfile == null -> StatusCard(message = stringResource(R.string.charts_adv_select_profile_first), isError = false)
            isLoading -> PremiumLoadingCard(title = stringResource(R.string.charts_profections_loading))
            errorMessage != null -> RetryableErrorCard(message = errorMessage.orEmpty(), onRetry = { refreshVersion += 1 })
            data != null -> {
                val d = data!!
                val annualLord = d.annualLord?.takeIf { it.isNotBlank() }
                val monthlyLord = d.monthlyLord?.takeIf { it.isNotBlank() }
                StudioSectionCard(
                    title = d.annualSign
                        ?.let { stringResource(R.string.charts_profections_year_title_with_sign, d.age + 1, d.annualHouse, it) }
                        ?: stringResource(R.string.charts_profections_year_title, d.age + 1, d.annualHouse),
                    subtitle = annualLord?.let { stringResource(R.string.charts_profections_time_lord, it) }
                        ?: stringResource(R.string.charts_profections_time_lord_missing),
                ) {
                    Text(stringResource(R.string.charts_profections_focus, d.annualFocus), style = MaterialTheme.typography.bodyMedium)
                    if (d.annualLordThemes.isNotBlank()) {
                        Text(stringResource(R.string.charts_profections_themes, d.annualLordThemes), style = MaterialTheme.typography.bodyMedium)
                    }
                }
                StudioSectionCard(
                    title = d.monthlySign
                        ?.let { stringResource(R.string.charts_profections_month_title_with_sign, d.monthlyHouse, it) }
                        ?: stringResource(R.string.charts_profections_month_title, d.monthlyHouse),
                    subtitle = monthlyLord
                        ?.let { stringResource(R.string.charts_profections_month_subtitle_with_lord, d.monthsIntoYear, it) }
                        ?: stringResource(R.string.charts_profections_month_subtitle, d.monthsIntoYear),
                ) {
                    Text(stringResource(R.string.charts_profections_focus, d.monthlyFocus), style = MaterialTheme.typography.bodyMedium)
                }
                if (d.interpretation.isNotBlank()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_profections_interpretation_title),
                        subtitle = stringResource(R.string.charts_profections_interpretation_subtitle),
                    ) {
                        Text(d.interpretation, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
    }
}

@Composable
fun DeclinationsScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var data by remember(selectedProfile?.id) { mutableStateOf<DeclinationsData?>(null) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile
        if (profile?.canRequestNatalChart != true) {
            data = null
            errorMessage = null
            isLoading = false
            return@LaunchedEffect
        }
        isLoading = true
        errorMessage = null
        remoteDataSource.fetchDeclinations(profile = profile)
            .onSuccess { data = it }
            .onFailure {
                data = null
                errorMessage = it.message ?: context.getString(R.string.charts_declinations_load_error)
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
        Text(text = stringResource(R.string.charts_declinations_title), style = MaterialTheme.typography.headlineMedium)
        TextButton(onClick = onBackToCharts) { Text(stringResource(R.string.charts_action_back_to_studio)) }
        when {
            selectedProfile == null -> StatusCard(message = stringResource(R.string.charts_adv_select_profile_first), isError = false)
            isLoading -> PremiumLoadingCard(title = stringResource(R.string.charts_declinations_loading))
            errorMessage != null -> RetryableErrorCard(message = errorMessage.orEmpty(), onRetry = { refreshVersion += 1 })
            data != null -> {
                val d = data!!
                if (d.declinations.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_declinations_section_title),
                        subtitle = stringResource(R.string.charts_declinations_section_subtitle),
                    ) {
                        d.declinations.forEach { entry ->
                            Text(
                                text = stringResource(
                                    if (entry.outOfBounds) R.string.charts_declinations_row_out_of_bounds else R.string.charts_declinations_row,
                                    entry.name,
                                    entry.declination,
                                ),
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }
                }
                if (d.parallels.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_declinations_parallels_title),
                        subtitle = stringResource(R.string.charts_declinations_parallels_subtitle),
                    ) {
                        d.parallels.forEach { p ->
                            Text(
                                text = stringResource(
                                    R.string.charts_declinations_parallel_row,
                                    p.planetA,
                                    p.type.replace('_', ' '),
                                    p.planetB,
                                    p.orb,
                                ),
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }
                } else if (d.note != null) {
                    StatusCard(message = d.note.orEmpty(), isError = false)
                }
            }
        }
    }
}

@Composable
fun FixedStarsScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var conjunctions by remember(selectedProfile?.id) { mutableStateOf<List<FixedStarConjunction>?>(null) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile
        if (profile?.canRequestNatalChart != true) {
            conjunctions = null
            errorMessage = null
            isLoading = false
            return@LaunchedEffect
        }
        isLoading = true
        errorMessage = null
        // Fixed-star conjunctions are computed from the natal planet longitudes.
        remoteDataSource.fetchNatalChart(profile)
            .mapCatching { chart ->
                val inputs = chart.planets.mapNotNull { p ->
                    p.absoluteDegree?.let { FixedStarPlanetInput(name = p.name, absoluteDegree = it) }
                }
                remoteDataSource.fetchFixedStars(planets = inputs).getOrThrow()
            }
            .onSuccess { conjunctions = it }
            .onFailure {
                conjunctions = null
                errorMessage = it.message ?: context.getString(R.string.charts_fixed_stars_load_error)
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
        Text(text = stringResource(R.string.charts_fixed_stars_title), style = MaterialTheme.typography.headlineMedium)
        TextButton(onClick = onBackToCharts) { Text(stringResource(R.string.charts_action_back_to_studio)) }
        when {
            selectedProfile == null -> StatusCard(message = stringResource(R.string.charts_adv_select_profile_first), isError = false)
            isLoading -> PremiumLoadingCard(title = stringResource(R.string.charts_fixed_stars_loading))
            errorMessage != null -> RetryableErrorCard(message = errorMessage.orEmpty(), onRetry = { refreshVersion += 1 })
            conjunctions != null -> {
                val list = conjunctions.orEmpty()
                if (list.isEmpty()) {
                    StatusCard(message = stringResource(R.string.charts_fixed_stars_empty), isError = false)
                } else {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_fixed_stars_section_title),
                        subtitle = stringResource(R.string.charts_fixed_stars_section_subtitle),
                    ) {
                        list.forEach { c ->
                            Text(
                                text = stringResource(R.string.charts_fixed_stars_row, c.planet, c.star, c.nature, c.orb),
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun RelocationChartScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var latText by rememberSaveable(selectedProfile?.id) { mutableStateOf("") }
    var lonText by rememberSaveable(selectedProfile?.id) { mutableStateOf("") }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var chart by remember(selectedProfile?.id) { mutableStateOf<ChartData?>(null) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var submitVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }

    LaunchedEffect(submitVersion) {
        if (submitVersion == 0) return@LaunchedEffect
        val profile = selectedProfile ?: return@LaunchedEffect
        val coordinates = parseRelocationCoordinates(latText, lonText)
        if (coordinates == null) {
            chart = null
            errorMessage = context.getString(R.string.charts_relocation_invalid_coordinates)
            return@LaunchedEffect
        }
        isLoading = true
        errorMessage = null
        remoteDataSource.fetchRelocationChart(
            profile = profile,
            newLatitude = coordinates.first,
            newLongitude = coordinates.second,
        )
            .onSuccess { chart = it }
            .onFailure {
                chart = null
                errorMessage = it.message ?: context.getString(R.string.charts_relocation_load_error)
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
        Text(text = stringResource(R.string.charts_relocation_title), style = MaterialTheme.typography.headlineMedium)
        StudioSectionCard(
            title = stringResource(R.string.charts_relocation_section_title),
            subtitle = stringResource(R.string.charts_relocation_section_subtitle),
        ) {
            TextButton(onClick = onBackToCharts) { Text(stringResource(R.string.charts_action_back_to_studio)) }
            OutlinedTextField(
                value = latText,
                onValueChange = { latText = it },
                label = { Text(stringResource(R.string.charts_relocation_latitude_label)) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = lonText,
                onValueChange = { lonText = it },
                label = { Text(stringResource(R.string.charts_relocation_longitude_label)) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            Button(
                onClick = { submitVersion += 1 },
                enabled = !isLoading && selectedProfile != null,
            ) {
                Text(
                    if (isLoading) {
                        stringResource(R.string.charts_relocation_calculating)
                    } else {
                        stringResource(R.string.charts_relocation_action_calculate)
                    },
                )
            }
        }
        when {
            isLoading -> PremiumLoadingCard(title = stringResource(R.string.charts_relocation_loading))
            errorMessage != null -> StatusCard(message = errorMessage.orEmpty(), isError = true)
            chart?.metadata?.isApproximated == true -> StatusCard(
                message = approximatedChartMessage(chart?.metadata?.note),
                isError = true,
            )
            chart != null -> {
                val loaded = chart!!
                // Planets and planet-to-planet aspects are identical to the natal chart;
                // what relocation changes is the houses and the angles (ASC/MC).
                if (loaded.houses.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_relocation_houses_title),
                        subtitle = stringResource(R.string.charts_relocation_houses_subtitle),
                    ) {
                        loaded.houses.forEach { HousePlacementRow(house = it) }
                    }
                }
                if (loaded.planets.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_adv_planets_title),
                        subtitle = stringResource(R.string.charts_relocation_planets_subtitle),
                    ) {
                        loaded.planets.take(12).forEach { PlanetPlacementRow(placement = it) }
                    }
                }
                val angleAspects = loaded.aspects
                    .filter { it.planetB in RelocationAngles || it.planetA in RelocationAngles }
                    .sortedBy { it.orb ?: Double.MAX_VALUE }
                if (angleAspects.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_relocation_angle_aspects_title),
                        subtitle = stringResource(R.string.charts_relocation_angle_aspects_subtitle),
                    ) {
                        angleAspects.take(10).forEach { AspectRow(aspect = it) }
                    }
                }
            }
        }
    }
}

private val RelocationAngles = setOf("Ascendant", "Midheaven")

/** Accepts "40.71" and the comma-decimal "40,71" many locales' keypads produce. */
internal fun parseCoordinate(text: String): Double? =
    text.trim().replace(',', '.').toDoubleOrNull()?.takeIf { it.isFinite() }

/** Parsed (latitude, longitude), or null unless both parse and are within ±90 / ±180. */
internal fun parseRelocationCoordinates(latText: String, lonText: String): Pair<Double, Double>? {
    val lat = parseCoordinate(latText) ?: return null
    val lon = parseCoordinate(lonText) ?: return null
    if (lat !in -90.0..90.0 || lon !in -180.0..180.0) return null
    return lat to lon
}

@Composable
fun ProgressionsScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var chart by remember(selectedProfile?.id) { mutableStateOf<ChartData?>(null) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile
        if (profile?.canRequestNatalChart != true) {
            chart = null
            errorMessage = null
            isLoading = false
            return@LaunchedEffect
        }

        isLoading = true
        errorMessage = null
        remoteDataSource.fetchProgressedChart(profile = profile, targetDate = LocalDate.now().toString())
            .onSuccess { chart = it }
            .onFailure {
                chart = null
                errorMessage = it.message ?: context.getString(R.string.charts_progressed_load_error)
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
        Text(
            text = stringResource(R.string.charts_progressions_card_title),
            style = MaterialTheme.typography.headlineMedium,
        )
        if (selectedProfile != null && selectedProfile.dataQuality != DataQuality.FULL) {
            DataQualityBanner(quality = selectedProfile.dataQuality)
        }

        StudioSectionCard(
            title = stringResource(R.string.charts_secondary_progressions_title),
            subtitle = stringResource(R.string.charts_secondary_progressions_subtitle),
        ) {
            TextButton(onClick = onBackToCharts) {
                Text(stringResource(R.string.charts_action_back_to_studio))
            }
            when {
                selectedProfile == null -> Text(
                    text = stringResource(R.string.charts_progressions_profile_required),
                    style = MaterialTheme.typography.bodyMedium,
                )

                !selectedProfile.canRequestNatalChart -> Text(
                    text = stringResource(R.string.charts_progressions_require_location_timezone),
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    Text(
                        text = stringResource(
                            R.string.charts_reading_for_quality_format,
                            selectedProfile.name,
                            selectedProfile.dataQuality.label,
                        ),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Button(
                        onClick = { refreshVersion += 1 },
                        enabled = !isLoading,
                    ) {
                        Text(
                            if (isLoading) {
                                stringResource(R.string.status_refreshing)
                            } else {
                                stringResource(R.string.charts_action_refresh_progressions)
                            },
                        )
                    }
                }
            }
        }

        when {
            isLoading -> PremiumLoadingCard(title = stringResource(R.string.charts_loading_progressed_chart))

            errorMessage != null -> StatusCard(message = errorMessage.orEmpty(), isError = true)

            chart != null -> {
                chart?.metadata?.let { metadata ->
                    StudioSectionCard(
                        title = stringResource(R.string.charts_chart_context_title),
                        subtitle = stringResource(R.string.charts_chart_context_subtitle),
                    ) {
                        Text(
                            text = stringResource(
                                R.string.charts_natal_date_format,
                                metadata.dateOfBirth ?: selectedProfile?.dateOfBirth ?: stringResource(R.string.charts_unknown),
                            ),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = stringResource(
                                R.string.charts_birth_time_anchor_format,
                                metadata.timeOfBirth ?: selectedProfile?.timeOfBirth ?: stringResource(R.string.charts_unknown),
                            ),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = stringResource(
                                R.string.charts_timezone_format,
                                metadata.timezone ?: selectedProfile?.timezone ?: stringResource(R.string.charts_unknown),
                            ),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }

                if (!chart?.planets.isNullOrEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_progressed_planets_title),
                        subtitle = stringResource(R.string.charts_progressed_planets_subtitle),
                    ) {
                        chart?.planets?.take(10)?.forEach { placement ->
                            PlanetPlacementRow(placement = placement)
                        }
                    }
                }

                if (!chart?.aspects.isNullOrEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_progressed_aspects_title),
                        subtitle = stringResource(R.string.charts_progressed_aspects_subtitle),
                    ) {
                        chart?.aspects?.take(8)?.forEach { aspect ->
                            AspectRow(aspect = aspect)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun SynastryChartScreen(
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val partnerProfiles = remember(profiles, selectedProfile?.id) {
        profiles.filter { it.id != selectedProfile?.id }
    }
    var selectedPartnerId by remember(selectedProfile?.id, partnerProfiles.map { it.id }) {
        mutableStateOf(partnerProfiles.firstOrNull()?.id)
    }
    var refreshVersion by remember(selectedProfile?.id, selectedPartnerId) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id, selectedPartnerId) { mutableStateOf(false) }
    var result by remember(selectedProfile?.id, selectedPartnerId) { mutableStateOf<SynastryChartData?>(null) }
    var errorMessage by remember(selectedProfile?.id, selectedPartnerId) { mutableStateOf<String?>(null) }
    val selectedPartner = partnerProfiles.firstOrNull { it.id == selectedPartnerId }

    LaunchedEffect(selectedProfile?.id, partnerProfiles.map { it.id }) {
        if (selectedPartnerId == null || partnerProfiles.none { it.id == selectedPartnerId }) {
            selectedPartnerId = partnerProfiles.firstOrNull()?.id
        }
    }

    LaunchedEffect(selectedProfile?.id, selectedPartnerId, refreshVersion) {
        val profile = selectedProfile
        val partner = selectedPartner
        if (profile?.canRequestNatalChart != true || partner?.canRequestNatalChart != true) {
            result = null
            errorMessage = null
            isLoading = false
            return@LaunchedEffect
        }

        isLoading = true
        errorMessage = null
        remoteDataSource.fetchSynastryChart(profile, partner)
            .onSuccess { result = it }
            .onFailure {
                result = null
                errorMessage = it.message ?: context.getString(R.string.charts_synastry_load_error)
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
        Text(
            text = stringResource(R.string.charts_synastry_card_title),
            style = MaterialTheme.typography.headlineMedium,
        )
        if (selectedProfile != null && selectedProfile.dataQuality != DataQuality.FULL) {
            DataQualityBanner(quality = selectedProfile.dataQuality)
        }

        StudioSectionCard(
            title = stringResource(R.string.charts_synastry_insight_title),
            subtitle = stringResource(R.string.charts_synastry_insight_subtitle),
        ) {
            TextButton(onClick = onBackToCharts) {
                Text(stringResource(R.string.charts_action_back_to_studio))
            }
            when {
                selectedProfile == null -> Text(
                    text = stringResource(R.string.charts_synastry_profile_required),
                    style = MaterialTheme.typography.bodyMedium,
                )

                partnerProfiles.isEmpty() -> Text(
                    text = stringResource(R.string.charts_synastry_no_partner_profiles),
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    Text(
                        text = stringResource(R.string.charts_choose_comparison_profile),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Row(
                        modifier = Modifier.horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        partnerProfiles.forEach { partner ->
                            FilterChip(
                                selected = selectedPartnerId == partner.id,
                                onClick = { selectedPartnerId = partner.id },
                                label = { Text(partner.name) },
                            )
                        }
                    }
                    Button(
                        onClick = { refreshVersion += 1 },
                        enabled = selectedProfile.canRequestNatalChart && selectedPartner?.canRequestNatalChart == true && !isLoading,
                    ) {
                        Text(
                            if (isLoading) {
                                stringResource(R.string.status_refreshing)
                            } else {
                                stringResource(R.string.charts_action_refresh_synastry)
                            },
                        )
                    }
                    if (selectedPartner?.canRequestNatalChart != true) {
                        Text(
                            text = stringResource(R.string.charts_synastry_require_both_profiles_chart_ready),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
        }

        when {
            isLoading -> PremiumLoadingCard(title = stringResource(R.string.charts_loading_compare_charts))

            errorMessage != null -> StatusCard(message = errorMessage.orEmpty(), isError = true)

            result != null -> {
                StudioSectionCard(
                    title = stringResource(R.string.charts_compatibility_snapshot_title),
                    subtitle = stringResource(R.string.charts_compatibility_snapshot_subtitle),
                ) {
                    Text(
                        text = stringResource(
                            R.string.charts_people_and_format,
                            result?.personA?.name.orEmpty(),
                            result?.personB?.name.orEmpty(),
                        ),
                        style = MaterialTheme.typography.titleMedium,
                    )
                    result?.compatibility?.strengths?.take(3)?.forEach { strength ->
                        Text(
                            text = stringResource(R.string.charts_relationship_strength_format, strength),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                    result?.compatibility?.challenges?.take(3)?.forEach { challenge ->
                        Text(
                            text = stringResource(R.string.charts_relationship_challenge_format, challenge),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                    result?.compatibility?.advice?.take(3)?.forEach { advice ->
                        Text(
                            text = stringResource(R.string.charts_relationship_advice_format, advice),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                }

                if (!result?.synastryAspects.isNullOrEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_key_synastry_aspects_title),
                        subtitle = stringResource(R.string.charts_key_synastry_aspects_subtitle),
                    ) {
                        result?.synastryAspects?.take(10)?.forEach { aspect ->
                            SynastryAspectRow(aspect = aspect)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun CompositeChartScreen(
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val partnerProfiles = remember(profiles, selectedProfile?.id) {
        profiles.filter { it.id != selectedProfile?.id }
    }
    var selectedPartnerId by remember(selectedProfile?.id, partnerProfiles.map { it.id }) {
        mutableStateOf(partnerProfiles.firstOrNull()?.id)
    }
    var refreshVersion by remember(selectedProfile?.id, selectedPartnerId) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id, selectedPartnerId) { mutableStateOf(false) }
    var result by remember(selectedProfile?.id, selectedPartnerId) { mutableStateOf<CompositeChartData?>(null) }
    var errorMessage by remember(selectedProfile?.id, selectedPartnerId) { mutableStateOf<String?>(null) }
    val selectedPartner = partnerProfiles.firstOrNull { it.id == selectedPartnerId }

    LaunchedEffect(selectedProfile?.id, partnerProfiles.map { it.id }) {
        if (selectedPartnerId == null || partnerProfiles.none { it.id == selectedPartnerId }) {
            selectedPartnerId = partnerProfiles.firstOrNull()?.id
        }
    }

    LaunchedEffect(selectedProfile?.id, selectedPartnerId, refreshVersion) {
        val profile = selectedProfile
        val partner = selectedPartner
        if (profile?.canRequestNatalChart != true || partner?.canRequestNatalChart != true) {
            result = null
            errorMessage = null
            isLoading = false
            return@LaunchedEffect
        }

        isLoading = true
        errorMessage = null
        remoteDataSource.fetchCompositeChart(profile, partner)
            .onSuccess { result = it }
            .onFailure {
                result = null
                errorMessage = it.message ?: context.getString(R.string.charts_composite_load_error)
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
        Text(
            text = stringResource(R.string.charts_composite_card_title),
            style = MaterialTheme.typography.headlineMedium,
        )
        if (selectedProfile != null && selectedProfile.dataQuality != DataQuality.FULL) {
            DataQualityBanner(quality = selectedProfile.dataQuality)
        }

        StudioSectionCard(
            title = stringResource(R.string.charts_relationship_itself_title),
            subtitle = stringResource(R.string.charts_relationship_itself_subtitle),
        ) {
            TextButton(onClick = onBackToCharts) {
                Text(stringResource(R.string.charts_action_back_to_studio))
            }
            when {
                selectedProfile == null -> Text(
                    text = stringResource(R.string.charts_composite_profile_required),
                    style = MaterialTheme.typography.bodyMedium,
                )

                partnerProfiles.isEmpty() -> Text(
                    text = stringResource(R.string.charts_composite_need_partner),
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    Text(
                        text = stringResource(R.string.charts_choose_comparison_profile),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Row(
                        modifier = Modifier.horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        partnerProfiles.forEach { partner ->
                            FilterChip(
                                selected = selectedPartnerId == partner.id,
                                onClick = { selectedPartnerId = partner.id },
                                label = { Text(partner.name) },
                            )
                        }
                    }
                    Button(
                        onClick = { refreshVersion += 1 },
                        enabled = selectedProfile.canRequestNatalChart && selectedPartner?.canRequestNatalChart == true && !isLoading,
                    ) {
                        Text(
                            if (isLoading) {
                                stringResource(R.string.status_refreshing)
                            } else {
                                stringResource(R.string.charts_action_refresh_composite)
                            },
                        )
                    }
                    if (selectedPartner?.canRequestNatalChart != true) {
                        Text(
                            text = stringResource(R.string.charts_composite_require_both_profiles_chart_ready),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
        }

        when {
            isLoading -> PremiumLoadingCard(title = stringResource(R.string.charts_loading_composite_chart))

            errorMessage != null -> StatusCard(message = errorMessage.orEmpty(), isError = true)

            result != null -> {
                StudioSectionCard(
                    title = stringResource(R.string.charts_composite_frame_title),
                    subtitle = stringResource(R.string.charts_composite_frame_subtitle),
                ) {
                    Text(
                        text = stringResource(
                            R.string.charts_people_plus_format,
                            result?.metadata?.personA.orEmpty(),
                            result?.metadata?.personB.orEmpty(),
                        ),
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = stringResource(R.string.charts_method_format, result?.metadata?.method.orEmpty()),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                if (!result?.planets.isNullOrEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_composite_planets_title),
                        subtitle = stringResource(R.string.charts_composite_planets_subtitle),
                    ) {
                        result?.planets?.take(10)?.forEach { planet ->
                            CompositePlanetRow(planet = planet)
                        }
                    }
                }
            }
        }
    }
}