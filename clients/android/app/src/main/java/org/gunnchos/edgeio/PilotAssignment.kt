package org.gunnchos.edgeio

import android.util.Log
import org.json.JSONObject

data class AssignmentImportDiagnostics(
    val assignmentId: String?,
    val declaredHash: String?,
    val calculatedHash: String?,
    val canonicalByteCount: Int?,
    val canonicalSha256: String?,
    val algorithm: String?,
    val category: String,
    val reason: String,
)

class AssignmentImportException(
    val diagnostics: AssignmentImportDiagnostics,
    cause: Throwable? = null,
) : IllegalArgumentException(diagnostics.reason, cause)

/**
 * Assignment payload matching field-kit schema gunnchos.pilot_assignment.
 */
data class PilotAssignment(
    val assignmentId: String,
    val matrixCellId: String,
    val assignmentHash: String,
    val assignmentHashAlgorithm: String,
    val protocolVersion: String,
    val collectionDayId: String,
    val namedTestZone: String,
    val locationCategory: String,
    val indoorOutdoor: String,
    val stationaryOrMoving: String,
    val networkCondition: String,
    val expectedNetworkTransport: String,
    val workloadProfile: String,
    val plannedDurationSeconds: Double,
    val sessionMode: SessionMode,
    val calibrationOnly: Boolean,
    val rehearsalOnly: Boolean,
    val environmentalNotePrompt: String,
    val expiresAt: String,
    val siteId: String?,
) {
    companion object {
        const val SCHEMA_NAME = "gunnchos.pilot_assignment"
        const val PROTOCOL_VERSION = "gate3-pilot-v1"
        private const val TAG = "EdgeIoAssignment"

        fun fromJsonObject(obj: JSONObject): PilotAssignment {
            require(obj.optString("schema_name") == SCHEMA_NAME) {
                "Expected schema_name=$SCHEMA_NAME"
            }
            val assignmentId = obj.optString("assignment_id").ifBlank { null }
            val declaredHash = obj.optString("assignment_hash").ifBlank { null }
            val algorithm = obj.optString("assignment_hash_algorithm").ifBlank { null }

            if (algorithm != AssignmentCanonicalJson.ALGORITHM_V1) {
                throw AssignmentImportException(
                    AssignmentImportDiagnostics(
                        assignmentId = assignmentId,
                        declaredHash = declaredHash,
                        calculatedHash = null,
                        canonicalByteCount = null,
                        canonicalSha256 = null,
                        algorithm = algorithm,
                        category = "algorithm",
                        reason = "unknown or missing assignment_hash_algorithm=$algorithm " +
                            "(require ${AssignmentCanonicalJson.ALGORITHM_V1})",
                    ),
                )
            }

            val hashResult = try {
                AssignmentCanonicalJson.hashAssignmentObject(obj)
            } catch (e: Exception) {
                throw AssignmentImportException(
                    AssignmentImportDiagnostics(
                        assignmentId = assignmentId,
                        declaredHash = declaredHash,
                        calculatedHash = null,
                        canonicalByteCount = null,
                        canonicalSha256 = null,
                        algorithm = algorithm,
                        category = "canonicalize",
                        reason = "canonicalization failed: ${e.message}",
                    ),
                    e,
                )
            }

            logDiagnostics(
                AssignmentImportDiagnostics(
                    assignmentId = assignmentId,
                    declaredHash = declaredHash,
                    calculatedHash = hashResult.digestHex,
                    canonicalByteCount = hashResult.canonicalByteCount,
                    canonicalSha256 = hashResult.canonicalSha256,
                    algorithm = algorithm,
                    category = "hash_check",
                    reason = "comparing declared vs calculated",
                ),
            )

            if (declaredHash == null || !declaredHash.matches(Regex("^[0-9a-f]{64}$"))) {
                throw AssignmentImportException(
                    AssignmentImportDiagnostics(
                        assignmentId = assignmentId,
                        declaredHash = declaredHash,
                        calculatedHash = hashResult.digestHex,
                        canonicalByteCount = hashResult.canonicalByteCount,
                        canonicalSha256 = hashResult.canonicalSha256,
                        algorithm = algorithm,
                        category = "hash_format",
                        reason = "assignment_hash must be 64 lowercase hex chars",
                    ),
                )
            }
            if (declaredHash != hashResult.digestHex) {
                val diag = AssignmentImportDiagnostics(
                    assignmentId = assignmentId,
                    declaredHash = declaredHash,
                    calculatedHash = hashResult.digestHex,
                    canonicalByteCount = hashResult.canonicalByteCount,
                    canonicalSha256 = hashResult.canonicalSha256,
                    algorithm = algorithm,
                    category = "hash_mismatch",
                    reason = "assignment_hash mismatch (payload integrity check failed) " +
                        "declared=${declaredHash.take(12)}… calculated=${hashResult.digestHex.take(12)}… " +
                        "canon_bytes=${hashResult.canonicalByteCount}",
                )
                logDiagnostics(diag)
                throw AssignmentImportException(diag)
            }

            val modeWire = obj.getString("session_mode")
            val mode = try {
                SessionMode.fromWire(modeWire)
            } catch (e: Exception) {
                throw AssignmentImportException(
                    AssignmentImportDiagnostics(
                        assignmentId = assignmentId,
                        declaredHash = declaredHash,
                        calculatedHash = hashResult.digestHex,
                        canonicalByteCount = hashResult.canonicalByteCount,
                        canonicalSha256 = hashResult.canonicalSha256,
                        algorithm = algorithm,
                        category = "session_mode",
                        reason = "unknown session_mode=$modeWire",
                    ),
                    e,
                )
            }

            val protocol = obj.getString("protocol_version")
            require(protocol == PROTOCOL_VERSION) {
                "unknown protocol_version=$protocol (expected $PROTOCOL_VERSION)"
            }
            require(assignmentId != null && assignmentId.startsWith("asn_")) {
                "assignment_id must start with asn_"
            }

            val planned = obj.get("planned_duration_seconds")
            val plannedSeconds = when (planned) {
                is Number -> planned.toDouble()
                else -> error("planned_duration_seconds must be a number")
            }
            require(plannedSeconds == kotlin.math.round(plannedSeconds)) {
                "planned_duration_seconds must be an integer number of seconds"
            }

            val calibrationOnly = obj.optBoolean("calibration_only", mode.calibrationOnly)
            val rehearsalOnly = obj.optBoolean("rehearsal_only", mode.rehearsalOnly)
            require(!(mode == SessionMode.PILOT && (calibrationOnly || rehearsalOnly))) {
                "PILOT assignment cannot be calibration_only or rehearsal_only"
            }
            require(!(mode == SessionMode.PILOT_REHEARSAL && !rehearsalOnly)) {
                "PILOT_REHEARSAL requires rehearsal_only=true"
            }
            require(!(mode == SessionMode.PILOT_REHEARSAL && calibrationOnly)) {
                "PILOT_REHEARSAL cannot be calibration_only"
            }
            require(!(mode == SessionMode.CALIBRATION && !calibrationOnly)) {
                "CALIBRATION requires calibration_only=true"
            }

            return PilotAssignment(
                assignmentId = assignmentId,
                matrixCellId = obj.getString("matrix_cell_id"),
                assignmentHash = declaredHash,
                assignmentHashAlgorithm = algorithm,
                protocolVersion = protocol,
                collectionDayId = obj.getString("collection_day_id"),
                namedTestZone = obj.getString("named_test_zone"),
                locationCategory = obj.getString("location_category"),
                indoorOutdoor = obj.getString("indoor_outdoor"),
                stationaryOrMoving = obj.getString("stationary_or_moving"),
                networkCondition = obj.getString("network_condition"),
                expectedNetworkTransport = obj.getString("expected_network_transport"),
                workloadProfile = obj.getString("workload_profile"),
                plannedDurationSeconds = plannedSeconds,
                sessionMode = mode,
                calibrationOnly = calibrationOnly,
                rehearsalOnly = rehearsalOnly,
                environmentalNotePrompt = obj.getString("environmental_note_prompt"),
                expiresAt = obj.getString("expires_at"),
                siteId = if (obj.has("site_id") && !obj.isNull("site_id")) {
                    obj.getString("site_id")
                } else {
                    null
                },
            )
        }

        fun isExpired(assignment: PilotAssignment, nowEpochMs: Long = System.currentTimeMillis()): Boolean {
            return try {
                val instant = java.time.Instant.parse(assignment.expiresAt.trim())
                instant.toEpochMilli() < nowEpochMs
            } catch (_: Exception) {
                false
            }
        }

        fun fromJson(text: String): PilotAssignment = fromJsonObject(JSONObject(text))

        fun computeCanonicalHash(obj: JSONObject): String =
            AssignmentCanonicalJson.hashAssignmentObject(obj).digestHex

        private fun logDiagnostics(diag: AssignmentImportDiagnostics) {
            val message =
                "assignment_import id=${diag.assignmentId} category=${diag.category} " +
                    "algo=${diag.algorithm} declared=${diag.declaredHash} calculated=${diag.calculatedHash} " +
                    "canon_bytes=${diag.canonicalByteCount} canon_sha256=${diag.canonicalSha256} " +
                    "reason=${diag.reason}"
            try {
                Log.i(TAG, message)
            } catch (_: RuntimeException) {
                // JVM unit tests lack android.util.Log native binding.
                System.out.println("$TAG: $message")
            }
        }
    }
}
