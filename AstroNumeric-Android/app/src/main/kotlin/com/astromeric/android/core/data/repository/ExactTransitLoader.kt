package com.astromeric.android.core.data.repository

import com.astromeric.android.core.data.local.ExactTransitCacheStore
import com.astromeric.android.core.data.local.NatalChartCacheStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.ephemeris.LocalSwissEphemerisEngine
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.ExactTransitAspectData

data class ExactTransitLoadResult(
    val transits: List<ExactTransitAspectData>? = null,
    val source: AstroDataSource? = null,
    val isCached: Boolean = false,
    val cachedAtEpochMillis: Long? = null,
    val errorMessage: String? = null,
)

suspend fun loadUpcomingExactTransitsWithCacheFallback(
    profile: AppProfile,
    remoteDataSource: AstroRemoteDataSource,
    cacheStore: ExactTransitCacheStore,
    natalChartCacheStore: NatalChartCacheStore,
    localEphemerisEngine: LocalSwissEphemerisEngine? = null,
    localEstimator: LocalExactTransitEstimator = LocalExactTransitEstimator(),
): ExactTransitLoadResult = remoteDataSource.fetchUpcomingExactTransits(profile).fold(
    onSuccess = { transits ->
        ExactTransitLoadResult(
            transits = transits,
            source = AstroDataSource.BACKEND,
            isCached = false,
            cachedAtEpochMillis = cacheStore.write(profile.id, transits, AstroDataSource.BACKEND),
        )
    },
    onFailure = { throwable ->
        val localSwissTransits = localEphemerisEngine?.findUpcomingExactTransits(profile)?.getOrNull()
        if (localSwissTransits != null) {
            ExactTransitLoadResult(
                transits = localSwissTransits,
                source = AstroDataSource.LOCAL_SWISS,
                isCached = false,
                cachedAtEpochMillis = cacheStore.write(profile.id, localSwissTransits, AstroDataSource.LOCAL_SWISS),
            )
        } else {
            val cached = cacheStore.read(profile.id)
            if (cached != null) {
                ExactTransitLoadResult(
                    transits = cached.transits,
                    source = cached.source,
                    isCached = true,
                    cachedAtEpochMillis = cached.cachedAtEpochMillis,
                )
            } else {
                val natalChart = natalChartCacheStore.read(profile.id)?.chart
                val localEstimate = natalChart?.let(localEstimator::estimateUpcomingExactTransits).orEmpty()
                if (localEstimate.isNotEmpty()) {
                    ExactTransitLoadResult(
                        transits = localEstimate,
                        source = AstroDataSource.LOCAL_ESTIMATE,
                        isCached = false,
                        errorMessage = throwable.message,
                    )
                } else {
                    ExactTransitLoadResult(
                        errorMessage = throwable.message ?: "Upcoming exact transits could not be loaded.",
                    )
                }
            }
        }
    },
)