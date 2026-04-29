package com.astromeric.android.app

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.astromeric.android.core.model.AstroNotificationCategory
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.DailyTransitReportData
import com.astromeric.android.core.model.LocalHabitData
import com.astromeric.android.core.model.MorningBriefData
import com.astromeric.android.core.model.TimingActivity
import com.astromeric.android.core.model.TimingAdvicePayload
import com.astromeric.android.core.model.toWindowLabel

class AstroNotificationService(
    private val context: Context,
) {
    fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return

        val manager = context.getSystemService(NotificationManager::class.java) ?: return
        val channels = AstroNotificationCategory.entries.map { category ->
            NotificationChannel(
                category.channelId,
                category.label,
                NotificationManager.IMPORTANCE_DEFAULT,
            ).apply {
                description = when (category) {
                    AstroNotificationCategory.DAILY_READING -> "Morning brief reminders and daily reading nudges"
                    AstroNotificationCategory.MOON_PHASE -> "Moon phase and lunar event alerts"
                    AstroNotificationCategory.HABIT_REMINDER -> "Habit reminder nudges"
                    AstroNotificationCategory.TIMING_ALERT -> "Timing tip notifications"
                    AstroNotificationCategory.TRANSIT_ALERT -> "Proactive transit alerts"
                }
            }
        }
        manager.createNotificationChannels(channels)
    }

    fun canPostNotifications(): Boolean {
        return Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
            ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) ==
            android.content.pm.PackageManager.PERMISSION_GRANTED
    }

    fun showDailyReadingNotification(
        profileName: String,
        brief: MorningBriefData,
    ) {
        if (!canPostNotifications()) return

        val lines = buildList {
            brief.vibe?.takeIf { it.isNotBlank() }?.let(::add)
            addAll(brief.bullets.mapNotNull { bullet -> bullet.text.takeIf { it.isNotBlank() } })
        }
        val content = lines.firstOrNull() ?: brief.greeting ?: "Your morning brief is ready."

        val notification = NotificationCompat.Builder(context, AstroNotificationCategory.DAILY_READING.channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("$profileName morning brief")
            .setContentText(content)
            .setStyle(
                NotificationCompat.BigTextStyle().bigText(
                    lines.take(3).joinToString(separator = "\n").ifBlank { content },
                ),
            )
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()

        NotificationManagerCompat.from(context).notify(1001, notification)
    }

    fun showMoonEventNotification(phaseName: String, influence: String?) {
        if (!canPostNotifications()) return

        val detail = influence?.takeIf { it.isNotBlank() }
            ?: "The lunar tone shifted. Open AstroNumeric for the updated brief."

        val notification = NotificationCompat.Builder(context, AstroNotificationCategory.MOON_PHASE.channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("$phaseName moon event")
            .setContentText(detail)
            .setStyle(NotificationCompat.BigTextStyle().bigText(detail))
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()

        NotificationManagerCompat.from(context).notify(1002, notification)
    }

    fun showTransitAlertNotification(
        profileName: String,
        report: DailyTransitReportData,
        source: AstroDataSource?,
        isCached: Boolean,
    ) {
        if (!canPostNotifications()) return

        val headline = report.highlights.firstOrNull()?.let { aspect ->
            "${aspect.transitPlanet} ${aspect.aspect.replaceFirstChar(Char::uppercase)} ${aspect.natalPoint}"
        } ?: "Your transit weather shifted."

        val detail = report.highlights.firstOrNull()?.interpretation
            ?.takeIf { it.isNotBlank() }
            ?: "${report.totalAspects} active transit aspect(s) are in play today."
        val provenanceLine = transitSourceLine(source = source, isCached = isCached)
        val contentText = listOfNotNull(headline, provenanceLine?.removePrefix("Source: ")).joinToString(separator = " • ")

        val notification = NotificationCompat.Builder(context, AstroNotificationCategory.TRANSIT_ALERT.channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("$profileName transit alert")
            .setContentText(contentText)
            .setStyle(
                NotificationCompat.BigTextStyle().bigText(
                    listOfNotNull(headline, detail, provenanceLine).joinToString(separator = "\n"),
                ),
            )
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        NotificationManagerCompat.from(context).notify(1003, notification)
    }

    fun showExactTransitNotification(
        profileName: String,
        transitPlanet: String,
        natalPoint: String,
        aspect: String,
        interpretation: String?,
        source: AstroDataSource?,
        isCached: Boolean,
        notificationId: Int,
    ) {
        if (!canPostNotifications()) return

        val headline = "$transitPlanet ${aspect.replaceFirstChar(Char::uppercase)} $natalPoint is exact now"
        val detail = interpretation?.takeIf { it.isNotBlank() }
            ?: "Open AstroNumeric to see how this transit sharpens your day."
        val provenanceLine = transitSourceLine(source = source, isCached = isCached)
        val contentText = listOfNotNull(headline, provenanceLine?.removePrefix("Source: ")).joinToString(separator = " • ")

        val notification = NotificationCompat.Builder(context, AstroNotificationCategory.TRANSIT_ALERT.channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("$profileName exact transit")
            .setContentText(contentText)
            .setStyle(
                NotificationCompat.BigTextStyle().bigText(
                    listOfNotNull(headline, detail, provenanceLine).joinToString(separator = "\n"),
                ),
            )
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        NotificationManagerCompat.from(context).notify(notificationId, notification)
    }

    fun showMercuryRetrogradeNotification(
        retrogradeActive: Boolean,
        supportingLine: String? = null,
    ) {
        if (!canPostNotifications()) return

        val title = if (retrogradeActive) {
            "Mercury retrograde is active"
        } else {
            "Mercury is direct again"
        }
        val detail = if (retrogradeActive) {
            supportingLine?.takeIf { it.isNotBlank() }
                ?: "Double-check travel, devices, and important messages before you commit."
        } else {
            supportingLine?.takeIf { it.isNotBlank() }
                ?: "The retrograde haze is lifting. It is a better moment to finalize conversations and plans."
        }

        val notification = NotificationCompat.Builder(context, AstroNotificationCategory.TRANSIT_ALERT.channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(detail)
            .setStyle(NotificationCompat.BigTextStyle().bigText(detail))
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()

        NotificationManagerCompat.from(context).notify(1006, notification)
    }

    fun showHabitReminderNotification(habits: List<LocalHabitData>) {
        if (!canPostNotifications() || habits.isEmpty()) return

        val title = if (habits.size == 1) {
            "Habit reminder"
        } else {
            "${habits.size} habits still open"
        }
        val lines = habits.take(3).map { "${it.emoji} ${it.name}" }
        val detail = lines.firstOrNull() ?: "Check in with your daily rituals."

        val notification = NotificationCompat.Builder(context, AstroNotificationCategory.HABIT_REMINDER.channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(detail)
            .setStyle(NotificationCompat.BigTextStyle().bigText(lines.joinToString(separator = "\n")))
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()

        NotificationManagerCompat.from(context).notify(1004, notification)
    }

    fun showTimingAlertNotification(
        activity: TimingActivity,
        advice: TimingAdvicePayload,
    ) {
        if (!canPostNotifications()) return

        val headline = advice.advice?.takeIf { it.isNotBlank() }
            ?: "Check today's best windows for ${activity.displayName.lowercase()}."
        val windows = when {
            advice.today.bestHours.orEmpty().isNotEmpty() -> "Best windows: ${advice.today.bestHours!!.take(2).joinToString { it.toWindowLabel() }}"
            advice.today.warnings.orEmpty().isNotEmpty() -> "Avoid: ${advice.today.warnings!!.take(2).joinToString()}"
            else -> advice.today.recommendations.orEmpty().firstOrNull().orEmpty()
        }

        val notification = NotificationCompat.Builder(context, AstroNotificationCategory.TIMING_ALERT.channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("${activity.emoji} Timing tip")
            .setContentText(headline)
            .setStyle(NotificationCompat.BigTextStyle().bigText(listOf(headline, windows).filter { it.isNotBlank() }.joinToString(separator = "\n")))
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()

        NotificationManagerCompat.from(context).notify(1005, notification)
    }

    private fun transitSourceLine(
        source: AstroDataSource?,
        isCached: Boolean,
    ): String? = when {
        source == null -> null
        isCached && source == AstroDataSource.LOCAL_SWISS -> "Source: cached Swiss scan"
        isCached && source == AstroDataSource.LOCAL_ESTIMATE -> "Source: cached local estimate"
        isCached -> "Source: cached backend scan"
        source == AstroDataSource.LOCAL_SWISS -> "Source: on-device Swiss scan"
        source == AstroDataSource.LOCAL_ESTIMATE -> "Source: local estimate"
        else -> "Source: backend scan"
    }
}