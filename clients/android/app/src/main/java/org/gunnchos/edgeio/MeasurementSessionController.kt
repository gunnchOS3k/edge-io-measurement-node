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

    fun start(
        runId: String,
        siteId: String,
        profile: String,
        plannedDurationSeconds: Double = 60.0,
        calibrationOnly: Boolean = false,
    ) {
        consent.ensureActive()
        session = SessionState(
            runId = runId,
            siteId = siteId,
            profile = profile,
            startedAtEpochMs = System.currentTimeMillis(),
            plannedDurationSeconds = plannedDurationSeconds,
            calibrationOnly = calibrationOnly,
            samples = emptyList(),
            consentStatusAtStart = consent.state.status,
            consentReceiptIdAtStart = consent.state.receiptId,
            consentCapturedAtIsoAtStart = consent.state.capturedAtIso,
        )
    }

    fun addSample(sample: MetricSample) {
        val current = session ?: return
        consent.ensureActive()
        session = current.copy(samples = current.samples + sample)
    }

    fun stop() {
        val current = session ?: return
        session = current.copy(endedAtEpochMs = System.currentTimeMillis())
    }

    fun delete() {
        session = null
    }

    fun elapsedSeconds(): Double {
        val current = session ?: return 0.0
        val start = current.startedAtEpochMs ?: return 0.0
        val end = current.endedAtEpochMs ?: System.currentTimeMillis()
        return ((end - start).coerceAtLeast(0)).toDouble() / 1000.0
    }
}
