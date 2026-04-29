package com.astromeric.android.feature.profile

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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.BuildConfig
import com.astromeric.android.app.MorningBriefWidgetSnapshot
import com.astromeric.android.app.MorningBriefWidgetSnapshotStore
import com.astromeric.android.core.data.local.ExactTransitCacheSnapshot
import com.astromeric.android.core.data.local.ExactTransitLoadStatus
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
    exactTransitCacheSnapshot: ExactTransitCacheSnapshot?,
    exactTransitLoadStatus: ExactTransitLoadStatus?,
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
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(text = "System diagnostics", style = MaterialTheme.typography.titleMedium)
                TextButton(onClick = onRefresh) {
                    Text("Refresh")
                }
            }
            Text(
                text = "Use this to sanity-check the local Android surface: permissions, Health Connect availability, and whether widget cache data has actually been seeded.",
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
                label = "Notification delivery",
                value = notificationDiagnosticsLabel(notificationsEnabledInSystem, notificationPermissionGranted),
            )
            ProfileDiagnosticsStatusRow(label = "Daily reminder window", value = notificationWindowLabel(dailyReminderEnabled, dailyReadingHour, dailyReadingMinute))
            ProfileDiagnosticsStatusRow(label = "Habit reminder window", value = notificationWindowLabel(habitReminderEnabled, habitReminderHour, habitReminderMinute))
            ProfileDiagnosticsStatusRow(label = "Timing alert window", value = notificationWindowLabel(timingAlertEnabled, timingAlertHour, timingAlertMinute))
            ProfileDiagnosticsStatusRow(label = "Transit alert window", value = notificationWindowLabel(transitAlertsEnabled, transitAlertHour, transitAlertMinute))
            ProfileDiagnosticsStatusRow(label = "Calendar permission", value = if (calendarPermissionGranted) "Granted" else "Not granted")
            ProfileDiagnosticsStatusRow(label = "Health Connect", value = healthAvailability.label)
            ProfileDiagnosticsStatusRow(label = "Morning Brief widgets", value = if (widgetInstanceCount == 0) "None placed" else "$widgetInstanceCount active")
            ProfileDiagnosticsStatusRow(label = "Widget cache", value = widgetSnapshot.cacheStatusLabel())
            ProfileDiagnosticsStatusRow(label = "Last daily reminder", value = notificationMarkerLabel(widgetSnapshotStore.lastDailyReadingNotificationDate()))
            ProfileDiagnosticsStatusRow(label = "Last habit reminder", value = notificationMarkerLabel(widgetSnapshotStore.lastHabitReminderNotificationDate()))
            ProfileDiagnosticsStatusRow(label = "Last timing alert", value = notificationMarkerLabel(widgetSnapshotStore.lastTimingAlertNotificationDate()))
            ProfileDiagnosticsStatusRow(label = "Last transit alert", value = notificationMarkerLabel(widgetSnapshotStore.lastTransitAlertNotificationDate()))
            ProfileDiagnosticsStatusRow(
                label = "Exact transit alarms",
                value = exactTransitAlarmLabel(
                    enabled = transitAlertsEnabled,
                    accessGranted = exactTransitAlarmAccess,
                    scheduledCount = scheduledTransitHashCount,
                ),
            )
            ProfileDiagnosticsStatusRow(label = "Exact transit cache", value = exactTransitCacheStatusLabel(exactTransitCacheSnapshot))
            ProfileDiagnosticsStatusRow(label = "Last exact transit source", value = exactTransitLoadStatusLabel(exactTransitLoadStatus))
            ProfileDiagnosticsStatusRow(label = "Selected profile", value = selectedProfile?.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER) ?: "None")
            ProfileDiagnosticsStatusRow(label = "Profile quality", value = selectedProfile?.dataQuality?.label ?: "No active profile")
            ProfileDiagnosticsStatusRow(label = "Exact-data profiles", value = "$fullDataCount of $profilesCount")
            ProfileDiagnosticsStatusRow(label = "Device-only profiles", value = localOnlyCount.toString())
            ProfileDiagnosticsStatusRow(label = "Synced profiles", value = syncedCount.toString())
            ProfileDiagnosticsStatusRow(
                label = "Account state",
                value = when {
                    personalModeEnabled -> "Dormant in personal mode"
                    isAuthenticated -> "Signed in"
                    else -> "Signed out"
                },
            )
        }
    }
}

