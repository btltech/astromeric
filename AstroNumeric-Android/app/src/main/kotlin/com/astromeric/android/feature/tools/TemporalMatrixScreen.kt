package com.astromeric.android.feature.tools

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.content.ContentUris
import android.provider.CalendarContract
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.astromeric.android.core.data.local.TimingAdviceCacheStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.loadTimingAdviceWithCacheFallback
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.MoonPhaseInfoData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.TimingActivity
import com.astromeric.android.core.model.TimingAdvicePayload
import com.astromeric.android.core.model.TimingDayPayload
import com.astromeric.android.core.model.TimingHourPayload
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.toWindowLabel
import com.astromeric.android.core.model.toTimingLocalTimeOrNull
import com.astromeric.android.core.ui.PermissionRationaleDialog
import com.astromeric.android.core.ui.shouldShowPermissionRationale
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withContext
import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale

@Composable
fun TemporalMatrixScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val timingAdviceCacheStore = remember(context) { TimingAdviceCacheStore(context.applicationContext) }
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var hasCalendarPermission by remember { mutableStateOf(hasCalendarPermission(context)) }
    var permissionRequested by remember { mutableStateOf(false) }
    var showCalendarRationale by remember { mutableStateOf(false) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var loadError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var events by remember { mutableStateOf<List<TemporalMatrixEvent>>(emptyList()) }
    var moonPhase by remember { mutableStateOf<MoonPhaseInfoData?>(null) }
    var adviceByActivity by remember(selectedProfile?.id) { mutableStateOf<Map<TimingActivity, TimingAdvicePayload>>(emptyMap()) }
    var cachedAdviceActivities by remember(selectedProfile?.id) { mutableStateOf<Set<TimingActivity>>(emptySet()) }

    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        permissionRequested = true
        hasCalendarPermission = granted
    }

    fun requestCalendarPermission() {
        permissionRequested = true
        if (shouldShowPermissionRationale(context, Manifest.permission.READ_CALENDAR)) {
            showCalendarRationale = true
        } else {
            permissionLauncher.launch(Manifest.permission.READ_CALENDAR)
        }
    }

    if (showCalendarRationale) {
        PermissionRationaleDialog(
            title = "Allow calendar access",
            message = "Temporal Matrix reads the next 48 hours from your device calendar so it can compare event timing against the live sky. Event titles and exact locations stay on this phone.",
            onConfirm = {
                showCalendarRationale = false
                permissionLauncher.launch(Manifest.permission.READ_CALENDAR)
            },
            onDismiss = {
                showCalendarRationale = false
            },
        )
    }

    LaunchedEffect(selectedProfile?.id, hasCalendarPermission, refreshVersion) {
        if (!hasCalendarPermission) {
            events = emptyList()
            moonPhase = null
            adviceByActivity = emptyMap()
            cachedAdviceActivities = emptySet()
            isLoading = false
            return@LaunchedEffect
        }

        isLoading = true
        loadError = null

        try {
            coroutineScope {
                val eventsRequest = async { loadUpcomingEvents(context) }
                val moonRequest = async { remoteDataSource.fetchMoonPhase() }

                val loadedEvents = eventsRequest.await()
                events = loadedEvents
                moonPhase = moonRequest.await().getOrNull()

                adviceByActivity = if (selectedProfile != null && loadedEvents.isNotEmpty()) {
                    val timingResults = loadedEvents
                        .map { inferTimingActivity(it.title) }
                        .distinct()
                        .map { activity ->
                            async {
                                val result = loadTimingAdviceWithCacheFallback(
                                    activity = activity,
                                    profile = selectedProfile,
                                    remoteDataSource = remoteDataSource,
                                    cacheStore = timingAdviceCacheStore,
                                )
                                Triple(activity, result.payload, result.isCached)
                            }
                        }
                        .map { it.await() }

                    cachedAdviceActivities = timingResults
                        .filter { (_, payload, isCached) -> payload != null && isCached }
                        .map { (activity, _, _) -> activity }
                        .toSet()

                    timingResults.mapNotNull { (activity, payload, _) ->
                            payload?.let { activity to it }
                        }
                        .toMap()
                } else {
                    cachedAdviceActivities = emptySet()
                    emptyMap()
                }
            }
        } catch (error: Exception) {
            loadError = error.message ?: "Temporal Matrix could not read your upcoming events."
        }

        isLoading = false
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Text(
                    text = "Temporal Matrix",
                    style = MaterialTheme.typography.headlineMedium,
                )
                Text(
                    text = "Overlay the next 48 hours with your calendar and live timing weather. This Android version stays honest about its inputs: event titles and locations remain on-device, while timing guidance comes from the same shared backend the rest of the app uses.",
                    style = MaterialTheme.typography.bodyMedium,
                )
                selectedProfile?.let { profile ->
                    AssistChip(
                        onClick = {},
                        label = {
                            Text(
                                "Active profile: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)}",
                            )
                        },
                    )
                } ?: Button(onClick = onOpenProfile) {
                    Text("Add Profile For Personal Timing")
                }
                if (moonPhase != null) {
                    AssistChip(
                        onClick = {},
                        label = { Text("Moon: ${moonPhase?.phase.orEmpty()}") },
                    )
                }
                OutlinedButton(onClick = { refreshVersion += 1 }, enabled = !isLoading) {
                    Text(if (isLoading) "Refreshing..." else "Refresh Matrix")
                }
            }
        }

        if (!hasCalendarPermission) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    Text(
                        text = if (permissionRequested) "Calendar Access Needed" else "Enable Calendar Access",
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = "The Temporal Matrix reads your next 48 hours directly from the device calendar so it can compare event timing against the live sky. Titles and exact locations stay local to this phone.",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Button(onClick = { requestCalendarPermission() }) {
                        Text("Allow Calendar Access")
                    }
                }
            }
            return@Column
        }

        when {
            isLoading && events.isEmpty() -> {
                CircularProgressIndicator()
            }

            loadError != null && events.isEmpty() -> {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        Text(
                            text = "Unable to Build the Matrix",
                            style = MaterialTheme.typography.titleMedium,
                        )
                        Text(
                            text = loadError.orEmpty(),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Button(onClick = { refreshVersion += 1 }) {
                            Text("Try Again")
                        }
                    }
                }
            }

            events.isEmpty() -> {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        Text(
                            text = "No Events in the Next 48 Hours",
                            style = MaterialTheme.typography.titleMedium,
                        )
                        Text(
                            text = "Your schedule is open. Use the free space intentionally instead of treating it as empty by default.",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                }
            }

            else -> {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(
                            text = "Next 48 Hours",
                            style = MaterialTheme.typography.titleMedium,
                        )
                        Text(
                            text = "${events.size} event(s) scanned across ${events.map { it.start.toLocalDate() }.distinct().size} day(s).",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = "Timing weather is inferred from the event title, its time window, and the shared timing endpoint. When the app cannot classify an event cleanly, it falls back to a meeting-style timing read instead of pretending to know more.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }

                events.forEach { event ->
                    val insight = buildTemporalInsight(event, adviceByActivity, cachedAdviceActivities, moonPhase)
                    TemporalMatrixEventCard(event = event, insight = insight, moonPhase = moonPhase)
                }
            }
        }
    }
}

