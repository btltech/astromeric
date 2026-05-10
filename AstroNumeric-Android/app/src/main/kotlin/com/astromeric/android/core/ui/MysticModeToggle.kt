package com.astromeric.android.core.ui

import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// ---------------------------------------------------------------------------
// Cosmic palette constants (shared with CosmicBackgroundCanvas)
// ---------------------------------------------------------------------------

private val CosmicPurple = Color(0xFF8B5CF6)
private val CosmicPurpleLight = Color(0xFFB48EFF)
private val TextMuted = Color(0xFF8888AA)
private val BorderSubtle = Color(0x22FFFFFF)

// ---------------------------------------------------------------------------
// MysticModeToggle
//
// Android equivalent of iOS MysticModeToggle.swift:
//   • Two-option capsule control: MUNDANE (practical) / MYSTIC (mystical)
//   • Sliding purple gradient capsule behind the active option
//   • Monospace font with letter-spacing, bold when active
//   • Haptic snap on each selection change
//
// Usage:
//   MysticModeToggle(
//       isMystic = isMystic,
//       onToggle = { isMystic = it },
//   )
//
// Tone mapping → ForecastRequest:
//   isMystic = false → "balanced_practical"
//   isMystic = true  → "balanced_mystical"
// ---------------------------------------------------------------------------

val Boolean.forecastTone: String get() = if (this) "balanced_mystical" else "balanced_practical"

private val ActiveGradient = Brush.linearGradient(
    colors = listOf(
        CosmicPurple.copy(alpha = 0.85f),
        CosmicPurple.copy(alpha = 0.55f),
    ),
)

@Composable
fun MysticModeToggle(
    isMystic: Boolean,
    onToggle: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
) {
    val haptic = LocalHapticFeedback.current

    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(CircleShape)
            .background(Color.White.copy(alpha = 0.04f))
            .border(width = 1.dp, color = BorderSubtle, shape = CircleShape)
            .padding(4.dp)
            .semantics(mergeDescendants = true) {
                stateDescription = if (isMystic) "Mystic" else "Mundane"
            },
    ) {
        MysticModeOption(
            label = "MUNDANE",
            active = !isMystic,
            modifier = Modifier.weight(1f),
            onClick = {
                if (isMystic) {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onToggle(false)
                }
            },
        )
        MysticModeOption(
            label = "MYSTIC",
            active = isMystic,
            modifier = Modifier.weight(1f),
            onClick = {
                if (!isMystic) {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onToggle(true)
                }
            },
        )
    }
}

@Composable
private fun MysticModeOption(
    label: String,
    active: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val bgAlpha by animateFloatAsState(
        targetValue = if (active) 1f else 0f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium),
        label = "optionBgAlpha",
    )
    val textAlpha by animateFloatAsState(
        targetValue = if (active) 1f else 0.45f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioNoBouncy, stiffness = Spring.StiffnessMediumLow),
        label = "optionTextAlpha",
    )

    Box(
        modifier = modifier
            .clip(CircleShape)
            .clickable(onClick = onClick)
            .semantics {
                role = Role.RadioButton
                contentDescription = label.lowercase().replaceFirstChar { it.uppercase() }
            },
        contentAlignment = Alignment.Center,
    ) {
        // Active indicator — animate in/out
        if (bgAlpha > 0.01f) {
            Box(
                modifier = Modifier
                    .matchParentSize()
                    .alpha(bgAlpha)
                    .shadow(elevation = 6.dp, shape = CircleShape, clip = false)
                    .clip(CircleShape)
                    .background(brush = ActiveGradient, shape = CircleShape),
            )
        }

        Text(
            text = label,
            fontFamily = FontFamily.Monospace,
            fontWeight = if (active) FontWeight.Bold else FontWeight.Normal,
            fontSize = 11.sp,
            letterSpacing = if (active) 2.5.sp else 1.5.sp,
            color = if (active) Color.White else TextMuted,
            modifier = Modifier
                .padding(vertical = 10.dp, horizontal = 16.dp)
                .alpha(textAlpha),
        )
    }
}
