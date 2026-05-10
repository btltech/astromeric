package com.astromeric.android.core.ui

import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.graphicsLayer

// ---------------------------------------------------------------------------
// RevealAnimations
// Android equivalents of iOS RevealAnimations.swift modifiers.
//
// Usage (matches iOS .scaleReveal(isRevealing:, fromScale:)):
//   var revealed by remember { mutableStateOf(false) }
//   LaunchedEffect(data) { if (data != null) revealed = true }
//   ContentComposable(
//       modifier = Modifier.scaleReveal(visible = revealed)
//   )
// ---------------------------------------------------------------------------

/**
 * Fades + scales content in from [fromScale] when [visible] becomes true.
 * Matches iOS ScaleRevealModifier (spring response 0.5, dampingFraction 0.7).
 */
@Composable
fun Modifier.scaleReveal(
    visible: Boolean,
    fromScale: Float = 0.90f,
    delayMillis: Int = 0,
): Modifier {
    val scale by animateFloatAsState(
        targetValue = if (visible) 1f else fromScale,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessMedium,
        ),
        label = "scaleReveal",
    )
    val alpha by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = tween(durationMillis = 300, delayMillis = delayMillis),
        label = "scaleRevealAlpha",
    )
    return this
        .graphicsLayer { scaleX = scale; scaleY = scale }
        .alpha(alpha)
}

/**
 * Slides content up from [offsetPx] and fades in when [visible] becomes true.
 * Matches iOS SlideUpRevealModifier (spring response 0.5, dampingFraction 0.8).
 */
@Composable
fun Modifier.slideUpReveal(
    visible: Boolean,
    offsetPx: Float = 48f,
    delayMillis: Int = 0,
): Modifier {
    val offset by animateFloatAsState(
        targetValue = if (visible) 0f else offsetPx,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessMediumLow,
        ),
        label = "slideUpReveal",
    )
    val alpha by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = tween(durationMillis = 300, delayMillis = delayMillis),
        label = "slideUpRevealAlpha",
    )
    return this
        .graphicsLayer { translationY = offset }
        .alpha(alpha)
}

/**
 * Shimmer-and-fade reveal for hero content.
 * Matches iOS ShimmerRevealModifier (spring response 0.6, dampingFraction 0.8).
 */
@Composable
fun Modifier.shimmerReveal(
    visible: Boolean,
    delayMillis: Int = 0,
): Modifier {
    val scale by animateFloatAsState(
        targetValue = if (visible) 1f else 0.96f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioLowBouncy,
            stiffness = Spring.StiffnessLow,
        ),
        label = "shimmerReveal",
    )
    val alpha by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = tween(durationMillis = 400, delayMillis = delayMillis),
        label = "shimmerRevealAlpha",
    )
    return this
        .graphicsLayer { scaleX = scale; scaleY = scale }
        .alpha(alpha)
}
