package com.astromeric.android.feature.tools

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
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
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.YesNoGuidanceData
import com.astromeric.android.core.model.displayName
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OracleScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onBack: () -> Unit,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()
    var question by remember { mutableStateOf("") }
    var isConsulting by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var guidance by remember { mutableStateOf<YesNoGuidanceData?>(null) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Oracle") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
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
                        Text("A profile is needed to consult the oracle.", style = MaterialTheme.typography.bodyMedium)
                        Button(onClick = onOpenProfile) { Text("Open Profile") }
                    }
                }
                return@Column
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Ask the Oracle", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                    Text(
                        "Frame a clear yes or no question and let the sky weigh in.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    OutlinedTextField(
                        value = question,
                        onValueChange = { question = it },
                        label = { Text("Your question") },
                        placeholder = { Text("Will this decision serve me well?") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = false,
                        maxLines = 3,
                    )
                    Button(
                        onClick = {
                            val q = question.trim()
                            if (q.isBlank()) return@Button
                            scope.launch {
                                isConsulting = true
                                errorMessage = null
                                guidance = null
                                guidance = remoteDataSource.fetchYesNoGuidance(q, selectedProfile)
                                    .onFailure { errorMessage = it.message ?: "Oracle could not respond." }
                                    .getOrNull()
                                isConsulting = false
                            }
                        },
                        enabled = question.isNotBlank() && !isConsulting,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(if (isConsulting) "Consulting..." else "Consult Oracle")
                    }
                }
            }

            if (isConsulting) {
                LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
            }

            errorMessage?.let { error ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Oracle Silent", style = MaterialTheme.typography.titleSmall)
                        Text(error, style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }

            AnimatedContent(
                targetState = guidance,
                transitionSpec = { fadeIn() togetherWith fadeOut() },
                label = "OracleResult",
            ) { g ->
                if (g != null) {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Column(
                                modifier = Modifier.padding(20.dp),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.spacedBy(10.dp),
                            ) {
                                Text(
                                    text = if (g.answer.equals("yes", ignoreCase = true)) "Yes ✨" else "No 🌑",
                                    style = MaterialTheme.typography.displaySmall,
                                    textAlign = TextAlign.Center,
                                    color = if (g.answer.equals("yes", ignoreCase = true)) MaterialTheme.colorScheme.primary
                                    else MaterialTheme.colorScheme.error,
                                )
                                Text(
                                    text = "${(g.confidence * 100).roundToInt()}% confidence",
                                    style = MaterialTheme.typography.labelLarge,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        }
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text("Question", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                Text(g.question, style = MaterialTheme.typography.bodyMedium)
                                Text("Reading", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
                                Text(g.reasoning, style = MaterialTheme.typography.bodyMedium)
                                if (g.guidance.isNotEmpty()) {
                                    Text("Guidance", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
                                    g.guidance.forEach { item ->
                                        Text("• $item", style = MaterialTheme.typography.bodySmall)
                                    }
                                }
                            }
                        }
                        OutlinedButton(
                            onClick = { guidance = null; question = "" },
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Ask Another Question")
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
