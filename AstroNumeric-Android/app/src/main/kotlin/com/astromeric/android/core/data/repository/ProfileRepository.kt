package com.astromeric.android.core.data.repository

import com.astromeric.android.core.data.local.ProfileDao
import com.astromeric.android.core.data.local.toDomain
import com.astromeric.android.core.data.local.toEntity
import com.astromeric.android.core.data.preferences.AppPreferencesStore
import com.astromeric.android.core.data.remote.AstroRemoteDataSource
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.ProfileDraft
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlin.math.min

class ProfileRepository(
    private val profileDao: ProfileDao,
    private val preferencesStore: AppPreferencesStore,
    private val remoteDataSource: AstroRemoteDataSource,
) {
    val profiles: Flow<List<AppProfile>> = profileDao.observeAll().map { entities ->
        entities.map { it.toDomain() }
    }

    val selectedProfileId: Flow<Int?> = preferencesStore.selectedProfileId

    val selectedProfile: Flow<AppProfile?> = combine(profiles, selectedProfileId) { profiles, selectedId ->
        when {
            profiles.isEmpty() -> null
            selectedId == null -> profiles.firstOrNull()
            else -> profiles.firstOrNull { it.id == selectedId } ?: profiles.firstOrNull()
        }
    }

    suspend fun getProfile(id: Int): AppProfile? = profileDao.getById(id)?.toDomain()

    suspend fun saveProfile(
        draft: ProfileDraft,
        select: Boolean = true,
    ): AppProfile {
        val localProfile = draft.toLocalProfile()

        val profile = syncProfileIfAuthenticated(localProfile).getOrElse {
            profileDao.upsert(localProfile.toEntity())
            localProfile
        }

        profileDao.upsert(profile.toEntity())

        if (select) {
            preferencesStore.setSelectedProfileId(profile.id)
        }
        return profile
    }

    suspend fun saveLocalProfile(
        draft: ProfileDraft,
        select: Boolean = true,
    ): AppProfile {
        val localProfile = draft.toLocalProfile()
        profileDao.upsert(localProfile.toEntity())
        if (select) {
            preferencesStore.setSelectedProfileId(localProfile.id)
        }
        return localProfile
    }

    suspend fun selectProfile(id: Int) {
        preferencesStore.setSelectedProfileId(id)
    }

    suspend fun deleteProfile(id: Int) {
        val authToken = preferencesStore.activeAuthAccessToken()
        if (authToken != null && id > 0) {
            remoteDataSource.deleteRemoteProfile(authToken, id)
        }
        profileDao.deleteById(id)
        val currentSelectedId = preferencesStore.selectedProfileId.first()
        if (currentSelectedId == id) {
            val fallbackId = profileDao.listOnce()
                .map { it.toDomain() }
                .firstOrNull { it.id != id }
                ?.id
            preferencesStore.setSelectedProfileId(fallbackId)
        }
    }

    private suspend fun nextLocalProfileId(): Int {
        val minId = profileDao.minId() ?: 0
        return min(minId - 1, -1)
    }

    private suspend fun ProfileDraft.toLocalProfile(): AppProfile = AppProfile(
        id = id ?: nextLocalProfileId(),
        name = name.trim(),
        dateOfBirth = dateOfBirth,
        timeOfBirth = timeOfBirth,
        timeConfidence = timeConfidence,
        placeOfBirth = placeOfBirth.trim(),
        latitude = latitude,
        longitude = longitude,
        timezone = timezone.trim(),
        houseSystem = houseSystem,
    )

    suspend fun syncProfilesToAccount(): Result<List<AppProfile>> = runCatching {
        val authToken = preferencesStore.activeAuthAccessToken()
            ?: error(
                if (preferencesStore.personalModeEnabled.first()) {
                    "Personal mode is enabled for this build. Account profile sync is dormant."
                } else {
                    "Sign in first to sync profiles."
                },
            )

        val localProfiles = profileDao.listOnce().map { it.toDomain() }
        val promotedProfiles = mutableMapOf<Int, Int>()

        localProfiles.filter { it.id <= 0 }.forEach { localProfile ->
            val remoteProfile = remoteDataSource.createRemoteProfile(authToken, localProfile).getOrThrow()
            profileDao.upsert(remoteProfile.toEntity())
            profileDao.deleteById(localProfile.id)
            promotedProfiles[localProfile.id] = remoteProfile.id
        }

        localProfiles.filter { it.id > 0 }.forEach { existingRemote ->
            remoteDataSource.updateRemoteProfile(authToken, existingRemote)
                .onSuccess { updated -> profileDao.upsert(updated.toEntity()) }
        }

        remoteDataSource.listRemoteProfiles(authToken)
            .onSuccess { remoteProfiles ->
                remoteProfiles.forEach { profileDao.upsert(it.toEntity()) }
            }
            .getOrThrow()

        promotedProfiles[preferencesStore.selectedProfileId.first()]?.let { newSelectedId ->
            preferencesStore.setSelectedProfileId(newSelectedId)
        }

        profileDao.listOnce().map { it.toDomain() }
    }

    private suspend fun syncProfileIfAuthenticated(profile: AppProfile): Result<AppProfile> {
        val authToken = preferencesStore.activeAuthAccessToken()
            ?: return Result.success(profile)

        return if (profile.id > 0) {
            remoteDataSource.updateRemoteProfile(authToken, profile).onSuccess { updated ->
                profileDao.upsert(updated.toEntity())
            }
        } else {
            remoteDataSource.createRemoteProfile(authToken, profile).onSuccess { created ->
                profileDao.upsert(created.toEntity())
                profileDao.deleteById(profile.id)
            }
        }
    }
}
