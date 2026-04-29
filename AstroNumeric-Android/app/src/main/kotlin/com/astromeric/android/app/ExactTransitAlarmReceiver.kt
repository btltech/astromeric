package com.astromeric.android.app

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.astromeric.android.core.model.AstroDataSource

class ExactTransitAlarmReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != ExactTransitAlarmScheduler.ACTION_EXACT_TRANSIT_ALARM) return

        AstroNotificationService(context).showExactTransitNotification(
            profileName = intent.getStringExtra(ExactTransitAlarmScheduler.EXTRA_PROFILE_NAME).orEmpty(),
            transitPlanet = intent.getStringExtra(ExactTransitAlarmScheduler.EXTRA_TRANSIT_PLANET).orEmpty(),
            natalPoint = intent.getStringExtra(ExactTransitAlarmScheduler.EXTRA_NATAL_POINT).orEmpty(),
            aspect = intent.getStringExtra(ExactTransitAlarmScheduler.EXTRA_ASPECT).orEmpty(),
            interpretation = intent.getStringExtra(ExactTransitAlarmScheduler.EXTRA_INTERPRETATION),
            source = AstroDataSource.fromStorage(intent.getStringExtra(ExactTransitAlarmScheduler.EXTRA_SOURCE)),
            isCached = intent.getBooleanExtra(ExactTransitAlarmScheduler.EXTRA_SOURCE_IS_CACHED, false),
            notificationId = intent.getIntExtra(ExactTransitAlarmScheduler.EXTRA_NOTIFICATION_ID, 1007),
        )
    }
}