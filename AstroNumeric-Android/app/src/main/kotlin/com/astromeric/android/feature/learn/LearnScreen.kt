package com.astromeric.android.feature.learn

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.MenuBook
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.astromeric.android.R
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.LearningModuleData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PremiumHeroCard
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
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
    var showGlossarySheet by remember { mutableStateOf(false) }
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
            eyebrow = stringResource(R.string.learn_eyebrow),
            title = stringResource(R.string.learn_title),
            body = stringResource(R.string.learn_body),
            chips = selectedProfile?.let { profile ->
                listOf(
                    stringResource(
                        R.string.learn_active_profile_chip,
                        profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                        profile.dataQuality.label,
                    ),
                )
            }.orEmpty(),
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                label = { Text(stringResource(R.string.learn_search_label)) },
                modifier = Modifier.weight(1f),
                singleLine = true,
            )
            OutlinedButton(onClick = { showGlossarySheet = true }) {
                Icon(
                    imageVector = Icons.Outlined.MenuBook,
                    contentDescription = stringResource(R.string.learn_open_glossary),
                )
            }
        }

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

    if (showGlossarySheet) {
        GlossarySheet(
            entries = learningContentState.glossaryEntries,
            onDismiss = { showGlossarySheet = false },
        )
    }
}