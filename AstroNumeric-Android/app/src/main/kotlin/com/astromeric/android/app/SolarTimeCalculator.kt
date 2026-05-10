package com.astromeric.android.app

import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.ZoneId
import kotlin.math.acos
import kotlin.math.asin
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.tan

/**
 * Lightweight solar time calculator (no external dependency).
 * Uses the NOAA simplified algorithm — accurate to ±1 minute for latitudes up to ±60°.
 */
object SolarTimeCalculator {

    data class SolarTimes(
        val sunriseEpochMillis: Long,
        val sunsetEpochMillis: Long,
    ) {
        val daylightMillis: Long get() = sunsetEpochMillis - sunriseEpochMillis
        val nightMillis: Long get() = 86_400_000L - daylightMillis
    }

    /**
     * Returns today's sunrise and sunset as epoch millis in the device's default timezone.
     * Falls back to 6 am / 6 pm if the calculation fails (e.g. polar day/night).
     *
     * @param latitude  Decimal degrees, positive = North.
     * @param longitude Decimal degrees, positive = East.
     * @param date      The date for which to calculate solar times (defaults to today).
     * @param zone      Timezone (defaults to system default).
     */
    fun calculate(
        latitude: Double,
        longitude: Double,
        date: LocalDate = LocalDate.now(),
        zone: ZoneId = ZoneId.systemDefault(),
    ): SolarTimes {
        val julianDay = toJulianDay(date)
        val sunrise = computeSunTime(julianDay, latitude, longitude, zone, date, rising = true)
        val sunset = computeSunTime(julianDay, latitude, longitude, zone, date, rising = false)

        val fallbackSunrise = date.atTime(6, 0).atZone(zone).toInstant().toEpochMilli()
        val fallbackSunset = date.atTime(18, 0).atZone(zone).toInstant().toEpochMilli()

        return SolarTimes(
            sunriseEpochMillis = sunrise ?: fallbackSunrise,
            sunsetEpochMillis = sunset ?: fallbackSunset,
        )
    }

    // ── Internal helpers ─────────────────────────────────────────────────────

    private fun toJulianDay(date: LocalDate): Double {
        val y = date.year
        val m = date.monthValue
        val d = date.dayOfMonth
        return 367.0 * y -
            Math.floor(7.0 * (y + Math.floor((m + 9.0) / 12.0)) / 4.0) +
            Math.floor(275.0 * m / 9.0) + d + 1721013.5
    }

    private fun computeSunTime(
        julianDay: Double,
        latitude: Double,
        longitude: Double,
        zone: ZoneId,
        date: LocalDate,
        rising: Boolean,
    ): Long? {
        val D = julianDay - 2451545.0          // days since J2000.0
        val g = toRad((357.5291 + 0.98560028 * D) % 360)
        val q = (280.4664 + 0.98564736 * D) % 360
        val L = toRad(q + 1.9148 * sin(g) + 0.0200 * sin(2 * g))

        val sinDec = sin(toRad(23.4393)) * sin(L)
        val dec = asin(sinDec)

        val latRad = toRad(latitude)
        val cosHA = (cos(toRad(90.833)) - sin(latRad) * sin(dec)) / (cos(latRad) * cos(dec))
        if (cosHA < -1.0 || cosHA > 1.0) return null  // polar day / night

        val HA = Math.toDegrees(acos(cosHA))
        val jNoon = 2451545.0 + D + 0.0009 - longitude / 360.0 + 0.0053 * sin(g) - 0.0069 * sin(2 * L)
        val jEvent = jNoon + (if (rising) -HA / 360.0 else HA / 360.0)

        // Convert Julian Day to epoch millis
        val epochMillis = ((jEvent - 2440587.5) * 86_400_000).toLong()
        return epochMillis
    }

    private fun toRad(deg: Double) = Math.toRadians(deg)
}
