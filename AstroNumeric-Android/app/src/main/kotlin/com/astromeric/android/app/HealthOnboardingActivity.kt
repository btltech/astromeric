package com.astromeric.android.app

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.astromeric.android.core.ui.theme.AstroNumericTheme

class HealthOnboardingActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AstroNumericTheme {
                HealthOnboardingScreen(
                    onOpenApp = {
                        startActivity(Intent(this, MainActivity::class.java))
                        finish()
                    },
                    onClose = { finish() },
                )
            }
        }
    }
}

@Composable
private fun HealthOnboardingScreen(
    onOpenApp: () -> Unit,
    onClose: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text(
            text = "Connect AstroNumeric to Health Connect",
            style = MaterialTheme.typography.headlineMedium,
        )
        Text(
            text = "Biometric-aware guidance is optional. When enabled, AstroNumeric can read a small set of health signals to add context to Cosmic Guide.",
            style = MaterialTheme.typography.bodyLarge,
        )
        Text(
            text = "Current Android support is read-only and limited to heart rate, resting heart rate, steps, total calories burned, and sleep. This data stays optional and does not block normal app use.",
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = "You control this consent from the app and from Android settings. You can disconnect it any time.",
            style = MaterialTheme.typography.bodyMedium,
        )
        Button(
            modifier = Modifier.fillMaxWidth(),
            onClick = onOpenApp,
        ) {
            Text("Open AstroNumeric")
        }
        OutlinedButton(
            modifier = Modifier.fillMaxWidth(),
            onClick = onClose,
        ) {
            Text("Close")
        }
    }
}