package com.astromeric.android.navigation

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.compose.ui.platform.LocalContext
import com.astromeric.android.app.PushRegistrationManager
import com.astromeric.android.core.data.local.NatalChartCacheStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.ephemeris.LocalSwissEphemerisEngine
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.repository.HabitRepository
import com.astromeric.android.core.data.repository.JournalRepository
import com.astromeric.android.core.data.repository.loadNatalChartWithCacheFallback
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DefaultHouseSystem
import com.astromeric.android.core.model.ProfileDraft
import com.astromeric.android.core.model.TimeConfidence
import com.astromeric.android.core.model.zodiacSignName
import com.astromeric.android.feature.charts.BirthChartDetailScreen
import com.astromeric.android.feature.charts.CompositeChartScreen
import com.astromeric.android.feature.charts.ChartsScreen
import com.astromeric.android.feature.charts.ProgressionsScreen
import com.astromeric.android.feature.charts.SynastryChartScreen
import com.astromeric.android.feature.explore.ExploreScreen
import com.astromeric.android.feature.guide.CosmicGuideScreen
import com.astromeric.android.feature.habits.HabitsScreen
import com.astromeric.android.feature.home.HomeScreen
import com.astromeric.android.feature.journal.JournalScreen
import com.astromeric.android.feature.learn.LearnScreen
import com.astromeric.android.feature.learn.LessonDetailScreen
import com.astromeric.android.feature.profile.HelpFaqScreen
import com.astromeric.android.feature.profile.NotificationSettingsScreen
import com.astromeric.android.feature.profile.ProfileEditorScreen
import com.astromeric.android.feature.profile.PrivacyScreen
import com.astromeric.android.feature.profile.ProfileListScreen
import com.astromeric.android.feature.profile.UserGuideScreen
import com.astromeric.android.feature.relationships.FriendsScreen
import com.astromeric.android.feature.relationships.RelationshipsScreen
import com.astromeric.android.feature.home.WeeklyVibeScreen
import com.astromeric.android.feature.reading.ReadingScreen
import com.astromeric.android.feature.tools.AffirmationScreen
import com.astromeric.android.feature.tools.BirthstonesScreen
import com.astromeric.android.feature.tools.DailyFeaturesScreen
import com.astromeric.android.feature.tools.MoonEventsScreen
import com.astromeric.android.feature.tools.MoonPhaseScreen
import com.astromeric.android.feature.tools.OracleScreen
import com.astromeric.android.feature.tools.TarotScreen
import com.astromeric.android.feature.tools.TemporalMatrixScreen
import com.astromeric.android.feature.tools.TimingAdvisorScreen
import com.astromeric.android.feature.tools.ToolsScreen
import com.astromeric.android.feature.tools.YearAheadScreen
import kotlinx.coroutines.launch

const val ProfileEditorBaseRoute = "profile/editor"
const val HabitsRoute = "habits"
const val JournalRoute = "journal"
const val LearnRoute = "learn"
const val RelationshipsRoute = "relationships"
const val TimingAdvisorRoute = "timing-advisor"
const val TemporalMatrixRoute = "temporal-matrix"
const val MoonPhaseRoute = "moon-phase"
const val YearAheadRoute = "year-ahead"
const val LifePhaseRoute = "life-phase"
const val ExploreRoute = "explore"
const val BirthstonesRoute = "birthstones"
const val ChartsStudioRoute = "charts/studio"
const val BirthChartDetailRoute = "charts/birth-detail"
const val ChartsYearAheadRoute = "charts/year-ahead"
const val ProgressionsRoute = "charts/progressions"
const val SynastryRoute = "charts/synastry"
const val CompositeRoute = "charts/composite"
const val PrivacyRoute = "profile/privacy"
const val NotificationsRoute = "profile/notifications"
const val UserGuideRoute = "profile/user-guide"
const val HelpRoute = "profile/help"
const val CosmicGuideRoute = "guide"
const val ReadingRoute = "reading"
const val DailyFeaturesRoute = "daily-features"
const val MoonEventsRoute = "moon-events"
const val WeeklyVibeRoute = "weekly-vibe"
const val AffirmationRoute = "affirmation"
const val OracleRoute = "oracle"
const val TarotRoute = "tarot"
const val FriendsRoute = "friends"
const val LessonDetailRoute = "lesson-detail"
const val DebugSwissSeedProfileName = "Swiss Offline Test"

enum class TopLevelDestination(
    val route: String,
    val label: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector,
) {
    HOME("home", "Home", Icons.Filled.Home),
    TOOLS("tools", "Tools", Icons.Filled.Build),
    CHARTS("charts", "Charts", Icons.Filled.BarChart),
    PROFILE("profile", "Profile", Icons.Filled.Person),
}

