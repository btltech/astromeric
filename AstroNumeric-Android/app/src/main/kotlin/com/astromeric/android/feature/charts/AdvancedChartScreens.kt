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
import com.astromeric.android.core.ui.DataQualityBanner
import com.astromeric.android.core.ui.PremiumLoadingCard
import java.time.LocalDate

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