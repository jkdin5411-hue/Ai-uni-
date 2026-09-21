package parth.assistant

import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.io.File

/**
 * Capability manager — the owner's "Add More" screen.
 *
 * For EACH kind (Skills, Agents, Tools): Create · Import · Export.
 * Packages are `.parth.json` files (same format as parth-core and the
 * skills/ folder in the repo) — import from any file manager, export to
 * Downloads for sharing.
 */
class CapabilityManagerActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; setPadding(32, 64, 32, 32)
        }
        for (kind in listOf("Skills", "Agents", "Tools")) {
            root.addView(TextView(this).apply {
                text = kind; textSize = 20f; setPadding(0, 24, 0, 8)
            })
            root.addView(button("Create new $kind (singular)") { /* TODO Phase 2: editor sheet */ })
            root.addView(button("Import $kind (.parth.json)") { /* TODO: SAF file picker */ })
            root.addView(button("Export selected") { /* TODO: write to Downloads */ })
        }
        setContentView(root)
    }

    private fun button(label: String, onClick: () -> Unit): Button =
        Button(this).apply { text = label; setOnClickListener { onClick() } }
}
