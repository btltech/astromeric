package com.astromeric.android.feature.tools

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.PrivacyDisplayRole
import com.astromeric.android.core.model.displayName
import com.astromeric.android.core.model.zodiacSignName
import com.astromeric.android.core.ui.PremiumContentCard

@Composable
fun BirthstonesScreen(
    selectedProfile: AppProfile?,
    hideSensitiveDetailsEnabled: Boolean,
    onOpenProfile: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val activeSign = selectedProfile
        ?.zodiacSignName()
        ?.let(BirthstoneSign::fromWireValue)

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        if (activeSign == null) {
            PremiumContentCard(
                title = "Birthstones",
                body = "Your profile unlocks the symbolic layer. Create a profile to match your sign with stones, meanings, and practical ways to use them.",
            ) {
                    Button(onClick = onOpenProfile) {
                        Text("Open Profile")
                    }
            }
            return@Column
        }

        PremiumContentCard(
            title = "Birthstones",
            body = "Use symbolic materials as a personal ritual language. This turns birthstones from trivia into something intentional: what they mean, how they resonate with your sign, and how to work with them.",
        ) {
                selectedProfile?.let { profile ->
                    AssistChip(
                        onClick = {},
                        label = {
                            Text(
                                "Active profile: ${profile.displayName(hideSensitiveDetailsEnabled, PrivacyDisplayRole.ACTIVE_USER)} · ${activeSign.displayName}",
                            )
                        },
                    )
                }
        }

        PremiumContentCard(
            title = "${activeSign.displayName} Birthstones",
            body = "Your birthstones carry energies that resonate with your sign. Use them for intention, protection, and amplifying your natural gifts.",
        ) {
                Text(
                    text = activeSign.emoji,
                    style = MaterialTheme.typography.displayMedium,
                )
                Text(
                    text = "${activeSign.element} · ${activeSign.modality}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
        }

        activeSign.birthstones.forEachIndexed { index, stone ->
            BirthstoneCard(
                stone = stone,
                index = index,
            )
        }

        PremiumContentCard(
            title = "Working with Birthstones",
            body = "You do not need to buy gemstones. Visualizing their colors during meditation can still activate the symbolic layer you want to work with.",
        )
    }
}

