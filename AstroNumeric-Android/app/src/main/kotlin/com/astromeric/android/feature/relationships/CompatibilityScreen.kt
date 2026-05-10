package com.astromeric.android.feature.relationships

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.R
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.CompatibilityMode
import com.astromeric.android.core.model.CompatibilityReportData
import com.astromeric.android.core.model.DataQuality
import com.astromeric.android.core.ui.DataQualityBanner
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.SavedRelationshipData
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.manualComparisonProfileId
import com.astromeric.android.core.model.toSavedRelationship
import com.astromeric.android.core.model.ProfilePayload
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumHeroCard
import com.astromeric.android.core.ui.PremiumLoadingCard
import java.time.LocalDate
import java.time.LocalTime
import kotlinx.coroutines.launch

@Composable
@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
fun CompatibilityScreen(
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    preferencesStore: AppPreferencesStore,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()
    val snackbarHostState = remember { SnackbarHostState() }
    val savedRelationships by preferencesStore.savedRelationships.collectAsStateWithLifecycle(initialValue = emptyList())
    val comparisonProfiles = remember(profiles, selectedProfile?.id) {
        profiles.filter { it.id != selectedProfile?.id }
    }

    var compatibilityMode by rememberSaveable { mutableStateOf(CompatibilityMode.ROMANTIC) }
    var useSavedProfile by rememberSaveable(comparisonProfiles.isNotEmpty()) {
        mutableStateOf(comparisonProfiles.isNotEmpty())
    }
    var selectedComparisonProfileId by rememberSaveable(selectedProfile?.id, profiles.size) {
        mutableStateOf(comparisonProfiles.firstOrNull()?.id)
    }

    var manualName by rememberSaveable(selectedProfile?.id) { mutableStateOf("") }
    var manualDob by rememberSaveable(selectedProfile?.id) { mutableStateOf("") }
    var manualTob by rememberSaveable(selectedProfile?.id) { mutableStateOf("") }
    var manualRequestVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }

    var isLoading by remember(selectedProfile?.id, selectedComparisonProfileId, compatibilityMode) {
        mutableStateOf(false)
    }
    var result by remember(selectedProfile?.id, selectedComparisonProfileId, compatibilityMode) {
        mutableStateOf<CompatibilityReportData?>(null)
    }
    var errorMessage by remember(selectedProfile?.id, selectedComparisonProfileId, compatibilityMode) {
        mutableStateOf<String?>(null)
    }
    var hasSaved by remember(result) { mutableStateOf(false) }

    val comparisonProfile = comparisonProfiles.firstOrNull { it.id == selectedComparisonProfileId }
    val manualReady = manualName.trim().isNotBlank() && isIsoDate(manualDob)
    val manualTimeValid = manualTob.isBlank() || isIsoTime(manualTob)
    val manualComparisonId = if (manualReady) manualComparisonProfileId(manualName, manualDob) else null

    val existingSaved = savedRelationships.firstOrNull { saved ->
        saved.primaryProfileId == selectedProfile?.id &&
            saved.comparisonProfileId == (if (useSavedProfile) comparisonProfile?.id else manualComparisonId) &&
            saved.mode == compatibilityMode
    }

    // Keep profile picker in sync if profiles change
    LaunchedEffect(selectedProfile?.id, profiles.size) {
        if (comparisonProfiles.none { it.id == selectedComparisonProfileId }) {
            selectedComparisonProfileId = comparisonProfiles.firstOrNull()?.id
        }
        if (comparisonProfiles.isEmpty()) useSavedProfile = false
    }

    // Auto-load when saved-profile mode is active
    LaunchedEffect(selectedProfile?.id, selectedComparisonProfileId, compatibilityMode) {
        if (!useSavedProfile) return@LaunchedEffect
        val profile = selectedProfile ?: return@LaunchedEffect
        val comparison = comparisonProfile ?: return@LaunchedEffect
        isLoading = true
        errorMessage = null
        remoteDataSource.fetchCompatibility(compatibilityMode, profile, comparison)
            .onSuccess { result = it }
            .onFailure { errorMessage = it.message ?: "Compatibility could not be loaded." }
        isLoading = false
    }

    // Load when manual Calculate is triggered
    LaunchedEffect(selectedProfile?.id, compatibilityMode, manualRequestVersion) {
        if (useSavedProfile || manualRequestVersion == 0) return@LaunchedEffect
        val profile = selectedProfile ?: return@LaunchedEffect
        if (!manualReady || !manualTimeValid) return@LaunchedEffect
        isLoading = true
        errorMessage = null
        remoteDataSource.fetchCompatibility(
            mode = compatibilityMode,
            personA = profile,
            personB = buildManualCompatibilityPayload(manualName, manualDob, manualTob),
        )
            .onSuccess { result = it }
            .onFailure { errorMessage = it.message ?: "Compatibility could not be loaded." }
        isLoading = false
    }

    Scaffold(
        modifier = modifier,
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.compatibility_screen_title)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.action_back),
                        )
                    }
                },
                actions = {
                    if (result != null) {
                        TextButton(
                            onClick = {
                                result = null
                                manualName = ""
                                manualDob = ""
                                manualTob = ""
                                manualRequestVersion = 0
                                errorMessage = null
                                hasSaved = false
                            },
                        ) {
                            Text(stringResource(R.string.compatibility_action_reset))
                        }
                    }
                },
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(innerPadding)
                .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            // Hero
            PremiumHeroCard(
                eyebrow = stringResource(R.string.compatibility_hero_eyebrow),
                title = stringResource(R.string.compatibility_hero_title),
                body = stringResource(R.string.compatibility_hero_body),
                chips = selectedProfile?.let {
                    listOf(
                        it.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                    )
                }.orEmpty(),
            )

            // Data quality notice
            if (selectedProfile != null && selectedProfile.dataQuality != DataQuality.FULL) {
                DataQualityBanner(quality = selectedProfile.dataQuality)
            }

            // Mode selector
            PremiumContentCard(
                title = stringResource(R.string.compatibility_section_input_title),
                body = stringResource(R.string.compatibility_section_input_subtitle),
            ) {
                if (selectedProfile == null) {
                    Text(
                        text = stringResource(R.string.relationships_select_primary_profile),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    return@PremiumContentCard
                }

                // Compatibility mode chips
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    CompatibilityMode.entries.forEach { mode ->
                        FilterChip(
                            selected = compatibilityMode == mode,
                            onClick = {
                                compatibilityMode = mode
                                result = null
                                hasSaved = false
                            },
                            label = { Text(compatibilityModeLabel(mode)) },
                        )
                    }
                }

                // Saved vs manual toggle (only if secondary profiles exist)
                if (comparisonProfiles.isNotEmpty()) {
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        FilterChip(
                            selected = useSavedProfile,
                            onClick = { useSavedProfile = true; result = null; hasSaved = false },
                            label = { Text(stringResource(R.string.relationships_saved_profile)) },
                        )
                        FilterChip(
                            selected = !useSavedProfile,
                            onClick = { useSavedProfile = false; result = null; hasSaved = false },
                            label = { Text(stringResource(R.string.relationships_manual_entry)) },
                        )
                    }
                }

                // Input area
                if (useSavedProfile) {
                    SavedProfileComparisonPicker(
                        comparisonProfiles = comparisonProfiles,
                        selectedComparisonProfileId = selectedComparisonProfileId,
                        onSelectedComparisonProfileIdChange = {
                            selectedComparisonProfileId = it
                            result = null
                            hasSaved = false
                        },
                        hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                    )
                } else {
                    ManualComparisonForm(
                        manualComparisonName = manualName,
                        onManualComparisonNameChange = { manualName = it },
                        manualComparisonDateOfBirth = manualDob,
                        onManualComparisonDateOfBirthChange = { manualDob = it },
                        manualComparisonTimeOfBirth = manualTob,
                        onManualComparisonTimeOfBirthChange = { manualTob = it },
                        canCalculate = manualReady && manualTimeValid,
                        onCalculateManual = { manualRequestVersion += 1 },
                    )
                }
            }

            // Results
            when {
                isLoading -> PremiumLoadingCard(title = stringResource(R.string.compatibility_loading))
                errorMessage != null -> PremiumContentCard(
                    title = stringResource(R.string.compatibility_error_title),
                    body = errorMessage,
                ) {}
                result != null -> CompatibilityResultCard(
                    compatibility = result!!,
                    compatibilityMode = compatibilityMode,
                    useSavedProfile = useSavedProfile,
                    existingSaved = existingSaved,
                    hasSaved = hasSaved,
                    onSave = {
                        val currentResult = result ?: return@CompatibilityResultCard
                        val primary = selectedProfile ?: return@CompatibilityResultCard
                        scope.launch {
                            val toSave = if (useSavedProfile && comparisonProfile != null) {
                                currentResult.toSavedRelationship(primary, comparisonProfile, compatibilityMode)
                            } else {
                                currentResult.toSavedRelationship(primary, manualName, manualDob, compatibilityMode)
                            }
                            preferencesStore.saveRelationship(toSave)
                            hasSaved = true
                            snackbarHostState.showSnackbar(
                                if (existingSaved != null) "Match updated." else "Saved to relationships."
                            )
                        }
                    },
                )
                useSavedProfile && comparisonProfile == null -> Unit
                !useSavedProfile && manualRequestVersion == 0 -> Unit
            }
        }
    }
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
private fun CompatibilityResultCard(
    compatibility: CompatibilityReportData,
    compatibilityMode: CompatibilityMode,
    useSavedProfile: Boolean,
    existingSaved: SavedRelationshipData?,
    hasSaved: Boolean,
    onSave: () -> Unit,
) {
    PremiumContentCard(
        title = stringResource(R.string.compatibility_result_title),
        body = null,
    ) {
        AssistChip(
            onClick = {},
            label = {
                Text(
                    stringResource(
                        R.string.relationships_score_mode_chip,
                        (compatibility.overallScore * 100).toInt(),
                        compatibilityModeLabel(compatibilityMode),
                    ),
                )
            },
        )
        Text(text = compatibility.summary, style = MaterialTheme.typography.bodyMedium)
        compatibility.dataQualityNote?.takeIf { it.isNotBlank() }?.let {
            Text(text = it, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        compatibility.dimensions.take(3).forEach { dimension ->
            Text(
                text = buildString {
                    append(stringResource(R.string.relationships_dimension_score, dimension.name, (dimension.score * 100).toInt()))
                    dimension.interpretation?.let { append(" · $it") }
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        if (compatibility.strengths.isNotEmpty()) {
            Text(
                text = stringResource(R.string.relationships_strengths, compatibility.strengths.joinToString()),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        if (compatibility.recommendations.isNotEmpty()) {
            Text(
                text = stringResource(R.string.relationships_recommendations, compatibility.recommendations.joinToString()),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        Button(onClick = onSave, enabled = !hasSaved) {
            Text(
                when {
                    hasSaved -> stringResource(R.string.compatibility_saved_label)
                    existingSaved != null -> stringResource(R.string.relationships_update_saved_match)
                    else -> stringResource(R.string.relationships_save_to_relationships)
                },
            )
        }
        if (!useSavedProfile) {
            Text(
                text = stringResource(R.string.relationships_manual_save_note),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun compatibilityModeLabel(mode: CompatibilityMode): String = when (mode) {
    CompatibilityMode.ROMANTIC -> stringResource(R.string.relationship_type_romantic)
    CompatibilityMode.FRIENDSHIP -> stringResource(R.string.relationship_type_friendship)
}

private fun isIsoDate(value: String): Boolean =
    runCatching { LocalDate.parse(value.trim()) }.isSuccess

private fun isIsoTime(value: String): Boolean =
    runCatching { LocalTime.parse(value.trim()) }.isSuccess

private fun buildManualCompatibilityPayload(
    name: String,
    dateOfBirth: String,
    timeOfBirth: String,
): ProfilePayload = ProfilePayload(
    name = name.trim(),
    dateOfBirth = dateOfBirth.trim(),
    timeOfBirth = timeOfBirth.trim().ifBlank { null },
    placeOfBirth = null,
    latitude = null,
    longitude = null,
    timezone = null,
    houseSystem = null,
)
