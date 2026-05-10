package com.astromeric.android.feature.relationships

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.FriendCompatibilityData
import com.astromeric.android.core.model.FriendProfileData
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FriendsScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    onBack: () -> Unit,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()
    val friendsLoadError = stringResource(R.string.friends_error_load)
    val friendAddError = stringResource(R.string.friends_error_add)
    val friendRemoveError = stringResource(R.string.friends_error_remove)
    val screenTitle = stringResource(R.string.relationships_section_cosmic_circle)
    val backDescription = stringResource(R.string.action_back)
    val refreshDescription = stringResource(R.string.action_refresh)
    val addFriendDescription = stringResource(R.string.relationships_add_friend)
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var friends by remember(selectedProfile?.id) { mutableStateOf<List<FriendProfileData>>(emptyList()) }
    var compatibilities by remember(selectedProfile?.id) { mutableStateOf<List<FriendCompatibilityData>>(emptyList()) }
    var refreshVersion by remember(selectedProfile?.id) { mutableStateOf(0) }
    var showAddSheet by remember { mutableStateOf(false) }
    val addSheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    val ownerId = selectedProfile?.id?.toString().orEmpty()

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        if (ownerId.isBlank()) return@LaunchedEffect
        isLoading = true
        errorMessage = null
        coroutineScope {
            val friendsDeferred = async { remoteDataSource.listFriends(ownerId) }
            val friendsResult = friendsDeferred.await()
            friendsResult.onFailure { errorMessage = it.message ?: friendsLoadError }
            friends = friendsResult.getOrDefault(emptyList())

            if (selectedProfile != null && friends.isNotEmpty()) {
                val compatResult = async { remoteDataSource.compareAllFriends(ownerId, selectedProfile) }
                compatibilities = compatResult.await().getOrDefault(emptyList())
            }
        }
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(screenTitle) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = backDescription)
                    }
                },
                actions = {
                    IconButton(onClick = { refreshVersion += 1 }, enabled = !isLoading) {
                        Icon(Icons.Filled.Refresh, contentDescription = refreshDescription)
                    }
                    IconButton(onClick = { showAddSheet = true }) {
                        Icon(Icons.Filled.Add, contentDescription = addFriendDescription)
                    }
                },
            )
        },
        modifier = modifier,
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            if (selectedProfile == null) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(stringResource(R.string.status_profile_required), style = MaterialTheme.typography.titleSmall)
                        Text(stringResource(R.string.friends_profile_required_body), style = MaterialTheme.typography.bodyMedium)
                        Button(onClick = onOpenProfile) { Text(stringResource(R.string.action_open_profile)) }
                    }
                }
                return@Column
            }

            if (isLoading) {
                LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
            }

            errorMessage?.let { error ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(stringResource(R.string.status_could_not_load), style = MaterialTheme.typography.titleSmall)
                        Text(error, style = MaterialTheme.typography.bodyMedium)
                        Button(onClick = { refreshVersion += 1 }) { Text(stringResource(R.string.action_retry)) }
                    }
                }
            }

            if (!isLoading && friends.isEmpty() && errorMessage == null) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        Text(stringResource(R.string.friends_empty_title), style = MaterialTheme.typography.titleMedium)
                        Text(
                            stringResource(R.string.friends_empty_body),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Button(onClick = { showAddSheet = true }) {
                            Icon(Icons.Filled.Add, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(8.dp))
                            Text(stringResource(R.string.friends_add_first_friend))
                        }
                    }
                }
            }

            if (friends.isNotEmpty()) {
                // Compatibility ranking
                if (compatibilities.isNotEmpty()) {
                    val ranked = compatibilities.sortedByDescending { it.overallScore }
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            Text(stringResource(R.string.friends_rankings_title), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                            ranked.forEach { compat ->
                                FriendCompatibilityRow(compat)
                            }
                        }
                    }
                }

                // Friends list
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text(stringResource(R.string.friends_all_title, friends.size), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                        friends.forEach { friend ->
                            FriendRow(
                                friend = friend,
                                onRemove = {
                                    scope.launch {
                                        remoteDataSource.removeFriend(ownerId, friend.id)
                                            .onSuccess { refreshVersion += 1 }
                                            .onFailure { errorMessage = it.message ?: friendRemoveError }
                                    }
                                },
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }

    if (showAddSheet) {
        AddFriendBottomSheet(
            sheetState = addSheetState,
            onDismiss = { showAddSheet = false },
            onSave = { name, dob, relType, avatar ->
                scope.launch {
                    val newFriend = FriendProfileData(
                        name = name,
                        dateOfBirth = dob,
                        relationshipType = relType,
                        avatarEmoji = avatar,
                    )
                    remoteDataSource.addFriend(ownerId, newFriend)
                        .onSuccess {
                            showAddSheet = false
                            refreshVersion += 1
                        }
                        .onFailure { errorMessage = it.message ?: friendAddError }
                }
            },
        )
    }
}

@Composable
private fun FriendCompatibilityRow(compat: FriendCompatibilityData) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(compat.emoji, style = MaterialTheme.typography.headlineSmall)
        Column(modifier = Modifier.weight(1f)) {
            Text(compat.friendName, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
            Text(
                compat.headline,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                stringResource(
                    R.string.relationships_score_type_line,
                    (compat.overallScore * 100).roundToInt(),
                    relationshipTypeLabel(compat.relationshipType),
                ),
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.primary,
            )
        }
    }
}

