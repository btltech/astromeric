package com.astromeric.android.core.data.local

import android.content.Context
import com.astromeric.android.core.model.AstroDataSource

data class SavedExactTransitLoadStatus(
    val source: AstroDataSource,
    val isCached: Boolean,
    val recordedAtEpochMillis: Long,
)

class ExactTransitLoadStatusStore(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun read(profileId: Int): SavedExactTransitLoadStatus? {
        val recordedAt = preferences.getLong(recordedAtKey(profileId), 0L)
        if (recordedAt <= 0L) {
            return null
        }
        return SavedExactTransitLoadStatus(
            source = AstroDataSource.fromStorage(preferences.getString(sourceKey(profileId), null)),
            isCached = preferences.getBoolean(cachedKey(profileId), false),
            recordedAtEpochMillis = recordedAt,
        )
    }

    fun write(
        profileId: Int,
        source: AstroDataSource,
        isCached: Boolean,
    ): Long {
        val recordedAt = System.currentTimeMillis()
        preferences.edit()
            .putString(sourceKey(profileId), source.name)
            .putBoolean(cachedKey(profileId), isCached)
            .putLong(recordedAtKey(profileId), recordedAt)
            .apply()
        return recordedAt
    }

    private fun sourceKey(profileId: Int): String = "exact_transits.$profileId.last_source"

    private fun cachedKey(profileId: Int): String = "exact_transits.$profileId.last_is_cached"

    private fun recordedAtKey(profileId: Int): String = "exact_transits.$profileId.last_recorded_at"

    private companion object {
        private const val PREFS_NAME = "exact_transit_load_status"
    }
}