@Composable
private fun DebugDiagnosticsActions(
    selectedProfile: AppProfile?,
    hideSensitiveDetailsEnabled: Boolean,
    exactTransitLoadStatus: ExactTransitLoadStatus?,
    isRunningDebugRefresh: Boolean,
    debugDiagnosticsNote: String?,
    onSeedDebugProfile: () -> Unit,
    onDebugDiagnosticsNoteChange: (String) -> Unit,
    onPreviewExactTransitNotification: (AppProfile, AstroDataSource, Boolean) -> Unit,
    onRunDebugRefresh: (AppProfile) -> Unit,
) {
    OutlinedButton(onClick = onSeedDebugProfile, modifier = Modifier.fillMaxWidth()) {
        Text("Seed Swiss test profile")
    }
    Text(
        text = "Debug-only: creates and selects a local exact-time profile with coordinates and timezone so offline Swiss fallback can be exercised on the emulator.",
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
    OutlinedButton(
        onClick = {
            val profile = selectedProfile
            if (profile == null) {
                onDebugDiagnosticsNoteChange("Select or seed a profile first.")
                return@OutlinedButton
            }
            val source = exactTransitLoadStatus?.source ?: AstroDataSource.LOCAL_SWISS
            val isCached = exactTransitLoadStatus?.isCached ?: false
            onPreviewExactTransitNotification(profile, source, isCached)
            onDebugDiagnosticsNoteChange("Triggered a sample exact-transit notification using ${debugTransitSourceLabel(source, isCached)}.")
        },
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text("Preview exact-transit notification")
    }
    OutlinedButton(
        onClick = {
            val profile = selectedProfile
            if (profile == null || isRunningDebugRefresh) {
                onDebugDiagnosticsNoteChange("Select or seed a profile first.")
                return@OutlinedButton
            }
            onRunDebugRefresh(profile)
        },
        enabled = !isRunningDebugRefresh,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(if (isRunningDebugRefresh) "Running refresh path..." else "Run refresh path now")
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
    notificationsEnabledInSystem: Boolean,
    notificationPermissionGranted: Boolean,
): String = when {
    !notificationsEnabledInSystem -> "Disabled in system settings"
    !notificationPermissionGranted -> "Permission missing"
    else -> "Ready"
}

private fun notificationWindowLabel(
    enabled: Boolean,
    hour: Int,
    minute: Int,
): String = if (enabled) LocalTime.of(hour, minute).format(TimeFormatter) else "Off"

private fun notificationMarkerLabel(date: String?): String = date ?: "Not delivered yet"

private fun exactTransitAlarmLabel(
    enabled: Boolean,
    accessGranted: Boolean,
    scheduledCount: Int,
): String = when {
    !enabled -> "Off"
    !accessGranted -> "Exact alarm access required"
    scheduledCount == 0 -> "No upcoming exact alarms"
    else -> "$scheduledCount scheduled"
}

private val GuideHealthAvailability.label: String
    get() = when (this) {
        GuideHealthAvailability.AVAILABLE -> "Available"
        GuideHealthAvailability.UPDATE_REQUIRED -> "Update required"
        GuideHealthAvailability.UNAVAILABLE -> "Unavailable"
    }

private fun MorningBriefWidgetSnapshot.cacheStatusLabel(): String {
    val updatedAt = lastUpdatedEpochMillis ?: return "No snapshot yet"
    val elapsed = Duration.ofMillis((System.currentTimeMillis() - updatedAt).coerceAtLeast(0L))
    val ageLabel = when {
        elapsed.toMinutes() < 1 -> "updated just now"
        elapsed.toHours() < 1 -> "updated ${elapsed.toMinutes()}m ago"
        elapsed.toHours() < 24 -> "updated ${elapsed.toHours()}h ago"
        else -> "updated ${elapsed.toDays()}d ago"
    }
    return if (greeting.isNotBlank() || vibe.isNotBlank() || personalDay != null) {
        "Ready, $ageLabel"
    } else {
        "Seeded fallback, $ageLabel"
    }
}

private fun debugTransitSourceLabel(
    source: AstroDataSource,
    isCached: Boolean,
): String = when {
    isCached && source == AstroDataSource.LOCAL_SWISS -> "cached Swiss scan"
    isCached && source == AstroDataSource.LOCAL_ESTIMATE -> "cached local estimate"
    isCached -> "cached backend scan"
    source == AstroDataSource.LOCAL_SWISS -> "on-device Swiss scan"
    source == AstroDataSource.LOCAL_ESTIMATE -> "local estimate"
    else -> "backend scan"
}