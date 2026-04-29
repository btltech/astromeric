package com.astromeric.android.core.data.local

import android.content.Context
import com.astromeric.android.core.model.TimingActivity
import com.astromeric.android.core.model.TimingAdvicePayload
import com.google.gson.Gson

data class CachedTimingAdviceSnapshot(
    val payload: TimingAdvicePayload,
    val cachedAtEpochMillis: Long,
)

class TimingAdviceCacheStore(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val gson = Gson()

    fun read(profileId: Int, activity: TimingActivity): CachedTimingAdviceSnapshot? {
        val payload = preferences.getString(payloadKey(profileId, activity), null) ?: return null
        val cachedAt = preferences.getLong(cachedAtKey(profileId, activity), 0L)
        val advice = runCatching { gson.fromJson(payload, TimingAdvicePayload::class.java) }.getOrNull() ?: return null
        return CachedTimingAdviceSnapshot(
            payload = advice,
            cachedAtEpochMillis = cachedAt,
        )
    }

    fun write(profileId: Int, activity: TimingActivity, payload: TimingAdvicePayload): Long {
        val cachedAt = System.currentTimeMillis()
        preferences.edit()
            .putString(payloadKey(profileId, activity), gson.toJson(payload))
            .putLong(cachedAtKey(profileId, activity), cachedAt)
            .apply()
        return cachedAt
    }

    private fun payloadKey(profileId: Int, activity: TimingActivity): String =
        "timing.$profileId.${activity.wireValue}.json"

    private fun cachedAtKey(profileId: Int, activity: TimingActivity): String =
        "timing.$profileId.${activity.wireValue}.cached_at"

    private companion object {
        private const val PREFS_NAME = "timing_advice_cache"
    }
}