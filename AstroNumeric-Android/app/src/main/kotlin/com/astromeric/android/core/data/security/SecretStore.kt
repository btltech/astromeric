package com.astromeric.android.core.data.security

/** Where a small secret lives. Tests use an in-memory one; the app uses [KeystoreSecretStore]. */
interface SecretStore {
    fun read(): ByteArray?

    fun write(secret: ByteArray): Boolean

    fun clear()
}
