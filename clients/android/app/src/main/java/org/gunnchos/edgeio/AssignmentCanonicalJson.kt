package org.gunnchos.edgeio

import org.json.JSONArray
import org.json.JSONObject
import java.security.MessageDigest
import kotlin.math.abs
import kotlin.math.round

/**
 * Shared with field-kit scripts/assignment_canonical.py
 * Algorithm: gunnchos-canonical-json-sha256-v1
 */
object AssignmentCanonicalJson {
    const val ALGORITHM_V1 = "gunnchos-canonical-json-sha256-v1"

    data class HashResult(
        val digestHex: String,
        val canonicalUtf8: ByteArray,
        val canonicalByteCount: Int,
        val canonicalSha256: String,
    )

    fun hashAssignmentObject(obj: JSONObject): HashResult {
        // Never use JSONObject.toString() as an intermediate crypto form.
        val payload = JSONObject()
        val keys = obj.keys().asSequence().toList()
        for (key in keys) {
            if (key == "assignment_hash") continue
            payload.put(key, obj.get(key))
        }
        val canonical = canonicalize(payload)
        val utf8 = canonical.toByteArray(Charsets.UTF_8)
        val digest = MessageDigest.getInstance("SHA-256").digest(utf8)
        val hex = digest.joinToString("") { "%02x".format(it) }
        val canonSha = MessageDigest.getInstance("SHA-256").digest(utf8)
            .joinToString("") { "%02x".format(it) }
        return HashResult(
            digestHex = hex,
            canonicalUtf8 = utf8,
            canonicalByteCount = utf8.size,
            canonicalSha256 = canonSha,
        )
    }

    fun canonicalize(value: Any?): String {
        return when (value) {
            null, JSONObject.NULL -> "null"
            is Boolean -> if (value) "true" else "false"
            is Number -> canonicalizeNumber(value)
            is String -> escapeString(value)
            is JSONArray -> {
                val parts = (0 until value.length()).map { canonicalize(value.get(it)) }
                parts.joinToString(separator = ",", prefix = "[", postfix = "]")
            }
            is JSONObject -> {
                val keys = value.keys().asSequence().toList().sorted()
                val parts = keys.map { key ->
                    escapeString(key) + ":" + canonicalize(value.get(key))
                }
                parts.joinToString(separator = ",", prefix = "{", postfix = "}")
            }
            else -> escapeString(value.toString())
        }
    }

    private fun canonicalizeNumber(value: Number): String {
        return when (value) {
            is Int, is Long, is Short, is Byte -> value.toString()
            is Double, is Float -> {
                val d = value.toDouble()
                require(d.isFinite()) { "non-finite JSON number is not allowed" }
                if (d == round(d) && abs(d) < 1e15) {
                    // Integer-valued floats serialize as integers (300 not 300.0).
                    d.toLong().toString()
                } else {
                    // Deterministic plain decimal without scientific notation.
                    val bd = java.math.BigDecimal.valueOf(d).stripTrailingZeros()
                    val plain = bd.toPlainString()
                    if (plain == "-0") "0" else plain
                }
            }
            else -> {
                val d = value.toDouble()
                require(d.isFinite()) { "non-finite JSON number is not allowed" }
                if (d == round(d) && abs(d) < 1e15) d.toLong().toString() else value.toString()
            }
        }
    }

    /** Match Python json.dumps(..., ensure_ascii=True) string encoding. */
    fun escapeString(value: String): String {
        val sb = StringBuilder(value.length + 2)
        sb.append('"')
        for (ch in value) {
            when (ch) {
                '\\' -> sb.append("\\\\")
                '"' -> sb.append("\\\"")
                '\b' -> sb.append("\\b")
                '\u000C' -> sb.append("\\f")
                '\n' -> sb.append("\\n")
                '\r' -> sb.append("\\r")
                '\t' -> sb.append("\\t")
                else -> {
                    val code = ch.code
                    if (code < 0x20 || code > 0x7E) {
                        sb.append("\\u%04x".format(code))
                    } else {
                        sb.append(ch)
                    }
                }
            }
        }
        sb.append('"')
        return sb.toString()
    }
}
