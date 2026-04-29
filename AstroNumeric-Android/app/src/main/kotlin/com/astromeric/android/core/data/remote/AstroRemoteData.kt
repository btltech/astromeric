package com.astromeric.android.core.data.remote

import com.astromeric.android.BuildConfig
import com.astromeric.android.core.model.AffirmationData
import com.astromeric.android.core.model.AIExplainRequestData
import com.astromeric.android.core.model.AIExplainResponseData
import com.astromeric.android.core.model.AlertFrequency
import com.astromeric.android.core.model.AlertPreferencesData
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.AuthRequestData
import com.astromeric.android.core.model.AuthSessionData
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.CompositeChartData
import com.astromeric.android.core.model.CompatibilityMode
import com.astromeric.android.core.model.CompatibilityPairRequest
import com.astromeric.android.core.model.CompatibilityReportData
import com.astromeric.android.core.model.CosmicGuideChatData
import com.astromeric.android.core.model.CosmicGuideChatRequestData
import com.astromeric.android.core.model.CreateHabitRequestData
import com.astromeric.android.core.model.DailyTransitReportData
import com.astromeric.android.core.model.DeviceTokenRequestData
import com.astromeric.android.core.model.DailyForecastData
import com.astromeric.android.core.model.DoDontData
import com.astromeric.android.core.model.ExactTransitAspectData
import com.astromeric.android.core.model.ForecastRequest
import com.astromeric.android.core.model.AddFriendRequestData
import com.astromeric.android.core.model.CompareAllFriendsRequestData
import com.astromeric.android.core.model.FriendCompatibilityData
import com.astromeric.android.core.model.FriendProfileData
import com.astromeric.android.core.model.GlossaryEntryData
import com.astromeric.android.core.model.HabitEntryData
import com.astromeric.android.core.model.HabitResponseData
import com.astromeric.android.core.model.JournalEntryActionData
import com.astromeric.android.core.model.JournalEntryRequestData
import com.astromeric.android.core.model.JournalOutcome
import com.astromeric.android.core.model.JournalOutcomeActionData
import com.astromeric.android.core.model.JournalOutcomeRequestData
import com.astromeric.android.core.model.JournalPatternsResponseData
import com.astromeric.android.core.model.JournalPromptsData
import com.astromeric.android.core.model.JournalReadingsData
import com.astromeric.android.core.model.JournalReportRequestData
import com.astromeric.android.core.model.JournalReportResponseData
import com.astromeric.android.core.model.JournalStatsResponseData
import com.astromeric.android.core.model.LearningModuleData
import com.astromeric.android.core.model.LogHabitEntryRequestData
import com.astromeric.android.core.model.PaginatedGlossaryEntriesData
import com.astromeric.android.core.model.PaginatedLearningModulesData
import com.astromeric.android.core.model.LifePhaseData
import com.astromeric.android.core.model.MorningBriefData
import com.astromeric.android.core.model.MoonEventsData
import com.astromeric.android.core.model.MoonPhaseInfoData
import com.astromeric.android.core.model.MoonRitualRequest
import com.astromeric.android.core.model.MoonRitualSummary
import com.astromeric.android.core.model.NatalChartRequest
import com.astromeric.android.core.model.NumerologyData
import com.astromeric.android.core.model.NumerologyRequestData
import com.astromeric.android.core.model.ProfilePayload
import com.astromeric.android.core.model.ProgressedChartRequestData
import com.astromeric.android.core.model.RelationshipEventData
import com.astromeric.android.core.model.RelationshipBestDaysData
import com.astromeric.android.core.model.RelationshipEventsData
import com.astromeric.android.core.model.RelationshipPhasesData
import com.astromeric.android.core.model.RelationshipTimingData
import com.astromeric.android.core.model.RelationshipTimelineData
import com.astromeric.android.core.model.RelationshipTimelineRequest
import com.astromeric.android.core.model.RelationshipTimingRequest
import com.astromeric.android.core.model.RelationshipVenusStatusData
import com.astromeric.android.core.model.RemoteProfileDto
import com.astromeric.android.core.model.TarotCardData
import com.astromeric.android.core.model.TimingActivity
import com.astromeric.android.core.model.TimingAdvicePayload
import com.astromeric.android.core.model.TransitAlertSubscriptionData
import com.astromeric.android.core.model.TransitAlertSubscriptionRequestData
import com.astromeric.android.core.model.TransitDailyRequestData
import com.astromeric.android.core.model.YesNoGuidanceData
import com.astromeric.android.core.model.YearAheadForecastData
import com.astromeric.android.core.model.YearAheadRequest
import com.astromeric.android.core.model.SynastryChartData
import com.astromeric.android.core.model.ZodiacGuidanceData
import com.astromeric.android.core.model.zodiacSignName
import com.astromeric.android.core.model.toCompatibilityRequest
import com.astromeric.android.core.model.toDomain
import com.astromeric.android.core.model.toTimingAdviceRequest
import com.astromeric.android.core.model.toRemoteCreateRequest
import com.astromeric.android.core.model.toRemoteUpdateRequest
import com.astromeric.android.core.model.V2ApiResponse
import com.astromeric.android.core.model.toPayload
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.HTTP
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.POST
import retrofit2.http.Query
import java.util.concurrent.TimeUnit

