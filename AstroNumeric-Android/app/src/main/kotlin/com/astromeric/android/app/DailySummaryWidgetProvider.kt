package com.astromeric.android.app

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import com.astromeric.android.R

/**
 * Widget showing the daily summary: personal day number, vibe, and first two cosmic bullet points.
 * Reads data from [MorningBriefWidgetSnapshotStore] (already populated by [AstroRefreshWorker]).
 */
class DailySummaryWidgetProvider : AppWidgetProvider() {
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
            val ids = manager.getAppWidgetIds(ComponentName(context, DailySummaryWidgetProvider::class.java))
            ids.forEach { updateWidget(context, manager, it) }
        }

        private fun updateWidget(
            context: Context,
            appWidgetManager: AppWidgetManager,
            appWidgetId: Int,
        ) {
            val snapshot = MorningBriefWidgetSnapshotStore(context).read()
            val launchIntent = buildLaunchPendingIntent(context, appWidgetId)

            val views = RemoteViews(context.packageName, R.layout.daily_summary_widget).apply {
                setTextViewText(R.id.dswHeader, context.getString(R.string.widget_daily_summary_header))
                setTextViewText(
                    R.id.dswPersonalDay,
                    snapshot.personalDay?.let { context.getString(R.string.widget_personal_day_number, it) }
                        ?: context.getString(R.string.widget_personal_day_fallback),
                )
                setTextViewText(
                    R.id.dswMoonBadge,
                    "${snapshot.moonEmoji} ${snapshot.moonPhase}".trim(),
                )
                setTextViewText(R.id.dswVibe, snapshot.vibe.ifBlank { snapshot.greeting })
                setTextViewText(R.id.dswBulletOne, snapshot.bullets.getOrNull(0).orEmpty())
                setTextViewText(R.id.dswBulletTwo, snapshot.bullets.getOrNull(1).orEmpty())
                setTextViewText(
                    R.id.dswUpdatedAt,
                    snapshot.lastUpdatedEpochMillis?.let { t ->
                        context.getString(
                            R.string.widget_updated_at,
                            android.text.format.DateFormat.getTimeFormat(context).format(t),
                        )
                    } ?: context.getString(R.string.widget_update_pending),
                )
                launchIntent?.let { setOnClickPendingIntent(R.id.dswRoot, it) }
            }

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }

        private fun buildLaunchPendingIntent(context: Context, requestCode: Int): PendingIntent? {
            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra(MorningBriefWidgetProvider.LaunchRouteExtra, MorningBriefWidgetProvider.HomeRoute)
            }
            return PendingIntent.getActivity(
                context, requestCode + 200, intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
        }
    }
}
