package com.astromeric.android.feature.learn

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.GlossaryEntryData
import com.astromeric.android.core.model.LearningModuleData
import com.astromeric.android.core.model.ZodiacGuidanceData
import com.astromeric.android.core.ui.PremiumBentoCard
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumEmptyStateCard
import com.astromeric.android.core.ui.PremiumLoadingCard
import com.astromeric.android.core.ui.PremiumSectionHeader
import com.astromeric.android.core.ui.PremiumStatusCard
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

data class LearningContentState(
    val isLoading: Boolean,
    val error: String?,
    val learningModules: List<LearningModuleData>,
    val glossaryEntries: List<GlossaryEntryData>,
    val zodiacGuidance: ZodiacGuidanceData?,
)

@Composable
fun rememberLearningContentState(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
): LearningContentState {
    var learningModules by remember { mutableStateOf<List<LearningModuleData>>(emptyList()) }
    var glossaryEntries by remember { mutableStateOf<List<GlossaryEntryData>>(emptyList()) }
    var zodiacGuidance by remember(selectedProfile?.id) { mutableStateOf<ZodiacGuidanceData?>(null) }
    var learningError by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var isLearningLoading by remember(selectedProfile?.id) { mutableStateOf(false) }

    LaunchedEffect(selectedProfile?.id) {
        isLearningLoading = true
        learningError = null

        coroutineScope {
            val modulesRequest = async { remoteDataSource.fetchLearningModules() }
            val glossaryRequest = async { remoteDataSource.fetchGlossaryEntries() }
            val zodiacRequest = async { selectedProfile?.let { remoteDataSource.fetchZodiacGuidance(it) } }

            learningModules = modulesRequest.await()
                .onFailure { learningError = it.message ?: "Learning modules could not be loaded." }
                .getOrDefault(emptyList())

            glossaryEntries = glossaryRequest.await()
                .onFailure { learningError = learningError ?: it.message ?: "Glossary could not be loaded." }
                .getOrDefault(emptyList())

            zodiacGuidance = zodiacRequest.await()
                ?.onFailure { learningError = learningError ?: it.message ?: "Zodiac guidance could not be loaded." }
                ?.getOrNull()
        }

        isLearningLoading = false
    }

    return LearningContentState(
        isLoading = isLearningLoading,
        error = learningError,
        learningModules = learningModules,
        glossaryEntries = glossaryEntries,
        zodiacGuidance = zodiacGuidance,
    )
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun LearningFeed(
    state: LearningContentState,
    completedLearningModuleIds: Set<String>,
    searchQuery: String,
    onToggleCompleted: (String, Boolean) -> Unit,
    onOpenLesson: (LearningModuleData) -> Unit = {},
    actionButtonLabel: String? = null,
    onActionClick: (() -> Unit)? = null,
    moduleLimit: Int? = null,
    glossaryLimit: Int? = null,
) {
    val filteredLearningModules = state.learningModules.filter { module ->
        searchQuery.isBlank() ||
            module.title.contains(searchQuery, ignoreCase = true) ||
            module.description.contains(searchQuery, ignoreCase = true) ||
            module.keywords.any { keyword -> keyword.contains(searchQuery, ignoreCase = true) }
    }
    val filteredGlossaryEntries = state.glossaryEntries.filter { entry ->
        searchQuery.isBlank() ||
            entry.term.contains(searchQuery, ignoreCase = true) ||
            entry.definition.contains(searchQuery, ignoreCase = true) ||
            entry.relatedTerms.any { term -> term.contains(searchQuery, ignoreCase = true) }
    }
    val learningTrackSummaries = state.learningModules
        .groupBy { it.category.ifBlank { "general" } }
        .entries
        .sortedByDescending { it.value.size }
        .take(4)
        .map { (category, modules) ->
            LearningTrackSummary(
                title = category.toDisplayLabel(),
                completedCount = modules.count { completedLearningModuleIds.contains(it.id) },
                lessonCount = modules.size,
            )
        }
    val completedCount = state.learningModules.count { completedLearningModuleIds.contains(it.id) }
    val visibleModules = moduleLimit?.let { filteredLearningModules.take(it) } ?: filteredLearningModules
    val visibleGlossaryEntries = glossaryLimit?.let { filteredGlossaryEntries.take(it) } ?: filteredGlossaryEntries

    PremiumContentCard(
        title = "Learning tracks",
        body = "Use structured lessons when you want skill-building instead of a quick lookup.",
    ) {
        if (state.learningModules.isNotEmpty()) {
            AssistChip(
                onClick = {},
                label = { Text("$completedCount/${state.learningModules.size} completed") },
            )
        }

        if (learningTrackSummaries.isNotEmpty()) {
            FlowRow(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                learningTrackSummaries.forEach { track ->
                    PremiumBentoCard(
                        title = track.title,
                        body = "${track.completedCount}/${track.lessonCount} complete",
                        modifier = Modifier.fillMaxWidth(0.48f),
                        badge = "Track",
                    )
                }
            }
        }

        if (actionButtonLabel != null && onActionClick != null) {
            Button(onClick = onActionClick) {
                Text(actionButtonLabel)
            }
        }
    }

    val hasNoLearningContent = state.learningModules.isEmpty() && state.glossaryEntries.isEmpty() && state.zodiacGuidance == null
    if (state.isLoading && hasNoLearningContent) {
        PremiumLoadingCard(title = "Loading learning content")
    } else if (state.error != null && hasNoLearningContent) {
        PremiumStatusCard(
            title = "Learning unavailable",
            message = state.error,
            isError = true,
        )
    }

    state.zodiacGuidance?.let { guidance ->
        PremiumContentCard(
            title = "${guidance.sign.replaceFirstChar { it.uppercase() }} guide",
            body = guidance.guidance,
            footer = if (guidance.characteristics.isNotEmpty()) {
                "Traits: ${guidance.characteristics.take(4).joinToString()}"
            } else {
                null
            },
        ) {
            Text(
                text = "${guidance.element} element · ${guidance.rulingPlanet} rules",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }

    if (visibleModules.isNotEmpty()) {
        PremiumContentCard {
            PremiumSectionHeader(
                title = "Modules",
                subtitle = "Continue lessons or mark what you have completed.",
            )
            visibleModules.forEach { module ->
                LearningModuleRow(
                    module = module,
                    isCompleted = completedLearningModuleIds.contains(module.id),
                    onToggleCompleted = {
                        onToggleCompleted(module.id, !completedLearningModuleIds.contains(module.id))
                    },
                    onOpen = { onOpenLesson(module) },
                )
            }
        }
    }

    if (visibleGlossaryEntries.isNotEmpty()) {
        PremiumContentCard {
            PremiumSectionHeader(
                title = "Glossary",
                subtitle = "Definitions for language that appears across readings and tools.",
            )
            visibleGlossaryEntries.forEach { entry ->
                LearningGlossaryRow(entry = entry)
            }
        }
    }

    if (!state.isLoading && state.error == null && hasNoLearningContent) {
        PremiumEmptyStateCard(
            title = "No learning content yet",
            message = "Learning content has not loaded yet.",
        )
    }
}

@Composable
private fun LearningModuleRow(
    module: LearningModuleData,
    isCompleted: Boolean,
    onToggleCompleted: () -> Unit,
    onOpen: () -> Unit = {},
) {
    PremiumContentCard(
        title = module.title,
        body = module.description,
        footer = if (module.keywords.isNotEmpty()) {
            "Keywords: ${module.keywords.take(4).joinToString()}"
        } else {
            null
        },
    ) {
        Text(
            text = "${module.category.toDisplayLabel()} · ${module.difficulty.toDisplayLabel()} · ${module.durationMinutes} min",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Button(onClick = onToggleCompleted) {
            Text(if (isCompleted) "Completed" else "Mark complete")
        }
        if (module.content.isNotBlank()) {
            androidx.compose.material3.TextButton(onClick = onOpen) {
                Text("Open Lesson")
            }
        }
    }
}

@Composable
private fun LearningGlossaryRow(entry: GlossaryEntryData) {
    PremiumContentCard(
        title = entry.term,
        body = entry.definition,
        footer = entry.usageExample,
    )
}

private data class LearningTrackSummary(
    val title: String,
    val completedCount: Int,
    val lessonCount: Int,
)

private fun String.toDisplayLabel(): String =
    replace('_', ' ')
        .replace('-', ' ')
        .split(' ')
        .filter { it.isNotBlank() }
        .joinToString(" ") { word -> word.replaceFirstChar { it.uppercase() } }
