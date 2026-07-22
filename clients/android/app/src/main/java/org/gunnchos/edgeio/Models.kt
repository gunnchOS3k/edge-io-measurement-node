package org.gunnchos.edgeio

data class ConsentState(
    val summaryAcknowledged: Boolean = false,
    val status: String = "pending", // pending|active|withdrawn
    val receiptId: String? = null,
    val capturedAtIso: String? = null,
)

data class MetricSample(
    val timestampIso: String,
    val latencyMs: Double?,
    val jitterMs: Double?,
    val packetLossPct: Double?,
    val uploadMbps: Double?,
    val downloadMbps: Double?,
    val networkType: String,
    val cpuPct: Double?,
    val memoryPct: Double?,
    val batteryPct: Double?,
    val charging: Boolean?,
    val thermalState: String,
    val localEdgeResponseMs: Double?,
    val signalDbm: Double?,
    val qualityFlags: List<String>,
    val unavailable: Map<String, String> = emptyMap(),
)

data class SessionState(
    val runId: String,
    val siteId: String,
    val profile: String,
    val startedAtEpochMs: Long? = null,
    val endedAtEpochMs: Long? = null,
    val plannedDurationSeconds: Double = 60.0,
    val samples: List<MetricSample> = emptyList(),
    val calibrationOnly: Boolean = false,
)
