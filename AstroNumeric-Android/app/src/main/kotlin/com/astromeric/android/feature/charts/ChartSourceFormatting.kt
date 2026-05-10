package com.astromeric.android.feature.charts

import android.content.Context
import com.astromeric.android.R
import com.astromeric.android.core.model.AstroDataSource

internal fun chartSourceLabel(
    context: Context,
    source: AstroDataSource?,
    isCached: Boolean,
): String = when {
    isCached && source == AstroDataSource.LOCAL_SWISS -> context.getString(R.string.chart_source_cached_local_swiss_label)
    isCached -> context.getString(R.string.chart_source_cached_backend_label)
    source == AstroDataSource.LOCAL_SWISS -> context.getString(R.string.chart_source_local_swiss_label)
    source == AstroDataSource.LOCAL_ESTIMATE -> context.getString(R.string.chart_source_local_estimate_label)
    source == AstroDataSource.BACKEND -> context.getString(R.string.chart_source_backend_label)
    else -> context.getString(R.string.chart_source_unavailable_label)
}

internal fun chartSourceDetail(
    context: Context,
    source: AstroDataSource?,
    isCached: Boolean,
): String = when {
    isCached && source == AstroDataSource.LOCAL_SWISS -> context.getString(R.string.chart_source_cached_local_swiss_detail)
    isCached -> context.getString(R.string.chart_source_cached_backend_detail)
    source == AstroDataSource.LOCAL_SWISS -> context.getString(R.string.chart_source_local_swiss_detail)
    source == AstroDataSource.LOCAL_ESTIMATE -> context.getString(R.string.chart_source_local_estimate_detail)
    source == AstroDataSource.BACKEND -> context.getString(R.string.chart_source_backend_detail)
    else -> context.getString(R.string.chart_source_unknown_detail)
}