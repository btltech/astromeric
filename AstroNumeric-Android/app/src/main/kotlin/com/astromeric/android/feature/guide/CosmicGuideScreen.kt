package com.astromeric.android.feature.guide

import android.Manifest
import android.content.Intent
import android.net.Uri
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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
import androidx.health.connect.client.PermissionController
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.R
import com.astromeric.android.core.data.local.ExactTransitCacheStore
import com.astromeric.android.core.data.local.NatalChartCacheStore
import com.astromeric.android.core.ephemeris.LocalSwissEphemerisEngine
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.loadNatalChartWithCacheFallback
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.CosmicGuideChatRequestData
import com.astromeric.android.core.model.DataQuality
import com.astromeric.android.core.model.GuideChatMessage
import com.astromeric.android.core.model.GuideMessageRole
import com.astromeric.android.core.model.GuideTone
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.toGuideHistory
import com.astromeric.android.core.model.zodiacSignName
import com.astromeric.android.core.ui.PermissionRationaleDialog
import com.astromeric.android.core.ui.PremiumHeroCard
import com.astromeric.android.core.ui.MysticModeToggle
import com.astromeric.android.core.ui.shouldShowPermissionRationale
import kotlinx.coroutines.launch

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun CosmicGuideScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    preferencesStore: AppPreferencesStore,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenProfile: () -> Unit,
    onOpenPrivacy: () -> Unit,
    onShowMessage: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val guideTone by preferencesStore.guideTone.collectAsStateWithLifecycle(initialValue = GuideTone.BALANCED)
    val calendarContextEnabled by preferencesStore.guideCalendarContextEnabled.collectAsStateWithLifecycle(initialValue = false)
    val biometricContextEnabled by preferencesStore.guideBiometricContextEnabled.collectAsStateWithLifecycle(initialValue = false)
    val localJournalEntries by preferencesStore.localJournalEntries.collectAsStateWithLifecycle(initialValue = emptyList())

    val chartCacheStore = remember(context) { NatalChartCacheStore(context.applicationContext) }
    val transitCacheStore = remember(context) { ExactTransitCacheStore(context.applicationContext) }
    val localEphemerisEngine = remember(context) { LocalSwissEphemerisEngine.getInstance(context.applicationContext) }
    val calendarProvider = remember(context) { GuideCalendarContextProvider(context.applicationContext) }
    val healthBridge = remember(context) { GuideHealthConnectBridge(context.applicationContext) }

    var inputText by remember(selectedProfile?.id) { mutableStateOf("") }
    var messages by remember(selectedProfile?.id) { mutableStateOf(emptyList<GuideChatMessage>()) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var isMystic by remember { mutableStateOf(true) }
    var moonSign by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var risingSign by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var showCalendarRationale by remember { mutableStateOf(false) }
    val calendarPermissionDeniedMessage = stringResource(R.string.privacy_calendar_permission_denied)
    val healthPermissionRequiredMessage = stringResource(R.string.guide_health_permission_required)
    val healthUpdateRequiredMessage = stringResource(R.string.guide_health_update_required_message)
    val healthUnavailableMessage = stringResource(R.string.guide_health_unavailable_message)
    val guideErrorFallback = stringResource(R.string.guide_error_fallback)

    val calendarPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        scope.launch {
            preferencesStore.setGuideCalendarContextEnabled(granted)
        }
        if (!granted) {
            onShowMessage(calendarPermissionDeniedMessage)
        }
    }
    val healthPermissionLauncher = rememberLauncherForActivityResult(PermissionController.createRequestPermissionResultContract()) { granted ->
        val approved = granted.containsAll(healthBridge.requiredPermissions)
        scope.launch {
            preferencesStore.setGuideBiometricContextEnabled(approved)
        }
        if (!approved) {
            onShowMessage(healthPermissionRequiredMessage)
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

    LaunchedEffect(selectedProfile?.id) {
        val profile = selectedProfile
        if (profile?.canRequestNatalChart != true) {
            moonSign = null
            risingSign = null
            return@LaunchedEffect
        }

        val result = loadNatalChartWithCacheFallback(
            profile = profile,
            remoteDataSource = remoteDataSource,
            chartCacheStore = chartCacheStore,
            localEphemerisEngine = localEphemerisEngine,
        )
        val chart = result.chart
        if (chart != null) {
            moonSign = chart.planets.firstOrNull { it.name.equals("Moon", ignoreCase = true) }?.sign
            risingSign = chart.points.firstOrNull { it.name.equals("Ascendant", ignoreCase = true) }?.sign
                ?: chart.houses.firstOrNull { it.house == 1 }?.sign
        } else {
            moonSign = null
            risingSign = null
        }
    }

    if (selectedProfile == null) {
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            PremiumHeroCard(
                eyebrow = stringResource(R.string.guide_eyebrow),
                title = stringResource(R.string.guide_title),
                body = stringResource(R.string.guide_body_no_profile),
            ) {
                Button(onClick = onOpenProfile) {
                    Text(stringResource(R.string.guide_open_profile))
                }
            }
        }
        return
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        PremiumHeroCard(
            eyebrow = stringResource(R.string.guide_eyebrow),
            title = stringResource(R.string.guide_title),
            body = stringResource(R.string.guide_body),
            chips = listOf(
                stringResource(
                    R.string.guide_active_profile_chip,
                    selectedProfile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                ),
            ),
        ) {
            Text(
                text = selectedProfile.dataQuality.description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            MysticModeToggle(
                isMystic = isMystic,
                onToggle = { isMystic = it },
            )
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                GuideTone.entries.forEach { tone ->
                    FilterChip(
                        selected = guideTone == tone,
                        onClick = {
                            scope.launch {
                                preferencesStore.setGuideTone(tone)
                            }
                        },
                        label = { Text("${tone.emoji} ${tone.label}") },
                    )
                }
            }
        }

        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (messages.isEmpty()) {
                item {
                    GuideContextCard(
                        title = stringResource(R.string.privacy_calendar_guidance_title),
                        body = if (calendarContextEnabled) {
                            stringResource(R.string.guide_calendar_body_enabled)
                        } else {
                            stringResource(R.string.guide_calendar_body_disabled)
                        },
                        actionLabel = if (calendarContextEnabled) stringResource(R.string.preference_state_on) else stringResource(R.string.action_enable),
                        onAction = {
                            if (calendarContextEnabled) {
                                scope.launch {
                                    preferencesStore.setGuideCalendarContextEnabled(false)
                                }
                            } else if (calendarProvider.hasPermission()) {
                                scope.launch {
                                    preferencesStore.setGuideCalendarContextEnabled(true)
                                }
                            } else {
                                requestCalendarPermission()
                            }
                        },
                    )
                }
                item {
                    val availability = healthBridge.availability()
                    GuideContextCard(
                        title = stringResource(R.string.privacy_biometric_guidance_title),
                        body = when {
                            biometricContextEnabled -> stringResource(R.string.guide_biometric_body_enabled)
                            availability == GuideHealthAvailability.UPDATE_REQUIRED -> stringResource(R.string.guide_biometric_body_update_required)
                            availability == GuideHealthAvailability.UNAVAILABLE -> stringResource(R.string.guide_biometric_body_unavailable)
                            else -> stringResource(R.string.guide_biometric_body_disabled)
                        },
                        actionLabel = if (biometricContextEnabled) stringResource(R.string.preference_state_on) else stringResource(R.string.action_enable),
                        onAction = {
                            if (biometricContextEnabled) {
                                scope.launch {
                                    preferencesStore.setGuideBiometricContextEnabled(false)
                                }
                            } else {
                                when (availability) {
                                    GuideHealthAvailability.AVAILABLE -> {
                                        healthPermissionLauncher.launch(healthBridge.requiredPermissions)
                                    }
                                    GuideHealthAvailability.UPDATE_REQUIRED -> {
                                        openHealthConnectListing(context)
                                        onShowMessage(healthUpdateRequiredMessage)
                                    }
                                    GuideHealthAvailability.UNAVAILABLE -> {
                                        onShowMessage(healthUnavailableMessage)
                                    }
                                }
                            }
                        },
                    )
                }
                item {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(10.dp),
                        ) {
                            Text(
                                text = stringResource(R.string.guide_suggested_prompts_title),
                                style = MaterialTheme.typography.titleMedium,
                            )
                            FlowRow(
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp),
                            ) {
                                defaultGuidePrompts().forEach { prompt ->
                                    AssistChip(
                                        onClick = { inputText = prompt },
                                        label = { Text(prompt) },
                                    )
                                }
                            }
                        }
                    }
                }
            }

            if (!errorMessage.isNullOrBlank()) {
                item {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Text(
                            text = errorMessage.orEmpty(),
                            modifier = Modifier.padding(16.dp),
                            color = MaterialTheme.colorScheme.error,
                        )
                    }
                }
            }

            items(messages, key = { it.id }) { message ->
                GuideMessageBubble(message = message)
            }

            if (isLoading) {
                item {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Text(
                            text = stringResource(R.string.guide_loading_message),
                            modifier = Modifier.padding(16.dp),
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    label = { Text(stringResource(R.string.guide_input_label)) },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 3,
                    enabled = !isLoading,
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Button(
                        enabled = inputText.isNotBlank() && !isLoading,
                        onClick = {
                            val trimmed = inputText.trim()
                            if (trimmed.isBlank()) {
                                return@Button
                            }
                            scope.launch {
                                errorMessage = null
                                isLoading = true

                                val updatedMessages = messages + GuideChatMessage(
                                    role = GuideMessageRole.USER,
                                    content = trimmed,
                                )
                                messages = updatedMessages
                                inputText = ""

                                val calendarContext = if (calendarContextEnabled) {
                                    calendarProvider.buildContextBlock()
                                } else {
                                    null
                                }
                                val biometricSnapshot = if (biometricContextEnabled && healthBridge.hasAllPermissions()) {
                                    healthBridge.readTodaySnapshot()
                                } else {
                                    GuideBiometricSnapshot()
                                }

                                val cachedTransits = transitCacheStore
                                    .read(selectedProfile.id)?.transits
                                    .orEmpty()
                                val bioCosmicContext = BioCosmicCorrelator.contextBlock(
                                    snapshot = biometricSnapshot.takeIf { it.hasData },
                                    transits = cachedTransits,
                                    query = trimmed,
                                )

                                val request = CosmicGuideChatRequestData(
                                    message = trimmed,
                                    sunSign = selectedProfile.zodiacSignName()?.replaceFirstChar { it.uppercase() },
                                    moonSign = moonSign,
                                    risingSign = risingSign,
                                    birthTimeAssumed = selectedProfile.dataQuality != DataQuality.FULL,
                                    timeConfidence = selectedProfile.timeConfidence.wireValue,
                                    history = updatedMessages.toGuideHistory(),
                                    systemPrompt = buildGuideSystemPrompt(
                                        profile = selectedProfile,
                                        tone = guideTone,
                                        isMystic = isMystic,
                                        hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                                        moonSign = moonSign,
                                        risingSign = risingSign,
                                        journalEntries = localJournalEntries.filter { it.profileId == selectedProfile.id },
                                        userQuery = trimmed,
                                        calendarContext = calendarContext,
                                        biometricSnapshot = biometricSnapshot.takeIf { it.hasData },
                                        bioCosmicContext = bioCosmicContext,
                                    ),
                                    tone = guideTone.wireValue,
                                )

                                remoteDataSource.fetchCosmicGuideChat(request)
                                    .onSuccess { response ->
                                        messages = updatedMessages + GuideChatMessage(
                                            role = GuideMessageRole.ASSISTANT,
                                            content = response.response,
                                        )
                                    }
                                    .onFailure { error ->
                                        errorMessage = error.message ?: guideErrorFallback
                                        onShowMessage(errorMessage.orEmpty())
                                    }

                                isLoading = false
                            }
                        },
                    ) {
                        Text(stringResource(R.string.guide_send))
                    }
                    OutlinedButton(onClick = onOpenPrivacy) {
                        Text(stringResource(R.string.guide_privacy))
                    }
                }
            }
        }
    }
}

