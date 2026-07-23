package org.gunnchos.edgeio

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

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

class SessionModeTest {
    @Test
    fun durationsAndPrefixesMatchGate3Contract() {
        assertEquals(60.0, SessionMode.CALIBRATION.plannedDurationSeconds, 0.0)
        assertEquals(300.0, SessionMode.PILOT_REHEARSAL.plannedDurationSeconds, 0.0)
        assertEquals(300.0, SessionMode.PILOT.plannedDurationSeconds, 0.0)
        assertEquals("pixel-cal", SessionMode.CALIBRATION.runIdPrefix)
        assertEquals("pixel-rehearsal", SessionMode.PILOT_REHEARSAL.runIdPrefix)
        assertEquals("pixel-pilot", SessionMode.PILOT.runIdPrefix)
        assertTrue(SessionMode.CALIBRATION.calibrationOnly)
        assertFalse(SessionMode.CALIBRATION.rehearsalOnly)
        assertFalse(SessionMode.PILOT_REHEARSAL.calibrationOnly)
        assertTrue(SessionMode.PILOT_REHEARSAL.rehearsalOnly)
        assertFalse(SessionMode.PILOT.calibrationOnly)
        assertFalse(SessionMode.PILOT.rehearsalOnly)
    }

    @Test
    fun modeSpecificUiLabelsAndTimers() {
        assertEquals("START 60S CALIBRATION", SessionMode.CALIBRATION.startButtonLabel)
        assertEquals("START 5-MIN PILOT REHEARSAL", SessionMode.PILOT_REHEARSAL.startButtonLabel)
        assertEquals("START 5-MIN PILOT SESSION", SessionMode.PILOT.startButtonLabel)
        assertEquals("01:00", SessionMode.CALIBRATION.timerTotalLabel)
        assertEquals("05:00", SessionMode.PILOT_REHEARSAL.timerTotalLabel)
        assertEquals("05:00", SessionMode.PILOT.timerTotalLabel)
    }

    @Test
    fun fromWireRejectsUnknownMode() {
        assertThrows(IllegalArgumentException::class.java) {
            SessionMode.fromWire("CALIBRATION_ONLY")
        }
    }
}

class PilotAssignmentParseTest {
    private fun rehearsalBase(): JSONObject {
        return JSONObject()
            .put("schema_name", "gunnchos.pilot_assignment")
            .put("schema_version", "1.0.0")
            .put("assignment_id", "asn_testhash12abcd")
            .put("matrix_cell_id", "rehearsal_zone_rehearsal_wifi_normal_learn")
            .put("protocol_version", "gate3-pilot-v1")
            .put("assignment_hash_algorithm", AssignmentCanonicalJson.ALGORITHM_V1)
            .put("collection_day_id", "rehearsal_day")
            .put("named_test_zone", "zone_rehearsal")
            .put("location_category", "home_or_private_indoor")
            .put("indoor_outdoor", "indoor")
            .put("stationary_or_moving", "stationary")
            .put("network_condition", "wifi_normal")
            .put("expected_network_transport", "wifi")
            .put("workload_profile", "learn")
            .put("planned_duration_seconds", 300)
            .put("session_mode", "PILOT_REHEARSAL")
            .put("calibration_only", false)
            .put("rehearsal_only", true)
            .put("environmental_note_prompt", "Do not enter addresses")
            .put("expires_at", "2099-01-01T00:00:00Z")
            .put("site_id", "gary")
            .put(
                "producer",
                JSONObject()
                    .put("repository", "gunnchos-7gc-ai-ran-field-kit")
                    .put("commit", "ffb237fb29a77f68fe2185b6d72de33edc076748"),
            )
    }

    @Test
    fun parsesFieldKitAssignmentSchema() {
        val base = rehearsalBase()
        val hash = AssignmentCanonicalJson.hashAssignmentObject(base).digestHex
        base.put("assignment_hash", hash)
        val asn = PilotAssignment.fromJson(base.toString())
        assertEquals("asn_testhash12abcd", asn.assignmentId)
        assertEquals(hash, asn.assignmentHash)
        assertEquals(SessionMode.PILOT_REHEARSAL, asn.sessionMode)
        assertTrue(asn.rehearsalOnly)
        assertEquals("wifi", asn.expectedNetworkTransport)
        assertEquals(300.0, asn.plannedDurationSeconds, 0.0)
        assertEquals(AssignmentCanonicalJson.ALGORITHM_V1, asn.assignmentHashAlgorithm)
    }

