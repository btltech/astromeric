package com.astromeric.android.feature.tools

import android.content.Context
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
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
import com.astromeric.android.core.ui.DataQualityBanner
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
    val context = LocalContext.current
    val yearAheadLoadError = stringResource(R.string.year_ahead_error_load)
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
                .onFailure { errorMessage = it.message ?: yearAheadLoadError }
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
            title = stringResource(R.string.year_ahead_title),
            subtitle = stringResource(R.string.year_ahead_hero_subtitle),
        ) {
            selectedProfile?.let { profile ->
                AssistChip(
                    onClick = {},
                    label = {
                        Text(
                            stringResource(
                                R.string.tools_active_profile,
                                profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER),
                            ),
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
                Text(
                    if (isLoading) {
                        stringResource(R.string.tools_refreshing)
                    } else {
                        stringResource(R.string.year_ahead_refresh)
                    },
                )
            }
        }

        if (selectedProfile == null) {
            YearAheadSectionCard(
                title = stringResource(R.string.year_ahead_profile_needed_title),
                subtitle = stringResource(R.string.year_ahead_profile_needed_subtitle),
            ) {
                Button(onClick = onOpenProfile) {
                    Text(stringResource(R.string.action_open_profile))
                }
            }
            return@Column
        }

        if (selectedProfile.dataQuality != DataQuality.FULL) {
            DataQualityBanner(quality = selectedProfile.dataQuality)
        }

        if (isLoading && forecast == null) {
            PremiumLoadingCard(title = stringResource(R.string.year_ahead_loading_title))
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
                            label = { Text(stringResource(R.string.year_ahead_age_chip, currentPhase.age)) },
                        )
                        Text(
                            text = stringResource(
                                R.string.year_ahead_age_range_format,
                                currentPhase.minAge,
                                currentPhase.maxAge,
                                currentPhase.duration,
                            ),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        LinearProgressIndicator(
                            progress = { currentPhase.progressPct / 100f },
                            modifier = Modifier.fillMaxWidth(),
                        )
                        Text(
                            text = stringResource(R.string.year_ahead_progress_format, currentPhase.progressPct),
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
                                text = stringResource(
                                    R.string.year_ahead_next_phase_format,
                                    nextPhase.name,
                                    nextPhase.beginsAtAge,
                                ),
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
                    title = stringResource(R.string.year_ahead_title_with_year, loadedForecast.year),
                    subtitle = loadedForecast.personalYear.description ?: loadedForecast.personalYear.theme,
                ) {
                    AssistChip(
                        onClick = {},
                        label = { Text(stringResource(R.string.year_ahead_personal_year_chip, loadedForecast.personalYear.number)) },
                    )
                    AssistChip(
                        onClick = {},
                        label = { Text(stringResource(R.string.year_ahead_universal_year_chip, loadedForecast.universalYear.number)) },
                    )
                    Text(
                        text = loadedForecast.personalYear.theme,
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        text = stringResource(R.string.year_ahead_collective_backdrop_format, loadedForecast.universalYear.theme),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Button(
                        onClick = { isExplaining = true },
                        enabled = !isExplaining,
                    ) {
                        Text(
                            if (isExplaining) {
                                stringResource(R.string.year_ahead_generating)
                            } else {
                                stringResource(R.string.year_ahead_explain_this_year)
                            },
                        )
                    }
                }

                YearAheadSectionCard(
                    title = stringResource(R.string.year_ahead_solar_return_title),
                    subtitle = loadedForecast.solarReturn.description,
                ) {
                    Text(
                        text = loadedForecast.solarReturn.date,
                        style = MaterialTheme.typography.titleMedium,
                    )
                }

                if (loadedForecast.eclipses.all.isNotEmpty()) {
                    YearAheadSectionCard(
                        title = stringResource(R.string.year_ahead_eclipses_title),
                        subtitle = stringResource(R.string.year_ahead_eclipses_subtitle),
                    ) {
                        loadedForecast.eclipses.all.forEach { eclipse ->
                            Text(
                                text = formatYearAheadEclipseLine(context, eclipse.type, eclipse.sign, eclipse.date, eclipse.degree),
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }
                }

                if (loadedForecast.eclipses.personalImpacts.isNotEmpty()) {
                    YearAheadSectionCard(
                        title = stringResource(R.string.year_ahead_personal_activations_title),
                        subtitle = stringResource(R.string.year_ahead_personal_activations_subtitle),
                    ) {
                        loadedForecast.eclipses.personalImpacts.forEach { impact ->
                            Text(
                                text = stringResource(
                                    R.string.year_ahead_personal_activation_heading,
                                    impact.eclipse.type,
                                    impact.eclipse.sign,
                                    impact.significance,
                                ),
                                style = MaterialTheme.typography.titleSmall,
                            )
                            impact.impacts.forEach { detail ->
                                Text(
                                    text = formatYearAheadImpactDetail(context, detail.name, detail.aspect, detail.orb),
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        }
                    }
                }

                if (loadedForecast.ingresses.isNotEmpty()) {
                    YearAheadSectionCard(
                        title = stringResource(R.string.year_ahead_major_ingresses_title),
                        subtitle = stringResource(R.string.year_ahead_major_ingresses_subtitle),
                    ) {
                        loadedForecast.ingresses.take(6).forEach { ingress ->
                            Text(
                                text = stringResource(R.string.year_ahead_ingress_line, ingress.planet, ingress.sign, ingress.date),
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
                        title = stringResource(R.string.year_ahead_key_themes_title),
                        subtitle = stringResource(R.string.year_ahead_key_themes_subtitle),
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
                        title = stringResource(R.string.year_ahead_advice_title),
                        subtitle = stringResource(R.string.year_ahead_advice_subtitle),
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
                        text = stringResource(R.string.year_ahead_monthly_highlights_title),
                        style = MaterialTheme.typography.titleLarge,
                    )
                    loadedForecast.monthlyForecasts.forEach { month ->
                        PremiumContentCard(
                            title = "${month.monthName} ${month.year}",
                            body = month.focus,
                        ) {
                                AssistChip(
                                    onClick = {},
                                    label = { Text(stringResource(R.string.year_ahead_personal_month_chip, month.personalMonth)) },
                                )
                                Text(
                                    text = "${month.season} · ${month.element}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                                if (month.eclipses.isNotEmpty()) {
                                    Text(
                                        text = stringResource(
                                            R.string.year_ahead_month_eclipses_format,
                                            month.eclipses.joinToString(separator = " • ") { "${it.type} in ${it.sign}" },
                                        ),
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    )
                                }
                                if (month.ingresses.isNotEmpty()) {
                                    Text(
                                        text = stringResource(
                                            R.string.year_ahead_month_ingresses_format,
                                            month.ingresses.joinToString(separator = " • ") { "${it.planet} -> ${it.sign}" },
                                        ),
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
                    title = stringResource(R.string.year_ahead_error_title),
                    subtitle = errorMessage,
                ) {
                    Button(onClick = { refreshVersion += 1 }) {
                        Text(stringResource(R.string.action_try_again))
                    }
                }
        } else {
                YearAheadSectionCard(
                    title = stringResource(R.string.year_ahead_title),
                    subtitle = stringResource(R.string.year_ahead_empty_subtitle),
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

        val fallback = buildYearAheadFallbackSummary(context, loadedForecast)
        val explainResult = remoteDataSource.fetchAIExplain(
            authToken = authAccessToken.takeIf { it.isNotBlank() },
            request = buildYearAheadExplainRequest(context, loadedForecast),
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
    val context = LocalContext.current
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text = stringResource(R.string.year_ahead_explanation_title),
            style = MaterialTheme.typography.titleLarge,
        )
        provider?.let { rawProvider ->
            AssistChip(
                onClick = {},
                label = { Text(explanationProviderLabel(context, rawProvider)) },
            )
        }
        generatedAt?.let { instant ->
            Text(
                text = stringResource(R.string.year_ahead_generated_format, formatExplanationTimestamp(instant)),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Text(
            text = stringResource(R.string.year_ahead_explanation_body),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        TextButton(onClick = onRegenerate, enabled = !isExplaining) {
            Text(
                if (isExplaining) {
                    stringResource(R.string.year_ahead_generating)
                } else {
                    stringResource(R.string.year_ahead_regenerate)
                },
            )
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
    content: @Composable () -> Unit,
) {
    PremiumContentCard(
        title = title,
        body = subtitle,
    ) {
        content()
    }
}

private fun buildYearAheadExplainRequest(context: Context, forecast: YearAheadForecastData): AIExplainRequestData {
    val sections = buildList {
        add(
            AIExplainSectionData(
                title = context.getString(R.string.year_ahead_explain_request_personal_year_title, forecast.personalYear.number),
                highlights = listOfNotNull(forecast.personalYear.theme, forecast.personalYear.description),
            ),
        )
        add(
            AIExplainSectionData(
                title = context.getString(R.string.year_ahead_solar_return_title),
                highlights = listOf(forecast.solarReturn.date, forecast.solarReturn.description),
            ),
        )
        if (forecast.keyThemes.isNotEmpty()) {
            add(
                AIExplainSectionData(
                    title = context.getString(R.string.year_ahead_key_themes_title),
                    highlights = forecast.keyThemes.take(6),
                ),
            )
        }
        if (forecast.advice.isNotEmpty()) {
            add(
                AIExplainSectionData(
                    title = context.getString(R.string.year_ahead_explain_request_advice_title),
                    highlights = forecast.advice.take(6),
                ),
            )
        }
    }

    return AIExplainRequestData(
        scope = "year_ahead",
        headline = context.getString(
            R.string.year_ahead_explain_request_headline,
            forecast.year,
            forecast.personalYear.number,
        ),
        theme = forecast.personalYear.theme,
        sections = sections,
        simpleLanguage = true,
    )
}

private fun buildYearAheadFallbackSummary(context: Context, forecast: YearAheadForecastData): String {
    val topThemes = forecast.keyThemes.take(4).joinToString(separator = ", ") { "**$it**" }
    val topAdvice = forecast.advice.firstOrNull().orEmpty()
    return buildString {
        appendLine("## ${context.getString(R.string.year_ahead_fallback_tldr)}")
        appendLine()
        appendLine(
            context.getString(
                R.string.year_ahead_fallback_personal_year_line,
                forecast.personalYear.number,
                forecast.year,
                forecast.personalYear.theme.lowercase(Locale.getDefault()),
            ),
        )
        appendLine()
        appendLine("---")
        appendLine()
        appendLine("## ${context.getString(R.string.year_ahead_fallback_key_points)}")
        appendLine(context.getString(R.string.year_ahead_fallback_solar_return_line, forecast.solarReturn.date))
        if (topThemes.isNotBlank()) {
            appendLine(context.getString(R.string.year_ahead_fallback_themes_line, topThemes))
        }
        if (topAdvice.isNotBlank()) {
            appendLine(context.getString(R.string.year_ahead_fallback_advice_line, topAdvice))
        }
        appendLine()
        appendLine("---")
        appendLine()
        appendLine("## ${context.getString(R.string.year_ahead_fallback_next_step_title)}")
        appendLine()
        append(context.getString(R.string.year_ahead_fallback_next_step_body))
    }.trim()
}

private fun explanationProviderLabel(context: Context, provider: String): String = when (provider) {
    "local-fallback" -> context.getString(R.string.year_ahead_provider_local_fallback)
    "premium-required" -> context.getString(R.string.year_ahead_provider_premium_required)
    "fallback" -> context.getString(R.string.year_ahead_provider_fallback)
    else -> provider.replace('-', ' ').replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.getDefault()) else it.toString() }
}

private fun formatYearAheadEclipseLine(
    context: Context,
    type: String,
    sign: String,
    date: String,
    degree: Double?,
): String {
    val degreeSuffix = degree?.let { context.getString(R.string.year_ahead_degree_suffix, it) }.orEmpty()
    return context.getString(R.string.year_ahead_eclipse_line, type, sign, date, degreeSuffix)
}

private fun formatYearAheadImpactDetail(
    context: Context,
    name: String,
    aspect: String,
    orb: Double?,
): String {
    val orbSuffix = orb?.let { context.getString(R.string.year_ahead_orb_suffix, it) }.orEmpty()
    return context.getString(R.string.year_ahead_impact_detail, name, aspect, orbSuffix)
}

private fun formatExplanationTimestamp(instant: Instant): String =
    DateTimeFormatter.ofPattern("MMM d, h:mm a", Locale.getDefault())
        .withZone(ZoneId.systemDefault())
        .format(instant)

private fun plainMarkdown(text: String): String =
    text.replace("**", "").replace("__", "")