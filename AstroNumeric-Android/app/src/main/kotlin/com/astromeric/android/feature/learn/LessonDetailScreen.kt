package com.astromeric.android.feature.learn

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.model.LearningModuleData
import com.astromeric.android.core.ui.PremiumContentCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LessonDetailScreen(
    module: LearningModuleData,
    isCompleted: Boolean,
    onToggleCompleted: () -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(module.title, maxLines = 1) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
            )
        },
        modifier = modifier,
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            // Header card
            PremiumContentCard(
                title = module.title,
                body = module.description,
            ) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        AssistChip(onClick = {}, label = { Text(module.category.toDisplayLabel()) })
                        AssistChip(onClick = {}, label = { Text(module.difficulty.toDisplayLabel()) })
                        AssistChip(onClick = {}, label = { Text("${module.durationMinutes} min") })
                    }
                    if (module.keywords.isNotEmpty()) {
                        Text(
                            "Keywords: ${module.keywords.joinToString()}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
            }

            // Full content
            if (module.content.isNotBlank()) {
                PremiumContentCard(title = "Lesson Content") {
                        HorizontalDivider()
                        // Render content as paragraphs split by double newline
                        module.content.split("\n\n").filter { it.isNotBlank() }.forEach { paragraph ->
                            if (paragraph.trimStart().startsWith("# ")) {
                                Text(
                                    paragraph.trimStart().removePrefix("# ").trim(),
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.SemiBold,
                                )
                            } else if (paragraph.trimStart().startsWith("## ")) {
                                Text(
                                    paragraph.trimStart().removePrefix("## ").trim(),
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Medium,
                                )
                            } else if (paragraph.trimStart().startsWith("- ") || paragraph.trimStart().startsWith("• ")) {
                                paragraph.lines().filter { it.isNotBlank() }.forEach { line ->
                                    Text(
                                        line.trimStart().removePrefix("-").removePrefix("•").trim().let { "• $it" },
                                        style = MaterialTheme.typography.bodyMedium,
                                    )
                                }
                            } else {
                                Text(paragraph.trim(), style = MaterialTheme.typography.bodyMedium)
                            }
                        }
                }
            }

            // Related modules
            if (module.relatedModules.isNotEmpty()) {
                PremiumContentCard(title = "Related Topics") {
                        module.relatedModules.forEach { related ->
                            Text("• $related", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                }
            }

            // Complete / mark button
            if (isCompleted) {
                OutlinedButton(
                    onClick = onToggleCompleted,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Icon(Icons.Filled.CheckCircle, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                    Text(" Completed — Mark Incomplete")
                }
            } else {
                Button(
                    onClick = onToggleCompleted,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Mark as Complete")
                }
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

private fun String.toDisplayLabel(): String =
    replace('_', ' ').replace('-', ' ')
        .split(' ')
        .filter { it.isNotBlank() }
        .joinToString(" ") { it.replaceFirstChar(Char::uppercase) }
