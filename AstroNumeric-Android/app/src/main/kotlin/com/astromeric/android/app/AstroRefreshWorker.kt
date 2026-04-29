package com.astromeric.android.app

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.astromeric.android.core.data.local.DailyTransitReportCacheStore
import com.astromeric.android.core.data.local.ExactTransitCacheStore
import com.astromeric.android.core.data.local.ExactTransitLoadStatusStore
import com.astromeric.android.core.data.local.NatalChartCacheStore
import com.astromeric.android.core.data.local.TimingAdviceCacheStore
import com.astromeric.android.core.data.repository.loadDailyTransitReportWithCacheFallback
import com.astromeric.android.core.data.repository.loadTimingAdviceWithCacheFallback
import com.astromeric.android.core.data.repository.loadUpcomingExactTransitsWithCacheFallback
import com.astromeric.android.core.ephemeris.LocalSwissEphemerisEngine
import com.astromeric.android.core.model.AlertFrequency
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.DailyTransitAspectData
import com.astromeric.android.core.model.DailyTransitReportData
import kotlinx.coroutines.flow.first
import java.time.Duration
import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.temporal.ChronoUnit

class AstroRefreshWorker(
    context: Context,
    params: WorkerParameters,
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result = runAstroRefresh(applicationContext)
}

internal suspend fun runAstroRefresh(
    applicationContext: Context,
    forceExactTransitDiagnostics: Boolean = false,
): androidx.work.ListenableWorker.Result {
    val application = applicationContext as? AstroNumericApplication ?: return androidx.work.ListenableWorker.Result.success()
    val appContainer = application.appContainer
    val selectedProfile = appContainer.profileRepository.selectedProfile.first() ?: return androidx.work.ListenableWorker.Result.success()

    val preferencesStore = appContainer.preferencesStore
    val remoteDataSource = appContainer.remoteDataSource
    val widgetSnapshotStore = MorningBriefWidgetSnapshotStore(applicationContext)
    val dailyTransitReportCacheStore = DailyTransitReportCacheStore(applicationContext)
    val exactTransitCacheStore = ExactTransitCacheStore(applicationContext)
    val exactTransitLoadStatusStore = ExactTransitLoadStatusStore(applicationContext)
    val natalChartCacheStore = NatalChartCacheStore(applicationContext)
    val localEphemerisEngine = LocalSwissEphemerisEngine.getInstance(applicationContext)
    val timingAdviceCacheStore = TimingAdviceCacheStore(applicationContext)
    val notificationService = AstroNotificationService(applicationContext)
    val exactTransitAlarmScheduler = ExactTransitAlarmScheduler(applicationContext, widgetSnapshotStore)
    val todayKey = LocalDate.now().toString()
    val now = LocalTime.now()

    val morningBrief = remoteDataSource.fetchMorningBrief(selectedProfile).getOrNull()
    val moonPhase = remoteDataSource.fetchMoonPhase().getOrNull()
    val transitReportResult = loadDailyTransitReportWithCacheFallback(
        profile = selectedProfile,
        remoteDataSource = remoteDataSource,
        cacheStore = dailyTransitReportCacheStore,
    )
    val transitReport = transitReportResult.report
    val doDont = remoteDataSource.fetchDoDont(selectedProfile).getOrNull()
    val timingActivity = preferencesStore.timingAlertActivity.first()
    val timingAdvice = loadTimingAdviceWithCacheFallback(
        activity = timingActivity,
        profile = selectedProfile,
        remoteDataSource = remoteDataSource,
        cacheStore = timingAdviceCacheStore,
    ).payload
    val localHabits = preferencesStore.localHabits.first()
    val incompleteHabits = localHabits.filterNot { it.isCompletedToday }

    widgetSnapshotStore.writeSnapshot(
        morningBrief = morningBrief,
        moonPhaseName = moonPhase?.phase,
        moonGuidance = moonPhase?.influence,
    )
    MorningBriefWidgetProvider.refreshAllWidgets(applicationContext)

    val dailyReadingEnabled = preferencesStore.notifyDailyReadingEnabled.first()
    if (
        dailyReadingEnabled &&
        morningBrief != null &&
        widgetSnapshotStore.lastDailyReadingNotificationDate() != todayKey &&
        isWithinNotificationWindow(
            now = now,
            hour = preferencesStore.dailyReadingHour.first(),
            minute = preferencesStore.dailyReadingMinute.first(),
        )
    ) {
        notificationService.showDailyReadingNotification(
            profileName = selectedProfile.name,
            brief = morningBrief,
        )
        widgetSnapshotStore.markDailyReadingNotification(todayKey)
    }

    val moonEventsEnabled = preferencesStore.notifyMoonEventsEnabled.first()
    val moonEventKey = moonPhase?.phase?.takeIf(::isMajorMoonEvent)?.let { "$todayKey:$it" }
    if (
        moonEventsEnabled &&
        moonPhase != null &&
        moonEventKey != null &&
        widgetSnapshotStore.lastMoonEventNotificationKey() != moonEventKey
    ) {
        notificationService.showMoonEventNotification(
            phaseName = moonPhase.phase,
            influence = moonPhase.influence,
        )
        widgetSnapshotStore.markMoonEventNotification(moonEventKey)
    }

    val habitReminderEnabled = preferencesStore.notifyHabitReminderEnabled.first()
    if (
        habitReminderEnabled &&
        incompleteHabits.isNotEmpty() &&
        widgetSnapshotStore.lastHabitReminderNotificationDate() != todayKey &&
        isWithinNotificationWindow(
            now = now,
            hour = preferencesStore.habitReminderHour.first(),
            minute = preferencesStore.habitReminderMinute.first(),
        )
    ) {
        notificationService.showHabitReminderNotification(incompleteHabits)
        widgetSnapshotStore.markHabitReminderNotification(todayKey)
    }

    val timingAlertEnabled = preferencesStore.notifyTimingAlertEnabled.first()
    if (
        timingAlertEnabled &&
        timingAdvice != null &&
        widgetSnapshotStore.lastTimingAlertNotificationDate() != todayKey &&
        isWithinNotificationWindow(
            now = now,
            hour = preferencesStore.timingAlertHour.first(),
            minute = preferencesStore.timingAlertMinute.first(),
        )
    ) {
        notificationService.showTimingAlertNotification(
            activity = timingActivity,
            advice = timingAdvice,
        )
        widgetSnapshotStore.markTimingAlertNotification(todayKey)
    }

    val transitAlertsEnabled = preferencesStore.notifyTransitAlertEnabled.first()
    val majorOnly = preferencesStore.transitAlertsMajorOnly.first()
    if (transitAlertsEnabled || forceExactTransitDiagnostics) {
        val exactTransitResult = loadUpcomingExactTransitsWithCacheFallback(
            profile = selectedProfile,
            remoteDataSource = remoteDataSource,
            cacheStore = exactTransitCacheStore,
            natalChartCacheStore = natalChartCacheStore,
            localEphemerisEngine = localEphemerisEngine,
        )
        exactTransitResult.source?.let { source ->
            exactTransitLoadStatusStore.write(
                profileId = selectedProfile.id,
                source = source,
                isCached = exactTransitResult.isCached,
            )
        }
        if (transitAlertsEnabled) {
            exactTransitResult.transits?.let { exactTransits ->
                exactTransitAlarmScheduler.reschedule(
                    profileName = selectedProfile.name,
                    transits = exactTransits,
                    majorOnly = majorOnly,
                    source = exactTransitResult.source ?: AstroDataSource.BACKEND,
                    isCached = exactTransitResult.isCached,
                )
            }
        }
    } else {
        exactTransitAlarmScheduler.clearScheduledTransitAlarms()
    }

    if (
        transitAlertsEnabled &&
        transitReport != null &&
        widgetSnapshotStore.lastTransitAlertNotificationDate() != todayKey &&
        isWithinNotificationWindow(
            now = now,
            hour = preferencesStore.transitAlertHour.first(),
            minute = preferencesStore.transitAlertMinute.first(),
        ) &&
        transitReport.shouldNotify(majorOnly = majorOnly)
    ) {
        notificationService.showTransitAlertNotification(
            profileName = selectedProfile.name,
            report = transitReport,
            source = transitReportResult.source,
            isCached = transitReportResult.isCached,
        )
        widgetSnapshotStore.markTransitAlertNotification(todayKey)
    }

    val retrogradeAlertsEnabled = preferencesStore.mercuryRetrogradeAlertsEnabled.first()
    val alertFrequency = preferencesStore.alertFrequency.first()
    val currentRetrogradeState = doDont?.mercuryRetrograde == true
    val previousRetrogradeState = widgetSnapshotStore.lastMercuryRetrogradeState()
    val retrogradeTransition = currentRetrogradeState != previousRetrogradeState
    val shouldSendRetrogradeAlert = retrogradeAlertsEnabled && shouldSendRetrogradeAlert(
        currentRetrogradeState = currentRetrogradeState,
        previousRetrogradeState = previousRetrogradeState,
        alertFrequency = alertFrequency,
        lastAlertAt = widgetSnapshotStore.lastRetrogradeAlertEpochMillis()?.let(Instant::ofEpochMilli),
    )
    if (shouldSendRetrogradeAlert) {
        val supportingLine = if (currentRetrogradeState) {
            doDont?.donts?.firstOrNull()
        } else {
            "The current Mercury retrograde cycle has ended."
        }
        notificationService.showMercuryRetrogradeNotification(
            retrogradeActive = currentRetrogradeState,
            supportingLine = supportingLine,
        )
        widgetSnapshotStore.markRetrogradeAlert(System.currentTimeMillis())
    }
    if (retrogradeTransition || doDont != null) {
        widgetSnapshotStore.markMercuryRetrogradeState(currentRetrogradeState)
    }

    return androidx.work.ListenableWorker.Result.success()
}

