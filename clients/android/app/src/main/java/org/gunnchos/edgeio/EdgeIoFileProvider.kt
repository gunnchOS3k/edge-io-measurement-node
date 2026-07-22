package org.gunnchos.edgeio

/**
 * Single source of truth for FileProvider authority.
 * Must match AndroidManifest: android:authorities="${applicationId}.provider"
 */
object EdgeIoFileProvider {
    const val AUTHORITY_SUFFIX = ".provider"

    fun authority(applicationId: String): String = applicationId + AUTHORITY_SUFFIX

    /** Debug-variant expected authority used in regression tests. */
    const val DEBUG_AUTHORITY = "org.gunnchos.edgeio.debug.provider"
}
