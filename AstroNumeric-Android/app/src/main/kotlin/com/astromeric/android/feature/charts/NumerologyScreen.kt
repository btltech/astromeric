package com.astromeric.android.feature.charts

import android.content.Context
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.NumerologyData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.NumerologyShareCard
import com.astromeric.android.core.ui.renderComposableToBitmap
import com.astromeric.android.core.ui.shareBitmapCard
import java.time.Instant

@Composable
@OptIn(ExperimentalMaterial3Api::class)
fun NumerologyScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    authAccessToken: String,
    hideSensitiveDetailsEnabled: Boolean = false,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var selectedMethod by rememberSaveable { mutableStateOf(NumerologyMethod.PYTHAGOREAN) }
    var isLoading by remember(selectedProfile?.id, selectedMethod) { mutableStateOf(false) }
    var numerologyData by remember(selectedProfile?.id, selectedMethod) { mutableStateOf<NumerologyData?>(null) }
    var errorMessage by remember(selectedProfile?.id, selectedMethod) { mutableStateOf<String?>(null) }
    var isExplaining by remember(selectedProfile?.id, selectedMethod) { mutableStateOf(false) }
    var explanationSummary by remember(selectedProfile?.id, selectedMethod) { mutableStateOf<String?>(null) }
    var explanationProvider by remember(selectedProfile?.id, selectedMethod) { mutableStateOf<String?>(null) }
    var explanationGeneratedAt by remember(selectedProfile?.id, selectedMethod) { mutableStateOf<Instant?>(null) }
    var showExplanationSheet by remember(selectedProfile?.id, selectedMethod) { mutableStateOf(false) }

    LaunchedEffect(selectedProfile?.id, selectedMethod) {
        val profile = selectedProfile ?: run {
            numerologyData = null
            errorMessage = null
            isLoading = false
            return@LaunchedEffect
        }
        isLoading = true
        errorMessage = null
        remoteDataSource.fetchNumerology(profile = profile, method = selectedMethod.wireValue)
            .onSuccess { numerologyData = it }
            .onFailure {
                numerologyData = null
                errorMessage = it.message ?: context.getString(R.string.charts_numerology_error_load)
            }
        isLoading = false
    }

    LaunchedEffect(isExplaining) {
        if (!isExplaining) return@LaunchedEffect
        val loadedNumerology = numerologyData ?: run { isExplaining = false; return@LaunchedEffect }
        val profile = selectedProfile ?: run { isExplaining = false; return@LaunchedEffect }
        val explainResult = remoteDataSource.fetchAIExplain(
            authToken = authAccessToken.takeIf { it.isNotBlank() },
            request = buildNumerologyExplainRequest(context, profile, loadedNumerology),
        ).getOrNull()
        explanationSummary = explainResult?.summary ?: buildNumerologyFallbackSummary(context, profile, loadedNumerology)
        explanationProvider = explainResult?.provider ?: "fallback"
        explanationGeneratedAt = Instant.now()
        showExplanationSheet = true
        isExplaining = false
    }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.numerology_screen_title)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.action_back),
                        )
                    }
                },
                actions = {
                    val data = numerologyData
                    if (data != null) {
                        IconButton(onClick = {
                            shareNumerologyCard(
                                context = context,
                                data = data,
                                profile = selectedProfile,
                                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                            )
                        }) {
                            Icon(Icons.Filled.Share, contentDescription = stringResource(R.string.action_share))
                        }
                    }
                },
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(innerPadding)
                .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            NumerologyTab(
                selectedProfile = selectedProfile,
                selectedMethod = selectedMethod,
                onSelectMethod = { selectedMethod = it },
                isLoading = isLoading,
                errorMessage = errorMessage,
                numerology = numerologyData,
                isExplaining = isExplaining,
                onExplain = { isExplaining = true },
            )
        }
    }

    if (showExplanationSheet && explanationSummary != null) {
        ModalBottomSheet(onDismissRequest = { showExplanationSheet = false }) {
            NumerologyExplanationSheet(
                markdown = explanationSummary.orEmpty(),
                provider = explanationProvider,
                generatedAt = explanationGeneratedAt,
                isExplaining = isExplaining,
                onRegenerate = { isExplaining = true },
            )
        }
    }
}

private fun shareNumerologyCard(
    context: Context,
    data: NumerologyData,
    profile: AppProfile?,
    hideSensitiveDetailsEnabled: Boolean,
) {
    val profileName = profile?.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.SHARE) ?: "AstroNumeric"
    val density = context.resources.displayMetrics.density
    val widthPx = (300 * density * 3).toInt()
    val bitmap = renderComposableToBitmap(context, widthPx, 0) {
        NumerologyShareCard(data = data, profileName = profileName)
    }
    shareBitmapCard(context, bitmap, filename = "numerology_share.png", chooserTitle = "Share Numerology")
}
