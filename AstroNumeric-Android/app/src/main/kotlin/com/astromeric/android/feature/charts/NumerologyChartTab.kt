package com.astromeric.android.feature.charts

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.NumerologyData
import com.astromeric.android.core.ui.PremiumLoadingCard
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

@Composable
internal fun NumerologyTab(
    selectedProfile: AppProfile?,
    selectedMethod: NumerologyMethod,
    onSelectMethod: (NumerologyMethod) -> Unit,
    isLoading: Boolean,
    errorMessage: String?,
    numerology: NumerologyData?,
    isExplaining: Boolean,
    onExplain: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        NumerologyContextCard(
            selectedProfile = selectedProfile,
            selectedMethod = selectedMethod,
            onSelectMethod = onSelectMethod,
            numerology = numerology,
            isExplaining = isExplaining,
            onExplain = onExplain,
        )

        when {
            selectedProfile == null -> Unit
            isLoading -> PremiumLoadingCard(title = "Calculating numerology")
            errorMessage != null -> StatusCard(message = errorMessage, isError = true)
            numerology != null -> NumerologyLoadedContent(numerology = numerology)
        }
    }
}

@Composable
private fun NumerologyContextCard(
    selectedProfile: AppProfile?,
    selectedMethod: NumerologyMethod,
    onSelectMethod: (NumerologyMethod) -> Unit,
    numerology: NumerologyData?,
    isExplaining: Boolean,
    onExplain: () -> Unit,
) {
    StudioSectionCard(
        title = "Numerology in context",
        subtitle = "Switch methods when you want a different lens on name-based emphasis, but keep the result connected to the profile's chart story.",
    ) {
        if (selectedProfile == null) {
            Text(
                text = "Select or create a profile before calculating numerology.",
                style = MaterialTheme.typography.bodyMedium,
            )
        } else {
            Text(
                text = "Reading for ${selectedProfile.name} · ${selectedProfile.dateOfBirth}",
                style = MaterialTheme.typography.bodyMedium,
            )
            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                NumerologyMethod.entries.forEach { method ->
                    FilterChip(
                        selected = selectedMethod == method,
                        onClick = { onSelectMethod(method) },
                        label = { Text(method.label) },
                    )
                }
            }
            Text(
                text = selectedMethod.description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            OutlinedButton(
                onClick = onExplain,
                enabled = numerology != null && !isExplaining,
            ) {
                Text(if (isExplaining) "Generating..." else "Explain My Numbers")
            }
        }
    }
}

@Composable
private fun NumerologyLoadedContent(numerology: NumerologyData) {
    NumerologySynthesisCard(numerology = numerology)
    NumerologyCoreNumbersCard(numerology = numerology)
    NumerologyLifePathCard(numerology = numerology)
    NumerologyCurrentCycleCard(numerology = numerology)
    NumerologyLuckyTimingCard(numerology = numerology)
    NumerologyDominantThemesCard(numerology = numerology)
    NumerologyLongRangeCard(numerology = numerology)
}

