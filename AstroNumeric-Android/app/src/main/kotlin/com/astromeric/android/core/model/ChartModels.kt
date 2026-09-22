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

// ---------------------------------------------------------------------------
// Advanced charts (iOS parity): solar arc, relocation, lunar return,
// profections, declinations, fixed stars. Shapes mirror backend
// backend/app/routers/charts.py exactly.
// ---------------------------------------------------------------------------

data class SolarArcChartRequest(
    @SerializedName("profile") val profile: ProfilePayload,
    @SerializedName("target_date") val targetDate: String? = null,
)

data class RelocationChartRequest(
    @SerializedName("profile") val profile: ProfilePayload,
    @SerializedName("new_latitude") val newLatitude: Double,
    @SerializedName("new_longitude") val newLongitude: Double,
    @SerializedName("new_timezone") val newTimezone: String? = null,
)

data class LunarReturnChartRequest(
    @SerializedName("profile") val profile: ProfilePayload,
    @SerializedName("target_date") val targetDate: String? = null,
    @SerializedName("location_lat") val locationLat: Double? = null,
    @SerializedName("location_lon") val locationLon: Double? = null,
    @SerializedName("location_tz") val locationTz: String? = null,
)

data class ProfectionsRequestData(
    @SerializedName("profile") val profile: ProfilePayload,
    @SerializedName("ref_date") val refDate: String? = null,
)

data class DeclinationsRequestData(
    @SerializedName("profile") val profile: ProfilePayload,
)

data class FixedStarPlanetInput(
    @SerializedName("name") val name: String,
    @SerializedName("absolute_degree") val absoluteDegree: Double,
)

data class FixedStarsRequestData(
    @SerializedName("planets") val planets: List<FixedStarPlanetInput>,
    @SerializedName("orb") val orb: Double? = 1.0,
)

data class ProfectionsData(
    @SerializedName("age") val age: Int = 0,
    @SerializedName("ascendant_sign") val ascendantSign: String? = null,
    @SerializedName("annual_house") val annualHouse: Int = 0,
    @SerializedName("annual_sign") val annualSign: String? = null,
    @SerializedName("annual_lord") val annualLord: String? = null,
    @SerializedName("annual_focus") val annualFocus: String = "",
    @SerializedName("annual_lord_themes") val annualLordThemes: String = "",
    @SerializedName("monthly_house") val monthlyHouse: Int = 0,
    @SerializedName("monthly_sign") val monthlySign: String? = null,
    @SerializedName("monthly_lord") val monthlyLord: String? = null,
    @SerializedName("monthly_focus") val monthlyFocus: String = "",
    @SerializedName("months_into_year") val monthsIntoYear: Int = 0,
    @SerializedName("interpretation") val interpretation: String = "",
)

data class DeclinationEntry(
    @SerializedName("name") val name: String = "",
    @SerializedName("longitude") val longitude: Double = 0.0,
    @SerializedName("latitude") val latitude: Double = 0.0,
    @SerializedName("declination") val declination: Double = 0.0,
    @SerializedName("out_of_bounds") val outOfBounds: Boolean = false,
)

data class DeclinationParallel(
    @SerializedName("planet_a") val planetA: String = "",
    @SerializedName("planet_b") val planetB: String = "",
    @SerializedName("type") val type: String = "",
    @SerializedName("orb") val orb: Double = 0.0,
    @SerializedName("strength") val strength: Double = 0.0,
)

data class DeclinationsData(
    @SerializedName("declinations") val declinations: List<DeclinationEntry> = emptyList(),
    @SerializedName("parallels") val parallels: List<DeclinationParallel> = emptyList(),
    @SerializedName("note") val note: String? = null,
)

data class FixedStarConjunction(
    @SerializedName("planet") val planet: String = "",
    @SerializedName("star") val star: String = "",
    @SerializedName("orb") val orb: Double = 0.0,
    @SerializedName("nature") val nature: String = "",
    @SerializedName("keywords") val keywords: String = "",
    @SerializedName("interpretation") val interpretation: String = "",
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
    // "flatlib" for real ephemeris data; "stub" / "polar-fallback" mean the positions
    // are approximated and must not be shown as a real chart.
    @SerializedName("provider")
    val provider: String? = null,
    @SerializedName("degraded")
    val degraded: Boolean? = null,
    @SerializedName("note")
    val note: String? = null,
    // Solar arc
    @SerializedName("solar_arc_degrees")
    val solarArcDegrees: Double? = null,
    @SerializedName("directed_to")
    val directedTo: String? = null,
    // Lunar return
    @SerializedName("return_datetime_local")
    val returnDatetimeLocal: String? = null,
) {
    val isApproximated: Boolean
        get() = degraded == true || provider == "stub" || provider == "polar-fallback"
}

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
