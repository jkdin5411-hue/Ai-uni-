"""Parth control words.

Owner decisions (2026-09-21):
  * WAKE word  = "Parth"   (say the name to activate / arm listening)
  * STOP word  = "Viram"   (replaces the earlier "Prasthan" design; halts speech
                            and pauses/stops long-running work immediately)

"Prasthan" is explicitly on the reject-list and is NOT recognized as any
control word.
"""
from __future__ import annotations

import re

WAKE_WORD = "parth"
STOP_WORD = "viram"

# Historical name removed by owner decision — must never trigger anything.
DEPRECATED_WORDS = ("prasthan", "प्रस्थान")

_WAKE_ALIASES = {"parth", "paarth", "पार्थ", "पार्त", "parthh"}
_STOP_ALIASES = {"viram", "viraam", "biram", "विराम", "विराम्", "बिराम"}

_SPLIT_RE = re.compile(r"[\s\.,!?;:()\[\]\"'‘’“”\-—–…।]+")


def normalize(text: str) -> str:
    """Lowercase + strip punctuation/Devanagari danda; keep words."""
    return _SPLIT_RE.sub(" ", (text or "").lower()).strip()


def tokens(text: str) -> list[str]:
    return normalize(text).split()


def contains_wake_word(text: str) -> bool:
    return any(t in _WAKE_ALIASES for t in tokens(text))


def contains_stop_word(text: str) -> bool:
    return any(t in _STOP_ALIASES for t in tokens(text))


def is_deprecated_word(text: str) -> bool:
    """True if the text is only the removed historical word (for tests/docs)."""
    return any(t in DEPRECATED_WORDS for t in tokens(text))


def strip_wake_word(text: str) -> str:
    """Remove the first wake-word occurrence and return the remaining command."""
    out = []
    removed = False
    for tok in (text or "").split():
        if not removed and tok.lower().strip(".,!?;:()\"'‘’“”-—…।") in _WAKE_ALIASES:
            removed = True
            continue
        out.append(tok)
    return " ".join(out).strip()
