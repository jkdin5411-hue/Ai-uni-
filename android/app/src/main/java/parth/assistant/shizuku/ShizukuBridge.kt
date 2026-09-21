package parth.assistant.shizuku

import android.content.Context
import android.content.pm.PackageManager
import rikka.shizuku.Shizuku

/**
 * Privileged bridge to system-level operations via Shizuku.
 *
 * The owner's phone is rooted with Shizuku: "कोई भी permission मैं रोकूँगा नहीं"
 * — every operation below is available once the owner grants Parth the Shizuku
 * permission. Parth can also grant itself further Android permissions
 * (owner-approved) the way Shizuku lends privileges to other apps.
 *
 * Known constraints handled here (docs/04 §1):
 *  - Shizuku dies on reboot → root start / trusted-WLAN wireless restart;
 *  - only ONE UiAutomation service can register at a time → mode manager
 *    falls back to the accessibility bridge when UiAutomation is taken.
 */
object ShizukuBridge {

    private const val SHIZUKU_REQUEST_CODE = 2001

    fun ensurePermission(context: Context, onReady: () -> Unit, onDenied: () -> Unit) {
        if (Shizuku.isPreV11()) { onDenied(); return }
        if (Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED) {
            onReady(); return
        }
        if (Shizuku.shouldShowRequestPermissionRationale()) {
            // Explain: system-level modification requires the Shizuku grant.
        }
        Shizuku.addRequestPermissionResultListener { reqCode, result ->
            if (reqCode == SHIZUKU_REQUEST_CODE) {
                if (result == PackageManager.PERMISSION_GRANTED) onReady() else onDenied()
            }
        }
        Shizuku.requestPermission(SHIZUKU_REQUEST_CODE)
    }

    fun isAlive(): Boolean = try { Shizuku.pingBinder() } catch (_: Throwable) { false }

    // ------------------------------------------------------------- privileged ops

    /** Run a restricted shell command at ADB/root privilege (e.g. settings put ...). */
    fun shell(command: String): Int {
        val process = Shizuku.newProcess(arrayOf("sh", "-c", command), null, null)
        return process.waitFor()
    }

    /** Modify a system setting (secure/global/system). */
    fun putSetting(namespace: String, key: String, value: String): Int =
        shell("settings put $namespace $key $value")

    /** Grant a runtime permission to a package at ADB level (incl. to Parth itself). */
    fun grantPermission(packageName: String, permission: String): Int =
        shell("pm grant $packageName $permission")

    /** Toggle airplane mode (rooted/ADB level). */
    fun setAirplaneMode(enabled: Boolean): Int =
        shell("cmd connectivity airplane-mode ${if (enabled) "enable" else "disable"}")

    /** Enable/disable Wi-Fi tethering. */
    fun setHotspot(enabled: Boolean): Int =
        shell("svc wifi ${if (enabled) "enable" else "disable"}; cmd wifi start-softap " +
                "ParthShare wpa2 parth12345") // exact syntax varies by API level

    /** Force-stop / disable / uninstall an app. */
    fun killApp(packageName: String): Int = shell("am force-stop $packageName")
    fun disableApp(packageName: String): Int = shell("pm disable-user --user 0 $packageName")

    /** Clean unwanted storage (owner-approval-gated in the executor). */
    fun clearAppCache(packageName: String): Int = shell("pm clear --cache-only $packageName")

    /** Wake the screen / keep awake for long autonomous runs. */
    fun wakeScreen(): Int = shell("input keyevent KEYCODE_WAKEUP")
}
