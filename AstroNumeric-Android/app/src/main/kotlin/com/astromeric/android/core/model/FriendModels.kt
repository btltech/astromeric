package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName
import java.util.UUID

data class FriendProfileData(
    @SerializedName("id")
    val id: String = UUID.randomUUID().toString(),
    @SerializedName("name")
    val name: String,
    @SerializedName("date_of_birth")
    val dateOfBirth: String,
    @SerializedName("time_of_birth")
    val timeOfBirth: String? = "12:00",
    @SerializedName("latitude")
    val latitude: Double? = null,
    @SerializedName("longitude")
    val longitude: Double? = null,
    @SerializedName("timezone")
    val timezone: String? = "UTC",
    @SerializedName("avatar_emoji")
    val avatarEmoji: String = "👤",
    @SerializedName("relationship_type")
    val relationshipType: String = "friendship",
    @SerializedName("notes")
    val notes: String? = null,
    @SerializedName("added_at")
    val addedAt: String? = null,
)

data class AddFriendRequestData(
    @SerializedName("owner_id")
    val ownerId: String,
    @SerializedName("friend")
    val friend: FriendProfileData,
)

data class CompareAllFriendsRequestData(
    @SerializedName("owner_id")
    val ownerId: String,
    @SerializedName("owner_profile")
    val ownerProfile: ProfilePayload,
)

data class FriendCompatibilityData(
    @SerializedName("friend_id")
    val friendId: String,
    @SerializedName("friend_name")
    val friendName: String,
    @SerializedName("overall_score")
    val overallScore: Float,
    @SerializedName("headline")
    val headline: String,
    @SerializedName("emoji")
    val emoji: String,
    @SerializedName("relationship_type")
    val relationshipType: String,
    @SerializedName("dimensions")
    val dimensions: List<Map<String, Any>> = emptyList(),
    @SerializedName("strengths")
    val strengths: List<String> = emptyList(),
    @SerializedName("recommendations")
    val recommendations: List<String> = emptyList(),
)

fun friendRelationshipLabel(type: String): String = when (type) {
    "romantic" -> "Romantic"
    "professional" -> "Professional"
    else -> "Friendship"
}