package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName

const val DefaultHouseSystem = "Placidus"
const val PrivateUserLabel = "Private User"
const val PrivateProfileLabel = "Private Profile"
const val OtherPersonLabel = "Other Person"
const val FriendLabel = "Friend"
const val MaskedDateLabel = "••••-••-••"
const val HiddenValueLabel = "Hidden"

enum class TimeConfidence(
    val wireValue: String,
    val displayTitle: String,
    val shortLabel: String,
) {
    EXACT("exact", "I know my exact birth time", "Exact"),
    APPROXIMATE("approximate", "I have an approximate time", "Approximate"),
    UNKNOWN("unknown", "I don't know my birth time", "Unknown");

    companion object {
        fun fromWireValue(value: String?): TimeConfidence =
            entries.firstOrNull { it.wireValue == value } ?: UNKNOWN
    }
}

enum class DataQuality(
    val label: String,
    val description: String,
) {
    FULL(
        label = "Full Data",
        description = "Your chart is calculated from your exact birth time and place.",
    ),
    DATE_AND_PLACE(
        label = "No Birth Time",
        description = "Rising sign and houses are estimated because birth time is unknown or approximate.",
    ),
    DATE_ONLY(
        label = "Date Only",
        description = "Only your Sun sign is reliable until birthplace coordinates are confirmed.",
    ),
}

enum class PrivacyDisplayRole {
    ACTIVE_USER,
    GENERIC_PROFILE,
    PARTNER,
    FRIEND,
    SHARE,
}

data class AppProfile(
    val id: Int,
    val name: String,
    val dateOfBirth: String,
    val timeOfBirth: String?,
    val timeConfidence: TimeConfidence,
    val placeOfBirth: String?,
    val latitude: Double?,
    val longitude: Double?,
    val timezone: String?,
    val houseSystem: String = DefaultHouseSystem,
) {
    val isRemoteBacked: Boolean
        get() = id > 0

    val isLocalOnly: Boolean
        get() = !isRemoteBacked

    val hasCoordinates: Boolean
        get() = latitude != null && longitude != null

    val hasTimezone: Boolean
        get() = !timezone.isNullOrBlank()

    val hasBirthTime: Boolean
        get() = !timeOfBirth.isNullOrBlank()

    val canRequestNatalChart: Boolean
        get() = hasCoordinates && hasTimezone

    val canRequestForecast: Boolean
        get() = canRequestNatalChart && hasBirthTime

    val dataQuality: DataQuality
        get() {
            val hasExactTime = hasBirthTime && timeConfidence == TimeConfidence.EXACT
            return when {
                hasCoordinates && hasExactTime -> DataQuality.FULL
                hasCoordinates -> DataQuality.DATE_AND_PLACE
                else -> DataQuality.DATE_ONLY
            }
        }
}

data class ProfileDraft(
    val id: Int? = null,
    val name: String,
    val dateOfBirth: String,
    val timeOfBirth: String?,
    val timeConfidence: TimeConfidence,
    val placeOfBirth: String,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
    val houseSystem: String = DefaultHouseSystem,
)

data class ProfilePayload(
    @SerializedName("name")
    val name: String,
    @SerializedName("date_of_birth")
    val dateOfBirth: String,
    @SerializedName("time_of_birth")
    val timeOfBirth: String?,
    @SerializedName("time_confidence")
    val timeConfidence: String? = null,
    @SerializedName("place_of_birth")
    val placeOfBirth: String?,
    @SerializedName("latitude")
    val latitude: Double?,
    @SerializedName("longitude")
    val longitude: Double?,
    @SerializedName("timezone")
    val timezone: String?,
    @SerializedName("house_system")
    val houseSystem: String?,
)

fun AppProfile.toPayload(hideSensitive: Boolean = false): ProfilePayload =
    ProfilePayload(
        name = if (hideSensitive) PrivateUserLabel else name,
        dateOfBirth = dateOfBirth,
        timeOfBirth = timeOfBirth,
        timeConfidence = timeConfidence.wireValue,
        placeOfBirth = if (hideSensitive) null else placeOfBirth,
        latitude = latitude,
        longitude = longitude,
        timezone = timezone,
        houseSystem = houseSystem,
    )

