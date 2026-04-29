package com.astromeric.android.app

import android.app.Application
import androidx.room.Room
import com.astromeric.android.core.localization.AppLanguageManager
import com.astromeric.android.core.data.local.AstroDatabase
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.data.repository.HabitRepository
import com.astromeric.android.core.data.repository.JournalRepository
import com.astromeric.android.core.data.repository.ProfileRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

class AstroNumericApplication : Application() {
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()
        AppLanguageManager.applySavedLanguage(appContainer.preferencesStore)
        AstroNotificationService(this).createNotificationChannels()
        AstroBackgroundScheduler.schedulePeriodicRefresh(this)
        AstroBackgroundScheduler.scheduleImmediateRefresh(this)
        applicationScope.launch {
            appContainer.pushRegistrationManager.syncCurrentToken()
        }
    }

    val appContainer: AppContainer by lazy {
        AppContainer(this)
    }
}

class AppContainer(application: Application) {
    private val database = Room.databaseBuilder(
        application,
        AstroDatabase::class.java,
        "astronumeric_android.db",
    ).build()

    val preferencesStore = AppPreferencesStore(application)

    val remoteDataSource: AstroRemoteDataSource = AstroRemoteDataSource.create()

    val pushRegistrationManager = PushRegistrationManager(
        context = application,
        preferencesStore = preferencesStore,
        remoteDataSource = remoteDataSource,
    )

    val profileRepository = ProfileRepository(
        profileDao = database.profileDao(),
        preferencesStore = preferencesStore,
        remoteDataSource = remoteDataSource,
    )

    val habitRepository = HabitRepository(
        preferencesStore = preferencesStore,
        remoteDataSource = remoteDataSource,
    )

    val journalRepository = JournalRepository(
        preferencesStore = preferencesStore,
        remoteDataSource = remoteDataSource,
    )
}
