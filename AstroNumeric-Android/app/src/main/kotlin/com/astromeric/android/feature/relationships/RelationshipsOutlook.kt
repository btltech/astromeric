package com.astromeric.android.feature.relationships

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.RelationshipBestDayData
import com.astromeric.android.core.model.RelationshipBestDaysData
import com.astromeric.android.core.model.RelationshipEventData
import com.astromeric.android.core.model.RelationshipEventsData
import com.astromeric.android.core.model.RelationshipFactorData
import com.astromeric.android.core.model.RelationshipPhasesData
import com.astromeric.android.core.model.RelationshipTimelineData
import com.astromeric.android.core.model.RelationshipTimingData
import com.astromeric.android.core.model.RelationshipVenusStatusData
import com.astromeric.android.core.model.displayName

@Composable
internal fun RelationshipOutlookSection(
    comparisonProfile: AppProfile?,
    hideSensitiveDetailsEnabled: Boolean,
    relationshipTimingError: String?,
    relationshipGuideError: String?,
    relationshipTiming: RelationshipTimingData?,
    relationshipVenusStatus: RelationshipVenusStatusData?,
    relationshipBestDays: RelationshipBestDaysData?,
    relationshipEvents: RelationshipEventsData?,
    relationshipPhases: RelationshipPhasesData?,
    relationshipTimeline: RelationshipTimelineData?,
) {
    RelationshipSectionCard(title = stringResource(R.string.relationships_section_outlook), error = null) {
        AssistChip(onClick = {}, label = { Text(stringResource(R.string.relationships_outlook_local_history_chip)) })
        AssistChip(
            onClick = {},
            label = {
                Text(
                    if (comparisonProfile != null) {
                        stringResource(
                            R.string.relationships_outlook_pair_timing_chip,
                            comparisonProfile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.PARTNER),
                        )
                    } else {
                        stringResource(R.string.relationships_outlook_sign_only_chip)
                    },
                )
            },
        )
        Text(
            text = if (comparisonProfile != null) {
                stringResource(R.string.relationships_outlook_pair_body)
            } else {
                stringResource(R.string.relationships_outlook_sign_only_body)
            },
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        RelationshipErrorText(errorMessage = relationshipTimingError)
        RelationshipErrorText(errorMessage = relationshipGuideError)
        relationshipTiming?.let { RelationshipTimingSummary(timing = it) }
        relationshipVenusStatus?.let { RelationshipTransitSummary(status = it) }
        relationshipBestDays?.bestDays?.take(3)?.takeIf { it.isNotEmpty() }?.let { bestDays ->
            Text(text = stringResource(R.string.relationships_best_upcoming_days_title), style = MaterialTheme.typography.titleSmall)
            bestDays.forEach { day -> RelationshipBestDayRow(day = day) }
        }
        relationshipEvents?.events?.take(3)?.takeIf { it.isNotEmpty() }?.let { events ->
            Text(text = stringResource(R.string.relationships_upcoming_events_title), style = MaterialTheme.typography.titleSmall)
            events.forEach { event -> RelationshipEventRow(event = event) }
        }
        relationshipPhases?.let { phases -> RelationshipPhaseSummary(phases = phases) }
        relationshipTimeline?.let { timeline -> RelationshipTimelineSummary(timeline = timeline) }
    }
}

@Composable
private fun RelationshipErrorText(errorMessage: String?) {
    errorMessage?.let {
        Text(
            text = it,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.error,
        )
    }
}

