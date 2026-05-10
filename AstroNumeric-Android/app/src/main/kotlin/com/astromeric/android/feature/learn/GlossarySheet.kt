package com.astromeric.android.feature.learn

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.AssistChip
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.core.model.GlossaryEntryData
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumEmptyStateCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GlossarySheet(
    entries: List<GlossaryEntryData>,
    onDismiss: () -> Unit,
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    var searchText by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf<String?>(null) }

    val categories = remember(entries) {
        entries.map { it.category }.filter { it.isNotBlank() }.distinct().sorted()
    }

    val filtered = remember(entries, searchText, selectedCategory) {
        entries
            .filter { entry ->
                selectedCategory == null || entry.category == selectedCategory
            }
            .filter { entry ->
                searchText.isBlank() ||
                    entry.term.contains(searchText, ignoreCase = true) ||
                    entry.definition.contains(searchText, ignoreCase = true) ||
                    entry.relatedTerms.any { it.contains(searchText, ignoreCase = true) }
            }
            .sortedBy { it.term.lowercase() }
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .windowInsetsPadding(WindowInsets.navigationBars),
        ) {
            // Header row
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = stringResource(R.string.learn_glossary_sheet_title),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.alignByBaseline(),
                )
                IconButton(onClick = onDismiss) {
                    Icon(
                        imageVector = Icons.Filled.Close,
                        contentDescription = stringResource(R.string.action_close),
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Search
            OutlinedTextField(
                value = searchText,
                onValueChange = { searchText = it },
                label = { Text(stringResource(R.string.learn_glossary_search_placeholder)) },
                singleLine = true,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp),
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Category chips
            if (categories.isNotEmpty()) {
                Row(
                    modifier = Modifier
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    FilterChip(
                        selected = selectedCategory == null,
                        onClick = { selectedCategory = null },
                        label = { Text(stringResource(R.string.learn_glossary_category_all)) },
                    )
                    categories.forEach { cat ->
                        FilterChip(
                            selected = selectedCategory == cat,
                            onClick = { selectedCategory = if (selectedCategory == cat) null else cat },
                            label = { Text(cat.replaceFirstChar { it.uppercase() }) },
                        )
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
            }

            // Entry list
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp)
                    .padding(bottom = 24.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (filtered.isEmpty()) {
                    PremiumEmptyStateCard(
                        title = stringResource(R.string.learn_glossary_empty_title),
                        message = stringResource(R.string.learn_glossary_empty_body),
                    )
                } else {
                    filtered.forEach { entry ->
                        GlossaryEntryCard(entry = entry)
                    }
                }
            }
        }
    }
}

@Composable
private fun GlossaryEntryCard(entry: GlossaryEntryData) {
    var expanded by remember(entry.term) { mutableStateOf(false) }
    val hasExtra = entry.usageExample.isNotBlank() || entry.relatedTerms.isNotEmpty()
    PremiumContentCard(
        title = entry.term,
        body = entry.definition,
        footer = if (expanded && entry.usageExample.isNotBlank()) {
            stringResource(R.string.learn_glossary_example, entry.usageExample)
        } else {
            null
        },
    ) {
        if (entry.category.isNotBlank()) {
            AssistChip(
                onClick = {},
                label = { Text(entry.category.replaceFirstChar { it.uppercase() }) },
            )
        }
        if (expanded && entry.relatedTerms.isNotEmpty()) {
            Text(
                text = stringResource(R.string.learn_glossary_related, entry.relatedTerms.joinToString()),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        if (hasExtra) {
            TextButton(onClick = { expanded = !expanded }) {
                Text(if (expanded) "Show less" else "Show more")
            }
        }
    }
}
