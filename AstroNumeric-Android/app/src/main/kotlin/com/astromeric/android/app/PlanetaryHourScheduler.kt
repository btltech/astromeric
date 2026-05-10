package com.astromeric.android.app

import java.time.LocalDate

/**
 * Computes the 24-entry Chaldean planetary hour schedule for a given location and day.
 * Matches the iOS [WidgetDataProvider.updatePlanetaryHours] algorithm.
 */
object PlanetaryHourScheduler {

    private val CHALDEAN = listOf("Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon")
    // Sunday=1, Monday=2, …, Saturday=7 (matching java.util.Calendar weekday constants)
    private val DAY_RULERS = listOf("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

    private val PLANET_SYMBOLS = mapOf(
        "Sun"     to "☀",
        "Moon"    to "☽",
        "Mars"    to "♂",
        "Mercury" to "☿",
        "Jupiter" to "♃",
        "Venus"   to "♀",
        "Saturn"  to "♄",
    )

    /**
     * Returns 24 [PlanetaryHourEntry] items (12 day hours + 12 night hours) for today.
     * Returns an empty list if location data is unavailable or the calculation fails.
     *
     * @param latitude  Decimal degrees (positive = North).
     * @param longitude Decimal degrees (positive = East).
     * @param date      Defaults to today.
     */
    fun buildSchedule(
        latitude: Double,
        longitude: Double,
        date: LocalDate = LocalDate.now(),
    ): List<PlanetaryHourEntry> = runCatching {
        val solar = SolarTimeCalculator.calculate(latitude, longitude, date)

        // Weekday: Sunday=1 … Saturday=7 using java.util.Calendar convention
        val weekday = java.util.Calendar.getInstance().let { cal ->
            cal.time = java.util.Date(solar.sunriseEpochMillis)
            cal.get(java.util.Calendar.DAY_OF_WEEK)
        }

        val dayRuler = DAY_RULERS[weekday - 1]
        val startIdx = CHALDEAN.indexOf(dayRuler).takeIf { it >= 0 } ?: return emptyList()

        val dayDurationMs = solar.daylightMillis.toDouble()
        val nightDurationMs = solar.nightMillis.toDouble()
        val dayHourMs = dayDurationMs / 12.0
        val nightHourMs = nightDurationMs / 12.0

        val schedule = mutableListOf<PlanetaryHourEntry>()

        // 12 day hours: sunrise → sunset
        for (i in 0 until 12) {
            val start = solar.sunriseEpochMillis + (i * dayHourMs).toLong()
            val end = solar.sunriseEpochMillis + ((i + 1) * dayHourMs).toLong()
            val ruler = CHALDEAN[(startIdx + i) % 7]
            schedule += PlanetaryHourEntry(
                rulerName = ruler,
                rulerSymbol = PLANET_SYMBOLS[ruler] ?: ruler.take(1),
                startEpochMillis = start,
                endEpochMillis = end,
            )
        }

        // 12 night hours: sunset → next sunrise (approx)
        for (i in 0 until 12) {
            val start = solar.sunsetEpochMillis + (i * nightHourMs).toLong()
            val end = solar.sunsetEpochMillis + ((i + 1) * nightHourMs).toLong()
            val ruler = CHALDEAN[(startIdx + 12 + i) % 7]
            schedule += PlanetaryHourEntry(
                rulerName = ruler,
                rulerSymbol = PLANET_SYMBOLS[ruler] ?: ruler.take(1),
                startEpochMillis = start,
                endEpochMillis = end,
            )
        }

        schedule
    }.getOrDefault(emptyList())
}
