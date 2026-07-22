package org.gunnchos.edgeio

import android.content.Intent
import android.os.Bundle
import android.os.SystemClock
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import org.gunnchos.edgeio.databinding.ActivityMainBinding
import java.io.File

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private val consent = ConsentManager()
    private val controller = MeasurementSessionController(consent)
    private var physicalMode: Boolean = true
    private var startedAtElapsed: Long = 0L
    private val ticker = object : Runnable {
        override fun run() {
            if (controller.session?.startedAtEpochMs != null) {
                val elapsed = (SystemClock.elapsedRealtime() - startedAtElapsed) / 1000
                binding.timer.text = "%02d:%02d".format(elapsed / 60, elapsed % 60)
                binding.timer.postDelayed(this, 1000)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.summary.text = getString(R.string.collection_summary)
        updateModeLabel()
        binding.profileSpinner.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, listOf("learn", "create", "sense"))
        binding.zoneSpinner.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, listOf("zone_a", "zone_b", "zone_c"))
        binding.networkSpinner.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, listOf("wifi_normal", "wifi_degraded", "cellular_normal", "local_network_degraded"))

        binding.ackSummary.setOnCheckedChangeListener { _, checked -> if (checked) consent.acknowledgeSummary() }
        binding.optIn.setOnCheckedChangeListener { _, checked ->
            if (checked) {
                try {
                    val state = consent.optIn("gary", "android-${System.currentTimeMillis()}")
                    binding.receipt.text = "Receipt: ${state.receiptId}"
                } catch (e: Exception) {
                    binding.optIn.isChecked = false
                    Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
                }
            }
        }
        binding.startBtn.setOnClickListener {
            try {
                if (!physicalMode) throw IllegalStateException("Production UI refuses synthetic collector")
                controller.start(
                    runId = "android-${System.currentTimeMillis()}",
                    siteId = "gary",
                    profile = binding.profileSpinner.selectedItem as String,
                )
                startedAtElapsed = SystemClock.elapsedRealtime()
                binding.timer.post(ticker)
                binding.status.text = "Collecting (${binding.zoneSpinner.selectedItem}/${binding.networkSpinner.selectedItem})"
            } catch (e: Exception) {
                Toast.makeText(this, e.message, Toast.LENGTH_LONG).show()
            }
        }
        binding.stopBtn.setOnClickListener {
            controller.stop()
            binding.timer.removeCallbacks(ticker)
            binding.status.text = "Stopped"
        }
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

    private fun updateModeLabel() {
        binding.modeLabel.text = if (physicalMode) getString(R.string.mode_physical) else getString(R.string.mode_synthetic)
    }

    private fun exportSession() {
        val session = controller.session ?: run {
            Toast.makeText(this, "No session", Toast.LENGTH_SHORT).show()
            return
        }
        val file = File(cacheDir, "${session.runId}.json")
        file.writeText(SessionExporter.toJson(session, consent, physicalMode,
            binding.zoneSpinner.selectedItem as String,
            binding.networkSpinner.selectedItem as String))
        val uri = FileProvider.getUriForFile(this, "$packageName.provider", file)
        val share = Intent(Intent.ACTION_SEND).apply {
            type = "application/json"
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(Intent.createChooser(share, "Export Edge-IO session"))
        binding.status.text = "Exported ${file.name}"
    }
}
