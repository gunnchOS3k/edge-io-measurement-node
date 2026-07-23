package org.gunnchos.edgeio

enum class SessionMode {
    CALIBRATION,
    PILOT_REHEARSAL,
    PILOT,
    ;

    val plannedDurationSeconds: Double
        get() = when (this) {
            CALIBRATION -> 60.0
            PILOT_REHEARSAL, PILOT -> 300.0
        }

    val runIdPrefix: String
        get() = when (this) {
            CALIBRATION -> "pixel-cal"
            PILOT_REHEARSAL -> "pixel-rehearsal"
            PILOT -> "pixel-pilot"
        }

    val calibrationOnly: Boolean
        get() = this == CALIBRATION

    val rehearsalOnly: Boolean
        get() = this == PILOT_REHEARSAL

    val timerTotalLabel: String
        get() = when (this) {
            CALIBRATION -> "01:00"
            PILOT_REHEARSAL, PILOT -> "05:00"
        }

    val startButtonLabel: String
        get() = when (this) {
            CALIBRATION -> "START 60S CALIBRATION"
            PILOT_REHEARSAL -> "START 5-MIN PILOT REHEARSAL"
            PILOT -> "START 5-MIN PILOT SESSION"
        }

    companion object {
        fun fromWire(value: String): SessionMode = valueOf(value)
    }
}
