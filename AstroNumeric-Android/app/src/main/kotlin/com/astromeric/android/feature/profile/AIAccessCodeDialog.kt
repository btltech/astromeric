package com.astromeric.android.feature.profile

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.astromeric.android.R
import com.astromeric.android.core.data.security.AIAccess

/**
 * Where the owner types the AI access code (opened by tapping the version line seven
 * times). The field never shows a stored code, and the code never leaves the device
 * except in the `X-AI-Access` header of requests to our own server.
 */
@Composable
fun AIAccessCodeDialog(onDismiss: () -> Unit) {
    var code by remember { mutableStateOf("") }
    var failed by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.ai_access_title)) },
        text = {
            Column(verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = code,
                    onValueChange = {
                        code = it
                        failed = false
                    },
                    label = { Text(stringResource(R.string.ai_access_hint)) },
                    singleLine = true,
                    visualTransformation = PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    modifier = Modifier.fillMaxWidth(),
                )
                Text(
                    text = stringResource(R.string.ai_access_body),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (failed) {
                    Text(
                        text = stringResource(R.string.ai_access_error),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error,
                    )
                }
            }
        },
        confirmButton = {
            TextButton(
                enabled = code.isNotBlank(),
                onClick = {
                    if (AIAccess.set(code)) onDismiss() else failed = true
                },
            ) {
                Text(stringResource(R.string.ai_access_save))
            }
        },
        dismissButton = {
            Column {
                TextButton(
                    onClick = {
                        AIAccess.clear()
                        onDismiss()
                    },
                ) {
                    Text(stringResource(R.string.ai_access_remove))
                }
                TextButton(onClick = onDismiss) {
                    Text(stringResource(R.string.ai_access_cancel))
                }
            }
        },
    )
}
