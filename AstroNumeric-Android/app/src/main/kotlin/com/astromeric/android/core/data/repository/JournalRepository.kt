package com.astromeric.android.core.data.repository

import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.JournalDashboardData
import com.astromeric.android.core.model.JournalEntryCardData
import com.astromeric.android.core.model.JournalMode
import com.astromeric.android.core.model.JournalOutcome
import com.astromeric.android.core.model.LocalJournalEntryData
import com.astromeric.android.core.model.defaultJournalPrompts
import com.astromeric.android.core.model.toCardData
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.time.Instant

class JournalRepository(
    private val preferencesStore: AppPreferencesStore,
    private val remoteDataSource: AstroRemoteDataSource,
) {
    fun entriesForProfile(profileId: Int): Flow<List<LocalJournalEntryData>> =
        preferencesStore.localJournalEntries.map { entries ->
            entries.filter { it.profileId == profileId }
                .sortedByDescending { it.updatedAt }
        }

    suspend fun loadDashboard(
        profile: AppProfile,
        scope: String = "daily",
        reportPeriod: String = "month",
    ): Result<JournalDashboardData> =
        runCatching {
            if (shouldUseRemoteMode(profile)) {
                loadRemoteDashboard(profile, scope = scope, reportPeriod = reportPeriod)
            } else {
                loadLocalDashboard(profile, scope = scope)
            }
        }

    suspend fun nextEntryId(profileId: Int): Int =
        preferencesStore.localJournalEntriesValue()
            .filter { it.profileId == profileId }
            .maxOfOrNull { it.id }
            ?.plus(1)
            ?: 1

    suspend fun upsertEntry(
        profileId: Int,
        entryId: Int?,
        entry: String,
        outcome: JournalOutcome,
    ): LocalJournalEntryData {
        val existingEntries = preferencesStore.localJournalEntriesValue()
        val now = Instant.now().toString()
        val existing = existingEntries.firstOrNull { it.profileId == profileId && it.id == entryId }
        val journalEntry = LocalJournalEntryData(
            id = existing?.id ?: nextEntryId(profileId),
            profileId = profileId,
            createdAt = existing?.createdAt ?: now,
            updatedAt = now,
            entry = entry.trim(),
            outcome = outcome.wireValue,
        )
        preferencesStore.upsertLocalJournalEntry(journalEntry)
        return journalEntry
    }

    suspend fun saveReflection(
        profile: AppProfile,
        entryId: Int?,
        entry: String,
        outcome: JournalOutcome,
    ): Result<Unit> =
        runCatching {
            if (shouldUseRemoteMode(profile)) {
                saveRemoteReflection(
                    profile = profile,
                    entryId = entryId,
                    entry = entry,
                    outcome = outcome,
                )
            } else {
                upsertEntry(
                    profileId = profile.id,
                    entryId = entryId,
                    entry = entry,
                    outcome = outcome,
                )
            }
        }

    suspend fun deleteEntry(profile: AppProfile, entryId: Int): Result<Unit> =
        runCatching {
            check(!shouldUseRemoteMode(profile)) {
                "Account-synced readings can be updated, but not deleted from Android yet."
            }
            preferencesStore.deleteLocalJournalEntry(profileId = profile.id, entryId = entryId)
        }

    suspend fun fetchPrompts(scope: String = "daily"): Result<List<String>> =
        remoteDataSource.fetchJournalPrompts(scope)
            .mapCatching { prompts ->
                if (prompts.isNotEmpty()) prompts else defaultJournalPrompts()
            }

    private suspend fun shouldUseRemoteMode(profile: AppProfile): Boolean =
        profile.id > 0 && preferencesStore.activeAuthAccessToken() != null

    private suspend fun loadLocalDashboard(
        profile: AppProfile,
        scope: String,
    ): JournalDashboardData {
        val prompts = fetchPrompts(scope).getOrDefault(defaultJournalPrompts())
        val entries = preferencesStore.localJournalEntriesValue()
            .filter { it.profileId == profile.id }
            .sortedByDescending { it.updatedAt }
            .map(LocalJournalEntryData::toCardData)

        return JournalDashboardData(
            mode = JournalMode.LOCAL,
            prompts = prompts,
            entries = entries,
        )
    }

    private suspend fun loadRemoteDashboard(
        profile: AppProfile,
        scope: String,
        reportPeriod: String,
    ): JournalDashboardData = coroutineScope {
        val authToken = requireNotNull(preferencesStore.activeAuthAccessToken()) {
            "Sign in first to load synced journal data."
        }

        val promptsDeferred = async {
            remoteDataSource.fetchJournalPrompts(scope).getOrElse { defaultJournalPrompts() }
        }
        val readingsDeferred = async {
            remoteDataSource.fetchJournalReadings(
                authToken = authToken,
                profileId = profile.id,
                limit = 50,
            )
        }
        val statsDeferred = async {
            remoteDataSource.fetchJournalStats(
                authToken = authToken,
                profileId = profile.id,
            )
        }
        val patternsDeferred = async {
            remoteDataSource.fetchJournalPatterns(
                authToken = authToken,
                profileId = profile.id,
            )
        }
        val reportDeferred = async {
            remoteDataSource.fetchJournalReport(
                authToken = authToken,
                profileId = profile.id,
                period = reportPeriod,
            )
        }

        val readings = readingsDeferred.await().getOrThrow()
        val statsPayload = statsDeferred.await().getOrNull()
        val patternsPayload = patternsDeferred.await().getOrNull()
        val reportPayload = reportDeferred.await().getOrNull()

        JournalDashboardData(
            mode = JournalMode.REMOTE,
            prompts = promptsDeferred.await(),
            entries = readings.readings.map { it.toCardData() },
            stats = statsPayload?.stats ?: reportPayload?.report?.accuracy,
            insights = statsPayload?.insights ?: reportPayload?.report?.insights,
            patterns = patternsPayload?.patterns ?: reportPayload?.report?.patterns,
            report = reportPayload?.report,
        )
    }

    private suspend fun saveRemoteReflection(
        profile: AppProfile,
        entryId: Int?,
        entry: String,
        outcome: JournalOutcome,
    ) {
        val authToken = requireNotNull(preferencesStore.activeAuthAccessToken()) {
            "Sign in first to update synced journal data."
        }
        val readingId = requireNotNull(entryId) {
            "Select a synced reading before saving your reflection."
        }

        val trimmedEntry = entry.trim()
        if (trimmedEntry.isNotBlank()) {
            remoteDataSource.saveJournalEntry(
                authToken = authToken,
                readingId = readingId,
                entry = trimmedEntry,
            ).getOrThrow()
        }

        remoteDataSource.saveJournalOutcome(
            authToken = authToken,
            readingId = readingId,
            outcome = outcome,
        ).getOrThrow()
    }
}