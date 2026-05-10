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
 * Widget that shows today's moon phase, emoji, and a short guidance line.
 * Reads data from [MorningBriefWidgetSnapshotStore] (already populated by [AstroRefreshWorker]).
 */
class MoonPhaseWidgetProvider : AppWidgetProvider() {
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
            val ids = manager.getAppWidgetIds(ComponentName(context, MoonPhaseWidgetProvider::class.java))
            ids.forEach { updateWidget(context, manager, it) }
        }

        private fun updateWidget(
            context: Context,
            appWidgetManager: AppWidgetManager,
            appWidgetId: Int,
        ) {
            val snapshot = MorningBriefWidgetSnapshotStore(context).read()
            val launchIntent = buildLaunchPendingIntent(context, appWidgetId)

            val views = RemoteViews(context.packageName, R.layout.moon_phase_widget).apply {
                setTextViewText(R.id.mpwEmoji, snapshot.moonEmoji)
                setTextViewText(R.id.mpwPhaseName, snapshot.moonPhase.ifBlank { context.getString(R.string.widget_moon_phase_fallback) })
                setTextViewText(R.id.mpwGuidance, snapshot.moonGuidance.ifBlank { snapshot.bullets.getOrNull(0).orEmpty() })
                setTextViewText(
                    R.id.mpwPersonalDay,
                    snapshot.personalDay?.let { context.getString(R.string.widget_personal_day_number, it) }
                        ?: context.getString(R.string.widget_personal_day_fallback),
                )
                setTextViewText(
                    R.id.mpwUpdatedAt,
                    snapshot.lastUpdatedEpochMillis?.let { t ->
                        context.getString(
                            R.string.widget_updated_at,
                            android.text.format.DateFormat.getTimeFormat(context).format(t),
                        )
                    } ?: context.getString(R.string.widget_update_pending),
                )
                launchIntent?.let { setOnClickPendingIntent(R.id.mpwRoot, it) }
            }

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }

        private fun buildLaunchPendingIntent(context: Context, requestCode: Int): PendingIntent? {
            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra(MorningBriefWidgetProvider.LaunchRouteExtra, MorningBriefWidgetProvider.HomeRoute)
            }
            return PendingIntent.getActivity(
                context, requestCode, intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
        }
    }
}
