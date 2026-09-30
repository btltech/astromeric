package com.astromeric.android.core.data.security

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.io.File
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * Keeps a secret encrypted under a non-exportable Android Keystore key, in a file
 * excluded from backups (so it can't be restored onto a device that lacks the key).
 */
class KeystoreSecretStore(
    context: Context,
    fileName: String,
    private val alias: String,
) : SecretStore {
    private val file = File(context.noBackupFilesDir, fileName)

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

    override fun clear() {
        runCatching { file.delete() }
    }

    private fun key(createIfMissing: Boolean = false): SecretKey? {
        val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (store.getKey(alias, null) as? SecretKey)?.let { return it }
        if (!createIfMissing) return null
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        generator.init(
            KeyGenParameterSpec.Builder(
                alias,
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
        const val TRANSFORMATION = "AES/GCM/NoPadding"
        const val TAG_BITS = 128
    }
}
