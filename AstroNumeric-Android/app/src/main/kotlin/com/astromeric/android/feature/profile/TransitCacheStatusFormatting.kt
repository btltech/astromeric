package com.astromeric.android.feature.profile

import android.content.Context
import com.astromeric.android.R
import com.astromeric.android.core.data.local.CachedExactTransitSnapshot
import com.astromeric.android.core.data.local.SavedExactTransitLoadStatus
import com.astromeric.android.core.model.AstroDataSource
import java.time.Duration
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

internal fun exactTransitCacheStatusLabel(context: Context, snapshot: CachedExactTransitSnapshot?): String {
    snapshot ?: return context.getString(R.string.profile_exact_transit_cache_none)
    val countLabel = context.getString(R.string.profile_exact_transit_upcoming_count, snapshot.transits.size)
    return context.getString(
        R.string.profile_exact_transit_cache_status_format,
        context.exactTransitCachedSourceLabel(snapshot.source).asSentenceCase(),
        countLabel,
        context.cacheAgeLabel(snapshot.cachedAtEpochMillis),
    )
}

internal fun exactTransitCacheDetailLabel(context: Context, snapshot: CachedExactTransitSnapshot?): String {
    snapshot ?: return context.getString(R.string.profile_exact_transit_cache_detail_empty)
    val formatted = CacheTimestampFormatter.format(
        Instant.ofEpochMilli(snapshot.cachedAtEpochMillis).atZone(ZoneId.systemDefault()),
    )
    val aspectCountLabel = context.resources.getQuantityString(
        R.plurals.profile_exact_transit_upcoming_aspects,
        snapshot.transits.size,
        snapshot.transits.size,
    )
    return context.getString(
        R.string.profile_exact_transit_cache_detail_format,
        context.exactTransitCachedSourceLabel(snapshot.source),
        formatted,
        aspectCountLabel,
    )
}

internal fun exactTransitLoadStatusLabel(context: Context, status: SavedExactTransitLoadStatus?): String {
    status ?: return context.getString(R.string.profile_exact_transit_load_none)
    return context.getString(
        R.string.profile_exact_transit_load_status_format,
        context.exactTransitLoadSourceLabel(status.source, status.isCached).asSentenceCase(),
        context.cacheAgeLabel(status.recordedAtEpochMillis),
    )
}

internal fun exactTransitLoadStatusDetailLabel(context: Context, status: SavedExactTransitLoadStatus?): String {
    status ?: return context.getString(R.string.profile_exact_transit_load_detail_empty)
    val formatted = CacheTimestampFormatter.format(
        Instant.ofEpochMilli(status.recordedAtEpochMillis).atZone(ZoneId.systemDefault()),
    )
    return context.getString(
        R.string.profile_exact_transit_load_detail_format,
        context.exactTransitLoadSourceLabel(status.source, status.isCached),
        formatted,
    )
}

private fun Context.exactTransitCachedSourceLabel(source: AstroDataSource): String = when (source) {
    AstroDataSource.BACKEND -> getString(R.string.profile_exact_transit_source_cached_backend)
    AstroDataSource.LOCAL_SWISS -> getString(R.string.profile_exact_transit_source_cached_swiss)
    AstroDataSource.LOCAL_ESTIMATE -> getString(R.string.profile_exact_transit_source_cached_local_estimate)
}

private fun Context.exactTransitLoadSourceLabel(
    source: AstroDataSource,
    isCached: Boolean,
): String = when {
    isCached && source == AstroDataSource.LOCAL_SWISS -> getString(R.string.profile_exact_transit_source_cached_swiss)
    isCached -> getString(R.string.profile_exact_transit_source_cached_backend)
    source == AstroDataSource.LOCAL_SWISS -> getString(R.string.profile_exact_transit_source_on_device_swiss)
    source == AstroDataSource.LOCAL_ESTIMATE -> getString(R.string.profile_exact_transit_source_local_estimate)
    else -> getString(R.string.profile_exact_transit_source_backend)
}

private fun Context.cacheAgeLabel(epochMillis: Long): String {
    val elapsed = Duration.ofMillis((System.currentTimeMillis() - epochMillis).coerceAtLeast(0L))
    return when {
        elapsed.toMinutes() < 1 -> getString(R.string.profile_exact_transit_age_just_now)
        elapsed.toHours() < 1 -> getString(R.string.profile_exact_transit_age_minutes, elapsed.toMinutes())
        elapsed.toHours() < 24 -> getString(R.string.profile_exact_transit_age_hours, elapsed.toHours())
        else -> getString(R.string.profile_exact_transit_age_days, elapsed.toDays())
    }
}

private fun String.asSentenceCase(): String = replaceFirstChar { firstChar ->
    if (firstChar.isLowerCase()) firstChar.titlecase() else firstChar.toString()
}

private val CacheTimestampFormatter: DateTimeFormatter =
    DateTimeFormatter.ofPattern("MMM d, h:mm a", Locale.getDefault())