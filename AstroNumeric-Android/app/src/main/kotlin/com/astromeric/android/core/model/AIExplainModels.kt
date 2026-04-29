package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName

data class AIExplainSectionData(
    @SerializedName("title")
    val title: String? = null,
    @SerializedName("highlights")
    val highlights: List<String> = emptyList(),
)

data class AIExplainRequestData(
    @SerializedName("scope")
    val scope: String,
    @SerializedName("headline")
    val headline: String? = null,
    @SerializedName("theme")
    val theme: String? = null,
    @SerializedName("sections")
    val sections: List<AIExplainSectionData> = emptyList(),
    @SerializedName("numerology_summary")
    val numerologySummary: String? = null,
    @SerializedName("simple_language")
    val simpleLanguage: Boolean = true,
)

data class AIExplainResponseData(
    @SerializedName("summary")
    val summary: String,
    @SerializedName("provider")
    val provider: String,
)