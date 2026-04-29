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
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.CompositeChartData
import com.astromeric.android.core.model.SynastryChartData
import com.astromeric.android.core.ui.PremiumLoadingCard
import java.time.LocalDate

@Composable
fun ProgressionsScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBackToCharts: () -> Unit,
    modifier: Modifier = Modifier,
) {
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
                errorMessage = it.message ?: "Progressed chart could not be loaded."
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
            text = "Progressions",
            style = MaterialTheme.typography.headlineMedium,
        )

        StudioSectionCard(
            title = "Secondary progressions",
            subtitle = "Use this view when you need inner development and long-form timing, not just the natal snapshot.",
        ) {
            TextButton(onClick = onBackToCharts) {
                Text("Back to Charts Studio")
            }
            when {
                selectedProfile == null -> Text(
                    text = "Select or create a profile before loading progressions.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                !selectedProfile.canRequestNatalChart -> Text(
                    text = "Add birthplace coordinates and timezone to unlock progressed chart calculations.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    Text(
                        text = "Reading for ${selectedProfile.name} · ${selectedProfile.dataQuality.label}",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Button(
                        onClick = { refreshVersion += 1 },
                        enabled = !isLoading,
                    ) {
                        Text(if (isLoading) "Refreshing..." else "Refresh progressions")
                    }
                }
            }
        }

        when {
            isLoading -> PremiumLoadingCard(title = "Loading progressed chart")

            errorMessage != null -> StatusCard(message = errorMessage.orEmpty(), isError = true)

            chart != null -> {
                chart?.metadata?.let { metadata ->
                    StudioSectionCard(
                        title = "Chart context",
                        subtitle = "Ground the progression in the natal profile before interpreting movement.",
                    ) {
                        Text(
                            text = "Natal date: ${metadata.dateOfBirth ?: selectedProfile?.dateOfBirth ?: "Unknown"}",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = "Birth time anchor: ${metadata.timeOfBirth ?: selectedProfile?.timeOfBirth ?: "Unknown"}",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = "Timezone: ${metadata.timezone ?: selectedProfile?.timezone ?: "Unknown"}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }

                if (!chart?.planets.isNullOrEmpty()) {
                    StudioSectionCard(
                        title = "Progressed planets",
                        subtitle = "These placements show how your natal potential is unfolding over time.",
                    ) {
                        chart?.planets?.take(10)?.forEach { placement ->
                            PlanetPlacementRow(placement = placement)
                        }
                    }
                }

                if (!chart?.aspects.isNullOrEmpty()) {
                    StudioSectionCard(
                        title = "Progressed aspects",
                        subtitle = "Look for the relationships that keep repeating across the current chapter.",
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
                errorMessage = it.message ?: "Synastry chart could not be loaded."
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
            text = "Synastry",
            style = MaterialTheme.typography.headlineMedium,
        )

        StudioSectionCard(
            title = "Aspect-level relationship insight",
            subtitle = "Use synastry when you need to see where two charts support, trigger, or challenge each other.",
        ) {
            TextButton(onClick = onBackToCharts) {
                Text("Back to Charts Studio")
            }
            when {
                selectedProfile == null -> Text(
                    text = "Select your primary profile before comparing charts.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                partnerProfiles.isEmpty() -> Text(
                    text = "Add another saved profile to unlock synastry comparisons.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    Text(
                        text = "Choose a comparison profile",
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
                        Text(if (isLoading) "Refreshing..." else "Refresh synastry")
                    }
                    if (selectedPartner?.canRequestNatalChart != true) {
                        Text(
                            text = "Both profiles need birthplace coordinates and timezone before synastry can calculate cleanly.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
        }

        when {
            isLoading -> PremiumLoadingCard(title = "Comparing charts")

            errorMessage != null -> StatusCard(message = errorMessage.orEmpty(), isError = true)

            result != null -> {
                StudioSectionCard(
                    title = "Compatibility snapshot",
                    subtitle = "Use this summary to separate chemistry, friction, and practical advice.",
                ) {
                    Text(
                        text = "${result?.personA?.name.orEmpty()} and ${result?.personB?.name.orEmpty()}",
                        style = MaterialTheme.typography.titleMedium,
                    )
                    result?.compatibility?.strengths?.take(3)?.forEach { strength ->
                        Text(
                            text = "Strength: $strength",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                    result?.compatibility?.challenges?.take(3)?.forEach { challenge ->
                        Text(
                            text = "Challenge: $challenge",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                    result?.compatibility?.advice?.take(3)?.forEach { advice ->
                        Text(
                            text = "Advice: $advice",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                }

                if (!result?.synastryAspects.isNullOrEmpty()) {
                    StudioSectionCard(
                        title = "Key synastry aspects",
                        subtitle = "These are the main energetic contact points between both charts.",
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
                errorMessage = it.message ?: "Composite chart could not be loaded."
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
            text = "Composite Chart",
            style = MaterialTheme.typography.headlineMedium,
        )

        StudioSectionCard(
            title = "The relationship itself",
            subtitle = "Composite charts describe the shared field created by two people, not just each person separately.",
        ) {
            TextButton(onClick = onBackToCharts) {
                Text("Back to Charts Studio")
            }
            when {
                selectedProfile == null -> Text(
                    text = "Select your primary profile before building a composite chart.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                partnerProfiles.isEmpty() -> Text(
                    text = "Add another saved profile to build a composite chart.",
                    style = MaterialTheme.typography.bodyMedium,
                )

                else -> {
                    Text(
                        text = "Choose a comparison profile",
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
                        Text(if (isLoading) "Refreshing..." else "Refresh composite")
                    }
                    if (selectedPartner?.canRequestNatalChart != true) {
                        Text(
                            text = "Both profiles need birthplace coordinates and timezone before the composite chart can calculate cleanly.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
        }

        when {
            isLoading -> PremiumLoadingCard(title = "Building composite chart")

            errorMessage != null -> StatusCard(message = errorMessage.orEmpty(), isError = true)

            result != null -> {
                StudioSectionCard(
                    title = "Composite frame",
                    subtitle = "Start with the chart identity before reading the planet blend.",
                ) {
                    Text(
                        text = "${result?.metadata?.personA.orEmpty()} + ${result?.metadata?.personB.orEmpty()}",
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = "Method: ${result?.metadata?.method.orEmpty()}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }

                if (!result?.planets.isNullOrEmpty()) {
                    StudioSectionCard(
                        title = "Composite planets",
                        subtitle = "These placements describe the relationship's tone, focus, and pressure points.",
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