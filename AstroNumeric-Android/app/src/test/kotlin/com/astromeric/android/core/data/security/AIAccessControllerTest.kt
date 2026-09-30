package com.astromeric.android.core.data.security

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** AI stays owner-only: nothing is sent, and nothing is shown, without the stored code. */
class AIAccessControllerTest {
    private class MemoryStore(var bytes: ByteArray? = null, val canWrite: Boolean = true) : SecretStore {
        override fun read(): ByteArray? = bytes

        override fun write(secret: ByteArray): Boolean {
            if (!canWrite) return false
            bytes = secret
            return true
        }

        override fun clear() {
            bytes = null
        }
    }

    @Test
    fun aDeviceWithoutACodeHasAiOff() {
        val controller = AIAccessController(MemoryStore()).also { it.load() }
        assertFalse(controller.isEnabled.value)
        assertNull(controller.code())
    }

    @Test
    fun aStoredCodeTurnsAiOnAtStartup() {
        val controller = AIAccessController(MemoryStore("owner-code".toByteArray())).also { it.load() }
        assertTrue(controller.isEnabled.value)
        assertEquals("owner-code", controller.code())
    }

    @Test
    fun settingACodeTrimsItAndTurnsAiOn() {
        val store = MemoryStore()
        val controller = AIAccessController(store).also { it.load() }
        assertTrue(controller.set("  owner-code \n"))
        assertTrue(controller.isEnabled.value)
        assertEquals("owner-code", controller.code())
        assertEquals("owner-code", store.bytes?.toString(Charsets.UTF_8))
    }

    @Test
    fun aBlankCodeTurnsAiOffAndForgetsTheCode() {
        val store = MemoryStore("owner-code".toByteArray())
        val controller = AIAccessController(store).also { it.load() }
        assertTrue(controller.set("   "))
        assertFalse(controller.isEnabled.value)
        assertNull(controller.code())
        assertNull(store.bytes)
    }

    @Test
    fun aCodeThatCannotBeStoredChangesNothing() {
        val controller = AIAccessController(MemoryStore(canWrite = false)).also { it.load() }
        assertFalse(controller.set("owner-code"))
        assertFalse(controller.isEnabled.value)
        assertNull(controller.code())
    }

    @Test
    fun clearingRemovesTheCode() {
        val store = MemoryStore("owner-code".toByteArray())
        val controller = AIAccessController(store).also { it.load() }
        controller.clear()
        assertFalse(controller.isEnabled.value)
        assertNull(controller.code())
        assertNull(store.bytes)
    }
}
