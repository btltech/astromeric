package com.astromeric.android.app

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.ExactTransitAspectData
import java.time.Instant
import java.time.OffsetDateTime

class ExactTransitAlarmScheduler(
    private val context: Context,
    private val snapshotStore: MorningBriefWidgetSnapshotStore,
) {
    private val alarmManager = context.getSystemService(AlarmManager::class.java)

    fun reschedule(
        profileName: String,
        transits: List<ExactTransitAspectData>,
        majorOnly: Boolean,
        source: AstroDataSource,
        isCached: Boolean,
    ) {
        clearScheduledTransitAlarms()
        if (!canScheduleExactAlarms()) return

        val now = Instant.now()
        val scheduledHashes = mutableSetOf<String>()

        transits.asSequence()
            .filter { transit ->
                transit.exactInstant()?.isAfter(now) == true && (!majorOnly || transit.isMajorTransit())
            }
            .take(MAX_SCHEDULED_TRANSITS)
            .forEach { transit ->
                val hash = transit.scheduleHash(profileName)
                val requestCode = requestCodeFor(hash)
                val pendingIntent = PendingIntent.getBroadcast(
                    context,
                    requestCode,
                    transitIntent(profileName, transit, requestCode, source, isCached),
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
                )
                alarmManager?.setExactAndAllowWhileIdle(
                    AlarmManager.RTC_WAKEUP,
                    requireNotNull(transit.exactInstant()).toEpochMilli(),
                    pendingIntent,
                )
                scheduledHashes += hash
            }

        snapshotStore.setScheduledTransitHashes(scheduledHashes)
    }

    fun clearScheduledTransitAlarms() {
        snapshotStore.scheduledTransitHashes().forEach { hash ->
            alarmManager?.cancel(
                PendingIntent.getBroadcast(
                    context,
                    requestCodeFor(hash),
                    Intent(context, ExactTransitAlarmReceiver::class.java).setAction(ACTION_EXACT_TRANSIT_ALARM),
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
                ),
            )
        }
        snapshotStore.setScheduledTransitHashes(emptySet())
    }

    fun canScheduleExactAlarms(): Boolean {
        return if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) {
            true
        } else {
            alarmManager?.canScheduleExactAlarms() == true
        }
    }

    private fun transitIntent(
        profileName: String,
        transit: ExactTransitAspectData,
        notificationId: Int,
        source: AstroDataSource,
        isCached: Boolean,
    ): Intent = Intent(context, ExactTransitAlarmReceiver::class.java)
        .setAction(ACTION_EXACT_TRANSIT_ALARM)
        .putExtra(EXTRA_PROFILE_NAME, profileName)
        .putExtra(EXTRA_TRANSIT_PLANET, transit.transitPlanet)
        .putExtra(EXTRA_NATAL_POINT, transit.natalPoint)
        .putExtra(EXTRA_ASPECT, transit.aspect)
        .putExtra(EXTRA_INTERPRETATION, transit.interpretation)
        .putExtra(EXTRA_SOURCE, source.name)
        .putExtra(EXTRA_SOURCE_IS_CACHED, isCached)
        .putExtra(EXTRA_NOTIFICATION_ID, notificationId)

    private fun ExactTransitAspectData.exactInstant(): Instant? =
        runCatching { OffsetDateTime.parse(exactDate).toInstant() }.getOrNull()

    private fun ExactTransitAspectData.isMajorTransit(): Boolean {
        return significance.equals("major", ignoreCase = true) ||
            aspect.equals("square", ignoreCase = true) ||
            aspect.equals("opposition", ignoreCase = true) ||
            (aspect.equals("conjunction", ignoreCase = true) && orb <= 1.0)
    }

    private fun ExactTransitAspectData.scheduleHash(profileName: String): String {
        return listOf(profileName, transitPlanet, aspect, natalPoint, exactDate).joinToString(separator = "|")
    }

    companion object {
        const val ACTION_EXACT_TRANSIT_ALARM = "com.astromeric.android.action.EXACT_TRANSIT_ALARM"
        const val EXTRA_PROFILE_NAME = "exact_transit.profile_name"
        const val EXTRA_TRANSIT_PLANET = "exact_transit.transit_planet"
        const val EXTRA_NATAL_POINT = "exact_transit.natal_point"
        const val EXTRA_ASPECT = "exact_transit.aspect"
        const val EXTRA_INTERPRETATION = "exact_transit.interpretation"
        const val EXTRA_SOURCE = "exact_transit.source"
        const val EXTRA_SOURCE_IS_CACHED = "exact_transit.source_is_cached"
        const val EXTRA_NOTIFICATION_ID = "exact_transit.notification_id"
        private const val MAX_SCHEDULED_TRANSITS = 20

        private fun requestCodeFor(hash: String): Int = hash.hashCode() and Int.MAX_VALUE
    }
}