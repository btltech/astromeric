package com.astromeric.android.app

import com.google.firebase.messaging.FirebaseMessagingService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

class AstroFirebaseMessagingService : FirebaseMessagingService() {
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onNewToken(token: String) {
        val application = applicationContext as? AstroNumericApplication ?: return
        serviceScope.launch {
            application.appContainer.pushRegistrationManager.registerToken(token)
        }
    }
}