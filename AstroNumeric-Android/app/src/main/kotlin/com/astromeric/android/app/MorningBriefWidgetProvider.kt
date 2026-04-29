package com.astromeric.android.app

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import com.astromeric.android.R

class MorningBriefWidgetProvider : AppWidgetProvider() {
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
        appWidgetIds.forEach { appWidgetId ->
            updateWidget(context, appWidgetManager, appWidgetId)
        }
    }

    companion object {
        const val LaunchRouteExtra: String = "launch_route"
        const val HomeRoute: String = "home"
        const val ToolsRoute: String = "tools"

        fun refreshAllWidgets(context: Context) {
            val manager = AppWidgetManager.getInstance(context)
            val componentName = ComponentName(context, MorningBriefWidgetProvider::class.java)
            val widgetIds = manager.getAppWidgetIds(componentName)
            widgetIds.forEach { appWidgetId ->
                updateWidget(context, manager, appWidgetId)
            }
        }

        private fun updateWidget(
            context: Context,
            appWidgetManager: AppWidgetManager,
            appWidgetId: Int,
        ) {
            val snapshot = MorningBriefWidgetSnapshotStore(context).read()
            val rootIntent = buildLaunchPendingIntent(context, HomeRoute, 0)
            val toolsIntent = buildLaunchPendingIntent(context, ToolsRoute, 1)

            val views = RemoteViews(context.packageName, R.layout.morning_brief_widget).apply {
                setTextViewText(R.id.widgetHeader, context.getString(R.string.widget_morning_brief_header))
                setTextViewText(R.id.widgetMoonEmoji, snapshot.moonEmoji)
                setTextViewText(R.id.widgetMoonPhase, snapshot.moonPhase.ifBlank { "Moon" })
                setTextViewText(
                    R.id.widgetPersonalDay,
                    snapshot.personalDay?.let { "Day $it" } ?: context.getString(R.string.widget_personal_day_fallback),
                )
                setTextViewText(R.id.widgetLineOne, snapshot.greeting.ifBlank { snapshot.bullets.getOrNull(0).orEmpty() })
                setTextViewText(R.id.widgetLineZero, snapshot.vibe.ifBlank { snapshot.moonGuidance })
                setTextViewText(R.id.widgetLineTwo, snapshot.bullets.getOrNull(1) ?: snapshot.bullets.getOrNull(0).orEmpty())
                setTextViewText(
                    R.id.widgetUpdatedAt,
                    snapshot.lastUpdatedEpochMillis?.let { updatedAt ->
                        context.getString(
                            R.string.widget_updated_at,
                            android.text.format.DateFormat.getTimeFormat(context).format(updatedAt),
                        )
                    } ?: context.getString(R.string.widget_update_pending),
                )
                setTextViewText(R.id.widgetOpenBrief, context.getString(R.string.widget_open_brief))
                setTextViewText(R.id.widgetOpenTools, context.getString(R.string.widget_open_tools))
                rootIntent?.let {
                    setOnClickPendingIntent(R.id.widgetRoot, it)
                    setOnClickPendingIntent(R.id.widgetOpenBrief, it)
                }
                toolsIntent?.let { setOnClickPendingIntent(R.id.widgetOpenTools, it) }
            }

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }

        private fun buildLaunchPendingIntent(
            context: Context,
            route: String,
            requestCode: Int,
        ): PendingIntent? {
            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra(LaunchRouteExtra, route)
            }
            return PendingIntent.getActivity(
                context,
                requestCode,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
        }
    }
}