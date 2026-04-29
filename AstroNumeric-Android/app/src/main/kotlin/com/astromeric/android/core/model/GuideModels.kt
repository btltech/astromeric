package com.astromeric.android.core.model

import com.google.gson.annotations.SerializedName
import java.util.UUID

enum class GuideTone(
    val wireValue: String,
    val label: String,
    val emoji: String,
    val prompt: String,
) {
    GENTLE(
        wireValue = "gentle",
        label = "Gentle",
        emoji = "🌸",
        prompt = "Speak with warmth and compassion. Be encouraging and supportive without becoming vague. Soften harsh aspects while keeping the guidance useful.",
    ),
    BALANCED(
        wireValue = "balanced",
        label = "Balanced",
        emoji = "⚖️",
        prompt = "Be informative and balanced. Mix encouragement with honest observations and concrete next steps.",
    ),
    DIRECT(
        wireValue = "direct",
        label = "Direct",
        emoji = "🎯",
        prompt = "Be blunt and straightforward. Avoid sugar-coating, but stay respectful and practical.",
    ),
    ROAST(
        wireValue = "roast",
        label = "Roast",
        emoji = "🔥",
        prompt = "Use playful chart-based teasing without cruelty. Keep it astrologically accurate, funny, and still useful.",
    );

    companion object {
        fun fromWireValue(value: String?): GuideTone =
            entries.firstOrNull { it.wireValue == value } ?: BALANCED
    }
}

enum class GuideMessageRole(
    val wireValue: String,
) {
    USER("user"),
    ASSISTANT("assistant");
}

data class GuideChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val role: GuideMessageRole,
    val content: String,
)

data class GuideChatHistoryItem(
    @SerializedName("role")
    val role: String,
    @SerializedName("content")
    val content: String,
)

data class CosmicGuideChatRequestData(
    @SerializedName("message")
    val message: String,
    @SerializedName("sun_sign")
    val sunSign: String? = null,
    @SerializedName("moon_sign")
    val moonSign: String? = null,
    @SerializedName("rising_sign")
    val risingSign: String? = null,
    @SerializedName("birth_time_assumed")
    val birthTimeAssumed: Boolean = false,
    @SerializedName("time_confidence")
    val timeConfidence: String? = null,
    @SerializedName("history")
    val history: List<GuideChatHistoryItem> = emptyList(),
    @SerializedName("system_prompt")
    val systemPrompt: String? = null,
    @SerializedName("tone")
    val tone: String? = null,
)

data class CosmicGuideChatData(
    @SerializedName("response")
    val response: String,
    @SerializedName("provider")
    val provider: String,
    @SerializedName("model")
    val model: String? = null,
)

fun List<GuideChatMessage>.toGuideHistory(limit: Int = 10): List<GuideChatHistoryItem> =
    takeLast(limit).map { message ->
        GuideChatHistoryItem(
            role = message.role.wireValue,
            content = message.content,
        )
    }