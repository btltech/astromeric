package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter

enum class JournalOutcome(
    val wireValue: String,
    val label: String,
    val badge: String,
) {
    YES("yes", "Accurate", "Yes"),
    PARTIAL("partial", "Mixed", "Partial"),
    NO("no", "Off", "No"),
    NEUTRAL("neutral", "Open", "Neutral");

    companion object {
        fun fromWireValue(value: String?): JournalOutcome =
            entries.firstOrNull { it.wireValue == value } ?: NEUTRAL
    }
}

enum class JournalMode {
    LOCAL,
    REMOTE,
}

data class LocalJournalEntryData(
    val id: Int,
    val profileId: Int,
    val createdAt: String,
    val updatedAt: String,
    val entry: String,
    val outcome: String? = null,
) {
    val preview: String
        get() = entry.trim().replace("\n", " ").take(160)

    val journalOutcome: JournalOutcome
        get() = JournalOutcome.fromWireValue(outcome)
}

data class JournalPromptItemData(
    @SerializedName("text")
    val text: String,
    @SerializedName("category")
    val category: String? = null,
)

data class JournalPromptsData(
    @SerializedName("scope")
    val scope: String,
    @SerializedName("prompts")
    val prompts: List<JournalPromptItemData>,
)

data class JournalEntryCardData(
    val id: Int,
    val scope: String? = null,
    val scopeLabel: String,
    val date: String? = null,
    val formattedDate: String,
    val hasJournal: Boolean,
    val journalPreview: String,
    val journalFull: String,
    val feedback: String? = null,
    val feedbackEmoji: String? = null,
    val contentSummary: String? = null,
    val isLocalOnly: Boolean = false,
) {
    val journalOutcome: JournalOutcome
        get() = JournalOutcome.fromWireValue(feedback)

    val previewText: String
        get() = journalPreview
            .trim()
            .ifBlank { contentSummary.orEmpty().trim() }
            .ifBlank { "No journal saved yet." }

    val supportingText: String?
        get() = contentSummary?.trim()?.takeIf { it.isNotBlank() }
}

data class JournalReadingsData(
    @SerializedName("profile_id")
    val profileId: Int,
    @SerializedName("total")
    val total: Int,
    @SerializedName("limit")
    val limit: Int,
    @SerializedName("offset")
    val offset: Int,
    @SerializedName("readings")
    val readings: List<RemoteJournalReadingData>,
)

data class RemoteJournalReadingData(
    @SerializedName("id")
    val id: Int,
    @SerializedName("scope")
    val scope: String = "daily",
    @SerializedName("scope_label")
    val scopeLabel: String = "Daily",
    @SerializedName("date")
    val date: String? = null,
    @SerializedName("formatted_date")
    val formattedDate: String? = null,
    @SerializedName("has_journal")
    val hasJournal: Boolean = false,
    @SerializedName("journal_preview")
    val journalPreview: String = "",
    @SerializedName("journal_full")
    val journalFull: String = "",
    @SerializedName("feedback")
    val feedback: String? = null,
    @SerializedName("feedback_emoji")
    val feedbackEmoji: String? = null,
    @SerializedName("content_summary")
    val contentSummary: String? = null,
) {
    fun toCardData(): JournalEntryCardData = JournalEntryCardData(
        id = id,
        scope = scope,
        scopeLabel = scopeLabel,
        date = date,
        formattedDate = formattedDate.orEmpty().ifBlank { date.orEmpty().ifBlank { "Undated" } },
        hasJournal = hasJournal,
        journalPreview = journalPreview,
        journalFull = journalFull,
        feedback = feedback,
        feedbackEmoji = feedbackEmoji,
        contentSummary = contentSummary,
        isLocalOnly = false,
    )
}

data class JournalEntryRequestData(
    @SerializedName("reading_id")
    val readingId: Int,
    @SerializedName("entry")
    val entry: String,
)

data class JournalSavedEntryData(
    @SerializedName("reading_id")
    val readingId: Int,
    @SerializedName("entry")
    val entry: String,
    @SerializedName("timestamp")
    val timestamp: String? = null,
    @SerializedName("word_count")
    val wordCount: Int = 0,
    @SerializedName("character_count")
    val characterCount: Int = 0,
)

data class JournalEntryActionData(
    @SerializedName("message")
    val message: String,
    @SerializedName("entry")
    val entry: JournalSavedEntryData,
)

data class JournalOutcomeRequestData(
    @SerializedName("reading_id")
    val readingId: Int,
    @SerializedName("outcome")
    val outcome: String,
    @SerializedName("notes")
    val notes: String? = null,
)

data class JournalSavedOutcomeData(
    @SerializedName("reading_id")
    val readingId: Int,
    @SerializedName("outcome")
    val outcome: String,
    @SerializedName("outcome_emoji")
    val outcomeEmoji: String? = null,
    @SerializedName("categories")
    val categories: List<String> = emptyList(),
    @SerializedName("notes")
    val notes: String? = null,
    @SerializedName("recorded_at")
    val recordedAt: String? = null,
)

data class JournalOutcomeActionData(
    @SerializedName("message")
    val message: String,
    @SerializedName("outcome")
    val outcome: JournalSavedOutcomeData,
)

data class JournalStatsResponseData(
    @SerializedName("profile_id")
    val profileId: Int,
    @SerializedName("stats")
    val stats: JournalAccuracyStatsData,
    @SerializedName("insights")
    val insights: JournalInsightsData,
)

