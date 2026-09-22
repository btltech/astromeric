package com.astromeric.android.feature.charts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class RelocationCoordinatesTest {

    @Test
    fun parses_dot_and_comma_decimals() {
        assertEquals(40.71 to -74.01, parseRelocationCoordinates("40.71", "-74.01"))
        assertEquals(48.85 to 2.35, parseRelocationCoordinates(" 48,85 ", "2,35"))
    }

    @Test
    fun accepts_the_range_boundaries() {
        assertEquals(90.0 to -180.0, parseRelocationCoordinates("90", "-180"))
    }

    @Test
    fun rejects_out_of_range_values() {
        assertNull(parseRelocationCoordinates("95", "10"))
        assertNull(parseRelocationCoordinates("-74.01", "400"))
    }

    @Test
    fun rejects_blank_non_numeric_and_non_finite_input() {
        assertNull(parseRelocationCoordinates("", "10"))
        assertNull(parseRelocationCoordinates("north", "10"))
        assertNull(parseRelocationCoordinates("NaN", "10"))
        assertNull(parseRelocationCoordinates("10", "Infinity"))
    }
}
