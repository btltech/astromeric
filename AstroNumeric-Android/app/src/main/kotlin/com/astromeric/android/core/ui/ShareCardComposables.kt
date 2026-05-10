package com.astromeric.android.core.ui

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Paint
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.platform.ViewCompositionStrategy
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import com.astromeric.android.core.model.ChartData
import com.astromeric.android.core.model.DailyForecastData
import com.astromeric.android.core.model.NumerologyData
import com.astromeric.android.core.model.TimingToolResult
import java.io.File
import java.util.Locale

// ──────────────────────────────────────────────────────────────────────────────
// Gradient colors matching iOS share card palette
// ──────────────────────────────────────────────────────────────────────────────
private val GradientStart = Color(0xFF20123A)
private val GradientMid   = Color(0xFF6241B5)
private val GradientEnd   = Color(0xFF187F8A)
private val PurpleAccent  = Color(0xFFD8C8FF)
private val PinkAccent    = Color(0xFFFFB3D1)
private val CardBg        = Color(0xFF181A33)
private val FooterBg      = Color(0xFF23264A)
private val TextPrimary   = Color(0xFFF0EEFF)
private val TextSecondary = Color(0xFFCBC6E8)
private val TextMuted     = Color(0xFF8B88AA)
private val Green         = Color(0xFF4FC978)
private val Orange        = Color(0xFFFFB347)

// ──────────────────────────────────────────────────────────────────────────────
// Shared card components
// ──────────────────────────────────────────────────────────────────────────────

@Composable
private fun ShareCardHeader(icon: String, title: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(90.dp)
            .background(
                Brush.linearGradient(
                    colors = listOf(GradientStart, GradientMid, GradientEnd),
                    start = Offset(0f, 0f),
                    end = Offset(Float.MAX_VALUE, Float.MAX_VALUE),
                ),
            ),
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(icon, fontSize = 24.sp)
            Text(
                text = title,
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary,
            )
            Text(
                text = "AstroNumeric",
                fontSize = 10.sp,
                fontWeight = FontWeight.Medium,
                color = TextPrimary.copy(alpha = 0.75f),
            )
        }
    }
}

@Composable
private fun ShareCardFooter() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(FooterBg)
            .padding(vertical = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text(
            text = "Shared from AstroNumeric",
            fontSize = 10.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextSecondary,
        )
        Text(
            text = "astromeric.com",
            fontSize = 9.sp,
            fontWeight = FontWeight.Medium,
            fontFamily = FontFamily.Monospace,
            color = TextMuted,
        )
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// Reading share card
// ──────────────────────────────────────────────────────────────────────────────

@Composable
fun ReadingShareCard(
    forecast: DailyForecastData,
    modifier: Modifier = Modifier,
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = CardBg,
        modifier = modifier.width(300.dp),
    ) {
        Column {
            ShareCardHeader(icon = "✨", title = "AstroNumeric")

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(CardBg)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                val scopeLabel = forecast.scope?.replaceFirstChar { it.titlecase(Locale.ROOT) } ?: "Daily"
                Text(
                    text = "$scopeLabel Reading",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary,
                )
                forecast.date?.let {
                    Text(text = it, fontSize = 11.sp, color = TextSecondary)
                }

                // Score ring
                forecast.overallScore?.let { rawScore ->
                    val score = rawScore * 10f  // 0–1 float → 0–100
                    val normalised = (score / 100f).coerceIn(0f, 1f)
                    val displayScore = String.format(Locale.ROOT, "%.1f", rawScore * 10f / 10f)
                    Box(contentAlignment = Alignment.Center) {
                        // Background ring
                        Box(
                            modifier = Modifier
                                .size(80.dp)
                                .drawBehind {
                                    drawArc(
                                        color = PurpleAccent.copy(alpha = 0.3f),
                                        startAngle = 0f,
                                        sweepAngle = 360f,
                                        useCenter = false,
                                        style = Stroke(width = 8.dp.toPx()),
                                    )
                                    drawArc(
                                        brush = Brush.sweepGradient(listOf(PurpleAccent, PinkAccent)),
                                        startAngle = -90f,
                                        sweepAngle = 360f * normalised,
                                        useCenter = false,
                                        style = Stroke(width = 8.dp.toPx(), cap = StrokeCap.Round),
                                    )
                                },
                        )
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(displayScore, fontSize = 18.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                            Text("/10", fontSize = 10.sp, color = TextSecondary)
                        }
                    }
                }

                // Top 3 sections
                forecast.sections.take(3).forEach { section ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                    ) {
                        Text(section.title, fontSize = 13.sp, color = TextPrimary, fontWeight = FontWeight.Medium)
                        val preview = section.summary.take(32) + if (section.summary.length > 32) "…" else ""
                        Text(preview, fontSize = 11.sp, color = TextSecondary, maxLines = 1)
                    }
                }
            }

            ShareCardFooter()
        }
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// Numerology share card
// ──────────────────────────────────────────────────────────────────────────────

