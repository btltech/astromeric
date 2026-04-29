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
                    onSuccess = { raw -> decodeProfileDraftFromJson(raw) },
                    onFailure = { Result.failure(it) },
                )
            }

            importResult.onSuccess { draft ->
                profileRepository.saveProfile(draft)
                onShowMessage("Profile imported into the local Android store.")
            }.onFailure { error ->
                onShowMessage(error.message ?: "Profile import failed.")
            }
        }
    }

    val privacySections = remember {
        listOf(
            PrivacySection(
                title = "What stays on device",
                bullets = listOf(
                    "Profiles, preferences, local relationship history, habits, and journal entries are primarily stored on-device in this Android build.",
                    "Privacy mode changes how details are shown in the UI, not whether the app can still calculate charts from your saved birth data.",
                ),
            ),
            PrivacySection(
                title = "What can go to the backend",
                bullets = listOf(
                    "Server-backed readings, compatibility, synced friends, and other remote features still send the profile details needed to compute results.",
                    "Privacy mode is not a network kill switch. It is a presentation boundary and a sharing boundary.",
                ),
            ),
            PrivacySection(
                title = "Backups and sharing",
                bullets = listOf(
                    "Backup exports stay full-fidelity so a profile can be restored later, even while privacy mode is on.",
                    "Plain-text sharing can be redacted when privacy mode is enabled.",
                ),
            ),
            PrivacySection(
                title = "Deletion and control",
                bullets = listOf(
                    "Deleting a profile removes it from the local Android store.",
                    "Questions about backend-held data such as synced friend records or notification tokens should go to privacy@astromeric.app.",
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
            eyebrow = "Privacy",
            title = "Make the data boundary legible.",
            body = "This screen explains what stays local, what still reaches the backend, and how redaction changes the visible UI.",
            chips = listOf("Local-first", "Permissions", "Control", "${profiles.size} local profile(s)"),
        )

        PremiumContentCard(
            title = "Hide Sensitive Details",
            body = privacyModeSummary(hideSensitiveDetailsEnabled),
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
            title = "Export, import, and share",
            body = selectedProfile?.let {
                "Selected profile: ${it.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)}"
            } ?: "Select a profile before exporting or sharing.",
            footer = "Backup exports always retain full profile details so they can be restored later. Redaction affects plain-text sharing and visible labels, not the backup payload itself.",
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
                    Text("Export selected profile")
                }
                OutlinedButton(
                    enabled = selectedProfile != null,
                    onClick = {
                        val profile = selectedProfile ?: return@OutlinedButton
                        val shareIntent = Intent(Intent.ACTION_SEND).apply {
                            type = "text/plain"
                            putExtra(Intent.EXTRA_SUBJECT, "AstroNumeric profile")
                            putExtra(Intent.EXTRA_TEXT, profile.toShareSummaryText(hideSensitiveDetailsEnabled))
                        }
                        context.startActivity(Intent.createChooser(shareIntent, "Share profile summary"))
                    },
                ) {
                    Text("Share text summary")
                }
                OutlinedButton(
                    onClick = {
                        importLauncher.launch(arrayOf("application/json", "text/plain"))
                    },
                ) {
                    Text("Import profile backup")
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
            title = "Questions?",
            body = "For privacy questions, deletion requests, or backend-held data concerns, email privacy@astromeric.app.",
        ) {
                OutlinedButton(
                    onClick = {
                        val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
                            data = Uri.parse("mailto:privacy@astromeric.app")
                            putExtra(Intent.EXTRA_SUBJECT, "AstroNumeric privacy question")
                            putExtra(Intent.EXTRA_TEXT, privacySupportEmailBody())
                        }
                        context.startActivity(emailIntent)
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("privacy@astromeric.app")
                }
        }
    }
}