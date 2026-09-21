package parth.assistant

import android.app.Application
import parth.assistant.service.ParthForegroundService

/**
 * Parth application entry.
 * Owner rule: start once → keep running forever (foreground service survives
 * app-back and is restarted on boot by [BootReceiver] and the watchdog).
 */
class ParthApp : Application() {

    override fun onCreate() {
        super.onCreate()
        instance = this
        ParthForegroundService.start(this)
    }

    companion object {
        @Volatile
        private var instance: ParthApp? = null

        fun get(): ParthApp = requireNotNull(instance) { "ParthApp not created yet" }
    }
}