@Composable
private fun TemporalMatrixEventCard(
    event: TemporalMatrixEvent,
    insight: TemporalMatrixInsight,
    moonPhase: MoonPhaseInfoData?,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = event.title,
                style = MaterialTheme.typography.titleMedium,
            )
            Text(
                text = "${event.dayLabel} · ${event.timeLabel}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            event.location?.takeIf { it.isNotBlank() }?.let { location ->
                Text(
                    text = location,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            AssistChip(
                onClick = {},
                label = { Text("${insight.threatLevel.emoji} ${insight.threatLevel.label}") },
            )
            AssistChip(
                onClick = {},
                label = { Text("${insight.activity.emoji} ${insight.activity.displayName}") },
            )
            insight.scoreLabel?.let { scoreLabel ->
                AssistChip(
                    onClick = {},
                    label = { Text(scoreLabel) },
                )
            }
            if (insight.usesCachedTiming) {
                AssistChip(
                    onClick = {},
                    label = { Text("Cached timing") },
                )
            }
            moonPhase?.phase?.takeIf { it.isNotBlank() }?.let { phase ->
                Text(
                    text = "Moon phase: $phase",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Text(
                text = insight.summary,
                style = MaterialTheme.typography.bodyMedium,
            )
            insight.matchedWindow?.let { matchedWindow ->
                Text(
                    text = "Aligned window: $matchedWindow",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            if (insight.warnings.isNotEmpty()) {
                Text(
                    text = "Watch-outs: ${insight.warnings.take(2).joinToString()}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

private data class TemporalMatrixEvent(
    val title: String,
    val location: String?,
    val start: ZonedDateTime,
    val end: ZonedDateTime,
) {
    val dayLabel: String
        get() = dayFormatter.format(start)

    val timeLabel: String
        get() = "${timeFormatter.format(start)} - ${timeFormatter.format(end)}"
}

private data class TemporalMatrixInsight(
    val activity: TimingActivity,
    val threatLevel: TemporalThreatLevel,
    val scoreLabel: String?,
    val summary: String,
    val matchedWindow: String?,
    val warnings: List<String>,
    val usesCachedTiming: Boolean,
)

private enum class TemporalThreatLevel(
    val label: String,
    val emoji: String,
) {
    SUPPORTIVE("Supportive", "🟢"),
    MIXED("Mixed", "🟡"),
    FRICTION("Friction", "🔴"),
}

private fun buildTemporalInsight(
    event: TemporalMatrixEvent,
    adviceByActivity: Map<TimingActivity, TimingAdvicePayload>,
    cachedAdviceActivities: Set<TimingActivity>,
    moonPhase: MoonPhaseInfoData?,
): TemporalMatrixInsight {
    val activity = inferTimingActivity(event.title)
    val payload = adviceByActivity[activity]
    val dayPayload = payload?.dayPayloadFor(event.start.toLocalDate())
    val matchedWindow = dayPayload?.bestHours.orEmpty().firstOrNull { hour ->
        event.overlaps(hour)
    }?.toWindowLabel()
    val warnings = dayPayload?.warnings.orEmpty().filter { it.isNotBlank() }
    val scoreLabel = dayPayload?.let { "${it.score}% ${it.rating}" }

    val threatLevel = when {
        matchedWindow != null -> TemporalThreatLevel.SUPPORTIVE
        (dayPayload?.score ?: 50) < 45 || warnings.isNotEmpty() -> TemporalThreatLevel.FRICTION
        else -> TemporalThreatLevel.MIXED
    }

    val summary = when {
        matchedWindow != null -> "This event lands inside one of the stronger ${activity.displayName.lowercase(Locale.getDefault())} windows."
        dayPayload != null && dayPayload.bestHours.orEmpty().isNotEmpty() -> "Timing reads ${dayPayload.rating.lowercase(Locale.getDefault())}. If this event can move, bias it toward ${dayPayload.bestHours.orEmpty().first().toWindowLabel()}."
        dayPayload != null -> "Timing reads ${dayPayload.rating.lowercase(Locale.getDefault())} for ${activity.displayName.lowercase(Locale.getDefault())}. Keep expectations realistic and reduce extra friction around the edges."
        moonPhase != null -> "No personalized timing read was available for this event, so treat the current ${moonPhase.phase.lowercase(Locale.getDefault())} phase as the broader weather."
        else -> "No live timing overlay was available for this event."
    }

    return TemporalMatrixInsight(
        activity = activity,
        threatLevel = threatLevel,
        scoreLabel = scoreLabel,
        summary = summary,
        matchedWindow = matchedWindow,
        warnings = warnings,
        usesCachedTiming = activity in cachedAdviceActivities,
    )
}

private fun TimingAdvicePayload.dayPayloadFor(date: LocalDate): TimingDayPayload? {
    val targetDate = date.toString()
    return allDays.orEmpty().firstOrNull { it.date == targetDate }
        ?: bestUpcoming?.takeIf { it.date == targetDate }
        ?: today.takeIf { it.date == targetDate }
}

private fun TemporalMatrixEvent.overlaps(hour: TimingHourPayload): Boolean {
    val startTime = hour.start.toTimingLocalTimeOrNull() ?: return false
    val endTime = hour.end.toTimingLocalTimeOrNull() ?: return false
    val eventStart = start.toLocalTime()
    val eventEnd = end.toLocalTime()
    return if (endTime > startTime) {
        eventStart < endTime && eventEnd > startTime
    } else {
        eventStart >= startTime || eventEnd <= endTime
    }
}

private fun inferTimingActivity(title: String): TimingActivity {
    val normalized = title.lowercase(Locale.getDefault())
    return when {
        normalized.contains("date") || normalized.contains("dinner") || normalized.contains("anniversary") -> TimingActivity.ROMANCE_DATE
        normalized.contains("interview") || normalized.contains("audition") -> TimingActivity.JOB_INTERVIEW
        normalized.contains("contract") || normalized.contains("sign") || normalized.contains("lease") -> TimingActivity.SIGNING_CONTRACTS
        normalized.contains("travel") || normalized.contains("flight") || normalized.contains("trip") -> TimingActivity.TRAVEL
        normalized.contains("budget") || normalized.contains("bank") || normalized.contains("invoice") || normalized.contains("payment") -> TimingActivity.FINANCIAL_DECISION
        normalized.contains("meditation") || normalized.contains("therapy") || normalized.contains("yoga") || normalized.contains("breath") -> TimingActivity.MEDITATION_SPIRITUAL
        normalized.contains("launch") || normalized.contains("kickoff") || normalized.contains("start") -> TimingActivity.STARTING_PROJECT
        normalized.contains("write") || normalized.contains("design") || normalized.contains("brainstorm") || normalized.contains("record") -> TimingActivity.CREATIVE_WORK
        else -> TimingActivity.BUSINESS_MEETING
    }
}

private suspend fun loadUpcomingEvents(
    context: Context,
    hoursAhead: Int = 48,
): List<TemporalMatrixEvent> = withContext(Dispatchers.IO) {
    val now = System.currentTimeMillis()
    val end = now + hoursAhead * HOUR_IN_MILLIS
    val projection = arrayOf(
        CalendarContract.Instances.BEGIN,
        CalendarContract.Instances.END,
        CalendarContract.Instances.TITLE,
        CalendarContract.Instances.EVENT_LOCATION,
        CalendarContract.Instances.ALL_DAY,
    )
    val zoneId = ZoneId.systemDefault()
    val uri = CalendarContract.Instances.CONTENT_URI.buildUpon().also { builder ->
        ContentUris.appendId(builder, now)
        ContentUris.appendId(builder, end)
    }.build()

    buildList {
        context.contentResolver.query(
            uri,
            projection,
            "${CalendarContract.Instances.VISIBLE} = 1",
            null,
            "${CalendarContract.Instances.BEGIN} ASC",
        )?.use { cursor ->
            val beginIndex = cursor.getColumnIndexOrThrow(CalendarContract.Instances.BEGIN)
            val endIndex = cursor.getColumnIndexOrThrow(CalendarContract.Instances.END)
            val titleIndex = cursor.getColumnIndexOrThrow(CalendarContract.Instances.TITLE)
            val locationIndex = cursor.getColumnIndexOrThrow(CalendarContract.Instances.EVENT_LOCATION)
            val allDayIndex = cursor.getColumnIndexOrThrow(CalendarContract.Instances.ALL_DAY)

            while (cursor.moveToNext()) {
                val begin = cursor.getLong(beginIndex)
                val finish = cursor.getLong(endIndex)
                val allDay = cursor.getInt(allDayIndex) == 1
                if (allDay || begin < now) {
                    continue
                }

                add(
                    TemporalMatrixEvent(
                        title = cursor.getString(titleIndex)?.takeIf { it.isNotBlank() } ?: "Untitled event",
                        location = cursor.getString(locationIndex),
                        start = Instant.ofEpochMilli(begin).atZone(zoneId),
                        end = Instant.ofEpochMilli(finish).atZone(zoneId),
                    ),
                )
            }
        }
    }
}

private fun hasCalendarPermission(context: Context): Boolean =
    ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALENDAR) == PackageManager.PERMISSION_GRANTED

private val dayFormatter: DateTimeFormatter = DateTimeFormatter.ofPattern("EEE MMM d")
private val timeFormatter: DateTimeFormatter = DateTimeFormatter.ofPattern("HH:mm")
private const val HOUR_IN_MILLIS = 60L * 60L * 1000L