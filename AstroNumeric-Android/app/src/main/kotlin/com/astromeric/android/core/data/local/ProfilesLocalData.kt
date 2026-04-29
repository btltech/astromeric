package com.astromeric.android.core.data.local

import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.RoomDatabase
import androidx.room.Upsert
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DefaultHouseSystem
import com.astromeric.android.core.model.TimeConfidence
import kotlinx.coroutines.flow.Flow

@Entity(tableName = "profiles")
data class ProfileEntity(
    @PrimaryKey
    val id: Int,
    val name: String,
    val dateOfBirth: String,
    val timeOfBirth: String?,
    val timeConfidence: String,
    val placeOfBirth: String?,
    val latitude: Double?,
    val longitude: Double?,
    val timezone: String?,
    val houseSystem: String,
)

@Dao
interface ProfileDao {
    @Query("SELECT * FROM profiles ORDER BY id DESC")
    fun observeAll(): Flow<List<ProfileEntity>>

    @Query("SELECT * FROM profiles ORDER BY id DESC")
    suspend fun listOnce(): List<ProfileEntity>

    @Query("SELECT * FROM profiles WHERE id = :id LIMIT 1")
    suspend fun getById(id: Int): ProfileEntity?

    @Query("SELECT MIN(id) FROM profiles")
    suspend fun minId(): Int?

    @Upsert
    suspend fun upsert(profile: ProfileEntity)

    @Query("DELETE FROM profiles WHERE id = :id")
    suspend fun deleteById(id: Int)
}

@Database(
    entities = [ProfileEntity::class],
    version = 1,
    exportSchema = false,
)
abstract class AstroDatabase : RoomDatabase() {
    abstract fun profileDao(): ProfileDao
}

fun ProfileEntity.toDomain(): AppProfile =
    AppProfile(
        id = id,
        name = name,
        dateOfBirth = dateOfBirth,
        timeOfBirth = timeOfBirth,
        timeConfidence = TimeConfidence.fromWireValue(timeConfidence),
        placeOfBirth = placeOfBirth,
        latitude = latitude,
        longitude = longitude,
        timezone = timezone,
        houseSystem = houseSystem.ifBlank { DefaultHouseSystem },
    )

fun AppProfile.toEntity(): ProfileEntity =
    ProfileEntity(
        id = id,
        name = name,
        dateOfBirth = dateOfBirth,
        timeOfBirth = timeOfBirth,
        timeConfidence = timeConfidence.wireValue,
        placeOfBirth = placeOfBirth,
        latitude = latitude,
        longitude = longitude,
        timezone = timezone,
        houseSystem = houseSystem,
    )
