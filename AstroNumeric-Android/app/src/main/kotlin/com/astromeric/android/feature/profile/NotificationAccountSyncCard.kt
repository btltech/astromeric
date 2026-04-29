package com.astromeric.android.feature.profile

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.astromeric.android.app.PushRegistrationManager
import com.astromeric.android.app.PushRegistrationResult
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.core.model.AlertFrequency
import com.astromeric.android.core.model.AppProfile
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

internal fun PushRegistrationResult.notificationMessage(defaultConfiguredMessage: String): String = when (this) {
    is PushRegistrationResult.Registered -> {
        if (linkedToAccount) {
            "${defaultConfiguredMessage.removeSuffix(".")} and linked this device to your signed-in account."
        } else {
            "${defaultConfiguredMessage.removeSuffix(".")} for this device."
        }
    }
    is PushRegistrationResult.Unregistered -> "Push delivery was detached from this device."
    PushRegistrationResult.NotConfigured -> "Firebase is not configured in this Android app yet. Add google-services.json to enable FCM push delivery."
    is PushRegistrationResult.Failed -> message
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
internal fun NotificationAccountSyncCard(
    scope: CoroutineScope,
    preferencesStore: AppPreferencesStore,
    remoteDataSource: AstroRemoteDataSource,
    profileRepository: ProfileRepository,
    pushRegistrationManager: PushRegistrationManager,
    selectedProfile: AppProfile?,
    personalModeEnabled: Boolean,
    authAccessToken: String,
    authUserEmail: String,
    authEmailDraft: String,
    onAuthEmailDraftChange: (String) -> Unit,
    authPasswordDraft: String,
    onAuthPasswordDraftChange: (String) -> Unit,
    authInFlight: Boolean,
    onAuthInFlightChange: (Boolean) -> Unit,
    firebaseConfigured: Boolean,
    mercuryRetrogradeAlertsEnabled: Boolean,
    alertFrequency: AlertFrequency,
    transitEmailDraft: String,
    onTransitEmailDraftChange: (String) -> Unit,
    accountSyncEnabled: Boolean,
    onShowMessage: (String) -> Unit,
    onSyncAlertPreferencesIfAuthenticated: suspend (Boolean, AlertFrequency) -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = "Account sync",
                style = MaterialTheme.typography.titleMedium,
            )
            if (personalModeEnabled) {
                Text(
                    text = "Personal mode is enabled for this build, matching the iOS local-first behavior. Notification preferences stay on-device, profile sync is dormant, and any stored account session is ignored until personal mode is turned off.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (authAccessToken.isNotBlank()) {
                    TextButton(
                        onClick = {
                            scope.launch {
                                preferencesStore.clearAuthSession()
                                onShowMessage("Stored account session cleared. Personal mode remains active.")
                            }
                        },
                    ) {
                        Text("Clear stored session")
                    }
                }
            } else if (authAccessToken.isBlank()) {
                Text(
                    text = "Sign in to sync Mercury retrograde preferences with your backend account. Transit email subscriptions can still use the current local-first profile payload even before you sign in.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                OutlinedTextField(
                    value = authEmailDraft,
                    onValueChange = onAuthEmailDraftChange,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Email") },
                    singleLine = true,
                )
                OutlinedTextField(
                    value = authPasswordDraft,
                    onValueChange = onAuthPasswordDraftChange,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Password") },
                    supportingText = {
                        Text("Backend accounts require at least 8 characters, one letter, and one number.")
                    },
                    singleLine = true,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedButton(
                        onClick = {
                            scope.launch {
                                if (authInFlight) return@launch
                                onAuthInFlightChange(true)
                                remoteDataSource.login(authEmailDraft, authPasswordDraft)
                                    .onSuccess { session ->
                                        preferencesStore.setAuthSession(session)
                                        profileRepository.syncProfilesToAccount()
                                            .onFailure { syncError ->
                                                onShowMessage(syncError.message ?: "Signed in, but profile sync failed.")
                                            }
                                        onShowMessage(
                                            pushRegistrationManager.syncCurrentToken().notificationMessage(
                                                defaultConfiguredMessage = "Signed in. Mercury retrograde preferences will now sync to your account",
                                            ),
                                        )
                                        onAuthPasswordDraftChange("")
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: "Sign-in failed.")
                                    }
                                onAuthInFlightChange(false)
                            }
                        },
                        enabled = !authInFlight && authEmailDraft.isNotBlank() && authPasswordDraft.isNotBlank(),
                    ) {
                        Text("Sign in")
                    }
                    TextButton(
                        onClick = {
                            scope.launch {
                                if (authInFlight) return@launch
                                onAuthInFlightChange(true)
                                remoteDataSource.register(authEmailDraft, authPasswordDraft)
                                    .onSuccess { session ->
                                        preferencesStore.setAuthSession(session)
                                        profileRepository.syncProfilesToAccount()
                                            .onFailure { syncError ->
                                                onShowMessage(syncError.message ?: "Account created, but profile sync failed.")
                                            }
                                        onShowMessage(
                                            pushRegistrationManager.syncCurrentToken().notificationMessage(
                                                defaultConfiguredMessage = "Account created. Android alert settings are now linked to your account",
                                            ),
                                        )
                                        onAuthPasswordDraftChange("")
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: "Account creation failed.")
                                    }
                                onAuthInFlightChange(false)
                            }
                        },
                        enabled = !authInFlight && authEmailDraft.isNotBlank() && authPasswordDraft.isNotBlank(),
                    ) {
                        Text("Create account")
                    }
                }
            } else {
                Text(
                    text = "Signed in as $authUserEmail. Mercury retrograde preference changes now sync with the backend, while transit email subscriptions still work for local-first profiles.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedButton(
                        onClick = {
                            scope.launch {
                                profileRepository.syncProfilesToAccount()
                                    .onSuccess { synced ->
                                        onShowMessage("Synced ${synced.size} profile(s) with your account.")
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: "Profile sync failed.")
                                    }
                            }
                        },
                    ) {
                        Text("Sync profiles")
                    }
                    OutlinedButton(
                        onClick = {
                            scope.launch {
                                remoteDataSource.fetchAlertPreferences(authAccessToken)
                                    .onSuccess { remotePrefs ->
                                        preferencesStore.setMercuryRetrogradeAlertsEnabled(remotePrefs.alertMercuryRetrograde)
                                        preferencesStore.setAlertFrequency(AlertFrequency.fromWireValue(remotePrefs.alertFrequency))
                                        onShowMessage("Backend alert settings refreshed.")
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: "Could not refresh backend alert settings.")
                                    }
                            }
                        },
                    ) {
                        Text("Refresh sync")
                    }
                    TextButton(
                        onClick = {
                            scope.launch {
                                onShowMessage(
                                    pushRegistrationManager.unregisterCurrentToken().notificationMessage(
                                        defaultConfiguredMessage = "Signed out",
                                    ),
                                )
                                preferencesStore.clearAuthSession()
                                onShowMessage("Signed out. Alert settings remain available locally.")
                            }
                        },
                    ) {
                        Text("Sign out")
                    }
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = "Push delivery",
                        style = MaterialTheme.typography.titleSmall,
                    )
                    Text(
                        text = if (firebaseConfigured) {
                            if (personalModeEnabled) {
                                "FCM is available on this build. Sync the device token to register this installation only; personal mode keeps it detached from any account session."
                            } else if (authAccessToken.isBlank()) {
                                "FCM is available on this build. Sync the device token now to register this installation, or sign in first to link it to your account."
                            } else {
                                "FCM is available on this build. Sync the device token to link this installation to $authUserEmail for backend push delivery."
                            }
                        } else {
                            "This Android repo still has no Firebase app config file. Token acquisition is wired, but FCM delivery will stay inactive until google-services.json is added."
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        OutlinedButton(
                            onClick = {
                                scope.launch {
                                    onShowMessage(
                                        pushRegistrationManager.syncCurrentToken().notificationMessage(
                                            defaultConfiguredMessage = "Push token synced",
                                        ),
                                    )
                                }
                            },
                        ) {
                            Text("Sync device token")
                        }
                        if (firebaseConfigured) {
                            TextButton(
                                onClick = {
                                    scope.launch {
                                        onShowMessage(
                                            pushRegistrationManager.unregisterCurrentToken().notificationMessage(
                                                defaultConfiguredMessage = "Push token removed",
                                            ),
                                        )
                                    }
                                },
                            ) {
                                Text("Remove token")
                            }
                        }
                    }
                }
            }

            NotificationToggleCard(
                title = "Mercury retrograde alerts",
                description = if (personalModeEnabled) {
                    "Stored locally. Personal mode keeps the backend account copy dormant in this build."
                } else if (authAccessToken.isBlank()) {
                    "Stored locally now. Sign in above if you want the backend copy to stay in sync too."
                } else {
                    "Stored locally and synced to your backend account."
                },
                checked = mercuryRetrogradeAlertsEnabled,
                onCheckedChange = { enabled ->
                    scope.launch {
                        preferencesStore.setMercuryRetrogradeAlertsEnabled(enabled)
                        onSyncAlertPreferencesIfAuthenticated(enabled, alertFrequency)
                    }
                },
            )

            Text(
                text = "Alert frequency",
                style = MaterialTheme.typography.titleSmall,
            )
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                AlertFrequency.entries.forEach { frequency ->
                    FilterChip(
                        selected = alertFrequency == frequency,
                        onClick = {
                            scope.launch {
                                preferencesStore.setAlertFrequency(frequency)
                                onSyncAlertPreferencesIfAuthenticated(mercuryRetrogradeAlertsEnabled, frequency)
                            }
                        },
                        label = { Text(frequency.label) },
                    )
                }
            }

            OutlinedTextField(
                value = transitEmailDraft,
                onValueChange = onTransitEmailDraftChange,
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Transit alert email") },
                supportingText = {
                    Text(
                        if (selectedProfile == null) {
                            "Choose a profile first. The address is still saved locally."
                        } else if (personalModeEnabled) {
                            "Personal mode stays local-first. Android will send the inline profile payload when syncing this email to the backend."
                        } else if (authAccessToken.isBlank()) {
                            "The backend can now subscribe this local-first profile payload directly, even before Android sign-in."
                        } else {
                            "This will subscribe the current profile against the backend using your signed-in session when available."
                        },
                    )
                },
            )
            TextButton(
                onClick = {
                    scope.launch {
                        preferencesStore.setTransitSubscriptionEmail(transitEmailDraft)
                        val profile = selectedProfile
                        if (profile == null || transitEmailDraft.isBlank()) {
                            onShowMessage("Transit subscription email saved locally.")
                            return@launch
                        }

                        remoteDataSource.subscribeTransitAlerts(
                            authToken = authAccessToken.takeIf { accountSyncEnabled },
                            profile = profile,
                            email = transitEmailDraft,
                        ).onSuccess {
                            onShowMessage("Transit subscription synced with the backend for ${profile.name}.")
                        }.onFailure { error ->
                            onShowMessage(error.message ?: "Transit email was saved locally, but backend subscription failed.")
                        }
                    }
                },
            ) {
                Text("Save email")
            }
        }
    }
}
