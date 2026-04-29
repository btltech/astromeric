package com.astromeric.android.core.data.repository

import com.astromeric.android.core.data.local.DailyTransitReportCacheStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AstroDataSource
import com.astromeric.android.core.model.DailyTransitReportData

data class DailyTransitReportLoadResult(
    val report: DailyTransitReportData? = null,
    val source: AstroDataSource? = null,
    val isCached: Boolean = false,
    val cachedAtEpochMillis: Long? = null,
    val errorMessage: String? = null,
)

suspend fun loadDailyTransitReportWithCacheFallback(
    profile: AppProfile,
    remoteDataSource: AstroRemoteDataSource,
    cacheStore: DailyTransitReportCacheStore,
): DailyTransitReportLoadResult = remoteDataSource.fetchDailyTransits(profile).fold(
    onSuccess = { report ->
        DailyTransitReportLoadResult(
            report = report,
            source = AstroDataSource.BACKEND,
            isCached = false,
            cachedAtEpochMillis = cacheStore.write(profile.id, report, AstroDataSource.BACKEND),
        )
    },
    onFailure = { throwable ->
        val cached = cacheStore.read(profile.id)
        if (cached != null) {
            DailyTransitReportLoadResult(
                report = cached.report,
                source = cached.source,
                isCached = true,
                cachedAtEpochMillis = cached.cachedAtEpochMillis,
            )
        } else {
            DailyTransitReportLoadResult(
                errorMessage = throwable.message ?: "Daily transit report could not be loaded.",
            )
        }
    },
)