@Composable
fun NumerologyShareCard(
    data: NumerologyData,
    profileName: String,
    modifier: Modifier = Modifier,
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = CardBg,
        modifier = modifier.width(300.dp),
    ) {
        Column {
            ShareCardHeader(icon = "✦", title = "Numerology")

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(CardBg)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(
                    text = profileName,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary,
                )

                // Life Path
                Text(
                    text = "Life Path",
                    fontSize = 11.sp,
                    color = TextSecondary,
                )
                Text(
                    text = "${data.lifePath.number}",
                    fontSize = 40.sp,
                    fontWeight = FontWeight.Bold,
                    color = PurpleAccent,
                )
                val meaningPreview = data.lifePath.meaning.take(60) + if (data.lifePath.meaning.length > 60) "…" else ""
                Text(
                    text = meaningPreview,
                    fontSize = 11.sp,
                    color = TextSecondary,
                    maxLines = 2,
                )

                // Lucky numbers
                if (data.luckyNumbers.isNotEmpty()) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(text = "Lucky:", fontSize = 11.sp, color = TextSecondary)
                        data.luckyNumbers.take(5).forEach { num ->
                            Text(text = "$num", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = PurpleAccent)
                        }
                    }
                }
            }

            ShareCardFooter()
        }
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// Timing share card
// ──────────────────────────────────────────────────────────────────────────────

@Composable
fun TimingShareCard(
    result: TimingToolResult,
    modifier: Modifier = Modifier,
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = CardBg,
        modifier = modifier.width(300.dp),
    ) {
        Column {
            ShareCardHeader(icon = "⏰", title = "Best Timing")

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(CardBg)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(
                    text = result.activity.displayName,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary,
                )

                result.bestTimes.firstOrNull()?.let { best ->
                    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(text = "Best window", fontSize = 11.sp, color = TextSecondary)
                        Text(text = best, fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Green)
                    }
                }

                result.tips.firstOrNull()?.let { tip ->
                    Text(
                        text = "💡 ${tip.take(80)}${if (tip.length > 80) "…" else ""}",
                        fontSize = 11.sp,
                        color = TextSecondary,
                        maxLines = 2,
                    )
                }
            }

            ShareCardFooter()
        }
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// Chart share card
// ──────────────────────────────────────────────────────────────────────────────

@Composable
private fun BigThreeItem(label: String, sign: String, estimated: Boolean = false) {
    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(label, fontSize = 20.sp)
        Text(
            text = if (estimated) "~$sign" else sign,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            color = if (estimated) Orange else PurpleAccent,
        )
        if (estimated) {
            Text(text = "est.", fontSize = 9.sp, color = Orange.copy(alpha = 0.8f))
        }
    }
}

@Composable
fun ChartShareCard(
    chart: ChartData,
    profileName: String,
    birthTimeAssumed: Boolean = false,
    modifier: Modifier = Modifier,
) {
    val sun  = chart.planets.firstOrNull { it.name.equals("Sun", ignoreCase = true) }
    val moon = chart.planets.firstOrNull { it.name.equals("Moon", ignoreCase = true) }
    val asc  = chart.points.firstOrNull { it.name.equals("Ascendant", ignoreCase = true) || it.name.equals("ASC", ignoreCase = true) }

    Surface(
        shape = RoundedCornerShape(16.dp),
        color = CardBg,
        modifier = modifier.width(300.dp),
    ) {
        Column {
            ShareCardHeader(icon = "⬡", title = "Birth Chart")

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(CardBg)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(
                    text = profileName,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary,
                )

                // Big Three
                Row(
                    horizontalArrangement = Arrangement.spacedBy(20.dp, Alignment.CenterHorizontally),
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    sun?.let  { BigThreeItem("☉", it.sign) }
                    moon?.let { BigThreeItem("☾", it.sign) }
                    asc?.let  { BigThreeItem("↑", it.sign, birthTimeAssumed) }
                }

                val planetCount = chart.planets.size + chart.points.size
                Text(
                    text = "$planetCount placements mapped",
                    fontSize = 11.sp,
                    color = TextSecondary,
                )

                if (birthTimeAssumed) {
                    Text(
                        text = "Rising sign estimated (birth time unknown)",
                        fontSize = 10.sp,
                        color = Orange,
                        maxLines = 1,
                    )
                }
            }

            ShareCardFooter()
        }
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// Bitmap renderer — renders a Composable off-screen via ComposeView → Bitmap
// ──────────────────────────────────────────────────────────────────────────────

fun renderComposableToBitmap(
    context: Context,
    widthPx: Int,
    heightPx: Int,
    content: @Composable () -> Unit,
): Bitmap {
    val composeView = ComposeView(context).apply {
        setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnDetachedFromWindow)
        setContent(content)
    }
    composeView.measure(
        android.view.View.MeasureSpec.makeMeasureSpec(widthPx, android.view.View.MeasureSpec.EXACTLY),
        android.view.View.MeasureSpec.makeMeasureSpec(0, android.view.View.MeasureSpec.UNSPECIFIED),
    )
    composeView.layout(0, 0, composeView.measuredWidth, composeView.measuredHeight)
    val bitmap = Bitmap.createBitmap(composeView.measuredWidth, composeView.measuredHeight, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(bitmap)
    composeView.draw(canvas)
    return bitmap
}

// ──────────────────────────────────────────────────────────────────────────────
// Share dispatcher — saves bitmap to cache and fires a share intent with image
// ──────────────────────────────────────────────────────────────────────────────

fun shareBitmapCard(
    context: Context,
    bitmap: Bitmap,
    filename: String = "astromeric_share.png",
    chooserTitle: String = "Share via",
) {
    val cacheDir = File(context.cacheDir, "share_cards").apply { mkdirs() }
    val file = File(cacheDir, filename)
    file.outputStream().use { bitmap.compress(Bitmap.CompressFormat.PNG, 95, it) }
    val uri: Uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)

    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "image/png"
        putExtra(Intent.EXTRA_STREAM, uri)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(Intent.createChooser(intent, chooserTitle))
}
