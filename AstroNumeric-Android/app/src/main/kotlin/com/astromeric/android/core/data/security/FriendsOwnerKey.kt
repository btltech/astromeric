package com.astromeric.android.core.data.security

import android.content.Context
import java.security.MessageDigest
import java.security.SecureRandom

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
    private const val FILE_NAME = "friends-owner.key"
    private const val KEY_ALIAS = "astromeric_friends_owner"
    private const val SECRET_LENGTH = 32

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
        ownerId(
            KeystoreSecretStore(context.applicationContext, FILE_NAME, KEY_ALIAS),
            profileId,
        )

    @Synchronized
    private fun installSecret(store: SecretStore): ByteArray? {
        store.read()?.takeIf { it.size == SECRET_LENGTH }?.let { return it }
        val fresh = ByteArray(SECRET_LENGTH).also { SecureRandom().nextBytes(it) }
        return if (store.write(fresh)) fresh else null
    }
}
