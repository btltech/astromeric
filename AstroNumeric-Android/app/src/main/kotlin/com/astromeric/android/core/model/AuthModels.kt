package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName

data class AuthRequestData(
    @SerializedName("email")
    val email: String,
    @SerializedName("password")
    val password: String,
)

data class AuthUserData(
    @SerializedName("id")
    val id: String,
    @SerializedName("email")
    val email: String,
    @SerializedName("is_paid")
    val isPaid: Boolean,
)

data class AuthSessionData(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("token_type")
    val tokenType: String,
    @SerializedName("user")
    val user: AuthUserData,
)