package com.astromeric.android.feature.charts

import android.content.Context
import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
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
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.maskedBirthplace
import com.astromeric.android.core.model.maskedBirthTime
import com.astromeric.android.core.model.maskedDateOfBirth
import com.astromeric.android.core.ui.ChartShareCard
import com.astromeric.android.core.ui.renderComposableToBitmap
import com.astromeric.android.core.ui.shareBitmapCard
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

private data class PendingBirthChartExport(
    val fileName: String,
    val content: String,
)

@Composable
fun BirthChartDetailScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onBackToCharts: () -> Unit,
    onShowMessage: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val chartCacheStore = remember(context) { NatalChartCacheStore(context.applicationContext) }
    val localEphemerisEngine = remember(context) { LocalSwissEphemerisEngine.getInstance(context.applicationContext) }
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var natalChart by remember(selectedProfile?.id) { mutableStateOf<ChartData?>(null) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var chartSource by remember(selectedProfile?.id) { mutableStateOf<AstroDataSource?>(null) }
    var cachedChartActive by remember(selectedProfile?.id) { mutableStateOf(false) }
    var cachedAtEpochMillis by remember(selectedProfile?.id) { mutableStateOf<Long?>(null) }
    var pendingExport by remember { mutableStateOf<PendingBirthChartExport?>(null) }

    val exportLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("text/plain")) { uri ->
        val export = pendingExport
        pendingExport = null
        if (uri == null || export == null) {
            return@rememberLauncherForActivityResult
        }

        scope.launch {
            val result = withContext(Dispatchers.IO) {
                runCatching {
                    context.contentResolver.openOutputStream(uri)?.use { output ->
                        output.write(export.content.toByteArray(Charsets.UTF_8))
                    } ?: error("Could not open the export target.")
                }
            }
            onShowMessage(
                if (result.isSuccess) {
                    context.getString(R.string.charts_export_success)
                } else {
                    result.exceptionOrNull()?.message ?: context.getString(R.string.charts_export_failed)
                },
            )
        }
    }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile
        if (profile?.canRequestNatalChart != true) {
            natalChart = null
            errorMessage = null
            chartSource = null
            cachedChartActive = false
            cachedAtEpochMillis = null
            isLoading = false
            return@LaunchedEffect
        }

        isLoading = true
        errorMessage = null
        chartSource = null
        cachedChartActive = false
        cachedAtEpochMillis = null

        val result = loadNatalChartWithCacheFallback(
            profile = profile,
            remoteDataSource = remoteDataSource,
            chartCacheStore = chartCacheStore,
            localEphemerisEngine = localEphemerisEngine,
        )
        natalChart = result.chart
        chartSource = result.source
        cachedChartActive = result.isCached
        cachedAtEpochMillis = result.cachedAtEpochMillis
        errorMessage = if (result.chart == null) {
            result.errorMessage ?: context.getString(R.string.charts_birth_load_error)
        } else {
            null
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
            text = stringResource(R.string.charts_birth_title),
            style = MaterialTheme.typography.headlineMedium,
        )

        StudioSectionCard(
            title = stringResource(R.string.charts_birth_full_detail_title),
            subtitle = stringResource(R.string.charts_birth_full_detail_subtitle),
        ) {
            TextButton(onClick = onBackToCharts) {
                Text(stringResource(R.string.charts_action_back_to_studio))
            }
            when {
                selectedProfile == null -> Text(
                    text = stringResource(R.string.charts_birth_profile_required),
                    style = MaterialTheme.typography.bodyMedium,
                )

                !selectedProfile.canRequestNatalChart -> Text(
                    text = stringResource(R.string.charts_birth_require_location_timezone),
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    val profile = selectedProfile
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(
                            onClick = { refreshVersion += 1 },
                            enabled = !isLoading,
                        ) {
                            Text(
                                if (isLoading) {
                                    stringResource(R.string.status_refreshing)
                                } else {
                                    stringResource(R.string.charts_action_refresh_chart)
                                },
                            )
                        }
                        OutlinedButton(
                            onClick = {
                                val chart = natalChart
                                if (chart == null) {
                                    onShowMessage(context.getString(R.string.charts_load_birth_chart_first))
                                    return@OutlinedButton
                                }
                                shareChartCard(
                                    context = context,
                                    chart = chart,
                                    profile = profile,
                                    hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                                )
                            },
                            enabled = natalChart != null,
                        ) {
                            Text(stringResource(R.string.charts_action_share_summary))
                        }
                    }
                    OutlinedButton(
                        onClick = {
                            val chart = natalChart
                            if (chart == null) {
                                onShowMessage(context.getString(R.string.charts_load_birth_chart_first))
                                return@OutlinedButton
                            }
                            val export = PendingBirthChartExport(
                                fileName = buildBirthChartExportFileName(profile, hideSensitiveDetailsEnabled),
                                content = buildBirthChartExportSummary(context, profile, chart, hideSensitiveDetailsEnabled, chartSource, cachedChartActive, cachedAtEpochMillis),
                            )
                            pendingExport = export
                            exportLauncher.launch(export.fileName)
                        },
                        enabled = natalChart != null,
                    ) {
                        Text(stringResource(R.string.charts_action_export_summary))
                    }
                }
            }
        }

        if (cachedChartActive && natalChart != null) {
            StudioSectionCard(
                title = stringResource(R.string.charts_offline_snapshot_title),
                subtitle = chartSourceDetail(context, chartSource, cachedChartActive),
            ) {
                cachedAtEpochMillis?.let { cachedAt ->
                    Text(
                        text = stringResource(R.string.charts_cached_at_format, formatChartCacheTimestamp(cachedAt)),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }

        when {
            isLoading && natalChart == null -> Card(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    CircularProgressIndicator()
                    Text(
                        text = stringResource(R.string.charts_loading_birth_chart),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }

            errorMessage != null -> StatusCard(message = errorMessage.orEmpty(), isError = true)

            natalChart != null && selectedProfile != null -> {
                val chart = natalChart ?: return@Column
                BirthChartIdentityCard(
                    profile = selectedProfile,
                    chart = chart,
                    hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                )
                BirthChartBigThreeCard(chart = chart)

                chart.metadata?.let { metadata ->
                    StudioSectionCard(
                        title = stringResource(R.string.charts_calculation_context_title),
                        subtitle = stringResource(R.string.charts_calculation_context_subtitle),
                    ) {
                        metadata.dataQuality?.let { quality ->
                            AssistChip(onClick = {}, label = { Text(quality) })
                        }
                        chartSource?.let { source ->
                            AssistChip(onClick = {}, label = { Text(chartSourceLabel(context, source, cachedChartActive)) })
                        }
                        Text(
                            text = stringResource(
                                R.string.charts_house_system_format,
                                metadata.houseSystem ?: selectedProfile.houseSystem,
                            ),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = stringResource(
                                R.string.charts_timezone_format,
                                metadata.timezone ?: selectedProfile.timezone ?: stringResource(R.string.charts_unknown),
                            ),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        if (metadata.birthTimeAssumed == true) {
                            Text(
                                text = stringResource(
                                    R.string.charts_birth_time_assumed_format,
                                    metadata.assumedTimeOfBirth ?: "12:00",
                                ),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }

                if (chart.planets.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_planet_placements_title),
                        subtitle = stringResource(R.string.charts_planet_placements_subtitle),
                    ) {
                        chart.planets.forEach { placement ->
                            PlanetPlacementRow(placement = placement)
                        }
                    }
                }

                if (chart.aspects.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_key_aspects_title),
                        subtitle = stringResource(R.string.charts_key_aspects_subtitle),
                    ) {
                        chart.aspects.take(10).forEach { aspect ->
                            AspectRow(aspect = aspect)
                        }
                    }
                }

                if (chart.houses.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_houses_title),
                        subtitle = stringResource(R.string.charts_houses_subtitle),
                    ) {
                        chart.houses.forEach { house ->
                            HousePlacementRow(house = house)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun BirthChartIdentityCard(
    profile: AppProfile,
    chart: ChartData,
    hideSensitiveDetailsEnabled: Boolean,
) {
    StudioSectionCard(
        title = profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
        subtitle = stringResource(R.string.charts_birth_identity_subtitle),
    ) {
        Text(
            text = stringResource(R.string.charts_birth_date_format, profile.maskedDateOfBirth(hideSensitiveDetailsEnabled)),
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = stringResource(R.string.charts_birth_time_format, profile.maskedBirthTime(hideSensitiveDetailsEnabled)),
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = stringResource(R.string.charts_birthplace_format, profile.maskedBirthplace(hideSensitiveDetailsEnabled)),
            style = MaterialTheme.typography.bodyMedium,
        )
        Row(
            modifier = Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            listOfNotNull(
                chart.planets.firstOrNull { it.name.equals("Sun", ignoreCase = true) }?.let {
                    stringResource(R.string.charts_chip_sun_format, it.sign)
                },
                chart.planets.firstOrNull { it.name.equals("Moon", ignoreCase = true) }?.let {
                    stringResource(R.string.charts_chip_moon_format, it.sign)
                },
                findAscendantSign(chart)?.let { stringResource(R.string.charts_chip_rising_format, it) },
            ).forEach { chip ->
                AssistChip(onClick = {}, label = { Text(chip) })
            }
        }
    }
}

@Composable
private fun BirthChartBigThreeCard(chart: ChartData) {
    val sun = chart.planets.firstOrNull { it.name.equals("Sun", ignoreCase = true) }
    val moon = chart.planets.firstOrNull { it.name.equals("Moon", ignoreCase = true) }
    val ascendantSign = findAscendantSign(chart)

    StudioSectionCard(
        title = stringResource(R.string.charts_big_three_title),
        subtitle = stringResource(R.string.charts_big_three_subtitle),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            BigThreeMetric(
                label = stringResource(R.string.charts_big_three_sun_label),
                value = sun?.sign ?: stringResource(R.string.charts_unknown),
                modifier = Modifier.weight(1f),
            )
            BigThreeMetric(
                label = stringResource(R.string.charts_big_three_moon_label),
                value = moon?.sign ?: stringResource(R.string.charts_unknown),
                modifier = Modifier.weight(1f),
            )
            BigThreeMetric(
                label = stringResource(R.string.charts_big_three_rising_label),
                value = ascendantSign ?: stringResource(R.string.charts_unknown),
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun BigThreeMetric(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
) {
    Card(modifier = modifier) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
            )
        }
    }
}

private fun buildBirthChartExportFileName(
    profile: AppProfile,
    hideSensitiveDetailsEnabled: Boolean,
): String {
    val rawName = profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.SHARE)
        .lowercase()
        .replace(Regex("[^a-z0-9]+"), "-")
        .trim('-')
        .ifBlank { "birth-chart" }
    return "$rawName-birth-chart.txt"
}

private fun buildBirthChartExportSummary(
    context: android.content.Context,
    profile: AppProfile,
    chart: ChartData,
    hideSensitiveDetailsEnabled: Boolean,
    chartSource: AstroDataSource?,
    cachedChartActive: Boolean,
    cachedAtEpochMillis: Long?,
): String {
    val unknown = context.getString(R.string.charts_unknown)
    val sun = chart.planets.firstOrNull { it.name.equals("Sun", ignoreCase = true) }?.sign ?: unknown
    val moon = chart.planets.firstOrNull { it.name.equals("Moon", ignoreCase = true) }?.sign ?: unknown
    val rising = findAscendantSign(chart) ?: unknown
    return buildString {
        appendLine(context.getString(R.string.charts_export_heading_birth_chart))
        appendLine()
        appendLine(context.getString(R.string.share_profile_line, profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.SHARE)))
        appendLine(context.getString(R.string.charts_birth_date_format, profile.maskedDateOfBirth(hideSensitiveDetailsEnabled)))
        appendLine(context.getString(R.string.charts_birth_time_format, profile.maskedBirthTime(hideSensitiveDetailsEnabled)))
        appendLine(context.getString(R.string.charts_birthplace_format, profile.maskedBirthplace(hideSensitiveDetailsEnabled)))
        appendLine(context.getString(R.string.charts_house_system_format, chart.metadata?.houseSystem ?: profile.houseSystem))
        appendLine(context.getString(R.string.charts_timezone_format, chart.metadata?.timezone ?: profile.timezone ?: unknown))
        chartSource?.let {
            appendLine(context.getString(R.string.charts_chart_source_format, chartSourceLabel(context, it, cachedChartActive)))
        }
        appendLine()
        appendLine(context.getString(R.string.charts_big_three_title))
        appendLine("- ${context.getString(R.string.charts_big_three_sun_label)}: $sun")
        appendLine("- ${context.getString(R.string.charts_big_three_moon_label)}: $moon")
        appendLine("- ${context.getString(R.string.charts_big_three_rising_label)}: $rising")
        appendLine()
        appendLine(context.getString(R.string.charts_planet_placements_title))
        chart.planets.forEach { placement ->
            val houseSuffix = placement.house?.let { " · ${context.getString(R.string.charts_row_house, it)}" }.orEmpty()
            val retrogradeSuffix = if (placement.retrograde == true) {
                " · ${context.getString(R.string.charts_row_retrograde)}"
            } else {
                ""
            }
            appendLine("- ${placement.name}: ${placement.sign} ${"%.1f".format(placement.degree)}°$houseSuffix$retrogradeSuffix")
        }
        if (chart.aspects.isNotEmpty()) {
            appendLine()
            appendLine(context.getString(R.string.charts_key_aspects_title))
            chart.aspects.take(10).forEach { aspect ->
                val orbSuffix = aspect.orb?.let { " · ${context.getString(R.string.charts_row_orb, it)}" }.orEmpty()
                appendLine("- ${aspect.planetA} ${aspect.type} ${aspect.planetB}$orbSuffix")
            }
        }
        if (chart.houses.isNotEmpty()) {
            appendLine()
            appendLine(context.getString(R.string.charts_houses_title))
            chart.houses.forEach { house ->
                val houseLine = house.degree?.let { degree ->
                    context.getString(R.string.charts_house_placement_format_degree, house.house, house.sign, degree)
                } ?: context.getString(R.string.charts_house_placement_format, house.house, house.sign)
                appendLine("- $houseLine")
            }
        }
        if (cachedChartActive) {
            appendLine()
            appendLine(context.getString(R.string.charts_offline_snapshot_title))
            chartSource?.let {
                appendLine("- ${context.getString(R.string.charts_export_source_format, chartSourceLabel(context, it, cachedChartActive))}")
            }
            cachedAtEpochMillis?.let {
                appendLine("- ${context.getString(R.string.charts_cached_at_format, formatChartCacheTimestamp(it))}")
            }
        }
    }.trim()
}

private fun findAscendantSign(chart: ChartData): String? =
    chart.points.firstOrNull { point ->
        point.name.equals("Ascendant", ignoreCase = true) || point.name.equals("ASC", ignoreCase = true)
    }?.sign

private fun shareChartCard(
    context: Context,
    chart: ChartData,
    profile: AppProfile?,
    hideSensitiveDetailsEnabled: Boolean,
) {
    val profileName = profile?.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.SHARE) ?: "AstroNumeric"
    val birthTimeAssumed = chart.metadata?.birthTimeAssumed == true
    val density = context.resources.displayMetrics.density
    val widthPx = (300 * density * 3).toInt()
    val bitmap = renderComposableToBitmap(context, widthPx, 0) {
        ChartShareCard(chart = chart, profileName = profileName, birthTimeAssumed = birthTimeAssumed)
    }
    shareBitmapCard(context, bitmap, filename = "chart_share.png", chooserTitle = "Share Birth Chart")
}