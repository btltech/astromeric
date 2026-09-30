package com.astromeric.android.core.data.security

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Live AI is reserved for the owner's own device. The server only calls the AI
 * provider for requests carrying the private access code (`X-AI-Access`); the code is
 * typed in once here and never ships in the app. Without it the app hides every AI
 * feature and uses the built-in answers, so nobody else's questions leave our servers
 * for an AI provider. Same rule as iOS.
 */
class AIAccessController(private val store: SecretStore) {
    private val enabled = MutableStateFlow(false)

    @Volatile
    private var code: String? = null

    /** True while a code is stored. Screens read this to show or hide AI. */
    val isEnabled: StateFlow<Boolean> = enabled

    /** The code to send with requests, or null on a device without one (the normal case). */
    fun code(): String? = code

    /** Reads the stored code. Call once at startup. */
    fun load() {
        code = store.read()?.toString(Charsets.UTF_8)?.trim()?.takeIf { it.isNotEmpty() }
        enabled.value = code != null
    }

    /**
     * Stores [input], or clears the code when it is blank. Returns false if the code
     * could not be stored (nothing changes then).
     */
    fun set(input: String): Boolean {
        val trimmed = input.trim()
        if (trimmed.isEmpty()) {
            clear()
            return true
        }
        if (!store.write(trimmed.toByteArray(Charsets.UTF_8))) return false
        code = trimmed
        enabled.value = true
        return true
    }

    fun clear() {
        store.clear()
        code = null
        enabled.value = false
    }
}

/** The app's one controller. Call [install] in `Application.onCreate`. */
object AIAccess {
    private const val FILE_NAME = "ai-access.key"
    private const val KEY_ALIAS = "astromeric_ai_access"
    const val HEADER = "X-AI-Access"

    @Volatile
    private var controller: AIAccessController? = null
    private val notInstalled = MutableStateFlow(false)

    fun install(context: Context) {
        controller = AIAccessController(
            KeystoreSecretStore(context.applicationContext, FILE_NAME, KEY_ALIAS),
        ).also { it.load() }
    }

    val isEnabled: StateFlow<Boolean>
        get() = controller?.isEnabled ?: notInstalled

    fun code(): String? = controller?.code()

    fun set(input: String): Boolean = controller?.set(input) ?: false

    fun clear() {
        controller?.clear()
    }
}
