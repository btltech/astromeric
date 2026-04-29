package com.astromeric.android.feature.charts

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
import androidx.compose.ui.unit.dp
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
                    "Birth chart summary exported."
                } else {
                    result.exceptionOrNull()?.message ?: "Birth chart export failed."
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
            result.errorMessage ?: "Birth chart could not be loaded."
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
            text = "Birth Chart",
            style = MaterialTheme.typography.headlineMedium,
        )

        StudioSectionCard(
            title = "Full chart detail",
            subtitle = "This dedicated flow mirrors iOS more closely: read the big three first, then move into placements, aspects, houses, and a portable chart summary.",
        ) {
            TextButton(onClick = onBackToCharts) {
                Text("Back to Charts Studio")
            }
            when {
                selectedProfile == null -> Text(
                    text = "Select or create a profile before opening the birth chart.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                !selectedProfile.canRequestNatalChart -> Text(
                    text = "Add birthplace coordinates and timezone to unlock the natal chart detail flow.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    val profile = selectedProfile
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(
                            onClick = { refreshVersion += 1 },
                            enabled = !isLoading,
                        ) {
                            Text(if (isLoading) "Refreshing..." else "Refresh chart")
                        }
                        OutlinedButton(
                            onClick = {
                                val chart = natalChart
                                if (chart == null) {
                                    onShowMessage("Load the birth chart first.")
                                    return@OutlinedButton
                                }
                                val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                    type = "text/plain"
                                    putExtra(Intent.EXTRA_SUBJECT, "AstroNumeric birth chart")
                                    putExtra(Intent.EXTRA_TEXT, buildBirthChartExportSummary(profile, chart, hideSensitiveDetailsEnabled, chartSource, cachedChartActive, cachedAtEpochMillis))
                                }
                                context.startActivity(Intent.createChooser(shareIntent, "Share birth chart summary"))
                            },
                            enabled = natalChart != null,
                        ) {
                            Text("Share summary")
                        }
                    }
                    OutlinedButton(
                        onClick = {
                            val chart = natalChart
                            if (chart == null) {
                                onShowMessage("Load the birth chart first.")
                                return@OutlinedButton
                            }
                            val export = PendingBirthChartExport(
                                fileName = buildBirthChartExportFileName(profile, hideSensitiveDetailsEnabled),
                                content = buildBirthChartExportSummary(profile, chart, hideSensitiveDetailsEnabled, chartSource, cachedChartActive, cachedAtEpochMillis),
                            )
                            pendingExport = export
                            exportLauncher.launch(export.fileName)
                        },
                        enabled = natalChart != null,
                    ) {
                        Text("Export summary")
                    }
                }
            }
        }

        if (cachedChartActive && natalChart != null) {
            StudioSectionCard(
                title = "Offline chart snapshot",
                subtitle = chartSourceDetail(chartSource, cachedChartActive),
            ) {
                cachedAtEpochMillis?.let { cachedAt ->
                    Text(
                        text = "Cached ${formatChartCacheTimestamp(cachedAt)}",
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
                        text = "Loading birth chart...",
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
                        title = "Calculation context",
                        subtitle = "Read this first so you know where the chart is exact and where it is estimated.",
                    ) {
                        metadata.dataQuality?.let { quality ->
                            AssistChip(onClick = {}, label = { Text(quality) })
                        }
                        chartSource?.let { source ->
                            AssistChip(onClick = {}, label = { Text(chartSourceLabel(source, cachedChartActive)) })
                        }
                        Text(
                            text = "House system: ${metadata.houseSystem ?: selectedProfile.houseSystem}",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = "Timezone: ${metadata.timezone ?: selectedProfile.timezone ?: "Unknown"}",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        if (metadata.birthTimeAssumed == true) {
                            Text(
                                text = "Birth time was assumed at ${metadata.assumedTimeOfBirth ?: "12:00"}.",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }

                if (chart.planets.isNotEmpty()) {
                    StudioSectionCard(
                        title = "Planet placements",
                        subtitle = "These placements show what part of you is speaking and the sign shows how it speaks.",
                    ) {
                        chart.planets.forEach { placement ->
                            PlanetPlacementRow(placement = placement)
                        }
                    }
                }

                if (chart.aspects.isNotEmpty()) {
                    StudioSectionCard(
                        title = "Key aspects",
                        subtitle = "Aspects tell you where energies reinforce each other, clash, or create useful tension.",
                    ) {
                        chart.aspects.take(10).forEach { aspect ->
                            AspectRow(aspect = aspect)
                        }
                    }
                }

                if (chart.houses.isNotEmpty()) {
                    StudioSectionCard(
                        title = "Houses",
                        subtitle = "Houses show where each part of the chart tends to play out in real life.",
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
        subtitle = "Start with the chart identity before diving into the technical layers.",
    ) {
        Text(
            text = "Birth date: ${profile.maskedDateOfBirth(hideSensitiveDetailsEnabled)}",
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = "Birth time: ${profile.maskedBirthTime(hideSensitiveDetailsEnabled)}",
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = "Birthplace: ${profile.maskedBirthplace(hideSensitiveDetailsEnabled)}",
            style = MaterialTheme.typography.bodyMedium,
        )
        Row(
            modifier = Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            listOfNotNull(
                chart.planets.firstOrNull { it.name.equals("Sun", ignoreCase = true) }?.let { "Sun ${it.sign}" },
                chart.planets.firstOrNull { it.name.equals("Moon", ignoreCase = true) }?.let { "Moon ${it.sign}" },
                findAscendantSign(chart)?.let { "Rising $it" },
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
        title = "Your Big Three",
        subtitle = "These are the fastest anchors for identity, emotional pattern, and presentation.",
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            BigThreeMetric(label = "Sun", value = sun?.sign ?: "Unknown", modifier = Modifier.weight(1f))
            BigThreeMetric(label = "Moon", value = moon?.sign ?: "Unknown", modifier = Modifier.weight(1f))
            BigThreeMetric(label = "Rising", value = ascendantSign ?: "Unknown", modifier = Modifier.weight(1f))
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
    profile: AppProfile,
    chart: ChartData,
    hideSensitiveDetailsEnabled: Boolean,
    chartSource: AstroDataSource?,
    cachedChartActive: Boolean,
    cachedAtEpochMillis: Long?,
): String {
    val sun = chart.planets.firstOrNull { it.name.equals("Sun", ignoreCase = true) }?.sign ?: "Unknown"
    val moon = chart.planets.firstOrNull { it.name.equals("Moon", ignoreCase = true) }?.sign ?: "Unknown"
    val rising = findAscendantSign(chart) ?: "Unknown"
    return buildString {
        appendLine("AstroNumeric Birth Chart")
        appendLine()
        appendLine("Profile: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.SHARE)}")
        appendLine("Birth date: ${profile.maskedDateOfBirth(hideSensitiveDetailsEnabled)}")
        appendLine("Birth time: ${profile.maskedBirthTime(hideSensitiveDetailsEnabled)}")
        appendLine("Birthplace: ${profile.maskedBirthplace(hideSensitiveDetailsEnabled)}")
        appendLine("House system: ${chart.metadata?.houseSystem ?: profile.houseSystem}")
        appendLine("Timezone: ${chart.metadata?.timezone ?: profile.timezone ?: "Unknown"}")
        chartSource?.let { appendLine("Chart source: ${chartSourceLabel(it, cachedChartActive)}") }
        appendLine()
        appendLine("Big Three")
        appendLine("- Sun: $sun")
        appendLine("- Moon: $moon")
        appendLine("- Rising: $rising")
        appendLine()
        appendLine("Planet placements")
        chart.planets.forEach { placement ->
            appendLine("- ${placement.name}: ${placement.sign} ${"%.1f".format(placement.degree)}°${placement.house?.let { " · House $it" } ?: ""}${if (placement.retrograde == true) " · Rx" else ""}")
        }
        if (chart.aspects.isNotEmpty()) {
            appendLine()
            appendLine("Key aspects")
            chart.aspects.take(10).forEach { aspect ->
                appendLine("- ${aspect.planetA} ${aspect.type} ${aspect.planetB}${aspect.orb?.let { " · orb ${"%.1f".format(it)}°" } ?: ""}")
            }
        }
        if (chart.houses.isNotEmpty()) {
            appendLine()
            appendLine("Houses")
            chart.houses.forEach { house ->
                appendLine("- House ${house.house}: ${house.sign}${house.degree?.let { " ${"%.1f".format(it)}°" } ?: ""}")
            }
        }
        if (cachedChartActive) {
            appendLine()
            appendLine("Offline snapshot")
            chartSource?.let { appendLine("- Source: ${chartSourceLabel(it, cachedChartActive)}") }
            cachedAtEpochMillis?.let { appendLine("- Cached: ${formatChartCacheTimestamp(it)}") }
        }
    }.trim()
}

private fun findAscendantSign(chart: ChartData): String? =
    chart.points.firstOrNull { point ->
        point.name.equals("Ascendant", ignoreCase = true) || point.name.equals("ASC", ignoreCase = true)
    }?.sign