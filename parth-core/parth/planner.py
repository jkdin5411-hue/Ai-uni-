"""Deterministic multi-app task planner.

Turns ONE long spoken instruction (Hinglish supported) into a typed TaskPlan of
Steps with phases. The spine is deliberately deterministic — research shows
agents fail when control flow is delegated to LLMs (docs/01 §6). An LLM planner
can later be plugged in to handle arbitrary phrasing, but it must emit the same
TaskPlan shape.

Phases (execution order; steps inside a phase run in parallel, per-connector
serialized by the Executor):
  0 open          – launch apps / start sessions
  1 read/gen      – read messages, generate video/thumbnails, research leads
  2 act           – send, reply, post, upload, delete (approval gates), deploy, train
  3 notify/report – tell the owner, call the owner's other phone
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------- segmenting
_SEGMENT_SPLIT_RE = re.compile(
    r"(?:\band then\b|\bthen\b|;|।|\bउसके बाद\b|\bऔर फिर\b|\bफिर\b|\baur fir\b|\buske baad\b)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------- connectors
# keyword -> connector id (substring match on the lowercased segment)
CONNECTOR_KEYWORDS: dict[str, list[str]] = {
    "whatsapp": ["whatsapp", "व्हाट्सएप", "व्हाट्सप्प", "whats app", "ग्रुप बना", "group बना", "group ban", "मैसेज भेज", "message भेज", "msg भेज", "रिप्लाई कर"],
    "gmail": ["gmail", "जीमेल", "email", "ईमेल", "मेल ", "delete", "important", "inbox"],
    "youtube": ["youtube", "यूट्यूब", "video upload", "seo", "title", "tags", "description डाल"],
    "instagram": ["instagram", "insta", "इंस्टाग्राम", "story", "reel", "comment", "post", "followers", "फॉलोअर्स"],
    "facebook": ["facebook", "फेसबुक", " fb "],
    "telegram": ["telegram", "टेलीग्राम"],
    "tiktok": ["tiktok", "टिकटॉक"],
    "aivideo": ["ai video", "video बनाओ", "video बना", "video banao", "google flow", "वीडियो बनाओ", "वीडियो बना"],
    "thumbnail": ["thumbnail", "थंबनेल", "chatgpt से"],
    "browser": ["browser", "ब्राउज़र", "web scraping", "scraping"],
    "leadfinder": ["clinic", "doctor", "dentist", "client", "lead", "हाई वैल्यू", "high value", "101"],
    "netlify": ["netlify", "deploy", "डिप्लॉय", "website बना", "website बनाकर", "website publish"],
    "gcloud": ["google cloud", "gcloud", "training start", "train कर", "train करना"],
    "phone": ["phone", "फोन", "storage", "स्टोरेज", "unwanted", "call लगा", "settings modify", "system modify"],
    "desktop": ["laptop", "लैपटॉप", "computer", "कंप्यूटर", " pc ", "desktop"],
    "assistant": [],
}

# ---------------------------------------------------------------- action rules
# connector -> [(action, phase, approval_required, [keywords])]
RULES: dict[str, list[tuple[str, int, bool, list[str]]]] = {
    "whatsapp": [
        ("open", 0, False, ["खोलो", "open", "खोलना"]),
        ("read_messages", 1, False, ["देखो", "message", "मैसेज", "read", "check", "किसका", "आया"]),
        ("reply", 2, False, ["reply", "जवाब", "उत्तर", "रिप्लाई"]),
        ("create_group", 2, True, ["group बना", "ग्रुप बना", "group ban", "group बनाकर", "ग्रुप बनाकर"]),
        ("send_group_message", 2, True, ["भेजो", "भेज दो", "send", "मैसेज भेज", "message भेज", "msg भेज"]),
    ],
    "gmail": [
        ("open", 0, False, ["खोलो", "open"]),
        ("read_emails", 1, False, ["देखो", "read", "check", "emails", "email", "मेल"]),
        ("delete_unimportant", 2, True, ["delete", "हटाओ", "साफ", "साफ़", "clean", "remove"]),
    ],
    "youtube": [
        ("open", 0, False, ["खोलो", "open"]),
        ("play_song", 2, False, ["लगाओ", "play", "song", "गाना"]),
        ("search_trends", 1, False, ["खोजो", "search", "trend"]),
        ("set_metadata", 2, False, ["seo", "title", "description", "tags", "डाल"]),
        ("upload_video", 2, True, ["upload", "पोस्ट", "post", "डाल दो"]),
    ],
    "instagram": [
        ("open", 0, False, ["खोलो", "open"]),
        ("read_dms", 1, False, ["देखो", "message", "dm", "read"]),
        ("reply_dms", 2, False, ["reply", "जवाब"]),
        ("reply_comments", 2, False, ["comment", "कमेंट"]),
        ("message_followers", 2, True, ["followers", "follower", "दोस्तों को", "message भेजो", "मैसेज भेजो"]),
        ("create_group", 2, True, ["group"]),
        ("upload_post", 2, True, ["post", "upload", "पोस्ट"]),
        ("upload_story", 2, True, ["story", "स्टोरी"]),
    ],
    "facebook": [
        ("open", 0, False, ["खोलो", "open", "same", "करो"]),
        ("message_friends", 2, True, ["message", "भेजो", "दोस्तों"]),
        ("reply_messages", 2, False, ["reply", "जवाब"]),
        ("upload_post", 2, True, ["post", "upload", "पोस्ट"]),
    ],
    "telegram": [
        ("open", 0, False, ["खोलो", "open"]),
        ("message_contacts", 2, True, ["message", "भेजो", "send"]),
        ("group_digest", 1, False, ["group", "groups", "देखो", "नया"]),
        ("notify_groups", 3, False, ["बताना", "बताओ", "notify"]),
    ],
    "tiktok": [
        ("open", 0, False, ["खोलो", "open"]),
        ("upload_post", 2, True, ["post", "upload", "पोस्ट", "कर दो"]),
    ],
    "aivideo": [
        ("login_platform", 0, False, ["login", "लॉगिन"]),
        ("generate_video", 1, False, ["बनाओ", "बना", "generate", "banao"]),
        ("download_video", 2, False, ["download", "डाउनलोड"]),
    ],
    "thumbnail": [
        ("generate_thumbnail", 1, False, ["बनाओ", "बना", "generate", "thumbnail"]),
    ],
    "browser": [
        ("open_url", 0, False, ["खोलो", "open", "go"]),
        ("web_search", 1, False, ["खोजो", "search", "find"]),
        ("scrape", 1, False, ["scrap", "scraping", "collect", "data collect", "निकाल"]),
    ],
    "leadfinder": [
        ("find_businesses", 1, False, ["खोजो", "find", "client", "clinic", "doctor", "search"]),
        ("collect_details", 1, False, ["detail", "details", "data", "निकाल", "collect"]),
        ("send_proposals", 2, True, ["proposal", "approach", "message भेजो"]),
    ],
    "netlify": [
        ("build_website", 1, False, ["website बना", "website बनाकर", "build"]),
        ("deploy_site", 2, False, ["deploy", "publish", "डिप्लॉय"]),
        ("get_url", 3, False, ["url", "link"]),
    ],
    "gcloud": [
        ("login", 0, False, ["login", "लॉगिन"]),
        ("import_project", 1, False, ["import", "project"]),
        ("start_training", 2, True, ["train", "training", "ट्रेन"]),
    ],
    "phone": [
        ("open_app", 0, False, ["खोलो", "open"]),
        ("clean_storage", 2, True, ["delete", "साफ", "साफ़", "clean", "unwanted", "हटाओ"]),
        ("system_settings", 2, False, ["settings", "system", "modify", "permission"]),
        ("call_phone", 3, False, ["call", "कॉल", "फोन लगा"]),
        ("read_notifications", 1, False, ["notification", "सूचना"]),
    ],
    "desktop": [
        ("build_ai_model", 1, False, ["model", "मॉडल", "ai बना"]),
        ("train_local", 2, False, ["train", "training"]),
    ],
    "assistant": [
        ("general_query", 1, False, []),
    ],
}


@dataclass
class Step:
    id: str
    title: str
    connector: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    phase: int = 1
    approval_required: bool = False
    retries: int = 0
    status: str = "pending"  # pending|running|done|failed|skipped|stopped|awaiting_approval
    result: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "title": self.title, "connector": self.connector,
            "action": self.action, "params": self.params, "phase": self.phase,
            "approval_required": self.approval_required, "retries": self.retries,
            "status": self.status, "result": self.result,
        }


@dataclass
class TaskPlan:
    command: str
    steps: list[Step] = field(default_factory=list)

    @property
    def parallel_groups(self) -> list[list[Step]]:
        """Steps grouped by phase (ascending); within a phase they may run in
        parallel (the executor serializes same-connector steps via a mutex)."""
        groups: dict[int, list[Step]] = {}
        for s in self.steps:
            groups.setdefault(s.phase, []).append(s)
        return [groups[p] for p in sorted(groups)]

    def summary(self) -> str:
        lines = [f"TaskPlan: {len(self.steps)} steps from one utterance"]
        for s in self.steps:
            flag = " [needs approval]" if s.approval_required else ""
            lines.append(f"  [{s.id}] phase{s.phase} {s.connector}.{s.action}{flag} — {s.title}")
        return "\n".join(lines)


_QUOTED_RE = re.compile(r"[\"“](.+?)[\"”]")


class TaskPlanner:
    """Keyword-deterministic planner (v1). LLM planner plugs in later."""

    def decompose(self, command: str) -> TaskPlan:
        segments = self._segments(command)
        steps: list[Step] = []
        seen: set[tuple[str, str]] = set()
        for seg in segments:
            for connector in self._connectors_in(seg):
                for action, phase, approval, keywords in RULES.get(connector, []):
                    if (connector, action) in seen:
                        continue
                    if self._matches(seg, keywords):
                        steps.append(self._make_step(steps, connector, action, phase, approval, seg))
                        seen.add((connector, action))
        # make sure apps get opened before they are used
        used = {s.connector for s in steps if s.action not in ("open", "login_platform", "login", "open_url", "open_app")}
        has_open = {s.connector for s in steps if s.action in ("open", "login_platform", "login", "open_url", "open_app")}
        for connector in sorted(used - has_open):
            open_action = next(
                (a for a, ph, ap, kw in RULES.get(connector, []) if ph == 0), None
            )
            if open_action:
                steps.append(self._make_step(steps, connector, open_action, 0, False, f"(auto) open {connector}"))
        if not steps:  # nothing recognized → route to the CEO assistant itself
            steps.append(self._make_step(steps, "assistant", "general_query", 1, False, command))
        steps.sort(key=lambda s: s.phase)
        return TaskPlan(command=command, steps=steps)

    # ------------------------------------------------------------------ utils
    def _segments(self, command: str) -> list[str]:
        parts = _SEGMENT_SPLIT_RE.split(command or "")
        # further split on commas, but keep anything non-empty
        out: list[str] = []
        for p in parts:
            for q in p.split(","):
                q = q.strip()
                if q:
                    out.append(q)
        return out or ([command] if command else [])

    def _connectors_in(self, segment: str) -> list[str]:
        low = " " + segment.lower() + " "
        found = []
        for connector, keywords in CONNECTOR_KEYWORDS.items():
            if any(k in low for k in keywords):
                found.append(connector)
        return found

    def _matches(self, segment: str, keywords: list[str]) -> bool:
        if not keywords:
            return True
        low = " " + segment.lower() + " "
        return any(k in low for k in keywords)

    def _make_step(self, steps: list[Step], connector: str, action: str, phase: int,
                   approval: bool, segment: str) -> Step:
        quoted = _QUOTED_RE.search(segment)
        params: dict[str, Any] = {"utterance": segment}
        if quoted:
            params["text"] = quoted.group(1)
        return Step(
            id=f"s{len(steps) + 1}",
            title=f"{connector.replace('_', ' ').title()}: {action.replace('_', ' ')}",
            connector=connector,
            action=action,
            params=params,
            phase=phase,
            approval_required=approval,
        )
