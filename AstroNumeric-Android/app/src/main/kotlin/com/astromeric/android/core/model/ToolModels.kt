package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale

enum class ToolProvenance(
    val label: String,
    val description: String,
) {
    CALCULATED("Calculated", "Driven by chart, transit, or numerology math."),
    HYBRID("Hybrid", "Blends calculation with interpretive guidance."),
    INTERPRETIVE("Interpretive", "Turns the signal into language, prompts, and reflection."),
    REFERENCE("Reference", "Guides and lookup material rather than a live reading."),
}

enum class TimingActivity(
    val wireValue: String,
    val displayName: String,
    val emoji: String,
) {
    BUSINESS_MEETING("business_meeting", "Meeting", "💼"),
    ROMANCE_DATE("romance_date", "Date", "❤️"),
    JOB_INTERVIEW("job_interview", "Interview", "🎯"),
    CREATIVE_WORK("creative_work", "Create", "🎨"),
    FINANCIAL_DECISION("financial_decision", "Finance", "💰"),
    TRAVEL("travel", "Travel", "✈️"),
    SIGNING_CONTRACTS("signing_contracts", "Sign", "✍️"),
    STARTING_PROJECT("starting_project", "Start", "🚀"),
    MEDITATION_SPIRITUAL("meditation_spiritual", "Meditate", "🧘");

    companion object {
        fun fromWireValue(value: String?): TimingActivity? =
            entries.firstOrNull { it.wireValue == value }
    }
}

enum class CompatibilityMode(
    val label: String,
) {
    ROMANTIC("Romantic"),
    FRIENDSHIP("Friendship"),
}

data class AffirmationData(
    @SerializedName("affirmation")
    val affirmation: String,
)

data class YesNoGuidanceData(
    @SerializedName("question")
    val question: String,
    @SerializedName("answer")
    val answer: String,
    @SerializedName("confidence")
    val confidence: Float,
    @SerializedName("reasoning")
    val reasoning: String,
    @SerializedName("guidance")
    val guidance: List<String> = emptyList(),
)

data class TarotCardData(
    @SerializedName("name")
    val name: String,
    @SerializedName("suit")
    val suit: String,
    @SerializedName("number")
    val number: Int,
    @SerializedName("upright")
    val upright: Boolean,
    @SerializedName("meaning")
    val meaning: String,
    @SerializedName("interpretation")
    val interpretation: String,
)

data class MoonPhaseInfoData(
    @SerializedName("phase")
    val phase: String,
    @SerializedName("illumination")
    val illumination: Float,
    @SerializedName("next_new_moon")
    val nextNewMoon: String,
    @SerializedName("next_full_moon")
    val nextFullMoon: String,
    @SerializedName("influence")
    val influence: String,
)

data class MoonCurrentPhaseData(
    @SerializedName("phase_name")
    val phaseName: String,
    @SerializedName("emoji")
    val emoji: String? = null,
    @SerializedName("illumination")
    val illumination: Float? = null,
    @SerializedName("days_until_next_phase")
    val daysUntilNextPhase: Float? = null,
    @SerializedName("moon_sign")
    val moonSign: String? = null,
    @SerializedName("is_waxing")
    val isWaxing: Boolean? = null,
    @SerializedName("is_waning")
    val isWaning: Boolean? = null,
)

data class MoonEventData(
    @SerializedName("type")
    val type: String,
    @SerializedName("date")
    val date: String,
    @SerializedName("emoji")
    val emoji: String? = null,
    @SerializedName("days_away")
    val daysAway: Float? = null,
    @SerializedName("sign")
    val sign: String? = null,
)

data class MoonEventsData(
    @SerializedName("events")
    val events: List<MoonEventData> = emptyList(),
    @SerializedName("days_ahead")
    val daysAhead: Int = 30,
)

data class MoonRitualRequest(
    @SerializedName("profile")
    val profile: ProfilePayload? = null,
)