interface AstroApiService {
    @POST("v2/auth/register")
    suspend fun register(
        @Body request: AuthRequestData,
    ): V2ApiResponse<AuthSessionData>

    @POST("v2/auth/login")
    suspend fun login(
        @Body request: AuthRequestData,
    ): V2ApiResponse<AuthSessionData>

    @POST("v2/notifications/register")
    suspend fun registerDeviceToken(
        @Header("Authorization") authorization: String? = null,
        @Body request: DeviceTokenRequestData,
    ): V2ApiResponse<Map<String, Boolean>>

    @HTTP(method = "DELETE", path = "v2/notifications/register", hasBody = true)
    suspend fun unregisterDeviceToken(
        @Header("Authorization") authorization: String? = null,
        @Body request: DeviceTokenRequestData,
    ): V2ApiResponse<Map<String, Boolean>>

    @GET("v2/profiles/")
    suspend fun listProfiles(
        @Header("Authorization") authorization: String,
    ): V2ApiResponse<List<RemoteProfileDto>>

    @POST("v2/profiles/")
    suspend fun createProfile(
        @Header("Authorization") authorization: String,
        @Body profile: com.astromeric.android.core.model.RemoteCreateProfileRequest,
    ): V2ApiResponse<RemoteProfileDto>

    @PUT("v2/profiles/{profileId}")
    suspend fun updateProfile(
        @Header("Authorization") authorization: String,
        @Path("profileId") profileId: Int,
        @Body profile: com.astromeric.android.core.model.RemoteUpdateProfileRequest,
    ): V2ApiResponse<RemoteProfileDto>

    @DELETE("v2/profiles/{profileId}")
    suspend fun deleteProfile(
        @Header("Authorization") authorization: String,
        @Path("profileId") profileId: Int,
    ): V2ApiResponse<Map<String, Any>>

    @POST("v2/daily/brief")
    suspend fun fetchMorningBrief(
        @Body profile: ProfilePayload,
    ): V2ApiResponse<MorningBriefData>

    @POST("v2/daily/affirmation")
    suspend fun fetchAffirmation(
        @Body profile: ProfilePayload,
    ): V2ApiResponse<AffirmationData>

    @POST("v2/daily/yes-no")
    suspend fun fetchYesNoGuidance(
        @Query("question") question: String,
        @Body profile: ProfilePayload,
    ): V2ApiResponse<YesNoGuidanceData>

    @POST("v2/daily/tarot")
    suspend fun drawTarotCard(): V2ApiResponse<TarotCardData>

    @GET("v2/daily/moon-phase")
    suspend fun fetchMoonPhase(): V2ApiResponse<MoonPhaseInfoData>

    @POST("v2/daily/do-dont")
    suspend fun fetchDoDont(
        @Body profile: ProfilePayload,
    ): V2ApiResponse<DoDontData>

    @GET("v2/learning/modules")
    suspend fun fetchLearningModules(
        @Query("category") category: String? = null,
    ): PaginatedLearningModulesData

    @GET("v2/learning/zodiac/{sign}")
    suspend fun fetchZodiacGuidance(
        @Path("sign") sign: String,
    ): V2ApiResponse<ZodiacGuidanceData>

