package com.astromeric.android.feature.journal

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.core.content.ContextCompat
import java.util.Locale

class VoiceJournalRecorder(
    private val context: Context,
) {
    var isRecording by mutableStateOf(false)
        private set

    var isAuthorized by mutableStateOf(false)
        private set

    var transcript by mutableStateOf("")
        private set

    var completedTranscript by mutableStateOf<String?>(null)
        private set

    var error by mutableStateOf<String?>(null)
        private set

    private val mainHandler = Handler(Looper.getMainLooper())
    private var speechRecognizer: SpeechRecognizer? = null

    fun refreshAuthorizationStatus() {
        isAuthorized = hasRecordAudioPermission()
    }

    fun onPermissionResult(granted: Boolean) {
        isAuthorized = granted
        error = if (granted) null else "Microphone access not authorized"
    }

    fun startRecording() {
        if (isRecording) {
            return
        }

        if (!hasRecordAudioPermission()) {
            isAuthorized = false
            error = "Microphone access not authorized"
            return
        }

        if (!SpeechRecognizer.isRecognitionAvailable(context)) {
            error = "Speech recognition unavailable"
            return
        }

        error = null
        transcript = ""
        completedTranscript = null
        isAuthorized = true
        destroyRecognizer()

        val recognizer = SpeechRecognizer.createSpeechRecognizer(context)
        speechRecognizer = recognizer
        recognizer.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) = Unit

            override fun onBeginningOfSpeech() = Unit

            override fun onRmsChanged(rmsdB: Float) = Unit

            override fun onBufferReceived(buffer: ByteArray?) = Unit

            override fun onEndOfSpeech() = Unit

            override fun onError(errorCode: Int) {
                postToMain {
                    isRecording = false
                    error = when (errorCode) {
                        SpeechRecognizer.ERROR_AUDIO -> "Audio capture error"
                        SpeechRecognizer.ERROR_CLIENT -> null
                        SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Microphone access not authorized"
                        SpeechRecognizer.ERROR_NETWORK,
                        SpeechRecognizer.ERROR_NETWORK_TIMEOUT,
                        SpeechRecognizer.ERROR_SERVER -> "Speech recognition unavailable"
                        SpeechRecognizer.ERROR_NO_MATCH,
                        SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> null
                        else -> "Speech recognition error"
                    }
                }
                destroyRecognizer()
            }

            override fun onResults(results: Bundle?) {
                val bestTranscript = results.bestTranscript()
                postToMain {
                    if (!bestTranscript.isNullOrBlank()) {
                        transcript = bestTranscript
                        completedTranscript = bestTranscript
                    }
                    isRecording = false
                }
                destroyRecognizer()
            }

            override fun onPartialResults(partialResults: Bundle?) {
                val bestTranscript = partialResults.bestTranscript()
                if (!bestTranscript.isNullOrBlank()) {
                    postToMain {
                        transcript = bestTranscript
                    }
                }
            }

            override fun onEvent(eventType: Int, params: Bundle?) = Unit
        })

        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, Locale.getDefault().toLanguageTag())
        }

        recognizer.startListening(intent)
        isRecording = true
    }

    fun stopRecording() {
        speechRecognizer?.stopListening()
        isRecording = false
    }

    fun consumeCompletedTranscript(): String? {
        val value = completedTranscript?.trim()?.takeIf { it.isNotEmpty() }
        completedTranscript = null
        if (value != null) {
            transcript = ""
        }
        return value
    }

    fun destroy() {
        destroyRecognizer()
        isRecording = false
        transcript = ""
        completedTranscript = null
        error = null
    }

    private fun hasRecordAudioPermission(): Boolean =
        ContextCompat.checkSelfPermission(context, android.Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED

    private fun destroyRecognizer() {
        speechRecognizer?.cancel()
        speechRecognizer?.destroy()
        speechRecognizer = null
    }

    private fun postToMain(block: () -> Unit) {
        mainHandler.post(block)
    }
}

private fun Bundle?.bestTranscript(): String? =
    this?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()