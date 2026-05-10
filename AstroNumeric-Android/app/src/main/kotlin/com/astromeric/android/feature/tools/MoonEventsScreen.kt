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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
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
    val errorFallback = stringResource(R.string.moon_events_error_load)
    var refreshVersion by remember { mutableIntStateOf(0) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var eventsData by remember { mutableStateOf<MoonEventsData?>(null) }

    LaunchedEffect(refreshVersion) {
        isLoading = true
        errorMessage = null
        eventsData = remoteDataSource.fetchUpcomingMoonEvents(days = 60)
            .onFailure { errorMessage = it.message ?: errorFallback }
            .getOrNull()
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.moon_events_title)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = stringResource(R.string.action_back))
                    }
                },
                actions = {
                    IconButton(
                        onClick = { refreshVersion += 1 },
                        enabled = !isLoading,
                    ) {
                        Icon(Icons.Filled.Refresh, contentDescription = stringResource(R.string.action_refresh))
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
                text = stringResource(R.string.moon_events_intro_body),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            if (isLoading && eventsData == null) {
                PremiumLoadingCard(title = stringResource(R.string.moon_events_loading_title))
                return@Column
            }

            errorMessage?.let { error ->
                PremiumStatusCard(
                    title = stringResource(R.string.status_could_not_load),
                    message = error,
                    isError = true,
                    actionLabel = stringResource(R.string.action_retry),
                    onAction = { refreshVersion += 1 },
                )
                return@Column
            }

            val events = eventsData?.events.orEmpty()

            if (events.isEmpty() && !isLoading) {
                PremiumEmptyStateCard(
                    title = stringResource(R.string.moon_events_empty_title),
                    message = stringResource(R.string.moon_events_empty_message),
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
                                    daysRounded == 0 -> stringResource(R.string.moon_events_today)
                                    daysRounded == 1 -> stringResource(R.string.moon_events_tomorrow)
                                    else -> stringResource(R.string.moon_events_in_days, daysRounded)
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
