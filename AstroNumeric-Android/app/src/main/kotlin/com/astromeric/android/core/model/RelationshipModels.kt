package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName
import java.time.Instant
import java.util.UUID

data class SavedRelationshipData(
    val id: String = UUID.randomUUID().toString(),
    val primaryProfileId: Int,
    val comparisonProfileId: Int,
    val primaryName: String,
    val comparisonName: String,
    val primaryDateOfBirth: String,
    val comparisonDateOfBirth: String,
    val mode: CompatibilityMode,
    val overallScore: Float,
    val summary: String,
    val dimensions: List<CompatibilityDimensionData> = emptyList(),
    val strengths: List<String> = emptyList(),
    val challenges: List<String> = emptyList(),
    val recommendations: List<String> = emptyList(),
    val confidence: Int? = null,
    val dataQualityNote: String? = null,
    val createdAt: String = Instant.now().toString(),
    val updatedAt: String = Instant.now().toString(),
) {
    fun pairMatches(other: SavedRelationshipData): Boolean =
        primaryProfileId == other.primaryProfileId &&
            comparisonProfileId == other.comparisonProfileId &&
            mode == other.mode

    fun redactedCopy(): SavedRelationshipData = copy(
        primaryName = "You",
        comparisonName = "${mode.label} Match",
        primaryDateOfBirth = MaskedDateLabel,
        comparisonDateOfBirth = MaskedDateLabel,
    )
}

fun CompatibilityReportData.toSavedRelationship(
    primaryProfile: AppProfile,
    comparisonProfile: AppProfile,
    mode: CompatibilityMode,
): SavedRelationshipData {
    val timestamp = generatedAt.ifBlank { Instant.now().toString() }
    return SavedRelationshipData(
        primaryProfileId = primaryProfile.id,
        comparisonProfileId = comparisonProfile.id,
        primaryName = primaryProfile.name,
        comparisonName = comparisonProfile.name,
        primaryDateOfBirth = primaryProfile.dateOfBirth,
        comparisonDateOfBirth = comparisonProfile.dateOfBirth,
        mode = mode,
        overallScore = overallScore,
        summary = summary,
        dimensions = dimensions,
        strengths = strengths,
        challenges = challenges,
        recommendations = recommendations,
        confidence = confidence,
        dataQualityNote = dataQualityNote,
        createdAt = timestamp,
        updatedAt = timestamp,
    )
}

fun CompatibilityReportData.toSavedRelationship(
    primaryProfile: AppProfile,
    comparisonName: String,
    comparisonDateOfBirth: String,
    mode: CompatibilityMode,
): SavedRelationshipData {
    val timestamp = generatedAt.ifBlank { Instant.now().toString() }
    val trimmedName = comparisonName.trim()
    val trimmedDateOfBirth = comparisonDateOfBirth.trim()
    return SavedRelationshipData(
        primaryProfileId = primaryProfile.id,
        comparisonProfileId = manualComparisonProfileId(trimmedName, trimmedDateOfBirth),
        primaryName = primaryProfile.name,
        comparisonName = trimmedName,
        primaryDateOfBirth = primaryProfile.dateOfBirth,
        comparisonDateOfBirth = trimmedDateOfBirth,
        mode = mode,
        overallScore = overallScore,
        summary = summary,
        dimensions = dimensions,
        strengths = strengths,
        challenges = challenges,
        recommendations = recommendations,
        confidence = confidence,
        dataQualityNote = dataQualityNote,
        createdAt = timestamp,
        updatedAt = timestamp,
    )
}

fun manualComparisonProfileId(name: String, dateOfBirth: String): Int {
    val normalized = "${name.trim().lowercase()}|${dateOfBirth.trim()}"
    val positiveHash = normalized.hashCode().toLong().let { if (it < 0) -it else it }
    return -(1_000_000 + (positiveHash % 1_000_000L).toInt())
}

data class RelationshipTimingRequest(
    @SerializedName("sun_sign")
    val sunSign: String,
    @SerializedName("partner_sign")
    val partnerSign: String? = null,
    @SerializedName("date")
    val date: String? = null,
)

data class RelationshipTransitData(
    @SerializedName("sign")
    val sign: String,
    @SerializedName("start")
    val start: String,
    @SerializedName("end")
    val end: String,
    @SerializedName("planet")
    val planet: String,
    @SerializedName("emoji")
    val emoji: String? = null,
)

data class RelationshipRetrogradeData(
    @SerializedName("is_retrograde")
    val isRetrograde: Boolean,
    @SerializedName("message")
    val message: String? = null,
    @SerializedName("sign")
    val sign: String? = null,
    @SerializedName("start")
    val start: String? = null,
    @SerializedName("end")
    val end: String? = null,
    @SerializedName("days_remaining")
    val daysRemaining: Int? = null,
    @SerializedName("warning")
    val warning: String? = null,
    @SerializedName("emoji")
    val emoji: String? = null,
)

data class RelationshipFactorData(
    @SerializedName("factor")
    val factor: String,
    @SerializedName("impact")
    val impact: Int,
    @SerializedName("emoji")
    val emoji: String? = null,
)

