package com.astromeric.android.feature.tools

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import com.astromeric.android.core.model.TarotCardData

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TarotScreen(
    remoteDataSource: AstroRemoteDataSource,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var drawVersion by remember { mutableIntStateOf(0) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var card by remember { mutableStateOf<TarotCardData?>(null) }
    var revealed by remember(drawVersion) { mutableStateOf(false) }

    LaunchedEffect(drawVersion) {
        isLoading = true
        errorMessage = null
        revealed = false
        card = null
        card = remoteDataSource.drawTarotCard()
            .onFailure { errorMessage = it.message ?: "Tarot card could not be drawn." }
            .getOrNull()
        isLoading = false
        if (card != null) revealed = true
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Tarot") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { drawVersion += 1 }, enabled = !isLoading) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Draw new card")
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
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = "Draw a card to receive a symbolic reflection for today.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )

            if (isLoading) {
                LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                return@Column
            }

            errorMessage?.let { error ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Draw Failed", style = MaterialTheme.typography.titleSmall)
                        Text(error, style = MaterialTheme.typography.bodyMedium)
                        OutlinedButton(onClick = { drawVersion += 1 }) { Text("Try Again") }
                    }
                }
                return@Column
            }

            AnimatedVisibility(
                visible = revealed && card != null,
                enter = fadeIn(tween(600)) + slideInVertically(tween(600), initialOffsetY = { it / 2 }),
                exit = fadeOut(),
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    // Card identity header
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(20.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Text(
                                text = card?.name.orEmpty(),
                                style = MaterialTheme.typography.headlineMedium,
                                fontWeight = FontWeight.Bold,
                                textAlign = TextAlign.Center,
                            )
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                card?.suit?.takeIf { it.isNotBlank() }?.let { suit ->
                                    AssistChip(
                                        onClick = {},
                                        label = { Text(suit.replaceFirstChar(Char::uppercase)) },
                                    )
                                }
                                AssistChip(
                                    onClick = {},
                                    label = {
                                        Text(if (card?.upright == true) "Upright" else "Reversed")
                                    },
                                )
                                card?.number?.takeIf { it > 0 }?.let { num ->
                                    AssistChip(onClick = {}, label = { Text("#$num") })
                                }
                            }
                        }
                    }

                    // Meaning
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Meaning", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.primary)
                            Text(card?.meaning.orEmpty(), style = MaterialTheme.typography.bodyMedium)
                        }
                    }

                    // Interpretation
                    card?.interpretation?.takeIf { it.isNotBlank() }?.let { interpretation ->
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text("Reflection", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.primary)
                                Text(interpretation, style = MaterialTheme.typography.bodyMedium)
                            }
                        }
                    }

                    OutlinedButton(
                        onClick = { drawVersion += 1 },
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("Draw Another Card")
                    }
                }
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