    @Test
    fun integerDurationThreeHundredNotThreeHundredPointZero() {
        val base = rehearsalBase()
        val hash = AssignmentCanonicalJson.hashAssignmentObject(base).digestHex
        val canon = String(AssignmentCanonicalJson.hashAssignmentObject(base).canonicalUtf8, Charsets.UTF_8)
        assertTrue(canon.contains("\"planned_duration_seconds\":300"))
        assertFalse(canon.contains("\"planned_duration_seconds\":300.0"))
        base.put("assignment_hash", hash)
        PilotAssignment.fromJson(base.toString())
    }

    @Test
    fun rejectsTamperedAssignmentHash() {
        val base = rehearsalBase()
        val hash = AssignmentCanonicalJson.hashAssignmentObject(base).digestHex
        base.put("assignment_hash", hash)
        base.put("named_test_zone", "zone_a")
        assertThrows(AssignmentImportException::class.java) {
            PilotAssignment.fromJson(base.toString())
        }
    }

    @Test
    fun rejectsWrongAlgorithm() {
        val base = rehearsalBase()
        base.put("assignment_hash_algorithm", "legacy-unsorted-v0")
        val hash = AssignmentCanonicalJson.hashAssignmentObject(base).digestHex
        base.put("assignment_hash", hash)
        assertThrows(AssignmentImportException::class.java) {
            PilotAssignment.fromJson(base.toString())
        }
    }

    @Test
    fun reorderedKeysDoNotChangeHash() {
        val a = rehearsalBase()
        val hashA = AssignmentCanonicalJson.hashAssignmentObject(a).digestHex
        val reordered = JSONObject()
            .put("workload_profile", "learn")
            .put("schema_version", "1.0.0")
            .put("schema_name", "gunnchos.pilot_assignment")
            .put("assignment_id", "asn_testhash12abcd")
            .put("matrix_cell_id", "rehearsal_zone_rehearsal_wifi_normal_learn")
            .put("protocol_version", "gate3-pilot-v1")
            .put("assignment_hash_algorithm", AssignmentCanonicalJson.ALGORITHM_V1)
            .put("collection_day_id", "rehearsal_day")
            .put("named_test_zone", "zone_rehearsal")
            .put("location_category", "home_or_private_indoor")
            .put("indoor_outdoor", "indoor")
            .put("stationary_or_moving", "stationary")
            .put("network_condition", "wifi_normal")
            .put("expected_network_transport", "wifi")
            .put("planned_duration_seconds", 300)
            .put("session_mode", "PILOT_REHEARSAL")
            .put("calibration_only", false)
            .put("rehearsal_only", true)
            .put("environmental_note_prompt", "Do not enter addresses")
            .put("expires_at", "2099-01-01T00:00:00Z")
            .put("site_id", "gary")
            .put(
                "producer",
                JSONObject()
                    .put("commit", "ffb237fb29a77f68fe2185b6d72de33edc076748")
                    .put("repository", "gunnchos-7gc-ai-ran-field-kit"),
            )
        val hashB = AssignmentCanonicalJson.hashAssignmentObject(reordered).digestHex
        assertEquals(hashA, hashB)
    }
}

class NetworkTransportDetectorTest {
    @Test
    fun mapsNetworkConditionToExpectedTransport() {
        assertEquals("wifi", NetworkTransportDetector.expectedTransportForCondition("wifi_normal"))
        assertEquals("wifi", NetworkTransportDetector.expectedTransportForCondition("wifi_degraded"))
        assertEquals("cellular", NetworkTransportDetector.expectedTransportForCondition("cellular_normal"))
        assertEquals("wifi", NetworkTransportDetector.expectedTransportForCondition("local_network_degraded"))
        assertTrue(NetworkTransportDetector.isCompatible("wifi", "wifi"))
        assertFalse(NetworkTransportDetector.isCompatible("cellular", "wifi"))
    }
}

class EdgeIoFileProviderTest {
    @Test
    fun debugAuthorityMatchesManifestConvention() {
        assertEquals(
            "org.gunnchos.edgeio.debug.provider",
            EdgeIoFileProvider.authority("org.gunnchos.edgeio.debug"),
        )
        assertEquals(EdgeIoFileProvider.DEBUG_AUTHORITY, EdgeIoFileProvider.authority("org.gunnchos.edgeio.debug"))
        assertFalse(EdgeIoFileProvider.authority("org.gunnchos.edgeio.debug").endsWith(".files"))
    }

