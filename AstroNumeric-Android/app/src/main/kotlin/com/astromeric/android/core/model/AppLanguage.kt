package com.astromeric.android.core.model

import java.util.Locale

enum class AppLanguage(
    val tag: String,
    val nativeLabel: String,
    val flag: String,
) {
    ENGLISH("en", "English", "🇺🇸"),
    SPANISH("es", "Español", "🇪🇸"),
    FRENCH("fr", "Français", "🇫🇷"),
    ROMANIAN("ro", "Română", "🇷🇴"),
    NEPALI("ne", "नेपाली", "🇳🇵");

    val chipLabel: String
        get() = "$flag $nativeLabel"

    companion object {
        fun fromTag(tag: String?): AppLanguage? {
            if (tag.isNullOrBlank()) {
                return null
            }
            val normalizedTag = Locale.forLanguageTag(tag).language.ifBlank { tag }
            return entries.firstOrNull { language ->
                language.tag.equals(tag, ignoreCase = true) ||
                    language.tag.equals(normalizedTag, ignoreCase = true)
            }
        }

        fun defaultFromSystem(): AppLanguage =
            fromTag(Locale.getDefault().toLanguageTag()) ?: ENGLISH
    }
}