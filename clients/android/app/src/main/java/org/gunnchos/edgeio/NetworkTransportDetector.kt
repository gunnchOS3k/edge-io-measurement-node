package org.gunnchos.edgeio

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities

/**
 * Detects active network transport for assignment compatibility checks and sample tags.
 * Returns one of: wifi, cellular, ethernet, vpn, other, unavailable.
 */
object NetworkTransportDetector {
    fun detect(context: Context): String {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
            ?: return "unavailable"
        val network = cm.activeNetwork ?: return "unavailable"
        val caps = cm.getNetworkCapabilities(network) ?: return "unavailable"
        return when {
            caps.hasTransport(NetworkCapabilities.TRANSPORT_VPN) -> "vpn"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "wifi"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "cellular"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "ethernet"
            else -> "other"
        }
    }

    fun expectedTransportForCondition(networkCondition: String): String {
        return when {
            networkCondition.startsWith("wifi") -> "wifi"
            networkCondition.startsWith("cellular") -> "cellular"
            "local_network" in networkCondition -> "wifi"
            else -> "unavailable"
        }
    }

    fun isCompatible(detectedTransport: String, expectedTransport: String): Boolean {
        if (expectedTransport == "unavailable") return detectedTransport != "unavailable"
        return detectedTransport == expectedTransport
    }
}
