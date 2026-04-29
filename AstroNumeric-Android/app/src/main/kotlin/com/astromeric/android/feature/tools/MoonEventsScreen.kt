package com.astromeric.android.feature.tools

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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.MoonEventData
import com.astromeric.android.core.model.MoonEventsData
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumEmptyStateCard
import com.astromeric.android.core.ui.PremiumLoadingCard
import com.astromeric.android.core.ui.PremiumStatusCard
import kotlin.math.roundToInt

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MoonEventsScreen(
    remoteDataSource: AstroRemoteDataSource,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    var refreshVersion by remember { mutableIntStateOf(0) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var eventsData by remember { mutableStateOf<MoonEventsData?>(null) }

    LaunchedEffect(refreshVersion) {
        isLoading = true
        errorMessage = null
        eventsData = remoteDataSource.fetchUpcomingMoonEvents(days = 60)
            .onFailure { errorMessage = it.message ?: "Moon events could not be loaded." }
            .getOrNull()
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Upcoming Moon Events") },
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
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                text = "Track new moons, full moons, and phase milestones over the next two months.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            if (isLoading && eventsData == null) {
                PremiumLoadingCard(title = "Loading moon events")
                return@Column
            }

            errorMessage?.let { error ->
                PremiumStatusCard(
                    title = "Could Not Load",
                    message = error,
                    isError = true,
                    actionLabel = "Retry",
                    onAction = { refreshVersion += 1 },
                )
                return@Column
            }

            val events = eventsData?.events.orEmpty()

            if (events.isEmpty() && !isLoading) {
                PremiumEmptyStateCard(
                    title = "No moon events",
                    message = "No upcoming moon events found.",
                )
                return@Column
            }

            events.forEach { event ->
                MoonEventCard(event = event)
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
private fun MoonEventCard(event: MoonEventData, modifier: Modifier = Modifier) {
    PremiumContentCard(modifier = modifier) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    event.emoji?.let { emoji ->
                        Text(text = emoji, style = MaterialTheme.typography.titleLarge)
                    }
                    Text(
                        text = event.type.replace("_", " ").split(" ")
                            .joinToString(" ") { it.replaceFirstChar(Char::uppercase) },
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold,
                    )
                }
                event.daysAway?.let { days ->
                    val daysRounded = days.roundToInt()
                    AssistChip(
                        onClick = {},
                        label = {
                            Text(
                                text = when {
                                    daysRounded == 0 -> "Today"
                                    daysRounded == 1 -> "Tomorrow"
                                    else -> "In $daysRounded days"
                                },
                            )
                        },
                    )
                }
            }
            Text(
                text = event.date,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            event.sign?.takeIf { it.isNotBlank() }?.let { sign ->
                Text(
                    text = sign.replaceFirstChar(Char::uppercase),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
    }
}
