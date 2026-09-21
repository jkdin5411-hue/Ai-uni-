package parth.assistant.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.IBinder
import parth.assistant.R
import parth.assistant.core.ParthEngine
import parth.assistant.voice.WakeWordEngine

/**
 * Run-once, run-forever foreground service.
 *
 * Owner rule: "मैं इसको एक बार start कर दूँ तो ये run होता रहे — app से back कर दूँ
 * तब भी on रहे।" Implemented as a foreground service with a persistent state
 * notification; survives app-back and screen-off; restarted on boot by
 * [parth.assistant.boot.BootReceiver] and kept alive by a watchdog.
 */
class ParthForegroundService : Service() {

    private lateinit var wakeWordEngine: WakeWordEngine

    override fun onCreate() {
        super.onCreate()
        startForeground(NOTIFICATION_ID, buildNotification("Dormant — say 'Parth'"))
        wakeWordEngine = WakeWordEngine(
            onWake = { ParthEngine.wake() },
            onUserSpeech = { ParthEngine.userStartedSpeaking() },
        )
        ParthEngine.onStateChange = { state ->
            updateNotification(
                when (state) {
                    ParthEngine.State.DORMANT -> "Dormant — say 'Parth'"
                    ParthEngine.State.LISTENING -> "Listening…"
                    ParthEngine.State.SPEAKING -> "Speaking (interruptible)"
                    ParthEngine.State.PLANNING -> "Planning…"
                    ParthEngine.State.EXECUTING -> "Working… (say 'Viram' to stop)"
                    ParthEngine.State.REPORTING -> "Showing results"
                }
            )
        }
        wakeWordEngine.start()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // STICKY: system restarts us if killed; BootReceiver restarts after reboot.
        return START_STICKY
    }

    override fun onDestroy() {
        wakeWordEngine.stop()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    // ------------------------------------------------------------- notification
    private fun buildNotification(text: String): Notification {
        val channel = NotificationChannel(CHANNEL_ID, "Parth status",
            NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        return Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_parth_status)
            .setContentTitle("Parth")
            .setContentText(text)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(text: String) {
        getSystemService(NotificationManager::class.java)
            .notify(NOTIFICATION_ID, buildNotification(text))
    }

    companion object {
        private const val CHANNEL_ID = "parth_status"
        private const val NOTIFICATION_ID = 1001

        fun start(context: Context) {
            context.startForegroundService(Intent(context, ParthForegroundService::class.java))
        }
    }
}
