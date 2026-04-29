package com.astromeric.android.core.data.repository

import com.astromeric.android.core.data.local.NatalChartCacheStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.ephemeris.LocalSwissEphemerisEngine
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.ChartData

data class NatalChartLoadResult(
    val chart: ChartData? = null,
    val source: AstroDataSource? = null,
    val isCached: Boolean = false,
    val cachedAtEpochMillis: Long? = null,
    val errorMessage: String? = null,
)

suspend fun loadNatalChartWithCacheFallback(
    profile: AppProfile,
    remoteDataSource: AstroRemoteDataSource,
    chartCacheStore: NatalChartCacheStore,
    localEphemerisEngine: LocalSwissEphemerisEngine? = null,
): NatalChartLoadResult = remoteDataSource.fetchNatalChart(profile).fold(
    onSuccess = { chart ->
        NatalChartLoadResult(
            chart = chart,
            source = AstroDataSource.BACKEND,
            isCached = false,
            cachedAtEpochMillis = chartCacheStore.write(profile.id, chart, AstroDataSource.BACKEND),
        )
    },
    onFailure = { throwable ->
        val localChart = localEphemerisEngine?.calculateNatalChart(profile)?.getOrNull()
        if (localChart != null) {
            NatalChartLoadResult(
                chart = localChart,
                source = AstroDataSource.LOCAL_SWISS,
                isCached = false,
                cachedAtEpochMillis = chartCacheStore.write(profile.id, localChart, AstroDataSource.LOCAL_SWISS),
            )
        } else {
            val cached = chartCacheStore.read(profile.id)
            if (cached != null) {
                NatalChartLoadResult(
                    chart = cached.chart,
                    source = cached.source,
                    isCached = true,
                    cachedAtEpochMillis = cached.cachedAtEpochMillis,
                )
            } else {
                NatalChartLoadResult(
                    errorMessage = throwable.message ?: "Natal chart could not be loaded.",
                )
            }
        }
    },
)