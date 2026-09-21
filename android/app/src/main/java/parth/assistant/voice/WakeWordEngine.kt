package parth.assistant.voice

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder

/**
 * On-device wake-word ("Parth") detection + VAD barge-in.
 *
 * Privacy: the hot mic audio never leaves the device — only after the wake
 * word is recognized does audio stream to STT (cloud or local). This addresses
 * the #1 voice-assistant fear (52% worry about passive listening — docs/01 §8).
 *
 * Phase 2 options for the real detector:
 *  - openWakeWord with a custom-trained "Parth" model (on-device, ~2 MB);
 *  - Picovoice Porcupine custom keyword (commercial, very low power);
 *  - Vito/AISHELL-class small KWS models via TFLite.
 * The audio loop below feeds frames to `detector` — swap the placeholder.
 */
class WakeWordEngine(
    private val onWake: () -> Unit,
    private val onUserSpeech: () -> Unit, // VAD event → barge-in
) {
    @Volatile private var running = false
    private var thread: Thread? = null

    /** Placeholder detector: returns 0.0. Replace with a real KWS model. */
    private val detector = { pcm: ShortArray -> 0.0 }
    /** Placeholder VAD: energy-based voice activity. */
    private val vad = { pcm: ShortArray -> pcm.map { it.toInt() }.average() > 900 }

    @SuppressLint("MissingPermission") // RECORD_AUDIO requested in MainActivity
    fun start() {
        if (running) return
        running = true
        thread = Thread({
            val minBuf = AudioRecord.getMinBufferSize(SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
            val record = AudioRecord(MediaRecorder.AudioSource.VOICE_RECOGNITION, SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, minBuf * 2)
            record.startRecording()
            val buffer = ShortArray(FRAME)
            while (running) {
                val n = record.read(buffer, 0, FRAME)
                if (n <= 0) continue
                val score = detector(buffer)
                if (score > 0.65) {           // "Parth" heard
                    onWake()
                    continue
                }
                if (vad(buffer)) onUserSpeech() // owner speaking → barge-in check
            }
            record.stop(); record.release()
        }, "parth-wake-word").apply { start() }
    }

    fun stop() {
        running = false
        thread?.interrupt()
        thread = null
    }

    companion object {
        private const val SAMPLE_RATE = 16000
        private const val FRAME = 512 // 32 ms frames
    }
}