fun AppProfile.displayName(
    hideSensitive: Boolean,
    role: PrivacyDisplayRole = PrivacyDisplayRole.GENERIC_PROFILE,
    index: Int? = null,
): String {
    if (!hideSensitive) {
        return name
    }

    return when (role) {
        PrivacyDisplayRole.ACTIVE_USER -> "You"
        PrivacyDisplayRole.PARTNER -> OtherPersonLabel
        PrivacyDisplayRole.FRIEND -> FriendLabel
        PrivacyDisplayRole.SHARE -> PrivateProfileLabel
        PrivacyDisplayRole.GENERIC_PROFILE -> {
            if (index != null) {
                "Profile ${index + 1}"
            } else {
                val normalizedId = kotlin.math.abs(id)
                if (normalizedId > 0) "Profile $normalizedId" else PrivateProfileLabel
            }
        }
    }
}

fun AppProfile.maskedDateOfBirth(hideSensitive: Boolean): String =
    if (hideSensitive) MaskedDateLabel else dateOfBirth

fun AppProfile.maskedBirthTime(hideSensitive: Boolean): String = when {
    hideSensitive -> HiddenValueLabel
    timeOfBirth.isNullOrBlank() -> "Unknown"
    else -> timeOfBirth
}

fun AppProfile.maskedBirthplace(hideSensitive: Boolean): String = when {
    hideSensitive -> HiddenValueLabel
    placeOfBirth.isNullOrBlank() -> "Birthplace missing"
    else -> placeOfBirth
}

data class CreateProfileRequest(
    @SerializedName("name")
    val name: String,
    @SerializedName("date_of_birth")
    val dateOfBirth: String,
    @SerializedName("time_of_birth")
    val timeOfBirth: String?,
    @SerializedName("time_confidence")
    val timeConfidence: String,
    @SerializedName("place_of_birth")
    val placeOfBirth: String?,
    @SerializedName("latitude")
    val latitude: Double?,
    @SerializedName("longitude")
    val longitude: Double?,
    @SerializedName("timezone")
    val timezone: String?,
    @SerializedName("save_profile")
    val saveProfile: Boolean = true,
)

data class UpdateProfileRequest(
    @SerializedName("name")
    val name: String,
    @SerializedName("time_of_birth")
    val timeOfBirth: String?,
    @SerializedName("time_confidence")
    val timeConfidence: String,
    @SerializedName("place_of_birth")
    val placeOfBirth: String?,
    @SerializedName("latitude")
    val latitude: Double?,
    @SerializedName("longitude")
    val longitude: Double?,
    @SerializedName("timezone")
    val timezone: String?,
    @SerializedName("house_system")
    val houseSystem: String?,
)

data class ForecastRequest(
    @SerializedName("profile")
    val profile: ProfilePayload,
    @SerializedName("scope")
    val scope: String,
    @SerializedName("include_details")
    val includeDetails: Boolean = true,
    @SerializedName("tone")
    val tone: String = "balanced_mystical",
)

data class MorningBriefBullet(
    @SerializedName("emoji")
    val emoji: String? = null,
    @SerializedName("text")
    val text: String = "",
)

data class MorningBriefData(
    @SerializedName("greeting")
    val greeting: String? = null,
    @SerializedName("bullets")
    val bullets: List<MorningBriefBullet> = emptyList(),
    @SerializedName("personal_day")
    val personalDay: Int? = null,
    @SerializedName("moon_phase")
    val moonPhase: String? = null,
    @SerializedName("vibe")
    val vibe: String? = null,
)

data class ForecastSectionData(
    @SerializedName("title")
    val title: String,
    @SerializedName("summary")
    val summary: String,
    @SerializedName("topics")
    val topics: Map<String, Float> = emptyMap(),
    @SerializedName("avoid")
    val avoid: List<String> = emptyList(),
    @SerializedName("embrace")
    val embrace: List<String> = emptyList(),
)

