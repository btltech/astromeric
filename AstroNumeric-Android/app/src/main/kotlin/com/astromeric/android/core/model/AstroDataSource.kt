package com.astromeric.android.core.model

enum class AstroDataSource(
    val label: String,
) {
    BACKEND("Backend"),
    LOCAL_SWISS("On-device Swiss"),
    LOCAL_ESTIMATE("Local estimate");

    companion object {
        fun fromStorage(value: String?): AstroDataSource =
            entries.firstOrNull { it.name == value } ?: BACKEND
    }
}