data class RelationshipTimingData(
    @SerializedName("date")
    val date: String,
    @SerializedName("score")
    val score: Int,
    @SerializedName("rating")
    val rating: String,
    @SerializedName("rating_emoji")
    val ratingEmoji: String,
    @SerializedName("venus_transit")
    val venusTransit: RelationshipTransitData? = null,
    @SerializedName("mars_transit")
    val marsTransit: RelationshipTransitData? = null,
    @SerializedName("venus_retrograde")
    val venusRetrograde: RelationshipRetrogradeData,
    @SerializedName("factors")
    val factors: List<RelationshipFactorData> = emptyList(),
    @SerializedName("warnings")
    val warnings: List<String> = emptyList(),
    @SerializedName("recommendations")
    val recommendations: List<String> = emptyList(),
    @SerializedName("person1_sign")
    val person1Sign: String,
    @SerializedName("person2_sign")
    val person2Sign: String? = null,
    @SerializedName("love_themes")
    val loveThemes: Map<String, String> = emptyMap(),
)

data class RelationshipBestDayData(
    @SerializedName("date")
    val date: String,
    @SerializedName("weekday")
    val weekday: String,
    @SerializedName("score")
    val score: Int,
    @SerializedName("rating")
    val rating: String,
    @SerializedName("rating_emoji")
    val ratingEmoji: String,
    @SerializedName("is_today")
    val isToday: Boolean = false,
    @SerializedName("days_away")
    val daysAway: Int = 0,
    @SerializedName("key_factor")
    val keyFactor: String? = null,
    @SerializedName("warnings")
    val warnings: List<String> = emptyList(),
)

data class RelationshipBestDaysData(
    @SerializedName("sun_sign")
    val sunSign: String,
    @SerializedName("days_ahead")
    val daysAhead: Int,
    @SerializedName("best_days")
    val bestDays: List<RelationshipBestDayData> = emptyList(),
    @SerializedName("top_day")
    val topDay: RelationshipBestDayData? = null,
)

data class RelationshipEventData(
    @SerializedName("date")
    val date: String,
    @SerializedName("type")
    val type: String,
    @SerializedName("title")
    val title: String,
    @SerializedName("emoji")
    val emoji: String? = null,
    @SerializedName("impact")
    val impact: String,
    @SerializedName("is_personal")
    val isPersonal: Boolean = false,
    @SerializedName("description")
    val description: String,
    @SerializedName("rating")
    val rating: Int = 0,
)

data class RelationshipEventsData(
    @SerializedName("days_ahead")
    val daysAhead: Int,
    @SerializedName("sun_sign")
    val sunSign: String? = null,
    @SerializedName("total_events")
    val totalEvents: Int,
    @SerializedName("events")
    val events: List<RelationshipEventData> = emptyList(),
)

data class RelationshipVenusStatusData(
    @SerializedName("date")
    val date: String,
    @SerializedName("venus")
    val venus: RelationshipTransitData? = null,
    @SerializedName("mars")
    val mars: RelationshipTransitData? = null,
    @SerializedName("venus_retrograde")
    val venusRetrograde: RelationshipRetrogradeData,
)

data class RelationshipPhaseDetailData(
    @SerializedName("theme")
    val theme: String,
    @SerializedName("description")
    val description: String,
)

data class RelationshipPhasesData(
    @SerializedName("phases")
    val phases: Map<String, RelationshipPhaseDetailData> = emptyMap(),
    @SerializedName("house_order")
    val houseOrder: List<Int> = emptyList(),
    @SerializedName("description")
    val description: String,
)

data class RelationshipTimelineRequest(
    @SerializedName("sun_sign")
    val sunSign: String,
    @SerializedName("partner_sign")
    val partnerSign: String? = null,
    @SerializedName("months_ahead")
    val monthsAhead: Int = 6,
)

data class RelationshipTimelinePeriodData(
    @SerializedName("start")
    val start: String,
    @SerializedName("end")
    val end: String,
    @SerializedName("months")
    val months: Int,
)

data class RelationshipTimelineData(
    @SerializedName("generated_at")
    val generatedAt: String,
    @SerializedName("sun_sign")
    val sunSign: String,
    @SerializedName("partner_sign")
    val partnerSign: String? = null,
    @SerializedName("period")
    val period: RelationshipTimelinePeriodData,
    @SerializedName("today")
    val today: RelationshipTimingData,
    @SerializedName("period_score")
    val periodScore: Float,
    @SerializedName("period_outlook")
    val periodOutlook: String,
    @SerializedName("best_upcoming_days")
    val bestUpcomingDays: List<RelationshipBestDayData> = emptyList(),
    @SerializedName("events")
    val events: List<RelationshipEventData> = emptyList(),
    @SerializedName("events_by_month")
    val eventsByMonth: Map<String, List<RelationshipEventData>> = emptyMap(),
    @SerializedName("love_themes")
    val loveThemes: Map<String, String> = emptyMap(),
    @SerializedName("total_events")
    val totalEvents: Int,
    @SerializedName("personal_events")
    val personalEvents: Int,
)