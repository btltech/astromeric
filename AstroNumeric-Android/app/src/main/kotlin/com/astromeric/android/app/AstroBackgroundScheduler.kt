package com.astromeric.android.app

import android.content.Context
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

object AstroBackgroundScheduler {
    private const val REFRESH_WORK_NAME = "astro_refresh_periodic"
    private const val REFRESH_NOW_WORK_NAME = "astro_refresh_now"

    fun schedulePeriodicRefresh(context: Context) {
        val request = PeriodicWorkRequestBuilder<AstroRefreshWorker>(6, TimeUnit.HOURS)
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build(),
            )
            .build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            REFRESH_WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            request,
        )
    }

    fun scheduleImmediateRefresh(context: Context) {
        val request = OneTimeWorkRequestBuilder<AstroRefreshWorker>()
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build(),
            )
            .build()

        WorkManager.getInstance(context).enqueueUniqueWork(
            REFRESH_NOW_WORK_NAME,
            ExistingWorkPolicy.REPLACE,
            request,
        )
    }
}