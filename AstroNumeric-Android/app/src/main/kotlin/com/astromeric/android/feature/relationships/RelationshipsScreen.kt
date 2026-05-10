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
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
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
import com.astromeric.android.core.model.FriendCompatibilityData
import com.astromeric.android.core.model.FriendLabel
import com.astromeric.android.core.model.FriendProfileData
import com.astromeric.android.core.model.OtherPersonLabel
import com.astromeric.android.core.model.PrivateUserLabel
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.ProfilePayload
import com.astromeric.android.core.model.RelationshipBestDayData
import com.astromeric.android.core.model.RelationshipBestDaysData
import com.astromeric.android.core.model.RelationshipEventData
import com.astromeric.android.core.model.RelationshipEventsData
import com.astromeric.android.core.model.RelationshipFactorData
import com.astromeric.android.core.model.RelationshipPhasesData
import com.astromeric.android.core.model.RelationshipTimelineData
import com.astromeric.android.core.model.RelationshipTimingData
import com.astromeric.android.core.model.RelationshipVenusStatusData
import com.astromeric.android.core.model.SavedRelationshipData
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.manualComparisonProfileId
import com.astromeric.android.core.model.toSavedRelationship
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumHeroCard
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.LocalTime

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun RelationshipsScreen(
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    preferencesStore: AppPreferencesStore,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenFriends: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()
    val relationshipTypes = listOf("friendship", "romantic", "professional")
    val friendEmojis = listOf("👤", "👩", "👨", "🧑", "👫", "💃", "🕺", "🦋", "🌟", "🔥")
    val compatibilityLoadError = stringResource(R.string.relationships_error_compatibility_load)
    val timingLoadError = stringResource(R.string.relationships_error_timing_load)
    val bestDaysLoadError = stringResource(R.string.relationships_error_best_days_load)
    val eventsLoadError = stringResource(R.string.relationships_error_events_load)
    val transitStatusLoadError = stringResource(R.string.relationships_error_transit_status_load)
    val phasesLoadError = stringResource(R.string.relationships_error_phases_load)
    val timelineLoadError = stringResource(R.string.relationships_error_timeline_load)
    val syncedFriendsLoadError = stringResource(R.string.relationships_error_synced_friends_load)
    val friendCompatibilityLoadError = stringResource(R.string.relationships_error_friend_compatibility_load)
    val friendSaveError = stringResource(R.string.relationships_error_friend_save)
    val friendRemoveError = stringResource(R.string.relationships_error_friend_remove)
    val savedRelationships by preferencesStore.savedRelationships.collectAsStateWithLifecycle(initialValue = emptyList())
    val comparisonProfiles = profiles.filter { it.id != selectedProfile?.id }
    var friendsRefreshVersion by remember(selectedProfile?.id) { mutableStateOf(0) }
    var compatibilityMode by remember { mutableStateOf(CompatibilityMode.ROMANTIC) }
    var useSavedProfileForCompatibility by remember(selectedProfile?.id, profiles.size) { mutableStateOf(comparisonProfiles.isNotEmpty()) }
    var relationshipFilterMode by remember { mutableStateOf<CompatibilityMode?>(null) }
    var selectedComparisonProfileId by remember(selectedProfile?.id, profiles.size) { mutableStateOf<Int?>(comparisonProfiles.firstOrNull()?.id) }
    var manualCompatibilityRequestVersion by remember(selectedProfile?.id) { mutableStateOf(0) }
    var manualComparisonName by remember(selectedProfile?.id) { mutableStateOf("") }
    var manualComparisonDateOfBirth by remember(selectedProfile?.id) { mutableStateOf("") }
    var manualComparisonTimeOfBirth by remember(selectedProfile?.id) { mutableStateOf("") }
    var friendName by remember(selectedProfile?.id) { mutableStateOf("") }
    var friendDateOfBirth by remember(selectedProfile?.id) { mutableStateOf("") }
    var friendRelationshipType by remember(selectedProfile?.id) { mutableStateOf("friendship") }
    var friendAvatar by remember(selectedProfile?.id) { mutableStateOf("👤") }
    var isSavingFriend by remember(selectedProfile?.id) { mutableStateOf(false) }
    var syncedFriends by remember(selectedProfile?.id) { mutableStateOf<List<FriendProfileData>>(emptyList()) }
    var friendCompatibilities by remember(selectedProfile?.id) { mutableStateOf<List<FriendCompatibilityData>>(emptyList()) }
    var compatibility by remember(selectedProfile?.id, selectedComparisonProfileId, compatibilityMode) { mutableStateOf<CompatibilityReportData?>(null) }
    var compatibilityError by remember(selectedProfile?.id, selectedComparisonProfileId, compatibilityMode) { mutableStateOf<String?>(null) }
    var friendsError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var relationshipTiming by remember(selectedProfile?.id, selectedComparisonProfileId) { mutableStateOf<RelationshipTimingData?>(null) }
    var relationshipBestDays by remember(selectedProfile?.id) { mutableStateOf<RelationshipBestDaysData?>(null) }
    var relationshipEvents by remember(selectedProfile?.id) { mutableStateOf<RelationshipEventsData?>(null) }
    var relationshipVenusStatus by remember { mutableStateOf<RelationshipVenusStatusData?>(null) }
    var relationshipPhases by remember { mutableStateOf<RelationshipPhasesData?>(null) }
    var relationshipTimeline by remember(selectedProfile?.id, selectedComparisonProfileId) { mutableStateOf<RelationshipTimelineData?>(null) }
    var relationshipTimingError by remember(selectedProfile?.id, selectedComparisonProfileId) { mutableStateOf<String?>(null) }
    var relationshipGuideError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }

    val comparisonProfile = comparisonProfiles.firstOrNull { it.id == selectedComparisonProfileId }
    val compatibilityComparisonProfile = if (useSavedProfileForCompatibility) comparisonProfile else null
    val manualCompatibilityReady = manualComparisonName.trim().isNotBlank() && isIsoDate(manualComparisonDateOfBirth)
    val manualCompatibilityTimeValid = manualComparisonTimeOfBirth.isBlank() || isIsoTime(manualComparisonTimeOfBirth)
    val manualComparisonRelationshipId = if (manualCompatibilityReady) {
        manualComparisonProfileId(manualComparisonName, manualComparisonDateOfBirth)
    } else {
        null
    }
    val ownerId = selectedProfile?.id?.toString()
    val existingSavedRelationship = savedRelationships.firstOrNull {
        it.primaryProfileId == selectedProfile?.id &&
            it.comparisonProfileId == (if (useSavedProfileForCompatibility) compatibilityComparisonProfile?.id else manualComparisonRelationshipId) &&
            it.mode == compatibilityMode
    }
    val filteredRelationships = savedRelationships.filter { relationshipFilterMode == null || it.mode == relationshipFilterMode }
    val averageCompatibilityScore = if (savedRelationships.isEmpty()) 0 else ((savedRelationships.sumOf { it.overallScore.toDouble() } / savedRelationships.size) * 100).toInt()

    LaunchedEffect(selectedProfile?.id, profiles.size) {
        if (comparisonProfiles.none { it.id == selectedComparisonProfileId }) {
            selectedComparisonProfileId = comparisonProfiles.firstOrNull()?.id
        }
        if (comparisonProfiles.isEmpty()) {
            useSavedProfileForCompatibility = false
        }
    }

    LaunchedEffect(useSavedProfileForCompatibility) {
        compatibility = null
        compatibilityError = null
    }

    LaunchedEffect(selectedProfile?.id, selectedComparisonProfileId, compatibilityMode) {
        compatibilityError = null
        if (useSavedProfileForCompatibility) {
            compatibility = if (selectedProfile != null && comparisonProfile != null) {
                remoteDataSource.fetchCompatibility(compatibilityMode, selectedProfile, comparisonProfile)
                    .onFailure { compatibilityError = it.message ?: compatibilityLoadError }
                    .getOrNull()
            } else {
                null
            }
        }
    }

    LaunchedEffect(selectedProfile?.id, compatibilityMode, manualCompatibilityRequestVersion) {
        if (useSavedProfileForCompatibility) {
            return@LaunchedEffect
        }

        compatibilityError = null
        compatibility = if (selectedProfile != null && manualCompatibilityRequestVersion > 0 && manualCompatibilityReady && manualCompatibilityTimeValid) {
            remoteDataSource.fetchCompatibility(
                mode = compatibilityMode,
                personA = selectedProfile,
                personB = buildManualCompatibilityPayload(
                    name = manualComparisonName,
                    dateOfBirth = manualComparisonDateOfBirth,
                    timeOfBirth = manualComparisonTimeOfBirth,
                ),
            )
                .onFailure { compatibilityError = it.message ?: compatibilityLoadError }
                .getOrNull()
        } else {
            null
        }
    }

    LaunchedEffect(selectedProfile?.id, selectedComparisonProfileId) {
        relationshipTimingError = null
        relationshipTiming = if (selectedProfile != null) {
            remoteDataSource.fetchRelationshipTiming(selectedProfile, comparisonProfile)
                .onFailure { relationshipTimingError = it.message ?: timingLoadError }
                .getOrNull()
        } else {
            null
        }

        relationshipBestDays = if (selectedProfile != null) {
            remoteDataSource.fetchRelationshipBestDays(selectedProfile)
                .onFailure {
                    relationshipTimingError = relationshipTimingError ?: it.message ?: bestDaysLoadError
                }
                .getOrNull()
        } else {
            null
        }
    }

    LaunchedEffect(selectedProfile?.id) {
        relationshipGuideError = null
        relationshipEvents = remoteDataSource.fetchRelationshipEvents(selectedProfile)
            .onFailure { relationshipGuideError = it.message ?: eventsLoadError }
            .getOrNull()
        relationshipVenusStatus = remoteDataSource.fetchRelationshipVenusStatus()
            .onFailure { relationshipGuideError = relationshipGuideError ?: it.message ?: transitStatusLoadError }
            .getOrNull()
        relationshipPhases = remoteDataSource.fetchRelationshipPhases()
            .onFailure { relationshipGuideError = relationshipGuideError ?: it.message ?: phasesLoadError }
            .getOrNull()
    }

    LaunchedEffect(selectedProfile?.id, selectedComparisonProfileId) {
        relationshipTimeline = if (selectedProfile != null) {
            remoteDataSource.fetchRelationshipTimeline(selectedProfile, comparisonProfile)
                .onFailure { relationshipGuideError = relationshipGuideError ?: it.message ?: timelineLoadError }
                .getOrNull()
        } else {
            null
        }
    }

    LaunchedEffect(selectedProfile?.id, friendsRefreshVersion) {
        friendsError = null
        if (selectedProfile == null || ownerId == null) {
            syncedFriends = emptyList()
            friendCompatibilities = emptyList()
        } else {
            syncedFriends = remoteDataSource.listFriends(ownerId)
                .onFailure { friendsError = it.message ?: syncedFriendsLoadError }
                .getOrDefault(emptyList())

            friendCompatibilities = remoteDataSource.compareAllFriends(ownerId, selectedProfile)
                .onFailure { friendsError = friendsError ?: it.message ?: friendCompatibilityLoadError }
                .getOrDefault(emptyList())
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = stringResource(R.string.relationships_hero_eyebrow),
            title = stringResource(R.string.relationships_hero_title),
            body = stringResource(R.string.relationships_hero_body),
            chips = selectedProfile?.let { profile ->
                listOf(
                    stringResource(
                        R.string.relationships_active_profile_chip,
                        profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                        profile.dataQuality.label,
                    ),
                )
            }.orEmpty(),
        ) {
            if (selectedProfile == null) {
                Text(
                    text = stringResource(R.string.relationships_no_profile_body),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            } else {
                androidx.compose.material3.TextButton(onClick = onOpenFriends) {
                    Text(stringResource(R.string.relationships_open_cosmic_circle))
                }
            }
        }

        CompatibilitySection(
            selectedProfile = selectedProfile,
            error = compatibilityError,
            compatibilityMode = compatibilityMode,
            onCompatibilityModeChange = { compatibilityMode = it },
            comparisonProfiles = comparisonProfiles,
            selectedComparisonProfileId = selectedComparisonProfileId,
            onSelectedComparisonProfileIdChange = { selectedComparisonProfileId = it },
            useSavedProfileForCompatibility = useSavedProfileForCompatibility,
            onUseSavedProfileForCompatibilityChange = { useSavedProfileForCompatibility = it },
            hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            manualComparisonName = manualComparisonName,
            onManualComparisonNameChange = { manualComparisonName = it },
            manualComparisonDateOfBirth = manualComparisonDateOfBirth,
            onManualComparisonDateOfBirthChange = { manualComparisonDateOfBirth = it },
            manualComparisonTimeOfBirth = manualComparisonTimeOfBirth,
            onManualComparisonTimeOfBirthChange = { manualComparisonTimeOfBirth = it },
            manualCompatibilityReady = manualCompatibilityReady,
            manualCompatibilityTimeValid = manualCompatibilityTimeValid,
            onCalculateManual = { manualCompatibilityRequestVersion += 1 },
            compatibility = compatibility,
            existingSavedRelationship = existingSavedRelationship,
            onSaveCompatibility = { currentCompatibility ->
                selectedProfile?.let { primary ->
                    scope.launch {
                        val relationshipToSave = if (useSavedProfileForCompatibility) {
                            compatibilityComparisonProfile?.let { secondary ->
                                currentCompatibility.toSavedRelationship(
                                    primaryProfile = primary,
                                    comparisonProfile = secondary,
                                    mode = compatibilityMode,
                                )
                            }
                        } else {
                            currentCompatibility.toSavedRelationship(
                                primaryProfile = primary,
                                comparisonName = manualComparisonName,
                                comparisonDateOfBirth = manualComparisonDateOfBirth,
                                mode = compatibilityMode,
                            )
                        }
                        relationshipToSave?.let { preferencesStore.saveRelationship(it) }
                    }
                }
            },
        )

        RelationshipOutlookSection(
            comparisonProfile = comparisonProfile,
            hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            relationshipTimingError = relationshipTimingError,
            relationshipGuideError = relationshipGuideError,
            relationshipTiming = relationshipTiming,
            relationshipVenusStatus = relationshipVenusStatus,
            relationshipBestDays = relationshipBestDays,
            relationshipEvents = relationshipEvents,
            relationshipPhases = relationshipPhases,
            relationshipTimeline = relationshipTimeline,
        )

        RelationshipSectionCard(
            title = stringResource(R.string.relationships_saved_title),
            error = null,
        ) {
            if (savedRelationships.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.relationships_saved_summary, savedRelationships.size, averageCompatibilityScore),
                    style = MaterialTheme.typography.bodyMedium,
                )
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    FilterChip(
                        selected = relationshipFilterMode == null,
                        onClick = { relationshipFilterMode = null },
                        label = { Text(stringResource(R.string.relationships_filter_all)) },
                    )
                    CompatibilityMode.entries.forEach { mode ->
                        FilterChip(
                            selected = relationshipFilterMode == mode,
                            onClick = { relationshipFilterMode = mode },
                            label = { Text(compatibilityModeLabel(mode)) },
                        )
                    }
                }
                filteredRelationships.take(6).forEach { relationship ->
                    SavedRelationshipRow(
                        relationship = relationship,
                        hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                        onDelete = {
                            scope.launch {
                                preferencesStore.deleteRelationship(relationship.id)
                            }
                        },
                    )
                }
            } else {
                Text(
                    text = stringResource(R.string.relationships_saved_empty),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }

        CosmicCircleSection(
            selectedProfile = selectedProfile,
            error = friendsError,
            syncedFriends = syncedFriends,
            friendCompatibilities = friendCompatibilities,
            friendName = friendName,
            onFriendNameChange = { friendName = it },
            friendDateOfBirth = friendDateOfBirth,
            onFriendDateOfBirthChange = { friendDateOfBirth = it },
            friendRelationshipType = friendRelationshipType,
            onFriendRelationshipTypeChange = { friendRelationshipType = it },
            friendAvatar = friendAvatar,
            onFriendAvatarChange = { friendAvatar = it },
            relationshipTypes = relationshipTypes,
            friendEmojis = friendEmojis,
            isSavingFriend = isSavingFriend,
            hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            onAddFriend = {
                scope.launch {
                    val currentOwnerId = ownerId ?: return@launch
                    isSavingFriend = true
                    friendsError = null
                    remoteDataSource.addFriend(
                        ownerId = currentOwnerId,
                        friend = FriendProfileData(
                            name = friendName.trim(),
                            dateOfBirth = friendDateOfBirth.trim(),
                            avatarEmoji = friendAvatar,
                            relationshipType = friendRelationshipType,
                        ),
                    )
                        .onSuccess {
                            friendName = ""
                            friendDateOfBirth = ""
                            friendRelationshipType = "friendship"
                            friendAvatar = "👤"
                            friendsRefreshVersion += 1
                        }
                        .onFailure { friendsError = it.message ?: friendSaveError }
                    isSavingFriend = false
                }
            },
            onRemoveFriend = { friendId ->
                scope.launch {
                    val currentOwnerId = ownerId ?: return@launch
                    remoteDataSource.removeFriend(currentOwnerId, friendId)
                        .onFailure { friendsError = it.message ?: friendRemoveError }
                    friendsRefreshVersion += 1
                }
            },
        )
    }
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
private fun CompatibilitySection(
    selectedProfile: AppProfile?,
    error: String?,
    compatibilityMode: CompatibilityMode,
    onCompatibilityModeChange: (CompatibilityMode) -> Unit,
    comparisonProfiles: List<AppProfile>,
    selectedComparisonProfileId: Int?,
    onSelectedComparisonProfileIdChange: (Int) -> Unit,
    useSavedProfileForCompatibility: Boolean,
    onUseSavedProfileForCompatibilityChange: (Boolean) -> Unit,
    hideSensitiveDetailsEnabled: Boolean,
    manualComparisonName: String,
    onManualComparisonNameChange: (String) -> Unit,
    manualComparisonDateOfBirth: String,
    onManualComparisonDateOfBirthChange: (String) -> Unit,
    manualComparisonTimeOfBirth: String,
    onManualComparisonTimeOfBirthChange: (String) -> Unit,
    manualCompatibilityReady: Boolean,
    manualCompatibilityTimeValid: Boolean,
    onCalculateManual: () -> Unit,
    compatibility: CompatibilityReportData?,
    existingSavedRelationship: SavedRelationshipData?,
    onSaveCompatibility: (CompatibilityReportData) -> Unit,
) {
    RelationshipSectionCard(title = stringResource(R.string.relationships_section_compatibility), error = error) {
        if (selectedProfile == null) {
            Text(
                text = stringResource(R.string.relationships_select_primary_profile),
                style = MaterialTheme.typography.bodyMedium,
            )
            return@RelationshipSectionCard
        }

        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            CompatibilityMode.entries.forEach { mode ->
                FilterChip(
                    selected = compatibilityMode == mode,
                    onClick = { onCompatibilityModeChange(mode) },
                    label = { Text(compatibilityModeLabel(mode)) },
                )
            }
        }

        if (comparisonProfiles.isNotEmpty()) {
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                FilterChip(
                    selected = useSavedProfileForCompatibility,
                    onClick = { onUseSavedProfileForCompatibilityChange(true) },
                    label = { Text(stringResource(R.string.relationships_saved_profile)) },
                )
                FilterChip(
                    selected = !useSavedProfileForCompatibility,
                    onClick = { onUseSavedProfileForCompatibilityChange(false) },
                    label = { Text(stringResource(R.string.relationships_manual_entry)) },
                )
            }
        }

        if (useSavedProfileForCompatibility) {
            SavedProfileComparisonPicker(
                comparisonProfiles = comparisonProfiles,
                selectedComparisonProfileId = selectedComparisonProfileId,
                onSelectedComparisonProfileIdChange = onSelectedComparisonProfileIdChange,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            )
        } else {
            ManualComparisonForm(
                manualComparisonName = manualComparisonName,
                onManualComparisonNameChange = onManualComparisonNameChange,
                manualComparisonDateOfBirth = manualComparisonDateOfBirth,
                onManualComparisonDateOfBirthChange = onManualComparisonDateOfBirthChange,
                manualComparisonTimeOfBirth = manualComparisonTimeOfBirth,
                onManualComparisonTimeOfBirthChange = onManualComparisonTimeOfBirthChange,
                canCalculate = manualCompatibilityReady && manualCompatibilityTimeValid,
                onCalculateManual = onCalculateManual,
            )
        }

        val currentCompatibility = compatibility
        if (currentCompatibility != null) {
            CompatibilityResultSummary(
                compatibility = currentCompatibility,
                compatibilityMode = compatibilityMode,
                useSavedProfileForCompatibility = useSavedProfileForCompatibility,
                existingSavedRelationship = existingSavedRelationship,
                onSaveCompatibility = onSaveCompatibility,
            )
        } else {
            Text(
                text = if (useSavedProfileForCompatibility) {
                    stringResource(R.string.relationships_choose_second_profile)
                } else {
                    stringResource(R.string.relationships_enter_second_person)
                },
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
internal fun SavedProfileComparisonPicker(
    comparisonProfiles: List<AppProfile>,
    selectedComparisonProfileId: Int?,
    onSelectedComparisonProfileIdChange: (Int) -> Unit,
    hideSensitiveDetailsEnabled: Boolean,
) {
    if (comparisonProfiles.isEmpty()) {
        Text(
            text = stringResource(R.string.relationships_no_secondary_profiles),
            style = MaterialTheme.typography.bodyMedium,
        )
        return
    }

    FlowRow(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        comparisonProfiles.forEachIndexed { index, profile ->
            FilterChip(
                selected = selectedComparisonProfileId == profile.id,
                onClick = { onSelectedComparisonProfileIdChange(profile.id) },
                label = {
                    Text(
                        profile.displayName(
                            hideSensitive = hideSensitiveDetailsEnabled,
                            role = PrivacyDisplayRole.GENERIC_PROFILE,
                            index = index,
                        ),
                    )
                },
            )
        }
    }
}

@Composable
internal fun ManualComparisonForm(
    manualComparisonName: String,
    onManualComparisonNameChange: (String) -> Unit,
    manualComparisonDateOfBirth: String,
    onManualComparisonDateOfBirthChange: (String) -> Unit,
    manualComparisonTimeOfBirth: String,
    onManualComparisonTimeOfBirthChange: (String) -> Unit,
    canCalculate: Boolean,
    onCalculateManual: () -> Unit,
) {
    OutlinedTextField(
        value = manualComparisonName,
        onValueChange = onManualComparisonNameChange,
        label = { Text(stringResource(R.string.relationships_name_label)) },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
    )
    OutlinedTextField(
        value = manualComparisonDateOfBirth,
        onValueChange = onManualComparisonDateOfBirthChange,
        label = { Text(stringResource(R.string.relationships_birth_date_label)) },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
        supportingText = { Text(stringResource(R.string.relationships_birth_date_hint)) },
    )
    OutlinedTextField(
        value = manualComparisonTimeOfBirth,
        onValueChange = onManualComparisonTimeOfBirthChange,
        label = { Text(stringResource(R.string.relationships_birth_time_label)) },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
        supportingText = { Text(stringResource(R.string.relationships_birth_time_hint)) },
    )
    Button(onClick = onCalculateManual, enabled = canCalculate) {
        Text(stringResource(R.string.relationships_calculate_compatibility))
    }
}

@Composable
private fun CompatibilityResultSummary(
    compatibility: CompatibilityReportData,
    compatibilityMode: CompatibilityMode,
    useSavedProfileForCompatibility: Boolean,
    existingSavedRelationship: SavedRelationshipData?,
    onSaveCompatibility: (CompatibilityReportData) -> Unit,
) {
    val modeLabel = compatibilityModeLabel(compatibilityMode)
    AssistChip(
        onClick = {},
        label = {
            Text(
                stringResource(
                    R.string.relationships_score_mode_chip,
                    (compatibility.overallScore * 100).toInt(),
                    modeLabel,
                ),
            )
        },
    )
    Text(text = compatibility.summary, style = MaterialTheme.typography.bodyMedium)
    compatibility.dataQualityNote?.takeIf { it.isNotBlank() }?.let { note ->
        Text(
            text = note,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
    compatibility.dimensions.take(3).forEach { dimension ->
        val dimensionText = buildString {
            append(stringResource(R.string.relationships_dimension_score, dimension.name, (dimension.score * 100).toInt()))
            dimension.interpretation?.let {
                append(" · ")
                append(it)
            }
        }
        Text(
            text = dimensionText,
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
    Button(onClick = { onSaveCompatibility(compatibility) }) {
        Text(
            if (existingSavedRelationship != null) {
                stringResource(R.string.relationships_update_saved_match)
            } else {
                stringResource(R.string.relationships_save_to_relationships)
            },
        )
    }
    if (!useSavedProfileForCompatibility) {
        Text(
            text = stringResource(R.string.relationships_manual_save_note),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
private fun CosmicCircleSection(
    selectedProfile: AppProfile?,
    error: String?,
    syncedFriends: List<FriendProfileData>,
    friendCompatibilities: List<FriendCompatibilityData>,
    friendName: String,
    onFriendNameChange: (String) -> Unit,
    friendDateOfBirth: String,
    onFriendDateOfBirthChange: (String) -> Unit,
    friendRelationshipType: String,
    onFriendRelationshipTypeChange: (String) -> Unit,
    friendAvatar: String,
    onFriendAvatarChange: (String) -> Unit,
    relationshipTypes: List<String>,
    friendEmojis: List<String>,
    isSavingFriend: Boolean,
    hideSensitiveDetailsEnabled: Boolean,
    onAddFriend: () -> Unit,
    onRemoveFriend: (String) -> Unit,
) {
    RelationshipSectionCard(title = stringResource(R.string.relationships_section_cosmic_circle), error = error) {
        if (selectedProfile == null) {
            Text(
                text = stringResource(R.string.relationships_select_profile_for_friends),
                style = MaterialTheme.typography.bodyMedium,
            )
            return@RelationshipSectionCard
        }

        AssistChip(
            onClick = {},
            label = { Text(stringResource(R.string.relationships_synced_friends_count, syncedFriends.size)) },
        )
        Text(
            text = stringResource(R.string.relationships_backend_friends_note),
            style = MaterialTheme.typography.bodyMedium,
        )
        OutlinedTextField(
            value = friendName,
            onValueChange = onFriendNameChange,
            label = { Text(stringResource(R.string.relationships_friend_name_label)) },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
        )
        OutlinedTextField(
            value = friendDateOfBirth,
            onValueChange = onFriendDateOfBirthChange,
            label = { Text(stringResource(R.string.relationships_birth_date_label)) },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            supportingText = { Text(stringResource(R.string.relationships_birth_date_hint)) },
        )
        Text(text = stringResource(R.string.relationships_relationship_type_title), style = MaterialTheme.typography.titleSmall)
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            relationshipTypes.forEach { type ->
                FilterChip(
                    selected = friendRelationshipType == type,
                    onClick = { onFriendRelationshipTypeChange(type) },
                    label = { Text(relationshipTypeLabel(type)) },
                )
            }
        }
        Text(text = stringResource(R.string.relationships_avatar_title), style = MaterialTheme.typography.titleSmall)
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            friendEmojis.forEach { emoji ->
                FilterChip(
                    selected = friendAvatar == emoji,
                    onClick = { onFriendAvatarChange(emoji) },
                    label = { Text(emoji) },
                )
            }
        }
        Button(
            onClick = onAddFriend,
            enabled = !isSavingFriend && friendName.isNotBlank() && isIsoDate(friendDateOfBirth),
        ) {
            Text(
                if (isSavingFriend) {
                    stringResource(R.string.relationships_adding_friend)
                } else {
                    stringResource(R.string.relationships_add_friend)
                },
            )
        }

        when {
            friendCompatibilities.isNotEmpty() -> {
                Text(text = stringResource(R.string.relationships_compatibility_ranking_title), style = MaterialTheme.typography.titleSmall)
                friendCompatibilities.take(6).forEach { compatibilitySummary ->
                    CosmicCircleRow(
                        compatibility = compatibilitySummary,
                        avatarEmoji = syncedFriends.firstOrNull { it.id == compatibilitySummary.friendId }?.avatarEmoji,
                        hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                        onRemove = { onRemoveFriend(compatibilitySummary.friendId) },
                    )
                }
            }

            syncedFriends.isEmpty() -> Text(
                text = stringResource(R.string.relationships_no_synced_friends),
                style = MaterialTheme.typography.bodyMedium,
            )

            else -> Text(
                text = stringResource(R.string.relationships_no_compatibility_rankings),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
internal fun RelationshipSectionCard(
    title: String,
    error: String?,
    content: @Composable () -> Unit,
) {
    PremiumContentCard(
        title = title,
        body = error,
    ) {
        content()
    }
}

@Composable
private fun SavedRelationshipRow(
    relationship: SavedRelationshipData,
    hideSensitiveDetailsEnabled: Boolean,
    onDelete: () -> Unit,
) {
    val modeLabel = compatibilityModeLabel(relationship.mode)
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = if (hideSensitiveDetailsEnabled) {
                    "$PrivateUserLabel + $OtherPersonLabel"
                } else {
                    "${relationship.primaryName} + ${relationship.comparisonName}"
                },
                style = MaterialTheme.typography.titleSmall,
            )
            Text(
                text = stringResource(
                    R.string.relationships_saved_meta,
                    modeLabel,
                    (relationship.overallScore * 100).toInt(),
                    relationship.updatedAt.substringBefore('T'),
                ),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = relationship.summary,
                style = MaterialTheme.typography.bodyMedium,
            )
            relationship.dataQualityNote?.takeIf { it.isNotBlank() }?.let { note ->
                Text(
                    text = note,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            if (relationship.strengths.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.relationships_strengths, relationship.strengths.joinToString()),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Button(onClick = onDelete) {
                Text(stringResource(R.string.action_delete))
            }
        }
    }
}

@Composable
private fun CosmicCircleRow(
    compatibility: FriendCompatibilityData,
    avatarEmoji: String?,
    hideSensitiveDetailsEnabled: Boolean,
    onRemove: () -> Unit,
) {
    val relationshipLabel = relationshipTypeLabel(compatibility.relationshipType)
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = buildString {
                    avatarEmoji?.let { append("$it ") }
                    append("${compatibility.emoji} ")
                    append(if (hideSensitiveDetailsEnabled) FriendLabel else compatibility.friendName)
                },
                style = MaterialTheme.typography.titleSmall,
            )
            Text(
                text = stringResource(
                    R.string.relationships_score_type_line,
                    (compatibility.overallScore * 100).toInt(),
                    relationshipLabel,
                ),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = compatibility.headline,
                style = MaterialTheme.typography.bodyMedium,
            )
            if (compatibility.strengths.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.relationships_strengths, compatibility.strengths.joinToString()),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            if (compatibility.recommendations.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.relationships_nurture, compatibility.recommendations.joinToString()),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Button(onClick = onRemove) {
                Text(stringResource(R.string.relationships_remove_friend))
            }
        }
    }
}

@Composable
private fun compatibilityModeLabel(mode: CompatibilityMode): String = when (mode) {
    CompatibilityMode.ROMANTIC -> stringResource(R.string.relationship_type_romantic)
    CompatibilityMode.FRIENDSHIP -> stringResource(R.string.relationship_type_friendship)
}

@Composable
private fun relationshipTypeLabel(type: String): String = when (type) {
    "romantic" -> stringResource(R.string.relationship_type_romantic)
    "professional" -> stringResource(R.string.relationship_type_professional)
    else -> stringResource(R.string.relationship_type_friendship)
}

private fun isIsoDate(value: String): Boolean =
    runCatching { LocalDate.parse(value.trim()) }.isSuccess

private fun isIsoTime(value: String): Boolean =
    runCatching { LocalTime.parse(value.trim()) }.isSuccess

private fun buildManualCompatibilityPayload(
    name: String,
    dateOfBirth: String,
    timeOfBirth: String,
): ProfilePayload =
    ProfilePayload(
        name = name.trim(),
        dateOfBirth = dateOfBirth.trim(),
        timeOfBirth = timeOfBirth.trim().ifBlank { null },
        placeOfBirth = null,
        latitude = null,
        longitude = null,
        timezone = null,
        houseSystem = null,
    )