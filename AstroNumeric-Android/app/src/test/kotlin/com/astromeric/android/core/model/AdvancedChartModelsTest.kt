package com.astromeric.android.core.model

import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Validates that the advanced-chart Gson models deserialize the exact JSON shapes
 * returned by backend/app/routers/charts.py. These run on the JVM (no device).
 */
class AdvancedChartModelsTest {
    private val gson = Gson()

    @Test
    fun profections_deserializes_all_fields() {
        val json = """
            {
              "age": 34,
              "annual_house": 11,
              "annual_lord": "Saturn",
              "annual_focus": "community, hopes, networks",
              "annual_lord_themes": "structure, discipline",
              "monthly_house": 3,
              "monthly_lord": "Mercury",
              "monthly_focus": "communication, siblings",
              "months_into_year": 2,
              "interpretation": "Year 35 activates House 11."
            }
        """.trimIndent()

        val data = gson.fromJson(json, ProfectionsData::class.java)

        assertEquals(34, data.age)
        assertEquals(11, data.annualHouse)
        assertEquals("Saturn", data.annualLord)
        assertEquals(3, data.monthlyHouse)
        assertEquals("Mercury", data.monthlyLord)
        assertEquals(2, data.monthsIntoYear)
        assertTrue(data.interpretation.isNotBlank())
    }

    @Test
    fun profections_without_ascendant_has_blank_lord_and_no_sign() {
        val json = """{"age": 12, "annual_house": 1, "annual_sign": null, "annual_lord": "", "monthly_lord": ""}"""

        val data = gson.fromJson(json, ProfectionsData::class.java)

        assertEquals("", data.annualLord)
        assertEquals(null, data.annualSign)
    }

    @Test
    fun chart_metadata_flags_approximated_positions() {
        val polar = gson.fromJson(
            """{"provider": "polar-fallback", "degraded": true, "note": "Polar latitude fallback"}""",
            ChartMetadata::class.java,
        )
        val real = gson.fromJson(
            """{"provider": "flatlib", "return_datetime_local": "2026-09-21T14:20:36-07:00"}""",
            ChartMetadata::class.java,
        )

        assertTrue(polar.isApproximated)
        assertFalse(real.isApproximated)
        assertEquals("2026-09-21T14:20:36-07:00", real.returnDatetimeLocal)
    }

    @Test
    fun declinations_deserializes_entries_and_parallels() {
        val json = """
            {
              "declinations": [
                {"name": "Sun", "longitude": 84.0, "latitude": 0.0, "declination": 23.1, "out_of_bounds": false},
                {"name": "Pluto", "longitude": 250.0, "latitude": 0.0, "declination": 24.0, "out_of_bounds": true}
              ],
              "parallels": [
                {"planet_a": "Sun", "planet_b": "Mars", "type": "parallel", "orb": 0.3, "strength": 0.8}
              ]
            }
        """.trimIndent()

        val data = gson.fromJson(json, DeclinationsData::class.java)

        assertEquals(2, data.declinations.size)
        assertEquals("Sun", data.declinations[0].name)
        assertEquals(23.1, data.declinations[0].declination, 0.0001)
        assertFalse(data.declinations[0].outOfBounds)
        assertTrue(data.declinations[1].outOfBounds)
        assertEquals(1, data.parallels.size)
        assertEquals("parallel", data.parallels[0].type)
        assertEquals("Mars", data.parallels[0].planetB)
    }

    @Test
    fun fixedStars_deserializes_list() {
        val json = """
            [
              {"planet": "Sun", "star": "Regulus", "orb": 0.4, "nature": "benefic",
               "keywords": "success, honour", "interpretation": "Sun conjunct Regulus."}
            ]
        """.trimIndent()

        val type = object : TypeToken<List<FixedStarConjunction>>() {}.type
        val list: List<FixedStarConjunction> = gson.fromJson(json, type)

        assertEquals(1, list.size)
        assertEquals("Sun", list[0].planet)
        assertEquals("Regulus", list[0].star)
        assertEquals("benefic", list[0].nature)
        assertEquals(0.4, list[0].orb, 0.0001)
    }

    @Test
    fun fixedStarRequest_serializes_snake_case() {
        val request = FixedStarsRequestData(
            planets = listOf(FixedStarPlanetInput(name = "Sun", absoluteDegree = 84.5)),
            orb = 1.0,
        )

        val json = gson.toJson(request)

        assertTrue(json.contains("\"absolute_degree\""))
        assertTrue(json.contains("\"planets\""))
        assertFalse(json.contains("absoluteDegree"))
    }
}
