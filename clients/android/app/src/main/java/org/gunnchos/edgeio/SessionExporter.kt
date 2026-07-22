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

    fun toJson(
        session: SessionState,
        consent: ConsentManager,
        physical: Boolean,
        zone: String,
        networkCondition: String,
        locationCategory: String = "home_or_private_indoor",
        deviceCategory: String = "phone",
        modelLabel: String = "pixel_6a",
        networkType: String = "wifi",
    ): String {
        require(physical) { "Production export path refuses synthetic collector substitution" }
        val evidence = "controlled_device_measurement"
        val mode = "PHYSICAL DEVICE COLLECTION"
        val startMs = session.startedAtEpochMs ?: error("session missing start")
        val endMs = session.endedAtEpochMs ?: System.currentTimeMillis()
        val actualDuration = ((endMs - startMs).coerceAtLeast(0)).toDouble() / 1000.0
        val consentAt = consent.state.capturedAtIso ?: error("consent timestamp required")
        val receipt = consent.state.receiptId ?: error("consent receipt required")

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
                .put("commit", "unknown_local_build")
                .put("client_version", "0.3.1-gate3-android"),
        )
        batch.put(
            "consent",
            JSONObject()
                .put("status", consent.state.status)
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
                .put("network_interfaces", JSONArray().put(networkType)),
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
                .put(
                    "notes",
                    "Physical Android collection; unavailable radio throughput fields are explicit, not zero-filled",
                ),
        )
        batch.put("evidence_level", evidence)

        val operatorNotes = buildString {
            append("model_label=$modelLabel")
            if (session.calibrationOnly) append("; calibration_only=true; not counted toward 54-session pilot")
        }
        val context = JSONObject()
        context.put("schema_name", "gunnchos.measurement_session_context")
        context.put("schema_version", "1.0.0")
        context.put("session_id", "android_${session.runId}")
        context.put("run_id", session.runId)
        context.put("collection_day_id", if (session.calibrationOnly) "calibration_day" else "day_unassigned")
        context.put("location_category", locationCategory)
        context.put("named_test_zone", zone)
        context.put("indoor_outdoor", "indoor")
        context.put("stationary_or_moving", "stationary")
        context.put("network_condition", networkCondition)
        context.put("network_type", networkType)
        context.put("workload_profile", session.profile)
        context.put("planned_duration_seconds", session.plannedDurationSeconds)
        context.put("actual_duration_seconds", actualDuration)
        context.put("start_timestamp", isoFromEpoch(startMs))
        context.put("end_timestamp", isoFromEpoch(endMs))
        context.put("device_category", deviceCategory)
        context.put("collector_version", "0.3.1-gate3-android")
        context.put("consent_receipt_id", receipt)
        context.put("consent_captured_at", consentAt)
        context.put("collection_purpose_version", "gate3-pilot-v1")
        context.put("privacy_policy_version", "gate3-privacy-v1")
        context.put("environmental_notes", "")
        context.put("degradation_method", "none")
        context.put("operator_notes", operatorNotes)
        context.put(
            "protocol_deviation",
            if (session.calibrationOnly) "calibration_not_pilot" else JSONObject.NULL,
        )
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
}
