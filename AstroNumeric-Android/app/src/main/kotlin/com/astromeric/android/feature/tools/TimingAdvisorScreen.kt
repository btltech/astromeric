package com.astromeric.android.feature.tools

import android.content.Context
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
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
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.core.data.local.TimingAdviceCacheStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.loadTimingAdviceWithCacheFallback
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.TimingActivity
import com.astromeric.android.core.model.TimingToolResult
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.toToolResult
import com.astromeric.android.core.ui.PremiumAction
import com.astromeric.android.core.ui.PremiumActionRow
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumHeroCard
import com.astromeric.android.core.ui.PremiumLoadingCard
import com.astromeric.android.core.ui.PremiumStatusCard
import com.astromeric.android.core.ui.TimingShareCard
import com.astromeric.android.core.ui.renderComposableToBitmap
import com.astromeric.android.core.ui.shareBitmapCard
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun TimingAdvisorScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onBack: () -> Unit,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val errorFallback = stringResource(R.string.timing_advisor_error_load)
    val timingAdviceCacheStore = remember(context) { TimingAdviceCacheStore(context.applicationContext) }
    var selectedActivity by remember { mutableStateOf<TimingActivity?>(null) }
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var timingResult by remember(selectedProfile?.id) { mutableStateOf<TimingToolResult?>(null) }
    var resultIsCached by remember(selectedProfile?.id) { mutableStateOf(false) }
    var cachedAtEpochMillis by remember(selectedProfile?.id) { mutableStateOf<Long?>(null) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }

    LaunchedEffect(selectedProfile?.id, selectedActivity, refreshVersion) {
        val profile = selectedProfile
        val activity = selectedActivity
        timingResult = null
        resultIsCached = false
        cachedAtEpochMillis = null
        errorMessage = null

        if (profile == null || activity == null) {
            isLoading = false
            return@LaunchedEffect
        }

        isLoading = true
        val result = loadTimingAdviceWithCacheFallback(
            activity = activity,
            profile = profile,
            remoteDataSource = remoteDataSource,
            cacheStore = timingAdviceCacheStore,
        )
        timingResult = result.payload?.toToolResult(activity)
        resultIsCached = result.isCached
        cachedAtEpochMillis = result.cachedAtEpochMillis
        if (timingResult == null) {
            errorMessage = result.errorMessage ?: errorFallback
        }
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.timing_advisor_title)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = stringResource(R.string.action_back))
                    }
                },
                actions = {
                    IconButton(
                        onClick = { refreshVersion += 1 },
                        enabled = !isLoading && selectedActivity != null,
                    ) {
                        Icon(Icons.Filled.Refresh, contentDescription = stringResource(R.string.action_refresh))
                    }
                    val result = timingResult
                    if (result != null) {
                        IconButton(onClick = {
                            shareTimingCard(context, result)
                        }) {
                            Icon(Icons.Filled.Share, contentDescription = stringResource(R.string.action_share))
                        }
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
            PremiumHeroCard(
                eyebrow = stringResource(R.string.timing_advisor_eyebrow),
                title = stringResource(R.string.timing_advisor_hero_title),
                body = stringResource(R.string.timing_advisor_hero_body),
                chips = listOf(
                    stringResource(R.string.timing_advisor_chip_best_windows),
                    stringResource(R.string.timing_advisor_chip_avoid_windows),
                    stringResource(R.string.timing_advisor_chip_practical_tips),
                ),
            ) {
                selectedProfile?.let { profile ->
                    Text(
                        text = profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }

            PremiumContentCard(
                title = stringResource(R.string.timing_advisor_disclaimer_title),
                body = stringResource(R.string.timing_advisor_disclaimer_body),
            )

            if (selectedProfile == null) {
                PremiumContentCard(
                    title = stringResource(R.string.status_profile_required),
                    body = stringResource(R.string.timing_advisor_profile_required_body),
                ) {
                    PremiumActionRow(
                        actions = listOf(
                            PremiumAction(
                                stringResource(R.string.action_open_profile),
                                onOpenProfile,
                                primary = true,
                            ),
                        ),
                    )
                }
                return@Column
            }

            PremiumContentCard(
                title = stringResource(R.string.timing_advisor_choose_moment_title),
                body = stringResource(R.string.timing_advisor_choose_moment_body),
            ) {
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        TimingActivity.entries.forEach { activity ->
                            FilterChip(
                                selected = selectedActivity == activity,
                                onClick = {
                                    selectedActivity = if (selectedActivity == activity) null else activity
                                },
                                label = { Text("${activity.emoji} ${activity.displayName}") },
                            )
                        }
                    }
            }

            if (selectedActivity == null) {
                TimingPreviewCard()
            } else if (isLoading) {
                TimingLoadingCard()
            } else if (errorMessage != null) {
                TimingErrorCard(
                    message = errorMessage.orEmpty(),
                    onRetry = { refreshVersion += 1 },
                )
            } else if (timingResult != null) {
                TimingResultCards(
                    result = timingResult ?: return@Column,
                    isCached = resultIsCached,
                    cachedAtEpochMillis = cachedAtEpochMillis,
                )
            }
        }
    }
}

