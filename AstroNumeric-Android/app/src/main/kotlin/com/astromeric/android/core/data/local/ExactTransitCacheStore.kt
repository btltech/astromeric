package com.astromeric.android.core.data.local

import android.content.Context
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.ExactTransitAspectData
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

data class CachedExactTransitSnapshot(
    val transits: List<ExactTransitAspectData>,
    val source: AstroDataSource,
    val cachedAtEpochMillis: Long,
)

class ExactTransitCacheStore(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val gson = Gson()

    fun read(profileId: Int): CachedExactTransitSnapshot? {
        val raw = preferences.getString(payloadKey(profileId), null) ?: return null
        val cachedAt = preferences.getLong(cachedAtKey(profileId), 0L)
        val type = object : TypeToken<List<ExactTransitAspectData>>() {}.type
        val transits = runCatching {
            gson.fromJson<List<ExactTransitAspectData>>(raw, type)
        }.getOrNull() ?: return null

        return CachedExactTransitSnapshot(
            transits = transits,
            source = AstroDataSource.fromStorage(preferences.getString(sourceKey(profileId), null)),
            cachedAtEpochMillis = cachedAt,
        )
    }

    fun write(
        profileId: Int,
        transits: List<ExactTransitAspectData>,
        source: AstroDataSource,
    ): Long {
        val cachedAt = System.currentTimeMillis()
        preferences.edit()
            .putString(payloadKey(profileId), gson.toJson(transits))
            .putString(sourceKey(profileId), source.name)
            .putLong(cachedAtKey(profileId), cachedAt)
            .apply()
        return cachedAt
    }

    private fun payloadKey(profileId: Int): String = "exact_transits.$profileId.json"

    private fun sourceKey(profileId: Int): String = "exact_transits.$profileId.source"

    private fun cachedAtKey(profileId: Int): String = "exact_transits.$profileId.cached_at"

    private companion object {
        private const val PREFS_NAME = "exact_transit_cache"
    }
}