package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName
import java.time.Instant
import java.time.OffsetDateTime
import java.util.UUID
import kotlin.math.max

data class HabitEntryData(
    @SerializedName("id")
    val id: String,
    @SerializedName("habit_name")
    val habitName: String,
    @SerializedName("category")
    val category: String,
    @SerializedName("date")
    val date: String,
    @SerializedName("completed")
    val completed: Boolean,
    @SerializedName("notes")
    val notes: String? = null,
    @SerializedName("streak_days")
    val streakDays: Int = 0,
)

data class HabitSummaryData(
    @SerializedName("habit_id")
    val habitId: String,
    @SerializedName("habit_name")
    val habitName: String,
    @SerializedName("total_days")
    val totalDays: Int,
    @SerializedName("completed_days")
    val completedDays: Int,
    @SerializedName("current_streak")
    val currentStreak: Int,
    @SerializedName("longest_streak")
    val longestStreak: Int,
    @SerializedName("completion_rate")
    val completionRate: Double,
    @SerializedName("last_completed")
    val lastCompleted: String? = null,
)

data class HabitResponseData(
    @SerializedName("id")
    val id: String,
    @SerializedName("name")
    val name: String,
    @SerializedName("description")
    val description: String,
    @SerializedName("category")
    val category: String,
    @SerializedName("created_date")
    val createdDate: String,
    @SerializedName("entries")
    val entries: List<HabitEntryData> = emptyList(),
    @SerializedName("summary")
    val summary: HabitSummaryData,
)

data class CreateHabitRequestData(
    @SerializedName("name")
    val name: String,
    @SerializedName("category")
    val category: String,
    @SerializedName("frequency")
    val frequency: String = "daily",
    @SerializedName("description")
    val description: String = "",
)

data class LogHabitEntryRequestData(
    @SerializedName("habit_id")
    val habitId: String,
    @SerializedName("completed")
    val completed: Boolean,
    @SerializedName("note")
    val note: String? = null,
)

data class LocalHabitData(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val category: String,
    val description: String = "",
    val emoji: String,
    val currentStreak: Int,
    val longestStreak: Int,
    val completionRate: Double,
    val isCompletedToday: Boolean,
    val lastCompleted: String? = null,
)

data class LocalHabitCategoryData(
    val id: String,
    val name: String,
    val emoji: String,
    val description: String,
    val bestPhases: List<String>,
    val avoidPhases: List<String>,
)

data class LunarHabitGuidanceData(
    val phase: String,
    val phaseName: String,
    val emoji: String,
    val theme: String,
    val bestFor: List<String>,
    val avoid: List<String>,
    val energy: String,
    val idealHabits: List<String>,
    val powerScoreModifier: Double,
)

fun HabitResponseData.toLocalHabit(): LocalHabitData =
    LocalHabitData(
        id = id,
        name = name,
        category = category,
        description = description,
        emoji = habitEmojiForCategory(category),
        currentStreak = summary.currentStreak,
        longestStreak = summary.longestStreak,
        completionRate = summary.completionRate,
        isCompletedToday = summary.lastCompleted?.let { isTodayIsoDate(it) } ?: false,
        lastCompleted = summary.lastCompleted,
    )

fun LocalHabitData.toggledForToday(): LocalHabitData {
    val now = Instant.now().toString()
    return if (isCompletedToday) {
        copy(
            isCompletedToday = false,
            currentStreak = max(0, currentStreak - 1),
            completionRate = 0.0,
            lastCompleted = null,
        )
    } else {
        val nextStreak = currentStreak + 1
        copy(
            isCompletedToday = true,
            currentStreak = nextStreak,
            longestStreak = max(longestStreak, nextStreak),
            completionRate = max(completionRate, 1.0),
            lastCompleted = now,
        )
    }
}

fun habitEmojiForCategory(category: String): String = when (category) {
    "exercise" -> "Run"
    "meditation" -> "Calm"
    "learning" -> "Learn"
    "creative" -> "Create"
    "social" -> "Social"
    "productivity" -> "Focus"
    "health" -> "Health"
    "rest" -> "Rest"
    "financial" -> "Money"
    "spiritual" -> "Spirit"
    else -> "Habit"
}

fun fallbackHabitCategories(): List<LocalHabitCategoryData> = listOf(
    LocalHabitCategoryData("exercise", "Exercise", "Run", "Physical activity and momentum.", listOf("first_quarter", "full_moon"), listOf("waning_crescent")),
    LocalHabitCategoryData("meditation", "Meditation", "Calm", "Mindfulness and stillness.", listOf("new_moon", "waning_crescent"), emptyList()),
    LocalHabitCategoryData("learning", "Learning", "Learn", "Study, repetition, and skill-building.", listOf("waxing_crescent", "first_quarter"), emptyList()),
    LocalHabitCategoryData("creative", "Creative", "Create", "Art, ideas, and expressive work.", listOf("waxing_gibbous", "full_moon"), emptyList()),
    LocalHabitCategoryData("health", "Health", "Health", "Diet and self-care routines.", listOf("new_moon", "waxing_crescent"), emptyList()),
    LocalHabitCategoryData("spiritual", "Spiritual", "Spirit", "Ritual, prayer, and inner work.", listOf("new_moon", "full_moon"), emptyList()),
)

fun fallbackLunarGuidance(phase: String): LunarHabitGuidanceData = when (phase) {
    "new_moon" -> LunarHabitGuidanceData(
        phase = "new_moon",
        phaseName = "New Moon",
        emoji = "New",
        theme = "Set the tone",
        bestFor = listOf("Starting new habits", "Planning", "Gentle intention setting"),
        avoid = listOf("Overcommitting", "All-or-nothing goals"),
        energy = "Quiet and intentional",
        idealHabits = listOf("meditation", "health", "spiritual"),
        powerScoreModifier = 1.2,
    )
    "full_moon" -> LunarHabitGuidanceData(
        phase = "full_moon",
        phaseName = "Full Moon",
        emoji = "Full",
        theme = "Peak momentum",
        bestFor = listOf("Visible action", "Celebration", "Tracking wins"),
        avoid = listOf("Impulse", "Overextension"),
        energy = "High and expressive",
        idealHabits = listOf("exercise", "creative", "social", "spiritual"),
        powerScoreModifier = 1.15,
    )
    "waning_crescent" -> LunarHabitGuidanceData(
        phase = "waning_crescent",
        phaseName = "Waning Crescent",
        emoji = "Rest",
        theme = "Release and recover",
        bestFor = listOf("Rest", "Reflection", "Light review"),
        avoid = listOf("Starting intense routines", "Harsh self-judgment"),
        energy = "Low and restorative",
        idealHabits = listOf("meditation", "rest", "spiritual"),
        powerScoreModifier = 0.9,
    )
    else -> LunarHabitGuidanceData(
        phase = phase,
        phaseName = phase.replace('_', ' ').split(' ').joinToString(" ") { it.replaceFirstChar(Char::uppercase) },
        emoji = "Moon",
        theme = "Steady progress",
        bestFor = listOf("Consistency", "Small wins", "Showing up again"),
        avoid = listOf("Perfectionism"),
        energy = "Balanced and practical",
        idealHabits = listOf("learning", "health", "creative"),
        powerScoreModifier = 1.0,
    )
}

fun normalizeMoonPhaseKey(phase: String?): String =
    phase.orEmpty().trim().lowercase().replace(' ', '_').ifBlank { "waxing_crescent" }

private fun isTodayIsoDate(value: String): Boolean =
    runCatching {
        OffsetDateTime.parse(value).toLocalDate() == OffsetDateTime.now().toLocalDate()
    }.getOrDefault(false)