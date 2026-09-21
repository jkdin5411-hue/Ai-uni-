"""Capability catalog — 151+ shipped skills, agents and tools (owner target: 151).

Builds the full v1 catalog (155 entries) and registers it into a Registry.
Every entry is individually importable/exportable/creatable per the spec.
"""
from __future__ import annotations

from .registry import Capability, Registry

# (category, kind, persona tags, [capability names])
CATALOG: list[tuple[str, str, list[str], list[str]]] = [
    ("Messaging & Comms", "skill", ["home", "office", "creator"], [
        "WhatsApp Message Reader", "WhatsApp Auto Replier", "WhatsApp Group Blast",
        "Telegram Group Digest", "SMS Auto Responder", "Missed Call Handler",
        "Email Triage", "Email Draft & Schedule", "Contact Enricher",
        "Broadcast Safety Limiter", "Daily Unread Digest", "Urgent Sender Escalation",
    ]),
    ("Content Creation", "skill", ["creator"], [
        "Idea Engine", "Trend Radar", "Script Writer", "Hook Generator",
        "Video Generator Bridge", "Thumbnail Generator", "SEO Title Optimizer",
        "SEO Description Writer", "Tag Researcher", "Shorts Cutter", "Repurpose Engine",
        "Content Calendar", "YouTube Upload Pipeline", "Instagram Post Pipeline",
        "Facebook Post Pipeline", "TikTok Post Pipeline", "Telegram Channel Post",
        "Story Poster", "Comment Triage", "DM Triage", "Analytics Digest",
        "Subtitle Generator", "Dubbing Agent", "Thumbnail A/B Tester",
    ]),
    ("Office Productivity", "skill", ["office"], [
        "Meeting Notes", "Meeting Action Items", "Focus Guard", "Status Report Writer",
        "File Organizer", "Document Summarizer", "Translator", "Web Clipper",
        "Calendar Manager", "Daily Brief", "Inbox Zero Sweep", "Followup Reminder",
    ]),
    ("Research & Intelligence", "skill", ["all"], [
        "Web Search", "Deep Research", "Fact Check", "Competitor Scan", "Market Map",
        "Lead Finder", "Due Diligence", "Price Tracker", "Source Logger",
    ]),
    ("Business & Clients", "skill", ["freelancer"], [
        "Proposal Writer", "Website Builder", "Netlify Deployer", "Website Audit",
        "CRM Sync", "Invoice Drafter", "Expense Tracker", "Brand Voice Guardian",
        "Outreach Sequencer", "Followup Sequencer", "Client Onboarding",
        "Contract Checklist",
    ]),
    ("Film & Series Production", "skill", ["producer"], [
        "Storyboard Artist", "Shot List Generator", "Character Sheet Manager",
        "Continuity Checker", "Scene Generator", "Voice Cast Agent",
        "Music Supervisor Agent", "Colorist Notes", "VFX Breakdown", "Consent Ledger",
        "Production Budget Guard", "Render Queue Manager",
    ]),
    ("Home & Personal Life", "skill", ["home"], [
        "Groceries Agent", "Pantry Tracker", "Meal Planner", "Birthday Rememberer",
        "Gift Idea Agent", "Packing List Maker", "Travel Itinerary", "Flight Watcher",
        "Health Log", "Medication Reminder", "Workout Planner",
        "Home Maintenance Scheduler", "Weather Brief", "News Digest", "Commute Advisor",
    ]),
    ("Company Org", "agent", ["all"], [
        "CEO Orchestrator", "CTO Technology", "Marketing Head", "Finance Head",
        "Social Media Head", "Legal & Compliance", "HR Agent Ops", "Research Head",
        "Content Studio Head", "Security Officer", "Memory Curator", "Skill Forger",
        "Critic", "Planner", "Observer", "Human Liaison",
    ]),
    ("Voice & IO", "tool", ["all"], [
        "Speech To Text Engine", "Text To Speech Engine", "Wake Word Engine",
        "Barge-In VAD", "Speech To Speech Bridge",
    ]),
    ("Device Bridges", "tool", ["phone-power-user", "developer"], [
        "Phone Control Bridge", "Desktop Control Bridge", "Browser Driver",
        "Screen Vision OCR", "Termux Tmux Bridge", "Floating Window Reporter",
        "Phone Call Reporter", "Boot Guardian", "Notification Listener",
        "Media Session Controller", "Hotspot Manager", "Stealth Profile Manager",
        "Screenshot Annotator", "Battery Guardian",
    ]),
    ("Connectors", "tool", ["all"], [
        "WhatsApp Connector", "Gmail Connector", "YouTube Connector",
        "Instagram Connector", "Facebook Connector", "Telegram Connector",
        "TikTok Connector", "Netlify Connector", "Google Cloud Connector",
        "AI Video Platform Connector", "Thumbnail Model Connector",
        "Calendar Connector", "SMS Connector", "Contacts Connector",
    ]),
    ("Core Services", "tool", ["developer"], [
        "Approval Gate", "Audit Log", "Memory Store", "Workflow Scheduler",
        "Model Router", "Spend Cap Guard", "Prompt Injection Firewall",
        "Task Planner Engine", "Parallel Executor", "Skill Package Validator",
    ]),
]


def _slug(name: str) -> str:
    return "-".join("".join(c if c.isalnum() else " " for c in name.lower()).split())


def build_catalog() -> list[Capability]:
    caps: list[Capability] = []
    seen: set[str] = set()
    for category, kind, tags, names in CATALOG:
        for name in names:
            cap_id = _slug(name)
            if cap_id in seen:
                raise ValueError(f"duplicate catalog id: {cap_id}")
            seen.add(cap_id)
            caps.append(Capability(
                id=cap_id,
                kind=kind,
                name=name,
                description=f"{name} — {kind} for {category} "
                            f"(personas: {', '.join(tags)}).",
                version="1.0.0",
                tags=[category.lower(), *tags],
            ))
    return caps


def register_catalog(registry: Registry) -> int:
    count = 0
    for cap in build_catalog():
        registry.add(cap)
        count += 1
    return count


def catalog_size() -> int:
    return len(build_catalog())
