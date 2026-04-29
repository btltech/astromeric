package com.astromeric.android.feature.profile

import android.Manifest
import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.appwidget.AppWidgetManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Paint
import android.graphics.drawable.ColorDrawable
import android.location.Geocoder
import android.net.Uri
import android.os.Build
import android.content.pm.PackageManager
import android.view.View
import android.view.ViewGroup
import android.widget.DatePicker
import android.widget.EditText
import android.widget.NumberPicker
import android.widget.TextView
import com.astromeric.android.R
import com.astromeric.android.BuildConfig
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ElevatedAssistChip
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.graphics.toArgb
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.work.ListenableWorker
import com.astromeric.android.app.AstroNotificationService
import com.astromeric.android.app.ExactTransitAlarmScheduler
import com.astromeric.android.app.MorningBriefWidgetProvider
import com.astromeric.android.app.MorningBriefWidgetSnapshotStore
import com.astromeric.android.app.runAstroRefresh
import com.astromeric.android.core.data.local.ExactTransitCacheStore
import com.astromeric.android.core.data.local.ExactTransitLoadStatusStore
import com.astromeric.android.core.localization.AppLanguageManager
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.core.model.AppLanguage
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.DataQuality
import com.astromeric.android.core.model.DefaultHouseSystem
import com.astromeric.android.core.model.GuideTone
import com.astromeric.android.core.model.HiddenValueLabel
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.ProfileDraft
import com.astromeric.android.core.model.TimeConfidence
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.maskedBirthplace
import com.astromeric.android.core.model.maskedDateOfBirth
import com.astromeric.android.core.model.maskedBirthTime
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumHeroCard
import com.astromeric.android.feature.guide.GuideHealthAvailability
import com.astromeric.android.feature.guide.GuideHealthConnectBridge
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.Duration
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

