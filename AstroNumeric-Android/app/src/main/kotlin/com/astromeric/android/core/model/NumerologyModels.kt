package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName
import java.time.LocalDate

data class NumerologyRequestData(
    @SerializedName("profile")
    val profile: ProfilePayload,
    @SerializedName("include_extended")
    val includeExtended: Boolean = false,
    @SerializedName("language")
    val language: String = "en",
    @SerializedName("method")
    val method: String = "pythagorean",
)

data class LifePathData(
    @SerializedName("number")
    val number: Int,
    @SerializedName("meaning")
    val meaning: String,
    @SerializedName("traits")
    val traits: List<String> = emptyList(),
    @SerializedName("life_purpose")
    val lifePurpose: String,
)

data class PersonalYearData(
    @SerializedName("year")
    val year: Int,
    @SerializedName("cycle_number")
    val cycleNumber: Int,
    @SerializedName("interpretation")
    val interpretation: String,
    @SerializedName("focus_areas")
    val focusAreas: List<String> = emptyList(),
)

data class PinnacleData(
    @SerializedName("number")
    val number: Int,
    @SerializedName("ages")
    val ages: String? = null,
    @SerializedName("meaning")
    val meaning: String? = null,
)

data class ChallengeData(
    @SerializedName("number")
    val number: Int,
    @SerializedName("ages")
    val ages: String? = null,
    @SerializedName("meaning")
    val meaning: String? = null,
)

data class NumerologyHighlightData(
    @SerializedName("key")
    val key: String,
    @SerializedName("label")
    val label: String,
    @SerializedName("number")
    val number: Int,
    @SerializedName("meaning")
    val meaning: String,
)

data class NumerologySynthesisData(
    @SerializedName("summary")
    val summary: String,
    @SerializedName("strengths")
    val strengths: List<String> = emptyList(),
    @SerializedName("growth_edges")
    val growthEdges: List<String> = emptyList(),
    @SerializedName("current_focus")
    val currentFocus: String,
    @SerializedName("affirmation")
    val affirmation: String,
    @SerializedName("dominant_numbers")
    val dominantNumbers: List<NumerologyHighlightData> = emptyList(),
)

data class NumerologyData(
    @SerializedName("profile")
    val profile: ProfilePayload? = null,
    @SerializedName("life_path")
    val lifePath: LifePathData,
    @SerializedName("destiny_number")
    val destinyNumber: Int,
    @SerializedName("destiny_interpretation")
    val destinyInterpretation: String,
    @SerializedName("personal_year")
    val personalYear: PersonalYearData,
    @SerializedName("lucky_numbers")
    val luckyNumbers: List<Int> = emptyList(),
    @SerializedName("auspicious_days")
    val auspiciousDays: List<Int> = emptyList(),
    @SerializedName("numerology_insights")
    val numerologyInsights: Map<String, String> = emptyMap(),
    @SerializedName("pinnacles")
    val pinnacles: List<PinnacleData> = emptyList(),
    @SerializedName("challenges")
    val challenges: List<ChallengeData> = emptyList(),
    @SerializedName("synthesis")
    val synthesis: NumerologySynthesisData? = null,
    @SerializedName("generated_at")
    val generatedAt: String? = null,
) {
    val personalMonthNumber: Int?
        get() = numerologyInsights["personal_month"]?.let {
            reduceNumber(personalYear.cycleNumber + LocalDate.now().monthValue)
        }

    val personalDayNumber: Int?
        get() = numerologyInsights["personal_day"]?.let { insight ->
            reduceNumber((personalMonthNumber ?: reduceNumber(personalYear.cycleNumber + LocalDate.now().monthValue)) + LocalDate.now().dayOfMonth)
        }
}

private fun reduceNumber(value: Int): Int {
    var current = value
    while (current > 9) {
        current = current.toString().sumOf { it.digitToInt() }
    }
    return current
}