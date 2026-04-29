package com.astromeric.android.core.data.repository

import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.CreateHabitRequestData
import com.astromeric.android.core.model.LocalHabitData
import com.astromeric.android.core.model.habitEmojiForCategory
import com.astromeric.android.core.model.toLocalHabit
import com.astromeric.android.core.model.toggledForToday
import kotlinx.coroutines.flow.Flow
import java.util.UUID

class HabitRepository(
    private val preferencesStore: AppPreferencesStore,
    private val remoteDataSource: AstroRemoteDataSource,
) {
    val localHabits: Flow<List<LocalHabitData>> = preferencesStore.localHabits

    suspend fun refreshHabits(): Result<List<LocalHabitData>> {
        val result = remoteDataSource.listHabits()
            .map { remoteHabits -> remoteHabits.map { it.toLocalHabit() } }

        result.onSuccess { habits ->
            preferencesStore.setLocalHabits(habits)
        }

        return result.recoverCatching {
            preferencesStore.localHabitsValue()
        }
    }

    suspend fun createHabit(
        name: String,
        category: String,
        description: String = "",
    ): Result<LocalHabitData> {
        val trimmedName = name.trim()
        val trimmedDescription = description.trim()

        val remoteResult = remoteDataSource.createHabit(
            CreateHabitRequestData(
                name = trimmedName,
                category = category,
                description = trimmedDescription,
            ),
        ).map { it.toLocalHabit() }

        val localHabit = remoteResult.getOrElse {
            LocalHabitData(
                id = UUID.randomUUID().toString(),
                name = trimmedName,
                category = category,
                description = trimmedDescription,
                emoji = habitEmojiForCategory(category),
                currentStreak = 0,
                longestStreak = 0,
                completionRate = 0.0,
                isCompletedToday = false,
            )
        }

        preferencesStore.upsertLocalHabit(localHabit)
        return Result.success(localHabit)
    }

    suspend fun toggleHabitCompletion(habit: LocalHabitData): Result<LocalHabitData> {
        val updated = habit.toggledForToday()
        preferencesStore.upsertLocalHabit(updated)

        if (habit.id.toIntOrNull() == null) {
            return Result.success(updated)
        }

        return remoteDataSource.logHabitEntry(
            habitId = habit.id,
            completed = updated.isCompletedToday,
        ).map {
            updated.copy(
                currentStreak = it.streakDays,
                longestStreak = maxOf(updated.longestStreak, it.streakDays),
            )
        }.onSuccess { synced ->
            preferencesStore.upsertLocalHabit(synced)
        }.onFailure {
            preferencesStore.upsertLocalHabit(habit)
        }
    }

    suspend fun deleteHabit(habitId: String) {
        preferencesStore.deleteLocalHabit(habitId)
    }
}