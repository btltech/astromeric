package com.astromeric.android.core.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle

private val DarkScheme = darkColorScheme(
    primary = Color(0xFFD8C8FF),
    onPrimary = Color(0xFF27114A),
    secondary = Color(0xFFFFC1D9),
    onSecondary = Color(0xFF3B1024),
    tertiary = Color(0xFFB9E7FF),
    background = Color(0xFF0F1022),
    surface = Color(0xFF181A33),
    surfaceVariant = Color(0xFF23264A),
    onSurface = Color(0xFFF0EEFF),
    onSurfaceVariant = Color(0xFFCBC6E8),
)

private val LightScheme = lightColorScheme(
    primary = Color(0xFF6B41B6),
    onPrimary = Color.White,
    secondary = Color(0xFFA03A69),
    onSecondary = Color.White,
    tertiary = Color(0xFF145A7C),
    background = Color(0xFFF7F3FF),
    surface = Color.White,
    surfaceVariant = Color(0xFFECE5FA),
    onSurface = Color(0xFF15152A),
    onSurfaceVariant = Color(0xFF4A4865),
)

private val HighContrastDarkScheme = DarkScheme.copy(
    primary = Color(0xFFF0E7FF),
    onPrimary = Color(0xFF17052F),
    secondary = Color(0xFFFFDFEA),
    onSecondary = Color(0xFF250714),
    surface = Color(0xFF13152A),
    surfaceVariant = Color(0xFF1A1D38),
    onSurface = Color(0xFFFFFFFF),
    onSurfaceVariant = Color(0xFFFFFFFF),
)

private val HighContrastLightScheme = LightScheme.copy(
    primary = Color(0xFF4A1E97),
    secondary = Color(0xFF7B1848),
    surface = Color(0xFFFFFFFF),
    surfaceVariant = Color(0xFFF4F0FF),
    onSurface = Color(0xFF000000),
    onSurfaceVariant = Color(0xFF15152A),
)

private val BaseTypography = Typography()

@Composable
fun AstroNumericTheme(
    darkTheme: Boolean = true,
    highContrastEnabled: Boolean = false,
    largeTextEnabled: Boolean = false,
    content: @Composable () -> Unit,
) {
    val colorScheme = when {
        darkTheme && highContrastEnabled -> HighContrastDarkScheme
        darkTheme -> DarkScheme
        highContrastEnabled -> HighContrastLightScheme
        else -> LightScheme
    }
    MaterialTheme(
        colorScheme = colorScheme,
        typography = scaledTypography(if (largeTextEnabled) 1.14f else 1f),
        content = content,
    )
}

private fun scaledTypography(scaleFactor: Float): Typography {
    if (scaleFactor == 1f) {
        return BaseTypography
    }
    return Typography(
        displayLarge = BaseTypography.displayLarge.scaled(scaleFactor),
        displayMedium = BaseTypography.displayMedium.scaled(scaleFactor),
        displaySmall = BaseTypography.displaySmall.scaled(scaleFactor),
        headlineLarge = BaseTypography.headlineLarge.scaled(scaleFactor),
        headlineMedium = BaseTypography.headlineMedium.scaled(scaleFactor),
        headlineSmall = BaseTypography.headlineSmall.scaled(scaleFactor),
        titleLarge = BaseTypography.titleLarge.scaled(scaleFactor),
        titleMedium = BaseTypography.titleMedium.scaled(scaleFactor),
        titleSmall = BaseTypography.titleSmall.scaled(scaleFactor),
        bodyLarge = BaseTypography.bodyLarge.scaled(scaleFactor),
        bodyMedium = BaseTypography.bodyMedium.scaled(scaleFactor),
        bodySmall = BaseTypography.bodySmall.scaled(scaleFactor),
        labelLarge = BaseTypography.labelLarge.scaled(scaleFactor),
        labelMedium = BaseTypography.labelMedium.scaled(scaleFactor),
        labelSmall = BaseTypography.labelSmall.scaled(scaleFactor),
    )
}

private fun TextStyle.scaled(scaleFactor: Float): TextStyle = copy(
    fontSize = fontSize * scaleFactor,
    lineHeight = lineHeight * scaleFactor,
)