data class MoonRitualDetail(
    @SerializedName("phase")
    val phase: String? = null,
    @SerializedName("moon_sign")
    val moonSign: String? = null,
    @SerializedName("theme")
    val theme: String? = null,
    @SerializedName("energy")
    val energy: String? = null,
    @SerializedName("sign_focus")
    val signFocus: String? = null,
    @SerializedName("activities")
    val activities: List<String> = emptyList(),
    @SerializedName("avoid")
    val avoid: List<String> = emptyList(),
    @SerializedName("element_boost")
    val elementBoost: String? = null,
    @SerializedName("body_focus")
    val bodyFocus: String? = null,
    @SerializedName("crystals")
    val crystals: List<String> = emptyList(),
    @SerializedName("colors")
    val colors: List<String> = emptyList(),
    @SerializedName("affirmation")
    val affirmation: String? = null,
)

data class MoonRitualSummary(
    @SerializedName("current_phase")
    val currentPhase: MoonCurrentPhaseData? = null,
    @SerializedName("moon_sign")
    val moonSign: String? = null,
    @SerializedName("ritual")
    val ritual: MoonRitualDetail? = null,
    @SerializedName("upcoming_events")
    val upcomingEvents: List<MoonEventData> = emptyList(),
)

data class LifePhaseCurrentData(
    @SerializedName("name")
    val name: String,
    @SerializedName("age")
    val age: Int,
    @SerializedName("min_age")
    val minAge: Int,
    @SerializedName("max_age")
    val maxAge: Int,
    @SerializedName("duration")
    val duration: String,
    @SerializedName("narrative")
    val narrative: String,
    @SerializedName("keywords")
    val keywords: List<String> = emptyList(),
    @SerializedName("progress_pct")
    val progressPct: Int,
)

data class UpcomingLifePhaseData(
    @SerializedName("name")
    val name: String,
    @SerializedName("begins_in_years")
    val beginsInYears: Int,
    @SerializedName("begins_at_age")
    val beginsAtAge: Int,
    @SerializedName("preview")
    val preview: String,
)

data class LifePhaseData(
    @SerializedName("current_phase")
    val currentPhase: LifePhaseCurrentData,
    @SerializedName("next_phase")
    val nextPhase: UpcomingLifePhaseData? = null,
)

data class CompatibilityPairRequest(
    @SerializedName("person_a")
    val personA: ProfilePayload,
    @SerializedName("person_b")
    val personB: ProfilePayload,
)

data class CompatibilityDimensionData(
    @SerializedName("name")
    val name: String,
    @SerializedName("score")
    val score: Float,
    @SerializedName("interpretation")
    val interpretation: String? = null,
)

data class CompatibilityReportData(
    @SerializedName("person_a")
    val personA: ProfilePayload,
    @SerializedName("person_b")
    val personB: ProfilePayload,
    @SerializedName("overall_score")
    val overallScore: Float,
    @SerializedName("summary")
    val summary: String,
    @SerializedName("dimensions")
    val dimensions: List<CompatibilityDimensionData> = emptyList(),
    @SerializedName("strengths")
    val strengths: List<String> = emptyList(),
    @SerializedName("challenges")
    val challenges: List<String> = emptyList(),
    @SerializedName("recommendations")
    val recommendations: List<String> = emptyList(),
    @SerializedName("generated_at")
    val generatedAt: String,
    @SerializedName("confidence")
    val confidence: Int? = null,
    @SerializedName("data_quality_note")
    val dataQualityNote: String? = null,
)

data class DoDontData(
    @SerializedName("dos")
    val dos: List<String> = emptyList(),
    @SerializedName("donts")
    val donts: List<String> = emptyList(),
    @SerializedName("personal_day")
    val personalDay: Int,
    @SerializedName("moon_phase")
    val moonPhase: String,
    @SerializedName("mercury_retrograde")
    val mercuryRetrograde: Boolean = false,
    @SerializedName("venus_retrograde")
    val venusRetrograde: Boolean = false,
)

data class TimingAdviceRequest(
    @SerializedName("activity")
    val activity: String,
    @SerializedName("profile")
    val profile: ProfilePayload?,
    @SerializedName("latitude")
    val latitude: Double,
    @SerializedName("longitude")
    val longitude: Double,
    @SerializedName("tz")
    val timezone: String,
)

