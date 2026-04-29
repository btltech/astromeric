package com.astromeric.android.core.ephemeris

object SwissEphemerisBridge {
    val isAvailable: Boolean by lazy {
        runCatching {
            System.loadLibrary("swissephbridge")
        }.isSuccess
    }

    fun probe(ephemerisPath: String): String {
        check(isAvailable) { "Swiss Ephemeris native bridge is unavailable." }
        return nativeProbe(ephemerisPath)
    }

    fun calculateNatalChart(
        ephemerisPath: String,
        name: String,
        dateOfBirth: String,
        timeOfBirth: String,
        birthTimeAssumed: Boolean,
        dataQuality: String,
        timezone: String,
        houseSystem: String,
        latitude: Double,
        longitude: Double,
        utcYear: Int,
        utcMonth: Int,
        utcDay: Int,
        utcHour: Double,
    ): String {
        check(isAvailable) { "Swiss Ephemeris native bridge is unavailable." }
        return nativeCalculateNatalChart(
            ephemerisPath = ephemerisPath,
            name = name,
            dateOfBirth = dateOfBirth,
            timeOfBirth = timeOfBirth,
            birthTimeAssumed = birthTimeAssumed,
            dataQuality = dataQuality,
            timezone = timezone,
            houseSystem = houseSystem,
            latitude = latitude,
            longitude = longitude,
            utcYear = utcYear,
            utcMonth = utcMonth,
            utcDay = utcDay,
            utcHour = utcHour,
        )
    }

    fun findUpcomingExactTransits(
        ephemerisPath: String,
        natalNames: Array<String>,
        natalDegrees: DoubleArray,
        daysAhead: Int,
        startEpochMillis: Long,
    ): String {
        check(isAvailable) { "Swiss Ephemeris native bridge is unavailable." }
        return nativeFindUpcomingExactTransits(
            ephemerisPath = ephemerisPath,
            natalNames = natalNames,
            natalDegrees = natalDegrees,
            daysAhead = daysAhead,
            startEpochMillis = startEpochMillis,
        )
    }

    private external fun nativeProbe(ephemerisPath: String): String

    private external fun nativeCalculateNatalChart(
        ephemerisPath: String,
        name: String,
        dateOfBirth: String,
        timeOfBirth: String,
        birthTimeAssumed: Boolean,
        dataQuality: String,
        timezone: String,
        houseSystem: String,
        latitude: Double,
        longitude: Double,
        utcYear: Int,
        utcMonth: Int,
        utcDay: Int,
        utcHour: Double,
    ): String

    private external fun nativeFindUpcomingExactTransits(
        ephemerisPath: String,
        natalNames: Array<String>,
        natalDegrees: DoubleArray,
        daysAhead: Int,
        startEpochMillis: Long,
    ): String
}