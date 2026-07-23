package org.gunnchos.edgeio

import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

object SessionExporter {
    private fun isoFromEpoch(ms: Long): String {
        val fmt = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
        fmt.timeZone = TimeZone.getTimeZone("UTC")
        return fmt.format(Date(ms))
    }

    fun resolveProtocolDeviation(session: SessionState): String? {
        if (session.protocolDeviation != null) return session.protocolDeviation
        return when {
            session.sessionMode == SessionMode.CALIBRATION || session.calibrationOnly ->
                "calibration_not_pilot"
            session.sessionMode == SessionMode.PILOT_REHEARSAL || session.rehearsalOnly ->
                "rehearsal_not_pilot"
            !session.transportCompatible ->
                "network_condition_mismatch"
            else -> null
        }
    }

    fun toJson(
        session: SessionState,
        consent: ConsentManager,
        physical: Boolean,
        zone: String = session.namedTestZone,
        networkCondition: String = session.networkCondition,
        locationCategory: String = session.locationCategory,
        deviceCategory: String = "phone",
        modelLabel: String = "pixel_6a",
        networkType: String = session.detectedNetworkTransport,
        producerCommit: String = BuildConfig.GIT_COMMIT,
        buildDirty: Boolean = BuildConfig.GIT_DIRTY.equals("true", ignoreCase = true),
    ): String {
        require(physical) { "Production export path refuses synthetic collector substitution" }
        val evidence = "controlled_device_measurement"
        val mode = "PHYSICAL DEVICE COLLECTION"
        val startMs = session.startedAtEpochMs ?: error("session missing start")
        val endMs = session.endedAtEpochMs ?: System.currentTimeMillis()
        val actualDuration = ((endMs - startMs).coerceAtLeast(0)).toDouble() / 1000.0
        // Prefer consent frozen at collection start so a later withdrawal does not rewrite evidence.
        val consentAt = session.consentCapturedAtIsoAtStart
            ?: consent.state.capturedAtIso
            ?: error("consent timestamp required")
        val receipt = session.consentReceiptIdAtStart
            ?: consent.state.receiptId
            ?: error("consent receipt required")
        val consentStatus = session.consentStatusAtStart
            ?: consent.state.status
        val protocolDeviation = resolveProtocolDeviation(session)
        val detectedTransport = session.detectedNetworkTransport.ifBlank { networkType }
        val declaredCondition = session.declaredNetworkCondition.ifBlank { networkCondition }

        val measurements = JSONArray()
        for (s in session.samples) {
            val m = JSONObject()
            m.put("timestamp", s.timestampIso)
            putNullable(m, "latency_ms", s.latencyMs)
            putNullable(m, "jitter_ms", s.jitterMs)
            putNullable(m, "packet_loss_pct", s.packetLossPct)
            putNullable(m, "upload_mbps", s.uploadMbps)
            putNullable(m, "download_mbps", s.downloadMbps)
            m.put("network_type", s.networkType)
            putNullable(m, "cpu_pct", s.cpuPct)
            putNullable(m, "memory_pct", s.memoryPct)
            putNullable(m, "battery_pct", s.batteryPct)
            if (s.charging != null) m.put("charging", s.charging) else m.put("charging", JSONObject.NULL)
            m.put("thermal_state", s.thermalState)
            m.put("workload_profile", session.profile)
            m.put("service_profile", "${session.profile}_continuity")
            putNullable(m, "local_edge_response_ms", s.localEdgeResponseMs)
            putNullable(m, "signal_dbm", s.signalDbm)
            m.put("quality_flags", JSONArray(s.qualityFlags))
            if (s.unavailable.isNotEmpty()) {
                m.put("unavailable_fields", JSONObject(s.unavailable as Map<*, *>))
            }
            measurements.put(m)
        }

        val batch = JSONObject()
        batch.put("schema_name", "gunnchos.edge_measurement_batch")
        batch.put("schema_version", "1.0.0")
        batch.put("run_id", session.runId)
        batch.put("site_id", session.siteId)
        batch.put(
            "producer",
            JSONObject()
                .put("repository", "edge-io-measurement-node")
                .put("commit", producerCommit)
                .put("client_version", BuildConfig.VERSION_NAME),
        )
        batch.put(
            "consent",
            JSONObject()
                .put("status", consentStatus)
                .put("receipt_id", receipt)
                .put("withdrawal_supported", true)
                .put("captured_at", consentAt),
        )
        batch.put(
            "privacy",
            JSONObject()
                .put("location_precision", "named_test_zone")
                .put("contains_direct_identifiers", false)
                .put("retention_days", 30),
        )
        batch.put(
            "device",
            JSONObject()
                .put("device_class", deviceCategory)
                .put("os_family", "android")
                .put("model_label", modelLabel)
                .put("network_interfaces", JSONArray().put(detectedTransport)),
        )
        batch.put(
            "workload",
            JSONObject()
                .put("profile", session.profile)
                .put("service_profile", "${session.profile}_continuity")
                .put("duration_s", actualDuration),
        )
        batch.put("measurements", measurements)
        batch.put(
            "provenance",
            JSONObject()
                .put("collector", "android_client")
                .put("generated_at", isoFromEpoch(endMs))
                .put("source", "PhysicalMetricsSampler")
                .put("build_dirty", buildDirty)
                .put(
                    "notes",
                    "Physical Android collection; unavailable radio throughput fields are explicit, not zero-filled",
                ),
        )
        batch.put("evidence_level", evidence)

        val operatorNotes = buildString {
            append("model_label=$modelLabel")
            if (session.calibrationOnly) append("; calibration_only=true; not counted toward 54-session pilot")
            if (session.rehearsalOnly) append("; rehearsal_only=true; not counted toward 54-session pilot")
        }
        val context = JSONObject()
        context.put("schema_name", "gunnchos.measurement_session_context")
        context.put("schema_version", "1.0.0")
        context.put("session_id", "android_${session.runId}")
        context.put("run_id", session.runId)
        context.put("collection_day_id", session.collectionDayId)
        context.put("location_category", locationCategory.ifBlank { session.locationCategory })
        context.put("named_test_zone", zone.ifBlank { session.namedTestZone })
        context.put("indoor_outdoor", session.indoorOutdoor)
        context.put("stationary_or_moving", session.stationaryOrMoving)
        context.put("network_condition", declaredCondition)
        context.put("declared_network_condition", declaredCondition)
        context.put("detected_network_transport", detectedTransport)
        context.put("network_type", detectedTransport)
        context.put("session_mode", session.sessionMode.name)
        context.put("calibration_only", session.calibrationOnly)
        context.put("rehearsal_only", session.rehearsalOnly)
        putOptionalString(context, "assignment_id", session.assignmentId)
        putOptionalString(context, "assignment_hash", session.assignmentHash)
        putOptionalString(context, "matrix_cell_id", session.matrixCellId)
        putOptionalString(context, "protocol_version", session.protocolVersion)
        context.put("transport_assignment_compatible", session.transportCompatible)
        context.put("workload_profile", session.profile)
        context.put("planned_duration_seconds", session.plannedDurationSeconds)
        context.put("actual_duration_seconds", actualDuration)
        context.put("start_timestamp", isoFromEpoch(startMs))
        context.put("end_timestamp", isoFromEpoch(endMs))
        context.put("device_category", deviceCategory)
        context.put("collector_version", BuildConfig.VERSION_NAME)
        context.put("consent_receipt_id", receipt)
        context.put("consent_captured_at", consentAt)
        context.put("collection_purpose_version", BuildConfig.ASSIGNMENT_PROTOCOL_VERSION)
        context.put("privacy_policy_version", "gate3-privacy-v1")
        context.put("environmental_notes", session.environmentalNotes.take(280))
        context.put("degradation_method", "none")
        context.put("operator_notes", operatorNotes)
        if (protocolDeviation == null) {
            context.put("protocol_deviation", JSONObject.NULL)
        } else {
            context.put("protocol_deviation", protocolDeviation)
        }
        context.put("evidence_level", evidence)

        val root = JSONObject()
        root.put("collection_mode_label", mode)
        root.put("session_context", context)
        root.put("measurement_batch", batch)
        return root.toString(2)
    }

    private fun putNullable(obj: JSONObject, key: String, value: Double?) {
        if (value == null) obj.put(key, JSONObject.NULL) else obj.put(key, value)
    }

    private fun putOptionalString(obj: JSONObject, key: String, value: String?) {
        if (value.isNullOrBlank()) {
            obj.put(key, JSONObject.NULL)
        } else {
            obj.put(key, value)
        }
    }
}
