package com.astromeric.android.core.data.repository

import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.ExactTransitAspectData
import java.time.Instant
import java.time.temporal.ChronoUnit
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

private data class AspectDefinition(
    val name: String,
    val angle: Double,
    val significance: String,
)

private data class OrbitCoefficients(
    val ascendingNodeBase: Double,
    val ascendingNodeRate: Double,
    val inclinationBase: Double,
    val inclinationRate: Double,
    val perihelionBase: Double,
    val perihelionRate: Double,
    val semiMajorAxisBase: Double,
    val semiMajorAxisRate: Double,
    val eccentricityBase: Double,
    val eccentricityRate: Double,
    val meanAnomalyBase: Double,
    val meanAnomalyRate: Double,
)

private data class TransitPlanetDefinition(
    val name: String,
    val orbit: OrbitCoefficients,
)

private data class CartesianPosition(
    val x: Double,
    val y: Double,
    val z: Double,
)

private data class ExactRefinement(
    val instant: Instant,
    val orb: Double,
)

class LocalExactTransitEstimator {
    fun estimateUpcomingExactTransits(
        chart: ChartData,
        startInstant: Instant = Instant.now(),
        daysAhead: Int = DEFAULT_DAYS_AHEAD,
    ): List<ExactTransitAspectData> {
        val natalDegrees = extractNatalDegrees(chart)
        if (natalDegrees.isEmpty()) {
            return emptyList()
        }

        val scanStart = startInstant.truncatedTo(ChronoUnit.MINUTES)
        val results = mutableListOf<ExactTransitAspectData>()

        repeat(daysAhead.coerceAtLeast(0)) { dayOffset ->
            val scanInstant = scanStart.plus(dayOffset.toLong(), ChronoUnit.DAYS)
            TransitPlanets.forEach { transitPlanet ->
                val transitDegree = geocentricLongitude(transitPlanet.orbit, scanInstant)
                natalDegrees.forEach { (natalName, natalDegree) ->
                    if (transitPlanet.name == natalName) {
                        return@forEach
                    }

                    AspectDefinitions.forEach { aspect ->
                        val orb = normalizedOrb(transitDegree, natalDegree, aspect.angle)
                        if (orb > SCAN_TRIGGER_ORB) {
                            return@forEach
                        }

                        val refinement = refineToExact(
                            orbit = transitPlanet.orbit,
                            natalDegree = natalDegree,
                            aspectAngle = aspect.angle,
                            startInstant = scanInstant,
                        ) ?: return@forEach

                        if (!refinement.instant.isAfter(scanStart)) {
                            return@forEach
                        }

                        val isDuplicate = results.any { existing ->
                            existing.transitPlanet == transitPlanet.name &&
                                existing.natalPoint == natalName &&
                                existing.aspect == aspect.name &&
                                abs(Instant.parse(existing.exactDate).epochSecond - refinement.instant.epochSecond) < ONE_DAY_SECONDS
                        }
                        if (isDuplicate) {
                            return@forEach
                        }

                        val nextDayOrb = normalizedOrb(
                            geocentricLongitude(transitPlanet.orbit, refinement.instant.plus(1, ChronoUnit.DAYS)),
                            natalDegree,
                            aspect.angle,
                        )

                        results += ExactTransitAspectData(
                            transitPlanet = transitPlanet.name,
                            natalPoint = natalName,
                            aspect = aspect.name,
                            exactDate = refinement.instant.toString(),
                            orb = refinement.orb.roundToPlaces(2),
                            isApplying = nextDayOrb > refinement.orb,
                            significance = aspect.significance,
                            interpretation = buildOfflineInterpretation(
                                transitPlanet = transitPlanet.name,
                                natalPoint = natalName,
                                aspect = aspect.name,
                            ),
                        )
                    }
                }
            }
        }

        return results.sortedBy { it.exactDate }.take(MAX_LOCAL_TRANSITS)
    }

    private fun extractNatalDegrees(chart: ChartData): Map<String, Double> {
        val natalDegrees = linkedMapOf<String, Double>()
        chart.planets.forEach { planet ->
            if (planet.name in NatalPointNames) {
                natalDegrees[planet.name] = planet.absoluteDegree ?: degreeFromSign(planet.sign, planet.degree)
            }
        }
        chart.points.firstOrNull { point ->
            point.name.equals("Ascendant", ignoreCase = true) || point.name.equals("ASC", ignoreCase = true)
        }?.let { ascendant ->
            natalDegrees["Ascendant"] = ascendant.absoluteDegree ?: degreeFromSign(ascendant.sign, ascendant.degree)
        }
        return natalDegrees
    }