@Composable
private fun RelationshipTimingSummary(timing: RelationshipTimingData) {
    Text(text = stringResource(R.string.relationships_timing_lens_title), style = MaterialTheme.typography.titleSmall)
    Text(
        text = stringResource(R.string.relationships_today_in_love, timing.ratingEmoji, timing.rating, timing.score),
        style = MaterialTheme.typography.titleSmall,
    )
    Text(
        text = buildString {
            append(timing.person1Sign.replaceFirstChar { it.uppercase() })
            timing.person2Sign?.takeIf { it.isNotBlank() }?.let { partner ->
                append(" + ")
                append(partner.replaceFirstChar { it.uppercase() })
            }
            append(" · ")
            append(timing.date)
        },
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
    timing.venusTransit?.let { transit -> RelationshipTransitText(name = stringResource(R.string.relationships_planet_venus), sign = transit.sign, start = transit.start, end = transit.end) }
    timing.marsTransit?.let { transit -> RelationshipTransitText(name = stringResource(R.string.relationships_planet_mars), sign = transit.sign, start = transit.start, end = transit.end) }
    timing.venusRetrograde.warning?.let { warning ->
        Text(text = warning, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
    if (timing.recommendations.isNotEmpty()) {
        Text(text = stringResource(R.string.relationships_timing_cues, timing.recommendations.take(2).joinToString()), style = MaterialTheme.typography.bodyMedium)
    }
    if (timing.factors.isNotEmpty()) {
        Text(text = stringResource(R.string.relationships_key_factors_title), style = MaterialTheme.typography.titleSmall)
        timing.factors.take(3).forEach { factor -> RelationshipFactorRow(factor = factor) }
    }
    if (timing.warnings.isNotEmpty()) {
        Text(
            text = stringResource(R.string.relationships_watchouts, timing.warnings.take(2).joinToString()),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
    if (timing.loveThemes.isNotEmpty()) {
        Text(
            text = timing.loveThemes.entries.take(3).joinToString(separator = " · ") { entry ->
                "${entry.key.toRelationshipLabel()}: ${entry.value}"
            },
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun RelationshipTransitSummary(status: RelationshipVenusStatusData) {
    Text(text = stringResource(R.string.relationships_current_transits_title), style = MaterialTheme.typography.titleSmall)
    status.venus?.let { transit -> RelationshipTransitText(name = stringResource(R.string.relationships_planet_venus), sign = transit.sign, start = transit.start, end = transit.end) }
    status.mars?.let { transit -> RelationshipTransitText(name = stringResource(R.string.relationships_planet_mars), sign = transit.sign, start = transit.start, end = transit.end) }
    status.venusRetrograde.message?.takeIf { it.isNotBlank() }?.let { message ->
        Text(text = message, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun RelationshipTransitText(
    name: String,
    sign: String,
    start: String,
    end: String,
) {
    Text(
        text = stringResource(R.string.relationships_transit_text, name, sign, start, end),
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun RelationshipPhaseSummary(phases: RelationshipPhasesData) {
    Text(text = stringResource(R.string.relationships_phases_title), style = MaterialTheme.typography.titleSmall)
    Text(text = phases.description, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    phases.houseOrder.take(3).forEach { house ->
        phases.phases[house.toString()]?.let { phase ->
            RelationshipPhaseRow(house = house, theme = phase.theme, description = phase.description)
        }
    }
}

@Composable
private fun RelationshipTimelineSummary(timeline: RelationshipTimelineData) {
    Text(text = stringResource(R.string.relationships_timeline_title), style = MaterialTheme.typography.titleSmall)
    Text(
        text = stringResource(R.string.relationships_period_score, timeline.period.start, timeline.period.end, timeline.periodScore),
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
    Text(text = timeline.periodOutlook, style = MaterialTheme.typography.bodyMedium)
    if (timeline.loveThemes.isNotEmpty()) {
        Text(
            text = timeline.loveThemes.entries.take(2).joinToString(separator = " · ") { entry ->
                "${entry.key.toRelationshipLabel()}: ${entry.value}"
            },
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
    Text(
        text = stringResource(R.string.relationships_total_events_summary, timeline.totalEvents, timeline.personalEvents),
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
    if (timeline.bestUpcomingDays.isNotEmpty()) {
        Text(text = stringResource(R.string.relationships_best_windows_title), style = MaterialTheme.typography.titleSmall)
        timeline.bestUpcomingDays.take(3).forEach { day -> RelationshipBestDayRow(day = day) }
    }
    if (timeline.eventsByMonth.isNotEmpty()) {
        Text(text = stringResource(R.string.relationships_by_month_title), style = MaterialTheme.typography.titleSmall)
        timeline.eventsByMonth.entries.sortedBy { it.key }.take(3).forEach { (month, events) ->
            RelationshipTimelineMonthRow(month = month, events = events)
        }
    }
}

@Composable
private fun RelationshipBestDayRow(day: RelationshipBestDayData) {
    var bestDayText = stringResource(R.string.relationships_best_day_base, day.ratingEmoji, day.weekday, day.date, day.score)
    day.keyFactor?.takeIf { it.isNotBlank() }?.let { keyFactor ->
        bestDayText = stringResource(R.string.relationships_best_day_with_factor, bestDayText, keyFactor)
    }
    if (day.isToday) {
        bestDayText = stringResource(R.string.relationships_best_day_today, bestDayText)
    }
    Text(
        text = bestDayText,
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun RelationshipFactorRow(factor: RelationshipFactorData) {
    val factorLabel = buildString {
        factor.emoji?.takeIf { it.isNotBlank() }?.let {
            append(it)
            append(' ')
        }
        append(factor.factor.toRelationshipLabel())
    }
    Text(
        text = stringResource(R.string.relationships_factor_impact, factorLabel, factor.impact),
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun RelationshipEventRow(event: RelationshipEventData) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = listOfNotNull(event.emoji, event.title).joinToString(" "),
                style = MaterialTheme.typography.titleSmall,
            )
            Text(
                text = if (event.isPersonal) {
                    stringResource(R.string.relationships_event_meta_personal, event.date, event.impact.replace('_', ' '))
                } else {
                    stringResource(R.string.relationships_event_meta, event.date, event.impact.replace('_', ' '))
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = event.description,
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

@Composable
private fun RelationshipPhaseRow(
    house: Int,
    theme: String,
    description: String,
) {
    Text(
        text = stringResource(R.string.relationships_house_format, house, theme, description),
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun RelationshipTimelineMonthRow(
    month: String,
    events: List<RelationshipEventData>,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = month,
                style = MaterialTheme.typography.titleSmall,
            )
            Text(
                text = if (events.size == 1) {
                    stringResource(R.string.relationships_month_events_one, events.size)
                } else {
                    stringResource(R.string.relationships_month_events_many, events.size)
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            events.take(2).forEach { event ->
                Text(
                    text = listOfNotNull(event.emoji, event.title).joinToString(" "),
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        }
    }
}

internal fun String.toRelationshipLabel(): String =
    replace('_', ' ')
        .replace('-', ' ')
        .split(' ')
        .filter { it.isNotBlank() }
        .joinToString(" ") { part -> part.replaceFirstChar { it.uppercase() } }
