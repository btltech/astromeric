package com.astromeric.android.core.localization

import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.model.AppLanguage
import kotlinx.coroutines.runBlocking

object AppLanguageManager {
    fun applyLanguage(language: AppLanguage) {
        AppCompatDelegate.setApplicationLocales(
            LocaleListCompat.forLanguageTags(language.tag),
        )
    }

    fun applySavedLanguage(preferencesStore: AppPreferencesStore) {
        runBlocking {
            applyLanguage(preferencesStore.appLanguageValue())
        }
    }
}