@Composable
private fun GuideContextCard(
    title: String,
    body: String,
    actionLabel: String,
    onAction: () -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                )
                Text(
                    text = body,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            OutlinedButton(onClick = onAction) {
                Text(actionLabel)
            }
        }
    }
}

@Composable
private fun GuideMessageBubble(
    message: GuideChatMessage,
) {
    val isUser = message.role == GuideMessageRole.USER
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start,
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(if (isUser) 0.88f else 0.94f),
        ) {
            Text(
                text = message.content,
                modifier = Modifier.padding(16.dp),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
private fun defaultGuidePrompts(): List<String> = listOf(
    stringResource(R.string.guide_prompt_1),
    stringResource(R.string.guide_prompt_2),
    stringResource(R.string.guide_prompt_3),
    stringResource(R.string.guide_prompt_4),
    stringResource(R.string.guide_prompt_5),
)

private fun openHealthConnectListing(context: android.content.Context) {
    val uri = Uri.parse(
        "market://details?id=${GuideHealthConnectBridge.providerPackageName}&url=healthconnect%3A%2F%2Fonboarding",
    )
    val intent = Intent(Intent.ACTION_VIEW).apply {
        setPackage("com.android.vending")
        data = uri
        putExtra("overlay", true)
        putExtra("callerId", context.packageName)
    }
    runCatching {
        context.startActivity(intent)
    }.onFailure {
        context.startActivity(
            Intent(
                Intent.ACTION_VIEW,
                Uri.parse("https://play.google.com/store/apps/details?id=${GuideHealthConnectBridge.providerPackageName}"),
            ),
        )
    }
}