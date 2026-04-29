package com.astromeric.android.feature.tools

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
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
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AffirmationData
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DoDontData
import com.astromeric.android.core.model.MorningBriefData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun DailyFeaturesScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onBack: () -> Unit,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var morningBrief by remember(selectedProfile?.id) { mutableStateOf<MorningBriefData?>(null) }
    var doDont by remember(selectedProfile?.id) { mutableStateOf<DoDontData?>(null) }
    var affirmation by remember(selectedProfile?.id) { mutableStateOf<AffirmationData?>(null) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile ?: run {
            morningBrief = null
            doDont = null
            affirmation = null
            isLoading = false
            return@LaunchedEffect
        }
        isLoading = true
        errorMessage = null
        coroutineScope {
            val briefRequest = async { remoteDataSource.fetchMorningBrief(profile) }
            val doDontRequest = async { remoteDataSource.fetchDoDont(profile) }
            val affirmationRequest = async { remoteDataSource.fetchAffirmation(profile) }

            morningBrief = briefRequest.await()
                .onFailure { errorMessage = it.message ?: "Morning brief could not be loaded." }
                .getOrNull()

            doDont = doDontRequest.await().getOrNull()
            affirmation = affirmationRequest.await().getOrNull()
        }
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Daily Features") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(
                        onClick = { refreshVersion += 1 },
                        enabled = !isLoading,
                    ) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Refresh")
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
                        Text(text = "Profile Required", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
                        Text(
                            text = "Create or select a profile to load your personalized daily features.",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Button(onClick = onOpenProfile) { Text("Open Profile") }
                    }
                }
                return@Column
            }

            AssistChip(
                onClick = {},
                label = {
                    Text(selectedProfile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER))
                },
            )

            if (isLoading && morningBrief == null) {
                repeat(3) { LinearProgressIndicator(modifier = Modifier.fillMaxWidth()) }
                return@Column
            }

            // Morning Brief card
            morningBrief?.let { brief ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text(
                            text = "Morning Brief",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold,
                        )
                        brief.greeting?.takeIf { it.isNotBlank() }?.let { greeting ->
                            Text(text = greeting, style = MaterialTheme.typography.bodyLarge)
                        }
                        if (brief.bullets.isNotEmpty()) {
                            HorizontalDivider()
                            brief.bullets.forEach { bullet ->
                                Row(
                                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                                    verticalAlignment = Alignment.Top,
                                ) {
                                    bullet.emoji?.let { emoji ->
                                        Text(text = emoji, style = MaterialTheme.typography.bodyMedium)
                                    }
                                    Text(text = bullet.text, style = MaterialTheme.typography.bodyMedium)
                                }
                            }
                        }
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            brief.personalDay?.let { day ->
                                AssistChip(onClick = {}, label = { Text("Personal Day $day") })
                            }
                            brief.moonPhase?.takeIf { it.isNotBlank() }?.let { phase ->
                                AssistChip(onClick = {}, label = { Text("🌙 $phase") })
                            }
                            brief.vibe?.takeIf { it.isNotBlank() }?.let { vibe ->
                                AssistChip(onClick = {}, label = { Text(vibe) })
                            }
                        }
                    }
                }
            }

            // Do & Don't card
            doDont?.let { dd ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text(
                            text = "Do & Don't",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold,
                        )
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            if (dd.mercuryRetrograde) {
                                AssistChip(onClick = {}, label = { Text("☿ Mercury Rx") })
                            }
                            if (dd.venusRetrograde) {
                                AssistChip(onClick = {}, label = { Text("♀ Venus Rx") })
                            }
                        }
                        if (dd.dos.isNotEmpty()) {
                            Text(
                                text = "Do",
                                style = MaterialTheme.typography.labelLarge,
                                color = MaterialTheme.colorScheme.primary,
                            )
                            dd.dos.forEach { item ->
                                Text(text = "✓ $item", style = MaterialTheme.typography.bodyMedium)
                            }
                        }
                        if (dd.donts.isNotEmpty()) {
                            Text(
                                text = "Avoid",
                                style = MaterialTheme.typography.labelLarge,
                                color = MaterialTheme.colorScheme.error,
                            )
                            dd.donts.forEach { item ->
                                Text(text = "✕ $item", style = MaterialTheme.typography.bodyMedium)
                            }
                        }
                    }
                }
            }

            // Affirmation card
            affirmation?.let { af ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            text = "Today's Affirmation",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold,
                        )
                        Text(
                            text = "✨ ${af.affirmation}",
                            style = MaterialTheme.typography.bodyLarge,
                        )
                    }
                }
            }

            errorMessage?.let { error ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(text = "Partial Load", style = MaterialTheme.typography.titleSmall)
                        Text(text = error, style = MaterialTheme.typography.bodySmall)
                        OutlinedButton(onClick = { refreshVersion += 1 }) { Text("Retry") }
                    }
                }
            }

            if (morningBrief == null && doDont == null && affirmation == null && !isLoading) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "Nothing loaded yet. Tap refresh to try again.",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        OutlinedButton(onClick = { refreshVersion += 1 }) { Text("Refresh") }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}
