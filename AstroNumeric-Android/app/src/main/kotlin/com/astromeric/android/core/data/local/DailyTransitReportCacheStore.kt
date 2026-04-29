package com.astromeric.android.core.data.local

import android.content.Context
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.DailyTransitReportData
import com.google.gson.Gson

data class CachedDailyTransitReportSnapshot(
    val report: DailyTransitReportData,
    val source: AstroDataSource,
    val cachedAtEpochMillis: Long,
)

class DailyTransitReportCacheStore(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val gson = Gson()

    fun read(profileId: Int): CachedDailyTransitReportSnapshot? {
        val raw = preferences.getString(payloadKey(profileId), null) ?: return null
        val cachedAt = preferences.getLong(cachedAtKey(profileId), 0L)
        val report = runCatching { gson.fromJson(raw, DailyTransitReportData::class.java) }.getOrNull() ?: return null
        return CachedDailyTransitReportSnapshot(
            report = report,
            source = AstroDataSource.fromStorage(preferences.getString(sourceKey(profileId), null)),
            cachedAtEpochMillis = cachedAt,
        )
    }

    fun write(
        profileId: Int,
        report: DailyTransitReportData,
        source: AstroDataSource,
    ): Long {
        val cachedAt = System.currentTimeMillis()
        preferences.edit()
            .putString(payloadKey(profileId), gson.toJson(report))
            .putString(sourceKey(profileId), source.name)
            .putLong(cachedAtKey(profileId), cachedAt)
            .apply()
        return cachedAt
    }

    private fun payloadKey(profileId: Int): String = "daily_transit_report.$profileId.json"

    private fun sourceKey(profileId: Int): String = "daily_transit_report.$profileId.source"

    private fun cachedAtKey(profileId: Int): String = "daily_transit_report.$profileId.cached_at"

    private companion object {
        private const val PREFS_NAME = "daily_transit_report_cache"
    }
}