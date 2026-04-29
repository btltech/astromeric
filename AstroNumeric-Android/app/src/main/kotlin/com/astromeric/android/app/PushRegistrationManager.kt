package com.astromeric.android.app

import android.content.Context
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.google.firebase.FirebaseApp
import com.google.firebase.messaging.FirebaseMessaging
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.tasks.await

sealed interface PushRegistrationResult {
    data class Registered(val token: String, val linkedToAccount: Boolean) : PushRegistrationResult
    data class Unregistered(val token: String) : PushRegistrationResult
    data object NotConfigured : PushRegistrationResult
    data class Failed(val message: String) : PushRegistrationResult
}

class PushRegistrationManager(
    private val context: Context,
    private val preferencesStore: AppPreferencesStore,
    private val remoteDataSource: AstroRemoteDataSource,
) {
    fun isFirebaseConfigured(): Boolean {
        if (FirebaseApp.getApps(context).isNotEmpty()) {
            return true
        }
        return runCatching { FirebaseApp.initializeApp(context) != null }.getOrDefault(false)
    }

    suspend fun syncCurrentToken(): PushRegistrationResult {
        if (!isFirebaseConfigured()) {
            return PushRegistrationResult.NotConfigured
        }

        val token = runCatching { FirebaseMessaging.getInstance().token.await() }
            .getOrElse { error ->
                return PushRegistrationResult.Failed(error.message ?: "FCM token could not be requested.")
            }

        return registerToken(token)
    }

    suspend fun registerToken(token: String): PushRegistrationResult {
        val authToken = preferencesStore.activeAuthAccessToken()
        return remoteDataSource.registerDeviceToken(authToken = authToken, token = token)
            .fold(
                onSuccess = {
                    PushRegistrationResult.Registered(
                        token = token,
                        linkedToAccount = !authToken.isNullOrBlank(),
                    )
                },
                onFailure = { error ->
                    PushRegistrationResult.Failed(error.message ?: "Device token could not be registered.")
                },
            )
    }

    suspend fun unregisterCurrentToken(): PushRegistrationResult {
        if (!isFirebaseConfigured()) {
            return PushRegistrationResult.NotConfigured
        }

        val token = runCatching { FirebaseMessaging.getInstance().token.await() }
            .getOrElse { error ->
                return PushRegistrationResult.Failed(error.message ?: "FCM token could not be requested.")
            }

        val authToken = preferencesStore.activeAuthAccessToken()
        return remoteDataSource.unregisterDeviceToken(authToken = authToken, token = token)
            .fold(
                onSuccess = { PushRegistrationResult.Unregistered(token) },
                onFailure = { error ->
                    PushRegistrationResult.Failed(error.message ?: "Device token could not be unregistered.")
                },
            )
    }
}