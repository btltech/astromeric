package com.astromeric.android.feature.profile

import android.content.Context
import com.astromeric.android.R
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

fun decodeProfileDraftFromJson(context: Context, json: String): Result<ProfileDraft> = runCatching {
    val export = ProfileTransferGson.fromJson(json, ProfileExportEnvelope::class.java)
    val profile = export.profile

    val name = profile.name?.trim().orEmpty()
    val dateOfBirth = profile.dateOfBirth?.trim().orEmpty()
    val placeOfBirth = profile.placeOfBirth?.trim().orEmpty()
    val latitude = profile.latitude
    val longitude = profile.longitude
    val timezone = profile.timezone?.trim().orEmpty()

    require(name.isNotEmpty()) { context.getString(R.string.profile_transfer_import_missing_name) }
    require(dateOfBirth.matches(Regex("^\\d{4}-\\d{2}-\\d{2}$"))) {
        context.getString(R.string.profile_transfer_import_invalid_birth_date)
    }
    require(placeOfBirth.isNotEmpty()) { context.getString(R.string.profile_transfer_import_missing_birthplace) }
    require(latitude != null && longitude != null) { context.getString(R.string.profile_transfer_import_missing_coordinates) }
    require(timezone.isNotEmpty()) { context.getString(R.string.profile_transfer_import_missing_timezone) }

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

fun AppProfile.toShareSummaryText(context: Context, hideSensitive: Boolean): String = buildString {
    appendLine(context.getString(R.string.profile_transfer_share_heading))
    appendLine()
    appendLine(
        context.getString(
            R.string.profile_transfer_share_name,
            displayName(hideSensitive, PrivacyDisplayRole.SHARE),
        ),
    )
    appendLine(context.getString(R.string.profile_transfer_share_date_of_birth, maskedDateOfBirth(hideSensitive)))
    appendLine(context.getString(R.string.profile_transfer_share_time_of_birth, maskedBirthTime(hideSensitive)))
    appendLine(context.getString(R.string.profile_transfer_share_place_of_birth, maskedBirthplace(hideSensitive)))
    appendLine()
    appendLine(context.getString(R.string.profile_transfer_share_chart_accuracy, dataQuality.label))
    appendLine(dataQuality.description)
    if (hideSensitive) {
        appendLine()
        appendLine(context.getString(R.string.profile_transfer_share_sensitive_hidden))
    } else if (timeOfBirth == null) {
        appendLine()
        appendLine(context.getString(R.string.profile_transfer_share_unknown_time))
    }
    appendLine()
    append(context.getString(R.string.profile_transfer_share_generated_with))
}

fun privacyModeSummary(context: Context, enabled: Boolean): String = if (enabled) {
    context.getString(R.string.profile_transfer_privacy_mode_enabled_summary)
} else {
    context.getString(R.string.profile_transfer_privacy_mode_disabled_summary)
}

fun privacySupportEmailBody(context: Context): String = buildString {
    append(context.getString(R.string.profile_transfer_privacy_email_intro))
    append("\n\n")
    append(context.getString(R.string.profile_transfer_privacy_email_body_line_1))
    append("\n")
    append(context.getString(R.string.profile_transfer_privacy_email_body_line_2))
}