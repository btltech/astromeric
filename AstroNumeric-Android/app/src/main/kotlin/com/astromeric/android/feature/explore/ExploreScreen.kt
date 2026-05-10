package com.astromeric.android.feature.explore

import androidx.annotation.StringRes
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.R
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

private enum class ExploreCategory(@StringRes val labelRes: Int) {
    TOOLS(R.string.explore_category_tools),
    LEARN(R.string.explore_category_learn),
    HABITS(R.string.explore_category_habits),
    RELATIONSHIPS(R.string.explore_category_relationships),
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
    val context = LocalContext.current
    val completedLearningModuleIds by preferencesStore.completedLearningModuleIds.collectAsStateWithLifecycle(initialValue = emptySet())
    var selectedCategory by remember { mutableStateOf(ExploreCategory.TOOLS) }
    var searchQuery by remember { mutableStateOf("") }
    val learningContentState = rememberLearningContentState(
        selectedProfile = selectedProfile,
        remoteDataSource = remoteDataSource,
    )

    val items = remember(completedLearningModuleIds.size, context) {
        listOf(
            ExploreItem(
                title = context.getString(R.string.explore_oracle_title),
                description = context.getString(R.string.explore_oracle_body),
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.TOOLS,
                actionLabel = context.getString(R.string.action_open_tools),
                provenance = ToolProvenance.HYBRID,
            ),
            ExploreItem(
                title = context.getString(R.string.explore_timing_title),
                description = context.getString(R.string.explore_timing_body),
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.TOOLS,
                actionLabel = context.getString(R.string.action_open_tools),
                provenance = ToolProvenance.CALCULATED,
            ),
            ExploreItem(
                title = context.getString(R.string.explore_year_ahead_title),
                description = context.getString(R.string.explore_year_ahead_body),
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.YEAR_AHEAD,
                actionLabel = context.getString(R.string.charts_action_open_year_ahead),
                provenance = ToolProvenance.CALCULATED,
            ),
            ExploreItem(
                title = context.getString(R.string.explore_life_phase_title),
                description = context.getString(R.string.explore_life_phase_body),
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.YEAR_AHEAD,
                actionLabel = context.getString(R.string.charts_action_open_year_ahead),
                provenance = ToolProvenance.HYBRID,
            ),
            ExploreItem(
                title = context.getString(R.string.explore_moon_daily_guide_title),
                description = context.getString(R.string.explore_moon_daily_guide_body),
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.TOOLS,
                actionLabel = context.getString(R.string.action_open_tools),
                provenance = ToolProvenance.CALCULATED,
            ),
            ExploreItem(
                title = context.getString(R.string.explore_chart_reading_title),
                description = context.getString(R.string.explore_chart_reading_body),
                category = ExploreCategory.TOOLS,
                destination = ExploreDestination.CHARTS,
                actionLabel = context.getString(R.string.action_open_charts),
                provenance = ToolProvenance.CALCULATED,
            ),
            ExploreItem(
                title = context.getString(R.string.explore_learning_modules_title),
                description = context.getString(R.string.explore_learning_modules_body),
                category = ExploreCategory.LEARN,
                destination = ExploreDestination.LEARN,
                actionLabel = context.getString(R.string.action_open_learn),
                note = context.getString(R.string.explore_learning_modules_note, completedLearningModuleIds.size),
            ),
            ExploreItem(
                title = context.getString(R.string.explore_glossary_title),
                description = context.getString(R.string.explore_glossary_body),
                category = ExploreCategory.LEARN,
                destination = ExploreDestination.LEARN,
                actionLabel = context.getString(R.string.action_open_learn),
            ),
            ExploreItem(
                title = context.getString(R.string.explore_zodiac_guidance_title),
                description = context.getString(R.string.explore_zodiac_guidance_body),
                category = ExploreCategory.LEARN,
                destination = ExploreDestination.LEARN,
                actionLabel = context.getString(R.string.action_open_learn),
            ),
            ExploreItem(
                title = context.getString(R.string.explore_lunar_habits_title),
                description = context.getString(R.string.explore_lunar_habits_body),
                category = ExploreCategory.HABITS,
                destination = ExploreDestination.HABITS,
                actionLabel = context.getString(R.string.action_open_habits),
                note = context.getString(R.string.explore_lunar_habits_note),
            ),
            ExploreItem(
                title = context.getString(R.string.explore_journal_loop_title),
                description = context.getString(R.string.explore_journal_loop_body),
                category = ExploreCategory.HABITS,
                destination = ExploreDestination.JOURNAL,
                actionLabel = context.getString(R.string.action_open_journal),
                note = context.getString(R.string.explore_journal_loop_note),
            ),
            ExploreItem(
                title = context.getString(R.string.explore_cosmic_circle_title),
                description = context.getString(R.string.explore_cosmic_circle_body),
                category = ExploreCategory.RELATIONSHIPS,
                destination = ExploreDestination.RELATIONSHIPS,
                actionLabel = context.getString(R.string.action_open_relationships),
            ),
            ExploreItem(
                title = context.getString(R.string.explore_compatibility_title),
                description = context.getString(R.string.explore_compatibility_body),
                category = ExploreCategory.RELATIONSHIPS,
                destination = ExploreDestination.RELATIONSHIPS,
                actionLabel = context.getString(R.string.action_open_relationships),
            ),
            ExploreItem(
                title = context.getString(R.string.explore_saved_relationship_history_title),
                description = context.getString(R.string.explore_saved_relationship_history_body),
                category = ExploreCategory.RELATIONSHIPS,
                destination = ExploreDestination.RELATIONSHIPS,
                actionLabel = context.getString(R.string.action_open_relationships),
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
            eyebrow = stringResource(R.string.explore_hero_eyebrow),
            title = stringResource(R.string.explore_hero_title),
            body = stringResource(R.string.explore_hero_body),
            chips = selectedProfile?.let { profile ->
                listOf(
                    stringResource(
                        R.string.explore_active_profile_chip,
                        profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                        profile.dataQuality.label,
                    ),
                )
            }.orEmpty(),
        ) {
            if (selectedProfile == null) {
                Text(
                    text = stringResource(R.string.explore_no_profile_hint),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            label = { Text(stringResource(R.string.explore_search_label)) },
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
                    label = { Text(stringResource(category.labelRes)) },
                )
            }
        }

        PremiumSectionHeader(
            title = stringResource(selectedCategory.labelRes),
            subtitle = sectionSubtitle(context, selectedCategory),
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
                actionButtonLabel = stringResource(R.string.explore_browse_all_lessons),
                onActionClick = onOpenLearn,
                moduleLimit = 3,
                glossaryLimit = 3,
            )
        } else if (filteredItems.isEmpty()) {
            PremiumEmptyStateCard(
                title = stringResource(R.string.explore_no_matches_title),
                message = stringResource(R.string.explore_no_matches_message),
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
                            ExploreDestination.UPCOMING -> onShowMessage(item.note ?: context.getString(R.string.explore_upcoming_staged_message))
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

private fun sectionSubtitle(context: android.content.Context, category: ExploreCategory): String = when (category) {
    ExploreCategory.TOOLS -> context.getString(R.string.explore_tools_subtitle)
    ExploreCategory.LEARN -> context.getString(R.string.explore_learn_subtitle)
    ExploreCategory.HABITS -> context.getString(R.string.explore_habits_subtitle)
    ExploreCategory.RELATIONSHIPS -> context.getString(R.string.explore_relationships_subtitle)
}