data class DailyForecastData(
    @SerializedName("profile")
    val profile: ProfilePayload? = null,
    @SerializedName("date")
    val date: String? = null,
    @SerializedName("scope")
    val scope: String? = null,
    @SerializedName("sections")
    val sections: List<ForecastSectionData> = emptyList(),
    @SerializedName("overall_score")
    val overallScore: Float? = null,
    @SerializedName("generated_at")
    val generatedAt: String? = null,
)

data class RemoteProfileDto(
    @SerializedName("id")
    val id: Int,
    @SerializedName("name")
    val name: String,
    @SerializedName("date_of_birth")
    val dateOfBirth: String,
    @SerializedName("time_of_birth")
    val timeOfBirth: String?,
    @SerializedName("time_confidence")
    val timeConfidence: String?,
    @SerializedName("place_of_birth")
    val placeOfBirth: String?,
    @SerializedName("latitude")
    val latitude: Double?,
    @SerializedName("longitude")
    val longitude: Double?,
    @SerializedName("timezone")
    val timezone: String?,
    @SerializedName("house_system")
    val houseSystem: String?,
)

fun RemoteProfileDto.toDomain(): AppProfile =
    AppProfile(
        id = id,
        name = name,
        dateOfBirth = dateOfBirth,
        timeOfBirth = timeOfBirth,
        timeConfidence = TimeConfidence.fromWireValue(timeConfidence),
        placeOfBirth = placeOfBirth,
        latitude = latitude,
        longitude = longitude,
        timezone = timezone,
        houseSystem = houseSystem ?: DefaultHouseSystem,
    )

data class RemoteCreateProfileRequest(
    @SerializedName("name")
    val name: String,
    @SerializedName("date_of_birth")
    val dateOfBirth: String,
    @SerializedName("time_of_birth")
    val timeOfBirth: String?,
    @SerializedName("time_confidence")
    val timeConfidence: String,
    @SerializedName("place_of_birth")
    val placeOfBirth: String?,
    @SerializedName("latitude")
    val latitude: Double?,
    @SerializedName("longitude")
    val longitude: Double?,
    @SerializedName("timezone")
    val timezone: String?,
    @SerializedName("house_system")
    val houseSystem: String?,
)

data class RemoteUpdateProfileRequest(
    @SerializedName("name")
    val name: String,
    @SerializedName("time_of_birth")
    val timeOfBirth: String?,
    @SerializedName("time_confidence")
    val timeConfidence: String,
    @SerializedName("place_of_birth")
    val placeOfBirth: String?,
    @SerializedName("latitude")
    val latitude: Double?,
    @SerializedName("longitude")
    val longitude: Double?,
    @SerializedName("timezone")
    val timezone: String?,
    @SerializedName("house_system")
    val houseSystem: String?,
)

fun AppProfile.toRemoteCreateRequest(): RemoteCreateProfileRequest =
    RemoteCreateProfileRequest(
        name = name,
        dateOfBirth = dateOfBirth,
        timeOfBirth = timeOfBirth,
        timeConfidence = timeConfidence.wireValue,
        placeOfBirth = placeOfBirth,
        latitude = latitude,
        longitude = longitude,
        timezone = timezone,
        houseSystem = houseSystem,
    )

fun AppProfile.toRemoteUpdateRequest(): RemoteUpdateProfileRequest =
    RemoteUpdateProfileRequest(
        name = name,
        timeOfBirth = timeOfBirth,
        timeConfidence = timeConfidence.wireValue,
        placeOfBirth = placeOfBirth,
        latitude = latitude,
        longitude = longitude,
        timezone = timezone,
        houseSystem = houseSystem,
    )

data class V2ApiResponse<T>(
    @SerializedName("status")
    val status: String,
    @SerializedName("data")
    val data: T,
)