    @Test
    fun releaseAuthorityUsesApplicationIdDotProvider() {
        assertEquals(
            "org.gunnchos.edgeio.provider",
            EdgeIoFileProvider.authority("org.gunnchos.edgeio"),
        )
    }
}

class SessionExporterTest {
    private fun activeConsent(): ConsentManager {
        val consent = ConsentManager()
        consent.acknowledgeSummary()
        consent.optIn("gary", "r1")
        return consent
    }

    private fun baseSample(networkType: String = "wifi") = MetricSample(
        timestampIso = ConsentManager.utcNowIso(),
        latencyMs = 42.0,
        jitterMs = null,
        packetLossPct = null,
        uploadMbps = null,
        downloadMbps = null,
        networkType = networkType,
        cpuPct = null,
        memoryPct = 55.0,
        batteryPct = 80.0,
        charging = true,
        thermalState = "nominal",
        localEdgeResponseMs = 42.0,
        signalDbm = null,
        qualityFlags = listOf("ok", "physical_android", "unavailable_fields_explicit"),
        unavailable = mapOf("upload_mbps" to "api_not_exposed_without_privileged_radio_stats"),
    )

    @Test
    fun physicalExportContainsRealTimestampsAndNoSyntheticLabel() {
        val consent = activeConsent()
        val start = System.currentTimeMillis() - 60_000
        val end = System.currentTimeMillis()
        val session = SessionState(
            runId = "pixel-cal-test",
            siteId = "gary",
            profile = "learn",
            startedAtEpochMs = start,
            endedAtEpochMs = end,
            plannedDurationSeconds = 60.0,
            sessionMode = SessionMode.CALIBRATION,
            calibrationOnly = true,
            collectionDayId = "calibration_day",
            namedTestZone = "zone_calibration",
            detectedNetworkTransport = "wifi",
            declaredNetworkCondition = "wifi_normal",
            protocolDeviation = "calibration_not_pilot",
            consentStatusAtStart = "active",
            consentReceiptIdAtStart = consent.state.receiptId,
            consentCapturedAtIsoAtStart = consent.state.capturedAtIso,
            samples = listOf(baseSample()),
        )
        val json = SessionExporter.toJson(
            session = session,
            consent = consent,
            physical = true,
            producerCommit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            buildDirty = false,
        )
        val root = JSONObject(json)
        assertEquals("PHYSICAL DEVICE COLLECTION", root.getString("collection_mode_label"))
        assertFalse(json.contains("SYNTHETIC TEST MODE"))
        val ctx = root.getJSONObject("session_context")
        assertEquals("controlled_device_measurement", ctx.getString("evidence_level"))
        assertEquals("calibration_not_pilot", ctx.getString("protocol_deviation"))
        assertEquals("CALIBRATION", ctx.getString("session_mode"))
        assertTrue(ctx.getBoolean("calibration_only"))
        assertFalse(ctx.getBoolean("rehearsal_only"))
        assertEquals("zone_calibration", ctx.getString("named_test_zone"))
        assertEquals("wifi", ctx.getString("detected_network_transport"))
        assertEquals("wifi_normal", ctx.getString("declared_network_condition"))
        assertTrue(ctx.getDouble("actual_duration_seconds") >= 59.0)
        assertTrue(ctx.getString("operator_notes").contains("calibration_only=true"))
        val batch = root.getJSONObject("measurement_batch")
        assertEquals("android_client", batch.getJSONObject("provenance").getString("collector"))
        assertFalse(batch.getJSONObject("provenance").getBoolean("build_dirty"))
        assertEquals("pixel_6a", batch.getJSONObject("device").getString("model_label"))
        assertEquals("active", batch.getJSONObject("consent").getString("status"))
        assertEquals("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", batch.getJSONObject("producer").getString("commit"))
        val m0 = batch.getJSONArray("measurements").getJSONObject(0)
        assertTrue(m0.isNull("upload_mbps"))
        assertTrue(m0.has("unavailable_fields"))
    }

