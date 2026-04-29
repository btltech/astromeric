package com.astromeric.android.core.ephemeris

import android.content.Context
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.ExactTransitAspectData
import com.astromeric.android.core.model.TimeConfidence
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.io.File
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneId
import java.time.ZoneOffset
import java.time.format.DateTimeParseException

class LocalSwissEphemerisEngine private constructor(
    private val appContext: Context,
) {
    private val gson = Gson()
    private val assetMutex = Mutex()
    private val bridgeMutex = Mutex()
    private val exactTransitListType = object : TypeToken<List<ExactTransitAspectData>>() {}.type

    suspend fun calculateNatalChart(profile: AppProfile): Result<ChartData> = try {
        val chart = withContext(Dispatchers.Default) {
            require(profile.canRequestNatalChart) { "Natal chart calculation requires coordinates and timezone." }

            val ephemerisPath = ensureEphemerisAssets()
            val utc = birthUtcSnapshot(profile)
            val json = bridgeMutex.withLock {
                SwissEphemerisBridge.calculateNatalChart(
                    ephemerisPath = ephemerisPath,
                    name = profile.name,
                    dateOfBirth = profile.dateOfBirth,
                    timeOfBirth = normalizedBirthTime(profile.timeOfBirth),
                    birthTimeAssumed = profile.timeConfidence != TimeConfidence.EXACT,
                    dataQuality = profile.dataQuality.label,
                    timezone = requireNotNull(profile.timezone),
                    houseSystem = profile.houseSystem,
                    latitude = requireNotNull(profile.latitude),
                    longitude = requireNotNull(profile.longitude),
                    utcYear = utc.year,
                    utcMonth = utc.month,
                    utcDay = utc.day,
                    utcHour = utc.hour,
                )
            }
            gson.fromJson(json, ChartData::class.java)
        }
        Result.success(chart)
    } catch (cancellation: CancellationException) {
        throw cancellation
    } catch (throwable: Throwable) {
        Result.failure(throwable)
    }

    suspend fun findUpcomingExactTransits(
        profile: AppProfile,
        daysAhead: Int = 7,
    ): Result<List<ExactTransitAspectData>> = try {
        val transits = withContext(Dispatchers.Default) {
            val chart = calculateNatalChart(profile).getOrElse { throw it }
            val natalDegrees = extractNatalDegrees(chart)
            require(natalDegrees.isNotEmpty()) { "Exact transit calculation requires natal planet degrees." }

            val ephemerisPath = ensureEphemerisAssets()
            val json = bridgeMutex.withLock {
                SwissEphemerisBridge.findUpcomingExactTransits(
                    ephemerisPath = ephemerisPath,
                    natalNames = natalDegrees.keys.toTypedArray(),
                    natalDegrees = natalDegrees.values.toDoubleArray(),
                    daysAhead = daysAhead,
                    startEpochMillis = System.currentTimeMillis(),
                )
            }
            gson.fromJson<List<ExactTransitAspectData>>(json, exactTransitListType)
        }
        Result.success(transits)
    } catch (cancellation: CancellationException) {
        throw cancellation
    } catch (throwable: Throwable) {
        Result.failure(throwable)
    }

    private suspend fun ensureEphemerisAssets(): String = withContext(Dispatchers.IO) {
        assetMutex.withLock {
            val targetDirectory = File(appContext.filesDir, "ephemeris")
            if (!targetDirectory.exists()) {
                targetDirectory.mkdirs()
            }

            RequiredEphemerisFiles.forEach { fileName ->
                val targetFile = File(targetDirectory, fileName)
                if (!targetFile.exists() || targetFile.length() == 0L) {
                    appContext.assets.open("ephemeris/$fileName").use { input ->
                        targetFile.outputStream().use { output ->
                            input.copyTo(output)
                        }
                    }
                }
            }

            targetDirectory.absolutePath
        }
    }

    private fun birthUtcSnapshot(profile: AppProfile): BirthUtcSnapshot {
        val zoneId = ZoneId.of(requireNotNull(profile.timezone))
        val localDate = LocalDate.parse(profile.dateOfBirth)
        val localTime = parseBirthTime(profile.timeOfBirth)
        val utcDateTime = LocalDateTime.of(localDate, localTime)
            .atZone(zoneId)
            .withZoneSameInstant(ZoneOffset.UTC)

        val utcTime = utcDateTime.toLocalTime()
        val utcHour = utcTime.hour + utcTime.minute / 60.0 + utcTime.second / 3600.0
        return BirthUtcSnapshot(
            year = utcDateTime.year,
            month = utcDateTime.monthValue,
            day = utcDateTime.dayOfMonth,
            hour = utcHour,
        )
    }

    private fun extractNatalDegrees(chart: ChartData): LinkedHashMap<String, Double> {
        val natalDegrees = linkedMapOf<String, Double>()
        listOf("Sun", "Moon", "Mercury", "Venus", "Mars").forEach { planetName ->
            chart.planets.firstOrNull { it.name.equals(planetName, ignoreCase = true) }?.absoluteDegree?.let { degree ->
                natalDegrees[planetName] = degree
            }
        }
        chart.points.firstOrNull { it.name.equals("Ascendant", ignoreCase = true) || it.name.equals("ASC", ignoreCase = true) }
            ?.absoluteDegree
            ?.let { degree ->
                natalDegrees["Ascendant"] = degree
            }
        return natalDegrees
    }

    private fun parseBirthTime(raw: String?): LocalTime {
        val candidate = raw?.trim().orEmpty()
        if (candidate.isBlank()) {
            return DefaultBirthTime
        }
        return runCatching { LocalTime.parse(candidate) }
            .recoverCatching {
                val parts = candidate.split(':')
                val hour = parts.getOrNull(0)?.toIntOrNull() ?: return@recoverCatching DefaultBirthTime
                val minute = parts.getOrNull(1)?.toIntOrNull() ?: 0
                val second = parts.getOrNull(2)?.toIntOrNull() ?: 0
                LocalTime.of(hour, minute, second)
            }
            .getOrElse { DefaultBirthTime }
    }

    private fun normalizedBirthTime(raw: String?): String = parseBirthTime(raw).toString()

    companion object {
        @Volatile
        private var instance: LocalSwissEphemerisEngine? = null

        fun getInstance(context: Context): LocalSwissEphemerisEngine =
            instance ?: synchronized(this) {
                instance ?: LocalSwissEphemerisEngine(context.applicationContext).also { instance = it }
            }

        private val RequiredEphemerisFiles = listOf(
            "seas_18.se1",
            "semo_18.se1",
            "sepl_18.se1",
            "seleapsec.txt",
        )
        private val DefaultBirthTime: LocalTime = LocalTime.NOON
    }
}

private data class BirthUtcSnapshot(
    val year: Int,
    val month: Int,
    val day: Int,
    val hour: Double,
)