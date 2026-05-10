package com.astromeric.android.feature.guide

import com.astromeric.android.core.model.ExactTransitAspectData
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import kotlin.math.abs

/**
 * BioCosmicCorrelator — mirrors iOS BioCosmicCorrelator.swift.
 *
 * Combines today's biometric snapshot with the user's cached exact transits to
 * generate a grounded narrative context block for the Cosmic Guide system prompt.
 *
 * iOS uses multi-day HealthKit time-series and Pearson correlation.
 * Android uses today's Health Connect snapshot + nearby transit window analysis
 * (Health Connect does not expose historical batches the same way HealthKit does).
 */
object BioCosmicCorrelator {

    private val DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd")

    /**
     * Build a context block that describes how today's biometric state relates
     * to upcoming and recently-past major transits.
     *
     * @param snapshot   Today's biometric data from [GuideHealthConnectBridge].
     * @param transits   Exact transit aspects from [ExactTransitCacheStore].
     * @param query      The user's current question (used to highlight relevant aspects).
     * @return A formatted context string, or null if there is no useful signal.
     */
    fun contextBlock(
        snapshot: GuideBiometricSnapshot?,
        transits: List<ExactTransitAspectData>,
        query: String? = null,
    ): String? {
        if (snapshot?.hasData != true && transits.isEmpty()) return null

        val today = LocalDate.now()
        val sections = mutableListOf<String>()

        // ── Biometric section ────────────────────────────────────────────────
        snapshot?.takeIf { it.hasData }?.let { bio ->
            val stressSignals = detectStressSignals(bio)
            val energySignals = detectEnergySignals(bio)
            val sleepSignals = detectSleepSignals(bio)

            val bioLines = buildList {
                if (stressSignals.isNotEmpty()) add("Stress indicators: ${stressSignals.joinToString()}")
                if (energySignals.isNotEmpty()) add("Energy signals: ${energySignals.joinToString()}")
                if (sleepSignals.isNotEmpty()) add("Sleep pattern: ${sleepSignals.joinToString()}")
            }

            if (bioLines.isNotEmpty()) {
                sections += "TODAY'S BIOMETRIC STATE:\n" + bioLines.joinToString(separator = "\n") { "  - $it" }
            }
        }

        // ── Transit window analysis ──────────────────────────────────────────
        if (transits.isNotEmpty()) {
            val (active, upcoming) = partitionTransits(transits, today)

            val transitLines = buildList {
                active.take(3).forEach { t ->
                    add("[ACTIVE] ${t.transitPlanet} ${t.aspect} ${t.natalPoint} — ${t.significance}" +
                        t.interpretation?.let { " ($it)" }.orEmpty())
                }
                upcoming.take(3).forEach { t ->
                    val daysAway = daysUntil(t.exactDate, today)
                    val label = if (daysAway == 0L) "today" else "in $daysAway day${if (daysAway == 1L) "" else "s"}"
                    add("[UPCOMING $label] ${t.transitPlanet} ${t.aspect} ${t.natalPoint} — ${t.significance}")
                }
            }

            if (transitLines.isNotEmpty()) {
                sections += "ACTIVE / APPROACHING TRANSITS:\n" + transitLines.joinToString(separator = "\n") { "  - $it" }
            }
        }

        // ── Qualitative correlation ──────────────────────────────────────────
        snapshot?.takeIf { it.hasData }?.let { bio ->
            val correlation = buildCorrelationNarrative(bio, transits, today, query)
            if (correlation.isNotBlank()) {
                sections += "BIOMETRIC–TRANSIT PATTERN:\n  $correlation"
            }
        }

        return if (sections.isEmpty()) null
        else sections.joinToString(separator = "\n\n")
    }

    // ── Private helpers ──────────────────────────────────────────────────────

    private fun detectStressSignals(bio: GuideBiometricSnapshot): List<String> = buildList {
        bio.heartRate?.let { hr ->
            when {
                hr > 90 -> add("elevated resting HR (${hr.toInt()} bpm)")
                hr < 55 -> add("low HR (${hr.toInt()} bpm) — deep rest or high fitness")
            }
        }
        bio.restingHeartRate?.let { rhr ->
            if (rhr > 80) add("high resting HR (${rhr.toInt()} bpm)")
        }
    }

    private fun detectEnergySignals(bio: GuideBiometricSnapshot): List<String> = buildList {
        bio.steps?.let { s ->
            when {
                s < 2000 -> add("low movement (${s} steps)")
                s > 12000 -> add("high activity day (${s} steps)")
            }
        }
        bio.totalCalories?.let { cal ->
            if (cal > 2800) add("high energy expenditure (${cal.toInt()} kcal)")
        }
    }

    private fun detectSleepSignals(bio: GuideBiometricSnapshot): List<String> = buildList {
        bio.sleepHours?.let { h ->
            when {
                h < 5.5 -> add("short sleep (${String.format("%.1f", h)} hrs)")
                h > 9.5 -> add("extended sleep (${String.format("%.1f", h)} hrs)")
                else -> add("${String.format("%.1f", h)} hrs")
            }
        }
    }

    private fun partitionTransits(
        transits: List<ExactTransitAspectData>,
        today: LocalDate,
    ): Pair<List<ExactTransitAspectData>, List<ExactTransitAspectData>> {
        val active = mutableListOf<ExactTransitAspectData>()
        val upcoming = mutableListOf<ExactTransitAspectData>()
        transits.forEach { t ->
            val days = daysUntil(t.exactDate, today)
            when {
                days in -2..2 -> active += t   // within ±2 days = active orb
                days in 3..14 -> upcoming += t
            }
        }
        // Prioritise major aspects
        active.sortByDescending { if (it.significance == "major") 1 else 0 }
        upcoming.sortBy { daysUntil(it.exactDate, today) }
        return active to upcoming
    }

    private fun buildCorrelationNarrative(
        bio: GuideBiometricSnapshot,
        transits: List<ExactTransitAspectData>,
        today: LocalDate,
        query: String?,
    ): String {
        val activeTransits = transits.filter { abs(daysUntil(it.exactDate, today)) <= 2 }
        if (activeTransits.isEmpty()) return ""

        val stressSignals = detectStressSignals(bio)
        val sleepSignals = detectSleepSignals(bio)

        // Look for Mars/Saturn/Pluto aspects when stress is elevated
        val tensionPlanets = setOf("Mars", "Saturn", "Pluto", "Uranus")
        val tensionAspects = setOf("square", "opposition", "conjunction")
        val activeTension = activeTransits.any {
            it.transitPlanet in tensionPlanets && it.aspect.lowercase() in tensionAspects
        }

        return buildString {
            if (stressSignals.isNotEmpty() && activeTension) {
                append("Biometric stress indicators correlate with active tension transit(s). ")
                append("The body often registers transit pressure before the mind does. ")
            }
            bio.sleepHours?.let { h ->
                if (h < 6.0) {
                    val moonActive = activeTransits.any { it.transitPlanet == "Moon" || it.natalPoint == "Moon" }
                    if (moonActive) append("Disrupted sleep may reflect an active Moon transit. ")
                }
            }
            if (bio.steps != null && bio.steps > 10000) {
                val jupiterActive = activeTransits.any { it.transitPlanet == "Jupiter" }
                if (jupiterActive) append("High physical energy is consistent with a Jupiter transit window. ")
            }
        }.trim()
    }

    private fun daysUntil(exactDate: String, from: LocalDate): Long =
        runCatching {
            val target = LocalDate.parse(exactDate.take(10), DATE_FORMAT)
            from.until(target, java.time.temporal.ChronoUnit.DAYS)
        }.getOrDefault(99L)
}
