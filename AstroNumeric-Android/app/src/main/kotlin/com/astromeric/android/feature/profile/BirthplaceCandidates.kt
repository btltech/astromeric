package com.astromeric.android.feature.profile

/** A place the geocoder found for what the person typed. The timezone comes later, from the coordinates. */
data class BirthplaceCandidate(
    val displayName: String,
    val latitude: Double,
    val longitude: Double,
)

/** "City, Region, Country", leaving out parts that are missing or repeated. */
fun birthplaceDisplayName(
    locality: String?,
    adminArea: String?,
    countryName: String?,
    featureName: String?,
    query: String,
): String =
    listOfNotNull(locality, adminArea, countryName)
        .map { it.trim() }
        .filter { it.isNotEmpty() }
        .distinct()
        .joinToString(separator = ", ")
        .ifBlank { featureName?.takeIf { it.isNotBlank() } ?: query }

/**
 * Drops repeats (the geocoder often lists one town several times) and keeps at most
 * [limit], in the order the geocoder ranked them.
 */
fun distinctBirthplaces(candidates: List<BirthplaceCandidate>, limit: Int = 5): List<BirthplaceCandidate> =
    candidates.distinctBy { it.displayName.lowercase() }.take(limit)
