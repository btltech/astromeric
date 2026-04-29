package com.astromeric.android.navigation

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
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
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.local.NatalChartCacheStore
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.core.data.repository.loadNatalChartWithCacheFallback
import com.astromeric.android.core.ephemeris.LocalSwissEphemerisEngine
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.zodiacSignName
import com.astromeric.android.feature.profile.ProfileEditorScreen
import kotlinx.coroutines.launch

@Composable
internal fun FirstRunProfilePromptOverlay(
    onCreateProfile: () -> Unit,
    onExploreFirst: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp),
        contentAlignment = Alignment.Center,
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.72f)),
        )
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                Text(
                    text = "Create Your Private Cosmic Profile",
                    style = MaterialTheme.typography.headlineSmall,
                )
                Text(
                    text = "Add your birth details once so Home, Charts, and timing can feel personal instead of generic. You can also explore first and create it later from Profile.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                FirstRunProofPoint(
                    title = "Local-first by default",
                    detail = "Your first profile stays on this device unless you later choose account sync.",
                )
                FirstRunProofPoint(
                    title = "Chart and numerology together",
                    detail = "The same profile powers Charts, daily guidance, and timing tools.",
                )
                FirstRunProofPoint(
                    title = "Explore stays open",
                    detail = "You can skip this and browse the shell first, then create your profile when ready.",
                )
                Button(
                    onClick = onCreateProfile,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Create Profile")
                }
                TextButton(
                    onClick = onExploreFirst,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Explore First")
                }
            }
        }
    }
}

@Composable
private fun FirstRunProofPoint(
    title: String,
    detail: String,
) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleSmall,
        )
        Text(
            text = detail,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
internal fun FirstRunProfileCompleteOverlay(
    profile: AppProfile,
    remoteDataSource: AstroRemoteDataSource,
    onOpenHome: () -> Unit,
    onOpenCharts: () -> Unit,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val chartCacheStore = remember(context) { NatalChartCacheStore(context.applicationContext) }
    val localEphemerisEngine = remember(context) { LocalSwissEphemerisEngine.getInstance(context.applicationContext) }
    var moonSign by remember(profile.id) { mutableStateOf<String?>(null) }
    var risingSign by remember(profile.id) { mutableStateOf<String?>(null) }
    val sunSign = profile.zodiacSignName()?.replaceFirstChar { it.uppercase() }
    val lifePathNumber = remember(profile.id) { profile.lifePathNumber() }

    LaunchedEffect(profile.id) {
        if (!profile.canRequestNatalChart) {
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

    Box(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp),
        contentAlignment = Alignment.Center,
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.72f)),
        )
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                Text(
                    text = "Your Profile Is Ready",
                    style = MaterialTheme.typography.headlineSmall,
                )
                Text(
                    text = "AstroNumeric can now combine your chart, core numbers, and daily timing into personal guidance.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                FirstRunSignalRow(
                    title = sunSign?.let { "$it Sun" } ?: "Sun Sign Syncing",
                    detail = sunSign?.let { zodiacDescriptor(it) } ?: "Your core chart signature starts with your birth date.",
                )
                FirstRunSignalRow(
                    title = moonSign?.let { "$it Moon" } ?: "Moon Sign Syncing",
                    detail = if (moonSign == null) {
                        "Your emotional rhythm will appear after chart sync."
                    } else {
                        buildString {
                            append("Emotional needs and instinctive responses")
                            if (!risingSign.isNullOrBlank()) {
                                append(" · Rising ")
                                append(risingSign)
                            }
                        }
                    },
                )
                FirstRunSignalRow(
                    title = lifePathNumber?.let { "Life Path $it" } ?: "Life Path Syncing",
                    detail = lifePathNumber?.let(::lifePathDetail) ?: "Your core numerology theme will appear from your birth date.",
                )
                FirstRunSignalRow(
                    title = profile.dataQuality.label,
                    detail = profile.dataQuality.description,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Button(
                        onClick = onOpenHome,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text("See Daily Guide")
                    }
                    Button(
                        onClick = onOpenCharts,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text("Open Chart")
                    }
                }
                TextButton(
                    onClick = onDismiss,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Continue")
                }
            }
        }
    }
}

@Composable
private fun FirstRunSignalRow(
    title: String,
    detail: String,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
            )
            Text(
                text = detail,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

private fun AppProfile.lifePathNumber(): Int? = runCatching {
    reduceLifePathNumber(dateOfBirth.filter(Char::isDigit).sumOf(Char::digitToInt))
}.getOrNull()

private fun reduceLifePathNumber(value: Int): Int {
    var current = value
    while (current !in setOf(11, 22, 33) && current > 9) {
        current = current.toString().sumOf(Char::digitToInt)
    }
    return current
}

private fun lifePathDetail(number: Int): String = when (number) {
    1 -> "Initiation, independence, and fresh starts"
    2 -> "Partnership, sensitivity, and careful timing"
    3 -> "Expression, creativity, and social flow"
    4 -> "Structure, discipline, and steady building"
    5 -> "Change, movement, and adaptive choices"
    6 -> "Care, responsibility, and relationship repair"
    7 -> "Reflection, study, and inner truth"
    8 -> "Power, resources, and long-range decisions"
    9 -> "Completion, release, and wider perspective"
    11 -> "Intuition, signal sensitivity, and inspiration"
    22 -> "Large-scale building and practical vision"
    33 -> "Service, teaching, and compassionate leadership"
    else -> "A core numerology theme for timing and reflection"
}

private fun zodiacDescriptor(sign: String): String = when (sign.lowercase()) {
    "aries" -> "Fire element, cardinal mode"
    "taurus" -> "Earth element, fixed mode"
    "gemini" -> "Air element, mutable mode"
    "cancer" -> "Water element, cardinal mode"
    "leo" -> "Fire element, fixed mode"
    "virgo" -> "Earth element, mutable mode"
    "libra" -> "Air element, cardinal mode"
    "scorpio" -> "Water element, fixed mode"
    "sagittarius" -> "Fire element, mutable mode"
    "capricorn" -> "Earth element, cardinal mode"
    "aquarius" -> "Air element, fixed mode"
    "pisces" -> "Water element, mutable mode"
    else -> "Your core chart signature starts with your birth date."
}

@Composable
fun OnboardingScaffold(
    profileRepository: ProfileRepository,
    preferencesStore: AppPreferencesStore,
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = "Create your private cosmic profile",
            style = MaterialTheme.typography.headlineMedium,
        )
        Text(
            text = "Start with the same local-first profile contract used on iOS so charts, numerology, and timing can stay aligned.",
            style = MaterialTheme.typography.bodyLarge,
            modifier = Modifier
                .padding(top = 12.dp, bottom = 24.dp)
                .fillMaxWidth(),
        )
        TextButton(
            onClick = {
                scope.launch {
                    preferencesStore.setInitialOnboardingCompleted(true)
                }
            },
        ) {
            Text("Skip for now")
        }
        ProfileEditorScreen(
            existingProfile = null,
            onSaved = {
                scope.launch {
                    preferencesStore.setInitialOnboardingCompleted(true)
                }
            },
            onCancel = {},
            profileRepository = profileRepository,
            modifier = Modifier.fillMaxWidth(),
            isOnboarding = true,
            scrollable = false,
        )
    }
}
