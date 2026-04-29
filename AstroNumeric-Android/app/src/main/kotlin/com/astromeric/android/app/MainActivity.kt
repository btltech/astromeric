package com.astromeric.android.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.core.ui.theme.AstroNumericTheme
import com.astromeric.android.navigation.AstroShell

class MainActivity : ComponentActivity() {
    private var launchRoute by mutableStateOf<String?>(null)
    private var launchRouteNonce by mutableIntStateOf(0)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        consumeLaunchRoute(intent?.getStringExtra(MorningBriefWidgetProvider.LaunchRouteExtra))

        val appContainer = (application as AstroNumericApplication).appContainer

        setContent {
            AstroNumericApp(
                appContainer = appContainer,
                launchRoute = launchRoute,
                launchRouteNonce = launchRouteNonce,
            )
        }
    }

    override fun onNewIntent(intent: android.content.Intent) {
        super.onNewIntent(intent)
        consumeLaunchRoute(intent.getStringExtra(MorningBriefWidgetProvider.LaunchRouteExtra))
    }

    private fun consumeLaunchRoute(route: String?) {
        launchRoute = route
        launchRouteNonce += 1
    }
}

@Composable
private fun AstroNumericApp(
    appContainer: AppContainer,
    launchRoute: String?,
    launchRouteNonce: Int,
) {
    val profiles by appContainer.profileRepository.profiles.collectAsStateWithLifecycle(initialValue = emptyList())
    val selectedProfile by appContainer.profileRepository.selectedProfile.collectAsStateWithLifecycle(initialValue = null)
    val initialOnboardingCompleted by appContainer.preferencesStore.initialOnboardingCompleted.collectAsStateWithLifecycle(initialValue = false)
    val highContrastEnabled by appContainer.preferencesStore.highContrastEnabled.collectAsStateWithLifecycle(initialValue = false)
    val largeTextEnabled by appContainer.preferencesStore.largeTextEnabled.collectAsStateWithLifecycle(initialValue = false)

    AstroNumericTheme(
        highContrastEnabled = highContrastEnabled,
        largeTextEnabled = largeTextEnabled,
    ) {
        AstroShell(
            profiles = profiles,
            selectedProfile = selectedProfile,
            profileRepository = appContainer.profileRepository,
            habitRepository = appContainer.habitRepository,
            journalRepository = appContainer.journalRepository,
            preferencesStore = appContainer.preferencesStore,
            remoteDataSource = appContainer.remoteDataSource,
            launchRoute = launchRoute,
            launchRouteNonce = launchRouteNonce,
            showFirstRunPrompt = profiles.isEmpty() && !initialOnboardingCompleted,
        )
    }
}

@Composable
private fun LoadingRoot() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background),
        contentAlignment = Alignment.Center,
    ) {
        CircularProgressIndicator()
    }
}
