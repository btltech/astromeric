package com.astromeric.android.app

import android.util.Log
import com.google.firebase.crashlytics.FirebaseCrashlytics

/**
 * Thin wrapper around Firebase Crashlytics.
 *
 * What is redacted: only the *values* of the custom keys passed to
 * [recordNonFatal], and only when the key name contains one of [SENSITIVE_KEYS]
 * (case-insensitive substring match, e.g. "birthDate" or "profile_name").
 *
 * What is NOT redacted and is sent as-is:
 *  - custom-key names, and values whose key doesn't match the list
 *    (e.g. "email", "place", "lat", "tz" are not on it);
 *  - [log] breadcrumb messages;
 *  - exception messages and stack traces, for both [recordNonFatal] and
 *    uncaught crashes (Crashlytics captures those automatically).
 *
 * Custom keys are session-wide in Crashlytics, so a key set here is attached to
 * every later report in the same process. Callers must keep personal data
 * (names, birth details, locations, journal or chart content) out of messages,
 * exception text and unlisted key names.
 */
object CrashReporter {
    private const val TAG = "CrashReporter"

    private val SENSITIVE_KEYS = listOf(
        "name", "birth", "dob", "dateofbirth", "timeofbirth", "placeofbirth",
        "latitude", "longitude", "journal", "chart", "profile",
    )

    private val crashlytics: FirebaseCrashlytics? by lazy {
        runCatching { FirebaseCrashlytics.getInstance() }.getOrNull()
    }

    /** Enable collection at startup. Safe to call once from Application.onCreate. */
    fun init(enabled: Boolean = true) {
        crashlytics?.isCrashlyticsCollectionEnabled = enabled
    }

    /** Report a handled (non-fatal) error with redacted context. */
    fun recordNonFatal(throwable: Throwable, context: Map<String, String> = emptyMap()) {
        val redacted = redact(context)
        Log.e(TAG, "Non-fatal: ${throwable.message} context=$redacted")
        crashlytics?.let { fc ->
            redacted.forEach { (k, v) -> fc.setCustomKey(k, v) }
            fc.recordException(throwable)
        }
    }

    /** Add a breadcrumb to the next crash report. The message is NOT redacted. */
    fun log(message: String) {
        crashlytics?.log(message)
    }

    internal fun redact(context: Map<String, String>): Map<String, String> =
        context.mapValues { (key, value) ->
            val lower = key.lowercase()
            if (SENSITIVE_KEYS.any { lower.contains(it) }) "<redacted>" else value
        }
}
