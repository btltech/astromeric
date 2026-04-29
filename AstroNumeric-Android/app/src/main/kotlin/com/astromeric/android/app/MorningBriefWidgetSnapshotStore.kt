package com.astromeric.android.app

import android.content.Context
import com.astromeric.android.core.model.MorningBriefData
import org.json.JSONArray

data class MorningBriefWidgetSnapshot(
    val greeting: String,
    val vibe: String,
    val bullets: List<String>,
    val personalDay: Int?,
    val moonPhase: String,
    val moonEmoji: String,
    val moonGuidance: String,
    val lastUpdatedEpochMillis: Long?,
)

class MorningBriefWidgetSnapshotStore(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun read(): MorningBriefWidgetSnapshot {
        val rawBullets = preferences.getString(KEY_BULLETS, null)
        val bullets = if (rawBullets.isNullOrBlank()) {
            listOf("Open AstroNumeric to refresh your morning brief.")
        } else {
            buildList {
                val json = JSONArray(rawBullets)
                repeat(json.length()) { index ->
                    add(json.optString(index))
                }
            }.filter { it.isNotBlank() }.ifEmpty {
                listOf("Open AstroNumeric to refresh your morning brief.")
            }
        }

        return MorningBriefWidgetSnapshot(
            greeting = preferences.getString(KEY_GREETING, null).orEmpty(),
            vibe = preferences.getString(KEY_VIBE, null).orEmpty(),
            bullets = bullets,
            personalDay = preferences.takeIf { it.contains(KEY_PERSONAL_DAY) }?.getInt(KEY_PERSONAL_DAY, 0),
            moonPhase = preferences.getString(KEY_MOON_PHASE, null).orEmpty(),
            moonEmoji = preferences.getString(KEY_MOON_EMOJI, null) ?: DEFAULT_MOON_EMOJI,
            moonGuidance = preferences.getString(KEY_MOON_GUIDANCE, null).orEmpty(),
            lastUpdatedEpochMillis = preferences.takeIf { it.contains(KEY_LAST_UPDATED) }?.getLong(KEY_LAST_UPDATED, 0L),
        )
    }

    fun writeSnapshot(
        morningBrief: MorningBriefData?,
        moonPhaseName: String?,
        moonGuidance: String? = null,
    ) {
        val current = read()
        val nextBullets = morningBrief?.toWidgetBullets()?.takeIf { it.isNotEmpty() } ?: current.bullets
        val nextPersonalDay = morningBrief?.personalDay ?: current.personalDay
        val nextMoonPhase = moonPhaseName ?: current.moonPhase
        val nextGreeting = morningBrief?.greeting?.takeIf { it.isNotBlank() } ?: current.greeting
        val nextVibe = morningBrief?.vibe?.takeIf { it.isNotBlank() } ?: current.vibe
        val nextMoonGuidance = moonGuidance?.takeIf { it.isNotBlank() } ?: current.moonGuidance

        preferences.edit()
            .putString(KEY_GREETING, nextGreeting)
            .putString(KEY_VIBE, nextVibe)
            .putString(KEY_BULLETS, JSONArray(nextBullets).toString())
            .apply {
                if (nextPersonalDay != null) putInt(KEY_PERSONAL_DAY, nextPersonalDay) else remove(KEY_PERSONAL_DAY)
            }
            .putString(KEY_MOON_PHASE, nextMoonPhase)
            .putString(KEY_MOON_EMOJI, moonEmojiFor(nextMoonPhase))
            .putString(KEY_MOON_GUIDANCE, nextMoonGuidance)
            .putLong(KEY_LAST_UPDATED, System.currentTimeMillis())
            .apply()
    }

    fun lastDailyReadingNotificationDate(): String? = preferences.getString(KEY_LAST_DAILY_READING_DATE, null)

    fun markDailyReadingNotification(date: String) {
        preferences.edit().putString(KEY_LAST_DAILY_READING_DATE, date).apply()
    }

    fun lastTransitAlertNotificationDate(): String? = preferences.getString(KEY_LAST_TRANSIT_ALERT_DATE, null)

    fun markTransitAlertNotification(date: String) {
        preferences.edit().putString(KEY_LAST_TRANSIT_ALERT_DATE, date).apply()
    }

    fun lastMoonEventNotificationKey(): String? = preferences.getString(KEY_LAST_MOON_EVENT_KEY, null)

    fun markMoonEventNotification(key: String) {
        preferences.edit().putString(KEY_LAST_MOON_EVENT_KEY, key).apply()
    }

    fun lastHabitReminderNotificationDate(): String? = preferences.getString(KEY_LAST_HABIT_REMINDER_DATE, null)

    fun markHabitReminderNotification(date: String) {
        preferences.edit().putString(KEY_LAST_HABIT_REMINDER_DATE, date).apply()
    }

    fun lastTimingAlertNotificationDate(): String? = preferences.getString(KEY_LAST_TIMING_ALERT_DATE, null)

    fun markTimingAlertNotification(date: String) {
        preferences.edit().putString(KEY_LAST_TIMING_ALERT_DATE, date).apply()
    }

    fun lastRetrogradeAlertEpochMillis(): Long? =
        preferences.takeIf { it.contains(KEY_LAST_RETROGRADE_ALERT_AT) }
            ?.getLong(KEY_LAST_RETROGRADE_ALERT_AT, 0L)

    fun markRetrogradeAlert(epochMillis: Long) {
        preferences.edit().putLong(KEY_LAST_RETROGRADE_ALERT_AT, epochMillis).apply()
    }

    fun lastMercuryRetrogradeState(): Boolean = preferences.getBoolean(KEY_LAST_MERCURY_RETROGRADE_STATE, false)

    fun markMercuryRetrogradeState(isRetrograde: Boolean) {
        preferences.edit().putBoolean(KEY_LAST_MERCURY_RETROGRADE_STATE, isRetrograde).apply()
    }

    fun scheduledTransitHashes(): Set<String> = preferences.getStringSet(KEY_SCHEDULED_TRANSIT_HASHES, emptySet()).orEmpty()

    fun setScheduledTransitHashes(hashes: Set<String>) {
        preferences.edit().putStringSet(KEY_SCHEDULED_TRANSIT_HASHES, hashes).apply()
    }

    private fun MorningBriefData.toWidgetBullets(): List<String> = buildList {
        vibe?.takeIf { it.isNotBlank() }?.let(::add)
        addAll(bullets.mapNotNull { bullet -> bullet.text.takeIf { it.isNotBlank() } })
        if (isEmpty()) {
            greeting?.takeIf { it.isNotBlank() }?.let(::add)
        }
    }

    private fun moonEmojiFor(phaseName: String): String = when {
        phaseName.contains("new", ignoreCase = true) -> "🌑"
        phaseName.contains("waxing crescent", ignoreCase = true) -> "🌒"
        phaseName.contains("first quarter", ignoreCase = true) -> "🌓"
        phaseName.contains("waxing gibbous", ignoreCase = true) -> "🌔"
        phaseName.contains("full", ignoreCase = true) -> "🌕"
        phaseName.contains("waning gibbous", ignoreCase = true) -> "🌖"
        phaseName.contains("last quarter", ignoreCase = true) -> "🌗"
        phaseName.contains("waning crescent", ignoreCase = true) -> "🌘"
        else -> DEFAULT_MOON_EMOJI
    }

    private companion object {
        private const val PREFS_NAME = "morning_brief_widget_snapshot"
        private const val KEY_GREETING = "widget.greeting"
        private const val KEY_VIBE = "widget.vibe"
        private const val KEY_BULLETS = "widget.bullets"
        private const val KEY_PERSONAL_DAY = "widget.personal_day"
        private const val KEY_MOON_PHASE = "widget.moon_phase"
        private const val KEY_MOON_EMOJI = "widget.moon_emoji"
        private const val KEY_MOON_GUIDANCE = "widget.moon_guidance"
        private const val KEY_LAST_UPDATED = "widget.last_updated"
        private const val KEY_LAST_DAILY_READING_DATE = "widget.last_daily_reading_date"
        private const val KEY_LAST_TRANSIT_ALERT_DATE = "widget.last_transit_alert_date"
        private const val KEY_LAST_MOON_EVENT_KEY = "widget.last_moon_event_key"
        private const val KEY_LAST_HABIT_REMINDER_DATE = "widget.last_habit_reminder_date"
        private const val KEY_LAST_TIMING_ALERT_DATE = "widget.last_timing_alert_date"
        private const val KEY_LAST_RETROGRADE_ALERT_AT = "widget.last_retrograde_alert_at"
        private const val KEY_LAST_MERCURY_RETROGRADE_STATE = "widget.last_mercury_retrograde_state"
        private const val KEY_SCHEDULED_TRANSIT_HASHES = "widget.scheduled_transit_hashes"
        private const val DEFAULT_MOON_EMOJI = "🌑"
    }
}