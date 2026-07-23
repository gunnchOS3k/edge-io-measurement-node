package org.gunnchos.edgeio

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.nio.charset.StandardCharsets

class AssignmentCanonicalGoldenTest {
    @Test
    fun fieldKitValidRehearsalGoldenMatchesAndroidHash() {
        val text = javaClass.classLoader!!
            .getResourceAsStream("pilot_assignment/valid_rehearsal.json")!!
            .bufferedReader(StandardCharsets.UTF_8)
            .readText()
        val meta = JSONObject(
            javaClass.classLoader!!
                .getResourceAsStream("pilot_assignment/valid_rehearsal.meta.json")!!
                .bufferedReader(StandardCharsets.UTF_8)
                .readText(),
        )
        val expectedCanon = javaClass.classLoader!!
            .getResourceAsStream("pilot_assignment/valid_rehearsal.canonical.json")!!
            .readBytes()
        val obj = JSONObject(text)
        val result = AssignmentCanonicalJson.hashAssignmentObject(obj)
        assertEquals(meta.getString("expected_hash"), result.digestHex)
        assertEquals(meta.getInt("canonical_byte_count"), result.canonicalByteCount)
        assertTrue(expectedCanon.contentEquals(result.canonicalUtf8))
        val asn = PilotAssignment.fromJson(text)
        assertEquals(meta.getString("assignment_id"), asn.assignmentId)
        assertEquals(SessionMode.PILOT_REHEARSAL, asn.sessionMode)
    }

    @Test
    fun regeneratedV2AssignmentImports() {
        val text = javaClass.classLoader!!
            .getResourceAsStream("pilot_assignment/gate3_rehearsal_assignment_v2.json")!!
            .bufferedReader(StandardCharsets.UTF_8)
            .readText()
        val asn = PilotAssignment.fromJson(text)
        assertEquals(SessionMode.PILOT_REHEARSAL, asn.sessionMode)
        assertTrue(asn.rehearsalOnly)
        assertEquals(300.0, asn.plannedDurationSeconds, 0.0)
        assertEquals(AssignmentCanonicalJson.ALGORITHM_V1, asn.assignmentHashAlgorithm)
    }
}
