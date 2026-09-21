package parth.assistant.boot

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import parth.assistant.service.ParthForegroundService

/**
 * Auto-start Parth after boot (owner rule: start once → runs forever).
 * Note (docs/04 §1.2): Shizuku itself needs a root start or trusted-WLAN
 * wireless ADB after reboot — Parth's watchdog retries the bridge until it is
 * back; the unprivileged accessibility path works immediately.
 */
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            ParthForegroundService.start(context)
        }
    }
}
