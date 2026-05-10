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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.DataQuality
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.DataQualityBanner
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
    val context = LocalContext.current
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        if (selectedProfile != null && selectedProfile.dataQuality != DataQuality.FULL) {
            DataQualityBanner(quality = selectedProfile.dataQuality)
        }
        StudioSectionCard(
            title = stringResource(R.string.charts_birth_foundation_title),
            subtitle = stringResource(R.string.charts_birth_foundation_subtitle),
        ) {
            Text(
                text = stringResource(
                    R.string.charts_current_profile_quality_format,
                    selectedProfile?.dataQuality?.label ?: stringResource(R.string.charts_no_profile_selected),
                ),
                style = MaterialTheme.typography.bodyMedium,
            )
            if (natalChart != null && chartSource != null) {
                AssistChip(
                    onClick = {},
                    label = { Text(chartSourceLabel(context, chartSource, cachedChartActive)) },
                )
                Text(
                    text = chartSourceDetail(context, chartSource, cachedChartActive),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            when {
                selectedProfile == null -> Text(
                    text = stringResource(R.string.charts_birth_tab_profile_required),
                    style = MaterialTheme.typography.bodyMedium,
                )

                !selectedProfile.canRequestNatalChart -> Text(
                    text = stringResource(R.string.charts_birth_tab_require_location_timezone),
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
                        Text(
                            if (isLoading) {
                                stringResource(R.string.status_refreshing)
                            } else {
                                stringResource(R.string.charts_action_refresh_chart)
                            },
                        )
                    }
                    OutlinedButton(
                        onClick = onOpenBirthChart,
                        enabled = natalChart != null,
                    ) {
                        Text(stringResource(R.string.charts_action_open_full_birth_chart))
                    }
                }
            }
        }

        if (cachedChartActive && natalChart != null) {
            StudioSectionCard(
                title = stringResource(R.string.charts_offline_resilience_title),
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
            isLoading -> PremiumLoadingCard(title = stringResource(R.string.charts_loading_natal_chart))

            errorMessage != null -> StatusCard(message = errorMessage, isError = true)

            natalChart != null -> {
                StudioSectionCard(
                    title = selectedProfile?.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER) ?: stringResource(R.string.charts_birth_title),
                    subtitle = stringResource(R.string.charts_birth_tab_identity_subtitle),
                ) {
                    Row(
                        modifier = Modifier.horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        listOfNotNull(
                            natalChart.planets.firstOrNull { it.name.equals("Sun", ignoreCase = true) }?.let {
                                stringResource(R.string.charts_chip_sun_format, it.sign)
                            },
                            natalChart.planets.firstOrNull { it.name.equals("Moon", ignoreCase = true) }?.let {
                                stringResource(R.string.charts_chip_moon_format, it.sign)
                            },
                            natalChart.points.firstOrNull {
                                it.name.equals("Ascendant", ignoreCase = true) || it.name.equals("ASC", ignoreCase = true)
                            }?.let { stringResource(R.string.charts_chip_rising_format, it.sign) },
                        ).forEach { chip ->
                            AssistChip(onClick = {}, label = { Text(chip) })
                        }
                    }
                    TextButton(onClick = onOpenBirthChart) {
                        Text(stringResource(R.string.charts_action_open_dedicated_chart_detail))
                    }
                }

                natalChart.metadata?.let { metadata ->
                    StudioSectionCard(
                        title = stringResource(R.string.charts_chart_metadata_title),
                        subtitle = stringResource(R.string.charts_chart_metadata_subtitle),
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
                                metadata.houseSystem ?: selectedProfile?.houseSystem ?: stringResource(R.string.charts_unknown),
                            ),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = stringResource(
                                R.string.charts_timezone_format,
                                metadata.timezone ?: selectedProfile?.timezone ?: stringResource(R.string.charts_unknown),
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

                if (natalChart.planets.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_planet_preview_title),
                        subtitle = stringResource(R.string.charts_planet_preview_subtitle),
                    ) {
                        natalChart.planets.take(6).forEach { placement ->
                            PlanetPlacementRow(placement = placement)
                        }
                        TextButton(onClick = onOpenBirthChart) {
                            Text(stringResource(R.string.charts_action_see_all_placements))
                        }
                    }
                }

                if (natalChart.houses.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_house_preview_title),
                        subtitle = stringResource(R.string.charts_house_preview_subtitle),
                    ) {
                        natalChart.houses.take(6).forEach { house ->
                            HousePlacementRow(house = house)
                        }
                    }
                }

                if (natalChart.aspects.isNotEmpty()) {
                    StudioSectionCard(
                        title = stringResource(R.string.charts_aspect_preview_title),
                        subtitle = stringResource(R.string.charts_aspect_preview_subtitle),
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
    onOpenCompatibility: () -> Unit,
    onOpenRelationships: () -> Unit,
    onOpenSynastry: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        StudioSectionCard(
            title = stringResource(R.string.charts_relationship_chemistry_title),
            subtitle = stringResource(R.string.charts_relationship_chemistry_subtitle),
        ) {
            when {
                selectedProfile == null -> Text(
                    text = stringResource(R.string.charts_select_primary_profile_relationships),
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    Text(
                        text = stringResource(R.string.charts_saved_comparison_profiles_format, partnerProfiles.size),
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
            title = stringResource(R.string.charts_open_compatibility_title),
            subtitle = stringResource(R.string.charts_open_compatibility_subtitle),
            buttonLabel = stringResource(R.string.charts_action_open_compatibility),
            onClick = onOpenCompatibility,
            enabled = selectedProfile != null,
        )

        StudioActionCard(
            title = stringResource(R.string.charts_open_relationships_title),
            subtitle = stringResource(R.string.charts_open_relationships_subtitle),
            buttonLabel = stringResource(R.string.charts_action_open_relationships),
            onClick = onOpenRelationships,
        )

        StudioActionCard(
            title = stringResource(R.string.charts_jump_to_synastry_title),
            subtitle = stringResource(R.string.charts_jump_to_synastry_subtitle),
            buttonLabel = stringResource(R.string.charts_action_open_synastry),
            onClick = onOpenSynastry,
            enabled = selectedProfile != null && partnerProfiles.isNotEmpty(),
            note = if (partnerProfiles.isEmpty()) stringResource(R.string.charts_add_saved_profile_first) else null,
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
            title = stringResource(R.string.charts_advanced_layers_title),
            subtitle = stringResource(R.string.charts_advanced_layers_subtitle),
        ) {
            Text(
                text = stringResource(R.string.charts_advanced_layers_body),
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        StudioActionCard(
            title = stringResource(R.string.charts_solar_return_title),
            subtitle = stringResource(R.string.charts_solar_return_subtitle),
            buttonLabel = stringResource(R.string.charts_action_open_year_ahead),
            onClick = onOpenYearAhead,
        )

        StudioActionCard(
            title = stringResource(R.string.charts_progressions_card_title),
            subtitle = stringResource(R.string.charts_progressions_card_subtitle),
            buttonLabel = stringResource(R.string.charts_action_open_progressions),
            onClick = onOpenProgressions,
            enabled = selectedProfile?.canRequestNatalChart == true,
            note = if (selectedProfile?.canRequestNatalChart != true) {
                stringResource(R.string.charts_progressions_require_location_timezone)
            } else {
                null
            },
        )

        StudioActionCard(
            title = stringResource(R.string.charts_synastry_card_title),
            subtitle = stringResource(R.string.charts_synastry_card_subtitle),
            buttonLabel = stringResource(R.string.charts_action_open_synastry),
            onClick = onOpenSynastry,
            enabled = selectedProfile?.canRequestNatalChart == true && partnerProfiles.isNotEmpty(),
            note = when {
                partnerProfiles.isEmpty() -> stringResource(R.string.charts_add_saved_profile_first)
                selectedProfile?.canRequestNatalChart != true -> stringResource(R.string.charts_finish_primary_profile_birth_details)
                else -> null
            },
        )

        StudioActionCard(
            title = stringResource(R.string.charts_composite_card_title),
            subtitle = stringResource(R.string.charts_composite_card_subtitle),
            buttonLabel = stringResource(R.string.charts_action_open_composite),
            onClick = onOpenComposite,
            enabled = selectedProfile?.canRequestNatalChart == true && partnerProfiles.isNotEmpty(),
            note = when {
                partnerProfiles.isEmpty() -> stringResource(R.string.charts_add_saved_profile_first)
                selectedProfile?.canRequestNatalChart != true -> stringResource(R.string.charts_finish_primary_profile_birth_details)
                else -> null
            },
        )
    }
}
