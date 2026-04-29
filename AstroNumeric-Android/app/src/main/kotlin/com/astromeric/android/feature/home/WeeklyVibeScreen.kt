package com.astromeric.android.feature.home

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import android.content.Context
import android.content.Intent
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DailyForecastData
import com.astromeric.android.core.model.DataQuality
import com.astromeric.android.core.model.ForecastSectionData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WeeklyVibeScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onBack: () -> Unit,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    // Weekly forecast — one call with scope="weekly"; sections map to days or themes
    var weeklyForecast by remember(selectedProfile?.id) { mutableStateOf<DailyForecastData?>(null) }

    LaunchedEffect(selectedProfile?.id, refreshVersion) {
        val profile = selectedProfile ?: run {
            weeklyForecast = null
            isLoading = false
            errorMessage = null
            return@LaunchedEffect
        }
        if (!profile.canRequestForecast) {
            weeklyForecast = null
            isLoading = false
            return@LaunchedEffect
        }
        isLoading = true
        errorMessage = null
        weeklyForecast = remoteDataSource.fetchForecast(profile, "weekly")
            .onFailure { errorMessage = it.message ?: "Weekly vibe could not be loaded." }
            .getOrNull()
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Weekly Vibe") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    weeklyForecast?.let { currentForecast ->
                        IconButton(
                            onClick = {
                                shareWeeklyVibe(
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
                    IconButton(onClick = { refreshVersion += 1 }, enabled = !isLoading) {
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
                .padding(vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            if (selectedProfile == null) {
                Column(modifier = Modifier.padding(horizontal = 20.dp)) {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Profile Required", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
                            Text(
                                "Create or select a profile to see your weekly cosmic vibe.",
                                style = MaterialTheme.typography.bodyMedium,
                            )
                            OutlinedButton(onClick = onOpenProfile) { Text("Open Profile") }
                        }
                    }
                }
                return@Column
            }

            if (selectedProfile.dataQuality == DataQuality.DATE_ONLY || !selectedProfile.canRequestForecast) {
                Column(modifier = Modifier.padding(horizontal = 20.dp)) {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Birth Time & Place Required", style = MaterialTheme.typography.titleSmall)
                            Text(
                                "Add your birth time and location to your profile for personalised weekly insights.",
                                style = MaterialTheme.typography.bodyMedium,
                            )
                            OutlinedButton(onClick = onOpenProfile) { Text("Update Profile") }
                        }
                    }
                }
                return@Column
            }

            if (isLoading && weeklyForecast == null) {
                // Skeleton row
                Row(
                    modifier = Modifier
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    repeat(5) {
                        Card(modifier = Modifier.width(140.dp).height(140.dp)) {
                            LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                        }
                    }
                }
                return@Column
            }

            errorMessage?.let { error ->
                Column(modifier = Modifier.padding(horizontal = 20.dp)) {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Could Not Load", style = MaterialTheme.typography.titleSmall)
                            Text(error, style = MaterialTheme.typography.bodyMedium)
                            OutlinedButton(onClick = { refreshVersion += 1 }) { Text("Retry") }
                        }
                    }
                }
                return@Column
            }

            val data = weeklyForecast
            if (data == null) return@Column

            // Overall score header
            data.overallScore?.let { score ->
                Column(modifier = Modifier.padding(horizontal = 20.dp)) {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Text("This Week", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                                Text(
                                    "${(score * 100).toInt()}%",
                                    style = MaterialTheme.typography.headlineSmall,
                                    color = MaterialTheme.colorScheme.primary,
                                )
                            }
                            LinearProgressIndicator(
                                progress = { score.coerceIn(0f, 1f) },
                                modifier = Modifier.fillMaxWidth(),
                            )
                        }
                    }
                }
            }

            Column(modifier = Modifier.padding(horizontal = 20.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        text = selectedProfile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    OutlinedButton(
                        onClick = {
                            shareWeeklyVibe(
                                context = context,
                                profile = selectedProfile,
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

            // Horizontal scroll of section cards
            if (data.sections.isNotEmpty()) {
                LazyRow(
                    contentPadding = PaddingValues(horizontal = 16.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    items(data.sections) { section ->
                        WeeklyVibeSectionCard(section = section)
                    }
                }
            }

            // Full detail section list below the timeline
            if (data.sections.isNotEmpty()) {
                Column(
                    modifier = Modifier.padding(horizontal = 20.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        "Full Breakdown",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(top = 4.dp),
                    )
                    data.sections.forEach { section ->
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text(section.title, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
                                Text(section.summary, style = MaterialTheme.typography.bodyMedium)
                                if (section.embrace.isNotEmpty()) {
                                    Text("Embrace", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
                                    section.embrace.forEach { item ->
                                        Text("• $item", style = MaterialTheme.typography.bodySmall)
                                    }
                                }
                                if (section.avoid.isNotEmpty()) {
                                    Text("Avoid", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.error)
                                    section.avoid.forEach { item ->
                                        Text("• $item", style = MaterialTheme.typography.bodySmall)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
private fun WeeklyVibeSectionCard(section: ForecastSectionData, modifier: Modifier = Modifier) {
    Card(modifier = modifier.width(160.dp)) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = section.title,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.SemiBold,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = section.summary,
                style = MaterialTheme.typography.bodySmall,
                maxLines = 4,
                overflow = TextOverflow.Ellipsis,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

private fun shareWeeklyVibe(
    context: Context,
    profile: AppProfile?,
    forecast: DailyForecastData,
    hideSensitiveDetailsEnabled: Boolean,
) {
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(
            Intent.EXTRA_TEXT,
            buildWeeklyVibeShareText(
                profile = profile,
                forecast = forecast,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            ),
        )
    }
    context.startActivity(Intent.createChooser(intent, "Share weekly vibe"))
}

private fun buildWeeklyVibeShareText(
    profile: AppProfile?,
    forecast: DailyForecastData,
    hideSensitiveDetailsEnabled: Boolean,
): String = buildString {
    appendLine("AstroNumeric Weekly Vibe")
    appendLine()
    profile?.let {
        appendLine("Profile: ${it.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.SHARE)}")
    }
    forecast.overallScore?.let { score ->
        appendLine("Week score: ${(score * 100).toInt()}%")
    }
    appendLine()
    forecast.sections.take(5).forEach { section ->
        appendLine("• ${section.title}: ${section.summary}")
    }
    appendLine()
    append("Generated with AstroNumeric")
}
