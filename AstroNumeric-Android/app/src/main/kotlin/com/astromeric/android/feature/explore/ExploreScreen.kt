package com.astromeric.android.feature.explore

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.ToolProvenance
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PremiumAction
import com.astromeric.android.core.ui.PremiumActionRow
import com.astromeric.android.core.ui.PremiumChipGroup
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumEmptyStateCard
import com.astromeric.android.core.ui.PremiumHeroCard
import com.astromeric.android.core.ui.PremiumSectionHeader
import com.astromeric.android.feature.learn.LearningFeed
import com.astromeric.android.feature.learn.rememberLearningContentState
import kotlinx.coroutines.launch

private enum class ExploreCategory(val label: String) {
    TOOLS("Tools"),
    LEARN("Learn"),
    HABITS("Habits"),
    RELATIONSHIPS("Relationships"),
}

private enum class ExploreDestination {
    LEARN,
    YEAR_AHEAD,
    RELATIONSHIPS,
    TOOLS,
    CHARTS,
    HABITS,
    JOURNAL,
    PROFILE,
    UPCOMING,
}

private data class ExploreItem(
    val title: String,
    val description: String,
    val category: ExploreCategory,
    val destination: ExploreDestination,
    val actionLabel: String,
    val provenance: ToolProvenance? = null,
    val note: String? = null,
)

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun ExploreScreen(
    selectedProfile: AppProfile?,
    preferencesStore: AppPreferencesStore,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenLearn: () -> Unit,
    onOpenYearAhead: () -> Unit,
    onOpenRelationships: () -> Unit,
    onOpenTools: () -> Unit,
    onOpenCharts: () -> Unit,
    onOpenHabits: () -> Unit,
    onOpenJournal: () -> Unit,
    onOpenProfile: () -> Unit,
    onShowMessage: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()
    val completedLearningModuleIds by preferencesStore.completedLearningModuleIds.collectAsStateWithLifecycle(initialValue = emptySet())
    var selectedCategory by remember { mutableStateOf(ExploreCategory.TOOLS) }
    var searchQuery by remember { mutableStateOf("") }
    val learningContentState = rememberLearningContentState(
        selectedProfile = selectedProfile,
        remoteDataSource = remoteDataSource,
    )

    val items = remember(completedLearningModuleIds.size) {
        listOf(
            ExploreItem(
                title = "Oracle",
                description = "Yes or no guidance using your current profile context and daily signal.",
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.TOOLS,
                actionLabel = "Open Tools",
                provenance = ToolProvenance.HYBRID,
            ),
            ExploreItem(
                title = "Timing",
                description = "Choose the best window for a date, interview, meeting, or launch.",
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.TOOLS,
                actionLabel = "Open Tools",
                provenance = ToolProvenance.CALCULATED,
            ),
            ExploreItem(
                title = "Year Ahead",
                description = "Long-range forecast from your solar return and numerology cycle.",
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.YEAR_AHEAD,
                actionLabel = "Open Year Ahead",
                provenance = ToolProvenance.CALCULATED,
            ),
            ExploreItem(
                title = "Life Phase",
                description = "Your current cycle interpreted inside the fuller year-ahead forecast.",
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.YEAR_AHEAD,
                actionLabel = "Open Year Ahead",
                provenance = ToolProvenance.HYBRID,
            ),
            ExploreItem(
                title = "Moon + Daily Guide",
                description = "Read the current moon phase, daily guide, ritual weather, and supportive cues in one place.",
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.TOOLS,
                actionLabel = "Open Tools",
                provenance = ToolProvenance.CALCULATED,
            ),
            ExploreItem(
                title = "Chart Reading",
                description = "Jump to the chart screen when you want placements, houses, and aspects instead of daily guidance.",
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.CHARTS,
                actionLabel = "Open Charts",
                provenance = ToolProvenance.CALCULATED,
            ),
            ExploreItem(
                title = "Learning Modules",
                description = "Use structured lessons when you want guided understanding instead of quick lookup.",
                category = ExploreCategory.LEARN,
                destination = ExploreDestination.LEARN,
                actionLabel = "Open Learn",
                note = "${completedLearningModuleIds.size} modules completed locally",
            ),
            ExploreItem(
                title = "Glossary",
                description = "Open term definitions fast when a reading introduces language you want clarified.",
                category = ExploreCategory.LEARN,
                destination = ExploreDestination.LEARN,
                actionLabel = "Open Learn",
            ),
            ExploreItem(
                title = "Zodiac Guidance",
                description = "Start with your sign summary when you want a fast orientation layer before going deeper.",
                category = ExploreCategory.LEARN,
                destination = ExploreDestination.LEARN,
                actionLabel = "Open Learn",
            ),
            ExploreItem(
                title = "Lunar Habits",
                description = "Track practices that align with moon phases and reflection cycles.",
                category = ExploreCategory.HABITS,
                destination = ExploreDestination.HABITS,
                actionLabel = "Open Habits",
                note = "Habits now supports local-first tracking with backend sync attempts.",
            ),
            ExploreItem(
                title = "Journal Loop",
                description = "Capture outcomes against readings so the app becomes more useful over time.",
                category = ExploreCategory.HABITS,
                destination = ExploreDestination.JOURNAL,
                actionLabel = "Open Journal",
                note = "Journal now mirrors the local-first personal mode from iOS.",
            ),
            ExploreItem(
                title = "Cosmic Circle",
                description = "Manage your synced people and see who ranks strongest right now.",
                category = ExploreCategory.RELATIONSHIPS,
                destination = ExploreDestination.RELATIONSHIPS,
                actionLabel = "Open Relationships",
            ),
            ExploreItem(
                title = "Compatibility",
                description = "Compare either a saved profile or a manually entered second person.",
                category = ExploreCategory.RELATIONSHIPS,
                destination = ExploreDestination.RELATIONSHIPS,
                actionLabel = "Open Relationships",
            ),
            ExploreItem(
                title = "Saved Relationship History",
                description = "Review your local relationship history alongside timing, events, and phase guidance.",
                category = ExploreCategory.RELATIONSHIPS,
                destination = ExploreDestination.RELATIONSHIPS,
                actionLabel = "Open Relationships",
            ),
        )
    }

    val filteredItems = items.filter { item ->
        item.category == selectedCategory && (
            searchQuery.isBlank() ||
                item.title.contains(searchQuery, ignoreCase = true) ||
                item.description.contains(searchQuery, ignoreCase = true) ||
                item.note?.contains(searchQuery, ignoreCase = true) == true
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
            eyebrow = "Explore",
            title = "Explore Workspace",
            body = "Start with the category that matches whether you need a tool, lesson, practice, or relationship view.",
            chips = selectedProfile?.let { profile ->
                listOf(
                    "Active profile: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)} · ${profile.dataQuality.label}",
                )
            }.orEmpty(),
        ) {
            if (selectedProfile == null) {
                Text(
                    text = "Create a profile first so Explore can route you into personalized tools and learning.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            label = { Text("Search explore") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
        )

        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            ExploreCategory.entries.forEach { category ->
                FilterChip(
                    selected = selectedCategory == category,
                    onClick = { selectedCategory = category },
                    label = { Text(category.label) },
                )
            }
        }

        PremiumSectionHeader(
            title = selectedCategory.label,
            subtitle = sectionSubtitle(selectedCategory),
        )

        if (selectedCategory == ExploreCategory.LEARN) {
            LearningFeed(
                state = learningContentState,
                completedLearningModuleIds = completedLearningModuleIds,
                searchQuery = searchQuery,
                onToggleCompleted = { moduleId, completed ->
                    scope.launch {
                        preferencesStore.setLearningModuleCompleted(moduleId, completed)
                    }
                },
                actionButtonLabel = "Browse all lessons",
                onActionClick = onOpenLearn,
                moduleLimit = 3,
                glossaryLimit = 3,
            )
        } else if (filteredItems.isEmpty()) {
            PremiumEmptyStateCard(
                title = "No matches",
                message = "No curated items match this search yet.",
            )
        } else {
            filteredItems.forEach { item ->
                ExploreItemCard(
                    item = item,
                    onClick = {
                        when (item.destination) {
                            ExploreDestination.LEARN -> onOpenLearn()
                            ExploreDestination.YEAR_AHEAD -> onOpenYearAhead()
                            ExploreDestination.RELATIONSHIPS -> onOpenRelationships()
                            ExploreDestination.TOOLS -> onOpenTools()
                            ExploreDestination.CHARTS -> onOpenCharts()
                            ExploreDestination.HABITS -> onOpenHabits()
                            ExploreDestination.JOURNAL -> onOpenJournal()
                            ExploreDestination.PROFILE -> onOpenProfile()
                            ExploreDestination.UPCOMING -> onShowMessage(item.note ?: "This Android slice is staged next.")
                        }
                    },
                )
            }
        }
    }
}

@Composable
private fun ExploreItemCard(
    item: ExploreItem,
    onClick: () -> Unit,
) {
    PremiumContentCard(
        title = item.title,
        body = item.description,
        footer = item.note,
    ) {
        item.provenance?.let { provenance ->
            PremiumChipGroup(labels = listOf(provenance.label))
        }
        PremiumActionRow(
            actions = listOf(
                PremiumAction(
                    label = item.actionLabel,
                    onClick = onClick,
                    primary = true,
                ),
            ),
        )
    }
}

private fun sectionSubtitle(category: ExploreCategory): String = when (category) {
    ExploreCategory.TOOLS -> "Use Tools when you want to decide, interpret, or act on something concrete today."
    ExploreCategory.LEARN -> "Use Learn when you want structured understanding, glossary support, or sign-based orientation."
    ExploreCategory.HABITS -> "Use Habits when you want repeatable practice, lunar timing cues, and local-first completion tracking."
    ExploreCategory.RELATIONSHIPS -> "Use Relationships when you want live comparison, synced people, or timing context around connection."
}