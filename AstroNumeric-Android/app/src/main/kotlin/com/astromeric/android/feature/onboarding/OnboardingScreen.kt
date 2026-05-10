package com.astromeric.android.feature.onboarding

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.PagerState
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.feature.profile.ProfileEditorScreen
import kotlinx.coroutines.launch

private const val PAGE_WELCOME = 0
private const val PAGE_FEATURES = 1
private const val PAGE_PROFILE = 2
private const val PAGE_NOTIFICATIONS = 3
private const val PAGE_COUNT = 4

@Composable
@OptIn(ExperimentalMaterial3Api::class)
fun OnboardingScreen(
    profileRepository: ProfileRepository,
    preferencesStore: AppPreferencesStore,
    onComplete: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()
    val pagerState = rememberPagerState(pageCount = { PAGE_COUNT })

    val notificationLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
    ) {
        scope.launch { preferencesStore.setInitialOnboardingCompleted(true) }
        onComplete()
    }

    fun completeOnboarding() {
        scope.launch { preferencesStore.setInitialOnboardingCompleted(true) }
        onComplete()
    }

    fun navigateTo(page: Int) = scope.launch { pagerState.animateScrollToPage(page) }

    Scaffold(
        modifier = modifier,
        topBar = {
            OnboardingTopBar(
                pagerState = pagerState,
                onBack = { navigateTo(pagerState.currentPage - 1) },
                onSkip = { navigateTo(PAGE_NOTIFICATIONS) },
            )
        },
    ) { innerPadding ->
        HorizontalPager(
            state = pagerState,
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
            userScrollEnabled = pagerState.currentPage != PAGE_PROFILE,
        ) { page ->
            when (page) {
                PAGE_WELCOME -> WelcomePage(
                    onGetStarted = { navigateTo(PAGE_FEATURES) },
                    onSkip = { navigateTo(PAGE_NOTIFICATIONS) },
                )

                PAGE_FEATURES -> FeaturesPage(
                    onNext = { navigateTo(PAGE_PROFILE) },
                    onSkip = { navigateTo(PAGE_NOTIFICATIONS) },
                )

                PAGE_PROFILE -> ProfilePage(
                    profileRepository = profileRepository,
                    onProfileSaved = { navigateTo(PAGE_NOTIFICATIONS) },
                    onSkip = { navigateTo(PAGE_NOTIFICATIONS) },
                )

                PAGE_NOTIFICATIONS -> NotificationsPage(
                    onEnable = {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                            notificationLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                        } else {
                            ::completeOnboarding.invoke()
                        }
                    },
                    onSkip = ::completeOnboarding,
                )
            }
        }
    }
}

@Composable
@OptIn(ExperimentalMaterial3Api::class)
private fun OnboardingTopBar(
    pagerState: PagerState,
    onBack: () -> Unit,
    onSkip: () -> Unit,
) {
    val currentPage = pagerState.currentPage
    Column {
        TopAppBar(
            title = {},
            navigationIcon = {
                if (currentPage > PAGE_WELCOME) {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.action_back),
                        )
                    }
                }
            },
            actions = {
                if (currentPage != PAGE_NOTIFICATIONS) {
                    TextButton(onClick = onSkip) {
                        Text(stringResource(R.string.onboarding_action_skip))
                    }
                }
            },
        )
        // Progress dots
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp)
                .padding(bottom = 8.dp),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            repeat(PAGE_COUNT) { index ->
                val isActive = index == currentPage
                Box(
                    modifier = Modifier
                        .height(8.dp)
                        .width(if (isActive) 24.dp else 8.dp)
                        .background(
                            color = if (isActive) {
                                MaterialTheme.colorScheme.primary
                            } else {
                                MaterialTheme.colorScheme.outlineVariant
                            },
                            shape = CircleShape,
                        ),
                )
                if (index < PAGE_COUNT - 1) Spacer(Modifier.width(6.dp))
            }
        }
    }
}

// ─── Page 0 — Welcome ────────────────────────────────────────────────────────

