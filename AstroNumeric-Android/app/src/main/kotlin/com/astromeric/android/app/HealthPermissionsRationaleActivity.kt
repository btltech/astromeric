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

class HealthPermissionsRationaleActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AstroNumericTheme {
                HealthPermissionsRationaleScreen(
                    onContinue = {
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
private fun HealthPermissionsRationaleScreen(
    onContinue: () -> Unit,
    onClose: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text(
            text = "Health Connect Privacy",
            style = MaterialTheme.typography.headlineMedium,
        )
        Text(
            text = "AstroNumeric only requests read-only health access when you explicitly enable biometric-aware guidance.",
            style = MaterialTheme.typography.bodyLarge,
        )
        Text(
            text = "The Android build currently uses health context only to enrich Cosmic Guide responses with broad signals like heart rate, steps, calories, and sleep. It does not write health data, and core app features continue working when this access stays off.",
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = "You can revoke Health Connect permissions at any time in system settings. Health context is optional and never required for charts, readings, habits, or journaling.",
            style = MaterialTheme.typography.bodyMedium,
        )
        Button(
            modifier = Modifier.fillMaxWidth(),
            onClick = onContinue,
        ) {
            Text("Continue to app")
        }
        OutlinedButton(
            modifier = Modifier.fillMaxWidth(),
            onClick = onClose,
        ) {
            Text("Not now")
        }
    }
}