@Composable
private fun TimingPreviewCard() {
    PremiumContentCard(title = stringResource(R.string.timing_advisor_preview_title)) {
        Text(text = stringResource(R.string.timing_advisor_preview_best_times), style = MaterialTheme.typography.bodyMedium)
        Text(text = stringResource(R.string.timing_advisor_preview_times_to_avoid), style = MaterialTheme.typography.bodyMedium)
        Text(text = stringResource(R.string.timing_advisor_preview_score), style = MaterialTheme.typography.bodyMedium)
        Text(text = stringResource(R.string.timing_advisor_preview_tips), style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun TimingLoadingCard() {
    PremiumLoadingCard(title = stringResource(R.string.timing_advisor_loading_title))
}

@Composable
private fun TimingErrorCard(
    message: String,
    onRetry: () -> Unit,
) {
    PremiumStatusCard(
        title = stringResource(R.string.timing_advisor_error_title),
        message = message,
        isError = true,
        actionLabel = stringResource(R.string.action_try_again),
        onAction = onRetry,
    )
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
private fun TimingResultCards(
    result: TimingToolResult,
    isCached: Boolean,
    cachedAtEpochMillis: Long?,
) {
    val context = LocalContext.current
    PremiumContentCard(title = stringResource(R.string.timing_advisor_result_title, result.activity.displayName)) {
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                AssistChip(
                    onClick = {},
                    label = { Text("${(result.score * 100).toInt()}% ${result.rating}") },
                )
                if (isCached) {
                    AssistChip(onClick = {}, label = { Text(stringResource(R.string.timing_advisor_cached_snapshot)) })
                }
            }
            if (isCached) {
                Text(
                    text = cachedAtEpochMillis?.let { formatTimingCacheTimestamp(context, it) }
                        ?: stringResource(R.string.timing_advisor_saved_snapshot_in_use),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            result.advice.takeIf { it.isNotBlank() }?.let { advice ->
                Text(text = advice, style = MaterialTheme.typography.bodyMedium)
            }
    }

    TimingListCard(
        title = stringResource(R.string.timing_advisor_best_times_title),
        emptyText = stringResource(R.string.timing_advisor_best_times_empty),
        items = result.bestTimes,
    )
    TimingListCard(
        title = stringResource(R.string.timing_advisor_avoid_times_title),
        emptyText = stringResource(R.string.timing_advisor_avoid_times_empty),
        items = result.avoidTimes,
    )
    TimingListCard(
        title = stringResource(R.string.timing_advisor_tips_title),
        emptyText = stringResource(R.string.timing_advisor_tips_empty),
        items = result.tips,
    )
}

@Composable
private fun TimingListCard(
    title: String,
    emptyText: String,
    items: List<String>,
) {
    PremiumContentCard(title = title) {
            if (items.isEmpty()) {
                Text(
                    text = emptyText,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            } else {
                items.forEach { item ->
                    Text(text = item, style = MaterialTheme.typography.bodyMedium)
                }
            }
    }
}

private fun formatTimingCacheTimestamp(context: Context, epochMillis: Long): String {
    val formatted = Instant.ofEpochMilli(epochMillis)
        .atZone(ZoneId.systemDefault())
        .format(DateTimeFormatter.ofPattern("MMM d, HH:mm", Locale.getDefault()))
    return context.getString(R.string.timing_advisor_saved_snapshot_from, formatted)
}

private fun shareTimingCard(context: Context, result: TimingToolResult) {
    val density = context.resources.displayMetrics.density
    val widthPx = (300 * density * 3).toInt()
    val bitmap = renderComposableToBitmap(context, widthPx, 0) {
        TimingShareCard(result = result)
    }
    shareBitmapCard(context, bitmap, filename = "timing_share.png", chooserTitle = "Share Best Timing")
}