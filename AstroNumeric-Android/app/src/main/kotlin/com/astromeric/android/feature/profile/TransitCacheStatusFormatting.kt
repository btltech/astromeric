package com.astromeric.android.feature.profile

import com.astromeric.android.core.data.local.CachedExactTransitSnapshot
import com.astromeric.android.core.data.local.SavedExactTransitLoadStatus
import com.astromeric.android.core.model.AstroDataSource
import java.time.Duration
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

internal fun exactTransitCacheStatusLabel(snapshot: CachedExactTransitSnapshot?): String {
    snapshot ?: return "No cached exact scan"
    val countLabel = when (snapshot.transits.size) {
        0 -> "0 upcoming"
        1 -> "1 upcoming"
        else -> "${snapshot.transits.size} upcoming"
    }
    return "${exactTransitCachedSourceLabel(snapshot.source)}, $countLabel, ${cacheAgeLabel(snapshot.cachedAtEpochMillis)}"
}

internal fun exactTransitCacheDetailLabel(snapshot: CachedExactTransitSnapshot?): String {
    snapshot ?: return "No saved exact transit snapshot yet. AstroNumeric will cache the next successful exact scan for offline alarm recovery."
    val formatted = CacheTimestampFormatter.format(
        Instant.ofEpochMilli(snapshot.cachedAtEpochMillis).atZone(ZoneId.systemDefault()),
    )
    return "Saved ${exactTransitCachedSourceLabel(snapshot.source).lowercase(Locale.getDefault())} from $formatted with ${snapshot.transits.size} upcoming aspect${if (snapshot.transits.size == 1) "" else "s"}."
}

internal fun exactTransitLoadStatusLabel(status: SavedExactTransitLoadStatus?): String {
    status ?: return "No recent exact scan"
    return "${exactTransitLoadSourceLabel(status.source, status.isCached)}, ${cacheAgeLabel(status.recordedAtEpochMillis)}"
}

internal fun exactTransitLoadStatusDetailLabel(status: SavedExactTransitLoadStatus?): String {
    status ?: return "No recent exact transit load has been recorded yet. After the next refresh, AstroNumeric will show whether transits came from backend, on-device Swiss, cache, or the local estimator."
    val formatted = CacheTimestampFormatter.format(
        Instant.ofEpochMilli(status.recordedAtEpochMillis).atZone(ZoneId.systemDefault()),
    )
    return "Last exact transit refresh used ${exactTransitLoadSourceLabel(status.source, status.isCached).lowercase(Locale.getDefault())} at $formatted."
}

private fun exactTransitCachedSourceLabel(source: AstroDataSource): String = when (source) {
    AstroDataSource.BACKEND -> "Cached backend scan"
    AstroDataSource.LOCAL_SWISS -> "Cached Swiss scan"
    AstroDataSource.LOCAL_ESTIMATE -> "Cached local estimate"
}

private fun exactTransitLoadSourceLabel(
    source: AstroDataSource,
    isCached: Boolean,
): String = when {
    isCached && source == AstroDataSource.LOCAL_SWISS -> "Cached Swiss scan"
    isCached -> "Cached backend scan"
    source == AstroDataSource.LOCAL_SWISS -> "On-device Swiss scan"
    source == AstroDataSource.LOCAL_ESTIMATE -> "Local estimate"
    else -> "Backend scan"
}

private fun cacheAgeLabel(epochMillis: Long): String {
    val elapsed = Duration.ofMillis((System.currentTimeMillis() - epochMillis).coerceAtLeast(0L))
    return when {
        elapsed.toMinutes() < 1 -> "just now"
        elapsed.toHours() < 1 -> "${elapsed.toMinutes()}m ago"
        elapsed.toHours() < 24 -> "${elapsed.toHours()}h ago"
        else -> "${elapsed.toDays()}d ago"
    }
}

private val CacheTimestampFormatter: DateTimeFormatter =
    DateTimeFormatter.ofPattern("MMM d, h:mm a", Locale.getDefault())