@Composable
private fun FriendRow(
    friend: FriendProfileData,
    onRemove: () -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(friend.avatarEmoji, style = MaterialTheme.typography.headlineSmall)
        Column(modifier = Modifier.weight(1f)) {
            Text(friend.name, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
            Text(
                stringResource(
                    R.string.friends_friend_meta,
                    friend.dateOfBirth,
                    relationshipTypeLabel(friend.relationshipType),
                ),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        IconButton(onClick = onRemove) {
            Icon(
                Icons.Filled.Delete,
                contentDescription = stringResource(R.string.friends_remove_content_description, friend.name),
                tint = MaterialTheme.colorScheme.error,
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AddFriendBottomSheet(
    sheetState: androidx.compose.material3.SheetState,
    onDismiss: () -> Unit,
    onSave: (name: String, dob: String, relType: String, avatar: String) -> Unit,
) {
    val avatarOptions = listOf("👤", "👩", "👨", "🧑", "💃", "🕺", "🦋", "🌟", "🔥", "💫")
    val relationshipTypes = listOf("friendship", "romantic", "professional")
    var name by remember { mutableStateOf("") }
    var dob by remember { mutableStateOf("") }
    var relType by remember { mutableStateOf("friendship") }
    var avatar by remember { mutableStateOf("👤") }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp)
                .padding(bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Text(stringResource(R.string.friends_add_sheet_title), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                label = { Text(stringResource(R.string.relationships_name_label)) },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedTextField(
                value = dob,
                onValueChange = { dob = it },
                label = { Text(stringResource(R.string.friends_birth_date_label)) },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            Text(stringResource(R.string.relationships_relationship_type_title), style = MaterialTheme.typography.labelMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                relationshipTypes.forEach { type ->
                    AssistChip(
                        onClick = { relType = type },
                        label = { Text(relationshipTypeLabel(type)) },
                    )
                }
            }
            Text(stringResource(R.string.relationships_avatar_title), style = MaterialTheme.typography.labelMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                avatarOptions.take(6).forEach { emoji ->
                    TextButton(onClick = { avatar = emoji }) {
                        Text(emoji, style = MaterialTheme.typography.titleLarge)
                    }
                }
            }
            Button(
                onClick = {
                    if (name.isNotBlank() && dob.isNotBlank()) {
                        onSave(name.trim(), dob.trim(), relType, avatar)
                    }
                },
                enabled = name.isNotBlank() && dob.isNotBlank(),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(stringResource(R.string.friends_add_to_circle))
            }
        }
    }
}

@Composable
private fun relationshipTypeLabel(type: String): String = when (type) {
    "romantic" -> stringResource(R.string.relationship_type_romantic)
    "professional" -> stringResource(R.string.relationship_type_professional)
    else -> stringResource(R.string.relationship_type_friendship)
}
