package com.astromeric.android.feature.habits

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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.R
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.HabitRepository
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.LocalHabitData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.fallbackHabitCategories
import com.astromeric.android.core.model.fallbackLunarGuidance
import com.astromeric.android.core.model.normalizeMoonPhaseKey
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

private const val AllHabitCategories = "all"

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun HabitsScreen(
    selectedProfile: AppProfile?,
    habitRepository: HabitRepository,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenProfile: () -> Unit,
    onShowMessage: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()
    val habits by habitRepository.localHabits.collectAsStateWithLifecycle(initialValue = emptyList())
    val unknownCategoryLabel = stringResource(R.string.habits_unknown_category_label)
    val unknownCategoryDescription = stringResource(R.string.habits_unknown_category_description)
    val syncUnavailableMessage = stringResource(R.string.habits_sync_unavailable)
    val syncFailedRestoreMessage = stringResource(R.string.habits_sync_failed_restore)
    val savedSyncedMessage = stringResource(R.string.habits_saved_synced)
    val savedLocalOnlyMessage = stringResource(R.string.habits_saved_local_only)
    val removedLocalCacheMessage = stringResource(R.string.habits_removed_local_cache)
    val fallbackCategories = remember { fallbackHabitCategories() }
    val categories = remember(habits, unknownCategoryLabel, unknownCategoryDescription) {
        val knownIds = fallbackCategories.map { it.id }.toSet()
        fallbackCategories + habits
            .map { it.category }
            .distinct()
            .filterNot { it in knownIds }
            .map { category ->
                com.astromeric.android.core.model.LocalHabitCategoryData(
                    id = category,
                    name = category.replaceFirstChar { it.titlecase() },
                    emoji = unknownCategoryLabel,
                    description = unknownCategoryDescription,
                    bestPhases = emptyList(),
                    avoidPhases = emptyList(),
                )
            }
    }
    val defaultLunarGuidance = remember { fallbackLunarGuidance("waxing_crescent") }

    var selectedCategory by remember { mutableStateOf(AllHabitCategories) }
    var draftName by remember { mutableStateOf("") }
    var draftDescription by remember { mutableStateOf("") }
    var draftCategory by remember { mutableStateOf(fallbackCategories.first().id) }
    var isRefreshing by remember { mutableStateOf(false) }
    var isCreating by remember { mutableStateOf(false) }
    var activeMoonPhaseLabel by remember { mutableStateOf(defaultLunarGuidance.phaseName) }
    var lunarGuidance by remember { mutableStateOf(defaultLunarGuidance) }

    val visibleHabits = habits.filter { habit ->
        selectedCategory == AllHabitCategories || habit.category == selectedCategory
    }
    val suggestedHabit = visibleHabits.firstOrNull { habit ->
        !habit.isCompletedToday && habit.category in lunarGuidance.idealHabits
    } ?: visibleHabits.firstOrNull { habit -> !habit.isCompletedToday }
    val completedTodayCount = visibleHabits.count { it.isCompletedToday }
    val averageCompletionRate = visibleHabits
        .takeIf { it.isNotEmpty() }
        ?.map { it.completionRate }
        ?.average()
        ?.times(100)
        ?.roundToInt()
        ?: 0

    fun refreshHabits(showFailureMessage: Boolean) {
        scope.launch {
            isRefreshing = true
            val result = habitRepository.refreshHabits()
            if (result.isFailure && showFailureMessage) {
                onShowMessage(syncUnavailableMessage)
            }
            isRefreshing = false
        }
    }

    fun refreshMoonGuidance() {
        scope.launch {
            remoteDataSource.fetchMoonPhase()
                .onSuccess { moonPhase ->
                    activeMoonPhaseLabel = moonPhase.phase
                    lunarGuidance = fallbackLunarGuidance(normalizeMoonPhaseKey(moonPhase.phase))
                }
                .onFailure {
                    activeMoonPhaseLabel = lunarGuidance.phaseName
                }
        }
    }

    LaunchedEffect(Unit) {
        refreshHabits(showFailureMessage = false)
        refreshMoonGuidance()
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = stringResource(R.string.habits_title),
                    style = MaterialTheme.typography.headlineMedium,
                )
                Text(
                    text = stringResource(R.string.habits_hero_body),
                    style = MaterialTheme.typography.bodyMedium,
                )
                selectedProfile?.let { profile ->
                    AssistChip(
                        onClick = {},
                        label = {
                            Text(
                                stringResource(
                                    R.string.habits_active_profile,
                                    profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                                    profile.dataQuality.label,
                                ),
                            )
                        },
                    )
                } ?: Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = stringResource(R.string.habits_profile_context_body),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.weight(1f),
                    )
                    OutlinedButton(onClick = onOpenProfile) {
                        Text(stringResource(R.string.action_open_profile))
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
                    text = stringResource(R.string.habits_moon_guidance_title),
                    style = MaterialTheme.typography.titleMedium,
                )
                AssistChip(
                    onClick = {},
                    label = {
                        Text(
                            stringResource(
                                R.string.habits_moon_guidance_chip,
                                activeMoonPhaseLabel,
                                lunarGuidance.energy,
                            ),
                        )
                    },
                )
                Text(
                    text = lunarGuidance.theme,
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = stringResource(R.string.habits_best_for_format, lunarGuidance.bestFor.joinToString()),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = stringResource(R.string.habits_ideal_categories_format, lunarGuidance.idealHabits.joinToString()),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            MetricCard(
                title = stringResource(R.string.habits_metric_active),
                value = visibleHabits.size.toString(),
                modifier = Modifier.weight(1f),
            )
            MetricCard(
                title = stringResource(R.string.habits_done_today),
                value = completedTodayCount.toString(),
                modifier = Modifier.weight(1f),
            )
            MetricCard(
                title = stringResource(R.string.habits_metric_avg_rate),
                value = stringResource(R.string.habits_percent_value, averageCompletionRate),
                modifier = Modifier.weight(1f),
            )
        }

        suggestedHabit?.let { habit ->
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text = stringResource(R.string.habits_suggested_next_habit),
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = stringResource(R.string.habits_suggested_body, habit.name),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    Button(
                        onClick = {
                            scope.launch {
                                val result = habitRepository.toggleHabitCompletion(habit)
                                if (result.isFailure) {
                                    onShowMessage(syncFailedRestoreMessage)
                                }
                            }
                        },
                    ) {
                        Text(
                            if (habit.isCompletedToday) {
                                stringResource(R.string.habits_mark_undone)
                            } else {
                                stringResource(R.string.habits_mark_done)
                            },
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
                Text(
                    text = stringResource(R.string.habits_create_title),
                    style = MaterialTheme.typography.titleMedium,
                )
                OutlinedTextField(
                    value = draftName,
                    onValueChange = { draftName = it },
                    label = { Text(stringResource(R.string.habits_name_label)) },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                )
                OutlinedTextField(
                    value = draftDescription,
                    onValueChange = { draftDescription = it },
                    label = { Text(stringResource(R.string.habits_description_label)) },
                    modifier = Modifier.fillMaxWidth(),
                )
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    categories.forEach { category ->
                        FilterChip(
                            selected = draftCategory == category.id,
                            onClick = { draftCategory = category.id },
                            label = { Text(category.name) },
                        )
                    }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        enabled = draftName.isNotBlank() && !isCreating,
                        onClick = {
                            scope.launch {
                                isCreating = true
                                val result = habitRepository.createHabit(
                                    name = draftName,
                                    category = draftCategory,
                                    description = draftDescription,
                                )
                                isCreating = false
                                if (result.isSuccess) {
                                    draftName = ""
                                    draftDescription = ""
                                    onShowMessage(savedSyncedMessage)
                                } else {
                                    onShowMessage(savedLocalOnlyMessage)
                                }
                            }
                        },
                    ) {
                        Text(
                            if (isCreating) {
                                stringResource(R.string.habits_saving)
                            } else {
                                stringResource(R.string.habits_create_action)
                            },
                        )
                    }
                    OutlinedButton(
                        onClick = {
                            draftName = ""
                            draftDescription = ""
                        },
                    ) {
                        Text(stringResource(R.string.habits_clear))
                    }
                }
            }
        }

        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            FilterChip(
                selected = selectedCategory == AllHabitCategories,
                onClick = { selectedCategory = AllHabitCategories },
                label = { Text(stringResource(R.string.habits_filter_all)) },
            )
            categories.forEach { category ->
                FilterChip(
                    selected = selectedCategory == category.id,
                    onClick = { selectedCategory = category.id },
                    label = { Text(category.name) },
                )
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                enabled = !isRefreshing,
                onClick = {
                    refreshHabits(showFailureMessage = true)
                    refreshMoonGuidance()
                },
            ) {
                Text(
                    if (isRefreshing) {
                        stringResource(R.string.tools_refreshing)
                    } else {
                        stringResource(R.string.habits_refresh)
                    },
                )
            }
            Text(
                text = stringResource(R.string.habits_cache_note),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 12.dp),
            )
        }

        if (visibleHabits.isEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(
                    text = stringResource(R.string.habits_empty_state, lunarGuidance.phaseName),
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        } else {
            visibleHabits.forEach { habit ->
                HabitCard(
                    habit = habit,
                    onToggle = {
                        scope.launch {
                            val result = habitRepository.toggleHabitCompletion(habit)
                            if (result.isFailure) {
                                onShowMessage(syncFailedRestoreMessage)
                            }
                        }
                    },
                    onDelete = {
                        scope.launch {
                            habitRepository.deleteHabit(habit.id)
                            onShowMessage(removedLocalCacheMessage)
                        }
                    },
                )
            }
        }
    }
}

@Composable
private fun MetricCard(
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
private fun HabitCard(
    habit: LocalHabitData,
    onToggle: () -> Unit,
    onDelete: () -> Unit,
) {
    val completionPercent = (habit.completionRate * 100).roundToInt()

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
                        text = habit.name,
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = habit.category.replaceFirstChar { it.titlecase() },
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                AssistChip(
                    onClick = {},
                    label = {
                        Text(
                            if (habit.isCompletedToday) {
                                stringResource(R.string.habits_done_today)
                            } else {
                                stringResource(R.string.habits_open)
                            },
                        )
                    },
                )
            }

            if (habit.description.isNotBlank()) {
                Text(
                    text = habit.description,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }

            Text(
                text = stringResource(
                    R.string.habits_streak_summary,
                    habit.currentStreak,
                    habit.longestStreak,
                    completionPercent,
                ),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = onToggle) {
                    Text(
                        if (habit.isCompletedToday) {
                            stringResource(R.string.habits_undo_today)
                        } else {
                            stringResource(R.string.habits_mark_done)
                        },
                    )
                }
                OutlinedButton(onClick = onDelete) {
                    Text(stringResource(R.string.habits_remove))
                }
            }
        }
    }
}