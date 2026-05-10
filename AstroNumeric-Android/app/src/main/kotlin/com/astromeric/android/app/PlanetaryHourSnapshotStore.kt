package com.astromeric.android.app

import android.content.Context
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

/**
 * Stores a pre-computed 24-hour planetary hour schedule as a JSON list.
 * Written by [AstroRefreshWorker]; read by [PlanetaryHourWidgetProvider].
 */
data class PlanetaryHourEntry(
    val rulerName: String,
    val rulerSymbol: String,
    val startEpochMillis: Long,
    val endEpochMillis: Long,
)

class PlanetaryHourSnapshotStore(context: Context) {

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val gson = Gson()

    fun write(schedule: List<PlanetaryHourEntry>) {
        prefs.edit()
            .putString(KEY_SCHEDULE, gson.toJson(schedule))
            .putLong(KEY_LAST_UPDATED, System.currentTimeMillis())
            .apply()
    }

    fun read(): List<PlanetaryHourEntry> {
        val raw = prefs.getString(KEY_SCHEDULE, null) ?: return emptyList()
        return runCatching {
            val type = object : TypeToken<List<PlanetaryHourEntry>>() {}.type
            gson.fromJson<List<PlanetaryHourEntry>>(raw, type)
        }.getOrDefault(emptyList())
    }

    fun lastUpdatedEpochMillis(): Long? =
        prefs.takeIf { it.contains(KEY_LAST_UPDATED) }?.getLong(KEY_LAST_UPDATED, 0L)

    companion object {
        private const val PREFS_NAME = "astro_planetary_hour_snapshot"
        private const val KEY_SCHEDULE = "schedule"
        private const val KEY_LAST_UPDATED = "last_updated"
    }
}
