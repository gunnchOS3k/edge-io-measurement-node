package org.gunnchos.edgeio

import android.app.ActivityManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors
import kotlin.math.abs

/**
 * Collects approved application-layer / device metrics only.
 * Explicitly does not collect GPS, SSID, BSSID, MAC, IMEI, IMSI, serials,
 * phone numbers, emails, account IDs, or advertising IDs.
 */
class PhysicalMetricsSampler(private val context: Context) {
    private val executor = Executors.newSingleThreadExecutor()
    private var lastLatencyMs: Double? = null

    fun sample(profile: String, networkTypeHint: String): MetricSample {
        val unavailable = linkedMapOf<String, String>()
        val battery = batteryStats()
        val memoryPct = memoryPercent()
        val networkType = activeNetworkType() ?: networkTypeHint
        val latency = probeLatencyMs()
        val jitter = if (lastLatencyMs != null && latency != null) {
            abs(latency - lastLatencyMs!!)
        } else {
            unavailable["jitter_ms"] = "insufficient_samples"
            null
        }
        if (latency != null) lastLatencyMs = latency else unavailable["latency_ms"] = "probe_unavailable"

        // Throughput APIs that would require privileged radio stats are not used.
        unavailable["upload_mbps"] = "api_not_exposed_without_privileged_radio_stats"
        unavailable["download_mbps"] = "api_not_exposed_without_privileged_radio_stats"
        unavailable["packet_loss_pct"] = "api_not_exposed_without_privileged_radio_stats"
        unavailable["signal_dbm"] = "not_collected_to_avoid_radio_identifiers"
        unavailable["cpu_pct"] = "api_not_exposed_on_unprivileged_android"

        return MetricSample(
            timestampIso = ConsentManager.utcNowIso(),
            latencyMs = latency,
            jitterMs = jitter,
            packetLossPct = null,
            uploadMbps = null,
            downloadMbps = null,
            networkType = networkType,
            cpuPct = null,
            memoryPct = memoryPct,
            batteryPct = battery.first,
            charging = battery.second,
            thermalState = "nominal",
            localEdgeResponseMs = latency,
            signalDbm = null,
            qualityFlags = listOf("ok", "physical_android", "unavailable_fields_explicit"),
            unavailable = unavailable,
        )
    }

    private fun batteryStats(): Pair<Double?, Boolean?> {
        val intent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
            ?: return Pair(null, null)
        val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
        val status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
        val pct = if (level >= 0 && scale > 0) (100.0 * level / scale) else null
        val charging = status == BatteryManager.BATTERY_STATUS_CHARGING ||
            status == BatteryManager.BATTERY_STATUS_FULL
        return Pair(pct, charging)
    }

    private fun memoryPercent(): Double? {
        val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val info = ActivityManager.MemoryInfo()
        am.getMemoryInfo(info)
        if (info.totalMem <= 0L) return null
        val used = info.totalMem - info.availMem
        return 100.0 * used.toDouble() / info.totalMem.toDouble()
    }

    private fun activeNetworkType(): String? {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork ?: return null
        val caps = cm.getNetworkCapabilities(network) ?: return null
        return when {
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "wifi"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "cellular"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "ethernet"
            else -> "unknown"
        }
    }

    private fun probeLatencyMs(): Double? {
        return try {
            val future = executor.submit<Double?> {
                val url = URL("https://www.google.com/generate_204")
                val conn = (url.openConnection() as HttpURLConnection).apply {
                    requestMethod = "GET"
                    connectTimeout = 3000
                    readTimeout = 3000
                    instanceFollowRedirects = false
                    useCaches = false
                }
                val t0 = System.nanoTime()
                try {
                    conn.responseCode
                    (System.nanoTime() - t0) / 1_000_000.0
                } finally {
                    conn.disconnect()
                }
            }
            future.get()
        } catch (_: Exception) {
            null
        }
    }
}
