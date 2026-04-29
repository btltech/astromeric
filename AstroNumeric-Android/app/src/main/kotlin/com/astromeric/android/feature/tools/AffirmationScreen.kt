package com.astromeric.android.feature.tools

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AffirmationData
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AffirmationScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onBack: () -> Unit,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var affirmation by remember(selectedProfile?.id) { mutableStateOf<AffirmationData?>(null) }
    var revealed by remember(selectedProfile?.id, refreshVersion) { mutableStateOf(false) }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile ?: run {
            affirmation = null
            revealed = false
            return@LaunchedEffect
        }
        isLoading = true
        errorMessage = null
        revealed = false
        affirmation = remoteDataSource.fetchAffirmation(profile)
            .onFailure { errorMessage = it.message ?: "Affirmation could not be loaded." }
            .getOrNull()
        isLoading = false
        if (affirmation != null) revealed = true
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Affirmation") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { refreshVersion += 1 }, enabled = !isLoading) {
                        Icon(Icons.Filled.Refresh, contentDescription = "New affirmation")
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
                .padding(horizontal = 24.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            if (selectedProfile == null) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Profile Required", style = MaterialTheme.typography.titleSmall)
                        Text("A profile is needed to personalise your affirmation.", style = MaterialTheme.typography.bodyMedium)
                        Button(onClick = onOpenProfile) { Text("Open Profile") }
                    }
                }
                return@Column
            }

            Text(
                text = selectedProfile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            if (isLoading) {
                LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                return@Column
            }

            errorMessage?.let { error ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Could Not Load", style = MaterialTheme.typography.titleSmall)
                        Text(error, style = MaterialTheme.typography.bodyMedium)
                        OutlinedButton(onClick = { refreshVersion += 1 }) { Text("Retry") }
                    }
                }
                return@Column
            }

            Spacer(modifier = Modifier.height(24.dp))

            AnimatedVisibility(
                visible = revealed && affirmation != null,
                enter = fadeIn() + slideInVertically(initialOffsetY = { it / 3 }),
                exit = fadeOut(),
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                ) {
                    Icon(
                        imageVector = Icons.Filled.AutoAwesome,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.height(48.dp),
                    )
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                        ) {
                            Text(
                                text = affirmation?.affirmation.orEmpty(),
                                style = MaterialTheme.typography.headlineSmall,
                                textAlign = TextAlign.Center,
                                fontWeight = FontWeight.Medium,
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            if (!isLoading && affirmation != null) {
                OutlinedButton(onClick = { refreshVersion += 1 }) {
                    Text("New Affirmation")
                }
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