@Composable
private fun NumerologySynthesisCard(numerology: NumerologyData) {
    val synthesis = numerology.synthesis ?: return
    StudioSectionCard(
        title = "Current synthesis",
        subtitle = "Use the summary as the glue between your core numbers and the current cycle.",
    ) {
        Text(text = synthesis.summary, style = MaterialTheme.typography.bodyMedium)
        if (synthesis.currentFocus.isNotBlank()) {
            Text(text = "Current focus: ${synthesis.currentFocus}", style = MaterialTheme.typography.bodyMedium)
        }
        if (synthesis.affirmation.isNotBlank()) {
            Text(
                text = "Affirmation: ${synthesis.affirmation}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        formatGeneratedAt(numerology.generatedAt)?.let { generatedAt ->
            Text(
                text = "Updated $generatedAt",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Text(
            text = "The explanation flow matches iOS more closely: try the backend explanation, then keep a structured local synthesis if the request is unavailable.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun NumerologyCoreNumbersCard(numerology: NumerologyData) {
    StudioSectionCard(
        title = "Core numbers",
        subtitle = "Life Path sets the main arc; Destiny and current cycles tell you how it is being expressed now.",
    ) {
        NumerologyMetricLine("Life Path", numerology.lifePath.number, numerology.lifePath.meaning)
        NumerologyMetricLine("Destiny", numerology.destinyNumber, numerology.destinyInterpretation)
        NumerologyMetricLine("Personal Year", numerology.personalYear.cycleNumber, numerology.personalYear.interpretation)
        numerology.personalMonthNumber?.let { personalMonth ->
            NumerologyMetricLine("Personal Month", personalMonth, numerology.numerologyInsights["personal_month"].orEmpty())
        }
        numerology.personalDayNumber?.let { personalDay ->
            NumerologyMetricLine("Personal Day", personalDay, numerology.numerologyInsights["personal_day"].orEmpty())
        }
    }
}

@Composable
private fun NumerologyLifePathCard(numerology: NumerologyData) {
    StudioSectionCard(
        title = "Life Path context",
        subtitle = "This is the stable through-line behind the changing cycle numbers.",
    ) {
        Text(text = numerology.lifePath.lifePurpose, style = MaterialTheme.typography.bodyMedium)
        if (numerology.lifePath.traits.isNotEmpty()) {
            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                numerology.lifePath.traits.forEach { trait ->
                    AssistChip(onClick = {}, label = { Text(trait) })
                }
            }
        }
    }
}

@Composable
private fun NumerologyCurrentCycleCard(numerology: NumerologyData) {
    StudioSectionCard(
        title = "Current cycle",
        subtitle = "This section turns the present year into practical focus areas instead of vague themes.",
    ) {
        numerology.personalYear.focusAreas.forEach { focusArea ->
            Text(text = "Focus: $focusArea", style = MaterialTheme.typography.bodyMedium)
        }
        numerology.numerologyInsights["soul_urge"]?.takeIf { it.isNotBlank() }?.let { soulUrge ->
            Text(text = "Soul urge: $soulUrge", style = MaterialTheme.typography.bodyMedium)
        }
        numerology.numerologyInsights["personality"]?.takeIf { it.isNotBlank() }?.let { personality ->
            Text(text = "Personality: $personality", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun NumerologyLuckyTimingCard(numerology: NumerologyData) {
    StudioSectionCard(
        title = "Lucky numbers and days",
        subtitle = "Treat these as timing accents, not substitutes for the rest of the reading.",
    ) {
        if (numerology.luckyNumbers.isNotEmpty()) {
            Text(text = "Lucky numbers", style = MaterialTheme.typography.titleSmall)
            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                numerology.luckyNumbers.forEach { luckyNumber ->
                    AssistChip(onClick = {}, label = { Text(luckyNumber.toString()) })
                }
            }
        }
        if (numerology.auspiciousDays.isNotEmpty()) {
            Text(text = "Auspicious days", style = MaterialTheme.typography.titleSmall)
            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                numerology.auspiciousDays.forEach { day ->
                    AssistChip(onClick = {}, label = { Text(day.toString()) })
                }
            }
        }
    }
}

@Composable
private fun NumerologyDominantThemesCard(numerology: NumerologyData) {
    val synthesis = numerology.synthesis ?: return
    StudioSectionCard(
        title = "Dominant themes",
        subtitle = "This is where the reading becomes actionable instead of just descriptive.",
    ) {
        synthesis.dominantNumbers.take(4).forEach { highlight ->
            Text(
                text = "${highlight.label} ${highlight.number}: ${highlight.meaning}",
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        synthesis.strengths.take(4).forEach { strength ->
            Text(text = "Strength: $strength", style = MaterialTheme.typography.bodyMedium)
        }
        synthesis.growthEdges.take(4).forEach { edge ->
            Text(text = "Growth edge: $edge", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun NumerologyLongRangeCard(numerology: NumerologyData) {
    if (numerology.pinnacles.isEmpty() && numerology.challenges.isEmpty()) return
    StudioSectionCard(
        title = "Long-range development",
        subtitle = "Pinnacles show major phases; challenges show the lessons likely to repeat inside them.",
    ) {
        numerology.pinnacles.take(3).forEach { pinnacle ->
            Text(
                text = "Pinnacle ${pinnacle.number}${pinnacle.ages?.let { " · $it" } ?: ""}: ${pinnacle.meaning.orEmpty()}",
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        numerology.challenges.take(3).forEach { challenge ->
            Text(
                text = "Challenge ${challenge.number}${challenge.ages?.let { " · $it" } ?: ""}: ${challenge.meaning.orEmpty()}",
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
private fun NumerologyMetricLine(
    title: String,
    number: Int,
    detail: String,
) {
    Text(
        text = buildString {
            append("$title $number")
            if (detail.isNotBlank()) {
                append(" · $detail")
            }
        },
        style = MaterialTheme.typography.bodyMedium,
    )
}

@Composable
internal fun NumerologyExplanationSheet(
    markdown: String,
    provider: String?,
    generatedAt: Instant?,
    isExplaining: Boolean,
    onRegenerate: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(text = "Numerology Explanation", style = MaterialTheme.typography.titleLarge)
        provider?.let { rawProvider ->
            AssistChip(onClick = {}, label = { Text(chartExplanationProviderLabel(rawProvider)) })
        }
        generatedAt?.let { instant ->
            Text(
                text = "Generated ${formatChartExplanationTimestamp(instant)}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Text(
            text = "This mirrors the iOS flow more closely: try the backend explanation first, then keep a deterministic local fallback if the request cannot complete.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        TextButton(onClick = onRegenerate, enabled = !isExplaining) {
            Text(if (isExplaining) "Generating..." else "Regenerate")
        }
        ChartExplanationMarkdown(markdown = markdown)
    }
}

@Composable
private fun ChartExplanationMarkdown(markdown: String) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        markdown.lines().forEach { rawLine ->
            val line = rawLine.trim()
            when {
                line.isBlank() -> Unit
                line.startsWith("### ") -> Text(
                    text = plainChartMarkdown(line.removePrefix("### ")),
                    style = MaterialTheme.typography.titleMedium,
                )
                line.startsWith("## ") -> Text(
                    text = plainChartMarkdown(line.removePrefix("## ")),
                    style = MaterialTheme.typography.titleLarge,
                )
                line.startsWith("- ") -> Text(
                    text = "• ${plainChartMarkdown(line.removePrefix("- "))}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                line == "---" -> Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(text = "", style = MaterialTheme.typography.bodySmall)
                }
                else -> Text(
                    text = plainChartMarkdown(line),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }
    }
}

private fun chartExplanationProviderLabel(provider: String): String = when (provider) {
    "local-fallback" -> "Local fallback"
    "premium-required" -> "Premium required"
    "fallback" -> "Fallback"
    else -> provider.replace('-', ' ').replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.getDefault()) else it.toString() }
}

private fun formatChartExplanationTimestamp(instant: Instant): String =
    DateTimeFormatter.ofPattern("MMM d, h:mm a", Locale.getDefault())
        .withZone(ZoneId.systemDefault())
        .format(instant)

private fun plainChartMarkdown(text: String): String =
    text.replace("**", "").replace("__", "")

private fun formatGeneratedAt(rawValue: String?): String? = rawValue?.let { value ->
    runCatching {
        DateTimeFormatter.ofPattern("MMM d, h:mm a", Locale.getDefault())
            .withZone(ZoneId.systemDefault())
            .format(OffsetDateTime.parse(value).toInstant())
    }.getOrNull()
}