@Composable
private fun BirthstoneCard(
    stone: BirthstoneInfo,
    index: Int,
) {
    PremiumContentCard(
        title = "${stone.emoji} ${stone.name}",
        body = "Stone ${index + 1} of 3",
    ) {
            Text(
                text = "Meaning",
                style = MaterialTheme.typography.titleSmall,
            )
            Text(
                text = stone.meaning,
                style = MaterialTheme.typography.bodyMedium,
            )
            Text(
                text = "How to Use",
                style = MaterialTheme.typography.titleSmall,
            )
            Text(
                text = stone.howToUse,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
    }
}

private data class BirthstoneInfo(
    val name: String,
    val emoji: String,
    val meaning: String,
    val howToUse: String,
)

private enum class BirthstoneSign(
    val wireValue: String,
    val displayName: String,
    val emoji: String,
    val element: String,
    val modality: String,
    val birthstones: List<BirthstoneInfo>,
) {
    ARIES(
        wireValue = "aries",
        displayName = "Aries",
        emoji = "♈️",
        element = "Fire",
        modality = "Cardinal",
        birthstones = listOf(
            BirthstoneInfo("Diamond", "💎", "Clarity and invincibility — amplifies Aries courage and willpower.", "Wear or carry diamond when taking bold action or starting something new."),
            BirthstoneInfo("Bloodstone", "🟢", "Grounds fiery Aries energy and promotes courage without recklessness.", "Hold bloodstone during stressful moments to stay grounded and decisive."),
            BirthstoneInfo("Jasper", "🔴", "A nurturing stone that promotes patience and stamina — balancing Aries impulsivity.", "Keep jasper nearby during long projects to sustain motivation."),
        ),
    ),
    TAURUS(
        wireValue = "taurus",
        displayName = "Taurus",
        emoji = "♉️",
        element = "Earth",
        modality = "Fixed",
        birthstones = listOf(
            BirthstoneInfo("Emerald", "💚", "Stone of prosperity and loyalty — resonates deeply with Taurus' love of abundance.", "Wear emerald to attract stability and strengthen bonds in relationships."),
            BirthstoneInfo("Rose Quartz", "🌸", "Opens the heart to self-love and harmony — softens Taurus stubbornness with compassion.", "Place rose quartz in your bedroom or carry it to invite warmth into relationships."),
            BirthstoneInfo("Malachite", "🌿", "Transformation stone that helps Taurus release what no longer serves them.", "Meditate with malachite when you're resisting necessary change."),
        ),
    ),
    GEMINI(
        wireValue = "gemini",
        displayName = "Gemini",
        emoji = "♊️",
        element = "Air",
        modality = "Mutable",
        birthstones = listOf(
            BirthstoneInfo("Agate", "🔵", "Brings mental clarity and helps Gemini articulate thoughts with precision.", "Hold agate before important conversations or presentations."),
            BirthstoneInfo("Citrine", "🌟", "Sunny and uplifting — enhances Gemini's natural wit and optimism.", "Keep citrine on your desk to spark creativity and clear mental fog."),
            BirthstoneInfo("Tiger's Eye", "🐯", "Grounds scattered Gemini energy into focused, practical action.", "Carry tiger's eye when you need to follow through on ideas."),
        ),
    ),
    CANCER(
        wireValue = "cancer",
        displayName = "Cancer",
        emoji = "♋️",
        element = "Water",
        modality = "Cardinal",
        birthstones = listOf(
            BirthstoneInfo("Ruby", "🔴", "A stone of passion and confidence. Helps Cancer step forward boldly and say what they truly feel.", "Wear or visualize ruby when trying new things or having courageous conversations."),
            BirthstoneInfo("Moonstone", "🌙", "Enhances intuition and emotional balance — Cancer's natural domain. Supports deep reflection.", "Carry moonstone when feelings deepen or when navigating emotional complexity."),
            BirthstoneInfo("Pearl", "🤍", "A calming gemstone that soothes stress and promotes inner harmony and emotional resilience.", "Wear pearl jewelry or place a pearl under your pillow to calm emotional turbulence."),
        ),
    ),
    LEO(
        wireValue = "leo",
        displayName = "Leo",
        emoji = "♌️",
        element = "Fire",
        modality = "Fixed",
        birthstones = listOf(
            BirthstoneInfo("Peridot", "💛", "Awakens Leo's warmth and generosity, while dispelling jealousy and resentment.", "Wear peridot to radiate positive energy and attract loyal people."),
            BirthstoneInfo("Carnelian", "🟠", "Fuels Leo's creative fire and boldness — a stone of action and self-expression.", "Hold carnelian before performing, presenting, or creating anything artistic."),
            BirthstoneInfo("Amber", "🟡", "Warm and sunny like Leo — promotes vitality, self-confidence, and joy.", "Keep amber nearby to maintain high energy and enthusiasm throughout the day."),
        ),
    ),
    VIRGO(
        wireValue = "virgo",
        displayName = "Virgo",
        emoji = "♍️",
        element = "Earth",
        modality = "Mutable",
        birthstones = listOf(
            BirthstoneInfo("Sapphire", "💙", "Stone of wisdom and clarity — sharpens Virgo's analytical mind.", "Wear sapphire when tackling complex problems or making important decisions."),
            BirthstoneInfo("Amazonite", "🩵", "Soothes Virgo's tendency toward worry and self-criticism with calm clarity.", "Hold amazonite when overthinking, or keep it on your desk as a reminder to be kind to yourself."),
            BirthstoneInfo("Moss Agate", "🍃", "Connects Virgo to nature's rhythms and promotes stability and healing.", "Keep moss agate near plants or in your workspace to foster calm productivity."),
        ),
    ),
    LIBRA(
        wireValue = "libra",
        displayName = "Libra",
        emoji = "♎️",
        element = "Air",
        modality = "Cardinal",
        birthstones = listOf(
            BirthstoneInfo("Opal", "🌈", "Stone of inspiration and creativity — magnifies Libra's love of beauty and harmony.", "Wear opal when seeking creative inspiration or artistic breakthroughs."),
            BirthstoneInfo("Lapis Lazuli", "🔵", "Promotes honest communication and inner truth — helps Libra speak up decisively.", "Hold lapis lazuli when you need to voice your opinion or make a difficult decision."),
            BirthstoneInfo("Rose Quartz", "🌸", "Enhances Libra's deep need for connection and harmonious relationships.", "Place rose quartz in shared spaces to nurture loving, balanced energy."),
        ),
    ),
    SCORPIO(
        wireValue = "scorpio",
        displayName = "Scorpio",
        emoji = "♏️",
        element = "Water",
        modality = "Fixed",
        birthstones = listOf(
            BirthstoneInfo("Topaz", "🟤", "Amplifies Scorpio's intensity and psychic perception — a stone of manifestation.", "Meditate with topaz when setting intentions or working through transformation."),
            BirthstoneInfo("Obsidian", "⚫️", "Powerful protective stone — shields Scorpio from psychic drain and negative energy.", "Keep obsidian near your entryway or carry it as a shield in draining environments."),
            BirthstoneInfo("Malachite", "🌿", "Accelerates Scorpio's natural transformation and releases deep emotional patterns.", "Use malachite in journaling or shadow work practices."),
        ),
    ),
    SAGITTARIUS(
        wireValue = "sagittarius",
        displayName = "Sagittarius",
        emoji = "♐️",
        element = "Fire",
        modality = "Mutable",
        birthstones = listOf(
            BirthstoneInfo("Turquoise", "🩵", "Stone of travel and wisdom — perfectly aligned with Sagittarius' adventurous spirit.", "Wear turquoise when traveling or seeking new wisdom and experiences."),
            BirthstoneInfo("Tanzanite", "💜", "Deepens Sagittarius' spiritual awareness and visionary thinking.", "Meditate with tanzanite to connect to higher purpose and spiritual insight."),
            BirthstoneInfo("Citrine", "🌟", "Amplifies optimism and attracts abundance — Sagittarius at their best.", "Keep citrine in your wallet or space to attract luck and opportunities."),
        ),
    ),
    CAPRICORN(
        wireValue = "capricorn",
        displayName = "Capricorn",
        emoji = "♑️",
        element = "Earth",
        modality = "Cardinal",
        birthstones = listOf(
            BirthstoneInfo("Garnet", "❤️", "Stone of commitment and perseverance — fuels Capricorn's drive toward long-term goals.", "Wear garnet when starting an ambitious project or needing sustained motivation."),
            BirthstoneInfo("Onyx", "⚫️", "Strengthens Capricorn's discipline and resilience, especially during hardship.", "Carry onyx during stressful periods to maintain strength and focus."),
            BirthstoneInfo("Smoky Quartz", "🤎", "Grounds ambition into practical steps — prevents Capricorn from burning out.", "Keep smoky quartz in your workspace to stay grounded and realistic."),
        ),
    ),
    AQUARIUS(
        wireValue = "aquarius",
        displayName = "Aquarius",
        emoji = "♒️",
        element = "Air",
        modality = "Fixed",
        birthstones = listOf(
            BirthstoneInfo("Amethyst", "💜", "Heightens Aquarius' intuition and visionary thinking — a stone of spiritual insight.", "Meditate with amethyst when working on innovative ideas or future planning."),
            BirthstoneInfo("Aquamarine", "🩵", "Aligns with Aquarius' humanitarian spirit — promotes clear, compassionate communication.", "Wear aquamarine when speaking for a cause or facilitating group conversations."),
            BirthstoneInfo("Labradorite", "🔮", "Stone of magic and transformation — awakens Aquarius' genius and originality.", "Keep labradorite nearby during creative or inventive work."),
        ),
    ),
    PISCES(
        wireValue = "pisces",
        displayName = "Pisces",
        emoji = "♓️",
        element = "Water",
        modality = "Mutable",
        birthstones = listOf(
            BirthstoneInfo("Aquamarine", "🩵", "Supports Pisces' empathic nature and emotional clarity — like the ocean depths.", "Wear aquamarine to stay emotionally clear and avoid absorbing others' energies."),
            BirthstoneInfo("Amethyst", "💜", "Amplifies Pisces' spiritual intuition and protects against psychic overwhelm.", "Place amethyst near your bed to enhance intuitive dreams and restful sleep."),
            BirthstoneInfo("Fluorite", "💚", "Brings mental clarity and focus to dreamy Pisces — organizes creative visions.", "Keep fluorite on your desk when you need to translate inspiration into action."),
        ),
    );

    companion object {
        fun fromWireValue(value: String): BirthstoneSign? =
            entries.firstOrNull { it.wireValue.equals(value, ignoreCase = true) }
    }
}