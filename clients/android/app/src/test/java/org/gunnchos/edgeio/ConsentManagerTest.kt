package org.gunnchos.edgeio

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test

class ConsentManagerTest {
    @Test
    fun blocksCollectionWithoutOptIn() {
        val c = ConsentManager()
        assertThrows(IllegalStateException::class.java) { c.ensureActive() }
    }

    @Test
    fun optInRequiresSummaryAndRecordsTimestamp() {
        val c = ConsentManager()
        assertThrows(IllegalStateException::class.java) { c.optIn("gary", "r1") }
        c.acknowledgeSummary()
        val state = c.optIn("gary", "r1")
        assertEquals("active", state.status)
        assertTrue(state.receiptId!!.startsWith("rcpt_"))
        assertTrue(state.capturedAtIso!!.endsWith("Z"))
    }
}

class SessionExporterTest {
    @Test
    fun physicalExportContainsRealTimestampsAndNoSyntheticLabel() {
        val consent = ConsentManager()
        consent.acknowledgeSummary()
        consent.optIn("gary", "r1")
        val start = System.currentTimeMillis() - 60_000
        val end = System.currentTimeMillis()
        val session = SessionState(
            runId = "pixel-cal-test",
            siteId = "gary",
            profile = "learn",
            startedAtEpochMs = start,
            endedAtEpochMs = end,
            plannedDurationSeconds = 60.0,
            calibrationOnly = true,
            samples = listOf(
                MetricSample(
                    timestampIso = ConsentManager.utcNowIso(),
                    latencyMs = 42.0,
                    jitterMs = null,
                    packetLossPct = null,
                    uploadMbps = null,
                    downloadMbps = null,
                    networkType = "wifi",
                    cpuPct = null,
                    memoryPct = 55.0,
                    batteryPct = 80.0,
                    charging = true,
                    thermalState = "nominal",
                    localEdgeResponseMs = 42.0,
                    signalDbm = null,
                    qualityFlags = listOf("ok", "physical_android", "unavailable_fields_explicit"),
                    unavailable = mapOf("upload_mbps" to "api_not_exposed_without_privileged_radio_stats"),
                ),
            ),
        )
        val json = SessionExporter.toJson(
            session = session,
            consent = consent,
            physical = true,
            zone = "zone_calibration",
            networkCondition = "wifi_normal",
        )
        val root = JSONObject(json)
        assertEquals("PHYSICAL DEVICE COLLECTION", root.getString("collection_mode_label"))
        assertFalse(json.contains("SYNTHETIC TEST MODE"))
        val ctx = root.getJSONObject("session_context")
        assertEquals("controlled_device_measurement", ctx.getString("evidence_level"))
        assertEquals("calibration_not_pilot", ctx.getString("protocol_deviation"))
        assertEquals("zone_calibration", ctx.getString("named_test_zone"))
        assertTrue(ctx.getDouble("actual_duration_seconds") >= 59.0)
        assertTrue(ctx.getString("operator_notes").contains("calibration_only=true"))
        val batch = root.getJSONObject("measurement_batch")
        assertEquals("android_client", batch.getJSONObject("provenance").getString("collector"))
        assertEquals("pixel_6a", batch.getJSONObject("device").getString("model_label"))
        val m0 = batch.getJSONArray("measurements").getJSONObject(0)
        assertTrue(m0.isNull("upload_mbps"))
        assertTrue(m0.has("unavailable_fields"))
    }

    @Test
    fun refusesSyntheticExportOnProductionPath() {
        val consent = ConsentManager()
        consent.acknowledgeSummary()
        consent.optIn("gary", "r1")
        val session = SessionState(
            runId = "x",
            siteId = "gary",
            profile = "learn",
            startedAtEpochMs = System.currentTimeMillis(),
            endedAtEpochMs = System.currentTimeMillis(),
        )
        assertThrows(IllegalArgumentException::class.java) {
            SessionExporter.toJson(
                session = session,
                consent = consent,
                physical = false,
                zone = "zone_calibration",
                networkCondition = "wifi_normal",
            )
        }
    }
}
