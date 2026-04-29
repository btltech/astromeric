package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName

data class NatalChartRequest(
    @SerializedName("profile")
    val profile: ProfilePayload,
    @SerializedName("lang")
    val lang: String = "en",
)

data class ProgressedChartRequestData(
    @SerializedName("profile")
    val profile: ProfilePayload,
    @SerializedName("target_date")
    val targetDate: String? = null,
)

data class PlanetPlacement(
    @SerializedName("name")
    val name: String,
    @SerializedName("sign")
    val sign: String,
    @SerializedName("degree")
    val degree: Double,
    @SerializedName("absolute_degree")
    val absoluteDegree: Double? = null,
    @SerializedName("house")
    val house: Int? = null,
    @SerializedName("retrograde")
    val retrograde: Boolean? = null,
    @SerializedName("dignity")
    val dignity: String? = null,
)

data class ChartPoint(
    @SerializedName("name")
    val name: String,
    @SerializedName("sign")
    val sign: String,
    @SerializedName("degree")
    val degree: Double,
    @SerializedName("absolute_degree")
    val absoluteDegree: Double? = null,
    @SerializedName("house")
    val house: Int? = null,
    @SerializedName("retrograde")
    val retrograde: Boolean? = null,
    @SerializedName("chart_type")
    val chartType: String? = null,
)

data class HousePlacement(
    @SerializedName("house")
    val house: Int,
    @SerializedName("sign")
    val sign: String,
    @SerializedName("degree")
    val degree: Double? = null,
)

data class ChartAspect(
    @SerializedName("planet_a")
    val planetA: String,
    @SerializedName("planet_b")
    val planetB: String,
    @SerializedName("type")
    val type: String,
    @SerializedName("orb")
    val orb: Double? = null,
    @SerializedName("strength")
    val strength: Double? = null,
)

data class ChartMetadata(
    @SerializedName("name")
    val name: String? = null,
    @SerializedName("date_of_birth")
    val dateOfBirth: String? = null,
    @SerializedName("time_of_birth")
    val timeOfBirth: String? = null,
    @SerializedName("birth_time_assumed")
    val birthTimeAssumed: Boolean? = null,
    @SerializedName("assumed_time_of_birth")
    val assumedTimeOfBirth: String? = null,
    @SerializedName("data_quality")
    val dataQuality: String? = null,
    @SerializedName("timezone")
    val timezone: String? = null,
    @SerializedName("house_system")
    val houseSystem: String? = null,
)

data class ChartData(
    @SerializedName("planets")
    val planets: List<PlanetPlacement> = emptyList(),
    @SerializedName("points")
    val points: List<ChartPoint> = emptyList(),
    @SerializedName("houses")
    val houses: List<HousePlacement> = emptyList(),
    @SerializedName("aspects")
    val aspects: List<ChartAspect> = emptyList(),
    @SerializedName("metadata")
    val metadata: ChartMetadata? = null,
)

data class NamedChartData(
    @SerializedName("name")
    val name: String,
    @SerializedName("chart")
    val chart: ChartData,
)

data class SynastryAspectData(
    @SerializedName("planet1")
    val planet1: String,
    @SerializedName("planet2")
    val planet2: String,
    @SerializedName("aspect")
    val aspect: String,
    @SerializedName("orb")
    val orb: Double,
    @SerializedName("applying")
    val applying: Boolean = false,
)

data class SynastryCompatibilityData(
    @SerializedName("strengths")
    val strengths: List<String> = emptyList(),
    @SerializedName("challenges")
    val challenges: List<String> = emptyList(),
    @SerializedName("advice")
    val advice: List<String> = emptyList(),
)

data class SynastryChartData(
    @SerializedName("person_a")
    val personA: NamedChartData,
    @SerializedName("person_b")
    val personB: NamedChartData,
    @SerializedName("synastry_aspects")
    val synastryAspects: List<SynastryAspectData> = emptyList(),
    @SerializedName("compatibility")
    val compatibility: SynastryCompatibilityData,
)

data class CompositeChartMetadata(
    @SerializedName("person_a")
    val personA: String,
    @SerializedName("person_b")
    val personB: String,
    @SerializedName("method")
    val method: String,
)

data class CompositeChartData(
    @SerializedName("planets")
    val planets: List<ChartPoint> = emptyList(),
    @SerializedName("metadata")
    val metadata: CompositeChartMetadata,
)
