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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
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
            text = stringResource(R.string.health_onboarding_title),
            style = MaterialTheme.typography.headlineMedium,
        )
        Text(
            text = stringResource(R.string.health_onboarding_description_1),
            style = MaterialTheme.typography.bodyLarge,
        )
        Text(
            text = stringResource(R.string.health_onboarding_description_2),
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = stringResource(R.string.health_onboarding_description_3),
            style = MaterialTheme.typography.bodyMedium,
        )
        Button(
            modifier = Modifier.fillMaxWidth(),
            onClick = onOpenApp,
        ) {
            Text(stringResource(R.string.health_onboarding_button_open))
        }
        OutlinedButton(
            modifier = Modifier.fillMaxWidth(),
            onClick = onClose,
        ) {
            Text(stringResource(R.string.health_onboarding_button_close))
        }
    }
}