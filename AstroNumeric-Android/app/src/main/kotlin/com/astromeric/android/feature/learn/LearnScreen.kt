package com.astromeric.android.feature.learn

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import com.astromeric.android.core.model.LearningModuleData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PremiumHeroCard
import kotlinx.coroutines.launch

@Composable
fun LearnScreen(
    selectedProfile: AppProfile?,
    preferencesStore: AppPreferencesStore,
    remoteDataSource: AstroRemoteDataSource,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenLesson: (LearningModuleData) -> Unit = {},
    modifier: Modifier = Modifier,
) {
    val scope = rememberCoroutineScope()
    val completedLearningModuleIds by preferencesStore.completedLearningModuleIds.collectAsStateWithLifecycle(initialValue = emptySet())
    var searchQuery by remember { mutableStateOf("") }
    val learningContentState = rememberLearningContentState(
        selectedProfile = selectedProfile,
        remoteDataSource = remoteDataSource,
    )

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumHeroCard(
            eyebrow = "Learn",
            title = "Learning Library",
            body = "Use structured lessons, glossary support, and sign-based orientation without routing back through Tools.",
            chips = selectedProfile?.let { profile ->
                listOf(
                    "Active profile: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)} · ${profile.dataQuality.label}",
                )
            }.orEmpty(),
        )

        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            label = { Text("Search lessons and glossary") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
        )

        LearningFeed(
            state = learningContentState,
            completedLearningModuleIds = completedLearningModuleIds,
            searchQuery = searchQuery,
            onToggleCompleted = { moduleId, completed ->
                scope.launch {
                    preferencesStore.setLearningModuleCompleted(
                        moduleId = moduleId,
                        completed = completed,
                    )
                }
            },
            onOpenLesson = onOpenLesson,
            glossaryLimit = 8,
        )
    }
}