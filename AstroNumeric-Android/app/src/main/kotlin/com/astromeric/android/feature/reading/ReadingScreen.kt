package com.astromeric.android.feature.reading

import android.content.Context
import androidx.annotation.StringRes
import com.astromeric.android.core.ui.ReadingShareCard
import com.astromeric.android.core.ui.renderComposableToBitmap
import com.astromeric.android.core.ui.shareBitmapCard
import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.Brush
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
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
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
import com.astromeric.android.core.ui.CosmicBackgroundCanvas
import com.astromeric.android.core.ui.MysticModeToggle
import com.astromeric.android.core.ui.TimeScrubber
import com.astromeric.android.core.ui.forecastTone
import java.util.Locale

private enum class ReadingScope(val wireValue: String, @StringRes val labelRes: Int) {
    DAILY("daily", R.string.reading_scope_today),
    WEEKLY("weekly", R.string.reading_scope_this_week),
    MONTHLY("monthly", R.string.reading_scope_this_month),
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
    val haptic = LocalHapticFeedback.current
    val readingLoadError = stringResource(R.string.reading_error_load)
    val screenTitle = stringResource(R.string.reading_title)
    val backDescription = stringResource(R.string.action_back)
    val shareDescription = stringResource(R.string.action_share)
    val refreshDescription = stringResource(R.string.action_refresh)
    val openProfileLabel = stringResource(R.string.action_open_profile)
    val updateProfileLabel = stringResource(R.string.action_update_profile)
    val retryLabel = stringResource(R.string.action_retry)
    var selectedScope by remember { mutableStateOf(ReadingScope.DAILY) }
    var isMystic by remember { mutableStateOf(true) }
    var dayOffset by remember { mutableIntStateOf(0) }
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id, selectedScope, isMystic, dayOffset) { mutableStateOf(false) }
    var errorMessage by remember(selectedProfile?.id, selectedScope, isMystic, dayOffset) { mutableStateOf<String?>(null) }
    var forecast by remember(selectedProfile?.id, selectedScope, isMystic, dayOffset, refreshVersion) { mutableStateOf<DailyForecastData?>(null) }

    LaunchedEffect(selectedProfile?.id, selectedScope, isMystic, dayOffset, refreshVersion) {
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
        forecast = remoteDataSource.fetchForecast(
            profile = profile,
            scope = selectedScope.wireValue,
            tone = isMystic.forecastTone,
            dateOffset = dayOffset,
        )
            .onFailure { errorMessage = it.message ?: readingLoadError }
            .getOrNull()
        isLoading = false
    }

    val selectedScopeLabel = stringResource(selectedScope.labelRes)

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(screenTitle) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = backDescription)
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
                            Icon(Icons.Filled.Share, contentDescription = shareDescription)
                        }
                    }
                    IconButton(
                        onClick = { refreshVersion += 1 },
                        enabled = !isLoading,
                    ) {
                        Icon(Icons.Filled.Refresh, contentDescription = refreshDescription)
                    }
                },
            )
        },
        modifier = modifier,
    ) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize()) {
            CosmicBackgroundCanvas(element = null, modifier = Modifier.matchParentSize())
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
                        onClick = {
                            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                            selectedScope = scope
                        },
                        label = { Text(stringResource(scope.labelRes)) },
                    )
                }
            }

            // Mystic / Mundane toggle
            MysticModeToggle(
                isMystic = isMystic,
                onToggle = { isMystic = it },
            )

            // Time scrubber (only for daily scope)
            if (selectedScope == ReadingScope.DAILY) {
                TimeScrubber(
                    offset = dayOffset,
                    onOffsetChange = { dayOffset = it },
                )
            }

            if (selectedProfile == null) {
                ReadingInfoCard(
                    title = stringResource(R.string.status_profile_required),
                    body = stringResource(R.string.reading_profile_required_body),
                ) {
                    Button(onClick = onOpenProfile) { Text(openProfileLabel) }
                }
                return@Column
            }

            if (selectedProfile.dataQuality == DataQuality.DATE_ONLY) {
                ReadingInfoCard(
                    title = stringResource(R.string.reading_birth_location_title),
                    body = stringResource(
                        R.string.reading_birth_location_body,
                        selectedScopeLabel.lowercase(Locale.getDefault()),
                    ),
                ) {
                    OutlinedButton(onClick = onOpenProfile) { Text(updateProfileLabel) }
                }
                return@Column
            }

            if (!selectedProfile.canRequestForecast) {
                ReadingInfoCard(
                    title = stringResource(R.string.reading_birth_time_title),
                    body = stringResource(R.string.reading_birth_time_body),
                ) {
                    OutlinedButton(onClick = onOpenProfile) { Text(updateProfileLabel) }
                }
                return@Column
            }

            if (isLoading && forecast == null) {
                repeat(3) { ReadingSkeletonCard() }
                return@Column
            }

            errorMessage?.let { error ->
                ReadingInfoCard(
                    title = stringResource(R.string.status_could_not_load),
                    body = error,
                ) {
                    OutlinedButton(onClick = { refreshVersion += 1 }) { Text(retryLabel) }
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
                    title = stringResource(R.string.reading_overview_title, selectedScopeLabel),
                    body = if (isLoading) stringResource(R.string.status_refreshing) else null,
                ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                text = stringResource(R.string.reading_overview_title, selectedScopeLabel),
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
                                text = stringResource(R.string.status_refreshing),
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
                        Text(shareDescription)
                    }
                }
            }

            // TLDR summary box
            data.tldr?.takeIf { it.isNotBlank() }?.let { tldr ->
                TldrCard(text = tldr)
            }

            // Section cards
            data.sections.forEach { section ->
                ReadingSectionCard(section = section)
            }

            if (data.sections.isEmpty() && !isLoading) {
                ReadingInfoCard(
                    title = stringResource(R.string.reading_no_sections_title),
                    body = stringResource(R.string.reading_no_sections_body),
                ) {
                    OutlinedButton(onClick = { refreshVersion += 1 }) { Text(refreshDescription) }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
        } // Box (cosmic bg)
    }
}

@Composable
private fun TldrCard(text: String, modifier: Modifier = Modifier) {
    val primary = MaterialTheme.colorScheme.primary
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.medium,
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.linearGradient(
                        listOf(
                            primary.copy(alpha = 0.18f),
                            primary.copy(alpha = 0.08f),
                        )
                    )
                )
                .padding(horizontal = 20.dp, vertical = 16.dp),
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = stringResource(R.string.reading_tldr_label),
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold,
                    color = primary,
                )
                Text(
                    text = text,
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurface,
                )
            }
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
                    text = stringResource(R.string.section_embrace),
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
                    text = stringResource(R.string.section_avoid),
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
        title = stringResource(R.string.reading_loading),
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
    val density = context.resources.displayMetrics.density
    val widthPx = (300 * density * 3).toInt()  // 3× for high-res
    val bitmap = renderComposableToBitmap(context, widthPx, 0) {
        ReadingShareCard(forecast = forecast)
    }
    shareBitmapCard(
        context = context,
        bitmap = bitmap,
        filename = "reading_share.png",
        chooserTitle = context.getString(R.string.reading_share_chooser_title),
    )
}