data class JournalAccuracyStatsData(
    @SerializedName("total_readings")
    val totalReadings: Int = 0,
    @SerializedName("rated_readings")
    val ratedReadings: Int = 0,
    @SerializedName("unrated_readings")
    val unratedReadings: Int = 0,
    @SerializedName("accuracy_rate")
    val accuracyRate: Double = 0.0,
    @SerializedName("by_outcome")
    val byOutcome: Map<String, Int> = emptyMap(),
    @SerializedName("by_scope")
    val byScope: Map<String, JournalScopeAccuracyData> = emptyMap(),
    @SerializedName("trend")
    val trend: String = "neutral",
    @SerializedName("trend_emoji")
    val trendEmoji: String = "➖",
    @SerializedName("message")
    val message: String = "",
)

data class JournalScopeAccuracyData(
    @SerializedName("accuracy")
    val accuracy: Double = 0.0,
    @SerializedName("total")
    val total: Int = 0,
    @SerializedName("yes")
    val yes: Int = 0,
    @SerializedName("no")
    val no: Int = 0,
    @SerializedName("partial")
    val partial: Int = 0,
)

data class JournalInsightsData(
    @SerializedName("total_journals")
    val totalJournals: Int = 0,
    @SerializedName("best_scope")
    val bestScope: String? = null,
    @SerializedName("best_scope_accuracy")
    val bestScopeAccuracy: Double? = null,
    @SerializedName("worst_scope")
    val worstScope: String? = null,
    @SerializedName("worst_scope_accuracy")
    val worstScopeAccuracy: Double? = null,
    @SerializedName("journaling_streak")
    val journalingStreak: Int = 0,
    @SerializedName("insights")
    val insights: List<String> = emptyList(),
)

data class JournalPatternsResponseData(
    @SerializedName("profile_id")
    val profileId: Int,
    @SerializedName("patterns")
    val patterns: JournalPatternAnalysisData,
)

data class JournalPatternAnalysisData(
    @SerializedName("patterns_found")
    val patternsFound: Boolean = false,
    @SerializedName("message")
    val message: String? = null,
    @SerializedName("patterns")
    val patterns: List<JournalPatternData> = emptyList(),
    @SerializedName("by_day")
    val byDay: Map<String, Double> = emptyMap(),
    @SerializedName("sample_size")
    val sampleSize: Int = 0,
)

data class JournalPatternData(
    @SerializedName("type")
    val type: String,
    @SerializedName("value")
    val value: String? = null,
    @SerializedName("accuracy")
    val accuracy: Double? = null,
    @SerializedName("insight")
    val insight: String,
)

data class JournalReportRequestData(
    @SerializedName("profile_id")
    val profileId: Int,
    @SerializedName("period")
    val period: String = "month",
)

data class JournalReportResponseData(
    @SerializedName("profile_id")
    val profileId: Int,
    @SerializedName("report")
    val report: JournalAccountabilityReportData,
)

data class JournalAccountabilityReportData(
    @SerializedName("period")
    val period: String,
    @SerializedName("generated_at")
    val generatedAt: String,
    @SerializedName("summary")
    val summary: JournalReportSummaryData,
    @SerializedName("accuracy")
    val accuracy: JournalAccuracyStatsData,
    @SerializedName("insights")
    val insights: JournalInsightsData,
    @SerializedName("patterns")
    val patterns: JournalPatternAnalysisData,
    @SerializedName("recommendations")
    val recommendations: List<JournalRecommendationData> = emptyList(),
)

data class JournalReportSummaryData(
    @SerializedName("total_readings")
    val totalReadings: Int = 0,
    @SerializedName("with_feedback")
    val withFeedback: Int = 0,
    @SerializedName("with_journal")
    val withJournal: Int = 0,
    @SerializedName("engagement_score")
    val engagementScore: Double = 0.0,
    @SerializedName("engagement_rating")
    val engagementRating: String = "",
)

data class JournalRecommendationData(
    @SerializedName("type")
    val type: String,
    @SerializedName("text")
    val text: String,
)

data class JournalDashboardData(
    val mode: JournalMode,
    val prompts: List<String>,
    val entries: List<JournalEntryCardData>,
    val stats: JournalAccuracyStatsData? = null,
    val insights: JournalInsightsData? = null,
    val patterns: JournalPatternAnalysisData? = null,
    val report: JournalAccountabilityReportData? = null,
) {
    val isRemote: Boolean
        get() = mode == JournalMode.REMOTE
}

fun LocalJournalEntryData.formattedUpdatedAt(): String = runCatching {
    DateTimeFormatter.ofPattern("MMM d, h:mm a")
        .withZone(ZoneId.systemDefault())
        .format(Instant.parse(updatedAt))
}.getOrDefault(updatedAt)

fun LocalJournalEntryData.toCardData(): JournalEntryCardData = JournalEntryCardData(
    id = id,
    scope = "journal",
    scopeLabel = "Journal Entry",
    date = updatedAt,
    formattedDate = formattedUpdatedAt(),
    hasJournal = entry.isNotBlank(),
    journalPreview = preview,
    journalFull = entry,
    feedback = outcome,
    feedbackEmoji = null,
    contentSummary = null,
    isLocalOnly = true,
)

fun defaultJournalPrompts(): List<String> = listOf(
    "What actually happened after the guidance?",
    "What part of the reading felt accurate, and what felt off?",
    "What would you repeat or change next time?",
)