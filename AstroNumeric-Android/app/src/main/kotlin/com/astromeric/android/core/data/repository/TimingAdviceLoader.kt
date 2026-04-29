package com.astromeric.android.core.data.repository

import com.astromeric.android.core.data.local.TimingAdviceCacheStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.TimingActivity
import com.astromeric.android.core.model.TimingAdvicePayload

data class TimingAdviceLoadResult(
    val payload: TimingAdvicePayload? = null,
    val isCached: Boolean = false,
    val cachedAtEpochMillis: Long? = null,
    val errorMessage: String? = null,
)

suspend fun loadTimingAdviceWithCacheFallback(
    activity: TimingActivity,
    profile: AppProfile,
    remoteDataSource: AstroRemoteDataSource,
    cacheStore: TimingAdviceCacheStore,
): TimingAdviceLoadResult = remoteDataSource.fetchTimingAdvice(activity, profile).fold(
    onSuccess = { payload ->
        TimingAdviceLoadResult(
            payload = payload,
            isCached = false,
            cachedAtEpochMillis = cacheStore.write(profile.id, activity, payload),
        )
    },
    onFailure = { throwable ->
        val cached = cacheStore.read(profile.id, activity)
        if (cached != null) {
            TimingAdviceLoadResult(
                payload = cached.payload,
                isCached = true,
                cachedAtEpochMillis = cached.cachedAtEpochMillis,
            )
        } else {
            TimingAdviceLoadResult(
                errorMessage = throwable.message ?: "Timing advice could not be loaded.",
            )
        }
    },
)