    @GET("v2/learning/glossary")
    suspend fun fetchGlossaryEntries(
        @Query("search") search: String? = null,
        @Query("category") category: String? = null,
    ): PaginatedGlossaryEntriesData

    @POST("v2/friends/add")
    suspend fun addFriend(
        @Body request: AddFriendRequestData,
    ): V2ApiResponse<FriendProfileData>

    @GET("v2/friends/list/{ownerId}")
    suspend fun listFriends(
        @Path("ownerId") ownerId: String,
    ): V2ApiResponse<List<FriendProfileData>>

    @DELETE("v2/friends/remove/{ownerId}/{friendId}")
    suspend fun removeFriend(
        @Path("ownerId") ownerId: String,
        @Path("friendId") friendId: String,
    ): V2ApiResponse<Map<String, Int>>

    @POST("v2/friends/compare-all")
    suspend fun compareAllFriends(
        @Body request: CompareAllFriendsRequestData,
    ): V2ApiResponse<List<FriendCompatibilityData>>

    @GET("v2/habits/list")
    suspend fun listHabits(): V2ApiResponse<List<HabitResponseData>>

    @POST("v2/habits/create")
    suspend fun createHabit(
        @Body request: CreateHabitRequestData,
    ): V2ApiResponse<HabitResponseData>

    @POST("v2/habits/log-entry")
    suspend fun logHabitEntry(
        @Body request: LogHabitEntryRequestData,
    ): V2ApiResponse<HabitEntryData>

    @GET("v2/journal/prompts")
    suspend fun fetchJournalPrompts(
        @Query("scope") scope: String = "daily",
    ): V2ApiResponse<JournalPromptsData>

    @GET("v2/journal/readings/{profileId}")
    suspend fun fetchJournalReadings(
        @Header("Authorization") authorization: String,
        @Path("profileId") profileId: Int,
        @Query("limit") limit: Int = 20,
        @Query("offset") offset: Int = 0,
    ): V2ApiResponse<JournalReadingsData>

    @POST("v2/journal/entry")
    suspend fun saveJournalEntry(
        @Header("Authorization") authorization: String,
        @Body request: JournalEntryRequestData,
    ): V2ApiResponse<JournalEntryActionData>

    @POST("v2/journal/outcome")
    suspend fun saveJournalOutcome(
        @Header("Authorization") authorization: String,
        @Body request: JournalOutcomeRequestData,
    ): V2ApiResponse<JournalOutcomeActionData>

    @GET("v2/journal/stats/{profileId}")
    suspend fun fetchJournalStats(
        @Header("Authorization") authorization: String,
        @Path("profileId") profileId: Int,
    ): V2ApiResponse<JournalStatsResponseData>

    @GET("v2/journal/patterns/{profileId}")
    suspend fun fetchJournalPatterns(
        @Header("Authorization") authorization: String,
        @Path("profileId") profileId: Int,
    ): V2ApiResponse<JournalPatternsResponseData>

    @POST("v2/journal/report")
    suspend fun fetchJournalReport(
        @Header("Authorization") authorization: String,
        @Body request: JournalReportRequestData,
    ): V2ApiResponse<JournalReportResponseData>

    @POST("v2/cosmic-guide/chat")
    suspend fun fetchCosmicGuideChat(
        @Body request: CosmicGuideChatRequestData,
    ): V2ApiResponse<CosmicGuideChatData>

    @POST("v2/transits/daily")
    suspend fun fetchDailyTransits(
        @Body request: TransitDailyRequestData,
    ): V2ApiResponse<DailyTransitReportData>

    @POST("v2/transits/upcoming-exact")
    suspend fun fetchUpcomingExactTransits(
        @Query("days_ahead") daysAhead: Int,
        @Body request: TransitDailyRequestData,
    ): V2ApiResponse<List<ExactTransitAspectData>>

    @POST("v2/transits/subscribe")
    suspend fun subscribeTransitAlerts(
        @Header("Authorization") authorization: String? = null,
        @Body request: TransitAlertSubscriptionRequestData,
    ): V2ApiResponse<TransitAlertSubscriptionData>

    @GET("v2/alerts/preferences")
    suspend fun fetchAlertPreferences(
        @Header("Authorization") authorization: String,
    ): AlertPreferencesData

