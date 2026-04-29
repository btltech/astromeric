package com.astromeric.android.feature.tools

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AIExplainRequestData
import com.astromeric.android.core.model.AIExplainSectionData
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DataQuality
import com.astromeric.android.core.model.LifePhaseData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.YearAheadForecastData
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.ui.PremiumContentCard
import com.astromeric.android.core.ui.PremiumLoadingCard
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import java.time.Instant
import java.time.Year
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

@Composable
@OptIn(ExperimentalLayoutApi::class, ExperimentalMaterial3Api::class)
fun YearAheadScreen(
    selectedProfile: AppProfile?,
    remoteDataSource: AstroRemoteDataSource,
    authAccessToken: String,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val currentYear = remember { Year.now().value }
    var selectedYear by remember(selectedProfile?.id) { mutableIntStateOf(currentYear) }
    var refreshVersion by remember(selectedProfile?.id) { mutableIntStateOf(0) }
    var isLoading by remember(selectedProfile?.id) { mutableStateOf(false) }
    var errorMessage by remember(selectedProfile?.id) { mutableStateOf<String?>(null) }
    var forecast by remember(selectedProfile?.id) { mutableStateOf<YearAheadForecastData?>(null) }
    var lifePhase by remember(selectedProfile?.id) { mutableStateOf<LifePhaseData?>(null) }
    var isExplaining by remember(selectedProfile?.id, selectedYear) { mutableStateOf(false) }
    var explanationSummary by remember(selectedProfile?.id, selectedYear, refreshVersion) { mutableStateOf<String?>(null) }
    var explanationProvider by remember(selectedProfile?.id, selectedYear, refreshVersion) { mutableStateOf<String?>(null) }
    var explanationGeneratedAt by remember(selectedProfile?.id, selectedYear, refreshVersion) { mutableStateOf<Instant?>(null) }
    var showExplanationSheet by remember(selectedProfile?.id, selectedYear, refreshVersion) { mutableStateOf(false) }

    LaunchedEffect(selectedProfile?.id, selectedYear, refreshVersion) {
        val profile = selectedProfile ?: run {
            forecast = null
            lifePhase = null
            errorMessage = null
            isLoading = false
            return@LaunchedEffect
        }

        isLoading = true
        errorMessage = null

        coroutineScope {
            val forecastRequest = async { remoteDataSource.fetchYearAheadForecast(profile, selectedYear) }
            val lifePhaseRequest = async { remoteDataSource.fetchLifePhase(profile) }

            forecast = forecastRequest.await()
                .onFailure { errorMessage = it.message ?: "Year ahead forecast could not be loaded." }
                .getOrNull()

            lifePhase = lifePhaseRequest.await().getOrNull()
        }

        isLoading = false
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        YearAheadSectionCard(
            title = "Year Ahead",
            subtitle = "See the shape of the year before it arrives one month at a time. Start with the larger arc, then use the monthly highlights to pace what you push, protect, or reconsider.",
        ) {
            selectedProfile?.let { profile ->
                AssistChip(
                    onClick = {},
                    label = {
                        Text(
                            "Active profile: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)}",
                        )
                    },
                )
            }
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                (selectedYear - 2..selectedYear + 1).forEach { year ->
                    FilterChip(
                        selected = selectedYear == year,
                        onClick = { selectedYear = year },
                        label = { Text(year.toString()) },
                    )
                }
            }
            OutlinedButton(onClick = { refreshVersion += 1 }, enabled = !isLoading) {
                Text(if (isLoading) "Refreshing..." else "Refresh forecast")
            }
        }

        if (selectedProfile == null) {
            YearAheadSectionCard(
                title = "Profile Needed",
                subtitle = "Create or select a profile to generate the long-range forecast and fold your current life phase into the same annual arc.",
            ) {
                Button(onClick = onOpenProfile) {
                    Text("Open Profile")
                }
            }
            return@Column
        }

        if (selectedProfile.dataQuality != DataQuality.FULL) {
            YearAheadSectionCard(
                title = "Reduced Precision",
                subtitle = "Year Ahead is less precise without an exact birth time. Solar return and house-level themes may be approximate until your birth details are complete.",
            ) {}
        }

        if (isLoading && forecast == null) {
            PremiumLoadingCard(title = "Loading year ahead")
        } else if (forecast != null) {
                val loadedForecast = requireNotNull(forecast)
                lifePhase?.let { phase ->
                    val currentPhase = phase.currentPhase
                    YearAheadSectionCard(
                        title = currentPhase.name,
                        subtitle = currentPhase.narrative,
                    ) {
                        AssistChip(
                            onClick = {},
                            label = { Text("Age ${currentPhase.age}") },
                        )
                        Text(
                            text = "Ages ${currentPhase.minAge}-${currentPhase.maxAge} · ${currentPhase.duration}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        LinearProgressIndicator(
                            progress = { currentPhase.progressPct / 100f },
                            modifier = Modifier.fillMaxWidth(),
                        )
                        Text(
                            text = "${currentPhase.progressPct}% through this cycle",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        if (currentPhase.keywords.isNotEmpty()) {
                            FlowRow(
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp),
                            ) {
                                currentPhase.keywords.forEach { keyword ->
                                    AssistChip(
                                        onClick = {},
                                        label = { Text(keyword) },
                                    )
                                }
                            }
                        }
                        phase.nextPhase?.let { nextPhase ->
                            Text(
                                text = "Next phase: ${nextPhase.name} around age ${nextPhase.beginsAtAge}",
                                style = MaterialTheme.typography.titleSmall,
                            )
                            Text(
                                text = nextPhase.preview,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }

                YearAheadSectionCard(
                    title = "Year Ahead ${loadedForecast.year}",
                    subtitle = loadedForecast.personalYear.description ?: loadedForecast.personalYear.theme,
                ) {
                    AssistChip(
                        onClick = {},
                        label = { Text("Personal Year ${loadedForecast.personalYear.number}") },
                    )
                    AssistChip(
                        onClick = {},
                        label = { Text("Universal Year ${loadedForecast.universalYear.number}") },
                    )
                    Text(
                        text = loadedForecast.personalYear.theme,
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = "Collective backdrop: ${loadedForecast.universalYear.theme}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Button(
                        onClick = { isExplaining = true },
                        enabled = !isExplaining,
                    ) {
                        Text(if (isExplaining) "Generating..." else "Explain This Year")
                    }
                }

                YearAheadSectionCard(
                    title = "Solar Return",
                    subtitle = loadedForecast.solarReturn.description,
                ) {
                    Text(
                        text = loadedForecast.solarReturn.date,
                        style = MaterialTheme.typography.titleMedium,
                    )
                }

                if (loadedForecast.eclipses.all.isNotEmpty()) {
                    YearAheadSectionCard(
                        title = "Eclipses This Year",
                        subtitle = "Watch these windows closely. They mark turning points that can reframe the pace and priority of the year.",
                    ) {
                        loadedForecast.eclipses.all.forEach { eclipse ->
                            Text(
                                text = "• ${eclipse.type} in ${eclipse.sign} · ${eclipse.date}${eclipse.degree?.let { " · ${String.format("%.1f", it)}°" } ?: ""}",
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }
                }

                if (loadedForecast.eclipses.personalImpacts.isNotEmpty()) {
                    YearAheadSectionCard(
                        title = "Personal Activations",
                        subtitle = "These are the chart points the eclipses touch most directly.",
                    ) {
                        loadedForecast.eclipses.personalImpacts.forEach { impact ->
                            Text(
                                text = "${impact.eclipse.type} in ${impact.eclipse.sign} · ${impact.significance}",
                                style = MaterialTheme.typography.titleSmall,
                            )
                            impact.impacts.forEach { detail ->
                                Text(
                                    text = "• ${detail.name} ${detail.aspect}${detail.orb?.let { " (${String.format("%.1f", it)}° orb)" } ?: ""}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        }
                    }
                }

                if (loadedForecast.ingresses.isNotEmpty()) {
                    YearAheadSectionCard(
                        title = "Major Ingresses",
                        subtitle = "These sign changes show where the broader weather shifts during the year.",
                    ) {
                        loadedForecast.ingresses.take(6).forEach { ingress ->
                            Text(
                                text = "• ${ingress.planet} -> ${ingress.sign} · ${ingress.date}",
                                style = MaterialTheme.typography.bodyMedium,
                            )
                            Text(
                                text = ingress.impact,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }

                if (loadedForecast.keyThemes.isNotEmpty()) {
                    YearAheadSectionCard(
                        title = "Key Themes",
                        subtitle = "Use these as the annual frame before you optimize smaller decisions.",
                    ) {
                        loadedForecast.keyThemes.forEach { theme ->
                            Text(
                                text = "• $theme",
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }
                }

                if (loadedForecast.advice.isNotEmpty()) {
                    YearAheadSectionCard(
                        title = "Year Advice",
                        subtitle = "Treat this as pacing guidance for the entire cycle, not one good day or one bad week.",
                    ) {
                        loadedForecast.advice.forEach { advice ->
                            Text(
                                text = "• $advice",
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }
                }

                if (loadedForecast.monthlyForecasts.isNotEmpty()) {
                    Text(
                        text = "Monthly Highlights",
                        style = MaterialTheme.typography.titleLarge,
                    )
                    loadedForecast.monthlyForecasts.forEach { month ->
                        PremiumContentCard(
                            title = "${month.monthName} ${month.year}",
                            body = month.focus,
                        ) {
                                AssistChip(
                                    onClick = {},
                                    label = { Text("Personal Month ${month.personalMonth}") },
                                )
                                Text(
                                    text = "${month.season} · ${month.element}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                                if (month.eclipses.isNotEmpty()) {
                                    Text(
                                        text = "Eclipses: ${month.eclipses.joinToString(separator = " • ") { "${it.type} in ${it.sign}" }}",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    )
                                }
                                if (month.ingresses.isNotEmpty()) {
                                    Text(
                                        text = "Ingresses: ${month.ingresses.joinToString(separator = " • ") { "${it.planet} -> ${it.sign}" }}",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    )
                                }
                                month.highlights.forEach { highlight ->
                                    Text(
                                        text = "• $highlight",
                                        style = MaterialTheme.typography.bodySmall,
                                    )
                                }
                        }
                    }
                }
        } else if (errorMessage != null) {
                YearAheadSectionCard(
                    title = "Unable to Load Year Ahead",
                    subtitle = errorMessage,
                ) {
                    Button(onClick = { refreshVersion += 1 }) {
                        Text("Try Again")
                    }
                }
        } else {
                YearAheadSectionCard(
                    title = "Year Ahead",
                    subtitle = "Select a year or refresh to load the annual forecast.",
                ) {}
        }
    }

    if (showExplanationSheet && explanationSummary != null) {
        ModalBottomSheet(
            onDismissRequest = { showExplanationSheet = false },
        ) {
            YearExplanationSheet(
                markdown = explanationSummary.orEmpty(),
                provider = explanationProvider,
                generatedAt = explanationGeneratedAt,
                isExplaining = isExplaining,
                onRegenerate = { isExplaining = true },
            )
        }
    }

    LaunchedEffect(isExplaining) {
        if (!isExplaining) return@LaunchedEffect

        val loadedForecast = forecast ?: run {
            isExplaining = false
            return@LaunchedEffect
        }

        val fallback = buildYearAheadFallbackSummary(loadedForecast)
        val explainResult = remoteDataSource.fetchAIExplain(
            authToken = authAccessToken.takeIf { it.isNotBlank() },
            request = buildYearAheadExplainRequest(loadedForecast),
        ).getOrNull()

        explanationSummary = explainResult?.summary ?: fallback
        explanationProvider = explainResult?.provider ?: "fallback"
        explanationGeneratedAt = Instant.now()
        showExplanationSheet = true
        isExplaining = false
    }
}

@Composable
private fun YearExplanationSheet(
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
        Text(
            text = "Year Explanation",
            style = MaterialTheme.typography.titleLarge,
        )
        provider?.let { rawProvider ->
            AssistChip(
                onClick = {},
                label = { Text(explanationProviderLabel(rawProvider)) },
            )
        }
        generatedAt?.let { instant ->
            Text(
                text = "Generated ${formatExplanationTimestamp(instant)}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Text(
            text = "This matches the iOS flow more closely: you can read the annual explanation in a dedicated surface and regenerate it without leaving the forecast.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        TextButton(onClick = onRegenerate, enabled = !isExplaining) {
            Text(if (isExplaining) "Generating..." else "Regenerate")
        }
        YearExplanationMarkdown(markdown = markdown)
    }
}

@Composable
private fun YearExplanationMarkdown(markdown: String) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        markdown.lines().forEach { rawLine ->
            val line = rawLine.trim()
            when {
                line.isBlank() -> Unit
                line.startsWith("### ") -> Text(
                    text = plainMarkdown(line.removePrefix("### ")),
                    style = MaterialTheme.typography.titleMedium,
                )
                line.startsWith("## ") -> Text(
                    text = plainMarkdown(line.removePrefix("## ")),
                    style = MaterialTheme.typography.titleLarge,
                )
                line.startsWith("- ") -> Text(
                    text = "• ${plainMarkdown(line.removePrefix("- "))}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                line == "---" -> Text(
                    text = "",
                    style = MaterialTheme.typography.bodySmall,
                )
                else -> Text(
                    text = plainMarkdown(line),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }
    }
}

@Composable
private fun YearAheadSectionCard(
    title: String,
    subtitle: String?,
    content: @Composable ColumnScope.() -> Unit,
) {
    PremiumContentCard(
        title = title,
        body = subtitle,
    ) {
        content()
    }
}

private fun buildYearAheadExplainRequest(forecast: YearAheadForecastData): AIExplainRequestData {
    val sections = buildList {
        add(
            AIExplainSectionData(
                title = "Personal Year ${forecast.personalYear.number}",
                highlights = listOfNotNull(forecast.personalYear.theme, forecast.personalYear.description),
            ),
        )
        add(
            AIExplainSectionData(
                title = "Solar Return",
                highlights = listOf(forecast.solarReturn.date, forecast.solarReturn.description),
            ),
        )
        if (forecast.keyThemes.isNotEmpty()) {
            add(AIExplainSectionData(title = "Key Themes", highlights = forecast.keyThemes.take(6)))
        }
        if (forecast.advice.isNotEmpty()) {
            add(AIExplainSectionData(title = "Advice", highlights = forecast.advice.take(6)))
        }
    }

    return AIExplainRequestData(
        scope = "year_ahead",
        headline = "Year Ahead ${forecast.year} • Personal Year ${forecast.personalYear.number}",
        theme = forecast.personalYear.theme,
        sections = sections,
        simpleLanguage = true,
    )
}

private fun buildYearAheadFallbackSummary(forecast: YearAheadForecastData): String {
    val topThemes = forecast.keyThemes.take(4).joinToString(separator = ", ") { "**$it**" }
    val topAdvice = forecast.advice.firstOrNull().orEmpty()
    return buildString {
        appendLine("## TL;DR")
        appendLine()
        appendLine("Your **Personal Year ${forecast.personalYear.number}** sets the tone for ${forecast.year}. Focus on **${forecast.personalYear.theme.lowercase()}**.")
        appendLine()
        appendLine("---")
        appendLine()
        appendLine("## Key points")
        appendLine("- Solar Return: **${forecast.solarReturn.date}**")
        if (topThemes.isNotBlank()) {
            appendLine("- Themes: $topThemes")
        }
        if (topAdvice.isNotBlank()) {
            appendLine("- Advice: $topAdvice")
        }
        appendLine()
        appendLine("---")
        appendLine()
        appendLine("## Practical next step")
        appendLine()
        append("Pick **one theme** and choose **one small habit** you can repeat weekly. Use the monthly highlights to plan around it.")
    }.trim()
}

private fun explanationProviderLabel(provider: String): String = when (provider) {
    "local-fallback" -> "Local fallback"
    "premium-required" -> "Premium required"
    "fallback" -> "Fallback"
    else -> provider.replace('-', ' ').replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.getDefault()) else it.toString() }
}

private fun formatExplanationTimestamp(instant: Instant): String =
    DateTimeFormatter.ofPattern("MMM d, h:mm a", Locale.getDefault())
        .withZone(ZoneId.systemDefault())
        .format(instant)

private fun plainMarkdown(text: String): String =
    text.replace("**", "").replace("__", "")