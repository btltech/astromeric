package com.astromeric.android.feature.guide

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.content.ContentUris
import android.provider.CalendarContract
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.Calendar
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class GuideCalendarContextProvider(
    private val context: Context,
) {
    suspend fun buildContextBlock(daysAhead: Int = 7): String? = withContext(Dispatchers.IO) {
        if (!hasPermission()) {
            return@withContext null
        }

        val now = System.currentTimeMillis()
        val end = now + daysAhead * DAY_IN_MILLIS
        val projection = arrayOf(
            CalendarContract.Instances.BEGIN,
            CalendarContract.Instances.END,
            CalendarContract.Instances.ALL_DAY,
        )
        val uri = CalendarContract.Instances.CONTENT_URI.buildUpon().also { builder ->
            ContentUris.appendId(builder, now)
            ContentUris.appendId(builder, end)
        }.build()

        val entries = mutableListOf<RedactedCalendarEntry>()
        context.contentResolver.query(
            uri,
            projection,
            "${CalendarContract.Instances.VISIBLE} = 1",
            null,
            "${CalendarContract.Instances.BEGIN} ASC",
        )?.use { cursor ->
            val beginIndex = cursor.getColumnIndexOrThrow(CalendarContract.Instances.BEGIN)
            val endIndex = cursor.getColumnIndexOrThrow(CalendarContract.Instances.END)
            val allDayIndex = cursor.getColumnIndexOrThrow(CalendarContract.Instances.ALL_DAY)

            while (cursor.moveToNext()) {
                val begin = cursor.getLong(beginIndex)
                val endTime = cursor.getLong(endIndex)
                val allDay = cursor.getInt(allDayIndex) == 1
                if (allDay || begin < now) {
                    continue
                }
                entries += RedactedCalendarEntry(
                    begin = begin,
                    end = endTime,
                )
            }
        }

        if (entries.isEmpty()) {
            return@withContext null
        }

        val dayFormatter = SimpleDateFormat("EEE MMM d", Locale.getDefault())
        val groupedByDay = entries.groupBy { it.dayKey }
        val busiestDay = groupedByDay.maxByOrNull { it.value.size }
        val shortestGapMinutes = entries.zipWithNext()
            .mapNotNull { (current, next) ->
                if (current.dayKey != next.dayKey) {
                    null
                } else {
                    ((next.begin - current.end).coerceAtLeast(0L) / 60000L).toInt()
                }
            }
            .minOrNull()
        val longestOpenWindowMinutes = buildList {
            add(((entries.first().begin - now).coerceAtLeast(0L) / 60000L).toInt())
            addAll(
                entries.zipWithNext().map { (current, next) ->
                    ((next.begin - current.end).coerceAtLeast(0L) / 60000L).toInt()
                },
            )
            add(((end - entries.last().end).coerceAtLeast(0L) / 60000L).toInt())
        }.maxOrNull()
        val lines = buildList {
            add("UPCOMING CALENDAR SUMMARY:")
            add("• ${entries.size} scheduled events across ${groupedByDay.size} day(s) in the next $daysAhead day(s).")
            busiestDay?.let { (dayKey, dayEntries) ->
                add("• Busiest day: ${dayFormatter.format(Date(dayKey))} with ${dayEntries.size} event(s).")
            }
            shortestGapMinutes?.let { gap ->
                if (gap <= 90) {
                    add("• Tightest cadence: only ${formatMinutes(gap)} between back-to-back events on the same day.")
                }
            }
            longestOpenWindowMinutes?.let { gap ->
                add("• Longest open window: ${formatMinutes(gap)} without a scheduled event.")
            }
            groupedByDay.entries
                .sortedBy { it.key }
                .take(5)
                .forEach { (dayKey, dayEntries) ->
                    val buckets = dayEntries.map { it.timeBucket }.distinct().joinToString(separator = ", ")
                    val compressed = dayEntries.isCompressedSchedule
                    val loadLabel = when {
                        dayEntries.size >= 4 -> "heavy load"
                        dayEntries.size == 3 -> "moderate load"
                        else -> "light load"
                    }
                    val compressedLabel = if (compressed) " · compressed schedule" else ""
                    add(
                        "• ${dayFormatter.format(Date(dayKey))}: ${dayEntries.size} event(s) across $buckets · $loadLabel$compressedLabel",
                    )
                }
            add("Titles, attendees, and exact times were intentionally redacted.")
        }

        lines.joinToString(separator = "\n")
    }

    fun hasPermission(): Boolean =
        ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALENDAR) == PackageManager.PERMISSION_GRANTED
}

private data class RedactedCalendarEntry(
    val begin: Long,
    val end: Long,
) {
    val dayKey: Long
        get() {
            val calendar = Calendar.getInstance().apply {
                timeInMillis = begin
                set(Calendar.HOUR_OF_DAY, 0)
                set(Calendar.MINUTE, 0)
                set(Calendar.SECOND, 0)
                set(Calendar.MILLISECOND, 0)
            }
            return calendar.timeInMillis
        }

    val timeBucket: String
        get() {
            val hour = ((begin / HOUR_IN_MILLIS) % 24).toInt()
            return when (hour) {
                in 5..11 -> "morning"
                in 12..16 -> "afternoon"
                in 17..21 -> "evening"
                else -> "late night"
            }
        }
}

private val List<RedactedCalendarEntry>.isCompressedSchedule: Boolean
    get() = zipWithNext().any { (current, next) ->
        current.dayKey == next.dayKey && (next.begin - current.end).coerceAtLeast(0L) <= 90L * 60L * 1000L
    }

private fun formatMinutes(minutes: Int): String {
    if (minutes < 60) {
        return "$minutes min"
    }

    val hours = minutes / 60
    val remainingMinutes = minutes % 60
    if (hours >= 24) {
        val days = hours / 24
        val remainingHours = hours % 24
        return if (remainingHours == 0) "$days d" else "$days d ${remainingHours} h"
    }
    return if (remainingMinutes == 0) "$hours h" else "$hours h ${remainingMinutes} min"
}

private const val HOUR_IN_MILLIS = 60L * 60L * 1000L
private const val DAY_IN_MILLIS = 24L * HOUR_IN_MILLIS