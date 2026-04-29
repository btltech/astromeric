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
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
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
import com.astromeric.android.core.model.friendRelationshipLabel
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
    val averageCompatibilityScore = if (savedRelationships.isEmpty()) 0 else (savedRelationships.sumOf { it.overallScore.toDouble() } / savedRelationships.size).toInt()

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
                    .onFailure { compatibilityError = it.message ?: "Compatibility could not be loaded." }
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
                .onFailure { compatibilityError = it.message ?: "Compatibility could not be loaded." }
                .getOrNull()
        } else {
            null
        }
    }

    LaunchedEffect(selectedProfile?.id, selectedComparisonProfileId) {
        relationshipTimingError = null
        relationshipTiming = if (selectedProfile != null) {
            remoteDataSource.fetchRelationshipTiming(selectedProfile, comparisonProfile)
                .onFailure { relationshipTimingError = it.message ?: "Relationship timing could not be loaded." }
                .getOrNull()
        } else {
            null
        }

        relationshipBestDays = if (selectedProfile != null) {
            remoteDataSource.fetchRelationshipBestDays(selectedProfile)
                .onFailure {
                    relationshipTimingError = relationshipTimingError ?: it.message ?: "Best relationship days could not be loaded."
                }
                .getOrNull()
        } else {
            null
        }
    }

    LaunchedEffect(selectedProfile?.id) {
        relationshipGuideError = null
        relationshipEvents = remoteDataSource.fetchRelationshipEvents(selectedProfile)
            .onFailure { relationshipGuideError = it.message ?: "Relationship events could not be loaded." }
            .getOrNull()
        relationshipVenusStatus = remoteDataSource.fetchRelationshipVenusStatus()
            .onFailure { relationshipGuideError = relationshipGuideError ?: it.message ?: "Relationship transit status could not be loaded." }
            .getOrNull()
        relationshipPhases = remoteDataSource.fetchRelationshipPhases()
            .onFailure { relationshipGuideError = relationshipGuideError ?: it.message ?: "Relationship phases could not be loaded." }
            .getOrNull()
    }

    LaunchedEffect(selectedProfile?.id, selectedComparisonProfileId) {
        relationshipTimeline = if (selectedProfile != null) {
            remoteDataSource.fetchRelationshipTimeline(selectedProfile, comparisonProfile)
                .onFailure { relationshipGuideError = relationshipGuideError ?: it.message ?: "Relationship timeline could not be loaded." }
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
                .onFailure { friendsError = it.message ?: "Synced friends could not be loaded." }
                .getOrDefault(emptyList())

            friendCompatibilities = remoteDataSource.compareAllFriends(ownerId, selectedProfile)
                .onFailure { friendsError = friendsError ?: it.message ?: "Friend compatibility could not be loaded." }
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
            eyebrow = "Relationships",
            title = "Relationship Studio",
            body = "Keep synced friends, saved compatibility history, and live relationship timing in one place instead of routing that depth through Tools.",
            chips = selectedProfile?.let { profile ->
                listOf(
                    "Active profile: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)} · ${profile.dataQuality.label}",
                )
            }.orEmpty(),
        ) {
            if (selectedProfile == null) {
                Text(
                    text = "Create or select a profile first so compatibility, Cosmic Circle, and relationship timing can personalize correctly.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            } else {
                androidx.compose.material3.TextButton(onClick = onOpenFriends) {
                    Text("Open Cosmic Circle")
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
            title = "Saved relationships",
            error = null,
        ) {
            if (savedRelationships.isNotEmpty()) {
                Text(
                    text = "${savedRelationships.size} saved · ${averageCompatibilityScore}% average score",
                    style = MaterialTheme.typography.bodyMedium,
                )
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    FilterChip(
                        selected = relationshipFilterMode == null,
                        onClick = { relationshipFilterMode = null },
                        label = { Text("All") },
                    )
                    CompatibilityMode.entries.forEach { mode ->
                        FilterChip(
                            selected = relationshipFilterMode == mode,
                            onClick = { relationshipFilterMode = mode },
                            label = { Text(mode.label) },
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
                    text = "Save a compatibility result to build a reusable relationship history.",
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
                        .onFailure { friendsError = it.message ?: "Friend could not be saved." }
                    isSavingFriend = false
                }
            },
            onRemoveFriend = { friendId ->
                scope.launch {
                    val currentOwnerId = ownerId ?: return@launch
                    remoteDataSource.removeFriend(currentOwnerId, friendId)
                        .onFailure { friendsError = it.message ?: "Friend could not be removed." }
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
    RelationshipSectionCard(title = "Compatibility", error = error) {
        if (selectedProfile == null) {
            Text(
                text = "Select a primary profile before calculating compatibility.",
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
                    label = { Text(mode.label) },
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
                    label = { Text("Saved profile") },
                )
                FilterChip(
                    selected = !useSavedProfileForCompatibility,
                    onClick = { onUseSavedProfileForCompatibilityChange(false) },
                    label = { Text("Manual entry") },
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
                    "Choose a second profile to load compatibility."
                } else {
                    "Enter the second person and run the comparison."
                },
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
private fun SavedProfileComparisonPicker(
    comparisonProfiles: List<AppProfile>,
    selectedComparisonProfileId: Int?,
    onSelectedComparisonProfileIdChange: (Int) -> Unit,
    hideSensitiveDetailsEnabled: Boolean,
) {
    if (comparisonProfiles.isEmpty()) {
        Text(
            text = "No secondary saved profiles yet. Use manual entry to compare someone new.",
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
private fun ManualComparisonForm(
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
        label = { Text("Name") },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
    )
    OutlinedTextField(
        value = manualComparisonDateOfBirth,
        onValueChange = onManualComparisonDateOfBirthChange,
        label = { Text("Birth date") },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
        supportingText = { Text("Use YYYY-MM-DD") },
    )
    OutlinedTextField(
        value = manualComparisonTimeOfBirth,
        onValueChange = onManualComparisonTimeOfBirthChange,
        label = { Text("Birth time") },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
        supportingText = { Text("Optional, use HH:MM") },
    )
    Button(onClick = onCalculateManual, enabled = canCalculate) {
        Text("Calculate compatibility")
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
    AssistChip(
        onClick = {},
        label = { Text("${(compatibility.overallScore * 100).toInt()}% ${compatibilityMode.label}") },
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
        Text(
            text = "${dimension.name}: ${(dimension.score * 100).toInt()}%${dimension.interpretation?.let { " · $it" } ?: ""}",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
    if (compatibility.strengths.isNotEmpty()) {
        Text(text = "Strengths: ${compatibility.strengths.joinToString()}", style = MaterialTheme.typography.bodyMedium)
    }
    if (compatibility.recommendations.isNotEmpty()) {
        Text(text = "Recommendations: ${compatibility.recommendations.joinToString()}", style = MaterialTheme.typography.bodyMedium)
    }
    Button(onClick = { onSaveCompatibility(compatibility) }) {
        Text(if (existingSavedRelationship != null) "Update saved match" else "Save to relationships")
    }
    if (!useSavedProfileForCompatibility) {
        Text(
            text = "Manual comparisons save into local relationship history using a private synthetic id derived from the entered name and date.",
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
    RelationshipSectionCard(title = "Cosmic Circle", error = error) {
        if (selectedProfile == null) {
            Text(
                text = "Select a profile before managing synced friends.",
                style = MaterialTheme.typography.bodyMedium,
            )
            return@RelationshipSectionCard
        }

        AssistChip(onClick = {}, label = { Text("${syncedFriends.size} synced friends") })
        Text(
            text = "Friends added here are stored through the backend and ranked separately from your on-device relationship history.",
            style = MaterialTheme.typography.bodyMedium,
        )
        OutlinedTextField(
            value = friendName,
            onValueChange = onFriendNameChange,
            label = { Text("Friend name") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
        )
        OutlinedTextField(
            value = friendDateOfBirth,
            onValueChange = onFriendDateOfBirthChange,
            label = { Text("Date of birth") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            supportingText = { Text("Use YYYY-MM-DD") },
        )
        Text(text = "Relationship type", style = MaterialTheme.typography.titleSmall)
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            relationshipTypes.forEach { type ->
                FilterChip(
                    selected = friendRelationshipType == type,
                    onClick = { onFriendRelationshipTypeChange(type) },
                    label = { Text(friendRelationshipLabel(type)) },
                )
            }
        }
        Text(text = "Avatar", style = MaterialTheme.typography.titleSmall)
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
            Text(if (isSavingFriend) "Adding..." else "Add friend")
        }

        when {
            friendCompatibilities.isNotEmpty() -> {
                Text(text = "Compatibility ranking", style = MaterialTheme.typography.titleSmall)
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
                text = "No synced friends yet.",
                style = MaterialTheme.typography.bodyMedium,
            )

            else -> Text(
                text = "Compatibility rankings are not available yet.",
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
                text = "${relationship.mode.label} · ${(relationship.overallScore * 100).toInt()}% · Updated ${relationship.updatedAt.substringBefore('T')}",
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
                    text = "Strengths: ${relationship.strengths.joinToString()}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Button(onClick = onDelete) {
                Text("Delete")
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
                text = "${friendRelationshipLabel(compatibility.relationshipType)} · ${(compatibility.overallScore).toInt()}%",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = compatibility.headline,
                style = MaterialTheme.typography.bodyMedium,
            )
            if (compatibility.strengths.isNotEmpty()) {
                Text(
                    text = "Strengths: ${compatibility.strengths.joinToString()}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            if (compatibility.recommendations.isNotEmpty()) {
                Text(
                    text = "Nurture: ${compatibility.recommendations.joinToString()}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Button(onClick = onRemove) {
                Text("Remove friend")
            }
        }
    }
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