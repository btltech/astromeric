package com.astromeric.android.feature.profile

import android.content.Context
import android.os.Build
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.BuildConfig
import com.astromeric.android.app.MorningBriefWidgetSnapshot
import com.astromeric.android.app.MorningBriefWidgetSnapshotStore
import com.astromeric.android.core.data.local.CachedExactTransitSnapshot
import com.astromeric.android.core.data.local.SavedExactTransitLoadStatus
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.feature.guide.GuideHealthAvailability
import java.time.Duration
import java.time.LocalTime

@Composable
internal fun SystemDiagnosticsCard(
    selectedProfile: AppProfile?,
    profilesCount: Int,
    fullDataCount: Int,
    localOnlyCount: Int,
    syncedCount: Int,
    hideSensitiveDetailsEnabled: Boolean,
    personalModeEnabled: Boolean,
    isAuthenticated: Boolean,
    notificationsEnabledInSystem: Boolean,
    notificationPermissionGranted: Boolean,
    calendarPermissionGranted: Boolean,
    healthAvailability: GuideHealthAvailability,
    dailyReminderEnabled: Boolean,
    habitReminderEnabled: Boolean,
    timingAlertEnabled: Boolean,
    transitAlertsEnabled: Boolean,
    dailyReadingHour: Int,
    dailyReadingMinute: Int,
    habitReminderHour: Int,
    habitReminderMinute: Int,
    timingAlertHour: Int,
    timingAlertMinute: Int,
    transitAlertHour: Int,
    transitAlertMinute: Int,
    widgetInstanceCount: Int,
    widgetSnapshot: MorningBriefWidgetSnapshot,
    widgetSnapshotStore: MorningBriefWidgetSnapshotStore,
    exactTransitCacheSnapshot: CachedExactTransitSnapshot?,
    exactTransitLoadStatus: SavedExactTransitLoadStatus?,
    exactTransitAlarmAccess: Boolean,
    scheduledTransitHashCount: Int,
    isRunningDebugRefresh: Boolean,
    debugDiagnosticsNote: String?,
    onRefresh: () -> Unit,
    onSeedDebugProfile: (() -> Unit)?,
    onDebugDiagnosticsNoteChange: (String) -> Unit,
    onPreviewExactTransitNotification: (AppProfile, AstroDataSource, Boolean) -> Unit,
    onRunDebugRefresh: (AppProfile) -> Unit,
) {
    val context = LocalContext.current
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = stringResource(R.string.profile_diagnostics_title),
                    style = MaterialTheme.typography.titleMedium,
                )
                TextButton(onClick = onRefresh) {
                    Text(stringResource(R.string.action_refresh))
                }
            }
            Text(
                text = stringResource(R.string.profile_diagnostics_body),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (BuildConfig.DEBUG && onSeedDebugProfile != null) {
                DebugDiagnosticsActions(
                    selectedProfile = selectedProfile,
                    hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                    exactTransitLoadStatus = exactTransitLoadStatus,
                    isRunningDebugRefresh = isRunningDebugRefresh,
                    debugDiagnosticsNote = debugDiagnosticsNote,
                    onSeedDebugProfile = onSeedDebugProfile,
                    onDebugDiagnosticsNoteChange = onDebugDiagnosticsNoteChange,
                    onPreviewExactTransitNotification = onPreviewExactTransitNotification,
                    onRunDebugRefresh = onRunDebugRefresh,
                )
            }
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_notification_delivery_label),
                value = notificationDiagnosticsLabel(context, notificationsEnabledInSystem, notificationPermissionGranted),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_daily_reminder_window_label),
                value = notificationWindowLabel(context, dailyReminderEnabled, dailyReadingHour, dailyReadingMinute),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_habit_reminder_window_label),
                value = notificationWindowLabel(context, habitReminderEnabled, habitReminderHour, habitReminderMinute),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_timing_alert_window_label),
                value = notificationWindowLabel(context, timingAlertEnabled, timingAlertHour, timingAlertMinute),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_transit_alert_window_label),
                value = notificationWindowLabel(context, transitAlertsEnabled, transitAlertHour, transitAlertMinute),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_calendar_permission_label),
                value = if (calendarPermissionGranted) {
                    stringResource(R.string.profile_diagnostics_calendar_permission_granted)
                } else {
                    stringResource(R.string.profile_diagnostics_calendar_permission_not_granted)
                },
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_health_connect_label),
                value = healthAvailability.label(context),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_morning_brief_widgets_label),
                value = if (widgetInstanceCount == 0) {
                    stringResource(R.string.profile_diagnostics_widgets_none_placed)
                } else {
                    stringResource(R.string.profile_diagnostics_widgets_active_count, widgetInstanceCount)
                },
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_widget_cache_label),
                value = widgetSnapshot.cacheStatusLabel(context),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_last_daily_reminder_label),
                value = notificationMarkerLabel(context, widgetSnapshotStore.lastDailyReadingNotificationDate()),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_last_habit_reminder_label),
                value = notificationMarkerLabel(context, widgetSnapshotStore.lastHabitReminderNotificationDate()),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_last_timing_alert_label),
                value = notificationMarkerLabel(context, widgetSnapshotStore.lastTimingAlertNotificationDate()),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_last_transit_alert_label),
                value = notificationMarkerLabel(context, widgetSnapshotStore.lastTransitAlertNotificationDate()),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_exact_transit_alarms_label),
                value = exactTransitAlarmLabel(
                    context,
                    enabled = transitAlertsEnabled,
                    accessGranted = exactTransitAlarmAccess,
                    scheduledCount = scheduledTransitHashCount,
                ),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_exact_transit_cache_label),
                value = exactTransitCacheStatusLabel(context, exactTransitCacheSnapshot),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_exact_transit_source_label),
                value = exactTransitLoadStatusLabel(context, exactTransitLoadStatus),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_selected_profile_label),
                value = selectedProfile?.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)
                    ?: stringResource(R.string.profile_diagnostics_selected_profile_none),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_profile_quality_label),
                value = selectedProfile?.dataQuality?.label
                    ?: stringResource(R.string.profile_diagnostics_profile_quality_none),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_exact_data_profiles_label),
                value = stringResource(
                    R.string.profile_diagnostics_exact_data_profiles_count,
                    fullDataCount,
                    profilesCount,
                ),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_device_only_profiles_label),
                value = localOnlyCount.toString(),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_synced_profiles_label),
                value = syncedCount.toString(),
            )
            ProfileDiagnosticsStatusRow(
                label = stringResource(R.string.profile_diagnostics_account_state_label),
                value = when {
                    personalModeEnabled -> stringResource(R.string.profile_diagnostics_account_state_personal_mode)
                    isAuthenticated -> stringResource(R.string.profile_diagnostics_account_state_signed_in)
                    else -> stringResource(R.string.profile_diagnostics_account_state_signed_out)
                },
            )
        }
    }
}

