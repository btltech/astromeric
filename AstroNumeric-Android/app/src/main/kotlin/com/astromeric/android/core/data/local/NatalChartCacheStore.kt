package com.astromeric.android.core.data.local

import android.content.Context
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.ChartData
import com.google.gson.Gson

data class CachedNatalChartSnapshot(
    val chart: ChartData,
    val source: AstroDataSource,
    val cachedAtEpochMillis: Long,
)

class NatalChartCacheStore(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val gson = Gson()

    fun read(profileId: Int): CachedNatalChartSnapshot? {
        val payload = preferences.getString(chartKey(profileId), null) ?: return null
        val cachedAt = preferences.getLong(cachedAtKey(profileId), 0L)
        val chart = runCatching { gson.fromJson(payload, ChartData::class.java) }.getOrNull() ?: return null
        return CachedNatalChartSnapshot(
            chart = chart,
            source = AstroDataSource.fromStorage(preferences.getString(sourceKey(profileId), null)),
            cachedAtEpochMillis = cachedAt,
        )
    }

    fun write(
        profileId: Int,
        chart: ChartData,
        source: AstroDataSource,
    ): Long {
        val cachedAt = System.currentTimeMillis()
        preferences.edit()
            .putString(chartKey(profileId), gson.toJson(chart))
            .putString(sourceKey(profileId), source.name)
            .putLong(cachedAtKey(profileId), cachedAt)
            .apply()
        return cachedAt
    }

    fun clearAll() {
        preferences.edit().clear().apply()
    }

    private fun chartKey(profileId: Int): String = "chart.$profileId.json"

    private fun sourceKey(profileId: Int): String = "chart.$profileId.source"

    private fun cachedAtKey(profileId: Int): String = "chart.$profileId.cached_at"

    private companion object {
        private const val PREFS_NAME = "natal_chart_cache"
    }
}