    private fun refineToExact(
        orbit: OrbitCoefficients,
        natalDegree: Double,
        aspectAngle: Double,
        startInstant: Instant,
    ): ExactRefinement? {
        var bestInstant = startInstant
        var bestOrb = Double.MAX_VALUE

        repeat(HOUR_SCAN_RANGE) { hourOffset ->
            val candidate = startInstant.plus(hourOffset.toLong(), ChronoUnit.HOURS)
            val orb = normalizedOrb(geocentricLongitude(orbit, candidate), natalDegree, aspectAngle)
            if (orb < bestOrb) {
                bestOrb = orb
                bestInstant = candidate
            }
        }

        val minuteWindowStart = bestInstant.minus(MINUTE_SCAN_WINDOW_MINUTES, ChronoUnit.MINUTES)
        repeat(MINUTE_SCAN_RANGE) { minuteOffset ->
            val candidate = minuteWindowStart.plus(minuteOffset.toLong(), ChronoUnit.MINUTES)
            val orb = normalizedOrb(geocentricLongitude(orbit, candidate), natalDegree, aspectAngle)
            if (orb < bestOrb) {
                bestOrb = orb
                bestInstant = candidate
            }
        }

        return bestOrb.takeIf { it < ACCEPTED_EXACT_ORB }?.let { ExactRefinement(bestInstant, it) }
    }

    private fun geocentricLongitude(
        orbit: OrbitCoefficients,
        instant: Instant,
    ): Double {
        val days = daysSinceEpoch(instant)
        val earth = heliocentricPosition(EarthOrbit, days)
        val planet = heliocentricPosition(orbit, days)
        return atan2(planet.y - earth.y, planet.x - earth.x).toDegrees().normalizeDegrees()
    }

    private fun heliocentricPosition(
        orbit: OrbitCoefficients,
        days: Double,
    ): CartesianPosition {
        val ascendingNode = (orbit.ascendingNodeBase + orbit.ascendingNodeRate * days).toRadians()
        val inclination = (orbit.inclinationBase + orbit.inclinationRate * days).toRadians()
        val perihelion = (orbit.perihelionBase + orbit.perihelionRate * days).toRadians()
        val semiMajorAxis = orbit.semiMajorAxisBase + orbit.semiMajorAxisRate * days
        val eccentricity = orbit.eccentricityBase + orbit.eccentricityRate * days
        val meanAnomaly = (orbit.meanAnomalyBase + orbit.meanAnomalyRate * days).normalizeDegrees().toRadians()

        var eccentricAnomaly = meanAnomaly + eccentricity * sin(meanAnomaly) * (1.0 + eccentricity * cos(meanAnomaly))
        repeat(5) {
            eccentricAnomaly -= (eccentricAnomaly - eccentricity * sin(eccentricAnomaly) - meanAnomaly) /
                (1.0 - eccentricity * cos(eccentricAnomaly))
        }

        val xv = semiMajorAxis * (cos(eccentricAnomaly) - eccentricity)
        val yv = semiMajorAxis * (sqrt(1.0 - eccentricity * eccentricity) * sin(eccentricAnomaly))

        val trueAnomaly = atan2(yv, xv)
        val radius = sqrt(xv * xv + yv * yv)
        val longitude = trueAnomaly + perihelion

        return CartesianPosition(
            x = radius * (cos(ascendingNode) * cos(longitude) - sin(ascendingNode) * sin(longitude) * cos(inclination)),
            y = radius * (sin(ascendingNode) * cos(longitude) + cos(ascendingNode) * sin(longitude) * cos(inclination)),
            z = radius * (sin(longitude) * sin(inclination)),
        )
    }

    private fun buildOfflineInterpretation(
        transitPlanet: String,
        natalPoint: String,
        aspect: String,
    ): String = "Estimated locally from your cached natal chart while offline. $transitPlanet $aspect your $natalPoint. Reconnect to refresh with backend-grade precision."

    private fun degreeFromSign(sign: String, degree: Double): Double {
        val signIndex = ZodiacSigns.indexOfFirst { it.equals(sign, ignoreCase = true) }
        return if (signIndex >= 0) {
            signIndex * 30 + degree
        } else {
            degree
        }
    }