fun profileEditorRoute(profileId: Int? = null): String =
    "$ProfileEditorBaseRoute/${profileId ?: 0}"

fun buildDebugSwissSeedProfileDraft(existingProfileId: Int?): ProfileDraft = ProfileDraft(
    id = existingProfileId,
    name = DebugSwissSeedProfileName,
    dateOfBirth = "1994-06-15",
    timeOfBirth = "12:34:00",
    timeConfidence = TimeConfidence.EXACT,
    placeOfBirth = "Reykjavik, Iceland",
    latitude = 64.1466,
    longitude = -21.9426,
    timezone = "Atlantic/Reykjavik",
    houseSystem = DefaultHouseSystem,
)

@Composable
fun AstroShell(
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    profileRepository: ProfileRepository,
    habitRepository: HabitRepository,
    journalRepository: JournalRepository,
    preferencesStore: AppPreferencesStore,
    remoteDataSource: AstroRemoteDataSource,
    launchRoute: String? = null,
    launchRouteNonce: Int = 0,
    showFirstRunPrompt: Boolean = false,
) {
    val navController = rememberNavController()
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination
    var showFirstRunProfileComplete by rememberSaveable { mutableStateOf(false) }
    val currentTopLevelRoute = currentDestination?.hierarchy
        ?.mapNotNull { destination -> destination.route }
        ?.firstOrNull { route -> TopLevelDestination.entries.any { it.route == route } }
        ?: TopLevelDestination.HOME.route
    val isProfileEditorRoute = currentDestination?.route?.startsWith(ProfileEditorBaseRoute) == true

    LaunchedEffect(launchRouteNonce) {
        if (launchRoute.isNullOrBlank()) return@LaunchedEffect
        navController.navigate(launchRoute) {
            popUpTo(navController.graph.findStartDestination().id) {
                saveState = true
            }
            launchSingleTop = true
            restoreState = true
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(hostState = snackbarHostState) },
        bottomBar = {
            if (!isProfileEditorRoute) {
                NavigationBar {
                    TopLevelDestination.entries.forEach { destination ->
                        NavigationBarItem(
                            selected = currentDestination?.hierarchy?.any { it.route == destination.route } == true,
                            onClick = {
                                navController.navigate(destination.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = { Icon(destination.icon, contentDescription = destination.label) },
                            label = { Text(destination.label) },
                        )
                    }
                }
            }
        },
        floatingActionButton = {
            if (!isProfileEditorRoute && !currentTopLevelRoute.startsWith(TopLevelDestination.PROFILE.route)) {
                FloatingActionButton(
                    onClick = {
                        navController.navigate(CosmicGuideRoute) {
                            launchSingleTop = true
                        }
                    },
                ) {
                    Icon(Icons.Filled.AutoAwesome, contentDescription = "Open Cosmic Guide")
                }
            }
        },
    ) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize()) {
            AstroNavHost(
                navController = navController,
                innerPadding = innerPadding,
                profiles = profiles,
                selectedProfile = selectedProfile,
                profileRepository = profileRepository,
                habitRepository = habitRepository,
                journalRepository = journalRepository,
                preferencesStore = preferencesStore,
                remoteDataSource = remoteDataSource,
                snackbarHostState = snackbarHostState,
                showFirstRunPrompt = showFirstRunPrompt,
                onFirstProfileCreated = {
                    showFirstRunProfileComplete = true
                },
            )

            if (showFirstRunPrompt && !isProfileEditorRoute && !showFirstRunProfileComplete) {
                FirstRunProfilePromptOverlay(
                    modifier = Modifier.padding(innerPadding),
                    onCreateProfile = {
                        navController.navigate(profileEditorRoute()) {
                            launchSingleTop = true
                        }
                    },
                    onExploreFirst = {
                        scope.launch {
                            preferencesStore.setInitialOnboardingCompleted(true)
                        }
                    },
                )
            }

            if (showFirstRunProfileComplete && selectedProfile != null) {
                FirstRunProfileCompleteOverlay(
                    profile = selectedProfile,
                    remoteDataSource = remoteDataSource,
                    modifier = Modifier.padding(innerPadding),
                    onOpenHome = {
                        showFirstRunProfileComplete = false
                        navController.navigate(TopLevelDestination.HOME.route) {
                            popUpTo(navController.graph.findStartDestination().id) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    },
                    onOpenCharts = {
                        showFirstRunProfileComplete = false
                        navController.navigate(TopLevelDestination.CHARTS.route) {
                            popUpTo(navController.graph.findStartDestination().id) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    },
                    onDismiss = {
                        showFirstRunProfileComplete = false
                    },
                )
            }
        }
    }
}

@Composable
private fun AstroNavHost(
    navController: NavHostController,
    innerPadding: PaddingValues,
    profiles: List<AppProfile>,
    selectedProfile: AppProfile?,
    profileRepository: ProfileRepository,
    habitRepository: HabitRepository,
    journalRepository: JournalRepository,
    preferencesStore: AppPreferencesStore,
    remoteDataSource: AstroRemoteDataSource,
    snackbarHostState: SnackbarHostState,
    showFirstRunPrompt: Boolean,
    onFirstProfileCreated: () -> Unit,
) {
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    val pushRegistrationManager = remember { PushRegistrationManager(context, preferencesStore, remoteDataSource) }
    val hideSensitiveDetailsEnabled by preferencesStore.hideSensitiveDetailsEnabled.collectAsStateWithLifecycle(initialValue = false)
    val personalModeEnabled by preferencesStore.personalModeEnabled.collectAsStateWithLifecycle(initialValue = com.astromeric.android.BuildConfig.PERSONAL_MODE)
    val authAccessToken by preferencesStore.authAccessToken.collectAsStateWithLifecycle(initialValue = "")
    val authUserEmail by preferencesStore.authUserEmail.collectAsStateWithLifecycle(initialValue = "")
    val effectiveAuthAccessToken = if (personalModeEnabled) "" else authAccessToken
    val accountSyncEnabled = !personalModeEnabled && authAccessToken.isNotBlank()
    var selectedLesson by remember { mutableStateOf<com.astromeric.android.core.model.LearningModuleData?>(null) }

    NavHost(
        navController = navController,
        startDestination = TopLevelDestination.HOME.route,
        modifier = Modifier.padding(innerPadding),
    ) {
        composable(TopLevelDestination.HOME.route) {
            HomeScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                habitRepository = habitRepository,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenTools = {
                    navController.navigate(TopLevelDestination.TOOLS.route) {
                        launchSingleTop = true
                    }
                },
                onOpenCharts = {
                    navController.navigate(TopLevelDestination.CHARTS.route) {
                        launchSingleTop = true
                    }
                },
                onCreateProfile = {
                    navController.navigate(profileEditorRoute()) {
                        launchSingleTop = true
                    }
                },
                onOpenWeeklyVibe = {
                    navController.navigate(WeeklyVibeRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenReading = {
                    navController.navigate(ReadingRoute) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(ExploreRoute) {
            ExploreScreen(
                selectedProfile = selectedProfile,
                preferencesStore = preferencesStore,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenLearn = {
                    navController.navigate(LearnRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenYearAhead = {
                    navController.navigate(YearAheadRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenRelationships = {
                    navController.navigate(RelationshipsRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenTools = {
                    navController.navigate(TopLevelDestination.TOOLS.route) {
                        launchSingleTop = true
                    }
                },
                onOpenCharts = {
                    navController.navigate(TopLevelDestination.CHARTS.route) {
                        launchSingleTop = true
                    }
                },
                onOpenHabits = {
                    navController.navigate(HabitsRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenJournal = {
                    navController.navigate(JournalRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
                onShowMessage = { message ->
                    scope.launch {
                        snackbarHostState.showSnackbar(message)
                    }
                },
            )
        }
        composable(LearnRoute) {
            LearnScreen(
                selectedProfile = selectedProfile,
                preferencesStore = preferencesStore,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenLesson = { module ->
                    selectedLesson = module
                    navController.navigate(LessonDetailRoute) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(RelationshipsRoute) {
            RelationshipsScreen(
                profiles = profiles,
                selectedProfile = selectedProfile,
                preferencesStore = preferencesStore,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenFriends = {
                    navController.navigate(FriendsRoute) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(TemporalMatrixRoute) {
            TemporalMatrixScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(TimingAdvisorRoute) {
            TimingAdvisorScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onBack = { navController.popBackStack() },
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(MoonPhaseRoute) {
            MoonPhaseScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            )
        }
        composable(YearAheadRoute) {
            YearAheadScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                authAccessToken = effectiveAuthAccessToken,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(LifePhaseRoute) {
            YearAheadScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                authAccessToken = effectiveAuthAccessToken,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(BirthstonesRoute) {
            BirthstonesScreen(
                selectedProfile = selectedProfile,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(ReadingRoute) {
            ReadingScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onBack = { navController.popBackStack() },
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(WeeklyVibeRoute) {
            WeeklyVibeScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onBack = { navController.popBackStack() },
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(DailyFeaturesRoute) {
            DailyFeaturesScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onBack = { navController.popBackStack() },
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(MoonEventsRoute) {
            MoonEventsScreen(
                remoteDataSource = remoteDataSource,
                onBack = { navController.popBackStack() },
            )
        }
        composable(AffirmationRoute) {
            AffirmationScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onBack = { navController.popBackStack() },
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(OracleRoute) {
            OracleScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onBack = { navController.popBackStack() },
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(TarotRoute) {
            TarotScreen(
                remoteDataSource = remoteDataSource,
                onBack = { navController.popBackStack() },
            )
        }
        composable(FriendsRoute) {
            FriendsScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                onBack = { navController.popBackStack() },
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(LessonDetailRoute) {
            val module = selectedLesson
            if (module != null) {
                val completedIds by preferencesStore.completedLearningModuleIds.collectAsStateWithLifecycle(initialValue = emptySet())
                LessonDetailScreen(
                    module = module,
                    isCompleted = completedIds.contains(module.id),
                    onToggleCompleted = {
                        scope.launch {
                            preferencesStore.setLearningModuleCompleted(
                                moduleId = module.id,
                                completed = !completedIds.contains(module.id),
                            )
                        }
                    },
                    onBack = { navController.popBackStack() },
                )
            } else {
                navController.popBackStack()
            }
        }
        composable(TopLevelDestination.TOOLS.route) {
            ToolsScreen(
                selectedProfile = selectedProfile,
                preferencesStore = preferencesStore,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenRelationships = {
                    navController.navigate(RelationshipsRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenLearn = {
                    navController.navigate(LearnRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenExplore = {
                    navController.navigate(ExploreRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenMoon = {
                    navController.navigate(MoonPhaseRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenTimingAdvisor = {
                    navController.navigate(TimingAdvisorRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenTemporalMatrix = {
                    navController.navigate(TemporalMatrixRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenYearAhead = {
                    navController.navigate(YearAheadRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenBirthstones = {
                    navController.navigate(BirthstonesRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenDailyFeatures = {
                    navController.navigate(DailyFeaturesRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenMoonEvents = {
                    navController.navigate(MoonEventsRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenAffirmation = {
                    navController.navigate(AffirmationRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenOracle = {
                    navController.navigate(OracleRoute) {
                        launchSingleTop = true
                    }
                },
                onOpenTarot = {
                    navController.navigate(TarotRoute) {
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(JournalRoute) {
            JournalScreen(
                selectedProfile = selectedProfile,
                journalRepository = journalRepository,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
                onShowMessage = { message ->
                    scope.launch {
                        snackbarHostState.showSnackbar(message)
                    }
                },
            )
        }
        composable(CosmicGuideRoute) {
            CosmicGuideScreen(
                selectedProfile = selectedProfile,
                remoteDataSource = remoteDataSource,
                preferencesStore = preferencesStore,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
                onOpenPrivacy = {
                    navController.navigate(PrivacyRoute) {
                        launchSingleTop = true
                    }
                },
                onShowMessage = { message ->
                    scope.launch {
                        snackbarHostState.showSnackbar(message)
                    }
                },
            )
        }
        composable(HabitsRoute) {
            HabitsScreen(
                selectedProfile = selectedProfile,
                habitRepository = habitRepository,
                remoteDataSource = remoteDataSource,
                hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
                onOpenProfile = {
                    navController.navigate(TopLevelDestination.PROFILE.route) {
                        launchSingleTop = true
                    }
                },
                onShowMessage = { message ->
                    scope.launch {
                        snackbarHostState.showSnackbar(message)
                    }
                },
            )
        }
        chartsGraph(
            navController = navController,
            profiles = profiles,
            selectedProfile = selectedProfile,
            remoteDataSource = remoteDataSource,
            effectiveAuthAccessToken = effectiveAuthAccessToken,
            hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            scope = scope,
            snackbarHostState = snackbarHostState,
        )
        profileGraph(
            navController = navController,
            profiles = profiles,
            selectedProfile = selectedProfile,
            preferencesStore = preferencesStore,
            profileRepository = profileRepository,
            remoteDataSource = remoteDataSource,
            pushRegistrationManager = pushRegistrationManager,
            hideSensitiveDetailsEnabled = hideSensitiveDetailsEnabled,
            personalModeEnabled = personalModeEnabled,
            accountSyncEnabled = accountSyncEnabled,
            authUserEmail = authUserEmail,
            showFirstRunPrompt = showFirstRunPrompt,
            scope = scope,
            snackbarHostState = snackbarHostState,
            onFirstProfileCreated = onFirstProfileCreated,
        )
    }
}


