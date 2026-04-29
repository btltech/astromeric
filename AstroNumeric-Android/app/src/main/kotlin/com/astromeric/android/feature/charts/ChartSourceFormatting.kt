package com.astromeric.android.feature.charts

import com.astromeric.android.core.model.AstroDataSource

internal fun chartSourceLabel(
    source: AstroDataSource?,
    isCached: Boolean,
): String = when {
    isCached && source == AstroDataSource.LOCAL_SWISS -> "Cached on-device Swiss chart"
    isCached -> "Cached backend chart"
    source == AstroDataSource.LOCAL_SWISS -> "On-device Swiss chart"
    source == AstroDataSource.LOCAL_ESTIMATE -> "Local chart estimate"
    source == AstroDataSource.BACKEND -> "Live backend chart"
    else -> "Chart source unavailable"
}

internal fun chartSourceDetail(
    source: AstroDataSource?,
    isCached: Boolean,
): String = when {
    isCached && source == AstroDataSource.LOCAL_SWISS -> "The live request failed, so Android is showing the last saved on-device Swiss chart."
    isCached -> "The live request failed, so Android is showing the last saved backend chart."
    source == AstroDataSource.LOCAL_SWISS -> "Calculated on this device with bundled Swiss Ephemeris data."
    source == AstroDataSource.LOCAL_ESTIMATE -> "Estimated on this device from local fallback data."
    source == AstroDataSource.BACKEND -> "Fetched from the live AstroNumeric backend."
    else -> "The chart source could not be determined."
}