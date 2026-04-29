package com.astromeric.android.feature.journal

import android.Manifest
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.core.data.repository.JournalRepository
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.JournalDashboardData
import com.astromeric.android.core.model.JournalEntryCardData
import com.astromeric.android.core.model.JournalOutcome
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.defaultJournalPrompts
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PermissionRationaleDialog
import com.astromeric.android.core.ui.PremiumHeroCard
import com.astromeric.android.core.ui.shouldShowPermissionRationale
import kotlinx.coroutines.launch

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun JournalScreen(
    selectedProfile: AppProfile?,
    journalRepository: JournalRepository,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenProfile: () -> Unit,
    onShowMessage: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val profileId = selectedProfile?.id
    val voiceRecorder = remember(context) { VoiceJournalRecorder(context.applicationContext) }

    var dashboard by remember(profileId) { mutableStateOf<JournalDashboardData?>(null) }
    var isLoading by remember(profileId) { mutableStateOf(false) }
    var loadError by remember(profileId) { mutableStateOf<String?>(null) }
    var refreshKey by remember(profileId) { mutableStateOf(0) }
    var selectedEntryId by remember(profileId) { mutableStateOf<Int?>(null) }
    var entryDraft by remember(profileId) { mutableStateOf("") }
    var outcomeDraft by remember(profileId) { mutableStateOf(JournalOutcome.NEUTRAL) }
    var showMicrophoneRationale by remember { mutableStateOf(false) }

    val prompts = dashboard?.prompts?.ifEmpty { defaultJournalPrompts() } ?: defaultJournalPrompts()
    val entries = dashboard?.entries.orEmpty()
    val isRemoteMode = dashboard?.isRemote == true
    val selectedEntry = entries.firstOrNull { it.id == selectedEntryId }
    val trackedEntries = entries.filter { it.hasJournal || it.journalFull.isNotBlank() }
    val accurateCount = dashboard?.stats?.byOutcome?.get(JournalOutcome.YES.wireValue)
        ?: trackedEntries.count { it.journalOutcome == JournalOutcome.YES }
    val mixedCount = dashboard?.stats?.byOutcome?.get(JournalOutcome.PARTIAL.wireValue)
        ?: trackedEntries.count { it.journalOutcome == JournalOutcome.PARTIAL }
    val remoteSaveEnabled = selectedEntry != null && (
        entryDraft.trim() != selectedEntry.journalFull.trim() || outcomeDraft != selectedEntry.journalOutcome
        ) && (
        entryDraft.isNotBlank() ||
            outcomeDraft != selectedEntry.journalOutcome ||
            selectedEntry.journalFull.isNotBlank()
        )
    val canSave = if (isRemoteMode) remoteSaveEnabled else entryDraft.isNotBlank()
        val modeLabel = if (isRemoteMode) {
            stringResource(R.string.journal_account_synced_mode)
        } else {
            stringResource(R.string.journal_local_first_mode)
        }
        val microphoneAccessRequiredMessage = stringResource(R.string.journal_microphone_required_message)
        val loadErrorFallback = stringResource(R.string.journal_load_error_fallback)
        val syncedSaveMessage = stringResource(R.string.journal_synced_save_message)
        val localSaveMessage = stringResource(R.string.journal_local_save_message)
        val saveErrorFallback = stringResource(R.string.journal_save_error_fallback)
        val removeMessage = stringResource(R.string.journal_remove_message)
        val removeErrorFallback = stringResource(R.string.journal_remove_error_fallback)

    fun resetDrafts(clearSelection: Boolean = true) {
        if (voiceRecorder.isRecording) {
            voiceRecorder.stopRecording()
        }
        if (clearSelection) {
            selectedEntryId = null
        }
        entryDraft = ""
        outcomeDraft = JournalOutcome.NEUTRAL
    }

    fun selectEntry(entry: JournalEntryCardData) {
        selectedEntryId = entry.id
        entryDraft = entry.journalFull
        outcomeDraft = entry.journalOutcome
    }

    fun requestRefresh(resetComposer: Boolean = false) {
        if (resetComposer) {
            resetDrafts(clearSelection = true)
        }
        refreshKey += 1
    }

    val recordAudioPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        voiceRecorder.onPermissionResult(granted)
        if (granted) {
            voiceRecorder.startRecording()
        } else {
            onShowMessage(microphoneAccessRequiredMessage)
        }
    }

    fun requestMicrophonePermission() {
        if (shouldShowPermissionRationale(context, Manifest.permission.RECORD_AUDIO)) {
            showMicrophoneRationale = true
        } else {
            recordAudioPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }

    if (showMicrophoneRationale) {
        PermissionRationaleDialog(
            title = stringResource(R.string.journal_microphone_permission_title),
            message = stringResource(R.string.journal_microphone_permission_message),
            onConfirm = {
                showMicrophoneRationale = false
                recordAudioPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            },
            onDismiss = {
                showMicrophoneRationale = false
            },
        )
    }

    LaunchedEffect(profileId, refreshKey) {
        voiceRecorder.refreshAuthorizationStatus()
        dashboard = null
        loadError = null

        val profile = selectedProfile ?: run {
            isLoading = false
            return@LaunchedEffect
        }

        isLoading = true
        journalRepository.loadDashboard(profile)
            .onSuccess { loaded ->
                dashboard = loaded
            }
            .onFailure { error ->
                loadError = error.message ?: loadErrorFallback
            }
        isLoading = false
    }

    LaunchedEffect(entries, selectedEntryId) {
        val currentEntryId = selectedEntryId ?: return@LaunchedEffect
        if (entries.none { it.id == currentEntryId }) {
            resetDrafts(clearSelection = true)
        }
    }

    LaunchedEffect(voiceRecorder.completedTranscript) {
        val spokenText = voiceRecorder.consumeCompletedTranscript() ?: return@LaunchedEffect
        entryDraft = buildString {
            append(entryDraft)
            if (entryDraft.isNotBlank() && !entryDraft.endsWith(" ")) {
                append(' ')
            }
            append(spokenText)
        }
    }

    DisposableEffect(voiceRecorder) {
        onDispose {
            voiceRecorder.destroy()
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = stringResource(R.string.journal_title),
            title = stringResource(R.string.journal_title),
            body = stringResource(R.string.journal_summary),
            chips = selectedProfile?.let { profile ->
                listOf(
                    stringResource(
                        R.string.journal_active_profile,
                        profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                        modeLabel,
                    ),
                )
            }.orEmpty(),
        ) {
            if (selectedProfile == null) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = stringResource(R.string.journal_create_profile_first),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.weight(1f),
                    )
                    OutlinedButton(onClick = onOpenProfile) {
                        Text(stringResource(R.string.journal_open_profile))
                    }
                }
            }
        }

        if (selectedProfile == null) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(
                    text = stringResource(R.string.journal_profile_required),
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            return@Column
        }

        if (isLoading) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    CircularProgressIndicator()
                    Text(
                        text = if (isRemoteMode) {
                            stringResource(R.string.journal_refreshing_synced)
                        } else {
                            stringResource(R.string.journal_refreshing_local)
                        },
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        }

        loadError?.let { errorMessage ->
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = errorMessage,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.error,
                    )
                    OutlinedButton(onClick = { requestRefresh() }) {
                        Text(stringResource(R.string.journal_retry))
                    }
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = stringResource(R.string.journal_reflection_prompts),
                    style = MaterialTheme.typography.titleMedium,
                )
                prompts.forEach { prompt ->
                    Text(
                        text = prompt,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (isRemoteMode) {
                JournalMetricCard(
                    title = stringResource(R.string.journal_metric_journaled),
                    value = (dashboard?.report?.summary?.withJournal ?: trackedEntries.size).toString(),
                    modifier = Modifier.weight(1f),
                )
                JournalMetricCard(
                    title = stringResource(R.string.journal_metric_accuracy),
                    value = formatPercent(dashboard?.stats?.accuracyRate),
                    modifier = Modifier.weight(1f),
                )
                JournalMetricCard(
                    title = stringResource(R.string.journal_metric_engagement),
                    value = formatPercent(dashboard?.report?.summary?.engagementScore),
                    modifier = Modifier.weight(1f),
                )
            } else {
                JournalMetricCard(
                    title = stringResource(R.string.journal_metric_entries),
                    value = trackedEntries.size.toString(),
                    modifier = Modifier.weight(1f),
                )
                JournalMetricCard(
                    title = stringResource(R.string.journal_metric_accurate),
                    value = accurateCount.toString(),
                    modifier = Modifier.weight(1f),
                )
                JournalMetricCard(
                    title = stringResource(R.string.journal_metric_mixed),
                    value = mixedCount.toString(),
                    modifier = Modifier.weight(1f),
                )
            }
        }

        if (isRemoteMode) {
            dashboard?.stats?.message
                ?.takeIf { it.isNotBlank() }
                ?.let { message ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Text(
                            text = "${dashboard?.stats?.trendEmoji.orEmpty()} $message",
                            modifier = Modifier.padding(16.dp),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                }

            dashboard?.insights?.insights
                ?.takeIf { it.isNotEmpty() }
                ?.let { insights ->
                    JournalBulletListCard(
                        title = stringResource(R.string.journal_insights_title),
                        items = insights,
                    )
                }

            dashboard?.patterns?.let { patterns ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(
                            text = stringResource(R.string.journal_patterns_title),
                            style = MaterialTheme.typography.titleMedium,
                        )
                        if (patterns.patternsFound && patterns.patterns.isNotEmpty()) {
                            patterns.patterns.forEach { pattern ->
                                Text(
                                    text = "• ${pattern.insight}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        } else {
                            Text(
                                text = patterns.message ?: stringResource(R.string.journal_patterns_empty),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
            }

            dashboard?.report?.recommendations
                ?.map { it.text }
                ?.takeIf { it.isNotEmpty() }
                ?.let { recommendations ->
                    JournalBulletListCard(
                        title = stringResource(R.string.journal_recommendations_title),
                        items = recommendations,
                    )
                }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text(
                    text = when {
                        isRemoteMode && selectedEntry == null -> stringResource(R.string.journal_select_synced_reading)
                        isRemoteMode -> stringResource(
                            R.string.journal_update_reading,
                            selectedEntry?.scopeLabel ?: stringResource(R.string.journal_reading_fallback),
                        )
                        selectedEntryId == null -> stringResource(R.string.journal_new_entry)
                        else -> stringResource(R.string.journal_edit_entry, selectedEntryId ?: 0)
                    },
                    style = MaterialTheme.typography.titleMedium,
                )
                if (isRemoteMode) {
                    Text(
                        text = if (selectedEntry == null) {
                            stringResource(R.string.journal_pick_synced_reading)
                        } else {
                            stringResource(
                                R.string.journal_editing_synced_reading,
                                selectedEntry.scopeLabel.lowercase(),
                                selectedEntry.formattedDate,
                            )
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    selectedEntry?.supportingText
                        ?.takeIf { it.isNotBlank() }
                        ?.let { summary ->
                            Text(
                                text = summary,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                }
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    JournalOutcome.entries.forEach { outcome ->
                        FilterChip(
                            selected = outcomeDraft == outcome,
                            onClick = { outcomeDraft = outcome },
                            label = { Text(outcome.label) },
                        )
                    }
                }
                OutlinedTextField(
                    value = entryDraft,
                    onValueChange = { entryDraft = it },
                    label = { Text(stringResource(R.string.journal_entry_label)) },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 6,
                )
                Text(
                    text = stringResource(R.string.journal_voice_detail),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(
                        onClick = {
                            if (voiceRecorder.isRecording) {
                                voiceRecorder.stopRecording()
                            } else if (voiceRecorder.isAuthorized) {
                                voiceRecorder.startRecording()
                            } else {
                                requestMicrophonePermission()
                            }
                        },
                    ) {
                        Text(
                            if (voiceRecorder.isRecording) {
                                stringResource(R.string.journal_stop_voice)
                            } else {
                                stringResource(R.string.journal_voice)
                            },
                        )
                    }
                    if (voiceRecorder.transcript.isNotBlank()) {
                        Text(
                            text = voiceRecorder.transcript,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.weight(1f),
                        )
                    }
                }
                voiceRecorder.error?.let { voiceError ->
                    Text(
                        text = voiceError,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error,
                    )
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        enabled = canSave && !isLoading,
                        onClick = {
                            scope.launch {
                                val profile = selectedProfile ?: return@launch
                                journalRepository.saveReflection(
                                    profile = profile,
                                    entryId = selectedEntryId,
                                    entry = entryDraft,
                                    outcome = outcomeDraft,
                                )
                                    .onSuccess {
                                        onShowMessage(
                                            if (isRemoteMode) {
                                                syncedSaveMessage
                                            } else {
                                                localSaveMessage
                                            },
                                        )
                                        requestRefresh(resetComposer = true)
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: saveErrorFallback)
                                    }
                            }
                        },
                    ) {
                        Text(
                            if (isRemoteMode) {
                                stringResource(R.string.journal_save_to_account)
                            } else if (selectedEntryId == null) {
                                stringResource(R.string.journal_save_entry)
                            } else {
                                stringResource(R.string.journal_update_entry)
                            },
                        )
                    }
                    OutlinedButton(onClick = { resetDrafts(clearSelection = true) }) {
                        Text(
                            if (isRemoteMode) {
                                stringResource(R.string.journal_clear_selection)
                            } else {
                                stringResource(R.string.journal_new_blank)
                            },
                        )
                    }
                }
            }
        }

        if (entries.isEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(
                    text = if (isRemoteMode) {
                        stringResource(R.string.journal_no_synced_readings)
                    } else {
                        stringResource(R.string.journal_no_local_entries)
                    },
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        } else {
            entries.forEach { entry ->
                JournalEntryCard(
                    entry = entry,
                    actionLabel = if (entry.isLocalOnly) {
                        stringResource(R.string.journal_edit_action)
                    } else {
                        stringResource(R.string.journal_reflect_action)
                    },
                    onEdit = { selectEntry(entry) },
                    onDelete = if (entry.isLocalOnly) {
                        {
                            scope.launch {
                                val profile = selectedProfile ?: return@launch
                                journalRepository.deleteEntry(profile, entry.id)
                                    .onSuccess {
                                        if (selectedEntryId == entry.id) {
                                            resetDrafts(clearSelection = true)
                                        }
                                        onShowMessage(removeMessage)
                                        requestRefresh()
                                    }
                                    .onFailure { error ->
                                        onShowMessage(error.message ?: removeErrorFallback)
                                    }
                            }
                        }
                    } else {
                        null
                    },
                )
            }
        }
    }
}

@Composable
private fun JournalMetricCard(
    title: String,
    value: String,
    modifier: Modifier = Modifier,
) {
    Card(modifier = modifier) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = value,
                style = MaterialTheme.typography.headlineSmall,
            )
        }
    }
}

@Composable
private fun JournalEntryCard(
    entry: JournalEntryCardData,
    actionLabel: String,
    onEdit: () -> Unit,
    onDelete: (() -> Unit)? = null,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(
                        text = entry.scopeLabel,
                        style = MaterialTheme.typography.titleSmall,
                    )
                    Text(
                        text = entry.formattedDate,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                AssistChip(
                    onClick = {},
                    label = {
                        Text(entry.feedbackEmoji?.takeIf { it.isNotBlank() } ?: entry.journalOutcome.badge)
                    },
                )
            }
            entry.supportingText
                ?.takeIf { it.isNotBlank() && it != entry.previewText }
                ?.let { summary ->
                    Text(
                        text = summary,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            Text(
                text = entry.previewText,
                style = MaterialTheme.typography.bodyMedium,
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = onEdit) {
                    Text(actionLabel)
                }
                onDelete?.let { deleteAction ->
                    OutlinedButton(onClick = deleteAction) {
                        Text(stringResource(R.string.journal_remove_action))
                    }
                }
            }
        }
    }
}

@Composable
private fun JournalBulletListCard(
    title: String,
    items: List<String>,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
            )
            items.forEach { item ->
                Text(
                    text = "• $item",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

private fun formatPercent(value: Double?): String =
    value?.let { "%.0f%%".format(it) } ?: "0%"
