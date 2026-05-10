package com.astromeric.android.app

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import com.astromeric.android.R
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Widget showing the current planetary hour ruler, its symbol, active window, and next hour.
 * Reads pre-computed schedule from [PlanetaryHourSnapshotStore] (populated by [AstroRefreshWorker]).
 */
class PlanetaryHourWidgetProvider : AppWidgetProvider() {
    override fun onEnabled(context: Context) {
        super.onEnabled(context)
        AstroBackgroundScheduler.schedulePeriodicRefresh(context)
        AstroBackgroundScheduler.scheduleImmediateRefresh(context)
    }

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        super.onUpdate(context, appWidgetManager, appWidgetIds)
        AstroBackgroundScheduler.scheduleImmediateRefresh(context)
        appWidgetIds.forEach { updateWidget(context, appWidgetManager, it) }
    }

    companion object {
        fun refreshAllWidgets(context: Context) {
            val manager = AppWidgetManager.getInstance(context)
            val ids = manager.getAppWidgetIds(ComponentName(context, PlanetaryHourWidgetProvider::class.java))
            ids.forEach { updateWidget(context, manager, it) }
        }

        private fun updateWidget(
            context: Context,
            appWidgetManager: AppWidgetManager,
            appWidgetId: Int,
        ) {
            val now = System.currentTimeMillis()
            val schedule = PlanetaryHourSnapshotStore(context).read()
            val timeFmt = SimpleDateFormat("h:mm a", Locale.getDefault())

            val current = schedule.firstOrNull { now >= it.startEpochMillis && now < it.endEpochMillis }
            val currentIdx = schedule.indexOf(current)
            val next = schedule.getOrNull(currentIdx + 1)

            val launchIntent = buildLaunchPendingIntent(context, appWidgetId)

            val views = RemoteViews(context.packageName, R.layout.planetary_hour_widget).apply {
                if (current != null) {
                    setTextViewText(R.id.phwPlanetSymbol, current.rulerSymbol)
                    setTextViewText(R.id.phwPlanetName, current.rulerName)
                    val window = "${timeFmt.format(Date(current.startEpochMillis))} – ${timeFmt.format(Date(current.endEpochMillis))}"
                    setTextViewText(R.id.phwWindow, window)
                } else {
                    setTextViewText(R.id.phwPlanetSymbol, "☿")
                    setTextViewText(R.id.phwPlanetName, context.getString(R.string.widget_planetary_hour_fallback))
                    setTextViewText(R.id.phwWindow, "")
                }

                setTextViewText(
                    R.id.phwNext,
                    next?.let { context.getString(R.string.widget_planetary_hour_next, it.rulerName) }.orEmpty(),
                )
                setTextViewText(
                    R.id.phwHeader,
                    context.getString(R.string.widget_planetary_hour_header),
                )
                launchIntent?.let { setOnClickPendingIntent(R.id.phwRoot, it) }
            }

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }

        private fun buildLaunchPendingIntent(context: Context, requestCode: Int): PendingIntent? {
            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra(MorningBriefWidgetProvider.LaunchRouteExtra, MorningBriefWidgetProvider.ToolsRoute)
            }
            return PendingIntent.getActivity(
                context, requestCode + 400, intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
        }
    }
}