@Composable
private fun DebugDiagnosticsActions(
    selectedProfile: AppProfile?,
    hideSensitiveDetailsEnabled: Boolean,
    exactTransitLoadStatus: SavedExactTransitLoadStatus?,
    isRunningDebugRefresh: Boolean,
    debugDiagnosticsNote: String?,
    onSeedDebugProfile: () -> Unit,
    onDebugDiagnosticsNoteChange: (String) -> Unit,
    onPreviewExactTransitNotification: (AppProfile, AstroDataSource, Boolean) -> Unit,
    onRunDebugRefresh: (AppProfile) -> Unit,
) {
    val context = LocalContext.current
    OutlinedButton(onClick = onSeedDebugProfile, modifier = Modifier.fillMaxWidth()) {
        Text(stringResource(R.string.profile_diagnostics_debug_seed_profile))
    }
    Text(
        text = stringResource(R.string.profile_diagnostics_debug_body),
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
    OutlinedButton(
        onClick = {
            val profile = selectedProfile
            if (profile == null) {
                onDebugDiagnosticsNoteChange(context.getString(R.string.profile_diagnostics_debug_select_profile_first))
                return@OutlinedButton
            }
            val source = exactTransitLoadStatus?.source ?: AstroDataSource.LOCAL_SWISS
            val isCached = exactTransitLoadStatus?.isCached ?: false
            onPreviewExactTransitNotification(profile, source, isCached)
            onDebugDiagnosticsNoteChange(
                context.getString(
                    R.string.profile_diagnostics_debug_preview_triggered,
                    debugTransitSourceLabel(context, source, isCached),
                ),
            )
        },
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(stringResource(R.string.profile_diagnostics_debug_preview_notification))
    }
    OutlinedButton(
        onClick = {
            val profile = selectedProfile
            if (profile == null || isRunningDebugRefresh) {
                onDebugDiagnosticsNoteChange(context.getString(R.string.profile_diagnostics_debug_select_profile_first))
                return@OutlinedButton
            }
            onRunDebugRefresh(profile)
        },
        enabled = !isRunningDebugRefresh,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(
            if (isRunningDebugRefresh) {
                stringResource(R.string.profile_diagnostics_debug_running_refresh)
            } else {
                stringResource(R.string.profile_diagnostics_debug_run_refresh)
            },
        )
    }
    debugDiagnosticsNote?.let { note ->
        Text(
            text = note,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun ProfileDiagnosticsStatusRow(
    label: String,
    value: String,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(text = label, style = MaterialTheme.typography.bodyMedium)
        Text(
            text = value,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

private fun notificationDiagnosticsLabel(
    context: Context,
    notificationsEnabledInSystem: Boolean,
    notificationPermissionGranted: Boolean,
): String = when {
    !notificationsEnabledInSystem -> context.getString(R.string.profile_diagnostics_notifications_disabled_system)
    !notificationPermissionGranted -> context.getString(R.string.profile_diagnostics_notifications_permission_missing)
    else -> context.getString(R.string.profile_diagnostics_notifications_ready)
}

private fun notificationWindowLabel(
    context: Context,
    enabled: Boolean,
    hour: Int,
    minute: Int,
): String = if (enabled) LocalTime.of(hour, minute).format(java.time.format.DateTimeFormatter.ofPattern("h:mm a")) else context.getString(R.string.preference_state_off)

private fun notificationMarkerLabel(context: Context, date: String?): String =
    date ?: context.getString(R.string.profile_diagnostics_not_delivered_yet)

private fun exactTransitAlarmLabel(
    context: Context,
    enabled: Boolean,
    accessGranted: Boolean,
    scheduledCount: Int,
): String = when {
    !enabled -> context.getString(R.string.preference_state_off)
    !accessGranted -> context.getString(R.string.profile_diagnostics_exact_alarm_access_required)
    scheduledCount == 0 -> context.getString(R.string.profile_diagnostics_exact_alarm_none)
    else -> context.getString(R.string.profile_diagnostics_exact_alarm_scheduled_count, scheduledCount)
}

private fun GuideHealthAvailability.label(context: Context): String = when (this) {
    GuideHealthAvailability.AVAILABLE -> context.getString(R.string.profile_diagnostics_health_available)
    GuideHealthAvailability.UPDATE_REQUIRED -> context.getString(R.string.profile_diagnostics_health_update_required)
    GuideHealthAvailability.UNAVAILABLE -> context.getString(R.string.profile_diagnostics_health_unavailable)
}

private fun MorningBriefWidgetSnapshot.cacheStatusLabel(context: Context): String {
    val updatedAt = lastUpdatedEpochMillis ?: return context.getString(R.string.profile_diagnostics_widget_cache_none)
    val elapsed = Duration.ofMillis((System.currentTimeMillis() - updatedAt).coerceAtLeast(0L))
    val ageLabel = when {
        elapsed.toMinutes() < 1 -> context.getString(R.string.profile_diagnostics_widget_cache_updated_just_now)
        elapsed.toHours() < 1 -> context.getString(R.string.profile_diagnostics_widget_cache_updated_minutes, elapsed.toMinutes())
        elapsed.toHours() < 24 -> context.getString(R.string.profile_diagnostics_widget_cache_updated_hours, elapsed.toHours())
        else -> context.getString(R.string.profile_diagnostics_widget_cache_updated_days, elapsed.toDays())
    }
    return if (greeting.isNotBlank() || vibe.isNotBlank() || personalDay != null) {
        context.getString(R.string.profile_diagnostics_widget_cache_ready, ageLabel)
    } else {
        context.getString(R.string.profile_diagnostics_widget_cache_seeded_fallback, ageLabel)
    }
}

private fun debugTransitSourceLabel(
    context: Context,
    source: AstroDataSource,
    isCached: Boolean,
): String = when {
    isCached && source == AstroDataSource.LOCAL_SWISS -> context.getString(R.string.profile_exact_transit_source_cached_swiss)
    isCached && source == AstroDataSource.LOCAL_ESTIMATE -> context.getString(R.string.profile_exact_transit_source_cached_local_estimate)
    isCached -> context.getString(R.string.profile_exact_transit_source_cached_backend)
    source == AstroDataSource.LOCAL_SWISS -> context.getString(R.string.profile_exact_transit_source_on_device_swiss)
    source == AstroDataSource.LOCAL_ESTIMATE -> context.getString(R.string.profile_exact_transit_source_local_estimate)
    else -> context.getString(R.string.profile_exact_transit_source_backend)
}