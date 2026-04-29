package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName

data class YearAheadRequest(
    @SerializedName("profile")
    val profile: ProfilePayload,
    @SerializedName("year")
    val year: Int? = null,
)

data class YearNumberThemeData(
    @SerializedName("number")
    val number: Int,
    @SerializedName("theme")
    val theme: String,
    @SerializedName("description")
    val description: String? = null,
)

data class SolarReturnInfoData(
    @SerializedName("date")
    val date: String,
    @SerializedName("description")
    val description: String,
)

data class YearAheadEclipseEventData(
    @SerializedName("date")
    val date: String,
    @SerializedName("type")
    val type: String,
    @SerializedName("sign")
    val sign: String,
    @SerializedName("degree")
    val degree: Double? = null,
)

data class YearAheadImpactDetailData(
    @SerializedName("type")
    val type: String,
    @SerializedName("name")
    val name: String,
    @SerializedName("aspect")
    val aspect: String,
    @SerializedName("orb")
    val orb: Double? = null,
)

data class YearAheadEclipseImpactData(
    @SerializedName("eclipse")
    val eclipse: YearAheadEclipseEventData,
    @SerializedName("impacts")
    val impacts: List<YearAheadImpactDetailData> = emptyList(),
    @SerializedName("significance")
    val significance: String,
)

data class YearAheadEclipseBundleData(
    @SerializedName("all")
    val all: List<YearAheadEclipseEventData> = emptyList(),
    @SerializedName("personal_impacts")
    val personalImpacts: List<YearAheadEclipseImpactData> = emptyList(),
)

data class YearAheadIngressData(
    @SerializedName("date")
    val date: String,
    @SerializedName("planet")
    val planet: String,
    @SerializedName("sign")
    val sign: String,
    @SerializedName("impact")
    val impact: String,
)

data class YearAheadMonthlyForecastData(
    @SerializedName("month")
    val month: Int,
    @SerializedName("month_name")
    val monthName: String,
    @SerializedName("year")
    val year: Int,
    @SerializedName("season")
    val season: String,
    @SerializedName("focus")
    val focus: String,
    @SerializedName("element")
    val element: String,
    @SerializedName("personal_month")
    val personalMonth: Int,
    @SerializedName("eclipses")
    val eclipses: List<YearAheadEclipseEventData> = emptyList(),
    @SerializedName("ingresses")
    val ingresses: List<YearAheadIngressData> = emptyList(),
    @SerializedName("highlights")
    val highlights: List<String> = emptyList(),
)

data class YearAheadForecastData(
    @SerializedName("year")
    val year: Int,
    @SerializedName("personal_year")
    val personalYear: YearNumberThemeData,
    @SerializedName("universal_year")
    val universalYear: YearNumberThemeData,
    @SerializedName("solar_return")
    val solarReturn: SolarReturnInfoData,
    @SerializedName("eclipses")
    val eclipses: YearAheadEclipseBundleData,
    @SerializedName("ingresses")
    val ingresses: List<YearAheadIngressData> = emptyList(),
    @SerializedName("monthly_forecasts")
    val monthlyForecasts: List<YearAheadMonthlyForecastData> = emptyList(),
    @SerializedName("key_themes")
    val keyThemes: List<String> = emptyList(),
    @SerializedName("advice")
    val advice: List<String> = emptyList(),
)