    @POST("v2/alerts/preferences")
    suspend fun updateAlertPreferences(
        @Header("Authorization") authorization: String,
        @Body request: AlertPreferencesData,
    ): AlertPreferencesData

    @POST("v2/relationships/timing")
    suspend fun fetchRelationshipTiming(
        @Body request: RelationshipTimingRequest,
    ): V2ApiResponse<RelationshipTimingData>

    @GET("v2/relationships/best-days/{sunSign}")
    suspend fun fetchRelationshipBestDays(
        @Path("sunSign") sunSign: String,
        @Query("days_ahead") daysAhead: Int = 30,
    ): V2ApiResponse<RelationshipBestDaysData>

    @GET("v2/relationships/events")
    suspend fun fetchRelationshipEvents(
        @Query("days_ahead") daysAhead: Int = 90,
        @Query("sun_sign") sunSign: String? = null,
    ): V2ApiResponse<RelationshipEventsData>

    @GET("v2/relationships/venus-status")
    suspend fun fetchRelationshipVenusStatus(): V2ApiResponse<RelationshipVenusStatusData>

    @GET("v2/relationships/phases")
    suspend fun fetchRelationshipPhases(): V2ApiResponse<RelationshipPhasesData>

    @POST("v2/relationships/timeline")
    suspend fun fetchRelationshipTimeline(
        @Body request: RelationshipTimelineRequest,
    ): V2ApiResponse<RelationshipTimelineData>

    @GET("v2/moon/upcoming")
    suspend fun fetchUpcomingMoonEvents(
        @Query("days") days: Int,
    ): V2ApiResponse<MoonEventsData>

    @POST("v2/moon/ritual")
    suspend fun fetchMoonRitual(
        @Body request: MoonRitualRequest,
    ): V2ApiResponse<MoonRitualSummary>

    @POST("v2/timing/advice")
    suspend fun fetchTimingAdvice(
        @Body request: com.astromeric.android.core.model.TimingAdviceRequest,
    ): V2ApiResponse<TimingAdvicePayload>

    @POST("v2/compatibility/romantic")
    suspend fun fetchRomanticCompatibility(
        @Body request: com.astromeric.android.core.model.CompatibilityPairRequest,
    ): V2ApiResponse<CompatibilityReportData>

    @POST("v2/compatibility/friendship")
    suspend fun fetchFriendshipCompatibility(
        @Body request: com.astromeric.android.core.model.CompatibilityPairRequest,
    ): V2ApiResponse<CompatibilityReportData>

    @POST("v2/year-ahead/life-phase")
    suspend fun fetchLifePhase(
        @Body profile: ProfilePayload,
    ): V2ApiResponse<LifePhaseData>

    @POST("v2/year-ahead/forecast")
    suspend fun fetchYearAheadForecast(
        @Body request: YearAheadRequest,
    ): V2ApiResponse<YearAheadForecastData>

    @POST("v2/ai/explain")
    suspend fun fetchAIExplain(
        @Header("Authorization") authorization: String? = null,
        @Body request: AIExplainRequestData,
    ): V2ApiResponse<AIExplainResponseData>

    @POST("v2/forecasts/daily")
    suspend fun fetchDailyForecast(
        @Body request: ForecastRequest,
    ): V2ApiResponse<DailyForecastData>

    @POST("v2/charts/natal")
    suspend fun fetchNatalChart(
        @Body request: NatalChartRequest,
    ): V2ApiResponse<ChartData>

    @POST("v2/charts/progressed")
    suspend fun fetchProgressedChart(
        @Body request: ProgressedChartRequestData,
    ): V2ApiResponse<ChartData>

    @POST("v2/charts/synastry")
    suspend fun fetchSynastryChart(
        @Body request: CompatibilityPairRequest,
    ): V2ApiResponse<SynastryChartData>

    @POST("v2/charts/composite")
    suspend fun fetchCompositeChart(
        @Body request: CompatibilityPairRequest,
    ): V2ApiResponse<CompositeChartData>

    @POST("v2/numerology/profile")
    suspend fun fetchNumerologyProfile(
        @Body request: NumerologyRequestData,
    ): V2ApiResponse<NumerologyData>
}

