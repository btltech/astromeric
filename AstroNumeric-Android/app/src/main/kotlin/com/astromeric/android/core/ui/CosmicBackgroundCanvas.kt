package com.astromeric.android.core.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.withFrameNanos
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import kotlinx.coroutines.isActive
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.floor
import kotlin.math.sin
import kotlin.random.Random

// ---------------------------------------------------------------------------
// Star particle data — computed once and remembered
// ---------------------------------------------------------------------------

private data class Star(
    val x: Float,         // 0..1 normalized screen fraction
    val y: Float,
    val radius: Float,    // dp-ish canvas pixels
    val baseAlpha: Float,
    val twinklePhase: Float,  // initial sin phase offset (radians)
    val twinkleSpeed: Float,  // radians / second
)

private fun buildStars(count: Int, seed: Int): List<Star> {
    val rng = Random(seed)
    return List(count) {
        Star(
            x = rng.nextFloat(),
            y = rng.nextFloat(),
            radius = 0.5f + rng.nextFloat() * 1.5f,
            baseAlpha = 0.2f + rng.nextFloat() * 0.5f,
            twinklePhase = rng.nextFloat() * (2f * PI.toFloat()),
            twinkleSpeed = 0.5f + rng.nextFloat() * 1.5f,
        )
    }
}

// ---------------------------------------------------------------------------
// Element → nebula tint (matches iOS CosmicScene.updateForElement)
// ---------------------------------------------------------------------------

private fun nebulaColors(element: String?): Pair<Color, Color> = when (element) {
    "Fire"  -> Color(1f, 0.30f, 0.20f, 0.35f) to Color(1f, 0.60f, 0.00f, 0.25f)
    "Water" -> Color(0.20f, 0.40f, 1.00f, 0.35f) to Color(0.10f, 0.80f, 0.90f, 0.25f)
    "Air"   -> Color(0.50f, 0.80f, 1.00f, 0.35f) to Color(0.90f, 0.90f, 1.00f, 0.25f)
    "Earth" -> Color(0.30f, 0.70f, 0.30f, 0.35f) to Color(0.60f, 0.50f, 0.30f, 0.25f)
    else    -> Color(0.50f, 0.30f, 0.90f, 0.35f) to Color(0.80f, 0.40f, 0.70f, 0.25f) // signature purple
}

// ---------------------------------------------------------------------------
// CosmicBackgroundCanvas
// Matches iOS CosmicScene:
//   • 80 static background stars + 30 twinkling stars
//   • Two offset radial nebula gradients, element-tinted
//   • Shooting star every ~8 s, visible for 1.5 s with gradient tail
//   • Runs at vsync (capped by device; iOS runs at 30 fps)
// ---------------------------------------------------------------------------

@Composable
fun CosmicBackgroundCanvas(
    element: String? = null,
    modifier: Modifier = Modifier,
) {
    val backgroundStars = remember { buildStars(count = 80, seed = 42) }
    val twinklingStars  = remember { buildStars(count = 30, seed = 99) }
    val (nebula1, nebula2) = remember(element) { nebulaColors(element) }

    // Single float drives all animation — one state mutation per frame
    var time by remember { mutableFloatStateOf(0f) }

    LaunchedEffect(Unit) {
        var lastNanos = 0L
        while (isActive) {
            withFrameNanos { nanos ->
                if (lastNanos == 0L) lastNanos = nanos
                time += (nanos - lastNanos) / 1_000_000_000f
                lastNanos = nanos
            }
        }
    }

    Canvas(modifier = modifier.fillMaxSize()) {
        val w = size.width
        val h = size.height

        // 1. Deep space base (matches iOS backgroundColor = (0.02, 0.02, 0.06))
        drawRect(color = Color(0xFF05050F))

        // 2. Nebula gradient layer 1 — centred, large
        val r1 = maxOf(w, h) * 0.75f
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(nebula1, Color.Transparent),
                center = Offset(w * 0.5f, h * 0.5f),
                radius = r1,
            ),
            radius = r1,
            center = Offset(w * 0.5f, h * 0.5f),
        )

        // 3. Nebula gradient layer 2 — upper-right offset for depth (matches iOS gradientLayer2)
        val r2 = maxOf(w, h) * 0.55f
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(nebula2, Color.Transparent),
                center = Offset(w * 0.75f, h * 0.30f),
                radius = r2,
            ),
            radius = r2,
            center = Offset(w * 0.75f, h * 0.30f),
        )

        // 4. Static background star field
        for (star in backgroundStars) {
            drawCircle(
                color = Color.White.copy(alpha = star.baseAlpha),
                radius = star.radius,
                center = Offset(star.x * w, star.y * h),
            )
        }

        // 5. Twinkling stars — alpha modulated by sin(time * speed + phase)
        for (star in twinklingStars) {
            val alpha = star.baseAlpha * (0.5f + 0.5f * sin(time * star.twinkleSpeed + star.twinklePhase).toFloat())
            drawCircle(
                color = Color.White.copy(alpha = alpha.coerceIn(0f, 1f)),
                radius = star.radius + 0.5f,
                center = Offset(star.x * w, star.y * h),
            )
        }

        // 6. Shooting star — deterministic from time so no extra state is needed.
        //    Each 8-second cycle a new star spawns; it's visible for the first 1.5 s.
        val cycleTime = time % 8f
        if (cycleTime < 1.5f) {
            val cycleSeed = floor(time / 8f).toLong()
            val rng = Random(cycleSeed)
            val ssX0    = rng.nextFloat()
            val ssY0    = rng.nextFloat() * 0.40f
            val ssAngle = PI.toFloat() / 4f + (rng.nextFloat() - 0.5f) * 0.40f
            val ssLen   = 0.12f + rng.nextFloat() * 0.08f

            val p        = cycleTime / 1.5f                          // 0→1 across visible window
            val headX    = (ssX0 + cos(ssAngle) * 0.25f * p) * w
            val headY    = (ssY0 + sin(ssAngle) * 0.25f * p) * h
            val tailFrac = minOf(p, 0.6f) / 0.6f
            val tailX    = headX - cos(ssAngle) * ssLen * w * tailFrac
            val tailY    = headY - sin(ssAngle) * ssLen * h * tailFrac
            val alpha    = (1f - p) * 0.85f

            drawLine(
                brush = Brush.linearGradient(
                    colors = listOf(Color.Transparent, Color.White.copy(alpha = alpha)),
                    start = Offset(tailX, tailY),
                    end = Offset(headX, headY),
                ),
                start = Offset(tailX, tailY),
                end = Offset(headX, headY),
                strokeWidth = 1.8f,
            )
        }
    }
}

// ---------------------------------------------------------------------------
// CosmicSurface — drop-in wrapper matching iOS ZStack + CosmicBackgroundView
// Usage:
//   CosmicSurface(element = profile?.element) {
//       // screen content here
//   }
// ---------------------------------------------------------------------------

@Composable
fun CosmicSurface(
    element: String? = null,
    modifier: Modifier = Modifier,
    content: @Composable BoxScope.() -> Unit,
) {
    Box(modifier = modifier.fillMaxSize()) {
        CosmicBackgroundCanvas(
            element = element,
            modifier = Modifier.matchParentSize(),
        )
        content()
    }
}
