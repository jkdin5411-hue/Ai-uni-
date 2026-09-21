package parth.assistant

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import parth.assistant.core.ParthEngine
import parth.assistant.service.ParthForegroundService

/**
 * Main screen: state indicator, mic status, and the capability manager
 * (Skills / Agents / Tools — each with Create, Import, Export, Add More).
 */
class MainActivity : AppCompatActivity() {

    private lateinit var stateLabel: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 64, 32, 32)
        }
        stateLabel = TextView(this).apply {
            text = "Parth — ${ParthEngine.get().state()}"
            textSize = 22f
        }
        root.addView(stateLabel)

        root.addView(button("Grant permissions") { requestCorePermissions() })
        root.addView(button("Enable floating windows") {
            startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION))
        })
        root.addView(button("Open capability manager (Skills/Agents/Tools)") {
            startActivity(Intent(this, CapabilityManagerActivity::class.java))
        })
        root.addView(button("Stop everything (Viram)") { ParthEngine.get().viram() })
        setContentView(root)
    }

    override fun onResume() {
        super.onResume()
        ParthForegroundService.start(this)
        stateLabel.text = "Parth — ${ParthEngine.get().state()}"
    }

    private fun button(label: String, onClick: () -> Unit): Button =
        Button(this).apply { text = label; setOnClickListener { onClick() } }

    private fun requestCorePermissions() {
        val wanted = mutableListOf(
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.POST_NOTIFICATIONS,
            Manifest.permission.CALL_PHONE,
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // foreground-service-microphone type declared in the manifest
        }
        val missing = wanted.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            requestPermissions(missing.toTypedArray(), 1001)
        }
    }
}
