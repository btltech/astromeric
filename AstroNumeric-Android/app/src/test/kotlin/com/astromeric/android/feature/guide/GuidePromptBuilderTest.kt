package com.astromeric.android.feature.guide

import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.GuideTone
import com.astromeric.android.core.model.LocalJournalEntryData
import com.astromeric.android.core.model.TimeConfidence
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** The Cosmic Guide gets the signs, never who the person is or where and when they were born. */
class GuidePromptBuilderTest {
    private val profile = AppProfile(
        id = 1,
        name = "Abiola Bolaji",
        dateOfBirth = "1990-06-15",
        timeOfBirth = "14:30:00",
        timeConfidence = TimeConfidence.EXACT,
        placeOfBirth = "Lagos, Nigeria",
        latitude = 6.45,
        longitude = 3.39,
        timezone = "Africa/Lagos",
    )

    private fun prompt(profile: AppProfile = this.profile) = buildGuideSystemPrompt(
        profile = profile,
        tone = GuideTone.BALANCED,
        moonSign = "Pisces",
        risingSign = "Libra",
        calendarContext = null,
    )

    @Test
    fun theNameAndBirthDetailsAreNotInThePrompt() {
        val text = prompt()
        listOf("Abiola", "Bolaji", "1990", "06-15", "14:30", "Lagos", "Nigeria", "Africa/").forEach {
            assertFalse("prompt should not contain \"$it\"", text.contains(it))
        }
    }

    @Test
    fun theSignsAreThere() {
        val text = prompt()
        assertTrue(text.contains("Sun Sign: Gemini"))
        assertTrue(text.contains("Moon Sign: Pisces"))
        assertTrue(text.contains("Rising Sign: Libra"))
        assertTrue(text.contains("deliberately not shared"))
    }

    @Test
    fun aConfirmedBirthTimeIsMarkedConfirmedAndAnUnknownOneIsNot() {
        assertTrue(prompt().contains("Birth time: confirmed"))
        val unknown = profile.copy(timeOfBirth = null, timeConfidence = TimeConfidence.UNKNOWN)
        val text = prompt(unknown)
        assertTrue(text.contains("Birth time: UNCONFIRMED"))
        assertTrue(text.contains("estimates"))
    }

    @Test
    fun noBiometricsAreMentioned() {
        assertFalse(prompt().lowercase().contains("biometric"))
    }

    @Test
    fun journalEntriesStillReachThePromptSoTheGuideCanRecallThem() {
        val entry = LocalJournalEntryData(
            id = 1,
            profileId = 1,
            entry = "I felt restless about the move",
            createdAt = "2026-09-01T10:00:00Z",
            updatedAt = "2026-09-01T10:00:00Z",
        )
        val text = buildGuideSystemPrompt(
            profile = profile,
            tone = GuideTone.BALANCED,
            moonSign = null,
            risingSign = null,
            journalEntries = listOf(entry),
            userQuery = "restless about the move",
            calendarContext = null,
        )
        assertTrue(text.contains("restless about the move"))
    }
}
