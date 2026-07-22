package org.gunnchos.edgeio

/**
 * Session controller that refuses collection before consent and after withdrawal.
 * Metric collection intentionally excludes GPS/email/phone/IMEI/MAC/advertising IDs.
 */
class MeasurementSessionController(
    private val consent: ConsentManager,
) {
    var session: SessionState? = null
        private set

    fun start(runId: String, siteId: String, profile: String) {
        consent.ensureActive()
        session = SessionState(
            runId = runId,
            siteId = siteId,
            profile = profile,
            startedAtEpochMs = System.currentTimeMillis(),
        )
    }

    fun stop() {
        // Export is performed by the host/exporter; samples remain in memory until delete.
    }

    fun delete() {
        session = null
    }
}