class AstroRemoteDataSource(
    private val apiService: AstroApiService,
) {
    suspend fun register(email: String, password: String): Result<AuthSessionData> =
        runCatching {
            apiService.register(AuthRequestData(email = email.trim(), password = password)).data
        }

    suspend fun login(email: String, password: String): Result<AuthSessionData> =
        runCatching {
            apiService.login(AuthRequestData(email = email.trim(), password = password)).data
        }

    suspend fun registerDeviceToken(
        authToken: String?,
        token: String,
        platform: String = "android",
    ): Result<Boolean> = runCatching {
        apiService.registerDeviceToken(
            authorization = authToken?.takeIf { it.isNotBlank() }?.let(::bearer),
            request = DeviceTokenRequestData(token = token, platform = platform),
        ).data["registered"] == true
    }

    suspend fun unregisterDeviceToken(
        authToken: String?,
        token: String,
        platform: String = "android",
    ): Result<Boolean> = runCatching {
        apiService.unregisterDeviceToken(
            authorization = authToken?.takeIf { it.isNotBlank() }?.let(::bearer),
            request = DeviceTokenRequestData(token = token, platform = platform),
        ).data["removed"] == true
    }

    suspend fun fetchMorningBrief(profile: AppProfile): Result<MorningBriefData> =
        runCatching {
            apiService.fetchMorningBrief(profile.toPayload()).data
        }

    suspend fun fetchAffirmation(profile: AppProfile): Result<AffirmationData> =
        runCatching {
            apiService.fetchAffirmation(profile.toPayload()).data
        }

    suspend fun fetchYesNoGuidance(
        question: String,
        profile: AppProfile,
    ): Result<YesNoGuidanceData> =
        runCatching {
            apiService.fetchYesNoGuidance(question, profile.toPayload()).data
        }

    suspend fun drawTarotCard(): Result<TarotCardData> =
        runCatching {
            apiService.drawTarotCard().data
        }

    suspend fun fetchMoonPhase(): Result<MoonPhaseInfoData> =
        runCatching {
            apiService.fetchMoonPhase().data
        }

    suspend fun fetchDoDont(profile: AppProfile): Result<DoDontData> =
        runCatching {
            apiService.fetchDoDont(profile.toPayload()).data
        }

    suspend fun fetchLearningModules(category: String? = null): Result<List<LearningModuleData>> =
        runCatching {
            val response = apiService.fetchLearningModules(category)
            if (response.data.isNotEmpty()) response.data else response.items
        }

    suspend fun fetchZodiacGuidance(profile: AppProfile): Result<ZodiacGuidanceData> =
        runCatching {
            val sign = requireNotNull(profile.zodiacSignName()) { "Zodiac sign could not be derived from profile." }
            apiService.fetchZodiacGuidance(sign).data
        }

    suspend fun fetchGlossaryEntries(search: String? = null): Result<List<GlossaryEntryData>> =
        runCatching {
            val response = apiService.fetchGlossaryEntries(search = search)
            if (response.data.isNotEmpty()) response.data else response.items
        }

    suspend fun addFriend(
        ownerId: String,
        friend: FriendProfileData,
    ): Result<FriendProfileData> =
        runCatching {
            apiService.addFriend(
                AddFriendRequestData(
                    ownerId = ownerId,
                    friend = friend,
                ),
            ).data
        }

    suspend fun listFriends(ownerId: String): Result<List<FriendProfileData>> =
        runCatching {
            apiService.listFriends(ownerId).data
        }

    suspend fun removeFriend(ownerId: String, friendId: String): Result<Boolean> =
        runCatching {
            (apiService.removeFriend(ownerId, friendId).data["removed"] ?: 0) > 0
        }

    suspend fun compareAllFriends(
        ownerId: String,
        profile: AppProfile,
    ): Result<List<FriendCompatibilityData>> =
        runCatching {
            apiService.compareAllFriends(
                CompareAllFriendsRequestData(
                    ownerId = ownerId,
                    ownerProfile = profile.toPayload(),
                ),
            ).data
        }

    suspend fun listHabits(): Result<List<HabitResponseData>> =
        runCatching {
            apiService.listHabits().data
        }

    suspend fun createHabit(request: CreateHabitRequestData): Result<HabitResponseData> =
        runCatching {
            apiService.createHabit(request).data
        }

    suspend fun logHabitEntry(
        habitId: String,
        completed: Boolean,
        note: String? = null,
    ): Result<HabitEntryData> =
        runCatching {
            apiService.logHabitEntry(
                LogHabitEntryRequestData(
                    habitId = habitId,
                    completed = completed,
                    note = note,
                ),
            ).data
        }

    suspend fun fetchJournalPrompts(scope: String = "daily"): Result<List<String>> =
        runCatching {
            apiService.fetchJournalPrompts(scope = scope).data.prompts.map { it.text }
        }

    suspend fun fetchJournalReadings(
        authToken: String,
        profileId: Int,
        limit: Int = 20,
        offset: Int = 0,
    ): Result<JournalReadingsData> =
        runCatching {
            apiService.fetchJournalReadings(
                authorization = bearer(authToken),
                profileId = profileId,
                limit = limit,
                offset = offset,
            ).data
        }

    suspend fun saveJournalEntry(
        authToken: String,
        readingId: Int,
        entry: String,
    ): Result<JournalEntryActionData> =
        runCatching {
            apiService.saveJournalEntry(
                authorization = bearer(authToken),
                request = JournalEntryRequestData(
                    readingId = readingId,
                    entry = entry,
                ),
            ).data
        }

    suspend fun saveJournalOutcome(
        authToken: String,
        readingId: Int,
        outcome: JournalOutcome,
        notes: String? = null,
    ): Result<JournalOutcomeActionData> =
        runCatching {
            apiService.saveJournalOutcome(
                authorization = bearer(authToken),
                request = JournalOutcomeRequestData(
                    readingId = readingId,
                    outcome = outcome.wireValue,
                    notes = notes,
                ),
            ).data
        }

    suspend fun fetchJournalStats(
        authToken: String,
        profileId: Int,
    ): Result<JournalStatsResponseData> =
        runCatching {
            apiService.fetchJournalStats(
                authorization = bearer(authToken),
                profileId = profileId,
            ).data
        }

    suspend fun fetchJournalPatterns(
        authToken: String,
        profileId: Int,
    ): Result<JournalPatternsResponseData> =
        runCatching {
            apiService.fetchJournalPatterns(
                authorization = bearer(authToken),
                profileId = profileId,
            ).data
        }

    suspend fun fetchJournalReport(
        authToken: String,
        profileId: Int,
        period: String = "month",
    ): Result<JournalReportResponseData> =
        runCatching {
            apiService.fetchJournalReport(
                authorization = bearer(authToken),
                request = JournalReportRequestData(
                    profileId = profileId,
                    period = period,
                ),
            ).data
        }

    suspend fun fetchCosmicGuideChat(request: CosmicGuideChatRequestData): Result<CosmicGuideChatData> =
        runCatching {
            apiService.fetchCosmicGuideChat(request).data
        }

    suspend fun fetchDailyTransits(profile: AppProfile): Result<DailyTransitReportData> =
        runCatching {
            apiService.fetchDailyTransits(TransitDailyRequestData(profile = profile.toPayload())).data
        }

    suspend fun fetchUpcomingExactTransits(
        profile: AppProfile,
        daysAhead: Int = 7,
    ): Result<List<ExactTransitAspectData>> =
        runCatching {
            apiService.fetchUpcomingExactTransits(
                daysAhead = daysAhead,
                request = TransitDailyRequestData(profile = profile.toPayload()),
            ).data
        }

    suspend fun fetchRelationshipTiming(
        profile: AppProfile,
        comparisonProfile: AppProfile? = null,
    ): Result<RelationshipTimingData> =
        runCatching {
            apiService.fetchRelationshipTiming(
                RelationshipTimingRequest(
                    sunSign = requireNotNull(profile.zodiacSignName()) { "Relationship timing requires a valid date of birth." }
                        .replaceFirstChar { it.uppercase() },
                    partnerSign = comparisonProfile?.zodiacSignName()?.replaceFirstChar { it.uppercase() },
                ),
            ).data
        }

    suspend fun fetchRelationshipBestDays(
        profile: AppProfile,
        daysAhead: Int = 30,
    ): Result<RelationshipBestDaysData> =
        runCatching {
            apiService.fetchRelationshipBestDays(
                sunSign = requireNotNull(profile.zodiacSignName()) { "Best relationship days require a valid date of birth." }
                    .replaceFirstChar { it.uppercase() },
                daysAhead = daysAhead,
            ).data
        }

    suspend fun fetchRelationshipEvents(
        profile: AppProfile? = null,
        daysAhead: Int = 90,
    ): Result<RelationshipEventsData> =
        runCatching {
            apiService.fetchRelationshipEvents(
                daysAhead = daysAhead,
                sunSign = profile?.zodiacSignName()?.replaceFirstChar { it.uppercase() },
            ).data
        }

    suspend fun fetchRelationshipVenusStatus(): Result<RelationshipVenusStatusData> =
        runCatching {
            apiService.fetchRelationshipVenusStatus().data
        }

    suspend fun fetchRelationshipPhases(): Result<RelationshipPhasesData> =
        runCatching {
            apiService.fetchRelationshipPhases().data
        }

    suspend fun fetchRelationshipTimeline(
        profile: AppProfile,
        comparisonProfile: AppProfile? = null,
        monthsAhead: Int = 6,
    ): Result<RelationshipTimelineData> =
        runCatching {
            apiService.fetchRelationshipTimeline(
                RelationshipTimelineRequest(
                    sunSign = requireNotNull(profile.zodiacSignName()) { "Relationship timeline requires a valid date of birth." }
                        .replaceFirstChar { it.uppercase() },
                    partnerSign = comparisonProfile?.zodiacSignName()?.replaceFirstChar { it.uppercase() },
                    monthsAhead = monthsAhead,
                ),
            ).data
        }

    suspend fun fetchUpcomingMoonEvents(days: Int = 30): Result<MoonEventsData> =
        runCatching {
            apiService.fetchUpcomingMoonEvents(days).data
        }

    suspend fun fetchMoonRitual(profile: AppProfile?): Result<MoonRitualSummary> =
        runCatching {
            apiService.fetchMoonRitual(MoonRitualRequest(profile = profile?.toPayload())).data
        }

    suspend fun fetchTimingAdvice(
        activity: TimingActivity,
        profile: AppProfile,
    ): Result<TimingAdvicePayload> =
        runCatching {
            apiService.fetchTimingAdvice(profile.toTimingAdviceRequest(activity)).data
        }

    suspend fun fetchCompatibility(
        mode: CompatibilityMode,
        personA: AppProfile,
        personB: AppProfile,
    ): Result<CompatibilityReportData> =
        fetchCompatibility(mode = mode, personA = personA, personB = personB.toPayload())

    suspend fun fetchCompatibility(
        mode: CompatibilityMode,
        personA: AppProfile,
        personB: ProfilePayload,
    ): Result<CompatibilityReportData> =
        runCatching {
            val request = CompatibilityPairRequest(
                personA = personA.toPayload(),
                personB = personB,
            )
            when (mode) {
                CompatibilityMode.ROMANTIC -> apiService.fetchRomanticCompatibility(request).data
                CompatibilityMode.FRIENDSHIP -> apiService.fetchFriendshipCompatibility(request).data
            }
        }

    suspend fun fetchLifePhase(profile: AppProfile): Result<LifePhaseData> =
        runCatching {
            apiService.fetchLifePhase(profile.toPayload()).data
        }

    suspend fun fetchYearAheadForecast(
        profile: AppProfile,
        year: Int,
    ): Result<YearAheadForecastData> =
        runCatching {
            apiService.fetchYearAheadForecast(
                YearAheadRequest(
                    profile = profile.toPayload(),
                    year = year,
                ),
            ).data
        }

    suspend fun fetchAIExplain(
        authToken: String?,
        request: AIExplainRequestData,
    ): Result<AIExplainResponseData> =
        runCatching {
            apiService.fetchAIExplain(
                authorization = authToken?.takeIf { it.isNotBlank() }?.let(::bearer),
                request = request,
            ).data
        }

    suspend fun fetchDailyForecast(profile: AppProfile): Result<DailyForecastData> =
        runCatching {
            apiService.fetchDailyForecast(ForecastRequest(profile = profile.toPayload(), scope = "daily")).data
        }

    suspend fun fetchForecast(profile: AppProfile, scope: String): Result<DailyForecastData> =
        runCatching {
            apiService.fetchDailyForecast(ForecastRequest(profile = profile.toPayload(), scope = scope)).data
        }

    suspend fun fetchNatalChart(profile: AppProfile): Result<ChartData> =
        runCatching {
            apiService.fetchNatalChart(NatalChartRequest(profile = profile.toPayload())).data
        }

    suspend fun fetchProgressedChart(
        profile: AppProfile,
        targetDate: String? = null,
    ): Result<ChartData> =
        runCatching {
            apiService.fetchProgressedChart(
                ProgressedChartRequestData(
                    profile = profile.toPayload(),
                    targetDate = targetDate,
                ),
            ).data
        }

    suspend fun fetchSynastryChart(
        personA: AppProfile,
        personB: AppProfile,
    ): Result<SynastryChartData> =
        runCatching {
            apiService.fetchSynastryChart(personA.toCompatibilityRequest(personB)).data
        }

    suspend fun fetchCompositeChart(
        personA: AppProfile,
        personB: AppProfile,
    ): Result<CompositeChartData> =
        runCatching {
            apiService.fetchCompositeChart(personA.toCompatibilityRequest(personB)).data
        }

    suspend fun fetchNumerology(
        profile: AppProfile,
        method: String = "pythagorean",
    ): Result<NumerologyData> =
        runCatching {
            apiService.fetchNumerologyProfile(
                NumerologyRequestData(
                    profile = profile.toPayload(),
                    method = method,
                ),
            ).data
        }

    suspend fun listRemoteProfiles(authToken: String): Result<List<AppProfile>> =
        runCatching {
            apiService.listProfiles(bearer(authToken)).data.map { it.toDomain() }
        }

    suspend fun createRemoteProfile(authToken: String, profile: AppProfile): Result<AppProfile> =
        runCatching {
            apiService.createProfile(bearer(authToken), profile.toRemoteCreateRequest()).data.toDomain()
        }

    suspend fun updateRemoteProfile(authToken: String, profile: AppProfile): Result<AppProfile> =
        runCatching {
            apiService.updateProfile(bearer(authToken), profile.id, profile.toRemoteUpdateRequest()).data.toDomain()
        }

    suspend fun deleteRemoteProfile(authToken: String, profileId: Int): Result<Unit> =
        runCatching {
            apiService.deleteProfile(bearer(authToken), profileId)
            Unit
        }

    suspend fun subscribeTransitAlerts(
        authToken: String?,
        profile: AppProfile,
        email: String,
    ): Result<TransitAlertSubscriptionData> =
        runCatching {
            apiService.subscribeTransitAlerts(
                authorization = authToken?.takeIf { it.isNotBlank() }?.let(::bearer),
                request = TransitAlertSubscriptionRequestData(
                    email = email.trim(),
                    profileId = profile.id.takeIf { it > 0 && !authToken.isNullOrBlank() },
                    profile = profile.toPayload().takeIf { profile.id <= 0 || authToken.isNullOrBlank() },
                ),
            ).data
        }

    suspend fun fetchAlertPreferences(authToken: String): Result<AlertPreferencesData> =
        runCatching {
            apiService.fetchAlertPreferences(bearer(authToken))
        }

    suspend fun updateAlertPreferences(
        authToken: String,
        alertsEnabled: Boolean,
        frequency: AlertFrequency,
    ): Result<AlertPreferencesData> =
        runCatching {
            apiService.updateAlertPreferences(
                authorization = bearer(authToken),
                request = AlertPreferencesData(
                    alertMercuryRetrograde = alertsEnabled,
                    alertFrequency = frequency.wireValue,
                ),
            )
        }

    private fun bearer(token: String): String = "Bearer $token"

    companion object {
        fun create(): AstroRemoteDataSource {
            val logging = HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) {
                    HttpLoggingInterceptor.Level.BASIC
                } else {
                    HttpLoggingInterceptor.Level.NONE
                }
            }

            val client = OkHttpClient.Builder()
                .connectTimeout(15, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .addInterceptor(logging)
                .build()

            val retrofit = Retrofit.Builder()
                .baseUrl(BuildConfig.API_BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()

            return AstroRemoteDataSource(retrofit.create(AstroApiService::class.java))
        }
    }
}