private val DateFormatter: DateTimeFormatter = DateTimeFormatter.ISO_LOCAL_DATE
private val TimeFormatter: DateTimeFormatter = DateTimeFormatter.ofPattern("h:mm a")

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun ProfileListScreen(
    profiles: List<AppProfile>,
    selectedProfileId: Int?,
    preferencesStore: AppPreferencesStore,
    hideSensitiveDetailsEnabled: Boolean,
    personalModeEnabled: Boolean,
    isAuthenticated: Boolean,
    accountEmail: String,
    onCreateProfile: () -> Unit,
    onOpenLearn: () -> Unit,
    onOpenGuide: () -> Unit,
    onOpenUserGuide: () -> Unit,
    onOpenHelp: () -> Unit,
    onOpenNotifications: () -> Unit,
    onOpenPrivacy: () -> Unit,
    onSyncProfiles: () -> Unit,
    onEditProfile: (Int) -> Unit,
    onSelectProfile: (Int) -> Unit,
    onDeleteProfile: (Int) -> Unit,
    onSeedDebugProfile: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val keyboardController = LocalSoftwareKeyboardController.current
    val scope = rememberCoroutineScope()
    val localOnlyCount = profiles.count(AppProfile::isLocalOnly)
    val syncedCount = profiles.count(AppProfile::isRemoteBacked)
    val selectedProfile = profiles.firstOrNull { it.id == selectedProfileId } ?: profiles.firstOrNull()
    val fullDataCount = profiles.count { it.dataQuality == DataQuality.FULL }
    val tonePreference by preferencesStore.tonePreference.collectAsStateWithLifecycle(initialValue = 50.0)
    val guideTone by preferencesStore.guideTone.collectAsStateWithLifecycle(initialValue = GuideTone.BALANCED)
    val highContrastEnabled by preferencesStore.highContrastEnabled.collectAsStateWithLifecycle(initialValue = false)
    val largeTextEnabled by preferencesStore.largeTextEnabled.collectAsStateWithLifecycle(initialValue = false)
    val appLanguage by preferencesStore.appLanguage.collectAsStateWithLifecycle(initialValue = AppLanguage.defaultFromSystem())
    val calendarContextEnabled by preferencesStore.guideCalendarContextEnabled.collectAsStateWithLifecycle(initialValue = false)
    val biometricContextEnabled by preferencesStore.guideBiometricContextEnabled.collectAsStateWithLifecycle(initialValue = false)
    val dailyReminderEnabled by preferencesStore.notifyDailyReadingEnabled.collectAsStateWithLifecycle(initialValue = false)
    val habitReminderEnabled by preferencesStore.notifyHabitReminderEnabled.collectAsStateWithLifecycle(initialValue = false)
    val timingAlertEnabled by preferencesStore.notifyTimingAlertEnabled.collectAsStateWithLifecycle(initialValue = false)
    val transitAlertsEnabled by preferencesStore.notifyTransitAlertEnabled.collectAsStateWithLifecycle(initialValue = false)
    val dailyReadingHour by preferencesStore.dailyReadingHour.collectAsStateWithLifecycle(initialValue = 7)
    val dailyReadingMinute by preferencesStore.dailyReadingMinute.collectAsStateWithLifecycle(initialValue = 0)
    val habitReminderHour by preferencesStore.habitReminderHour.collectAsStateWithLifecycle(initialValue = 20)
    val habitReminderMinute by preferencesStore.habitReminderMinute.collectAsStateWithLifecycle(initialValue = 0)
    val timingAlertHour by preferencesStore.timingAlertHour.collectAsStateWithLifecycle(initialValue = 10)
    val timingAlertMinute by preferencesStore.timingAlertMinute.collectAsStateWithLifecycle(initialValue = 0)
    val transitAlertHour by preferencesStore.transitAlertHour.collectAsStateWithLifecycle(initialValue = 9)
    val transitAlertMinute by preferencesStore.transitAlertMinute.collectAsStateWithLifecycle(initialValue = 0)
    val widgetSnapshotStore = remember(context) { MorningBriefWidgetSnapshotStore(context.applicationContext) }
    val exactTransitCacheStore = remember(context) { ExactTransitCacheStore(context.applicationContext) }
    val exactTransitLoadStatusStore = remember(context) { ExactTransitLoadStatusStore(context.applicationContext) }
    var diagnosticsRefreshVersion by rememberSaveable { mutableStateOf(0) }
    val widgetSnapshot = remember(context, diagnosticsRefreshVersion) { widgetSnapshotStore.read() }
    val scheduledTransitHashCount = remember(context, diagnosticsRefreshVersion) { widgetSnapshotStore.scheduledTransitHashes().size }
    val exactTransitCacheSnapshot = remember(selectedProfile?.id, diagnosticsRefreshVersion) {
        selectedProfile?.let { exactTransitCacheStore.read(it.id) }
    }
    val exactTransitLoadStatus = remember(selectedProfile?.id, diagnosticsRefreshVersion) {
        selectedProfile?.let { exactTransitLoadStatusStore.read(it.id) }
    }
    val exactTransitAlarmScheduler = remember(context) {
        ExactTransitAlarmScheduler(context.applicationContext, widgetSnapshotStore)
    }
    val exactTransitAlarmAccess = remember(diagnosticsRefreshVersion) { exactTransitAlarmScheduler.canScheduleExactAlarms() }
    val widgetInstanceCount = AppWidgetManager.getInstance(context).getAppWidgetIds(
        ComponentName(context, MorningBriefWidgetProvider::class.java),
    ).size
    var debugDiagnosticsNote by rememberSaveable(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var isRunningDebugRefresh by rememberSaveable { mutableStateOf(false) }
    val notificationsEnabledInSystem = NotificationManagerCompat.from(context).areNotificationsEnabled()
    val notificationPermissionGranted = Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
        ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
    val calendarPermissionGranted = ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALENDAR) == PackageManager.PERMISSION_GRANTED
    val healthAvailability = remember(context) {
        GuideHealthConnectBridge(context.applicationContext)
    }.availability()

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            PremiumHeroCard(
                eyebrow = "Profile",
                title = "Your Cosmic Identity",
                body = "Manage local-first identity, privacy, alerts, and account state without leaving the main shell.",
                chips = listOf(
                    "${profiles.size} profile(s)",
                    "${localOnlyCount} local",
                    "${fullDataCount} complete",
                ),
            ) {
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    TextButton(onClick = onOpenNotifications) {
                        Text("Alerts")
                    }
                    TextButton(onClick = onOpenPrivacy) {
                        Text(if (hideSensitiveDetailsEnabled) "Privacy: On" else "Privacy")
                    }
                    Button(onClick = onCreateProfile) {
                        Icon(Icons.Filled.Add, contentDescription = null)
                        Text("New profile")
                    }
                }
            }
        }

        item {
            PremiumContentCard(
                title = when {
                    personalModeEnabled -> "Personal mode"
                    isAuthenticated -> "Signed in as $accountEmail"
                    else -> "Local-only profile mode"
                },
                body = when {
                    personalModeEnabled -> "This build keeps the iOS-style local-first contract. Profiles stay on this device and any saved account session stays dormant while personal mode is enabled."
                    isAuthenticated -> "$syncedCount account-synced profile(s) and $localOnlyCount device-only profile(s)."
                    else -> "Profiles stay on this device until you sign in. $localOnlyCount profile(s) are currently device-only."
                },
            )
        }

        item {
            if (profiles.isEmpty()) {
                NoProfileSetupCard(
                    onCreateProfile = onCreateProfile,
                    onOpenPrivacy = onOpenPrivacy,
                )
            } else if (selectedProfile != null) {
                ActiveProfileSummaryCard(
                    profile = selectedProfile,
                    hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                    onEditProfile = { onEditProfile(selectedProfile.id) },
                    onCreateProfile = onCreateProfile,
                )
            }
        }

        item {
            PremiumContentCard(
                title = "Settings & account",
                body = "Shape how visible your data is, where alerts go, and whether device-only profiles ever attach to an account.",
            ) {
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        ElevatedAssistChip(
                            onClick = onOpenNotifications,
                            label = { Text(if (personalModeEnabled) "Alerts & local settings" else "Alerts & account") },
                        )
                        ElevatedAssistChip(
                            onClick = onOpenPrivacy,
                            label = { Text(if (hideSensitiveDetailsEnabled) "Privacy redaction on" else "Open privacy controls") },
                        )
                        if (!personalModeEnabled && isAuthenticated && localOnlyCount > 0) {
                            ElevatedAssistChip(
                                onClick = onSyncProfiles,
                                label = { Text("Sync device-only profiles") },
                            )
                        } else if (!personalModeEnabled && !isAuthenticated) {
                            ElevatedAssistChip(
                                onClick = onOpenNotifications,
                                label = { Text("Sign in to sync") },
                            )
                        }
                        ElevatedAssistChip(
                            onClick = onCreateProfile,
                            label = { Text("Create another profile") },
                        )
                    }
            }
        }

        item {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = stringResource(R.string.profile_accessibility_title),
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = stringResource(R.string.profile_accessibility_summary),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    PreferenceToggleRow(
                        label = stringResource(R.string.profile_accessibility_high_contrast_label),
                        detail = stringResource(R.string.profile_accessibility_high_contrast_detail),
                        checked = highContrastEnabled,
                        onCheckedChange = { enabled ->
                            scope.launch {
                                preferencesStore.setHighContrastEnabled(enabled)
                            }
                        },
                    )
                    PreferenceToggleRow(
                        label = stringResource(R.string.profile_accessibility_large_text_label),
                        detail = stringResource(R.string.profile_accessibility_large_text_detail),
                        checked = largeTextEnabled,
                        onCheckedChange = { enabled ->
                            scope.launch {
                                preferencesStore.setLargeTextEnabled(enabled)
                            }
                        },
                    )
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            text = stringResource(R.string.profile_language_title),
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.SemiBold,
                        )
                        Text(
                            text = stringResource(R.string.profile_language_summary),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            AppLanguage.entries.forEach { language ->
                                FilterChip(
                                    selected = appLanguage == language,
                                    onClick = {
                                        scope.launch {
                                            preferencesStore.setAppLanguage(language)
                                            AppLanguageManager.applyLanguage(language)
                                        }
                                    },
                                    label = { Text(language.chipLabel) },
                                )
                            }
                        }
                    }
                }
            }
        }

        item {
            PremiumContentCard(
                title = "Experience settings",
                body = "Mirror the same controls iOS exposes: how readings sound, which nudges are active, and how much optional context the guide can use.",
            ) {
                    ProfileStatusRow(label = "Reading tone", value = tonePreferenceLabel(tonePreference))
                    ProfileStatusRow(label = "Guide voice", value = guideTone.label)
                    ProfileStatusRow(label = "Daily reading reminder", value = if (dailyReminderEnabled) "On" else "Off")
                    ProfileStatusRow(label = "Calendar context", value = if (calendarContextEnabled) "On" else "Off")
                    ProfileStatusRow(label = "Biometric context", value = if (biometricContextEnabled) "On" else "Off")
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        ElevatedAssistChip(
                            onClick = onOpenNotifications,
                            label = { Text("Notification settings") },
                        )
                        ElevatedAssistChip(
                            onClick = onOpenGuide,
                            label = { Text("Guide preferences") },
                        )
                        ElevatedAssistChip(
                            onClick = onOpenPrivacy,
                            label = { Text("Privacy controls") },
                        )
                    }
            }
        }

        item {
            PremiumContentCard(
                title = "Learning & support",
                body = "Keep the Profile hub useful even when users need education, guidance, or a human follow-up.",
            ) {
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        ElevatedAssistChip(
                            onClick = onOpenUserGuide,
                            label = { Text("User Guide") },
                        )
                        ElevatedAssistChip(
                            onClick = onOpenHelp,
                            label = { Text("Help & FAQ") },
                        )
                        ElevatedAssistChip(
                            onClick = onOpenLearn,
                            label = { Text("Learn Astrology & Numerology") },
                        )
                        ElevatedAssistChip(
                            onClick = onOpenGuide,
                            label = { Text("Open Cosmic Guide") },
                        )
                        ElevatedAssistChip(
                            onClick = {
                                launchMailIntent(
                                    context = context,
                                    address = "support@astromeric.app",
                                    subject = "AstroNumeric Android Support",
                                    body = buildSupportEmailBody(
                                        profilesCount = profiles.size,
                                        hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                                    ),
                                )
                            },
                            label = { Text("Email support") },
                        )
                        ElevatedAssistChip(
                            onClick = onOpenPrivacy,
                            label = { Text("Privacy policy") },
                        )
                    }
            }
        }

        item {
            PremiumContentCard(
                title = "Backups & transfer",
                body = selectedProfile?.let {
                    "Active profile ready for backup or share: ${it.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)}"
                } ?: "Select or create a profile before exporting, importing, or sharing a summary.",
                footer = "Android already ships full-fidelity export/import in Privacy. Redaction changes visible labels and text sharing, not the backup payload itself.",
            ) {
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Button(
                            onClick = onOpenPrivacy,
                            modifier = Modifier.weight(1f),
                        ) {
                            Text("Export/import backups")
                        }
                        OutlinedButton(
                            onClick = {
                                selectedProfile?.let { profile ->
                                    shareProfileSummary(
                                        context = context,
                                        profile = profile,
                                        hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                                    )
                                }
                            },
                            enabled = selectedProfile != null,
                            modifier = Modifier.weight(1f),
                        ) {
                            Text("Share summary")
                        }
                    }
            }
        }

        item {
            PremiumContentCard(title = "Trust & safety") {
                    ProfileInfoLine(
                        title = "Private by default",
                        detail = "Profiles begin on-device and stay local unless you explicitly attach them to an account-backed flow.",
                    )
                    ProfileInfoLine(
                        title = "Privacy mode ${if (hideSensitiveDetailsEnabled) "is on" else "is off"}",
                        detail = if (hideSensitiveDetailsEnabled) {
                            "Names and birth details are masked across the Android UI while calculations still use the saved profile data they need."
                        } else {
                            "Profile details are currently visible in full. Open Privacy to mask names and birth details across the main UI."
                        },
                    )
                    ProfileInfoLine(
                        title = "Shared backend boundary",
                        detail = "Forecasts, charts, AI guidance, and alerts still use the same Railway `/v2` backend surface as iOS when those features need it.",
                    )
                    OutlinedButton(
                        onClick = {
                            launchMailIntent(
                                context = context,
                                address = "support@astromeric.app",
                                subject = "AstroNumeric Android Support",
                                body = buildSupportEmailBody(
                                    profilesCount = profiles.size,
                                    hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                                ),
                            )
                        },
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("Send support email")
                    }
            }
        }

        item {
            SystemDiagnosticsCard(
                selectedProfile = selectedProfile,
                profilesCount = profiles.size,
                fullDataCount = fullDataCount,
                localOnlyCount = localOnlyCount,
                syncedCount = syncedCount,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                personalModeEnabled = personalModeEnabled,
                isAuthenticated = isAuthenticated,
                notificationsEnabledInSystem = notificationsEnabledInSystem,
                notificationPermissionGranted = notificationPermissionGranted,
                calendarPermissionGranted = calendarPermissionGranted,
                healthAvailability = healthAvailability,
                dailyReminderEnabled = dailyReminderEnabled,
                habitReminderEnabled = habitReminderEnabled,
                timingAlertEnabled = timingAlertEnabled,
                transitAlertsEnabled = transitAlertsEnabled,
                dailyReadingHour = dailyReadingHour,
                dailyReadingMinute = dailyReadingMinute,
                habitReminderHour = habitReminderHour,
                habitReminderMinute = habitReminderMinute,
                timingAlertHour = timingAlertHour,
                timingAlertMinute = timingAlertMinute,
                transitAlertHour = transitAlertHour,
                transitAlertMinute = transitAlertMinute,
                widgetInstanceCount = widgetInstanceCount,
                widgetSnapshot = widgetSnapshot,
                widgetSnapshotStore = widgetSnapshotStore,
                exactTransitCacheSnapshot = exactTransitCacheSnapshot,
                exactTransitLoadStatus = exactTransitLoadStatus,
                exactTransitAlarmAccess = exactTransitAlarmAccess,
                scheduledTransitHashCount = scheduledTransitHashCount,
                isRunningDebugRefresh = isRunningDebugRefresh,
                debugDiagnosticsNote = debugDiagnosticsNote,
                onRefresh = { diagnosticsRefreshVersion += 1 },
                onSeedDebugProfile = onSeedDebugProfile,
                onDebugDiagnosticsNoteChange = { debugDiagnosticsNote = it },
                onPreviewExactTransitNotification = { profile, source, isCached ->
                    AstroNotificationService(context.applicationContext).showExactTransitNotification(
                        profileName = profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                        transitPlanet = "Mars",
                        natalPoint = "Sun",
                        aspect = "square",
                        interpretation = "Debug preview of the exact-transit notification payload.",
                        source = source,
                        isCached = isCached,
                        notificationId = 1008,
                    )
                },
                onRunDebugRefresh = { profile ->
                    scope.launch {
                        isRunningDebugRefresh = true
                        debugDiagnosticsNote = "Running the shared refresh path now..."
                        val refreshResult = runAstroRefresh(
                            applicationContext = context.applicationContext,
                            forceExactTransitDiagnostics = true,
                        )
                        val refreshedStatus = exactTransitLoadStatusStore.read(profile.id)
                        diagnosticsRefreshVersion += 1
                        debugDiagnosticsNote = when (refreshResult) {
                            is ListenableWorker.Result.Success -> refreshedStatus?.let(::exactTransitLoadStatusDetailLabel)
                                ?: "Refresh finished, but no exact transit source was recorded."
                            is ListenableWorker.Result.Retry -> "Refresh requested a retry."
                            is ListenableWorker.Result.Failure -> "Refresh failed."
                            else -> "Refresh completed with an unexpected result."
                        }
                        isRunningDebugRefresh = false
                    }
                },
            )
        }

        item {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    Text(
                        text = "App info",
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = "AstroNumeric Android ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Text(
                        text = "This build stays dark-first and local-first while sharing the same backend contract as iOS.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }

        if (profiles.isNotEmpty()) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(
                        text = "All profiles",
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = "Switch the active profile, edit details, or remove an old entry from this device.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }

        itemsIndexed(items = profiles, key = { _, profile -> profile.id }) { index, profile ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    onClick = { onSelectProfile(profile.id) },
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                        ) {
                            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                Text(
                                    text = profile.displayName(
                                        hideSensitive = hideSensitiveDetailsEnabled,
                                        role = PrivacyDisplayRole.GENERIC_PROFILE,
                                        index = index,
                                    ),
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.SemiBold,
                                )
                                Text(
                                    text = "${profile.maskedDateOfBirth(hideSensitiveDetailsEnabled)} · ${profile.maskedBirthplace(hideSensitiveDetailsEnabled)}",
                                    style = MaterialTheme.typography.bodyMedium,
                                )
                            }

                            Row {
                                IconButton(onClick = { onEditProfile(profile.id) }) {
                                    Icon(Icons.Filled.Edit, contentDescription = "Edit profile")
                                }
                                IconButton(onClick = { onDeleteProfile(profile.id) }) {
                                    Icon(Icons.Filled.Delete, contentDescription = "Delete profile")
                                }
                            }
                        }

                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            ElevatedAssistChip(
                                onClick = {},
                                label = { Text(if (profile.isRemoteBacked) "Account Synced" else "Device Only") },
                            )
                            ElevatedAssistChip(
                                onClick = {},
                                label = { Text(profile.dataQuality.label) },
                            )
                            if (selectedProfile?.id == profile.id) {
                                ElevatedAssistChip(
                                    onClick = {},
                                    label = { Text("Selected") },
                                )
                            }
                            ElevatedAssistChip(
                                onClick = {},
                                label = { Text(profile.timezone ?: "Timezone missing") },
                            )
                        }

                        Text(
                            text = profile.dataQuality.description,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        if (!personalModeEnabled && isAuthenticated && profile.isLocalOnly) {
                            Text(
                                text = "This profile still lives only on this device. Sync it to attach it to your account-backed alerts and profile storage.",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
            }
    }
}

@Composable
private fun NoProfileSetupCard(
    onCreateProfile: () -> Unit,
    onOpenPrivacy: () -> Unit,
) {
    PremiumContentCard(
        title = "No profile set up",
        body = "Create your profile to unlock a real chart, meaningful numerology, and timing that actually belongs to you.",
    ) {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Button(
                    onClick = onCreateProfile,
                    modifier = Modifier.weight(1f),
                ) {
                    Text("Create profile")
                }
                TextButton(
                    onClick = onOpenPrivacy,
                    modifier = Modifier.weight(1f),
                ) {
                    Text("Privacy controls")
                }
            }
    }
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
private fun ActiveProfileSummaryCard(
    profile: AppProfile,
    hideSensitiveDetailsEnabled: Boolean,
    onEditProfile: () -> Unit,
    onCreateProfile: () -> Unit,
) {
    var showBirthDate by rememberSaveable(profile.id) { mutableStateOf(false) }

    PremiumContentCard(
        title = "Birth details",
        body = "This profile powers your chart, numerology, timing tools, and personal guidance throughout the app.",
    ) {
            Text(
                text = profile.displayName(
                    hideSensitive = hideSensitiveDetailsEnabled,
                    role = PrivacyDisplayRole.ACTIVE_USER,
                ),
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.SemiBold,
            )
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                ElevatedAssistChip(
                    onClick = {},
                    label = { Text(profile.dataQuality.label) },
                )
                ElevatedAssistChip(
                    onClick = {},
                    label = { Text(if (profile.isRemoteBacked) "Account synced" else "Device only") },
                )
                ElevatedAssistChip(
                    onClick = {},
                    label = { Text(profile.timezone ?: "Timezone missing") },
                )
            }
            Text(
                text = profile.dataQuality.description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            ProfileDetailValueRow(
                label = "Birth date",
                value = when {
                    hideSensitiveDetailsEnabled -> HiddenValueLabel
                    showBirthDate -> formatBirthDateForDisplay(profile.dateOfBirth)
                    else -> "Tap reveal below"
                },
            )
            if (!hideSensitiveDetailsEnabled) {
                TextButton(onClick = { showBirthDate = !showBirthDate }) {
                    Text(if (showBirthDate) "Hide birth date" else "Reveal birth date")
                }
            }
            ProfileDetailValueRow(
                label = "Birth time",
                value = if (hideSensitiveDetailsEnabled) {
                    profile.maskedBirthTime(true)
                } else {
                    formatBirthTimeForDisplay(profile.timeOfBirth)
                },
            )
            ProfileDetailValueRow(
                label = "Time confidence",
                value = profile.timeConfidence.displayTitle,
            )
            ProfileDetailValueRow(
                label = "Birthplace",
                value = profile.maskedBirthplace(hideSensitiveDetailsEnabled),
            )
            ProfileDetailValueRow(
                label = "Timezone",
                value = profile.timezone ?: "Timezone missing",
            )
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Button(
                    onClick = onEditProfile,
                    modifier = Modifier.weight(1f),
                ) {
                    Text("Edit active profile")
                }
                TextButton(
                    onClick = onCreateProfile,
                    modifier = Modifier.weight(1f),
                ) {
                    Text("Create another")
                }
        }
    }
}

