package com.astromeric.android.core.data.preferences

import android.content.Context
import com.astromeric.android.BuildConfig
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.core.doublePreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.emptyPreferences
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringSetPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.astromeric.android.core.model.AuthSessionData
import com.astromeric.android.core.model.AppLanguage
import com.astromeric.android.core.model.AlertFrequency
import com.astromeric.android.core.model.GuideTone
import com.astromeric.android.core.model.LocalJournalEntryData
import com.astromeric.android.core.model.LocalHabitData
import com.astromeric.android.core.model.SavedRelationshipData
import com.astromeric.android.core.model.TimingActivity
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import java.io.IOException
import java.time.Instant

private val Context.dataStore by preferencesDataStore(name = "astronumeric_app_preferences")

class AppPreferencesStore(
    private val context: Context,
) {
    private val gson = Gson()
    private val localJournalEntriesType = object : TypeToken<List<LocalJournalEntryData>>() {}.type
    private val localHabitsType = object : TypeToken<List<LocalHabitData>>() {}.type
    private val savedRelationshipsType = object : TypeToken<List<SavedRelationshipData>>() {}.type
    private val selectedProfileIdKey = intPreferencesKey("selected_profile_id")
    private val initialOnboardingCompletedKey = booleanPreferencesKey("initial_onboarding_completed")
    private val personalModeEnabledKey = booleanPreferencesKey("personal_mode_enabled")
    private val hideSensitiveDetailsKey = booleanPreferencesKey("hide_sensitive_details")
    private val highContrastEnabledKey = booleanPreferencesKey("high_contrast_enabled")
    private val largeTextEnabledKey = booleanPreferencesKey("large_text_enabled")
    private val appLanguageKey = stringPreferencesKey("app_language")
    private val guideToneKey = stringPreferencesKey("guide_tone")
    private val guideCalendarContextEnabledKey = booleanPreferencesKey("guide_calendar_context_enabled")
    private val guideBiometricContextEnabledKey = booleanPreferencesKey("guide_biometric_context_enabled")
    private val notifyDailyReadingKey = booleanPreferencesKey("notify_daily_reading")
    private val notifyMoonEventsKey = booleanPreferencesKey("notify_moon_events")
    private val notifyHabitReminderKey = booleanPreferencesKey("notify_habit_reminder")
    private val notifyTimingAlertKey = booleanPreferencesKey("notify_timing_alert")
    private val notifyTransitAlertKey = booleanPreferencesKey("notify_transit_alert")
    private val transitAlertsMajorOnlyKey = booleanPreferencesKey("transit_alerts_major_only")
    private val mercuryRetrogradeAlertsKey = booleanPreferencesKey("alerts_mercury_retrograde")
    private val alertFrequencyKey = stringPreferencesKey("alerts_frequency")
    private val dailyReadingHourKey = intPreferencesKey("notify_daily_reading_hour")
    private val dailyReadingMinuteKey = intPreferencesKey("notify_daily_reading_minute")
    private val habitReminderHourKey = intPreferencesKey("notify_habit_reminder_hour")
    private val habitReminderMinuteKey = intPreferencesKey("notify_habit_reminder_minute")
    private val timingAlertHourKey = intPreferencesKey("notify_timing_alert_hour")
    private val timingAlertMinuteKey = intPreferencesKey("notify_timing_alert_minute")
    private val transitAlertHourKey = intPreferencesKey("notify_transit_alert_hour")
    private val transitAlertMinuteKey = intPreferencesKey("notify_transit_alert_minute")
    private val timingAlertActivityKey = stringPreferencesKey("notify_timing_activity")
    private val transitSubscriptionEmailKey = stringPreferencesKey("transit_subscription_email")
    private val authAccessTokenKey = stringPreferencesKey("auth_access_token")
    private val authUserIdKey = stringPreferencesKey("auth_user_id")
    private val authUserEmailKey = stringPreferencesKey("auth_user_email")
    private val authUserPaidKey = booleanPreferencesKey("auth_user_paid")
    private val tonePreferenceKey = doublePreferencesKey("tone_preference")
    private val completedLearningModulesKey = stringSetPreferencesKey("completed_learning_modules")
    private val savedRelationshipsKey = stringPreferencesKey("saved_relationships")
    private val localHabitsKey = stringPreferencesKey("local_habits")
    private val localJournalEntriesKey = stringPreferencesKey("local_journal_entries")

    val selectedProfileId: Flow<Int?> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[selectedProfileIdKey] }

    val initialOnboardingCompleted: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[initialOnboardingCompletedKey] ?: false }

    val personalModeEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[personalModeEnabledKey] ?: BuildConfig.PERSONAL_MODE }

    val tonePreference: Flow<Double> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[tonePreferenceKey] ?: 50.0 }

    val hideSensitiveDetailsEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[hideSensitiveDetailsKey] ?: false }

    val highContrastEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[highContrastEnabledKey] ?: false }

    val largeTextEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[largeTextEnabledKey] ?: false }

    val appLanguage: Flow<AppLanguage> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences ->
            AppLanguage.fromTag(preferences[appLanguageKey]) ?: AppLanguage.defaultFromSystem()
        }

    val guideTone: Flow<GuideTone> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> GuideTone.fromWireValue(preferences[guideToneKey]) }

    val guideCalendarContextEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[guideCalendarContextEnabledKey] ?: false }

    val guideBiometricContextEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[guideBiometricContextEnabledKey] ?: false }

    val notifyDailyReadingEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[notifyDailyReadingKey] ?: false }

    val notifyMoonEventsEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[notifyMoonEventsKey] ?: false }

    val notifyHabitReminderEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[notifyHabitReminderKey] ?: false }

    val notifyTimingAlertEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[notifyTimingAlertKey] ?: false }

    val notifyTransitAlertEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[notifyTransitAlertKey] ?: false }

    val transitAlertsMajorOnly: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[transitAlertsMajorOnlyKey] ?: false }

    val mercuryRetrogradeAlertsEnabled: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[mercuryRetrogradeAlertsKey] ?: true }

    val alertFrequency: Flow<AlertFrequency> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> AlertFrequency.fromWireValue(preferences[alertFrequencyKey]) }

    val dailyReadingHour: Flow<Int> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[dailyReadingHourKey] ?: 7 }

    val dailyReadingMinute: Flow<Int> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[dailyReadingMinuteKey] ?: 0 }

    val habitReminderHour: Flow<Int> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[habitReminderHourKey] ?: 20 }

    val habitReminderMinute: Flow<Int> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[habitReminderMinuteKey] ?: 0 }

    val timingAlertHour: Flow<Int> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[timingAlertHourKey] ?: 10 }

    val timingAlertMinute: Flow<Int> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[timingAlertMinuteKey] ?: 0 }

    val transitAlertHour: Flow<Int> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[transitAlertHourKey] ?: 9 }

    val transitAlertMinute: Flow<Int> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[transitAlertMinuteKey] ?: 0 }

    val timingAlertActivity: Flow<TimingActivity> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> TimingActivity.fromWireValue(preferences[timingAlertActivityKey]) ?: TimingActivity.CREATIVE_WORK }

    val transitSubscriptionEmail: Flow<String> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[transitSubscriptionEmailKey].orEmpty() }

    val authAccessToken: Flow<String> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[authAccessTokenKey].orEmpty() }

    val authUserId: Flow<String> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[authUserIdKey].orEmpty() }

    val authUserEmail: Flow<String> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[authUserEmailKey].orEmpty() }

    val authUserPaid: Flow<Boolean> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) emit(emptyPreferences()) else throw exception
        }
        .map { preferences -> preferences[authUserPaidKey] ?: false }

    val completedLearningModuleIds: Flow<Set<String>> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> preferences[completedLearningModulesKey] ?: emptySet() }

    val savedRelationships: Flow<List<SavedRelationshipData>> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> decodeRelationships(preferences[savedRelationshipsKey]) }

    val localHabits: Flow<List<LocalHabitData>> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> decodeLocalHabits(preferences[localHabitsKey]) }

    val localJournalEntries: Flow<List<LocalJournalEntryData>> = context.dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences -> decodeLocalJournalEntries(preferences[localJournalEntriesKey]) }

    suspend fun setSelectedProfileId(id: Int?) {
        context.dataStore.edit { preferences ->
            if (id == null) {
                preferences.remove(selectedProfileIdKey)
            } else {
                preferences[selectedProfileIdKey] = id
            }
        }
    }

    suspend fun setInitialOnboardingCompleted(completed: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[initialOnboardingCompletedKey] = completed
        }
    }

    suspend fun setPersonalModeEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[personalModeEnabledKey] = enabled
        }
    }

    suspend fun setTonePreference(value: Double) {
        context.dataStore.edit { preferences ->
            preferences[tonePreferenceKey] = value
        }
    }

    suspend fun setHideSensitiveDetailsEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[hideSensitiveDetailsKey] = enabled
        }
    }

    suspend fun setHighContrastEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[highContrastEnabledKey] = enabled
        }
    }

    suspend fun setLargeTextEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[largeTextEnabledKey] = enabled
        }
    }

    suspend fun setAppLanguage(language: AppLanguage) {
        context.dataStore.edit { preferences ->
            preferences[appLanguageKey] = language.tag
        }
    }

    suspend fun appLanguageValue(): AppLanguage = appLanguage.first()

    suspend fun scrubStoredSensitiveDetails() {
        context.dataStore.edit { preferences ->
            val current = decodeRelationships(preferences[savedRelationshipsKey])
            if (current.isNotEmpty()) {
                preferences[savedRelationshipsKey] = gson.toJson(current.map { it.redactedCopy() })
            }
        }
    }

    suspend fun setGuideTone(tone: GuideTone) {
        context.dataStore.edit { preferences ->
            preferences[guideToneKey] = tone.wireValue
        }
    }

    suspend fun setGuideCalendarContextEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[guideCalendarContextEnabledKey] = enabled
        }
    }

    suspend fun setGuideBiometricContextEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[guideBiometricContextEnabledKey] = enabled
        }
    }

    suspend fun setNotifyDailyReadingEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[notifyDailyReadingKey] = enabled
        }
    }

    suspend fun setNotifyMoonEventsEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[notifyMoonEventsKey] = enabled
        }
    }

    suspend fun setNotifyHabitReminderEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[notifyHabitReminderKey] = enabled
        }
    }

    suspend fun setNotifyTimingAlertEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[notifyTimingAlertKey] = enabled
        }
    }

    suspend fun setNotifyTransitAlertEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[notifyTransitAlertKey] = enabled
        }
    }

    suspend fun setTransitAlertsMajorOnly(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[transitAlertsMajorOnlyKey] = enabled
        }
    }

    suspend fun setMercuryRetrogradeAlertsEnabled(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[mercuryRetrogradeAlertsKey] = enabled
        }
    }

    suspend fun setAlertFrequency(frequency: AlertFrequency) {
        context.dataStore.edit { preferences ->
            preferences[alertFrequencyKey] = frequency.wireValue
        }
    }

    suspend fun setDailyReadingTime(hour: Int, minute: Int) {
        context.dataStore.edit { preferences ->
            preferences[dailyReadingHourKey] = hour
            preferences[dailyReadingMinuteKey] = minute
        }
    }

    suspend fun setHabitReminderTime(hour: Int, minute: Int) {
        context.dataStore.edit { preferences ->
            preferences[habitReminderHourKey] = hour
            preferences[habitReminderMinuteKey] = minute
        }
    }

    suspend fun setTimingAlertTime(hour: Int, minute: Int) {
        context.dataStore.edit { preferences ->
            preferences[timingAlertHourKey] = hour
            preferences[timingAlertMinuteKey] = minute
        }
    }

    suspend fun setTransitAlertTime(hour: Int, minute: Int) {
        context.dataStore.edit { preferences ->
            preferences[transitAlertHourKey] = hour
            preferences[transitAlertMinuteKey] = minute
        }
    }

    suspend fun setTimingAlertActivity(activity: TimingActivity) {
        context.dataStore.edit { preferences ->
            preferences[timingAlertActivityKey] = activity.wireValue
        }
    }

    suspend fun setTransitSubscriptionEmail(email: String) {
        context.dataStore.edit { preferences ->
            preferences[transitSubscriptionEmailKey] = email.trim()
        }
    }

    suspend fun setAuthSession(session: AuthSessionData) {
        context.dataStore.edit { preferences ->
            preferences[authAccessTokenKey] = session.accessToken
            preferences[authUserIdKey] = session.user.id
            preferences[authUserEmailKey] = session.user.email
            preferences[authUserPaidKey] = session.user.isPaid
        }
    }

    suspend fun clearAuthSession() {
        context.dataStore.edit { preferences ->
            preferences.remove(authAccessTokenKey)
            preferences.remove(authUserIdKey)
            preferences.remove(authUserEmailKey)
            preferences.remove(authUserPaidKey)
        }
    }

    suspend fun activeAuthAccessToken(): String? {
        if (personalModeEnabled.first()) {
            return null
        }
        return authAccessToken.first().takeIf { it.isNotBlank() }
    }

    suspend fun setLearningModuleCompleted(moduleId: String, completed: Boolean) {
        context.dataStore.edit { preferences ->
            val current = preferences[completedLearningModulesKey].orEmpty().toMutableSet()
            if (completed) {
                current.add(moduleId)
            } else {
                current.remove(moduleId)
            }
            preferences[completedLearningModulesKey] = current
        }
    }

    suspend fun saveRelationship(relationship: SavedRelationshipData) {
        context.dataStore.edit { preferences ->
            val current = decodeRelationships(preferences[savedRelationshipsKey]).toMutableList()
            val existingIndex = current.indexOfFirst { it.pairMatches(relationship) }
            val updated = if (existingIndex >= 0) {
                relationship.copy(
                    id = current[existingIndex].id,
                    createdAt = current[existingIndex].createdAt,
                    updatedAt = Instant.now().toString(),
                )
            } else {
                relationship.copy(updatedAt = Instant.now().toString())
            }

            if (existingIndex >= 0) {
                current.removeAt(existingIndex)
            }
            current.add(0, updated)
            preferences[savedRelationshipsKey] = gson.toJson(current)
        }
    }

    suspend fun deleteRelationship(relationshipId: String) {
        context.dataStore.edit { preferences ->
            val current = decodeRelationships(preferences[savedRelationshipsKey])
                .filterNot { it.id == relationshipId }
            preferences[savedRelationshipsKey] = gson.toJson(current)
        }
    }

    suspend fun localHabitsValue(): List<LocalHabitData> = localHabits.first()

    suspend fun setLocalHabits(habits: List<LocalHabitData>) {
        context.dataStore.edit { preferences ->
            preferences[localHabitsKey] = gson.toJson(habits)
        }
    }

    suspend fun upsertLocalHabit(habit: LocalHabitData) {
        context.dataStore.edit { preferences ->
            val current = decodeLocalHabits(preferences[localHabitsKey]).toMutableList()
            val existingIndex = current.indexOfFirst { it.id == habit.id }
            if (existingIndex >= 0) {
                current[existingIndex] = habit
            } else {
                current.add(0, habit)
            }
            preferences[localHabitsKey] = gson.toJson(current)
        }
    }

    suspend fun deleteLocalHabit(habitId: String) {
        context.dataStore.edit { preferences ->
            val current = decodeLocalHabits(preferences[localHabitsKey])
                .filterNot { it.id == habitId }
            preferences[localHabitsKey] = gson.toJson(current)
        }
    }

    suspend fun localJournalEntriesValue(): List<LocalJournalEntryData> = localJournalEntries.first()

    suspend fun upsertLocalJournalEntry(entry: LocalJournalEntryData) {
        context.dataStore.edit { preferences ->
            val current = decodeLocalJournalEntries(preferences[localJournalEntriesKey]).toMutableList()
            val existingIndex = current.indexOfFirst {
                it.profileId == entry.profileId && it.id == entry.id
            }
            if (existingIndex >= 0) {
                current[existingIndex] = entry
            } else {
                current.add(entry)
            }
            preferences[localJournalEntriesKey] = gson.toJson(current)
        }
    }

    suspend fun deleteLocalJournalEntry(profileId: Int, entryId: Int) {
        context.dataStore.edit { preferences ->
            val current = decodeLocalJournalEntries(preferences[localJournalEntriesKey])
                .filterNot { it.profileId == profileId && it.id == entryId }
            preferences[localJournalEntriesKey] = gson.toJson(current)
        }
    }

    private fun decodeRelationships(raw: String?): List<SavedRelationshipData> {
        if (raw.isNullOrBlank()) {
            return emptyList()
        }
        return runCatching {
            gson.fromJson<List<SavedRelationshipData>>(raw, savedRelationshipsType)
        }.getOrDefault(emptyList())
    }

    private fun decodeLocalHabits(raw: String?): List<LocalHabitData> {
        if (raw.isNullOrBlank()) {
            return emptyList()
        }
        return runCatching {
            gson.fromJson<List<LocalHabitData>>(raw, localHabitsType)
        }.getOrDefault(emptyList())
    }

    private fun decodeLocalJournalEntries(raw: String?): List<LocalJournalEntryData> {
        if (raw.isNullOrBlank()) {
            return emptyList()
        }
        return runCatching {
            gson.fromJson<List<LocalJournalEntryData>>(raw, localJournalEntriesType)
        }.getOrDefault(emptyList())
    }
}
