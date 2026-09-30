package com.astromeric.android.feature.profile

import org.junit.Assert.assertEquals
import org.junit.Test

class BirthplaceCandidatesTest {
    @Test
    fun nameKeepsCityRegionAndCountryWithoutRepeats() {
        // Lagos state and Lagos city are one name, so it isn't repeated.
        assertEquals("Lagos, Nigeria", birthplaceDisplayName("Lagos", "Lagos", "Nigeria", null, "lagos"))
        assertEquals("Lagos, Faro, Portugal", birthplaceDisplayName("Lagos", "Faro", "Portugal", null, "lagos"))
    }

    @Test
    fun nameFallsBackToTheFeatureThenTheQuery() {
        assertEquals("Mount Kenya", birthplaceDisplayName(null, null, null, "Mount Kenya", "kenya"))
        assertEquals("somewhere", birthplaceDisplayName(" ", null, "", null, "somewhere"))
    }

    @Test
    fun repeatsAreDroppedAndTheListIsCapped() {
        val places = listOf(
            BirthplaceCandidate("Lagos, Lagos, Nigeria", 6.45, 3.39),
            BirthplaceCandidate("lagos, lagos, nigeria", 6.46, 3.40),
            BirthplaceCandidate("Lagos, Faro, Portugal", 37.1, -8.67),
            BirthplaceCandidate("Lagos, Chile", -39.9, -72.8),
            BirthplaceCandidate("Lagos, Mexico", 21.3, -101.9),
            BirthplaceCandidate("Lagos, Spain", 40.0, -3.0),
            BirthplaceCandidate("Lagos, Ghana", 5.6, -0.2),
        )
        val result = distinctBirthplaces(places)
        assertEquals(5, result.size)
        assertEquals("Lagos, Lagos, Nigeria", result.first().displayName)
        assertEquals(listOf(6.45, 37.1, -39.9, 21.3, 40.0), result.map { it.latitude })
    }
}
