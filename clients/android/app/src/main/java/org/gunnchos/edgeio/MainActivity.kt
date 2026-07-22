package org.gunnchos.edgeio

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.widget.ArrayAdapter
import android.widget.Toast
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
    private val plannedDurationSeconds = 60.0

    private val ticker = object : Runnable {
        override fun run() {
            val session = controller.session
            if (session?.startedAtEpochMs != null && session.endedAtEpochMs == null) {
                val elapsed = (SystemClock.elapsedRealtime() - startedAtElapsed) / 1000
                binding.timer.text = "%02d:%02d / 01:00".format(elapsed / 60, elapsed % 60)
                if (elapsed >= plannedDurationSeconds.toLong()) {
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
            sampleExecutor.execute {
                val sample = sampler.sample(
                    profile = session.profile,
                    networkTypeHint = "wifi",
                )
                mainHandler.post {
                    if (controller.session?.endedAtEpochMs == null) {
                        controller.addSample(sample)
                        binding.status.text =
                            "Collecting sample #${controller.session?.samples?.size ?: 0}"
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
        binding.profileSpinner.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            listOf("learn", "create", "sense"),
        )
        binding.zoneSpinner.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            listOf("zone_calibration", "zone_a", "zone_b", "zone_c"),
        )
        binding.networkSpinner.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            listOf("wifi_normal", "wifi_degraded", "cellular_normal", "local_network_degraded"),
        )

        binding.ackSummary.setOnCheckedChangeListener { _, checked ->
            if (checked) consent.acknowledgeSummary()
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
        }
        binding.startBtn.setOnClickListener {
            try {
                if (!physicalMode) throw IllegalStateException("Production UI refuses synthetic collector")
                if (!binding.optIn.isChecked) throw IllegalStateException("Affirmative consent required")
                controller.start(
                    runId = "pixel-cal-${System.currentTimeMillis()}",
                    siteId = "gary",
                    profile = binding.profileSpinner.selectedItem as String,
                    plannedDurationSeconds = plannedDurationSeconds,
                    calibrationOnly = binding.calibrationOnly.isChecked,
                )
                startedAtElapsed = SystemClock.elapsedRealtime()
                binding.timer.post(ticker)
                mainHandler.post(sampleLoop)
                binding.status.text =
                    "PHYSICAL collecting (${binding.zoneSpinner.selectedItem}/${binding.networkSpinner.selectedItem})"
            } catch (e: Exception) {
                Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
            }
        }
        binding.stopBtn.setOnClickListener { stopCollection("Stopped by operator") }
        binding.exportBtn.setOnClickListener { exportSession() }
        binding.deleteBtn.setOnClickListener {
            controller.delete()
            binding.status.text = "Session deleted"
        }
        binding.withdrawBtn.setOnClickListener {
            try {
                consent.withdraw()
                binding.status.text = "Consent withdrawn"
            } catch (e: Exception) {
                Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
            }
        }
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

    private fun exportSession() {
        val session = controller.session
        if (session == null) {
            Toast.makeText(this, "No session to export", Toast.LENGTH_LONG).show()
            return
        }
        if (session.endedAtEpochMs == null) controller.stop()
        try {
            val json = SessionExporter.toJson(
                session = session,
                consent = consent,
                physical = true,
                zone = binding.zoneSpinner.selectedItem as String,
                networkCondition = binding.networkSpinner.selectedItem as String,
                locationCategory = "home_or_private_indoor",
                deviceCategory = "phone",
                modelLabel = "pixel_6a",
                networkType = "wifi",
            )
            val out = File(cacheDir, "${session.runId}.json")
            out.writeText(json)
            val uri = FileProvider.getUriForFile(this, "$packageName.files", out)
            val share = Intent(Intent.ACTION_SEND).apply {
                type = "application/json"
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(share, "Export Edge-IO session"))
            binding.status.text = "Export ready: ${out.name}"
        } catch (e: Exception) {
            Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
        }
    }
}
