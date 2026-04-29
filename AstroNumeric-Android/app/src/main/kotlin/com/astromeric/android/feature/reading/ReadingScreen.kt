package com.astromeric.android.feature.reading

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DailyForecastData
import com.astromeric.android.core.model.DataQuality
import com.astromeric.android.core.model.ForecastSectionData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumLoadingCard
import com.astromeric.android.core.ui.PremiumMetricTile
import android.content.Context
import android.content.Intent

private enum class ReadingScope(val wireValue: String, val label: String) {
    DAILY("daily", "Today"),
    WEEKLY("weekly", "This Week"),
    MONTHLY("monthly", "This Month"),
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun ReadingScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onBack: () -> Unit,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var selectedScope by remember { mutableStateOf(ReadingScope.DAILY) }
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id, selectedScope) { mutableStateOf(false) }
    var errorMessage by remember(selectedProfile?.id, selectedScope) { mutableStateOf<String?>(null) }
    var forecast by remember(selectedProfile?.id, selectedScope, refreshVersion) { mutableStateOf<DailyForecastData?>(null) }

    LaunchedEffect(selectedProfile?.id, selectedScope, refreshVersion) {
        val profile = selectedProfile ?: run {
            forecast = null
            isLoading = false
            errorMessage = null
            return@LaunchedEffect
        }
        if (!profile.canRequestForecast) {
            forecast = null
            isLoading = false
            errorMessage = null
            return@LaunchedEffect
        }
        isLoading = true
        errorMessage = null
        forecast = remoteDataSource.fetchForecast(profile, selectedScope.wireValue)
            .onFailure { errorMessage = it.message ?: "Reading could not be loaded." }
            .getOrNull()
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Reading") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    forecast?.let { currentForecast ->
                        IconButton(
                            onClick = {
                                shareReadingForecast(
                                    context = context,
                                    profile = selectedProfile,
                                    forecast = currentForecast,
                                    hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                                )
                            },
                            enabled = !isLoading,
                        ) {
                            Icon(Icons.Filled.Share, contentDescription = "Share")
                        }
                    }
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
            // Scope picker
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                ReadingScope.entries.forEach { scope ->
                    FilterChip(
                        selected = selectedScope == scope,
                        onClick = { selectedScope = scope },
                        label = { Text(scope.label) },
                    )
                }
            }

            if (selectedProfile == null) {
                ReadingInfoCard(
                    title = "Profile Required",
                    body = "Create or select a profile to generate a personalized reading across daily, weekly, and monthly scopes.",
                ) {
                    Button(onClick = onOpenProfile) { Text("Open Profile") }
                }
                return@Column
            }

            if (selectedProfile.dataQuality == DataQuality.DATE_ONLY) {
                ReadingInfoCard(
                    title = "Add Birth Location",
                    body = "A birth location is required for forecast readings. Add it to your profile to unlock ${selectedScope.label.lowercase()} insights.",
                ) {
                    OutlinedButton(onClick = onOpenProfile) { Text("Update Profile") }
                }
                return@Column
            }

            if (!selectedProfile.canRequestForecast) {
                ReadingInfoCard(
                    title = "Add Birth Time",
                    body = "A confirmed birth time and place are required for forecast readings.",
                ) {
                    OutlinedButton(onClick = onOpenProfile) { Text("Update Profile") }
                }
                return@Column
            }

            if (isLoading && forecast == null) {
                repeat(3) { ReadingSkeletonCard() }
                return@Column
            }

            errorMessage?.let { error ->
                ReadingInfoCard(
                    title = "Could Not Load",
                    body = error,
                ) {
                    OutlinedButton(onClick = { refreshVersion += 1 }) { Text("Retry") }
                }
                return@Column
            }

            val data = forecast
            if (data == null) {
                ReadingSkeletonCard()
                return@Column
            }

            // Overall score header
            data.overallScore?.let { score ->
                PremiumContentCard(
                    title = "${selectedScope.label} Overview",
                    body = if (isLoading) "Refreshing..." else null,
                ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                text = "${selectedScope.label} Overview",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold,
                            )
                            Text(
                                text = "${(score * 100).toInt()}%",
                                style = MaterialTheme.typography.headlineSmall,
                                color = MaterialTheme.colorScheme.primary,
                            )
                        }
                        LinearProgressIndicator(
                            progress = { score.coerceIn(0f, 1f) },
                            modifier = Modifier.fillMaxWidth(),
                        )
                        if (isLoading) {
                            Text(
                                text = "Refreshing...",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                }
            }

            // Profile context chip
            selectedProfile.let { profile ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    AssistChip(
                        onClick = {},
                        label = {
                            Text(profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER))
                        },
                    )
                    OutlinedButton(
                        onClick = {
                            shareReadingForecast(
                                context = context,
                                profile = profile,
                                forecast = data,
                                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                            )
                        },
                    ) {
                        Icon(Icons.Filled.Share, contentDescription = null)
                        Text("Share")
                    }
                }
            }

            // Section cards
            data.sections.forEach { section ->
                ReadingSectionCard(section = section)
            }

            if (data.sections.isEmpty() && !isLoading) {
                ReadingInfoCard(
                    title = "No sections",
                    body = "The reading returned no sections. Try refreshing.",
                ) {
                    OutlinedButton(onClick = { refreshVersion += 1 }) { Text("Refresh") }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun ReadingSectionCard(section: ForecastSectionData, modifier: Modifier = Modifier) {
    PremiumContentCard(
        title = section.title,
        body = section.summary,
        modifier = modifier,
    ) {
            if (section.embrace.isNotEmpty()) {
                Text(
                    text = "Embrace",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
                section.embrace.forEach { item ->
                    Text(
                        text = "• $item",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
            if (section.avoid.isNotEmpty()) {
                Text(
                    text = "Avoid",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.error,
                )
                section.avoid.forEach { item ->
                    Text(
                        text = "• $item",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
            if (section.topics.isNotEmpty()) {
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    section.topics.forEach { (topic, score) ->
                        AssistChip(
                            onClick = {},
                            label = { Text("$topic ${(score * 100).toInt()}%") },
                        )
                    }
                }
            }
    }
}

@Composable
private fun ReadingSkeletonCard(modifier: Modifier = Modifier) {
    PremiumLoadingCard(
        title = "Loading reading",
        modifier = modifier,
    )
}

@Composable
private fun ReadingInfoCard(
    title: String,
    body: String,
    modifier: Modifier = Modifier,
    action: (@Composable () -> Unit)? = null,
) {
    PremiumContentCard(
        title = title,
        body = body,
        modifier = modifier,
    ) {
        action?.invoke()
    }
}

private fun shareReadingForecast(
    context: Context,
    profile: AppProfile?,
    forecast: DailyForecastData,
    hideSensitiveDetailsEnabled: Boolean,
) {
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(
            Intent.EXTRA_TEXT,
            buildReadingShareText(
                profile = profile,
                forecast = forecast,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            ),
        )
    }
    context.startActivity(Intent.createChooser(intent, "Share reading"))
}

private fun buildReadingShareText(
    profile: AppProfile?,
    forecast: DailyForecastData,
    hideSensitiveDetailsEnabled: Boolean,
): String = buildString {
    val scopeLabel = forecast.scope
        ?.replaceFirstChar { character ->
            if (character.isLowerCase()) character.titlecase() else character.toString()
        }
        ?: "Daily"
    appendLine("AstroNumeric $scopeLabel Reading")
    appendLine()
    profile?.let {
        appendLine("Profile: ${it.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.SHARE)}")
    }
    forecast.overallScore?.let { score ->
        appendLine("Overall score: ${(score * 100).toInt()}%")
    }
    appendLine()
    forecast.sections.take(3).forEach { section ->
        appendLine(section.title)
        appendLine(section.summary)
        if (section.embrace.isNotEmpty()) {
            appendLine("Embrace: ${section.embrace.take(2).joinToString()}")
        }
        if (section.avoid.isNotEmpty()) {
            appendLine("Avoid: ${section.avoid.take(2).joinToString()}")
        }
        appendLine()
    }
    append("Generated with AstroNumeric")
}
