package com.astromeric.android.feature.guide

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.RestingHeartRateRecord
import androidx.health.connect.client.records.SleepSessionRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.TotalCaloriesBurnedRecord
import androidx.health.connect.client.request.AggregateRequest
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.Instant
import java.time.ZoneId
import java.time.ZonedDateTime

enum class GuideHealthAvailability {
    AVAILABLE,
    UPDATE_REQUIRED,
    UNAVAILABLE,
}

data class GuideBiometricSnapshot(
    val heartRate: Double? = null,
    val restingHeartRate: Double? = null,
    val steps: Long? = null,
    val totalCalories: Double? = null,
    val sleepHours: Double? = null,
    val timestamp: Instant? = null,
) {
    val hasData: Boolean
        get() = heartRate != null || restingHeartRate != null || steps != null || totalCalories != null || sleepHours != null

    val promptDescription: String
        get() {
            val lines = buildList {
                heartRate?.let { add("  - Heart Rate: ${it.toInt()} bpm") }
                restingHeartRate?.let { add("  - Resting HR: ${it.toInt()} bpm") }
                steps?.let { add("  - Steps: $it") }
                totalCalories?.let { add("  - Total Calories Burned: ${it.toInt()} kcal") }
                sleepHours?.let { add("  - Sleep: ${String.format("%.1f", it)} hrs") }
            }
            return if (lines.isEmpty()) {
                "  - No biometric data available"
            } else {
                lines.joinToString(separator = "\n")
            }
        }
}

class GuideHealthConnectBridge(
    private val context: Context,
) {
    private val client: HealthConnectClient by lazy {
        HealthConnectClient.getOrCreate(context)
    }

    val requiredPermissions: Set<String> = setOf(
        HealthPermission.getReadPermission(HeartRateRecord::class),
        HealthPermission.getReadPermission(RestingHeartRateRecord::class),
        HealthPermission.getReadPermission(StepsRecord::class),
        HealthPermission.getReadPermission(TotalCaloriesBurnedRecord::class),
        HealthPermission.getReadPermission(SleepSessionRecord::class),
    )

    fun availability(): GuideHealthAvailability = when (
        HealthConnectClient.getSdkStatus(context, providerPackageName)
    ) {
        HealthConnectClient.SDK_AVAILABLE -> GuideHealthAvailability.AVAILABLE
        HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> GuideHealthAvailability.UPDATE_REQUIRED
        else -> GuideHealthAvailability.UNAVAILABLE
    }

    suspend fun hasAllPermissions(): Boolean = withContext(Dispatchers.IO) {
        if (availability() != GuideHealthAvailability.AVAILABLE) {
            return@withContext false
        }
        client.permissionController.getGrantedPermissions().containsAll(requiredPermissions)
    }

    suspend fun readTodaySnapshot(): GuideBiometricSnapshot = withContext(Dispatchers.IO) {
        if (!hasAllPermissions()) {
            return@withContext GuideBiometricSnapshot()
        }

        val zone = ZoneId.systemDefault()
        val now = Instant.now()
        val startOfDay = ZonedDateTime.now(zone).toLocalDate().atStartOfDay(zone).toInstant()
        val yesterday = startOfDay.minusSeconds(24L * 60L * 60L)

        val aggregates = client.aggregate(
            AggregateRequest(
                metrics = setOf(
                    StepsRecord.COUNT_TOTAL,
                    TotalCaloriesBurnedRecord.ENERGY_TOTAL,
                ),
                timeRangeFilter = TimeRangeFilter.between(startOfDay, now),
            ),
        )

        val heartRateRecords = client.readRecords(
            ReadRecordsRequest(
                recordType = HeartRateRecord::class,
                timeRangeFilter = TimeRangeFilter.between(startOfDay, now),
            ),
        ).records
        val restingHeartRateRecords = client.readRecords(
            ReadRecordsRequest(
                recordType = RestingHeartRateRecord::class,
                timeRangeFilter = TimeRangeFilter.between(startOfDay, now),
            ),
        ).records
        val sleepRecords = client.readRecords(
            ReadRecordsRequest(
                recordType = SleepSessionRecord::class,
                timeRangeFilter = TimeRangeFilter.between(yesterday, now),
            ),
        ).records

        val latestHeartRate = heartRateRecords
            .flatMap { record -> record.samples }
            .maxByOrNull { sample -> sample.time }
            ?.beatsPerMinute
        val latestRestingHeartRate = restingHeartRateRecords
            .maxByOrNull { record -> record.time }
            ?.beatsPerMinute
        val totalSleepHours = sleepRecords
            .sumOf { record -> java.time.Duration.between(record.startTime, record.endTime).toMinutes() }
            .takeIf { it > 0 }
            ?.toDouble()
            ?.div(60.0)

        GuideBiometricSnapshot(
            heartRate = latestHeartRate?.toDouble(),
            restingHeartRate = latestRestingHeartRate?.toDouble(),
            steps = aggregates[StepsRecord.COUNT_TOTAL],
            totalCalories = aggregates[TotalCaloriesBurnedRecord.ENERGY_TOTAL]?.inKilocalories,
            sleepHours = totalSleepHours,
            timestamp = now,
        )
    }

    companion object {
        const val providerPackageName = "com.google.android.apps.healthdata"
    }
}