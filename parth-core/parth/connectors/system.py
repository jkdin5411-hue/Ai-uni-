"""System connectors: phone control (Shizuku/Accessibility), desktop computer-use,
Termux/tmux, and the cross-device call reporter.

These map 1:1 to the owner's device requirements:
  * rooted phone with Shizuku → system-level modification permissions;
  * tmux/Termux permissions granted;
  * results shown in-app AND in floating windows;
  * when the owner is away, Parth CALLS their second phone to report.
"""
from __future__ import annotations

from .base import Connector


class PhoneControlConnector(Connector):
    """Android device bridge — Shizuku (privileged) + AccessibilityService (fallback)."""

    name = "phone"
    ACTIONS = {
        "open_app": "launch an app by package/id",
        "tap": "tap screen coordinates (vision-grounded)",
        "swipe": "swipe gesture",
        "read_screen": "capture + OCR/VLM screen understanding",
        "screenshot": "take a screenshot",
        "grant_permission": "grant a permission to an app via Shizuku (privileged)",
        "system_settings": "modify system settings via Shizuku (privileged)",
        "clean_storage": "delete unwanted/hidden storage AFTER owner approval",
        "read_notifications": "read + triage the notification shade",
        "call_phone": "place a call (used for the cross-device report)",
        "enable_hotspot": "toggle Wi-Fi tethering (Shizuku)",
        "auto_start": "keep Parth alive / restart on boot (watchdog)",
    }


class DesktopControlConnector(Connector):
    """Windows/macOS/Linux computer-use: screen vision + mouse/keyboard."""

    name = "desktop"
    ACTIONS = {
        "open_app": "launch a desktop app",
        "screenshot": "capture the screen",
        "click": "click at coordinates",
        "type_text": "type text into the focused window",
        "hotkey": "send a key combination",
        "floating_window": "show results in a floating window (PC-style)",
        "build_ai_model": "scaffold/train a local model on the laptop",
        "train_local": "run local training/fine-tuning (budget-capped)",
    }


class TmuxConnector(Connector):
    """Termux + tmux bridge — the owner grants tmux and shell permissions."""

    name = "tmux"
    ACTIONS = {
        "new_session": "create a tmux session",
        "send_keys": "run a shell command inside a session",
        "read_output": "read the pane output",
        "list_sessions": "list active sessions",
    }


class CallReporterConnector(Connector):
    """Cross-device reporting: Parth calls the owner's other phone and reports
    professionally when work finishes or a client accepts."""

    name = "call_reporter"
    ACTIONS = {
        "call_owner": "place a voice call to the owner's second device",
        "speak_report": "deliver the report over the call (TTS)",
    }
