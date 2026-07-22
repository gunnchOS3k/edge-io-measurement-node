package org.gunnchos.edgeio

object SessionExporter {
    fun toJson(
        session: SessionState,
        consent: ConsentManager,
        physical: Boolean,
        zone: String,
        networkCondition: String,
    ): String {
        val evidence = if (physical) "controlled_device_measurement" else "synthetic"
        val mode = if (physical) "PHYSICAL DEVICE COLLECTION" else "SYNTHETIC TEST MODE"
        // Minimal export envelope; host-side schema validation required before Gate 3 assembly.
        return """
        {
          "collection_mode_label": "$mode",
          "session_context": {
            "schema_name": "gunnchos.measurement_session_context",
            "schema_version": "1.0.0",
            "session_id": "android_${session.runId}",
            "run_id": "${session.runId}",
            "collection_day_id": "day_unassigned",
            "location_category": "other_approved_test_zone",
            "named_test_zone": "$zone",
            "indoor_outdoor": "indoor",
            "stationary_or_moving": "stationary",
            "network_condition": "$networkCondition",
            "network_type": "wifi",
            "workload_profile": "${session.profile}",
            "planned_duration_seconds": 300,
            "actual_duration_seconds": 0,
            "start_timestamp": "1970-01-01T00:00:00Z",
            "end_timestamp": "1970-01-01T00:00:00Z",
            "device_category": "phone",
            "collector_version": "0.3.0-gate3-android",
            "consent_receipt_id": "${consent.state.receiptId}",
            "environmental_notes": "",
            "degradation_method": "none",
            "operator_notes": "",
            "protocol_deviation": null,
            "evidence_level": "$evidence"
          },
          "note": "Host must complete measurement_batch via validated collector export path before Gate 3 assembly."
        }
        """.trimIndent()
    }
}