    private fun normalizedOrb(
        degreeA: Double,
        degreeB: Double,
        aspectAngle: Double,
    ): Double {
        var difference = abs(degreeA - degreeB)
        if (difference > 180.0) {
            difference = 360.0 - difference
        }
        return abs(difference - aspectAngle)
    }

    private fun daysSinceEpoch(instant: Instant): Double =
        (instant.toEpochMilli() - EphemerisEpoch.toEpochMilli()) / MILLIS_PER_DAY.toDouble()

    private fun Double.toRadians(): Double = this * PI / 180.0

    private fun Double.toDegrees(): Double = this * 180.0 / PI

    private fun Double.normalizeDegrees(): Double {
        val normalized = this % 360.0
        return if (normalized < 0.0) normalized + 360.0 else normalized
    }

    private fun Double.roundToPlaces(places: Int): Double {
        val factor = 10.0.pow(places)
        return kotlin.math.round(this * factor) / factor
    }

    private fun Double.pow(exponent: Int): Double =
        Math.pow(this, exponent.toDouble())

    private companion object {
        private val NatalPointNames = setOf("Sun", "Moon", "Mercury", "Venus", "Mars")
        private val ZodiacSigns = listOf(
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        )
        private val AspectDefinitions = listOf(
            AspectDefinition("conjunction", 0.0, "major"),
            AspectDefinition("opposition", 180.0, "major"),
            AspectDefinition("trine", 120.0, "major"),
            AspectDefinition("square", 90.0, "major"),
            AspectDefinition("sextile", 60.0, "minor"),
        )
        private val TransitPlanets = listOf(
            TransitPlanetDefinition(
                name = "Mars",
                orbit = OrbitCoefficients(49.5574, 2.11081e-5, 1.8497, -1.78e-8, 286.5016, 2.92961e-5, 1.523688, 0.0, 0.093405, 2.516e-9, 18.6021, 0.5240207766),
            ),
            TransitPlanetDefinition(
                name = "Jupiter",
                orbit = OrbitCoefficients(100.4542, 2.76854e-5, 1.3030, -1.557e-7, 273.8777, 1.64505e-5, 5.20256, 0.0, 0.048498, 4.469e-9, 19.8950, 0.0830853001),
            ),
            TransitPlanetDefinition(
                name = "Saturn",
                orbit = OrbitCoefficients(113.6634, 2.38980e-5, 2.4886, -1.081e-7, 339.3939, 2.97661e-5, 9.55475, 0.0, 0.055546, -9.499e-9, 316.9670, 0.0334442282),
            ),
            TransitPlanetDefinition(
                name = "Uranus",
                orbit = OrbitCoefficients(74.0005, 1.3978e-5, 0.7733, 1.9e-8, 96.6612, 3.0565e-5, 19.18171, -1.55e-8, 0.047318, 7.45e-9, 142.5905, 0.011725806),
            ),
            TransitPlanetDefinition(
                name = "Neptune",
                orbit = OrbitCoefficients(131.7806, 3.0173e-5, 1.7700, -2.55e-7, 272.8461, -6.027e-6, 30.05826, 3.313e-8, 0.008606, 2.15e-9, 260.2471, 0.005995147),
            ),
            TransitPlanetDefinition(
                name = "Pluto",
                orbit = OrbitCoefficients(110.30347, 2.49947e-4, 17.14175, 4.84e-7, 113.76329, 3.28025e-5, 39.48168677, 0.0, 0.24880766, 0.0, 14.53, 0.003975709),
            ),
        )
        private val EarthOrbit = OrbitCoefficients(0.0, 0.0, 0.0, 0.0, 282.9404, 4.70935e-5, 1.0, 0.0, 0.016709, -1.151e-9, 356.0470, 0.9856002585)
        private val EphemerisEpoch: Instant = Instant.parse("2000-01-01T00:00:00Z")
        private const val DEFAULT_DAYS_AHEAD = 7
        private const val SCAN_TRIGGER_ORB = 1.5
        private const val ACCEPTED_EXACT_ORB = 1.0
        private const val HOUR_SCAN_RANGE = 24
        private const val MINUTE_SCAN_RANGE = 60
        private const val MINUTE_SCAN_WINDOW_MINUTES = 30L
        private const val MAX_LOCAL_TRANSITS = 20
        private const val ONE_DAY_SECONDS = 24 * 60 * 60L
        private const val MILLIS_PER_DAY = 24L * 60L * 60L * 1000L
    }
}