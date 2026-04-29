package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName
import java.time.LocalDate

data class LearningModuleData(
    @SerializedName("id")
    val id: String,
    @SerializedName("title")
    val title: String,
    @SerializedName("description")
    val description: String,
    @SerializedName("category")
    val category: String,
    @SerializedName("difficulty")
    val difficulty: String,
    @SerializedName("duration_minutes")
    val durationMinutes: Int,
    @SerializedName("content")
    val content: String,
    @SerializedName("keywords")
    val keywords: List<String> = emptyList(),
    @SerializedName("related_modules")
    val relatedModules: List<String> = emptyList(),
)

data class PaginatedLearningModulesData(
    @SerializedName("data")
    val data: List<LearningModuleData> = emptyList(),
    @SerializedName("items")
    val items: List<LearningModuleData> = emptyList(),
    @SerializedName("page")
    val page: Int = 1,
    @SerializedName("page_size")
    val pageSize: Int = 10,
    @SerializedName("total")
    val total: Int = 0,
    @SerializedName("pages")
    val pages: Int = 1,
)

data class ZodiacGuidanceData(
    @SerializedName("sign")
    val sign: String,
    @SerializedName("date_range")
    val dateRange: String,
    @SerializedName("element")
    val element: String,
    @SerializedName("ruling_planet")
    val rulingPlanet: String,
    @SerializedName("characteristics")
    val characteristics: List<String> = emptyList(),
    @SerializedName("compatibility")
    val compatibility: Map<String, Float> = emptyMap(),
    @SerializedName("guidance")
    val guidance: String,
)

data class GlossaryEntryData(
    @SerializedName("term")
    val term: String,
    @SerializedName("definition")
    val definition: String,
    @SerializedName("category")
    val category: String,
    @SerializedName("usage_example")
    val usageExample: String,
    @SerializedName("related_terms")
    val relatedTerms: List<String> = emptyList(),
)

data class PaginatedGlossaryEntriesData(
    @SerializedName("data")
    val data: List<GlossaryEntryData> = emptyList(),
    @SerializedName("items")
    val items: List<GlossaryEntryData> = emptyList(),
    @SerializedName("page")
    val page: Int = 1,
    @SerializedName("page_size")
    val pageSize: Int = 10,
    @SerializedName("total")
    val total: Int = 0,
    @SerializedName("pages")
    val pages: Int = 1,
)

fun AppProfile.zodiacSignName(): String? =
    runCatching { LocalDate.parse(dateOfBirth) }
        .map { date -> zodiacSignFor(date.monthValue, date.dayOfMonth) }
        .getOrNull()

private fun zodiacSignFor(month: Int, day: Int): String = when {
    (month == 3 && day >= 21) || (month == 4 && day <= 19) -> "aries"
    (month == 4 && day >= 20) || (month == 5 && day <= 20) -> "taurus"
    (month == 5 && day >= 21) || (month == 6 && day <= 20) -> "gemini"
    (month == 6 && day >= 21) || (month == 7 && day <= 22) -> "cancer"
    (month == 7 && day >= 23) || (month == 8 && day <= 22) -> "leo"
    (month == 8 && day >= 23) || (month == 9 && day <= 22) -> "virgo"
    (month == 9 && day >= 23) || (month == 10 && day <= 22) -> "libra"
    (month == 10 && day >= 23) || (month == 11 && day <= 21) -> "scorpio"
    (month == 11 && day >= 22) || (month == 12 && day <= 21) -> "sagittarius"
    (month == 12 && day >= 22) || (month == 1 && day <= 19) -> "capricorn"
    (month == 1 && day >= 20) || (month == 2 && day <= 18) -> "aquarius"
    else -> "pisces"
}