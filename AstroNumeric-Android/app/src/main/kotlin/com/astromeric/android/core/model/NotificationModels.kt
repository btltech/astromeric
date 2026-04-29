package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName

enum class AlertFrequency(
    val wireValue: String,
    val label: String,
) {
    EVERY_RETROGRADE("every_retrograde", "Every Retrograde"),
    WEEKLY_DIGEST("weekly_digest", "Weekly Digest"),
    ONCE_PER_YEAR("once_per_year", "Once Per Year"),
    NONE("none", "None");

    companion object {
        fun fromWireValue(value: String?): AlertFrequency =
            entries.firstOrNull { it.wireValue == value } ?: EVERY_RETROGRADE
    }
}

enum class AstroNotificationCategory(
    val channelId: String,
    val label: String,
) {
    DAILY_READING("daily_reading", "Daily Reading"),
    MOON_PHASE("moon_phase", "Moon Phase"),
    HABIT_REMINDER("habit_reminder", "Habit Reminder"),
    TIMING_ALERT("timing_alert", "Timing Alert"),
    TRANSIT_ALERT("transit_alert", "Transit Alert"),
}

data class TransitDailyRequestData(
    @SerializedName("profile")
    val profile: ProfilePayload,
)

data class DailyTransitAspectData(
    @SerializedName("transit_planet")
    val transitPlanet: String,
    @SerializedName("natal_point")
    val natalPoint: String,
    @SerializedName("aspect")
    val aspect: String,
    @SerializedName("orb")
    val orb: Double,
    @SerializedName("interpretation")
    val interpretation: String? = null,
)

data class DailyTransitReportData(
    @SerializedName("date")
    val date: String,
    @SerializedName("profile_name")
    val profileName: String,
    @SerializedName("transits")
    val transits: List<DailyTransitAspectData> = emptyList(),
    @SerializedName("highlights")
    val highlights: List<DailyTransitAspectData> = emptyList(),
    @SerializedName("total_aspects")
    val totalAspects: Int = 0,
    @SerializedName("alert_level")
    val alertLevel: String = "low",
)

data class AlertPreferencesData(
    @SerializedName("alert_mercury_retrograde")
    val alertMercuryRetrograde: Boolean = true,
    @SerializedName("alert_frequency")
    val alertFrequency: String = AlertFrequency.EVERY_RETROGRADE.wireValue,
)

data class DeviceTokenRequestData(
    @SerializedName("token")
    val token: String,
    @SerializedName("platform")
    val platform: String = "android",
)

data class TransitAlertSubscriptionData(
    @SerializedName("profile_id")
    val profileId: Int,
    @SerializedName("email")
    val email: String,
    @SerializedName("subscribed")
    val subscribed: Boolean,
)

data class TransitAlertSubscriptionRequestData(
    @SerializedName("email")
    val email: String,
    @SerializedName("profile_id")
    val profileId: Int? = null,
    @SerializedName("profile")
    val profile: ProfilePayload? = null,
)

data class ExactTransitAspectData(
    @SerializedName("transit_planet")
    val transitPlanet: String,
    @SerializedName("natal_point")
    val natalPoint: String,
    @SerializedName("aspect")
    val aspect: String,
    @SerializedName("exact_date")
    val exactDate: String,
    @SerializedName("orb")
    val orb: Double,
    @SerializedName("is_applying")
    val isApplying: Boolean,
    @SerializedName("significance")
    val significance: String,
    @SerializedName("interpretation")
    val interpretation: String? = null,
)