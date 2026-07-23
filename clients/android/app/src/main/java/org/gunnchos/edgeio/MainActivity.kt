package org.gunnchos.edgeio

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.util.Log
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import org.gunnchos.edgeio.databinding.ActivityMainBinding
import java.io.File
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private val consent = ConsentManager()
    private val controller = MeasurementSessionController(consent)
    private lateinit var sampler: PhysicalMetricsSampler
    private val sampleExecutor = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())
    private val physicalMode: Boolean = true
    private var startedAtElapsed: Long = 0L
    private var lastExportFile: File? = null
    private var importedAssignment: PilotAssignment? = null
    private var assignmentValid = false
    private var assignmentValidationMessage = "none"
    private var suppressModeCallback = false

    private val profiles = listOf("learn", "create", "sense")
    private val zones = listOf("zone_calibration", "zone_a", "zone_b", "zone_c", "zone_rehearsal")
    private val networkConditions = listOf(
        "wifi_normal",
        "wifi_degraded",
        "cellular_normal",
        "local_network_degraded",
    )

    private val createDocument =
        registerForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
            val src = lastExportFile
            if (uri == null || src == null || !src.exists()) {
                binding.status.text = "Save cancelled; cache JSON retained: ${src?.name ?: "(none)"}"
                return@registerForActivityResult
            }
            try {
                contentResolver.openOutputStream(uri)?.use { out ->
                    src.inputStream().use { input -> input.copyTo(out) }
                } ?: error("Unable to open destination for write")
                binding.status.text = "Saved via document picker: ${src.name} (${src.length()} bytes). Session retained."
            } catch (e: Exception) {
                logExportFailure("document_save", e)
                binding.status.text =
                    "Document save failed: ${e.javaClass.simpleName}: ${e.message}. Cache file retained: ${src.name}"
                Toast.makeText(this, "Save failed — see on-screen status for full diagnostic", Toast.LENGTH_LONG).show()
            }
        }

    private val openAssignment =
        registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
            if (uri == null) {
                binding.status.text = "Assignment import cancelled"
                return@registerForActivityResult
            }
            try {
                val text = contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
                    ?: error("Unable to read assignment document")
                val assignment = try {
                    PilotAssignment.fromJson(text)
                } catch (ie: AssignmentImportException) {
                    val d = ie.diagnostics
                    importedAssignment = null
                    assignmentValid = false
                    assignmentValidationMessage =
                        "FAIL[${d.category}] id=${d.assignmentId} " +
                            "declared=${d.declaredHash?.take(12)}… calc=${d.calculatedHash?.take(12)}… " +
                            "bytes=${d.canonicalByteCount} — ${d.reason}"
                    refreshSessionDetails()
                    binding.status.text = assignmentValidationMessage
                    Log.e("EdgeIoAssignment", assignmentValidationMessage, ie)
                    Toast.makeText(this, "Assignment import failed — see on-screen status", Toast.LENGTH_LONG).show()
                    return@registerForActivityResult
                }
                if (assignment.sessionMode == SessionMode.CALIBRATION) {
                    importedAssignment = assignment
                    assignmentValid = false
                    assignmentValidationMessage = "rejected: calibration assignment cannot drive pilot/rehearsal UI"
                    applyAssignmentToUi(assignment)
                    refreshSessionDetails()
                    binding.status.text = "Calibration assignment rejected for pilot/rehearsal import"
                    return@registerForActivityResult
                }
                if (PilotAssignment.isExpired(assignment)) {
                    importedAssignment = assignment
                    assignmentValid = false
                    assignmentValidationMessage = "expired (${assignment.expiresAt})"
                    applyAssignmentToUi(assignment)
                    refreshSessionDetails()
                    binding.status.text = "Assignment expired: ${assignment.assignmentId}"
                    return@registerForActivityResult
                }
                importedAssignment = assignment
                assignmentValid = true
                assignmentValidationMessage =
                    "PASS hash+protocol (${assignment.assignmentId} / ${assignment.assignmentHash.take(12)}…)"
                applyAssignmentToUi(assignment)
                refreshSessionDetails()
                binding.status.text =
                    "Imported PASS ${assignment.assignmentId} mode=${assignment.sessionMode} " +
                        "algo=${assignment.assignmentHashAlgorithm}"
            } catch (e: Exception) {
                importedAssignment = null
                assignmentValid = false
                assignmentValidationMessage = "invalid: ${e.message}"
                refreshSessionDetails()
                Toast.makeText(this, "Assignment import failed: ${e.message}", Toast.LENGTH_LONG).show()
                binding.status.text = "Assignment import failed: ${e.message}"
            }
        }

    private val ticker = object : Runnable {
        override fun run() {
            val session = controller.session
            if (session?.startedAtEpochMs != null && session.endedAtEpochMs == null) {
                val elapsed = (SystemClock.elapsedRealtime() - startedAtElapsed) / 1000
                val total = selectedMode().timerTotalLabel
                binding.timer.text = "%02d:%02d / %s".format(elapsed / 60, elapsed % 60, total)
                if (elapsed >= session.plannedDurationSeconds.toLong()) {
                    stopCollection("Timer finished")
                } else {
                    binding.timer.postDelayed(this, 1000)
                }
            }
        }
    }

    private val sampleLoop = object : Runnable {
        override fun run() {
            val session = controller.session ?: return
            if (session.endedAtEpochMs != null) return
            val transport = NetworkTransportDetector.detect(applicationContext)
            sampleExecutor.execute {
                val sample = sampler.sample(
                    profile = session.profile,
                    networkTypeHint = transport,
                )
                mainHandler.post {
                    if (controller.session?.endedAtEpochMs == null) {
                        controller.addSample(sample)
                        binding.status.text =
                            "Collecting sample #${controller.session?.samples?.size ?: 0} ($transport)"
                    }
                }
            }
            mainHandler.postDelayed(this, 5000)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        sampler = PhysicalMetricsSampler(applicationContext)
        binding.summary.text = getString(R.string.collection_summary)
        updateModeLabel()

        binding.sessionModeSpinner.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            SessionMode.values().map { it.name },
        )
        binding.profileSpinner.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            profiles,
        )
        binding.zoneSpinner.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            zones,
        )
        binding.networkSpinner.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            networkConditions,
        )

        binding.sessionModeSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                if (!suppressModeCallback) onModeChanged()
            }

            override fun onNothingSelected(parent: AdapterView<*>?) = Unit
        }

        binding.ackSummary.setOnCheckedChangeListener { _, checked ->
            if (checked) consent.acknowledgeSummary()
            refreshSessionDetails()
        }
        binding.optIn.setOnCheckedChangeListener { _, checked ->
            if (checked) {
                try {
                    val state = consent.optIn("gary", "android-${System.currentTimeMillis()}")
                    binding.receipt.text = "Receipt: ${state.receiptId}\nConsent at: ${state.capturedAtIso}"
                } catch (e: Exception) {
                    binding.optIn.isChecked = false
                    Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
                }
            }
            refreshSessionDetails()
        }
        binding.documentDeviation.setOnCheckedChangeListener { _, _ -> refreshSessionDetails() }

        binding.importAssignmentBtn.setOnClickListener {
            openAssignment.launch(arrayOf("application/json"))
        }
        binding.startBtn.setOnClickListener { startCollection() }
        binding.stopBtn.setOnClickListener { stopCollection("Stopped by operator") }
        binding.exportBtn.setOnClickListener { exportSession() }
        binding.deleteBtn.setOnClickListener {
            controller.delete()
            binding.status.text = "Session deleted"
        }
        binding.withdrawBtn.setOnClickListener {
            try {
                consent.withdraw()
                refreshSessionDetails()
                binding.status.text =
                    "Consent withdrawn (prior session export still uses frozen start-of-session consent)"
            } catch (e: Exception) {
                Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
            }
        }

        onModeChanged()
        refreshSessionDetails()
    }

    private fun selectedMode(): SessionMode {
        val name = binding.sessionModeSpinner.selectedItem as? String ?: SessionMode.CALIBRATION.name
        return SessionMode.fromWire(name)
    }

    private fun onModeChanged() {
        val mode = selectedMode()
        binding.startBtn.text = mode.startButtonLabel
        binding.timer.text = "00:00 / ${mode.timerTotalLabel}"
        val assignmentBound = mode != SessionMode.CALIBRATION && importedAssignment != null
        setSpinnersEnabled(!assignmentBound)
        if (mode == SessionMode.CALIBRATION && importedAssignment == null) {
            selectSpinner(binding.zoneSpinner, "zone_calibration")
            selectSpinner(binding.networkSpinner, "wifi_normal")
        } else {
            val asn = importedAssignment
            if (asn != null && asn.sessionMode == mode) {
                // Sync assignment fields without re-entering via mode spinner callback.
                suppressModeCallback = true
                try {
                    selectSpinner(binding.profileSpinner, asn.workloadProfile)
                    selectSpinner(binding.zoneSpinner, asn.namedTestZone)
                    selectSpinner(binding.networkSpinner, asn.networkCondition)
                } finally {
                    suppressModeCallback = false
                }
                setSpinnersEnabled(false)
            }
        }
        refreshSessionDetails()
    }

    private fun setSpinnersEnabled(enabled: Boolean) {
        binding.profileSpinner.isEnabled = enabled
        binding.zoneSpinner.isEnabled = enabled
        binding.networkSpinner.isEnabled = enabled
    }

    private fun applyAssignmentToUi(assignment: PilotAssignment) {
        suppressModeCallback = true
        try {
            selectSpinner(binding.sessionModeSpinner, assignment.sessionMode.name)
            selectSpinner(binding.profileSpinner, assignment.workloadProfile)
            selectSpinner(binding.zoneSpinner, assignment.namedTestZone)
            selectSpinner(binding.networkSpinner, assignment.networkCondition)
        } finally {
            suppressModeCallback = false
        }
        if (assignment.environmentalNotePrompt.isNotBlank()) {
            binding.environmentalNotes.hint = assignment.environmentalNotePrompt
        }
        setSpinnersEnabled(false)
        binding.startBtn.text = assignment.sessionMode.startButtonLabel
        binding.timer.text = "00:00 / ${assignment.sessionMode.timerTotalLabel}"
        refreshSessionDetails()
    }

    private fun selectSpinner(spinner: android.widget.Spinner, value: String) {
        val adapter = spinner.adapter ?: return
        for (i in 0 until adapter.count) {
            if (adapter.getItem(i)?.toString() == value) {
                spinner.setSelection(i)
                return
            }
        }
        // Value not in adapter — append so assignment zones/conditions still display.
        val items = (0 until adapter.count).map { adapter.getItem(it).toString() }.toMutableList()
        items.add(value)
        spinner.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, items)
        spinner.setSelection(items.lastIndex)
    }

    private fun refreshSessionDetails() {
        val mode = selectedMode()
        val detected = NetworkTransportDetector.detect(applicationContext)
        val declared = when {
            importedAssignment != null && mode != SessionMode.CALIBRATION ->
                importedAssignment!!.networkCondition
            else -> binding.networkSpinner.selectedItem as? String ?: "wifi_normal"
        }
        val expected = importedAssignment?.expectedNetworkTransport
            ?: NetworkTransportDetector.expectedTransportForCondition(declared)
        val compatible = NetworkTransportDetector.isCompatible(detected, expected)
        val asn = importedAssignment
        val day = when {
            asn != null && mode != SessionMode.CALIBRATION -> asn.collectionDayId
            mode == SessionMode.CALIBRATION -> "calibration_day"
            else -> "day_unassigned"
        }
        val zone = when {
            asn != null && mode != SessionMode.CALIBRATION -> asn.namedTestZone
            else -> binding.zoneSpinner.selectedItem as? String ?: "zone_calibration"
        }
        val profile = when {
            asn != null && mode != SessionMode.CALIBRATION -> asn.workloadProfile
            else -> binding.profileSpinner.selectedItem as? String ?: "learn"
        }
        val locationCategory = asn?.locationCategory ?: "home_or_private_indoor"
        val indoorOutdoor = asn?.indoorOutdoor ?: "indoor"
        val movement = asn?.stationaryOrMoving ?: "stationary"
        val cellId = asn?.matrixCellId ?: "(none)"
        val planned = if (asn != null && mode != SessionMode.CALIBRATION) {
            asn.plannedDurationSeconds.toInt()
        } else {
            mode.plannedDurationSeconds.toInt()
        }

        binding.countingBanner.text = when (mode) {
            SessionMode.CALIBRATION -> "CALIBRATION — DOES NOT COUNT (excluded from 54-session pilot)"
            SessionMode.PILOT_REHEARSAL -> "REHEARSAL — DOES NOT COUNT (excluded from 54-session pilot)"
            SessionMode.PILOT -> "PILOT — COUNTS toward the 54-session matrix (only after full validation)"
        }
        binding.countingBanner.setTextColor(
            when (mode) {
                SessionMode.PILOT -> 0xFF0B6E4F.toInt()
                else -> 0xFF8B1E3F.toInt()
            },
        )
        binding.buildIdentity.text =
            "Build: ${BuildConfig.VERSION_NAME} (code ${BuildConfig.VERSION_CODE}) " +
                "commit=${BuildConfig.GIT_COMMIT.take(12)} dirty=${BuildConfig.GIT_DIRTY} " +
                "protocol=${BuildConfig.ASSIGNMENT_PROTOCOL_VERSION} ts=${BuildConfig.BUILD_TIMESTAMP}"
        binding.assignmentStatus.text =
            "Assignment validation: ${if (assignmentValid) "OK" else "not ready"} — $assignmentValidationMessage"
        binding.consentStatus.text =
            "Consent status: ${consent.state.status} (ack=${consent.state.summaryAcknowledged})"
        binding.sessionDetails.text = buildString {
            appendLine("Mode: ${mode.name}")
            appendLine("Collection day: $day")
            appendLine("Matrix cell id: $cellId")
            appendLine("Named test zone: $zone")
            appendLine("Location category: $locationCategory")
            appendLine("Indoor/outdoor: $indoorOutdoor")
            appendLine("Stationary/moving: $movement")
            appendLine("Declared network condition: $declared")
            appendLine("Detected network transport: $detected")
            appendLine("Expected transport: $expected")
            appendLine("Transport compatible: $compatible")
            appendLine("Workload: $profile")
            appendLine("Planned duration: ${planned}s (${mode.timerTotalLabel})")
            if (asn != null) {
                appendLine("Assignment id: ${asn.assignmentId}")
                appendLine("Assignment hash: ${asn.assignmentHash}")
            }
        }
    }

    private fun startCollection() {
        try {
            if (!physicalMode) throw IllegalStateException("Production UI refuses synthetic collector")
            if (!binding.optIn.isChecked || consent.state.status != "active") {
                throw IllegalStateException("Affirmative consent required")
            }
            val mode = selectedMode()
            val detected = NetworkTransportDetector.detect(applicationContext)
            val notes = binding.environmentalNotes.text?.toString()?.take(280).orEmpty()
            val documentDeviation = binding.documentDeviation.isChecked

            when (mode) {
                SessionMode.CALIBRATION -> startCalibration(detected, notes)
                SessionMode.PILOT_REHEARSAL, SessionMode.PILOT ->
                    startAssignmentBound(mode, detected, notes, documentDeviation)
            }
        } catch (e: Exception) {
            Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
        }
    }

    private fun startCalibration(detected: String, notes: String) {
        val zone = binding.zoneSpinner.selectedItem as String
        val network = binding.networkSpinner.selectedItem as String
        val profile = binding.profileSpinner.selectedItem as String
        val mode = SessionMode.CALIBRATION
        controller.start(
            runId = "${mode.runIdPrefix}-${System.currentTimeMillis()}",
            siteId = "gary",
            profile = profile,
            plannedDurationSeconds = mode.plannedDurationSeconds,
            sessionMode = mode,
            calibrationOnly = true,
            rehearsalOnly = false,
            collectionDayId = "calibration_day",
            namedTestZone = zone,
            locationCategory = "home_or_private_indoor",
            indoorOutdoor = "indoor",
            stationaryOrMoving = "stationary",
            networkCondition = network,
            detectedNetworkTransport = detected,
            declaredNetworkCondition = network,
            environmentalNotes = notes,
            transportCompatible = true,
            protocolDeviation = "calibration_not_pilot",
        )
        beginLiveCollection("PHYSICAL collecting calibration ($zone/$network/$detected)")
    }

    private fun startAssignmentBound(
        mode: SessionMode,
        detected: String,
        notes: String,
        documentDeviation: Boolean,
    ) {
        val asn = importedAssignment
            ?: throw IllegalStateException("Valid assignment required for ${mode.name}")
        if (!assignmentValid) throw IllegalStateException("Assignment validation failed")
        if (asn.sessionMode != mode) {
            throw IllegalStateException("Assignment session_mode=${asn.sessionMode} does not match UI mode=$mode")
        }
        val expected = asn.expectedNetworkTransport
        val compatible = NetworkTransportDetector.isCompatible(detected, expected)
        if (!compatible && !documentDeviation) {
            throw IllegalStateException(
                "Detected transport=$detected incompatible with expected=$expected. " +
                    "Check the protocol deviation box to document network_condition_mismatch.",
            )
        }
        val deviation = when {
            mode == SessionMode.PILOT_REHEARSAL -> "rehearsal_not_pilot"
            !compatible && documentDeviation -> "network_condition_mismatch"
            else -> null
        }
        controller.start(
            runId = "${mode.runIdPrefix}-${System.currentTimeMillis()}",
            siteId = asn.siteId ?: "gary",
            profile = asn.workloadProfile,
            plannedDurationSeconds = asn.plannedDurationSeconds.coerceAtLeast(mode.plannedDurationSeconds),
            sessionMode = mode,
            calibrationOnly = asn.calibrationOnly,
            rehearsalOnly = asn.rehearsalOnly,
            collectionDayId = asn.collectionDayId,
            namedTestZone = asn.namedTestZone,
            locationCategory = asn.locationCategory,
            indoorOutdoor = asn.indoorOutdoor,
            stationaryOrMoving = asn.stationaryOrMoving,
            networkCondition = asn.networkCondition,
            detectedNetworkTransport = detected,
            declaredNetworkCondition = asn.networkCondition,
            assignmentId = asn.assignmentId,
            assignmentHash = asn.assignmentHash,
            matrixCellId = asn.matrixCellId,
            protocolVersion = asn.protocolVersion,
            environmentalNotes = notes,
            transportCompatible = compatible,
            protocolDeviation = deviation,
        )
        beginLiveCollection(
            "PHYSICAL collecting ${mode.name} (${asn.namedTestZone}/${asn.networkCondition}/$detected)",
        )
    }

    private fun beginLiveCollection(status: String) {
        startedAtElapsed = SystemClock.elapsedRealtime()
        binding.timer.post(ticker)
        mainHandler.post(sampleLoop)
        binding.status.text = status
    }

    private fun stopCollection(reason: String) {
        binding.timer.removeCallbacks(ticker)
        mainHandler.removeCallbacks(sampleLoop)
        controller.stop()
        val n = controller.session?.samples?.size ?: 0
        binding.status.text = "$reason — samples=$n. Export when ready."
    }

    private fun updateModeLabel() {
        binding.modeLabel.text = getString(R.string.mode_physical)
        binding.modeLabel.setTextColor(0xFF0B6E4F.toInt())
    }

    private fun fileProviderAuthority(): String =
        EdgeIoFileProvider.authority(BuildConfig.APPLICATION_ID)

    private fun writeSessionJson(): File {
        val session = controller.session ?: error("No session to export")
        if (session.endedAtEpochMs == null) controller.stop()
        val active = controller.session ?: session
        val detected = active.detectedNetworkTransport.ifBlank {
            NetworkTransportDetector.detect(applicationContext)
        }
        val json = SessionExporter.toJson(
            session = active,
            consent = consent,
            physical = true,
            zone = active.namedTestZone,
            networkCondition = active.declaredNetworkCondition,
            locationCategory = active.locationCategory,
            deviceCategory = "phone",
            modelLabel = "pixel_6a",
            networkType = detected,
        )
        val out = File(cacheDir, "${active.runId}.json")
        out.writeText(json)
        check(out.exists() && out.length() > 0L) { "Export write failed: empty or missing ${out.name}" }
        lastExportFile = out
        return out
    }

    private fun exportSession() {
        if (controller.session == null && lastExportFile?.exists() != true) {
            Toast.makeText(this, "No session to export", Toast.LENGTH_LONG).show()
            return
        }
        try {
            val out = if (controller.session != null) {
                writeSessionJson()
            } else {
                lastExportFile!!
            }
            binding.status.text = "Wrote ${out.name} (${out.length()} bytes) to app cache. Opening share…"
            val authority = fileProviderAuthority()
            val uri = FileProvider.getUriForFile(this, authority, out)
            val share = Intent(Intent.ACTION_SEND).apply {
                type = "application/json"
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            try {
                startActivity(Intent.createChooser(share, "Export Edge-IO session"))
                binding.status.text =
                    "Share open: ${out.name} (${out.length()} bytes). Authority=$authority. Session retained — EXPORT again or Save to Downloads if needed."
            } catch (shareError: Exception) {
                logExportFailure("share_chooser", shareError)
                binding.status.text =
                    "Share failed (${shareError.javaClass.simpleName}: ${shareError.message}). JSON retained at ${out.name}. Opening Save to Downloads…"
                createDocument.launch(out.name)
            }
        } catch (e: Exception) {
            logExportFailure("exportSession", e)
            val retained = lastExportFile?.let { " Retained cache file: ${it.name} (${it.length()} bytes)." } ?: ""
            val msg = "Export failed: ${e.javaClass.name}: ${e.message}.$retained Session NOT deleted."
            binding.status.text = msg
            Log.e(TAG, msg, e)
            Toast.makeText(this, "Export failed — see on-screen status (full diagnostic)", Toast.LENGTH_LONG).show()
            lastExportFile?.takeIf { it.exists() && it.length() > 0L }?.let { createDocument.launch(it.name) }
        }
    }

    private fun logExportFailure(stage: String, e: Exception) {
        Log.e(TAG, "export_failure stage=$stage class=${e.javaClass.name} message=${e.message}", e)
    }

    companion object {
        private const val TAG = "EdgeIoExport"
    }
}
