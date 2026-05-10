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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
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
    onOpenFullScreen: (() -> Unit)? = null,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        NumerologyContextCard(
            selectedProfile = selectedProfile,
            selectedMethod = selectedMethod,
            onSelectMethod = onSelectMethod,
            numerology = numerology,
            isExplaining = isExplaining,
            onExplain = onExplain,
            onOpenFullScreen = onOpenFullScreen,
        )

        when {
            selectedProfile == null -> Unit
            isLoading -> PremiumLoadingCard(title = stringResource(R.string.charts_numerology_loading_title))
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
    onOpenFullScreen: (() -> Unit)? = null,
) {
    StudioSectionCard(
        title = stringResource(R.string.charts_numerology_context_title),
        subtitle = stringResource(R.string.charts_numerology_context_subtitle),
    ) {
        if (selectedProfile == null) {
            Text(
                text = stringResource(R.string.charts_numerology_select_profile),
                style = MaterialTheme.typography.bodyMedium,
            )
        } else {
            Text(
                text = stringResource(R.string.charts_numerology_reading_for, selectedProfile.name, selectedProfile.dateOfBirth),
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
                        label = { Text(stringResource(method.labelRes)) },
                    )
                }
            }
            Text(
                text = stringResource(selectedMethod.descriptionRes),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            OutlinedButton(
                onClick = onExplain,
                enabled = numerology != null && !isExplaining,
            ) {
                Text(
                    if (isExplaining) {
                        stringResource(R.string.charts_numerology_generating)
                    } else {
                        stringResource(R.string.charts_numerology_explain)
                    },
                )
            }
            onOpenFullScreen?.let { openFull ->
                TextButton(onClick = openFull) {
                    Text(stringResource(R.string.charts_numerology_open_full_view))
                }
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
        title = stringResource(R.string.charts_numerology_synthesis_title),
        subtitle = stringResource(R.string.charts_numerology_synthesis_subtitle),
    ) {
        Text(text = synthesis.summary, style = MaterialTheme.typography.bodyMedium)
        if (synthesis.currentFocus.isNotBlank()) {
            Text(
                text = stringResource(R.string.charts_numerology_current_focus_format, synthesis.currentFocus),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        if (synthesis.affirmation.isNotBlank()) {
            Text(
                text = stringResource(R.string.charts_numerology_affirmation_format, synthesis.affirmation),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        formatGeneratedAt(numerology.generatedAt)?.let { generatedAt ->
            Text(
                text = stringResource(R.string.charts_numerology_updated, generatedAt),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Text(
            text = stringResource(R.string.charts_numerology_synthesis_note),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun NumerologyCoreNumbersCard(numerology: NumerologyData) {
    StudioSectionCard(
        title = stringResource(R.string.charts_numerology_core_numbers_title),
        subtitle = stringResource(R.string.charts_numerology_core_numbers_subtitle),
    ) {
        NumerologyMetricLine(stringResource(R.string.charts_numerology_life_path_label), numerology.lifePath.number, numerology.lifePath.meaning)
        NumerologyMetricLine(stringResource(R.string.charts_numerology_destiny_label), numerology.destinyNumber, numerology.destinyInterpretation)
        NumerologyMetricLine(stringResource(R.string.charts_numerology_personal_year_label), numerology.personalYear.cycleNumber, numerology.personalYear.interpretation)
        numerology.personalMonthNumber?.let { personalMonth ->
            NumerologyMetricLine(stringResource(R.string.charts_numerology_personal_month_label), personalMonth, numerology.numerologyInsights["personal_month"].orEmpty())
        }
        numerology.personalDayNumber?.let { personalDay ->
            NumerologyMetricLine(stringResource(R.string.charts_numerology_personal_day_label), personalDay, numerology.numerologyInsights["personal_day"].orEmpty())
        }
    }
}

@Composable
private fun NumerologyLifePathCard(numerology: NumerologyData) {
    StudioSectionCard(
        title = stringResource(R.string.charts_numerology_life_path_context_title),
        subtitle = stringResource(R.string.charts_numerology_life_path_context_subtitle),
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
        title = stringResource(R.string.charts_numerology_current_cycle_title),
        subtitle = stringResource(R.string.charts_numerology_current_cycle_subtitle),
    ) {
        numerology.personalYear.focusAreas.forEach { focusArea ->
            Text(text = stringResource(R.string.charts_numerology_focus_format, focusArea), style = MaterialTheme.typography.bodyMedium)
        }
        numerology.numerologyInsights["soul_urge"]?.takeIf { it.isNotBlank() }?.let { soulUrge ->
            Text(text = stringResource(R.string.charts_numerology_soul_urge_format, soulUrge), style = MaterialTheme.typography.bodyMedium)
        }
        numerology.numerologyInsights["personality"]?.takeIf { it.isNotBlank() }?.let { personality ->
            Text(text = stringResource(R.string.charts_numerology_personality_format, personality), style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun NumerologyLuckyTimingCard(numerology: NumerologyData) {
    StudioSectionCard(
        title = stringResource(R.string.charts_numerology_lucky_timing_title),
        subtitle = stringResource(R.string.charts_numerology_lucky_timing_subtitle),
    ) {
        if (numerology.luckyNumbers.isNotEmpty()) {
            Text(text = stringResource(R.string.charts_numerology_lucky_numbers_label), style = MaterialTheme.typography.titleSmall)
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
            Text(text = stringResource(R.string.charts_numerology_auspicious_days_label), style = MaterialTheme.typography.titleSmall)
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
        title = stringResource(R.string.charts_numerology_dominant_themes_title),
        subtitle = stringResource(R.string.charts_numerology_dominant_themes_subtitle),
    ) {
        synthesis.dominantNumbers.take(4).forEach { highlight ->
            Text(
                text = stringResource(R.string.charts_numerology_dominant_highlight_format, highlight.label, highlight.number, highlight.meaning),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        synthesis.strengths.take(4).forEach { strength ->
            Text(text = stringResource(R.string.charts_numerology_strength_format, strength), style = MaterialTheme.typography.bodyMedium)
        }
        synthesis.growthEdges.take(4).forEach { edge ->
            Text(text = stringResource(R.string.charts_numerology_growth_edge_format, edge), style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun NumerologyLongRangeCard(numerology: NumerologyData) {
    if (numerology.pinnacles.isEmpty() && numerology.challenges.isEmpty()) return
    StudioSectionCard(
        title = stringResource(R.string.charts_numerology_long_range_title),
        subtitle = stringResource(R.string.charts_numerology_long_range_subtitle),
    ) {
        numerology.pinnacles.forEach { pinnacle ->
            Text(
                text = stringResource(
                    R.string.charts_numerology_pinnacle_format,
                    pinnacle.number,
                    pinnacle.ages?.let { " · $it" } ?: "",
                    pinnacle.meaning.orEmpty(),
                ),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        numerology.challenges.forEach { challenge ->
            Text(
                text = stringResource(
                    R.string.charts_numerology_challenge_format,
                    challenge.number,
                    challenge.ages?.let { " · $it" } ?: "",
                    challenge.meaning.orEmpty(),
                ),
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
        val context = LocalContext.current
        Text(text = stringResource(R.string.charts_numerology_explanation_title), style = MaterialTheme.typography.titleLarge)
        provider?.let { rawProvider ->
            AssistChip(onClick = {}, label = { Text(chartExplanationProviderLabel(rawProvider, context)) })
        }
        generatedAt?.let { instant ->
            Text(
                text = stringResource(R.string.charts_numerology_generated_at, formatChartExplanationTimestamp(instant)),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Text(
            text = stringResource(R.string.charts_numerology_sheet_note),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        TextButton(onClick = onRegenerate, enabled = !isExplaining) {
            Text(
                if (isExplaining) {
                    stringResource(R.string.charts_numerology_generating)
                } else {
                    stringResource(R.string.charts_numerology_regenerate)
                },
            )
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

private fun chartExplanationProviderLabel(provider: String, context: android.content.Context): String = when (provider) {
    "local-fallback" -> context.getString(R.string.charts_provider_local_fallback)
    "premium-required" -> context.getString(R.string.charts_provider_premium_required)
    "fallback" -> context.getString(R.string.charts_provider_fallback)
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