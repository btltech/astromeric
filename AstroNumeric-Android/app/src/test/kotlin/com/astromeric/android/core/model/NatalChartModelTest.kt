package com.astromeric.android.core.model

import com.google.gson.Gson
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Test

/**
 * Validates the core natal ChartData contract (the shape both the iOS and Android
 * apps consume from POST /v2/charts/natal), including snake_case → camelCase
 * mapping. Pure JVM (no device).
 */
class NatalChartModelTest {
    private val gson = Gson()

    private val natalJson = """
        {
          "planets": [
            {"name":"Sun","sign":"Gemini","degree":24.5,"absolute_degree":84.5,"house":10,"retrograde":false,"dignity":"none"},
            {"name":"Moon","sign":"Pisces","degree":12.1,"absolute_degree":342.1,"house":7,"retrograde":false}
          ],
          "points": [],
          "houses": [
            {"house":1,"sign":"Virgo","degree":15.0},
            {"house":10,"sign":"Gemini","degree":20.0}
          ],
          "aspects": [
            {"planet_a":"Sun","planet_b":"Moon","type":"square","orb":2.3,"strength":0.7}
          ],
          "metadata": {
            "name":"Test","date_of_birth":"1990-06-15","time_of_birth":"14:30",
            "timezone":"America/New_York","house_system":"Placidus","data_quality":"full"
          }
        }
    """.trimIndent()

    @Test
    fun natalChart_planets_parse_with_snake_case() {
        val chart = gson.fromJson(natalJson, ChartData::class.java)

        assertEquals(2, chart.planets.size)
        val sun = chart.planets[0]
        assertEquals("Sun", sun.name)
        assertEquals("Gemini", sun.sign)
        assertEquals(84.5, sun.absoluteDegree!!, 0.0001)
        assertEquals(10, sun.house)
        assertFalse(sun.retrograde == true)
    }

    @Test
    fun natalChart_houses_and_aspects_parse() {
        val chart = gson.fromJson(natalJson, ChartData::class.java)

        assertEquals(2, chart.houses.size)
        assertEquals(1, chart.houses[0].house)
        assertEquals("Virgo", chart.houses[0].sign)

        assertEquals(1, chart.aspects.size)
        val aspect = chart.aspects[0]
        assertEquals("Sun", aspect.planetA)
        assertEquals("Moon", aspect.planetB)
        assertEquals("square", aspect.type)
        assertEquals(2.3, aspect.orb!!, 0.0001)
    }

    @Test
    fun natalChart_metadata_maps_snake_case_keys() {
        val chart = gson.fromJson(natalJson, ChartData::class.java)

        assertNotNull(chart.metadata)
        assertEquals("1990-06-15", chart.metadata?.dateOfBirth)
        assertEquals("America/New_York", chart.metadata?.timezone)
        assertEquals("Placidus", chart.metadata?.houseSystem)
        assertEquals("full", chart.metadata?.dataQuality)
    }

    @Test
    fun natalChartRequest_serializes_profile_and_lang() {
        val request = NatalChartRequest(
            profile = ProfilePayload(
                name = "Test",
                dateOfBirth = "1990-06-15",
                timeOfBirth = null,
                placeOfBirth = null,
                latitude = null,
                longitude = null,
                timezone = null,
                houseSystem = null,
            ),
        )
        val json = gson.toJson(request)
        assertEquals(true, json.contains("\"profile\""))
        assertEquals(true, json.contains("\"lang\""))
    }
}
