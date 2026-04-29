package com.astromeric.android.feature.charts

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PremiumLoadingCard

@Composable
internal fun BirthChartTab(
    selectedProfile: AppProfile?,
    natalChart: ChartData?,
    isLoading: Boolean,
    errorMessage: String?,
    chartSource: AstroDataSource?,
    cachedChartActive: Boolean,
    cachedAtEpochMillis: Long?,
    onRefresh: () -> Unit,
    onOpenBirthChart: () -> Unit,
    hideSensitiveDetailsEnabled: Boolean,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        StudioSectionCard(
            title = "Birth chart foundation",
            subtitle = "Android prefers the live backend for natal charts, then falls back to on-device Swiss or a saved snapshot so the chart remains readable.",
        ) {
            Text(
                text = "Current profile quality: ${selectedProfile?.dataQuality?.label ?: "No profile selected"}",
                style = MaterialTheme.typography.bodyMedium,
            )
            if (natalChart != null && chartSource != null) {
                AssistChip(
                    onClick = {},
                    label = { Text(chartSourceLabel(chartSource, cachedChartActive)) },
                )
                Text(
                    text = chartSourceDetail(chartSource, cachedChartActive),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            when {
                selectedProfile == null -> Text(
                    text = "Select or create a profile before requesting chart data.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                !selectedProfile.canRequestNatalChart -> Text(
                    text = "Add birthplace coordinates and timezone to unlock natal chart calculations. Birth time is optional and will fall back to noon-style estimation.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    Text(
                        text = selectedProfile.dataQuality.description,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Button(
                        onClick = onRefresh,
                        enabled = !isLoading,
                    ) {
                        Text(if (isLoading) "Refreshing..." else "Refresh chart")
                    }
                    OutlinedButton(
                        onClick = onOpenBirthChart,
                        enabled = natalChart != null,
                    ) {
                        Text("Open full Birth Chart")
                    }
                }
            }
        }

        if (cachedChartActive && natalChart != null) {
            StudioSectionCard(
                title = "Offline resilience",
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
            isLoading -> PremiumLoadingCard(title = "Loading natal chart")

            errorMessage != null -> StatusCard(message = errorMessage, isError = true)

            natalChart != null -> {
                StudioSectionCard(
                    title = selectedProfile?.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER) ?: "Birth Chart",
                    subtitle = "Use the studio tab for orientation, then open the full chart flow for a dedicated detail and export surface.",
                ) {
                    Row(
                        modifier = Modifier.horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        listOfNotNull(
                            natalChart.planets.firstOrNull { it.name.equals("Sun", ignoreCase = true) }?.let { "Sun ${it.sign}" },
                            natalChart.planets.firstOrNull { it.name.equals("Moon", ignoreCase = true) }?.let { "Moon ${it.sign}" },
                            natalChart.points.firstOrNull {
                                it.name.equals("Ascendant", ignoreCase = true) || it.name.equals("ASC", ignoreCase = true)
                            }?.let { "Rising ${it.sign}" },
                        ).forEach { chip ->
                            AssistChip(onClick = {}, label = { Text(chip) })
                        }
                    }
                    TextButton(onClick = onOpenBirthChart) {
                        Text("Open dedicated chart detail")
                    }
                }

                natalChart.metadata?.let { metadata ->
                    StudioSectionCard(
                        title = "Chart metadata",
                        subtitle = "Read the calculation context before interpreting placements.",
                    ) {
                        metadata.dataQuality?.let { quality ->
                            AssistChip(onClick = {}, label = { Text(quality) })
                        }
                        chartSource?.let { source ->
                            AssistChip(onClick = {}, label = { Text(chartSourceLabel(source, cachedChartActive)) })
                        }
                        Text(
                            text = "House system: ${metadata.houseSystem ?: selectedProfile?.houseSystem ?: "Unknown"}",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = "Timezone: ${metadata.timezone ?: selectedProfile?.timezone ?: "Unknown"}",
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

                if (natalChart.planets.isNotEmpty()) {
                    StudioSectionCard(
                        title = "Planet preview",
                        subtitle = "The dedicated detail flow carries the full placement list, export actions, and a more iOS-like reading order.",
                    ) {
                        natalChart.planets.take(6).forEach { placement ->
                            PlanetPlacementRow(placement = placement)
                        }
                        TextButton(onClick = onOpenBirthChart) {
                            Text("See all placements")
                        }
                    }
                }

                if (natalChart.houses.isNotEmpty()) {
                    StudioSectionCard(
                        title = "House preview",
                        subtitle = "Houses tell you where each theme is landing in lived experience.",
                    ) {
                        natalChart.houses.take(6).forEach { house ->
                            HousePlacementRow(house = house)
                        }
                    }
                }

                if (natalChart.aspects.isNotEmpty()) {
                    StudioSectionCard(
                        title = "Aspect preview",
                        subtitle = "These are the strongest internal tensions and harmonies in the natal pattern.",
                    ) {
                        natalChart.aspects.take(8).forEach { aspect ->
                            AspectRow(aspect = aspect)
                        }
                    }
                }
            }
        }
    }
}

@Composable
internal fun CompatibilityTab(
    selectedProfile: AppProfile?,
    partnerProfiles: List<AppProfile>,
    onOpenRelationships: () -> Unit,
    onOpenSynastry: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        StudioSectionCard(
            title = "Relationship chemistry",
            subtitle = "Compatibility is more useful when it explains where connection is easy, where friction is productive, and where effort is required.",
        ) {
            when {
                selectedProfile == null -> Text(
                    text = "Select your primary profile to compare relationships.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    Text(
                        text = "Saved comparison profiles: ${partnerProfiles.size}",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    if (partnerProfiles.isNotEmpty()) {
                        Row(
                            modifier = Modifier.horizontalScroll(rememberScrollState()),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            partnerProfiles.forEach { partner ->
                                AssistChip(
                                    onClick = {},
                                    label = { Text(partner.name) },
                                )
                            }
                        }
                    }
                }
            }
        }

        StudioActionCard(
            title = "Open Relationships",
            subtitle = "Go to the broader compatibility workspace for romantic, friendship, and timing tools.",
            buttonLabel = "Open Relationships",
            onClick = onOpenRelationships,
        )

        StudioActionCard(
            title = "Jump to Synastry",
            subtitle = "When both people have chart-ready data, move straight into aspect-level comparison.",
            buttonLabel = "Open Synastry",
            onClick = onOpenSynastry,
            enabled = selectedProfile != null && partnerProfiles.isNotEmpty(),
            note = if (partnerProfiles.isEmpty()) "Add another saved profile first." else null,
        )
    }
}

@Composable
internal fun AdvancedChartsTab(
    selectedProfile: AppProfile?,
    partnerProfiles: List<AppProfile>,
    onOpenYearAhead: () -> Unit,
    onOpenProgressions: () -> Unit,
    onOpenSynastry: () -> Unit,
    onOpenComposite: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        StudioSectionCard(
            title = "Advanced chart layers",
            subtitle = "Pick the layer that matches the question instead of forcing every question through the natal chart alone.",
        ) {
            Text(
                text = "Returns explain the year, progressions explain inner development, synastry explains contact, and composite explains the relationship itself.",
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        StudioActionCard(
            title = "Solar Return + Year Ahead",
            subtitle = "Read your personal year, solar return framing, and monthly themes in one dedicated flow.",
            buttonLabel = "Open Year Ahead",
            onClick = onOpenYearAhead,
        )

        StudioActionCard(
            title = "Progressions",
            subtitle = "Open the dedicated progression flow instead of loading a compact summary inside the studio.",
            buttonLabel = "Open Progressions",
            onClick = onOpenProgressions,
            enabled = selectedProfile?.canRequestNatalChart == true,
            note = if (selectedProfile?.canRequestNatalChart != true) {
                "Add birthplace coordinates and timezone to unlock progressed chart calculations."
            } else {
                null
            },
        )

        StudioActionCard(
            title = "Synastry",
            subtitle = "Move into a dedicated aspect-level comparison between two chart-ready profiles.",
            buttonLabel = "Open Synastry",
            onClick = onOpenSynastry,
            enabled = selectedProfile?.canRequestNatalChart == true && partnerProfiles.isNotEmpty(),
            note = when {
                partnerProfiles.isEmpty() -> "Add another saved profile first."
                selectedProfile?.canRequestNatalChart != true -> "Finish the primary profile's birth coordinates and timezone first."
                else -> null
            },
        )

        StudioActionCard(
            title = "Composite Chart",
            subtitle = "See the relationship's shared chart in its own flow instead of a compressed card.",
            buttonLabel = "Open Composite",
            onClick = onOpenComposite,
            enabled = selectedProfile?.canRequestNatalChart == true && partnerProfiles.isNotEmpty(),
            note = when {
                partnerProfiles.isEmpty() -> "Add another saved profile first."
                selectedProfile?.canRequestNatalChart != true -> "Finish the primary profile's birth coordinates and timezone first."
                else -> null
            },
        )
    }
}
