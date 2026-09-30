package com.astromeric.android.core.data.security

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.io.File
import java.security.KeyStore
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * The friends endpoints (under `/v2/friends`) are keyed only by the owner key sent in the
 * `X-Owner-Key` header, so that key has to be an unguessable secret. Local profile
 * ids (1, 2, ...) are the same on every device and must never be sent.
 *
 * A random 256-bit install secret is made once and kept for this device only:
 * encrypted with a non-exportable Android Keystore key, in a file excluded from
 * backups. Each profile's owner key is SHA-256("<secret>:<profileId>") as 64 hex
 * characters, exactly as on iOS, so every profile keeps its own friend list.
 */
object FriendsOwnerKey {
    const val HEADER = "X-Owner-Key"
    private const val SECRET_LENGTH = 32

    /** Where the install secret lives. Tests use an in-memory one. */
    interface SecretStore {
        fun read(): ByteArray?
        fun write(secret: ByteArray): Boolean
    }

    /** Owner key for a profile from a known secret. Matches iOS `FriendsOwnerKey.derive`. */
    fun derive(secret: ByteArray, profileId: Int): String {
        val digest = MessageDigest.getInstance("SHA-256")
        digest.update(secret)
        digest.update(":$profileId".toByteArray(Charsets.UTF_8))
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    /**
     * Owner key for a profile, or null if the secret can't be stored. Callers must not
     * fall back to the profile id.
     */
    fun ownerId(store: SecretStore, profileId: Int): String? {
        val secret = installSecret(store) ?: return null
        return derive(secret, profileId)
    }

    fun ownerId(context: Context, profileId: Int): String? =
        ownerId(KeystoreSecretStore(context.applicationContext), profileId)

    @Synchronized
    private fun installSecret(store: SecretStore): ByteArray? {
        store.read()?.takeIf { it.size == SECRET_LENGTH }?.let { return it }
        val fresh = ByteArray(SECRET_LENGTH).also { SecureRandom().nextBytes(it) }
        return if (store.write(fresh)) fresh else null
    }
}

/** Keeps the secret encrypted under an Android Keystore key, outside backups. */
internal class KeystoreSecretStore(context: Context) : FriendsOwnerKey.SecretStore {
    private val file = File(context.noBackupFilesDir, FILE_NAME)

    override fun read(): ByteArray? =
        runCatching {
            if (!file.exists()) return null
            val bytes = file.readBytes()
            val ivLength = bytes[0].toInt() and 0xFF
            val iv = bytes.copyOfRange(1, 1 + ivLength)
            val encrypted = bytes.copyOfRange(1 + ivLength, bytes.size)
            val cipher = Cipher.getInstance(TRANSFORMATION)
            cipher.init(Cipher.DECRYPT_MODE, key() ?: return null, GCMParameterSpec(TAG_BITS, iv))
            cipher.doFinal(encrypted)
        }.getOrNull()

    override fun write(secret: ByteArray): Boolean =
        runCatching {
            val cipher = Cipher.getInstance(TRANSFORMATION)
            cipher.init(Cipher.ENCRYPT_MODE, key(createIfMissing = true) ?: return false)
            val encrypted = cipher.doFinal(secret)
            val iv = cipher.iv
            file.writeBytes(byteArrayOf(iv.size.toByte()) + iv + encrypted)
            true
        }.getOrDefault(false)

    private fun key(createIfMissing: Boolean = false): SecretKey? {
        val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (store.getKey(ALIAS, null) as? SecretKey)?.let { return it }
        if (!createIfMissing) return null
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        generator.init(
            KeyGenParameterSpec.Builder(
                ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .build(),
        )
        return generator.generateKey()
    }

    private companion object {
        const val ALIAS = "astromeric_friends_owner"
        const val FILE_NAME = "friends-owner.key"
        const val TRANSFORMATION = "AES/GCM/NoPadding"
        const val TAG_BITS = 128
    }
}