@Composable
private fun WelcomePage(
    onGetStarted: () -> Unit,
    onSkip: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(16.dp))
        Icon(
            Icons.Filled.AutoAwesome,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.primary,
        )
        Text(
            text = stringResource(R.string.onboarding_welcome_title),
            style = MaterialTheme.typography.headlineMedium,
            textAlign = TextAlign.Center,
        )
        Text(
            text = stringResource(R.string.onboarding_welcome_tagline),
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(Modifier.height(8.dp))
        OnboardingProofPoint(
            title = stringResource(R.string.onboarding_first_run_proof_local_title),
            body = stringResource(R.string.onboarding_first_run_proof_local_detail),
        )
        OnboardingProofPoint(
            title = stringResource(R.string.onboarding_first_run_proof_chart_title),
            body = stringResource(R.string.onboarding_first_run_proof_chart_detail),
        )
        OnboardingProofPoint(
            title = stringResource(R.string.onboarding_first_run_proof_explore_title),
            body = stringResource(R.string.onboarding_first_run_proof_explore_detail),
        )
        Spacer(Modifier.height(8.dp))
        Button(
            onClick = onGetStarted,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.onboarding_welcome_button_start))
        }
        TextButton(
            onClick = onSkip,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.onboarding_first_run_button_explore))
        }
    }
}

// ─── Page 1 — Feature highlights ─────────────────────────────────────────────

@Composable
private fun FeaturesPage(
    onNext: () -> Unit,
    onSkip: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text(
            text = stringResource(R.string.onboarding_features_title),
            style = MaterialTheme.typography.headlineSmall,
        )
        Text(
            text = stringResource(R.string.onboarding_features_subtitle),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        FeatureHighlightCard(
            icon = Icons.Filled.Star,
            title = stringResource(R.string.onboarding_feature_charts_title),
            body = stringResource(R.string.onboarding_feature_charts_body),
        )
        FeatureHighlightCard(
            icon = Icons.Filled.AutoAwesome,
            title = stringResource(R.string.onboarding_feature_numerology_title),
            body = stringResource(R.string.onboarding_feature_numerology_body),
        )
        FeatureHighlightCard(
            icon = Icons.Filled.Favorite,
            title = stringResource(R.string.onboarding_feature_compatibility_title),
            body = stringResource(R.string.onboarding_feature_compatibility_body),
        )
        FeatureHighlightCard(
            icon = Icons.Filled.Person,
            title = stringResource(R.string.onboarding_feature_timing_title),
            body = stringResource(R.string.onboarding_feature_timing_body),
        )
        Spacer(Modifier.height(8.dp))
        Button(
            onClick = onNext,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.onboarding_features_button_next))
        }
        TextButton(
            onClick = onSkip,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.onboarding_action_skip))
        }
    }
}

@Composable
private fun FeatureHighlightCard(
    icon: ImageVector,
    title: String,
    body: String,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            verticalAlignment = Alignment.Top,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp),
            )
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(text = title, style = MaterialTheme.typography.titleSmall)
                Text(text = body, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}

// ─── Page 2 — Profile creation ────────────────────────────────────────────────

@Composable
private fun ProfilePage(
    profileRepository: ProfileRepository,
    onProfileSaved: () -> Unit,
    onSkip: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text = stringResource(R.string.onboarding_profile_title),
            style = MaterialTheme.typography.headlineSmall,
        )
        Text(
            text = stringResource(R.string.onboarding_profile_subtitle),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        ProfileEditorScreen(
            existingProfile = null,
            onSaved = onProfileSaved,
            onCancel = {},
            profileRepository = profileRepository,
            isOnboarding = true,
            scrollable = false,
            modifier = Modifier.fillMaxWidth(),
        )
        TextButton(
            onClick = onSkip,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.onboarding_profile_skip))
        }
    }
}

// ─── Page 3 — Notifications ───────────────────────────────────────────────────

@Composable
private fun NotificationsPage(
    onEnable: () -> Unit,
    onSkip: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(16.dp))
        Icon(
            Icons.Filled.Notifications,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.primary,
        )
        Text(
            text = stringResource(R.string.onboarding_notifications_title),
            style = MaterialTheme.typography.headlineSmall,
            textAlign = TextAlign.Center,
        )
        Text(
            text = stringResource(R.string.onboarding_notifications_body),
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OnboardingProofPoint(
            title = stringResource(R.string.onboarding_notifications_benefit_1_title),
            body = stringResource(R.string.onboarding_notifications_benefit_1_body),
        )
        OnboardingProofPoint(
            title = stringResource(R.string.onboarding_notifications_benefit_2_title),
            body = stringResource(R.string.onboarding_notifications_benefit_2_body),
        )
        Spacer(Modifier.weight(1f))
        Button(
            onClick = onEnable,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.onboarding_notifications_button_enable))
        }
        TextButton(
            onClick = onSkip,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.onboarding_notifications_button_skip))
        }
    }
}

// ─── Shared ───────────────────────────────────────────────────────────────────

@Composable
private fun OnboardingProofPoint(
    title: String,
    body: String,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(text = title, style = MaterialTheme.typography.titleSmall)
            Text(text = body, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
