package com.astromeric.android.feature.profile

import android.Manifest
import android.app.TimePickerDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.app.AstroBackgroundScheduler
import com.astromeric.android.app.ExactTransitAlarmScheduler
import com.astromeric.android.app.PushRegistrationManager
import com.astromeric.android.app.PushRegistrationResult
import com.astromeric.android.core.data.local.ExactTransitCacheStore
import com.astromeric.android.core.data.local.ExactTransitLoadStatusStore
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.core.model.AlertFrequency
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.TimingActivity
import com.astromeric.android.core.ui.PermissionRationaleDialog
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.shouldShowPermissionRationale
import kotlinx.coroutines.launch
import java.time.LocalTime
import java.time.format.DateTimeFormatter

private enum class NotificationPermissionTarget {
    DAILY_READING,
    MOON_EVENTS,
    HABIT_REMINDER,
    TIMING_ALERT,
    TRANSIT_ALERTS,
}

private fun notificationPermissionRationale(target: NotificationPermissionTarget): String = when (target) {
    NotificationPermissionTarget.DAILY_READING ->
        "Daily reading reminders need notification access so AstroNumeric can deliver your morning brief at the time you choose."
    NotificationPermissionTarget.MOON_EVENTS ->
        "Moon event alerts need notification access so AstroNumeric can surface new-moon and full-moon moments without forcing you to open the app."
    NotificationPermissionTarget.HABIT_REMINDER ->
        "Habit reminders need notification access so AstroNumeric can nudge you when your local ritual list still has open items for the day."
    NotificationPermissionTarget.TIMING_ALERT ->
        "Timing alerts need notification access so AstroNumeric can send one focused daily timing nudge instead of making you manually check the screen."
    NotificationPermissionTarget.TRANSIT_ALERTS ->
        "Transit alerts need notification access so AstroNumeric can warn you about upcoming exact aspects and scheduled transit windows."
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun NotificationSettingsScreen(
    preferencesStore: AppPreferencesStore,
    remoteDataSource: AstroRemoteDataSource,
    profileRepository: ProfileRepository,
    pushRegistrationManager: PushRegistrationManager,
    selectedProfile: AppProfile?,
    onShowMessage: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val timeFormatter = remember { DateTimeFormatter.ofPattern("h:mm a") }
    val exactTransitCacheStore = remember(context) { ExactTransitCacheStore(context.applicationContext) }
    val exactTransitLoadStatusStore = remember(context) { ExactTransitLoadStatusStore(context.applicationContext) }
    val exactTransitCacheSnapshot = remember(selectedProfile?.id) {
        selectedProfile?.let { exactTransitCacheStore.read(it.id) }
    }
    val exactTransitLoadStatus = remember(selectedProfile?.id) {
        selectedProfile?.let { exactTransitLoadStatusStore.read(it.id) }
    }
    val canScheduleExactTransitAlarms = remember {
        ExactTransitAlarmScheduler(
            context = context,
            snapshotStore = com.astromeric.android.app.MorningBriefWidgetSnapshotStore(context),
        ).canScheduleExactAlarms()
    }

    val dailyReadingEnabled by preferencesStore.notifyDailyReadingEnabled.collectAsStateWithLifecycle(initialValue = false)
    val moonEventsEnabled by preferencesStore.notifyMoonEventsEnabled.collectAsStateWithLifecycle(initialValue = false)
    val habitReminderEnabled by preferencesStore.notifyHabitReminderEnabled.collectAsStateWithLifecycle(initialValue = false)
    val timingAlertEnabled by preferencesStore.notifyTimingAlertEnabled.collectAsStateWithLifecycle(initialValue = false)
    val transitAlertsEnabled by preferencesStore.notifyTransitAlertEnabled.collectAsStateWithLifecycle(initialValue = false)
    val transitMajorOnly by preferencesStore.transitAlertsMajorOnly.collectAsStateWithLifecycle(initialValue = false)
    val mercuryRetrogradeAlertsEnabled by preferencesStore.mercuryRetrogradeAlertsEnabled.collectAsStateWithLifecycle(initialValue = true)
    val alertFrequency by preferencesStore.alertFrequency.collectAsStateWithLifecycle(initialValue = AlertFrequency.EVERY_RETROGRADE)
    val dailyReadingHour by preferencesStore.dailyReadingHour.collectAsStateWithLifecycle(initialValue = 7)
    val dailyReadingMinute by preferencesStore.dailyReadingMinute.collectAsStateWithLifecycle(initialValue = 0)
    val habitReminderHour by preferencesStore.habitReminderHour.collectAsStateWithLifecycle(initialValue = 20)
    val habitReminderMinute by preferencesStore.habitReminderMinute.collectAsStateWithLifecycle(initialValue = 0)
    val timingAlertHour by preferencesStore.timingAlertHour.collectAsStateWithLifecycle(initialValue = 10)
    val timingAlertMinute by preferencesStore.timingAlertMinute.collectAsStateWithLifecycle(initialValue = 0)
    val transitAlertHour by preferencesStore.transitAlertHour.collectAsStateWithLifecycle(initialValue = 9)
    val transitAlertMinute by preferencesStore.transitAlertMinute.collectAsStateWithLifecycle(initialValue = 0)
    val timingAlertActivity by preferencesStore.timingAlertActivity.collectAsStateWithLifecycle(initialValue = TimingActivity.CREATIVE_WORK)
    val savedTransitEmail by preferencesStore.transitSubscriptionEmail.collectAsStateWithLifecycle(initialValue = "")
    val personalModeEnabled by preferencesStore.personalModeEnabled.collectAsStateWithLifecycle(initialValue = com.astromeric.android.BuildConfig.PERSONAL_MODE)
    val authAccessToken by preferencesStore.authAccessToken.collectAsStateWithLifecycle(initialValue = "")
    val authUserEmail by preferencesStore.authUserEmail.collectAsStateWithLifecycle(initialValue = "")
    var transitEmailDraft by rememberSaveable(savedTransitEmail) { mutableStateOf(savedTransitEmail) }
    var authEmailDraft by rememberSaveable(authUserEmail) { mutableStateOf(authUserEmail) }
    var authPasswordDraft by rememberSaveable { mutableStateOf("") }
    var authInFlight by remember { mutableStateOf(false) }
    val firebaseConfigured = remember { pushRegistrationManager.isFirebaseConfigured() }
    val accountSyncEnabled = !personalModeEnabled && authAccessToken.isNotBlank()

    suspend fun syncAlertPreferencesIfAuthenticated(
        alertsEnabled: Boolean,
        frequency: AlertFrequency,
    ) {
        if (personalModeEnabled) return
        val token = authAccessToken.takeIf { it.isNotBlank() } ?: return
        remoteDataSource.updateAlertPreferences(token, alertsEnabled, frequency)
            .onFailure { error ->
                onShowMessage(error.message ?: "Alert preferences were saved locally but backend sync failed.")
            }
    }

    LaunchedEffect(authAccessToken, personalModeEnabled) {
        if (personalModeEnabled) return@LaunchedEffect
        val token = authAccessToken.takeIf { it.isNotBlank() } ?: return@LaunchedEffect
        remoteDataSource.fetchAlertPreferences(token)
            .onSuccess { remotePrefs ->
                preferencesStore.setMercuryRetrogradeAlertsEnabled(remotePrefs.alertMercuryRetrograde)
                preferencesStore.setAlertFrequency(AlertFrequency.fromWireValue(remotePrefs.alertFrequency))
            }
            .onFailure { error ->
                onShowMessage(error.message ?: "Signed-in alert preferences could not be refreshed.")
            }
    }

    var pendingPermissionTarget by remember { mutableStateOf<NotificationPermissionTarget?>(null) }
    var showNotificationRationaleFor by remember { mutableStateOf<NotificationPermissionTarget?>(null) }
    val notificationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
    ) { granted ->
        val target = pendingPermissionTarget ?: return@rememberLauncherForActivityResult
        pendingPermissionTarget = null

        scope.launch {
            when (target) {
                NotificationPermissionTarget.DAILY_READING -> preferencesStore.setNotifyDailyReadingEnabled(granted)
                NotificationPermissionTarget.MOON_EVENTS -> preferencesStore.setNotifyMoonEventsEnabled(granted)
                NotificationPermissionTarget.HABIT_REMINDER -> preferencesStore.setNotifyHabitReminderEnabled(granted)
                NotificationPermissionTarget.TIMING_ALERT -> preferencesStore.setNotifyTimingAlertEnabled(granted)
                NotificationPermissionTarget.TRANSIT_ALERTS -> preferencesStore.setNotifyTransitAlertEnabled(granted)
            }
            if (granted) {
                AstroBackgroundScheduler.scheduleImmediateRefresh(context)
            } else {
                onShowMessage("Notification permission is required before alerts can be enabled.")
            }
        }
    }

    fun canPostNotifications(): Boolean {
        return Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
            ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
    }

    fun requestPermissionIfNeeded(target: NotificationPermissionTarget, enable: Boolean, onGranted: suspend () -> Unit) {
        if (enable && !canPostNotifications()) {
            pendingPermissionTarget = target
            if (shouldShowPermissionRationale(context, Manifest.permission.POST_NOTIFICATIONS)) {
                showNotificationRationaleFor = target
            } else {
                notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
            return
        }

        scope.launch {
            onGranted()
            if (enable) {
                AstroBackgroundScheduler.scheduleImmediateRefresh(context)
            }
        }
    }

    showNotificationRationaleFor?.let { target ->
        PermissionRationaleDialog(
            title = "Allow notification access",
            message = notificationPermissionRationale(target),
            onConfirm = {
                showNotificationRationaleFor = null
                notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            },
            onDismiss = {
                showNotificationRationaleFor = null
                pendingPermissionTarget = null
            },
        )
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text(
            text = "Notifications",
            style = MaterialTheme.typography.headlineMedium,
        )

        PremiumContentCard(
            title = "Android now has the first native background pipeline for alerts and widgets.",
            body = "A WorkManager refresh runs every few hours, updates the morning brief widget cache, and can deliver daily brief, moon-event, and transit alerts once their local rules are met.",
        )

        NotificationToggleCard(
            title = "Daily reading reminder",
            description = "Delivers the morning brief once during your preferred morning window and keeps the widget cache warm.",
            checked = dailyReadingEnabled,
            onCheckedChange = { enabled ->
                requestPermissionIfNeeded(NotificationPermissionTarget.DAILY_READING, enabled) {
                    preferencesStore.setNotifyDailyReadingEnabled(enabled)
                }
            },
            trailingContent = {
                TextButton(
                    onClick = {
                        TimePickerDialog(
                            context,
                            { _, hour, minute ->
                                scope.launch {
                                    preferencesStore.setDailyReadingTime(hour, minute)
                                    AstroBackgroundScheduler.scheduleImmediateRefresh(context)
                                }
                            },
                            dailyReadingHour,
                            dailyReadingMinute,
                            false,
                        ).show()
                    },
                ) {
                    Text(LocalTime.of(dailyReadingHour, dailyReadingMinute).format(timeFormatter))
                }
            },
        )

        NotificationToggleCard(
            title = "Moon event alerts",
            description = "Sends a lunar alert when the refresh pipeline catches a new moon or full moon state.",
            checked = moonEventsEnabled,
            onCheckedChange = { enabled ->
                requestPermissionIfNeeded(NotificationPermissionTarget.MOON_EVENTS, enabled) {
                    preferencesStore.setNotifyMoonEventsEnabled(enabled)
                }
            },
        )

        NotificationToggleCard(
            title = "Habit reminder",
            description = "Looks at your local habit list and nudges you once if today still has open rituals.",
            checked = habitReminderEnabled,
            onCheckedChange = { enabled ->
                requestPermissionIfNeeded(NotificationPermissionTarget.HABIT_REMINDER, enabled) {
                    preferencesStore.setNotifyHabitReminderEnabled(enabled)
                }
            },
            trailingContent = {
                TextButton(
                    onClick = {
                        TimePickerDialog(
                            context,
                            { _, hour, minute ->
                                scope.launch {
                                    preferencesStore.setHabitReminderTime(hour, minute)
                                    AstroBackgroundScheduler.scheduleImmediateRefresh(context)
                                }
                            },
                            habitReminderHour,
                            habitReminderMinute,
                            false,
                        ).show()
                    },
                ) {
                    Text(LocalTime.of(habitReminderHour, habitReminderMinute).format(timeFormatter))
                }
            },
        )

        NotificationToggleCard(
            title = "Timing tip",
            description = "Fetches a live timing reading for your chosen activity and turns it into one daily nudge.",
            checked = timingAlertEnabled,
            onCheckedChange = { enabled ->
                requestPermissionIfNeeded(NotificationPermissionTarget.TIMING_ALERT, enabled) {
                    preferencesStore.setNotifyTimingAlertEnabled(enabled)
                }
            },
            trailingContent = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    TextButton(
                        onClick = {
                            TimePickerDialog(
                                context,
                                { _, hour, minute ->
                                    scope.launch {
                                        preferencesStore.setTimingAlertTime(hour, minute)
                                        AstroBackgroundScheduler.scheduleImmediateRefresh(context)
                                    }
                                },
                                timingAlertHour,
                                timingAlertMinute,
                                false,
                            ).show()
                        },
                    ) {
                        Text(LocalTime.of(timingAlertHour, timingAlertMinute).format(timeFormatter))
                    }
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        TimingActivity.entries.forEach { activity ->
                            FilterChip(
                                selected = timingAlertActivity == activity,
                                onClick = {
                                    scope.launch {
                                        preferencesStore.setTimingAlertActivity(activity)
                                        AstroBackgroundScheduler.scheduleImmediateRefresh(context)
                                    }
                                },
                                label = { Text("${activity.emoji} ${activity.displayName}") },
                            )
                        }
                    }
                }
            },
        )

        NotificationToggleCard(
            title = "Transit alerts",
            description = "Checks the backend daily transit report, schedules exact local alarms for upcoming exact aspects when Android allows it, and still falls back to your preferred delivery window.",
            checked = transitAlertsEnabled,
            onCheckedChange = { enabled ->
                requestPermissionIfNeeded(NotificationPermissionTarget.TRANSIT_ALERTS, enabled) {
                    preferencesStore.setNotifyTransitAlertEnabled(enabled)
                }
            },
            trailingContent = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    TextButton(
                        onClick = {
                            TimePickerDialog(
                                context,
                                { _, hour, minute ->
                                    scope.launch {
                                        preferencesStore.setTransitAlertTime(hour, minute)
                                        AstroBackgroundScheduler.scheduleImmediateRefresh(context)
                                    }
                                },
                                transitAlertHour,
                                transitAlertMinute,
                                false,
                            ).show()
                        },
                    ) {
                        Text(LocalTime.of(transitAlertHour, transitAlertMinute).format(timeFormatter))
                    }

                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && !canScheduleExactTransitAlarms) {
                        Text(
                            text = "Exact transit alarms are currently off for AstroNumeric, so Android will fall back to the broader delivery window instead of minute-level alerts.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        OutlinedButton(
                            onClick = {
                                context.startActivity(
                                    Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)
                                        .setData(Uri.parse("package:${context.packageName}")),
                                )
                            },
                        ) {
                            Text("Enable exact alarms")
                        }
                    }

                    Text(
                        text = exactTransitCacheDetailLabel(exactTransitCacheSnapshot),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Text(
                        text = exactTransitLoadStatusDetailLabel(exactTransitLoadStatus),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            },
        )

        NotificationToggleCard(
            title = "Major transits only",
            description = "Keep proactive transit alerts scoped to stronger squares, oppositions, and tight conjunctions.",
            checked = transitMajorOnly,
            enabled = transitAlertsEnabled,
            onCheckedChange = { enabled ->
                scope.launch {
                    preferencesStore.setTransitAlertsMajorOnly(enabled)
                    AstroBackgroundScheduler.scheduleImmediateRefresh(context)
                }
            },
        )

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                NotificationAccountSyncCard(
                    scope = scope,
                    preferencesStore = preferencesStore,
                    remoteDataSource = remoteDataSource,
                    profileRepository = profileRepository,
                    pushRegistrationManager = pushRegistrationManager,
                    selectedProfile = selectedProfile,
                    personalModeEnabled = personalModeEnabled,
                    authAccessToken = authAccessToken,
                    authUserEmail = authUserEmail,
                    authEmailDraft = authEmailDraft,
                    onAuthEmailDraftChange = { authEmailDraft = it },
                    authPasswordDraft = authPasswordDraft,
                    onAuthPasswordDraftChange = { authPasswordDraft = it },
                    authInFlight = authInFlight,
                    onAuthInFlightChange = { authInFlight = it },
                    firebaseConfigured = firebaseConfigured,
                    mercuryRetrogradeAlertsEnabled = mercuryRetrogradeAlertsEnabled,
                    alertFrequency = alertFrequency,
                    transitEmailDraft = transitEmailDraft,
                    onTransitEmailDraftChange = { transitEmailDraft = it },
                    accountSyncEnabled = accountSyncEnabled,
                    onShowMessage = onShowMessage,
                    onSyncAlertPreferencesIfAuthenticated = ::syncAlertPreferencesIfAuthenticated,
                )
            }
        }
    }
}

@Composable
internal fun NotificationToggleCard(
    title: String,
    description: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    trailingContent: @Composable (() -> Unit)? = null,
) {
    PremiumContentCard(modifier = modifier) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = description,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Switch(
                    checked = checked,
                    onCheckedChange = onCheckedChange,
                    enabled = enabled,
                )
            }

            trailingContent?.invoke()
    }
}