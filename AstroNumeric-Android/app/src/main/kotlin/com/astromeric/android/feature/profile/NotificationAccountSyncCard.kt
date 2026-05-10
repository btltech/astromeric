package com.astromeric.android.feature.profile

import android.content.Context
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.app.PushRegistrationManager
import com.astromeric.android.app.PushRegistrationResult
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.core.model.AlertFrequency
import com.astromeric.android.core.model.AppProfile
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

internal fun PushRegistrationResult.notificationMessage(
    context: Context,
    defaultConfiguredMessage: String,
): String = when (this) {
    is PushRegistrationResult.Registered -> {
        if (linkedToAccount) {
            context.getString(
                R.string.notification_account_sync_push_linked_account,
                defaultConfiguredMessage.removeSuffix("."),
            )
        } else {
            context.getString(
                R.string.notification_account_sync_push_for_device,
                defaultConfiguredMessage.removeSuffix("."),
            )
        }
    }
    is PushRegistrationResult.Unregistered -> context.getString(R.string.notification_account_sync_push_detached)
    PushRegistrationResult.NotConfigured -> context.getString(R.string.notification_account_sync_push_not_configured)
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
    val context = LocalContext.current
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = stringResource(R.string.notification_account_sync_title),
                style = MaterialTheme.typography.titleMedium,
            )
            if (personalModeEnabled) {
                Text(
                    text = stringResource(R.string.notification_account_sync_personal_mode_body),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (authAccessToken.isNotBlank()) {
                    TextButton(
                        onClick = {
                            scope.launch {
                                preferencesStore.clearAuthSession()
                                onShowMessage(context.getString(R.string.notification_account_sync_clear_stored_session_message))
                            }
                        },
                    ) {
                        Text(stringResource(R.string.notification_account_sync_clear_stored_session))
                    }
                }
            } else if (authAccessToken.isBlank()) {
                Text(
                    text = stringResource(R.string.notification_account_sync_sign_in_body),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                OutlinedTextField(
                    value = authEmailDraft,
                    onValueChange = onAuthEmailDraftChange,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text(stringResource(R.string.notification_account_sync_email_label)) },
                    singleLine = true,
                )
                OutlinedTextField(
                    value = authPasswordDraft,
                    onValueChange = onAuthPasswordDraftChange,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text(stringResource(R.string.notification_account_sync_password_label)) },
                    supportingText = {
                        Text(stringResource(R.string.notification_account_sync_password_supporting))
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
                                                onShowMessage(syncError.message ?: context.getString(R.string.notification_account_sync_sign_in_profile_sync_failed))
                                            }
                                        onShowMessage(
                                            pushRegistrationManager.syncCurrentToken().notificationMessage(
                                                context = context,
                                                defaultConfiguredMessage = context.getString(R.string.notification_account_sync_signed_in_default),
                                            ),
                                        )
                                        onAuthPasswordDraftChange("")
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: context.getString(R.string.notification_account_sync_sign_in_failed))
                                    }
                                onAuthInFlightChange(false)
                            }
                        },
                        enabled = !authInFlight && authEmailDraft.isNotBlank() && authPasswordDraft.isNotBlank(),
                    ) {
                        Text(stringResource(R.string.notification_account_sync_sign_in_button))
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
                                                onShowMessage(syncError.message ?: context.getString(R.string.notification_account_sync_account_created_profile_sync_failed))
                                            }
                                        onShowMessage(
                                            pushRegistrationManager.syncCurrentToken().notificationMessage(
                                                context = context,
                                                defaultConfiguredMessage = context.getString(R.string.notification_account_sync_account_created_default),
                                            ),
                                        )
                                        onAuthPasswordDraftChange("")
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: context.getString(R.string.notification_account_sync_account_creation_failed))
                                    }
                                onAuthInFlightChange(false)
                            }
                        },
                        enabled = !authInFlight && authEmailDraft.isNotBlank() && authPasswordDraft.isNotBlank(),
                    ) {
                        Text(stringResource(R.string.notification_account_sync_create_account_button))
                    }
                }
            } else {
                Text(
                    text = stringResource(R.string.notification_account_sync_signed_in_as, authUserEmail),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedButton(
                        onClick = {
                            scope.launch {
                                profileRepository.syncProfilesToAccount()
                                    .onSuccess { synced ->
                                        onShowMessage(context.getString(R.string.notification_account_sync_profiles_synced, synced.size))
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: context.getString(R.string.notification_account_sync_profile_sync_failed))
                                    }
                            }
                        },
                    ) {
                        Text(stringResource(R.string.notification_account_sync_sync_profiles))
                    }
                    OutlinedButton(
                        onClick = {
                            scope.launch {
                                remoteDataSource.fetchAlertPreferences(authAccessToken)
                                    .onSuccess { remotePrefs ->
                                        preferencesStore.setMercuryRetrogradeAlertsEnabled(remotePrefs.alertMercuryRetrograde)
                                        preferencesStore.setAlertFrequency(AlertFrequency.fromWireValue(remotePrefs.alertFrequency))
                                        onShowMessage(context.getString(R.string.notification_account_sync_backend_refreshed))
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: context.getString(R.string.notification_account_sync_backend_refresh_failed))
                                    }
                            }
                        },
                    ) {
                        Text(stringResource(R.string.notification_account_sync_refresh_sync))
                    }
                    TextButton(
                        onClick = {
                            scope.launch {
                                onShowMessage(
                                    pushRegistrationManager.unregisterCurrentToken().notificationMessage(
                                        context = context,
                                        defaultConfiguredMessage = context.getString(R.string.notification_account_sync_signed_out_default),
                                    ),
                                )
                                preferencesStore.clearAuthSession()
                                onShowMessage(context.getString(R.string.notification_account_sync_signed_out_local_message))
                            }
                        },
                    ) {
                        Text(stringResource(R.string.notification_account_sync_sign_out))
                    }
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = stringResource(R.string.notification_account_sync_push_delivery_title),
                        style = MaterialTheme.typography.titleSmall,
                    )
                    Text(
                        text = if (firebaseConfigured) {
                            if (personalModeEnabled) {
                                stringResource(R.string.notification_account_sync_push_available_personal)
                            } else if (authAccessToken.isBlank()) {
                                stringResource(R.string.notification_account_sync_push_available_signed_out)
                            } else {
                                stringResource(R.string.notification_account_sync_push_available_signed_in, authUserEmail)
                            }
                        } else {
                            stringResource(R.string.notification_account_sync_push_missing_config)
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
                                            context = context,
                                            defaultConfiguredMessage = context.getString(R.string.notification_account_sync_push_token_synced_default),
                                        ),
                                    )
                                }
                            },
                        ) {
                            Text(stringResource(R.string.notification_account_sync_sync_device_token))
                        }
                        if (firebaseConfigured) {
                            TextButton(
                                onClick = {
                                    scope.launch {
                                        onShowMessage(
                                            pushRegistrationManager.unregisterCurrentToken().notificationMessage(
                                                context = context,
                                                defaultConfiguredMessage = context.getString(R.string.notification_account_sync_push_token_removed_default),
                                            ),
                                        )
                                    }
                                },
                            ) {
                                Text(stringResource(R.string.notification_account_sync_remove_token))
                            }
                        }
                    }
                }
            }

            NotificationToggleCard(
                title = stringResource(R.string.notification_account_sync_mercury_title),
                description = if (personalModeEnabled) {
                    stringResource(R.string.notification_account_sync_mercury_description_personal)
                } else if (authAccessToken.isBlank()) {
                    stringResource(R.string.notification_account_sync_mercury_description_signed_out)
                } else {
                    stringResource(R.string.notification_account_sync_mercury_description_signed_in)
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
                text = stringResource(R.string.notification_account_sync_alert_frequency_title),
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
                label = { Text(stringResource(R.string.notification_account_sync_transit_email_label)) },
                supportingText = {
                    Text(
                        if (selectedProfile == null) {
                            stringResource(R.string.notification_account_sync_transit_email_support_none)
                        } else if (personalModeEnabled) {
                            stringResource(R.string.notification_account_sync_transit_email_support_personal)
                        } else if (authAccessToken.isBlank()) {
                            stringResource(R.string.notification_account_sync_transit_email_support_signed_out)
                        } else {
                            stringResource(R.string.notification_account_sync_transit_email_support_signed_in)
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
                            onShowMessage(context.getString(R.string.notification_account_sync_transit_email_saved_local))
                            return@launch
                        }

                        remoteDataSource.subscribeTransitAlerts(
                            authToken = authAccessToken.takeIf { accountSyncEnabled },
                            profile = profile,
                            email = transitEmailDraft,
                        ).onSuccess {
                            onShowMessage(
                                context.getString(
                                    R.string.notification_account_sync_transit_email_synced_backend,
                                    profile.name,
                                ),
                            )
                        }.onFailure { error ->
                            onShowMessage(error.message ?: context.getString(R.string.notification_account_sync_transit_email_sync_failed))
                        }
                    }
                },
            ) {
                Text(stringResource(R.string.notification_account_sync_save_email))
            }
        }
    }
}
