package com.astromeric.android.feature.profile

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.content.Context
import android.graphics.Paint
import android.graphics.drawable.ColorDrawable
import android.location.Geocoder
import android.os.Build
import android.view.View
import android.view.ViewGroup
import android.widget.DatePicker
import android.widget.EditText
import android.widget.NumberPicker
import android.widget.TextView
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.input.ImeAction
import com.astromeric.android.R
import com.astromeric.android.core.data.repository.ProfileRepository
import com.astromeric.android.core.model.AppProfile
import com.astromeric.android.core.model.DefaultHouseSystem
import com.astromeric.android.core.model.ProfileDraft
import com.astromeric.android.core.model.TimeConfidence
import com.astromeric.android.core.ui.PremiumContentCard
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

private val EditorDateFormatter: DateTimeFormatter = DateTimeFormatter.ISO_LOCAL_DATE

@Composable
fun ProfileEditorScreen(
    existingProfile: AppProfile?,
    profileRepository: ProfileRepository,
    onSaved: () -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier,
    isOnboarding: Boolean = false,
    scrollable: Boolean = true,
) {
    val context = LocalContext.current
    val keyboardController = LocalSoftwareKeyboardController.current
    val scope = rememberCoroutineScope()

    var name by rememberSaveable(existingProfile?.id) { mutableStateOf(existingProfile?.name.orEmpty()) }
    var birthDate by rememberSaveable(existingProfile?.id) { mutableStateOf(existingProfile?.dateOfBirth ?: LocalDate.now().minusYears(20).format(EditorDateFormatter)) }
    var timeConfidence by rememberSaveable(existingProfile?.id) { mutableStateOf(existingProfile?.timeConfidence ?: TimeConfidence.UNKNOWN) }
    var birthTime by rememberSaveable(existingProfile?.id) { mutableStateOf(existingProfile?.timeOfBirth?.take(5).orEmpty()) }
    var placeOfBirth by rememberSaveable(existingProfile?.id) { mutableStateOf(existingProfile?.placeOfBirth.orEmpty()) }
    var isSaving by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    val fallbackTimezone = existingProfile?.timezone?.takeUnless { it.isBlank() } ?: ZoneId.systemDefault().id
    val canSave = name.isNotBlank() &&
        birthDate.isNotBlank() &&
        placeOfBirth.isNotBlank() &&
        (timeConfidence == TimeConfidence.UNKNOWN || birthTime.matches(Regex("^\\d{2}:\\d{2}$")))

    fun submitProfile() {
        if (isSaving) return

        keyboardController?.hide()
        scope.launch {
            errorMessage = null
            if (!canSave) {
                errorMessage = "Name, birth date, birth place, and a valid time are required."
                return@launch
            }

            isSaving = true
            try {
                val trimmedBirthplace = placeOfBirth.trim()
                val resolvedBirthplace = existingProfile
                    ?.takeIf {
                        it.placeOfBirth?.equals(trimmedBirthplace, ignoreCase = true) == true &&
                            it.latitude != null &&
                            it.longitude != null &&
                            !it.timezone.isNullOrBlank()
                    }
                    ?.let {
                        ResolvedBirthplace(
                            displayName = requireNotNull(it.placeOfBirth),
                            latitude = requireNotNull(it.latitude),
                            longitude = requireNotNull(it.longitude),
                            timezone = requireNotNull(it.timezone),
                        )
                    }
                    ?: resolveBirthplace(
                        context = context,
                        query = trimmedBirthplace,
                        fallbackTimezone = fallbackTimezone,
                    )

                if (resolvedBirthplace == null) {
                    errorMessage = "Could not confirm that birth place. Enter a city and country, then try again."
                    return@launch
                }

                profileRepository.saveProfile(
                    draft = ProfileDraft(
                        id = existingProfile?.id,
                        name = name,
                        dateOfBirth = birthDate,
                        timeOfBirth = if (timeConfidence == TimeConfidence.UNKNOWN) null else "$birthTime:00",
                        timeConfidence = timeConfidence,
                        placeOfBirth = resolvedBirthplace.displayName,
                        latitude = resolvedBirthplace.latitude,
                        longitude = resolvedBirthplace.longitude,
                        timezone = resolvedBirthplace.timezone,
                        houseSystem = existingProfile?.houseSystem ?: DefaultHouseSystem,
                    ),
                )
                onSaved()
            } finally {
                isSaving = false
            }
        }
    }

    Column(
        modifier = if (scrollable) modifier.verticalScroll(rememberScrollState()) else modifier,
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        PremiumContentCard(
            title = if (existingProfile == null) {
                if (isOnboarding) "Create your first profile" else "Create profile"
            } else {
                "Edit profile"
            },
            body = "Phase 1 already matches the iOS time-confidence rules and local persistence strategy.",
        )

        errorMessage?.let { message ->
            Text(
                text = message,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("Name") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
        )

        DateInputRow(
            birthDate = birthDate,
            birthTime = birthTime,
            timeConfidence = timeConfidence,
            onBirthDateChange = { birthDate = it },
            onBirthTimeChange = { birthTime = it },
            onTimeConfidenceChange = { timeConfidence = it },
            modifier = Modifier.fillMaxWidth(),
        )

        OutlinedTextField(
            value = placeOfBirth,
            onValueChange = { placeOfBirth = it },
            label = { Text("Birth place") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
            keyboardActions = KeyboardActions(onDone = { submitProfile() }),
        )

        Text(
            text = "Enter a city and country. Coordinates and timezone are confirmed automatically when you save, matching iOS.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            if (!isOnboarding) {
                TextButton(onClick = onCancel, modifier = Modifier.weight(1f)) {
                    Text("Cancel")
                }
            }
            Button(
                onClick = ::submitProfile,
                modifier = Modifier.weight(1f),
                enabled = !isSaving,
            ) {
                Text(if (isSaving) "Saving..." else if (existingProfile == null) "Create profile" else "Save changes")
            }
        }
    }
}

@Composable
@OptIn(ExperimentalLayoutApi::class)
private fun DateInputRow(
    birthDate: String,
    birthTime: String,
    timeConfidence: TimeConfidence,
    onBirthDateChange: (String) -> Unit,
    onBirthTimeChange: (String) -> Unit,
    onTimeConfidenceChange: (TimeConfidence) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val colorScheme = MaterialTheme.colorScheme
    val isDarkTheme = isSystemInDarkTheme()
    val initialDate = remember(birthDate) {
        runCatching { LocalDate.parse(birthDate, EditorDateFormatter) }.getOrElse { LocalDate.now().minusYears(20) }
    }

    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(text = "Birth details", style = MaterialTheme.typography.titleMedium)

        Button(
            onClick = {
                val dateDialog = DatePickerDialog(
                    context,
                    R.style.Theme_AstroNumeric_Android_DatePicker,
                    { _, year, month, dayOfMonth ->
                        onBirthDateChange(LocalDate.of(year, month + 1, dayOfMonth).format(EditorDateFormatter))
                    },
                    initialDate.year,
                    initialDate.monthValue - 1,
                    initialDate.dayOfMonth,
                )
                dateDialog.setOnShowListener {
                    styleSpinnerDatePickerDialog(
                        dialog = dateDialog,
                        surfaceColor = colorScheme.surfaceVariant.toArgb(),
                        onSurfaceColor = colorScheme.onSurface.toArgb(),
                        onSurfaceVariantColor = colorScheme.onSurfaceVariant.toArgb(),
                        accentColor = colorScheme.primary.toArgb(),
                        isDarkTheme = isDarkTheme,
                    )
                }
                dateDialog.show()
            },
        ) {
            Text("Birth date: $birthDate")
        }

        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            TimeConfidence.entries.forEach { option ->
                FilterChip(
                    selected = timeConfidence == option,
                    onClick = { onTimeConfidenceChange(option) },
                    label = { Text(option.shortLabel) },
                )
            }
        }

        if (timeConfidence != TimeConfidence.UNKNOWN) {
            Button(
                onClick = {
                    val parts = birthTime.split(":")
                    val hour = parts.getOrNull(0)?.toIntOrNull() ?: 12
                    val minute = parts.getOrNull(1)?.toIntOrNull() ?: 0
                    TimePickerDialog(
                        context,
                        { _, pickedHour, pickedMinute ->
                            onBirthTimeChange(String.format(Locale.US, "%02d:%02d", pickedHour, pickedMinute))
                        },
                        hour,
                        minute,
                        true,
                    ).show()
                },
            ) {
                Text("Birth time: ${birthTime.ifBlank { "Tap to choose" }}")
            }
            if (timeConfidence == TimeConfidence.APPROXIMATE) {
                Text(
                    text = "Approximate times are saved and treated as estimated for rising sign and house logic.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        } else {
            Text(
                text = "Unknown birth time falls back to noon-style estimation, matching the iOS data-quality rules.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

private fun styleSpinnerDatePickerDialog(
    dialog: DatePickerDialog,
    surfaceColor: Int,
    onSurfaceColor: Int,
    onSurfaceVariantColor: Int,
    accentColor: Int,
    isDarkTheme: Boolean,
) {
    dialog.window?.setBackgroundDrawable(ColorDrawable(surfaceColor))
    dialog.getButton(DatePickerDialog.BUTTON_POSITIVE)?.setTextColor(accentColor)
    dialog.getButton(DatePickerDialog.BUTTON_NEGATIVE)?.setTextColor(accentColor)
    dialog.datePicker.applySpinnerPalette(
        surfaceColor = surfaceColor,
        textColor = onSurfaceColor,
        secondaryTextColor = onSurfaceVariantColor,
        accentColor = accentColor,
        isDarkTheme = isDarkTheme,
    )
}

private fun DatePicker.applySpinnerPalette(
    surfaceColor: Int,
    textColor: Int,
    secondaryTextColor: Int,
    accentColor: Int,
    isDarkTheme: Boolean,
) {
    setBackgroundColor(surfaceColor)
    findNumberPickers().forEach { picker ->
        picker.setBackgroundColor(surfaceColor)
        picker.descendantFocusability = NumberPicker.FOCUS_BLOCK_DESCENDANTS
        tintNumberPickerDivider(picker, accentColor)
        tintNumberPickerSelectorWheel(
            picker = picker,
            color = adjustAlpha(textColor, if (isDarkTheme) 0.86f else 0.76f),
        )
        picker.findEmbeddedEditTexts().forEach { editText ->
            editText.setTextColor(textColor)
            editText.setHintTextColor(adjustAlpha(textColor, if (isDarkTheme) 0.72f else 0.6f))
            editText.setBackgroundColor(surfaceColor)
            editText.highlightColor = adjustAlpha(accentColor, 0.18f)
        }
        picker.findEmbeddedLabelTextViews().forEach { label ->
            label.setTextColor(secondaryTextColor)
            label.setHintTextColor(adjustAlpha(secondaryTextColor, if (isDarkTheme) 0.9f else 0.78f))
        }
    }
}

private fun DatePicker.findNumberPickers(): List<NumberPicker> = buildList {
    collectNumberPickers(this@findNumberPickers, this)
}

private fun collectNumberPickers(view: View, pickers: MutableList<NumberPicker>) {
    when (view) {
        is NumberPicker -> pickers += view
        is ViewGroup -> {
            for (index in 0 until view.childCount) {
                collectNumberPickers(view.getChildAt(index), pickers)
            }
        }
    }
}

private fun NumberPicker.findEmbeddedEditTexts(): List<EditText> = buildList {
    collectEditTexts(this@findEmbeddedEditTexts, this)
}

private fun NumberPicker.findEmbeddedLabelTextViews(): List<TextView> = buildList {
    collectLabelTextViews(this@findEmbeddedLabelTextViews, this)
}

private fun collectEditTexts(view: View, editTexts: MutableList<EditText>) {
    when (view) {
        is EditText -> editTexts += view
        is ViewGroup -> {
            for (index in 0 until view.childCount) {
                collectEditTexts(view.getChildAt(index), editTexts)
            }
        }
    }
}

private fun collectLabelTextViews(view: View, textViews: MutableList<TextView>) {
    when (view) {
        is EditText -> Unit
        is TextView -> textViews += view
        is ViewGroup -> {
            for (index in 0 until view.childCount) {
                collectLabelTextViews(view.getChildAt(index), textViews)
            }
        }
    }
}

private fun tintNumberPickerDivider(picker: NumberPicker, color: Int) {
    runCatching {
        val dividerField = NumberPicker::class.java.getDeclaredField("mSelectionDivider")
        dividerField.isAccessible = true
        dividerField.set(picker, ColorDrawable(color))
        picker.invalidate()
    }
}

private fun tintNumberPickerSelectorWheel(picker: NumberPicker, color: Int) {
    runCatching {
        val selectorWheelPaintField = NumberPicker::class.java.getDeclaredField("mSelectorWheelPaint")
        selectorWheelPaintField.isAccessible = true
        val selectorWheelPaint = selectorWheelPaintField.get(picker) as? Paint ?: return@runCatching
        selectorWheelPaint.color = color
        picker.invalidate()
    }
}

private fun adjustAlpha(color: Int, factor: Float): Int {
    val alpha = (color ushr 24) and 0xFF
    val red = (color ushr 16) and 0xFF
    val green = (color ushr 8) and 0xFF
    val blue = color and 0xFF
    val adjustedAlpha = (alpha * factor).toInt().coerceIn(0, 255)
    return (adjustedAlpha shl 24) or (red shl 16) or (green shl 8) or blue
}

private data class ResolvedBirthplace(
    val displayName: String,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
)

@Suppress("DEPRECATION")
private suspend fun resolveBirthplace(
    context: Context,
    query: String,
    fallbackTimezone: String = ZoneId.systemDefault().id,
): ResolvedBirthplace? = withContext(Dispatchers.IO) {
    if (query.isBlank() || !Geocoder.isPresent()) {
        return@withContext null
    }

    val geocoder = Geocoder(context, Locale.getDefault())
    val addresses = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        suspendGeocode(geocoder, query)
    } else {
        geocoder.getFromLocationName(query, 1).orEmpty()
    }

    val address = addresses.firstOrNull() ?: return@withContext null
    val displayName = listOfNotNull(address.locality, address.adminArea, address.countryName)
        .distinct()
        .joinToString(separator = ", ")
        .ifBlank { address.featureName ?: query }
    val timezone = address.extras?.getString("timezone")
        ?: address.extras?.getString("timeZone")
        ?: fallbackTimezone

    ResolvedBirthplace(
        displayName = displayName,
        latitude = address.latitude,
        longitude = address.longitude,
        timezone = timezone,
    )
}

private suspend fun suspendGeocode(
    geocoder: Geocoder,
    query: String,
): List<android.location.Address> = kotlinx.coroutines.suspendCancellableCoroutine { continuation ->
    geocoder.getFromLocationName(query, 1) { addresses ->
        if (continuation.isActive) {
            continuation.resume(addresses) { _, _, _ -> }
        }
    }
}