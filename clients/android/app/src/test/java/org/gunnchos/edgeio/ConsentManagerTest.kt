package org.gunnchos.edgeio

import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test

class ConsentManagerTest {
    @Test
    fun blocksCollectionWithoutOptIn() {
        val c = ConsentManager()
        assertThrows(IllegalStateException::class.java) { c.ensureActive() }
    }

    @Test
    fun optInRequiresSummary() {
        val c = ConsentManager()
        assertThrows(IllegalStateException::class.java) { c.optIn("gary", "r1") }
        c.acknowledgeSummary()
        val state = c.optIn("gary", "r1")
        assertEquals("active", state.status)
    }
}
