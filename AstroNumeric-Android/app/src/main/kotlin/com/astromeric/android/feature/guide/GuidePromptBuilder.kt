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
    isMystic: Boolean = true,
    hideSensitiveDetailsEnabled: Boolean,
    moonSign: String?,
    risingSign: String?,
    journalEntries: List<LocalJournalEntryData> = emptyList(),
    userQuery: String? = null,
    calendarContext: String?,
    biometricSnapshot: GuideBiometricSnapshot?,
    bioCosmicContext: String? = null,
): String {
    val sections = mutableListOf<String>()
    sections += """
        You are the Cosmic Guide, a polished astrologer and numerology companion for AstroNumeric.
        Be specific, emotionally accurate, and practical. Keep answers grounded in recognizable patterns instead of vague mysticism.
        End with one useful next step or reflection prompt.
    """.trimIndent()
    sections += "TONE: ${tone.prompt}"
    sections += if (isMystic) {
        "FRAMING: Use mystical, archetypal, and cosmic language. Lean into symbolic interpretation and spiritual resonance."
    } else {
        "FRAMING: Use practical, grounded, down-to-earth language. Avoid mystical jargon. Focus on actionable, real-world implications."
    }

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

    bioCosmicContext?.takeIf { it.isNotBlank() }?.let {
        sections += it
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

private val STOP_WORDS = setOf(
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
    "how", "its", "now", "old", "see", "two", "way", "who", "did", "let",
    "put", "say", "she", "too", "use", "that", "this", "with", "have",
    "from", "they", "will", "been", "more", "just", "into", "when", "your",
    "what", "some", "than", "them", "then", "well", "were", "also",
)

private fun tokenize(text: String): List<String> =
    text.lowercase()
        .split(Regex("[^a-z0-9]+"))
        .filter { it.length >= 3 && it !in STOP_WORDS }

private fun buildJournalContextBlock(
    entries: List<LocalJournalEntryData>,
    query: String?,
): String? {
    val corpus = entries.filter { it.entry.isNotBlank() }
    if (corpus.isEmpty()) return null

    val queryTerms = tokenize(query.orEmpty()).toSet()

    // Pre-tokenize all documents
    val tokenizedCorpus = corpus.map { it to tokenize(it.entry) }

    // Compute IDF: log((N + 1) / (df + 1)) with smoothing
    val N = corpus.size.toDouble()
    val idf: Map<String, Double> = if (queryTerms.isNotEmpty()) {
        queryTerms.associateWith { term ->
            val df = tokenizedCorpus.count { (_, tokens) -> term in tokens }
            Math.log((N + 1.0) / (df + 1.0)) + 1.0
        }
    } else emptyMap()

    val scoredEntries = tokenizedCorpus.map { (entry, tokens) ->
        val score = if (queryTerms.isEmpty()) {
            0.0
        } else {
            val tokenCount = tokens.size.coerceAtLeast(1)
            queryTerms.sumOf { term ->
                val tf = tokens.count { it == term }.toDouble() / tokenCount
                tf * (idf[term] ?: 1.0)
            }
        }
        entry to score
    }

    val selectedEntries = if (queryTerms.isEmpty()) {
        scoredEntries.sortedByDescending { it.first.updatedAt }
    } else {
        scoredEntries
            .filter { it.second > 0.0 }
            .sortedWith(
                compareByDescending<Pair<LocalJournalEntryData, Double>> { it.second }
                    .thenByDescending { it.first.updatedAt },
            )
    }
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