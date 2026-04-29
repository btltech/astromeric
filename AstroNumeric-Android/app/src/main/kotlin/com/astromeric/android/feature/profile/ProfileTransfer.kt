package com.astromeric.android.feature.profile

import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DefaultHouseSystem
import com.astromeric.android.core.model.HiddenValueLabel
import com.astromeric.android.core.model.MaskedDateLabel
import com.astromeric.android.core.model.PrivateProfileLabel
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.ProfileDraft
import com.astromeric.android.core.model.TimeConfidence
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.maskedBirthplace
import com.astromeric.android.core.model.maskedBirthTime
import com.astromeric.android.core.model.maskedDateOfBirth
import com.google.gson.GsonBuilder
import java.time.Instant

private const val ProfileExportVersion = "1.1"
private val ProfileTransferGson = GsonBuilder().setPrettyPrinting().create()

data class ProfileExportEnvelope(
    val version: String = ProfileExportVersion,
    val exportedAt: String,
    val isRedacted: Boolean = false,
    val profile: ExportedProfileData,
)

data class ExportedProfileData(
    val name: String? = null,
    val dateOfBirth: String? = null,
    val timeOfBirth: String? = null,
    val timeConfidence: String? = null,
    val placeOfBirth: String? = null,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val timezone: String? = null,
    val houseSystem: String? = null,
)

fun AppProfile.exportFileName(hideSensitive: Boolean): String {
    if (hideSensitive) {
        return "private_profile.json"
    }

    val sanitizedName = name
        .trim()
        .replace(' ', '_')
        .replace('/', '-')
        .ifBlank { "profile" }
    return "${sanitizedName}_profile.json"
}

fun AppProfile.toProfileExportJson(): String = ProfileTransferGson.toJson(
    ProfileExportEnvelope(
        exportedAt = Instant.now().toString(),
        isRedacted = false,
        profile = ExportedProfileData(
            name = name,
            dateOfBirth = dateOfBirth,
            timeOfBirth = timeOfBirth,
            timeConfidence = timeConfidence.wireValue,
            placeOfBirth = placeOfBirth,
            latitude = latitude,
            longitude = longitude,
            timezone = timezone,
            houseSystem = houseSystem,
        ),
    ),
)

fun decodeProfileDraftFromJson(json: String): Result<ProfileDraft> = runCatching {
    val export = ProfileTransferGson.fromJson(json, ProfileExportEnvelope::class.java)
    val profile = export.profile

    val name = profile.name?.trim().orEmpty()
    val dateOfBirth = profile.dateOfBirth?.trim().orEmpty()
    val placeOfBirth = profile.placeOfBirth?.trim().orEmpty()
    val latitude = profile.latitude
    val longitude = profile.longitude
    val timezone = profile.timezone?.trim().orEmpty()

    require(name.isNotEmpty()) { "Imported profile is missing a name." }
    require(dateOfBirth.matches(Regex("^\\d{4}-\\d{2}-\\d{2}$"))) { "Imported profile needs a YYYY-MM-DD birth date." }
    require(placeOfBirth.isNotEmpty()) { "Imported profile is missing a birthplace." }
    require(latitude != null && longitude != null) { "Imported profile is missing coordinates." }
    require(timezone.isNotEmpty()) { "Imported profile is missing a timezone." }

    val normalizedTime = profile.timeOfBirth?.trim()?.takeIf { it.isNotEmpty() }
    ProfileDraft(
        name = name,
        dateOfBirth = dateOfBirth,
        timeOfBirth = normalizedTime,
        timeConfidence = when {
            normalizedTime == null -> TimeConfidence.UNKNOWN
            profile.timeConfidence.isNullOrBlank() -> TimeConfidence.EXACT
            else -> TimeConfidence.fromWireValue(profile.timeConfidence)
        },
        placeOfBirth = placeOfBirth,
        latitude = latitude,
        longitude = longitude,
        timezone = timezone,
        houseSystem = profile.houseSystem?.takeIf { it.isNotBlank() } ?: DefaultHouseSystem,
    )
}

fun AppProfile.toShareSummaryText(hideSensitive: Boolean): String = buildString {
    appendLine("AstroNumeric Profile")
    appendLine()
    appendLine("Name: ${displayName(hideSensitive, PrivacyDisplayRole.SHARE)}")
    appendLine("Date of Birth: ${maskedDateOfBirth(hideSensitive)}")
    appendLine("Time of Birth: ${maskedBirthTime(hideSensitive)}")
    appendLine("Place of Birth: ${maskedBirthplace(hideSensitive)}")
    appendLine()
    appendLine("Chart Accuracy: ${dataQuality.label}")
    appendLine(dataQuality.description)
    if (hideSensitive) {
        appendLine()
        appendLine("Sensitive details were hidden because privacy mode is enabled.")
    } else if (timeOfBirth == null) {
        appendLine()
        appendLine("Time of birth is unknown, so exact rising sign and house precision may be reduced.")
    }
    appendLine()
    append("Generated with AstroNumeric")
}

fun privacyModeSummary(enabled: Boolean): String = if (enabled) {
    "Names, birth details, and some share surfaces are masked in the UI, but server-backed features still use the profile data required to calculate results. Backup exports still contain full details so they can be restored later."
} else {
    "Profile details display in full inside the app. You can still export a backup, import a backup, or share a redacted summary whenever you need to control what leaves the screen."
}

fun privacySupportEmailBody(): String = buildString {
    append("Privacy question from Android app")
    append("\n\n")
    append("Device privacy mode is about UI redaction, not a network kill switch.")
    append("\n")
    append("Please describe the backend-held or device-held data question here.")
}