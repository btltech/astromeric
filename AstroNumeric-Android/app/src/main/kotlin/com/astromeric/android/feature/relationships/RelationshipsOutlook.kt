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
import androidx.compose.ui.unit.dp
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
    RelationshipSectionCard(title = "Relationship outlook", error = null) {
        AssistChip(onClick = {}, label = { Text("Saved history stays local") })
        AssistChip(
            onClick = {},
            label = {
                Text(
                    if (comparisonProfile != null) {
                        "Pair timing: ${comparisonProfile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.PARTNER)}"
                    } else {
                        "Sign timing: no second profile selected"
                    },
                )
            },
        )
        Text(
            text = if (comparisonProfile != null) {
                "Live timing and timeline cues below are calculated for this profile pair."
            } else {
                "Live timing below currently uses the active profile sign only until you choose a second profile."
            },
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        RelationshipErrorText(errorMessage = relationshipTimingError)
        RelationshipErrorText(errorMessage = relationshipGuideError)
        relationshipTiming?.let { RelationshipTimingSummary(timing = it) }
        relationshipVenusStatus?.let { RelationshipTransitSummary(status = it) }
        relationshipBestDays?.bestDays?.take(3)?.takeIf { it.isNotEmpty() }?.let { bestDays ->
            Text(text = "Best upcoming days", style = MaterialTheme.typography.titleSmall)
            bestDays.forEach { day -> RelationshipBestDayRow(day = day) }
        }
        relationshipEvents?.events?.take(3)?.takeIf { it.isNotEmpty() }?.let { events ->
            Text(text = "Upcoming events", style = MaterialTheme.typography.titleSmall)
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
    Text(text = "Timing lens", style = MaterialTheme.typography.titleSmall)
    Text(
        text = "Today in love: ${timing.ratingEmoji} ${timing.rating} · ${timing.score}%",
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
    timing.venusTransit?.let { transit -> RelationshipTransitText(name = "Venus", sign = transit.sign, start = transit.start, end = transit.end) }
    timing.marsTransit?.let { transit -> RelationshipTransitText(name = "Mars", sign = transit.sign, start = transit.start, end = transit.end) }
    timing.venusRetrograde.warning?.let { warning ->
        Text(text = warning, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
    if (timing.recommendations.isNotEmpty()) {
        Text(text = "Timing cues: ${timing.recommendations.take(2).joinToString()}", style = MaterialTheme.typography.bodyMedium)
    }
    if (timing.factors.isNotEmpty()) {
        Text(text = "Key factors", style = MaterialTheme.typography.titleSmall)
        timing.factors.take(3).forEach { factor -> RelationshipFactorRow(factor = factor) }
    }
    if (timing.warnings.isNotEmpty()) {
        Text(
            text = "Watchouts: ${timing.warnings.take(2).joinToString()}",
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
    Text(text = "Current transits", style = MaterialTheme.typography.titleSmall)
    status.venus?.let { transit -> RelationshipTransitText(name = "Venus", sign = transit.sign, start = transit.start, end = transit.end) }
    status.mars?.let { transit -> RelationshipTransitText(name = "Mars", sign = transit.sign, start = transit.start, end = transit.end) }
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
        text = "$name in $sign · $start to $end",
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun RelationshipPhaseSummary(phases: RelationshipPhasesData) {
    Text(text = "Relationship phases", style = MaterialTheme.typography.titleSmall)
    Text(text = phases.description, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    phases.houseOrder.take(3).forEach { house ->
        phases.phases[house.toString()]?.let { phase ->
            RelationshipPhaseRow(house = house, theme = phase.theme, description = phase.description)
        }
    }
}

@Composable
private fun RelationshipTimelineSummary(timeline: RelationshipTimelineData) {
    Text(text = "Timeline outlook", style = MaterialTheme.typography.titleSmall)
    Text(
        text = "${timeline.period.start} to ${timeline.period.end} · ${timeline.periodScore}%",
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
        text = "${timeline.totalEvents} total events · ${timeline.personalEvents} personal",
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
    if (timeline.bestUpcomingDays.isNotEmpty()) {
        Text(text = "Best windows in this period", style = MaterialTheme.typography.titleSmall)
        timeline.bestUpcomingDays.take(3).forEach { day -> RelationshipBestDayRow(day = day) }
    }
    if (timeline.eventsByMonth.isNotEmpty()) {
        Text(text = "By month", style = MaterialTheme.typography.titleSmall)
        timeline.eventsByMonth.entries.sortedBy { it.key }.take(3).forEach { (month, events) ->
            RelationshipTimelineMonthRow(month = month, events = events)
        }
    }
}

@Composable
private fun RelationshipBestDayRow(day: RelationshipBestDayData) {
    Text(
        text = buildString {
            append("${day.ratingEmoji} ${day.weekday} ${day.date} · ${day.score}%")
            day.keyFactor?.takeIf { it.isNotBlank() }?.let { append(" · $it") }
            if (day.isToday) append(" · Today")
        },
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun RelationshipFactorRow(factor: RelationshipFactorData) {
    Text(
        text = buildString {
            factor.emoji?.takeIf { it.isNotBlank() }?.let {
                append(it)
                append(' ')
            }
            append(factor.factor.toRelationshipLabel())
            append(" · ")
            append(factor.impact)
            append(" impact")
        },
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
                text = "${event.date} · ${event.impact.replace('_', ' ')}${if (event.isPersonal) " · Personal" else ""}",
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
        text = "House $house · $theme: $description",
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
                text = "${events.size} event${if (events.size == 1) "" else "s"}",
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