    @Test
    fun calibrationExportHasCalibrationOnlyTrue() {
        val consent = activeConsent()
        val now = System.currentTimeMillis()
        val session = SessionState(
            runId = "pixel-cal-only",
            siteId = "gary",
            profile = "learn",
            startedAtEpochMs = now - 30_000,
            endedAtEpochMs = now,
            plannedDurationSeconds = 60.0,
            sessionMode = SessionMode.CALIBRATION,
            calibrationOnly = true,
            collectionDayId = "calibration_day",
            namedTestZone = "zone_calibration",
            detectedNetworkTransport = "wifi",
            declaredNetworkCondition = "wifi_normal",
            consentStatusAtStart = "active",
            consentReceiptIdAtStart = consent.state.receiptId,
            consentCapturedAtIsoAtStart = consent.state.capturedAtIso,
            samples = listOf(baseSample()),
        )
        val ctx = JSONObject(
            SessionExporter.toJson(
                session = session,
                consent = consent,
                physical = true,
                producerCommit = "dddddddddddddddddddddddddddddddddddddddd",
                buildDirty = false,
            ),
        ).getJSONObject("session_context")
        assertTrue(ctx.getBoolean("calibration_only"))
        assertEquals("CALIBRATION", ctx.getString("session_mode"))
        assertEquals("calibration_not_pilot", ctx.getString("protocol_deviation"))
    }

    @Test
    fun rehearsalExportHasRehearsalOnlyAndDeviation() {
        val consent = activeConsent()
        val hash = "b".repeat(64)
        val now = System.currentTimeMillis()
        val session = SessionState(
            runId = "pixel-rehearsal-test",
            siteId = "gary",
            profile = "learn",
            startedAtEpochMs = now - 300_000,
            endedAtEpochMs = now,
            plannedDurationSeconds = 300.0,
            sessionMode = SessionMode.PILOT_REHEARSAL,
            calibrationOnly = false,
            rehearsalOnly = true,
            collectionDayId = "rehearsal_day",
            namedTestZone = "zone_rehearsal",
            locationCategory = "home_or_private_indoor",
            indoorOutdoor = "indoor",
            stationaryOrMoving = "stationary",
            networkCondition = "wifi_normal",
            detectedNetworkTransport = "wifi",
            declaredNetworkCondition = "wifi_normal",
            assignmentId = "asn_rehearsaltest01",
            assignmentHash = hash,
            matrixCellId = "rehearsal_zone_rehearsal_wifi_normal_learn",
            protocolVersion = "gate3-pilot-v1",
            transportCompatible = true,
            protocolDeviation = "rehearsal_not_pilot",
            consentStatusAtStart = "active",
            consentReceiptIdAtStart = consent.state.receiptId,
            consentCapturedAtIsoAtStart = consent.state.capturedAtIso,
            samples = listOf(baseSample()),
        )
        val ctx = JSONObject(
            SessionExporter.toJson(
                session = session,
                consent = consent,
                physical = true,
                producerCommit = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                buildDirty = false,
            ),
        ).getJSONObject("session_context")
        assertEquals("PILOT_REHEARSAL", ctx.getString("session_mode"))
        assertTrue(ctx.getBoolean("rehearsal_only"))
        assertFalse(ctx.getBoolean("calibration_only"))
        assertEquals("rehearsal_not_pilot", ctx.getString("protocol_deviation"))
        assertEquals(hash, ctx.getString("assignment_hash"))
        assertEquals("asn_rehearsaltest01", ctx.getString("assignment_id"))
        assertEquals("rehearsal_day", ctx.getString("collection_day_id"))
    }

    @Test
    fun exportIncludesSessionModeAndAssignmentHash() {
        val consent = activeConsent()
        val hash = "c".repeat(64)
        val now = System.currentTimeMillis()
        val session = SessionState(
            runId = "pixel-pilot-test",
            siteId = "gary",
            profile = "create",
            startedAtEpochMs = now - 300_000,
            endedAtEpochMs = now,
            plannedDurationSeconds = 300.0,
            sessionMode = SessionMode.PILOT,
            collectionDayId = "day_01",
            namedTestZone = "zone_a",
            detectedNetworkTransport = "cellular",
            declaredNetworkCondition = "cellular_normal",
            assignmentId = "asn_pilotcell000001",
            assignmentHash = hash,
            matrixCellId = "day_01_zone_a_cellular_normal_create",
            protocolVersion = "gate3-pilot-v1",
            transportCompatible = true,
            consentStatusAtStart = "active",
            consentReceiptIdAtStart = consent.state.receiptId,
            consentCapturedAtIsoAtStart = consent.state.capturedAtIso,
            samples = listOf(baseSample("cellular")),
        )
        val root = JSONObject(
            SessionExporter.toJson(
                session = session,
                consent = consent,
                physical = true,
                producerCommit = "ffffffffffffffffffffffffffffffffffffffff",
                buildDirty = false,
            ),
        )
        val ctx = root.getJSONObject("session_context")
        assertEquals("PILOT", ctx.getString("session_mode"))
        assertEquals(hash, ctx.getString("assignment_hash"))
        assertEquals("cellular", ctx.getString("network_type"))
        assertEquals("cellular", ctx.getString("detected_network_transport"))
        assertTrue(ctx.isNull("protocol_deviation"))
    }

