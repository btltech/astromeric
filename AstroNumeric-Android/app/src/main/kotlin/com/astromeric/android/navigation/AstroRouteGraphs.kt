package com.astromeric.android.navigation

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.SnackbarHostState
import androidx.compose.ui.Modifier
import androidx.navigation.NavGraphBuilder
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.composable
import androidx.navigation.compose.navigation
import androidx.navigation.navArgument
import com.astromeric.android.app.PushRegistrationManager
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.feature.charts.BirthChartDetailScreen
import com.astromeric.android.feature.charts.ChartsScreen
import com.astromeric.android.feature.charts.CompositeChartScreen
import com.astromeric.android.feature.charts.ProgressionsScreen
import com.astromeric.android.feature.charts.SynastryChartScreen
import com.astromeric.android.feature.profile.HelpFaqScreen
import com.astromeric.android.feature.profile.NotificationSettingsScreen
import com.astromeric.android.feature.profile.PrivacyScreen
import com.astromeric.android.feature.profile.ProfileEditorScreen
import com.astromeric.android.feature.profile.ProfileListScreen
import com.astromeric.android.feature.profile.UserGuideScreen
import com.astromeric.android.feature.tools.YearAheadScreen
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

internal fun NavGraphBuilder.chartsGraph(
    navController: NavHostController,
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    effectiveAuthAccessToken: String,
    hideSensitiveDetailsEnabled: Boolean,
    scope: CoroutineScope,
    snackbarHostState: SnackbarHostState,
) {
    navigation(startDestination = ChartsStudioRoute, route = TopLevelDestination.CHARTS.route) {
        composable(ChartsStudioRoute) {
            ChartsScreen(
                profiles = profiles,
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                authAccessToken = effectiveAuthAccessToken,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenRelationships = { navController.navigateSingleTop(RelationshipsRoute) },
                onOpenYearAhead = { navController.navigateSingleTop(ChartsYearAheadRoute) },
                onOpenBirthChart = { navController.navigateSingleTop(BirthChartDetailRoute) },
                onOpenProgressions = { navController.navigateSingleTop(ProgressionsRoute) },
                onOpenSynastry = { navController.navigateSingleTop(SynastryRoute) },
                onOpenComposite = { navController.navigateSingleTop(CompositeRoute) },
            )
        }
        composable(BirthChartDetailRoute) {
            BirthChartDetailScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onBackToCharts = { navController.popBackStack() },
                onShowMessage = { message -> scope.launch { snackbarHostState.showSnackbar(message) } },
            )
        }
        composable(ProgressionsRoute) {
            ProgressionsScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                onBackToCharts = { navController.popBackStack() },
            )
        }
        composable(ChartsYearAheadRoute) {
            YearAheadScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                authAccessToken = effectiveAuthAccessToken,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenProfile = { navController.navigateSingleTop(TopLevelDestination.PROFILE.route) },
            )
        }
        composable(SynastryRoute) {
            SynastryChartScreen(
                profiles = profiles,
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                onBackToCharts = { navController.popBackStack() },
            )
        }
        composable(CompositeRoute) {
            CompositeChartScreen(
                profiles = profiles,
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                onBackToCharts = { navController.popBackStack() },
            )
        }
    }
}

internal fun NavGraphBuilder.profileGraph(
    navController: NavHostController,
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    preferencesStore: AppPreferencesStore,
    profileRepository: ProfileRepository,
    remoteDataSource: AstroRemoteDataSource,
    pushRegistrationManager: PushRegistrationManager,
    hideSensitiveDetailsEnabled: Boolean,
    personalModeEnabled: Boolean,
    accountSyncEnabled: Boolean,
    authUserEmail: String,
    showFirstRunPrompt: Boolean,
    scope: CoroutineScope,
    snackbarHostState: SnackbarHostState,
    onFirstProfileCreated: () -> Unit,
) {
    composable(TopLevelDestination.PROFILE.route) {
        ProfileListScreen(
            profiles = profiles,
            selectedProfileId = selectedProfile?.id,
            preferencesStore = preferencesStore,
            hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            personalModeEnabled = personalModeEnabled,
            isAuthenticated = accountSyncEnabled,
            accountEmail = authUserEmail,
            onCreateProfile = { navController.navigate(profileEditorRoute()) },
            onOpenLearn = { navController.navigateSingleTop(LearnRoute) },
            onOpenGuide = { navController.navigateSingleTop(CosmicGuideRoute) },
            onOpenUserGuide = { navController.navigateSingleTop(UserGuideRoute) },
            onOpenHelp = { navController.navigateSingleTop(HelpRoute) },
            onOpenNotifications = { navController.navigateSingleTop(NotificationsRoute) },
            onOpenPrivacy = { navController.navigateSingleTop(PrivacyRoute) },
            onSyncProfiles = {
                scope.launch {
                    profileRepository.syncProfilesToAccount()
                        .onSuccess { synced -> snackbarHostState.showSnackbar("Synced ${synced.size} profile(s) with your account.") }
                        .onFailure { error -> snackbarHostState.showSnackbar(error.message ?: "Profile sync failed.") }
                }
            },
            onEditProfile = { profileId -> navController.navigate(profileEditorRoute(profileId)) },
            onSelectProfile = { profileId -> scope.launch { profileRepository.selectProfile(profileId) } },
            onDeleteProfile = { profileId -> scope.launch { profileRepository.deleteProfile(profileId) } },
            onSeedDebugProfile = {
                scope.launch {
                    val existingLocalSeed = profiles.firstOrNull { it.isLocalOnly && it.name == DebugSwissSeedProfileName }
                    profileRepository.saveLocalProfile(draft = buildDebugSwissSeedProfileDraft(existingLocalSeed?.id))
                    snackbarHostState.showSnackbar("Seeded and selected the Swiss test profile.")
                }
            },
        )
    }
    composable(NotificationsRoute) {
        NotificationSettingsScreen(
            preferencesStore = preferencesStore,
            remoteDataSource = remoteDataSource,
            profileRepository = profileRepository,
            pushRegistrationManager = pushRegistrationManager,
            selectedProfile = selectedProfile,
            onShowMessage = { message -> scope.launch { snackbarHostState.showSnackbar(message) } },
        )
    }
    composable(UserGuideRoute) { UserGuideScreen() }
    composable(HelpRoute) { HelpFaqScreen() }
    composable(PrivacyRoute) {
        PrivacyScreen(
            profiles = profiles,
            selectedProfile = selectedProfile,
            preferencesStore = preferencesStore,
            profileRepository = profileRepository,
            onShowMessage = { message -> scope.launch { snackbarHostState.showSnackbar(message) } },
        )
    }
    composable(
        route = "$ProfileEditorBaseRoute/{profileId}",
        arguments = listOf(navArgument("profileId") { type = NavType.IntType }),
    ) { backStackEntry ->
        val profileId = backStackEntry.arguments?.getInt("profileId") ?: 0
        val existingProfile = profiles.firstOrNull { it.id == profileId }
        val isFirstProfileCreation = existingProfile == null && showFirstRunPrompt

        ProfileEditorScreen(
            existingProfile = existingProfile,
            onSaved = {
                if (isFirstProfileCreation) {
                    scope.launch { preferencesStore.setInitialOnboardingCompleted(true) }
                    onFirstProfileCreated()
                }
                navController.popBackStack()
            },
            onCancel = { navController.popBackStack() },
            profileRepository = profileRepository,
            modifier = Modifier.fillMaxSize(),
        )
    }
}

private fun NavHostController.navigateSingleTop(route: String) {
    navigate(route) { launchSingleTop = true }
}