private fun isWithinNotificationWindow(
    now: LocalTime,
    hour: Int,
    minute: Int,
    windowMinutes: Long = 4 * 60,
): Boolean {
    val target = LocalTime.of(hour, minute)
    val minutesAfterTarget = Duration.between(target, now).toMinutes()
    return minutesAfterTarget in 0..windowMinutes
}

private fun isMajorMoonEvent(phaseName: String): Boolean =
    phaseName.contains("full", ignoreCase = true) || phaseName.contains("new", ignoreCase = true)

private fun DailyTransitReportData.shouldNotify(majorOnly: Boolean): Boolean {
    if (highlights.isEmpty()) return false
    return if (!majorOnly) {
        alertLevel.equals("high", ignoreCase = true) || alertLevel.equals("medium", ignoreCase = true)
    } else {
        highlights.any { it.isMajorTransit() }
    }
}

private fun DailyTransitAspectData.isMajorTransit(): Boolean {
    return aspect.equals("square", ignoreCase = true) ||
        aspect.equals("opposition", ignoreCase = true) ||
        (aspect.equals("conjunction", ignoreCase = true) && orb <= 1.0)
}

private fun shouldSendRetrogradeAlert(
    currentRetrogradeState: Boolean,
    previousRetrogradeState: Boolean,
    alertFrequency: AlertFrequency,
    lastAlertAt: Instant?,
): Boolean {
    if (alertFrequency == AlertFrequency.NONE) {
        return false
    }

    if (!currentRetrogradeState && previousRetrogradeState) {
        return alertFrequency == AlertFrequency.EVERY_RETROGRADE
    }

    if (!currentRetrogradeState) {
        return false
    }

    if (!previousRetrogradeState) {
        return true
    }

    val now = Instant.now()
    return when (alertFrequency) {
        AlertFrequency.EVERY_RETROGRADE -> false
        AlertFrequency.WEEKLY_DIGEST -> lastAlertAt == null || lastAlertAt.plus(7, ChronoUnit.DAYS).isBefore(now)
        AlertFrequency.ONCE_PER_YEAR -> lastAlertAt == null || lastAlertAt.plus(365, ChronoUnit.DAYS).isBefore(now)
        AlertFrequency.NONE -> false
    }
}