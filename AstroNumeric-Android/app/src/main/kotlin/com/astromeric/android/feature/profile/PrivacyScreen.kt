package com.astromeric.android.feature.profile

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.R
import com.astromeric.android.core.data.local.NatalChartCacheStore
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PermissionRationaleDialog
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumHeroCard
import com.astromeric.android.core.ui.shouldShowPermissionRationale
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

private data class PendingProfileExport(
    val fileName: String,
    val content: String,
)

private data class PrivacySection(
    val title: String,
    val bullets: List<String>,
)

@Composable
fun PrivacyScreen(
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    preferencesStore: AppPreferencesStore,
    profileRepository: ProfileRepository,
    onShowMessage: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val hideSensitiveDetailsEnabled by preferencesStore.hideSensitiveDetailsEnabled.collectAsStateWithLifecycle(initialValue = false)
    val calendarContextEnabled by preferencesStore.guideCalendarContextEnabled.collectAsStateWithLifecycle(initialValue = false)
    val biometricContextEnabled by preferencesStore.guideBiometricContextEnabled.collectAsStateWithLifecycle(initialValue = false)
    val chartCacheStore = remember(context) { NatalChartCacheStore(context.applicationContext) }
    var pendingExport by remember { mutableStateOf<PendingProfileExport?>(null) }
    var showCalendarRationale by remember { mutableStateOf(false) }

    val calendarPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        scope.launch {
            preferencesStore.setGuideCalendarContextEnabled(granted)
        }
        if (!granted) {
            onShowMessage(context.getString(R.string.privacy_calendar_permission_denied))
        }
    }

    fun requestCalendarPermission() {
        if (shouldShowPermissionRationale(context, Manifest.permission.READ_CALENDAR)) {
            showCalendarRationale = true
        } else {
            calendarPermissionLauncher.launch(Manifest.permission.READ_CALENDAR)
        }
    }

    if (showCalendarRationale) {
        PermissionRationaleDialog(
            title = stringResource(R.string.privacy_calendar_permission_title),
            message = stringResource(R.string.privacy_calendar_permission_message),
            onConfirm = {
                showCalendarRationale = false
                calendarPermissionLauncher.launch(Manifest.permission.READ_CALENDAR)
            },
            onDismiss = {
                showCalendarRationale = false
            },
        )
    }

    val exportLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        val export = pendingExport
        pendingExport = null
        if (uri == null || export == null) {
            return@rememberLauncherForActivityResult
        }

        scope.launch {
            val result = withContext(Dispatchers.IO) {
                runCatching {
                    context.contentResolver.openOutputStream(uri)?.use { output ->
                        output.write(export.content.toByteArray(Charsets.UTF_8))
                    } ?: error("Could not open the export target.")
                }
            }
            onShowMessage(
                if (result.isSuccess) {
                    "Profile backup exported." 
                } else {
                    result.exceptionOrNull()?.message ?: "Profile export failed."
                },
            )
        }
    }

    val importLauncher = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri == null) {
            return@rememberLauncherForActivityResult
        }

        scope.launch {
            val importResult = withContext(Dispatchers.IO) {
                runCatching {
                    context.contentResolver.openInputStream(uri)?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }
                        ?: error("Could not read the selected file.")
                }.fold(
                    onSuccess = { raw -> decodeProfileDraftFromJson(context, raw) },
                    onFailure = { Result.failure(it) },
                )
            }

            importResult.onSuccess { draft ->
                profileRepository.saveProfile(draft)
                onShowMessage(context.getString(R.string.privacy_screen_import_success))
            }.onFailure { error ->
                onShowMessage(error.message ?: context.getString(R.string.privacy_screen_import_failed))
            }
        }
    }

    val privacySections = remember(context) {
        listOf(
            PrivacySection(
                title = context.getString(R.string.privacy_screen_section_on_device_title),
                bullets = listOf(
                    context.getString(R.string.privacy_screen_section_on_device_bullet_1),
                    context.getString(R.string.privacy_screen_section_on_device_bullet_2),
                ),
            ),
            PrivacySection(
                title = context.getString(R.string.privacy_screen_section_backend_title),
                bullets = listOf(
                    context.getString(R.string.privacy_screen_section_backend_bullet_1),
                    context.getString(R.string.privacy_screen_section_backend_bullet_2),
                ),
            ),
            PrivacySection(
                title = context.getString(R.string.privacy_screen_section_backups_title),
                bullets = listOf(
                    context.getString(R.string.privacy_screen_section_backups_bullet_1),
                    context.getString(R.string.privacy_screen_section_backups_bullet_2),
                ),
            ),
            PrivacySection(
                title = context.getString(R.string.privacy_screen_section_deletion_title),
                bullets = listOf(
                    context.getString(R.string.privacy_screen_section_deletion_bullet_1),
                    context.getString(R.string.privacy_screen_section_deletion_bullet_2),
                ),
            ),
        )
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = stringResource(R.string.privacy_screen_hero_eyebrow),
            title = stringResource(R.string.privacy_screen_hero_title),
            body = stringResource(R.string.privacy_screen_hero_body),
            chips = listOf(
                stringResource(R.string.privacy_screen_chip_local_first),
                stringResource(R.string.privacy_screen_chip_permissions),
                stringResource(R.string.privacy_screen_chip_control),
                stringResource(R.string.privacy_screen_chip_profile_count, profiles.size),
            ),
        )

        PremiumContentCard(
            title = stringResource(R.string.privacy_screen_hide_sensitive_details_title),
            body = privacyModeSummary(context, hideSensitiveDetailsEnabled),
        ) {
                Switch(
                    checked = hideSensitiveDetailsEnabled,
                    onCheckedChange = { enabled ->
                        scope.launch {
                            preferencesStore.setHideSensitiveDetailsEnabled(enabled)
                            if (enabled && !hideSensitiveDetailsEnabled) {
                                preferencesStore.scrubStoredSensitiveDetails()
                                chartCacheStore.clearAll()
                            }
                        }
                    },
                )
        }

        PremiumContentCard(title = stringResource(R.string.privacy_context_integrations_title)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        Text(
                            text = stringResource(R.string.privacy_calendar_guidance_title),
                            style = MaterialTheme.typography.bodyLarge,
                        )
                        Text(
                            text = stringResource(R.string.privacy_calendar_guidance_detail),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    Button(
                        onClick = {
                            val granted = ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALENDAR) == PackageManager.PERMISSION_GRANTED
                            if (calendarContextEnabled) {
                                scope.launch {
                                    preferencesStore.setGuideCalendarContextEnabled(false)
                                }
                            } else if (granted) {
                                scope.launch {
                                    preferencesStore.setGuideCalendarContextEnabled(true)
                                }
                            } else {
                                requestCalendarPermission()
                            }
                        },
                    ) {
                        Text(stringResource(if (calendarContextEnabled) R.string.preference_state_on else R.string.preference_state_off))
                    }
                }
                if (calendarContextEnabled) {
                    Text(
                        text = stringResource(R.string.privacy_calendar_enabled_message),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary,
                    )
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        Text(
                            text = stringResource(R.string.privacy_biometric_guidance_title),
                            style = MaterialTheme.typography.bodyLarge,
                        )
                        Text(
                            text = stringResource(R.string.privacy_biometric_guidance_detail),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    Button(
                        onClick = {
                            scope.launch {
                                preferencesStore.setGuideBiometricContextEnabled(!biometricContextEnabled)
                            }
                        },
                    ) {
                        Text(stringResource(if (biometricContextEnabled) R.string.preference_state_on else R.string.preference_state_off))
                    }
                }
                if (biometricContextEnabled) {
                    Text(
                        text = stringResource(R.string.privacy_biometric_enabled_message),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary,
                    )
                }
        }

        PremiumContentCard(
            title = stringResource(R.string.privacy_screen_export_import_share_title),
            body = selectedProfile?.let {
                stringResource(
                    R.string.privacy_screen_selected_profile,
                    it.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                )
            } ?: stringResource(R.string.privacy_screen_select_profile_before_export),
            footer = stringResource(R.string.privacy_screen_export_import_share_footer),
        ) {
                Button(
                    enabled = selectedProfile != null,
                    onClick = {
                        val profile = selectedProfile ?: return@Button
                        val export = PendingProfileExport(
                            fileName = profile.exportFileName(hideSensitiveDetailsEnabled),
                            content = profile.toProfileExportJson(),
                        )
                        pendingExport = export
                        exportLauncher.launch(export.fileName)
                    },
                ) {
                    Text(stringResource(R.string.privacy_screen_export_selected_profile))
                }
                OutlinedButton(
                    enabled = selectedProfile != null,
                    onClick = {
                        val profile = selectedProfile ?: return@OutlinedButton
                        val shareIntent = Intent(Intent.ACTION_SEND).apply {
                            type = "text/plain"
                            putExtra(Intent.EXTRA_SUBJECT, context.getString(R.string.privacy_screen_share_profile_subject))
                            putExtra(Intent.EXTRA_TEXT, profile.toShareSummaryText(context, hideSensitiveDetailsEnabled))
                        }
                        context.startActivity(
                            Intent.createChooser(
                                shareIntent,
                                context.getString(R.string.privacy_screen_share_profile_chooser_title),
                            ),
                        )
                    },
                ) {
                    Text(stringResource(R.string.privacy_screen_share_text_summary))
                }
                OutlinedButton(
                    onClick = {
                        importLauncher.launch(arrayOf("application/json", "text/plain"))
                    },
                ) {
                    Text(stringResource(R.string.privacy_screen_import_profile_backup))
                }
        }

        privacySections.forEach { section ->
            PremiumContentCard(title = section.title) {
                    section.bullets.forEach { bullet ->
                        Text(
                            text = "• $bullet",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
            }
        }

        PremiumContentCard(
            title = stringResource(R.string.privacy_screen_questions_title),
            body = stringResource(R.string.privacy_screen_questions_body),
        ) {
                OutlinedButton(
                    onClick = {
                        val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
                            data = Uri.parse("mailto:privacy@astromeric.app")
                            putExtra(Intent.EXTRA_SUBJECT, context.getString(R.string.privacy_screen_privacy_question_subject))
                            putExtra(Intent.EXTRA_TEXT, privacySupportEmailBody(context))
                        }
                        context.startActivity(emailIntent)
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.privacy_screen_privacy_email))
                }
        }
    }
}