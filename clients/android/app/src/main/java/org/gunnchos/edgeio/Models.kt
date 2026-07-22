package org.gunnchos.edgeio

/**
 * Minimal Edge-IO Android client scaffold.
 *
 * Functional requirements covered by this scaffold + companion ViewModel:
 * - plain-language collection summary
 * - affirmative opt-in before collection
 * - non-identifying consent receipt
 * - start/stop, elapsed time, export, delete, withdrawal
 * - no direct identifier collection
 *
 * Full Compose UI wiring is intentional and compact for Gate 2.
 */
data class ConsentState(
    val summaryAcknowledged: Boolean = false,
    val status: String = "pending", // pending|active|withdrawn
    val receiptId: String? = null,
)

data class SessionState(
    val runId: String,
    val siteId: String,
    val profile: String,
    val startedAtEpochMs: Long? = null,
    val samples: List<Map<String, Any>> = emptyList(),
)
