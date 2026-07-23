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
        sessionMode: SessionMode = SessionMode.CALIBRATION,
        calibrationOnly: Boolean = sessionMode.calibrationOnly,
        rehearsalOnly: Boolean = sessionMode.rehearsalOnly,
        collectionDayId: String = if (calibrationOnly) "calibration_day" else "day_unassigned",
        namedTestZone: String = "zone_calibration",
        locationCategory: String = "home_or_private_indoor",
        indoorOutdoor: String = "indoor",
        stationaryOrMoving: String = "stationary",
        networkCondition: String = "wifi_normal",
        detectedNetworkTransport: String = "unavailable",
        declaredNetworkCondition: String = networkCondition,
        assignmentId: String? = null,
        assignmentHash: String? = null,
        matrixCellId: String? = null,
        protocolVersion: String? = null,
        environmentalNotes: String = "",
        transportCompatible: Boolean = true,
        protocolDeviation: String? = null,
    ) {
        consent.ensureActive()
        session = SessionState(
            runId = runId,
            siteId = siteId,
            profile = profile,
            startedAtEpochMs = System.currentTimeMillis(),
            plannedDurationSeconds = plannedDurationSeconds,
            sessionMode = sessionMode,
            calibrationOnly = calibrationOnly,
            rehearsalOnly = rehearsalOnly,
            collectionDayId = collectionDayId,
            namedTestZone = namedTestZone,
            locationCategory = locationCategory,
            indoorOutdoor = indoorOutdoor,
            stationaryOrMoving = stationaryOrMoving,
            networkCondition = networkCondition,
            detectedNetworkTransport = detectedNetworkTransport,
            declaredNetworkCondition = declaredNetworkCondition,
            assignmentId = assignmentId,
            assignmentHash = assignmentHash,
            matrixCellId = matrixCellId,
            protocolVersion = protocolVersion,
            environmentalNotes = environmentalNotes,
            transportCompatible = transportCompatible,
            protocolDeviation = protocolDeviation,
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