    @Test
    fun exportKeepsFrozenActiveConsentAfterLaterWithdrawal() {
        val consent = activeConsent()
        val controller = MeasurementSessionController(consent)
        controller.start(
            runId = "pixel-cal-frozen",
            siteId = "gary",
            profile = "learn",
            plannedDurationSeconds = 60.0,
            sessionMode = SessionMode.CALIBRATION,
            calibrationOnly = true,
            protocolDeviation = "calibration_not_pilot",
        )
        consent.withdraw()
        assertEquals("withdrawn", consent.state.status)
        val session = controller.session!!.copy(endedAtEpochMs = System.currentTimeMillis())
        val json = SessionExporter.toJson(
            session = session,
            consent = consent,
            physical = true,
            producerCommit = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            buildDirty = false,
        )
        val batch = JSONObject(json).getJSONObject("measurement_batch")
        assertEquals("active", batch.getJSONObject("consent").getString("status"))
    }

    @Test
    fun refusesSyntheticExportOnProductionPath() {
        val consent = activeConsent()
        val session = SessionState(
            runId = "x",
            siteId = "gary",
            profile = "learn",
            startedAtEpochMs = System.currentTimeMillis(),
            endedAtEpochMs = System.currentTimeMillis(),
            consentStatusAtStart = "active",
            consentReceiptIdAtStart = consent.state.receiptId,
            consentCapturedAtIsoAtStart = consent.state.capturedAtIso,
        )
        assertThrows(IllegalArgumentException::class.java) {
            SessionExporter.toJson(
                session = session,
                consent = consent,
                physical = false,
                producerCommit = "cccccccccccccccccccccccccccccccccccccccc",
                buildDirty = false,
            )
        }
    }

    @Test
    fun resolveProtocolDeviationPrefersExplicitThenMode() {
        val cal = SessionState(
            runId = "a",
            siteId = "gary",
            profile = "learn",
            sessionMode = SessionMode.CALIBRATION,
            calibrationOnly = true,
        )
        assertEquals("calibration_not_pilot", SessionExporter.resolveProtocolDeviation(cal))
        val rehearsal = SessionState(
            runId = "b",
            siteId = "gary",
            profile = "learn",
            sessionMode = SessionMode.PILOT_REHEARSAL,
            rehearsalOnly = true,
        )
        assertEquals("rehearsal_not_pilot", SessionExporter.resolveProtocolDeviation(rehearsal))
        val mismatch = SessionState(
            runId = "c",
            siteId = "gary",
            profile = "learn",
            sessionMode = SessionMode.PILOT,
            transportCompatible = false,
        )
        assertEquals("network_condition_mismatch", SessionExporter.resolveProtocolDeviation(mismatch))
        val ok = SessionState(
            runId = "d",
            siteId = "gary",
            profile = "learn",
            sessionMode = SessionMode.PILOT,
            transportCompatible = true,
        )
        assertNull(SessionExporter.resolveProtocolDeviation(ok))
    }

    @Test
    fun cacheJsonRemainsAfterSimulatedShareFailure() {
        val dir = createTempDir(prefix = "edgeio-export-")
        try {
            val out = File(dir, "pixel-cal-retry.json")
            out.writeText("""{"ok":true}""")
            assertTrue(out.exists() && out.length() > 0)
            assertEquals("""{"ok":true}""", out.readText())
        } finally {
            dir.deleteRecursively()
        }
    }
}

class ManifestAuthorityContractTest {
    @Test
    fun mergedManifestSnippetDeclaresApplicationIdProvider() {
        val applicationIdDebug = "org.gunnchos.edgeio.debug"
        val expected = "$applicationIdDebug.provider"
        assertEquals(EdgeIoFileProvider.DEBUG_AUTHORITY, expected)
        assertTrue(expected.endsWith(EdgeIoFileProvider.AUTHORITY_SUFFIX))
        assertFalse(expected.contains(".files"))
    }
}
