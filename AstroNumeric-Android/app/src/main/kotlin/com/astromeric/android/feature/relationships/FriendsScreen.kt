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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.FriendCompatibilityData
import com.astromeric.android.core.model.FriendProfileData
import com.astromeric.android.core.model.friendRelationshipLabel
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
            friendsResult.onFailure { errorMessage = it.message ?: "Could not load friends." }
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
                title = { Text("Cosmic Circle") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { refreshVersion += 1 }, enabled = !isLoading) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Refresh")
                    }
                    IconButton(onClick = { showAddSheet = true }) {
                        Icon(Icons.Filled.Add, contentDescription = "Add friend")
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
                        Text("Profile Required", style = MaterialTheme.typography.titleSmall)
                        Text("A profile is needed to view your Cosmic Circle.", style = MaterialTheme.typography.bodyMedium)
                        Button(onClick = onOpenProfile) { Text("Open Profile") }
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
                        Text("Could Not Load", style = MaterialTheme.typography.titleSmall)
                        Text(error, style = MaterialTheme.typography.bodyMedium)
                        Button(onClick = { refreshVersion += 1 }) { Text("Retry") }
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
                        Text("Your Cosmic Circle is empty", style = MaterialTheme.typography.titleMedium)
                        Text(
                            "Add people whose birth data you know to see cosmic compatibility rankings.",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        Button(onClick = { showAddSheet = true }) {
                            Icon(Icons.Filled.Add, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(8.dp))
                            Text("Add Your First Friend")
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
                            Text("Compatibility Rankings", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                            ranked.forEach { compat ->
                                FriendCompatibilityRow(compat)
                            }
                        }
                    }
                }

                // Friends list
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text("All Friends (${friends.size})", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                        friends.forEach { friend ->
                            FriendRow(
                                friend = friend,
                                onRemove = {
                                    scope.launch {
                                        remoteDataSource.removeFriend(ownerId, friend.id)
                                            .onSuccess { refreshVersion += 1 }
                                            .onFailure { errorMessage = it.message ?: "Could not remove friend." }
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
                        .onFailure { errorMessage = it.message ?: "Could not add friend." }
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
                "${(compat.overallScore * 100).roundToInt()}% · ${friendRelationshipLabel(compat.relationshipType)}",
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
                "${friend.dateOfBirth} · ${friendRelationshipLabel(friend.relationshipType)}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        IconButton(onClick = onRemove) {
            Icon(Icons.Filled.Delete, contentDescription = "Remove ${friend.name}", tint = MaterialTheme.colorScheme.error)
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
            Text("Add to Cosmic Circle", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                label = { Text("Name") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            OutlinedTextField(
                value = dob,
                onValueChange = { dob = it },
                label = { Text("Date of Birth (YYYY-MM-DD)") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            Text("Relationship", style = MaterialTheme.typography.labelMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                relationshipTypes.forEach { type ->
                    AssistChip(
                        onClick = { relType = type },
                        label = { Text(friendRelationshipLabel(type)) },
                    )
                }
            }
            Text("Avatar", style = MaterialTheme.typography.labelMedium)
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
                Text("Add to Circle")
            }
        }
    }
}