data class TimingHourPayload(
    @SerializedName("start")
    val start: String,
    @SerializedName("end")
    val end: String,
    @SerializedName("planet")
    val planet: String,
)

data class TimingDayPayload(
    @SerializedName("date")
    val date: String,
    @SerializedName("score")
    val score: Int,
    @SerializedName("rating")
    val rating: String,
    @SerializedName("warnings")
    val warnings: List<String>? = null,
    @SerializedName("recommendations")
    val recommendations: List<String>? = null,
    @SerializedName("best_hours")
    val bestHours: List<TimingHourPayload>? = null,
    @SerializedName("weekday")
    val weekday: String? = null,
)

data class TimingAdvicePayload(
    @SerializedName("activity")
    val activity: String,
    @SerializedName("advice")
    val advice: String? = null,
    @SerializedName("today")
    val today: TimingDayPayload,
    @SerializedName("best_upcoming")
    val bestUpcoming: TimingDayPayload? = null,
    @SerializedName("today_is_best")
    val todayIsBest: Boolean? = null,
    @SerializedName("all_days")
    val allDays: List<TimingDayPayload>? = null,
)

data class TimingToolResult(
    val activity: TimingActivity,
    val score: Float,
    val rating: String,
    val bestTimes: List<String>,
    val avoidTimes: List<String>,
    val tips: List<String>,
    val generatedAt: String,
    val advice: String,
)

fun AppProfile.toTimingAdviceRequest(activity: TimingActivity): TimingAdviceRequest =
    TimingAdviceRequest(
        activity = activity.wireValue,
        profile = toPayload(),
        latitude = latitude ?: 40.7128,
        longitude = longitude ?: -74.0060,
        timezone = timezone ?: "UTC",
    )

fun TimingAdvicePayload.toToolResult(activity: TimingActivity): TimingToolResult {
    val primaryDay = if (todayIsBest == false && bestUpcoming != null) bestUpcoming else today
    val dedupedTips = linkedSetOf<String>()

    advice?.takeIf { it.isNotBlank() }?.let(dedupedTips::add)
    primaryDay.recommendations.orEmpty()
        .filter { it.isNotBlank() }
        .forEach(dedupedTips::add)

    return TimingToolResult(
        activity = activity,
        score = primaryDay.score / 100f,
        rating = primaryDay.rating,
        bestTimes = primaryDay.bestHours.orEmpty().map { it.toWindowLabel() },
        avoidTimes = primaryDay.warnings.orEmpty(),
        tips = dedupedTips.toList(),
        generatedAt = primaryDay.date,
        advice = advice.orEmpty(),
    )
}

fun TimingHourPayload.toWindowLabel(): String {
    val startLabel = start.toTimingClockLabel()
    val endLabel = end.toTimingClockLabel()
    return "$startLabel - $endLabel"
}

fun String.toTimingLocalTimeOrNull(): LocalTime? {
    runCatching { OffsetDateTime.parse(this).toLocalTime() }.getOrNull()?.let { return it }
    runCatching { LocalDateTime.parse(this).toLocalTime() }.getOrNull()?.let { return it }
    runCatching { LocalTime.parse(this) }.getOrNull()?.let { return it }

    val trimmed = substringAfter('T', this)
        .substringBefore('+')
        .substringBefore('Z')
        .trim()
    if (trimmed.isBlank()) {
        return null
    }

    val segments = trimmed.split(':')
    if (segments.size < 2) {
        return null
    }

    val hour = segments.getOrNull(0)?.toIntOrNull() ?: return null
    val minute = segments.getOrNull(1)?.toIntOrNull() ?: return null
    return runCatching { LocalTime.of(hour, minute) }.getOrNull()
}

fun String.toTimingClockLabel(): String =
    toTimingLocalTimeOrNull()?.format(TimingClockFormatter) ?: this

private val TimingClockFormatter: DateTimeFormatter =
    DateTimeFormatter.ofPattern("HH:mm", Locale.getDefault())

fun AppProfile.toCompatibilityRequest(other: AppProfile): CompatibilityPairRequest =
    CompatibilityPairRequest(
        personA = toPayload(),
        personB = other.toPayload(),
    )