package com.astromeric.android.app

import org.junit.Assert.assertEquals
import org.junit.Test

/** Pins down exactly what CrashReporter redacts, so its KDoc stays accurate. */
class CrashReporterRedactionTest {

    @Test
    fun redacts_values_whose_key_name_contains_a_sensitive_term() {
        val redacted = CrashReporter.redact(
            mapOf(
                "profile_name" to "Jane Doe",
                "birthDate" to "1990-05-15",
                "LATITUDE" to "40.71",
                "journalEntry" to "private text",
            ),
        )

        redacted.values.forEach { assertEquals("<redacted>", it) }
    }

    @Test
    fun keeps_values_whose_key_name_is_not_on_the_list() {
        val context = mapOf(
            "email" to "jane@example.com",
            "place" to "New York",
            "lat" to "40.71",
            "screen" to "journal",
        )

        assertEquals(context, CrashReporter.redact(context))
    }

    @Test
    fun keeps_key_names_unchanged() {
        val redacted = CrashReporter.redact(mapOf("chart_id" to "abc", "ephemeris_file" to "sepl_18.se1"))

        assertEquals(setOf("chart_id", "ephemeris_file"), redacted.keys)
        assertEquals("sepl_18.se1", redacted["ephemeris_file"])
    }
}
