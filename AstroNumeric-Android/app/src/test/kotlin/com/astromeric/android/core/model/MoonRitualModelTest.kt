package com.astromeric.android.core.model

import com.google.gson.Gson
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * The server now sends the Moon ritual's `avoid` as one comma-separated string.
 * The whole ritual response used to fail to read because of it.
 */
class MoonRitualModelTest {
    private val gson = Gson()

    private fun ritual(avoid: String) =
        """
        {
          "current_phase": {"phase_name": "Full Moon"},
          "moon_sign": "Pisces",
          "ritual": {
            "phase": "Full Moon", "moon_sign": "Pisces", "theme": "Release",
            "activities": ["Meditation", "Journaling"],
            "avoid": $avoid,
            "crystals": ["Moonstone"], "colors": ["Silver"], "affirmation": "I release."
          },
          "upcoming_events": []
        }
        """.trimIndent()

    @Test
    fun readsAvoidSentAsOneString() {
        val summary = gson.fromJson(
            ritual("\"Starting new ventures, Making impulsive decisions, Emotional reactivity\""),
            MoonRitualSummary::class.java,
        )
        assertEquals(
            listOf("Starting new ventures", "Making impulsive decisions", "Emotional reactivity"),
            summary.ritual?.avoid,
        )
        assertEquals(listOf("Meditation", "Journaling"), summary.ritual?.activities)
        assertEquals("Pisces", summary.moonSign)
    }

    @Test
    fun stillReadsAvoidSentAsAList() {
        val summary = gson.fromJson(ritual("[\"Gossip\", \"Overspending\"]"), MoonRitualSummary::class.java)
        assertEquals(listOf("Gossip", "Overspending"), summary.ritual?.avoid)
    }

    @Test
    fun missingOrNullAvoidIsEmpty() {
        val nulled = gson.fromJson(ritual("null"), MoonRitualSummary::class.java)
        assertTrue(nulled.ritual?.avoid?.isEmpty() == true)
        val absent = gson.fromJson(
            """{"ritual": {"phase": "New Moon"}}""",
            MoonRitualSummary::class.java,
        )
        assertTrue(absent.ritual?.avoid?.isEmpty() == true)
    }

    @Test
    fun blankPiecesAreDropped() {
        val summary = gson.fromJson(ritual("\"Rushing, , Arguing,\""), MoonRitualSummary::class.java)
        assertEquals(listOf("Rushing", "Arguing"), summary.ritual?.avoid)
    }
}
