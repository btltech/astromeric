package com.astromeric.android.core.data.security

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** The owner key gates a whole friend list, so it has to match the server's rules and iOS. */
class FriendsOwnerKeyTest {
    private class MemoryStore(var secret: ByteArray? = null, val canWrite: Boolean = true) :
        SecretStore {
        var writes = 0

        override fun read(): ByteArray? = secret

        override fun write(secret: ByteArray): Boolean {
            if (!canWrite) return false
            writes += 1
            this.secret = secret
            return true
        }

        override fun clear() {
            secret = null
        }
    }

    // The server accepts a UUID or 32–64 hex characters.
    private val serverRule = Regex("^[0-9a-fA-F]{32,64}$")
    private val secret = ByteArray(32) { it.toByte() }

    @Test
    fun matchesTheKeyIosWorksOutForTheSameSecret() {
        // SHA-256 of the 32 bytes 0x00..0x1f followed by ":-1" and ":7", from an independent implementation.
        assertEquals("482e0805cfe6da7093a9e52b73ec4eda120d406e4de1079ec67b2e016535d154", FriendsOwnerKey.derive(secret, -1))
        assertEquals("d8d25f1410802c6265506035f9c915ccdabd7184241bb1b01f53d3a3a6906fdc", FriendsOwnerKey.derive(secret, 7))
    }

    @Test
    fun keyIsSixtyFourHexCharactersTheServerAccepts() {
        val key = FriendsOwnerKey.derive(secret, 1)
        assertEquals(64, key.length)
        assertTrue(serverRule.matches(key))
    }

    @Test
    fun everyProfileAndEveryInstallGetsItsOwnKey() {
        val other = ByteArray(32) { (it + 1).toByte() }
        assertNotEquals(FriendsOwnerKey.derive(secret, 1), FriendsOwnerKey.derive(secret, 2))
        assertNotEquals(FriendsOwnerKey.derive(secret, 1), FriendsOwnerKey.derive(other, 1))
    }

    @Test
    fun createsTheSecretOnceAndReusesIt() {
        val store = MemoryStore()
        val first = FriendsOwnerKey.ownerId(store, 1)
        val second = FriendsOwnerKey.ownerId(store, 1)
        assertEquals(first, second)
        assertEquals(1, store.writes)
        assertTrue(serverRule.matches(first!!))
    }

    @Test
    fun replacesAStoredSecretOfTheWrongSize() {
        val store = MemoryStore(secret = ByteArray(5))
        val key = FriendsOwnerKey.ownerId(store, 1)
        assertTrue(key != null && serverRule.matches(key))
        assertEquals(32, store.secret?.size)
    }

    @Test
    fun neverFallsBackToTheProfileIdWhenTheSecretCannotBeStored() {
        assertNull(FriendsOwnerKey.ownerId(MemoryStore(canWrite = false), 1))
    }
}