@Composable
private fun ProfileInfoLine(
    title: String,
    detail: String,
) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(
            text = title,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = detail,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun ProfileStatusRow(
    label: String,
    value: String,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun ProfileDetailValueRow(
    label: String,
    value: String,
) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}

@Composable
private fun PreferenceToggleRow(
    label: String,
    detail: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Column(
            modifier = Modifier
                .weight(1f)
                .padding(end = 16.dp),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold,
            )
            Text(
                text = detail,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
        )
    }
}

private fun tonePreferenceLabel(value: Double): String = when {
    value < 25.0 -> "Very Practical"
    value < 50.0 -> "Balanced Practical"
    value < 75.0 -> "Balanced Mystical"
    else -> "Very Mystical"
}

private fun formatBirthDateForDisplay(raw: String): String = runCatching {
    LocalDate.parse(raw).format(DateTimeFormatter.ofPattern("MMMM d, yyyy"))
}.getOrDefault(raw)

private fun formatBirthTimeForDisplay(raw: String?): String {
    if (raw.isNullOrBlank()) {
        return "Not set"
    }
    val normalized = raw.take(5)
    return runCatching {
        LocalTime.parse(normalized).format(TimeFormatter)
    }.getOrDefault(normalized)
}

private fun buildSupportEmailBody(
    profilesCount: Int,
    hideSensitiveDetailsEnabled: Boolean,
): String = buildString {
    appendLine("Please describe what happened:")
    appendLine()
    appendLine("Screen or feature:")
    appendLine("Expected result:")
    appendLine("Actual result:")
    appendLine("Steps to reproduce:")
    appendLine()
    appendLine("---")
    appendLine("Diagnostics")
    appendLine("AstroNumeric Android ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})")
    appendLine("Android ${Build.VERSION.RELEASE}")
    appendLine("Device: ${Build.MANUFACTURER} ${Build.MODEL}")
    appendLine("Profiles on device: $profilesCount")
    appendLine("Privacy mode: ${if (hideSensitiveDetailsEnabled) "On" else "Off"}")
    appendLine()
    append("No birth date, birth time, birthplace, journal text, or chart data is included automatically.")
}

private fun launchMailIntent(
    context: Context,
    address: String,
    subject: String,
    body: String,
) {
    val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
        data = Uri.parse("mailto:$address")
        putExtra(Intent.EXTRA_SUBJECT, subject)
        putExtra(Intent.EXTRA_TEXT, body)
    }
    if (emailIntent.resolveActivity(context.packageManager) != null) {
        context.startActivity(emailIntent)
    }
}

private fun shareProfileSummary(
    context: Context,
    profile: AppProfile,
    hideSensitiveDetailsEnabled: Boolean,
) {
    val shareIntent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_SUBJECT, "AstroNumeric profile")
        putExtra(Intent.EXTRA_TEXT, profile.toShareSummaryText(hideSensitiveDetailsEnabled))
    }
    if (shareIntent.resolveActivity(context.packageManager) != null) {
        context.startActivity(Intent.createChooser(shareIntent, "Share profile summary"))
    }
}


