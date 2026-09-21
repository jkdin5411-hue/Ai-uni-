# Parth — Android app scaffold

Voice-first autonomous assistant for the owner's rooted / Shizuku-enabled phone.
This folder contains the production architecture sources. Build with Android
Studio (or `./gradlew assembleDebug`) on a machine with the Android SDK.

## What's implemented in these sources

| File | Purpose |
|---|---|
| `core/ParthEngine.kt` | The wake/`Viram`/barge-in state machine (mirror of `parth-core`) |
| `service/ParthForegroundService.kt` | **Run once, run forever**: foreground service that survives app-back, restarted by watchdog + boot |
| `service/PhoneControlAccessibilityService.kt` | Phone-use engine: reads the layout tree, performs taps/swipes/text (unprivileged mode) |
| `shizuku/ShizukuBridge.kt` | Privileged system ops via Shizuku (ADB/root level): settings, permissions, tether, app control, restricted shell |
| `voice/WakeWordEngine.kt` | On-device "Parth" hotword + VAD barge-in (plug openWakeWord/Porcupine custom keyword) |
| `ui/FloatingResultWindow.kt` | PC-style floating result overlay (`SYSTEM_ALERT_WINDOW`) |
| `boot/BootReceiver.kt` | Auto-start after reboot |

## Permission checklist (owner grants everything; app must request explicitly)

- `FOREGROUND_SERVICE` + `FOREGROUND_SERVICE_MICROPHONE` — always-on listening
- `RECORD_AUDIO` — wake word / STT (audio stays on-device until armed)
- `SYSTEM_ALERT_WINDOW` — floating result windows
- `BIND_ACCESSIBILITY_SERVICE` — phone-use automation (declared purpose: user-directed automation of the owner's device)
- `RECEIVE_BOOT_COMPLETED` — auto start
- `POST_NOTIFICATIONS` — persistent state notification
- `CALL_PHONE` / `MANAGE_OWN_CALLS` — cross-device report calls
- Shizuku permission (`rikka.shizuku.permission.BIND_BRIDGE_SERVICE`) — privileged bridge
- Termux:RunCommand permission — tmux/shell control

## Setup on the owner's phone (rooted + Shizuku)

1. Install Shizuku, start it (root start is most reliable; wireless ADB works with trusted-WLAN + ADB-auth-timeout disabled — see docs/04 §1.2).
2. Sideload Parth, launch once → the setup wizard walks every permission.
3. Grant Shizuku permission to Parth when prompted → Parth can now modify system settings and grant itself further permissions you approve.
4. Say "Parth" — the assistant arms; say "Viram" to stop anything, anytime.

See `docs/04-problems-bugs-risks.md` for the honest list of Android constraints
(single UiAutomation service, OEM battery killers, banking-app detection, …).
