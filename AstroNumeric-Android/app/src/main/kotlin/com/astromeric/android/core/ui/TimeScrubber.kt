package com.astromeric.android.core.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.abs
import kotlin.math.roundToInt

// ---------------------------------------------------------------------------
// TimeScrubber
//
// Android equivalent of iOS TimeScrubber.swift:
//   • Horizontal drag track spanning -range..+range days (default ±7)
//   • Tick marks at each step, today's dot glows purple
//   • Knob snaps to integer offsets, haptic on each step + on return-to-zero
//   • Label row: "−7D" ··· "TODAY / +ND · FUTURE / −ND · PAST" ··· "+7D"
//   • Accessibility: adjustable action
//
// Usage:
//   TimeScrubber(
//       offset = dayOffset,
//       onOffsetChange = { dayOffset = it },
//   )
// ---------------------------------------------------------------------------

private val CosmicPurple = Color(0xFF8B5CF6)
private val TrackColor   = Color(0x10FFFFFF)
private val TickColor    = Color(0x40FFFFFF)
private val TextMuted    = Color(0xFF8888AA)

@Composable
fun TimeScrubber(
    offset: Int,
    onOffsetChange: (Int) -> Unit,
    range: Int = 7,
    modifier: Modifier = Modifier,
) {
    val haptic = LocalHapticFeedback.current
    var trackWidthPx by remember { mutableFloatStateOf(0f) }
    // Drag accumulator — let us snap without losing sub-step drag progress
    var dragAccumPx by remember { mutableFloatStateOf(0f) }
    var lastSnap by remember { mutableIntStateOf(offset) }

    val tickCount = range * 2 + 1  // e.g. 15 ticks for ±7
    val label = when {
        offset == 0 -> "TODAY"
        offset > 0  -> "+${offset}D · FUTURE"
        else        -> "${offset}D · PAST"
    }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .semantics {
                contentDescription = "Time travel scrubber, $label"
            },
    ) {
        // Track + knob
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(20.dp)
                .onSizeChanged { trackWidthPx = it.width.toFloat() }
                .pointerInput(range, trackWidthPx) {
                    detectHorizontalDragGestures(
                        onDragStart = {
                            dragAccumPx = offset.toFloat() / range * (trackWidthPx / 2f)
                        },
                        onDragEnd = {
                            if (offset == 0) haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        },
                        onHorizontalDrag = { _, deltaX ->
                            if (trackWidthPx > 0f) {
                                dragAccumPx += deltaX
                                // Convert pixel position to step fraction
                                val halfW = trackWidthPx / 2f
                                val raw = (dragAccumPx / halfW) * range
                                val snapped = raw.roundToInt().coerceIn(-range, range)
                                if (snapped != lastSnap) {
                                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                    lastSnap = snapped
                                }
                                onOffsetChange(snapped)
                            }
                        },
                    )
                },
        ) {
            Canvas(modifier = Modifier.matchParentSize()) {
                val w = size.width
                val cy = size.height / 2f
                val halfW = w / 2f
                val pct = if (range == 0) 0.5f else (offset.toFloat() + range) / (range * 2f)
                val knobX = w * pct

                // Track base
                drawLine(
                    color = TrackColor,
                    start = Offset(0f, cy),
                    end = Offset(w, cy),
                    strokeWidth = 4.dp.toPx(),
                    cap = StrokeCap.Round,
                )

                // Filled highlight from center → knob
                if (offset != 0) {
                    val startX = if (offset > 0) halfW else knobX
                    val endX   = if (offset > 0) knobX  else halfW
                    drawLine(
                        brush = Brush.horizontalGradient(
                            colors = if (offset > 0)
                                listOf(CosmicPurple.copy(alpha = 0f), CosmicPurple.copy(alpha = 0.55f))
                            else
                                listOf(CosmicPurple.copy(alpha = 0.55f), CosmicPurple.copy(alpha = 0f)),
                            startX = startX,
                            endX = endX,
                        ),
                        start = Offset(startX, cy),
                        end = Offset(endX, cy),
                        strokeWidth = 4.dp.toPx(),
                        cap = StrokeCap.Round,
                    )
                }

                // Tick marks
                for (i in 0 until tickCount) {
                    val x = w * i.toFloat() / (tickCount - 1).toFloat()
                    val isCenter = i == tickCount / 2
                    val r = if (isCenter) 3.dp.toPx() else 1.5.dp.toPx()
                    if (isCenter) {
                        // Glowing today dot
                        drawCircle(color = CosmicPurple.copy(alpha = 0.35f), radius = r * 3, center = Offset(x, cy))
                    }
                    drawCircle(
                        color = if (isCenter) CosmicPurple else TickColor,
                        radius = r,
                        center = Offset(x, cy),
                    )
                }

                // Knob
                val knobR = 9.dp.toPx()
                // Glow ring
                drawCircle(color = CosmicPurple.copy(alpha = 0.35f), radius = knobR * 2f, center = Offset(knobX, cy))
                // White fill
                drawCircle(color = Color.White, radius = knobR, center = Offset(knobX, cy))
                // Purple border
                drawCircle(
                    color = CosmicPurple.copy(alpha = 0.55f),
                    radius = knobR - 1.dp.toPx(),
                    center = Offset(knobX, cy),
                    style = androidx.compose.ui.graphics.drawscope.Stroke(width = 2.dp.toPx()),
                )
            }
        }

        // Labels row
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "−${range}D",
                fontFamily = FontFamily.Monospace,
                fontSize = 10.sp,
                color = TextMuted,
            )
            Box(modifier = Modifier.weight(1f), contentAlignment = Alignment.Center) {
                Text(
                    text = label,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 11.sp,
                    color = Color.White,
                )
            }
            Text(
                text = "+${range}D",
                fontFamily = FontFamily.Monospace,
                fontSize = 10.sp,
                color = TextMuted,
            )
        }
    }
}
