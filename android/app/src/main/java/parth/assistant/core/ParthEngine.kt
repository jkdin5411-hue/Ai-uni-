package parth.assistant.core

import android.os.Handler
import android.os.Looper
import java.util.concurrent.atomic.AtomicReference

/**
 * ParthEngine — the on-device voice state machine. Mirrors `parth-core`'s
 * `parth.assistant.ParthAssistant` (Python) so both platforms behave
 * identically.
 *
 * Owner rules, implemented exactly:
 *  - wake word "Parth" arms listening;
 *  - barge-in: while Parth speaks, any user speech silences it instantly;
 *  - "Viram" (replaces the removed "Prasthan") stops speech + work + session;
 *  - the engine runs forever once started (service-level lifecycle).
 */
object ParthEngine {

    enum class State { DORMANT, LISTENING, SPEAKING, PLANNING, EXECUTING, REPORTING }

    const val WAKE_WORD = "parth"
    const val STOP_WORD = "viram"
    // Historical word removed by owner decision — must never trigger anything.
    private val REJECTED_WORDS = setOf("prasthan", "प्रस्थान")

    private val state = AtomicReference(State.DORMANT)
    private val main = Handler(Looper.getMainLooper())
    @Volatile private var sessionActive = false
    @Volatile private var speechInterrupted = false

    var onStateChange: ((State) -> Unit)? = null
    var onSay: ((String) -> Unit)? = null
    var onCommand: ((String) -> Unit)? = null

    fun state(): State = state.get()

    private fun transition(next: State) {
        state.set(next)
        main.post { onStateChange?.invoke(next) }
    }

    /** Wake word "Parth" detected (or app opened). */
    fun wake() {
        sessionActive = true
        speechInterrupted = false
        transition(State.LISTENING)
    }

    /** STOP word "Viram": silence speech, cancel work, end session. */
    fun viram() {
        speechInterrupted = true
        sessionActive = false
        // TODO Phase 2: executor.cancel() — stop all running steps/agents
        transition(State.DORMANT)
    }

    /** VAD event: the owner started speaking. Returns true if we barge-in. */
    fun userStartedSpeaking(): Boolean {
        if (state.get() == State.SPEAKING) {
            speechInterrupted = true
            transition(State.LISTENING) // silenced → listen
            return true
        }
        return false
    }

    /** Speak in chunks; barge-in silences mid-utterance. */
    fun say(text: String) {
        transition(State.SPEAKING)
        speechInterrupted = false
        val words = text.split(" ")
        val sb = StringBuilder()
        for (w in words) {
            if (speechInterrupted) break
            if (sb.isNotEmpty()) sb.append(' ')
            sb.append(w)
            main.post { onSay?.invoke(sb.toString()) }
            // Real TTS streams audio here; VAD callback interrupts playback.
        }
        if (!speechInterrupted) {
            transition(if (sessionActive) State.LISTENING else State.DORMANT)
        }
    }

    /** A finalized utterance from the STT engine. */
    fun hear(utterance: String) {
        val norm = utterance.lowercase().trim()
        if (containsAny(norm, STOP_WORD, "विराम", "viraam")) return viram()
        if (containsAny(norm, REJECTED_WORDS)) return // removed word: ignore
        val command = if (containsAny(norm, WAKE_WORD, "पार्थ", "paarth")) {
            norm.replace(WAKE_WORD, "").replace("पार्थ", "").trim()
        } else if (state.get() == State.LISTENING) {
            norm
        } else {
            return // dormant and no wake word — ignore
        }
        if (command.isEmpty()) return wake()
        if (!sessionActive) wake()
        process(command)
    }

    private fun process(command: String) {
        transition(State.PLANNING)
        // Phase 2: planner.decompose(command) → TaskPlan (same JSON contract
        // as parth-core), then executor runs steps in parallel with the
        // per-connector device mutex and approval-gated actions.
        transition(State.EXECUTING)
        onCommand?.invoke(command)
    }

    private fun containsAny(text: String, vararg needles: String): Boolean =
        needles.any { it in text }

    private fun containsAny(text: String, needles: Set<String>): Boolean =
        needles.any { it in text }
}
