package org.gunnchos.edgeio

import java.security.MessageDigest
import java.util.UUID

class ConsentManager {
    var state: ConsentState = ConsentState()
        private set

    fun acknowledgeSummary() {
        state = state.copy(summaryAcknowledged = true)
    }

    fun optIn(siteId: String, runId: String): ConsentState {
        check(state.summaryAcknowledged) { "Acknowledge collection summary before opt-in" }
        val material = "$siteId|$runId|${UUID.randomUUID()}"
        val digest = MessageDigest.getInstance("SHA-256")
            .digest(material.toByteArray())
            .joinToString("") { "%02x".format(it) }
            .take(16)
        state = ConsentState(
            summaryAcknowledged = true,
            status = "active",
            receiptId = "rcpt_$digest",
        )
        return state
    }

    fun withdraw() {
        check(state.status == "active") { "No active consent" }
        state = state.copy(status = "withdrawn")
    }

    fun ensureActive() {
        check(state.status == "active") { "Collection blocked without active consent" }
    }
}
