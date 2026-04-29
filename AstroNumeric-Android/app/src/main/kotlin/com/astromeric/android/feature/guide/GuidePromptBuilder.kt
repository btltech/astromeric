package com.astromeric.android.feature.guide

import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DataQuality
import com.astromeric.android.core.model.GuideTone
import com.astromeric.android.core.model.LocalJournalEntryData
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.maskedBirthTime
import com.astromeric.android.core.model.maskedBirthplace
import com.astromeric.android.core.model.maskedDateOfBirth
import com.astromeric.android.core.model.zodiacSignName

fun buildGuideSystemPrompt(
    profile: AppProfile,
    tone: GuideTone,
    hideSensitiveDetailsEnabled: Boolean,
    moonSign: String?,
    risingSign: String?,
    journalEntries: List<LocalJournalEntryData> = emptyList(),
    userQuery: String? = null,
    calendarContext: String?,
    biometricSnapshot: GuideBiometricSnapshot?,
): String {
    val sections = mutableListOf<String>()
    sections += """
        You are the Cosmic Guide, a polished astrologer and numerology companion for AstroNumeric.
        Be specific, emotionally accurate, and practical. Keep answers grounded in recognizable patterns instead of vague mysticism.
        End with one useful next step or reflection prompt.
    """.trimIndent()
    sections += "TONE: ${tone.prompt}"

    val sunSign = profile.zodiacSignName()?.replaceFirstChar { it.uppercase() } ?: "Unknown"
    sections += buildString {
        appendLine("PROFILE CONTEXT:")
        appendLine("- Name: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)}")
        appendLine("- Birth Date: ${profile.maskedDateOfBirth(hideSensitiveDetailsEnabled)}")
        appendLine("- Birth Time: ${profile.maskedBirthTime(hideSensitiveDetailsEnabled)}")
        appendLine("- Birth Place: ${profile.maskedBirthplace(hideSensitiveDetailsEnabled)}")
        appendLine("- Sun Sign: $sunSign")
        if (!moonSign.isNullOrBlank()) {
            appendLine("- Moon Sign: $moonSign")
        }
        if (!risingSign.isNullOrBlank()) {
            appendLine("- Rising Sign: $risingSign")
        }
    }.trim()

    if (profile.dataQuality != DataQuality.FULL) {
        sections += when (profile.dataQuality) {
            DataQuality.DATE_AND_PLACE -> "Birth time is approximate or unknown. Treat rising-sign and house statements as estimates, not facts."
            DataQuality.DATE_ONLY -> "Birthplace coordinates are incomplete. Focus on Sun-sign and broad timing themes instead of house-specific claims."
            DataQuality.FULL -> ""
        }
    }

    calendarContext?.takeIf { it.isNotBlank() }?.let { context ->
        sections += context
    }

    buildJournalContextBlock(
        entries = journalEntries,
        query = userQuery,
    )?.let { journalContext ->
        sections += journalContext
    }

    biometricSnapshot?.takeIf { it.hasData }?.let { snapshot ->
        sections += "TODAY'S BIOMETRIC CONTEXT:\n${snapshot.promptDescription}"
    }

    sections += """
        RESPONSE RULES:
        - Keep the answer to 2-4 short paragraphs.
        - Anchor each major claim to something concrete when possible: signs, chart factors, timing, calendar pressure, or biometric rhythm.
        - If journal entries are provided, reference the user's own past reflections when relevant.
        - Do not present astrology, biometrics, or journaling as proof of future events.
        - Do not give medical, legal, financial, or emergency instructions.
    """.trimIndent()

    return sections.filter { it.isNotBlank() }.joinToString(separator = "\n\n")
}

private fun buildJournalContextBlock(
    entries: List<LocalJournalEntryData>,
    query: String?,
): String? {
    val queryTerms = query
        .orEmpty()
        .lowercase()
        .split(Regex("[^a-z0-9]+"))
        .filter { it.length >= 3 }
        .toSet()

    val scoredEntries = entries
        .filter { it.entry.isNotBlank() }
        .map { entry ->
            val body = entry.entry.lowercase()
            val score = queryTerms.count { term -> body.contains(term) }
            entry to score
        }

    val selectedEntries = if (queryTerms.isEmpty()) {
        scoredEntries
    } else {
        scoredEntries.filter { it.second > 0 }
    }
        .sortedWith(
            compareByDescending<Pair<LocalJournalEntryData, Int>> { it.second }
                .thenByDescending { it.first.updatedAt },
        )
        .take(3)
        .map { it.first }

    if (selectedEntries.isEmpty()) {
        return null
    }

    val formattedEntries = selectedEntries.mapIndexed { index, entry ->
        val date = entry.updatedAt.take(10).ifBlank { entry.createdAt.take(10) }
        val outcome = entry.outcome?.takeIf { it.isNotBlank() }?.let { " (outcome: $it)" }.orEmpty()
        val preview = entry.entry.trim().replace(Regex("\\s+"), " ").take(300)
        "  ${index + 1}. [$date]$outcome: \"$preview\""
    }.joinToString(separator = "\n")

    return "RELEVANT JOURNAL ENTRIES (from user's past reflections):\n$formattedEntries"
}