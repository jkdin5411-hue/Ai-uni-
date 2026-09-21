"""Parth's internal company organization.

Owner requirement: "इसके अंदर full company agency रख दो" — CEO, CTO, Marketing,
Finance, Social Media, Legal, HR, Research, Content Studio, Security,
Operations. Every department is an agent you can create / import / export.

Research basis (docs/01 §6): attaching every tool to one agent destroys
reliability — so Parth routes each task to a department with a narrow toolset.
"""
from __future__ import annotations

from dataclasses import dataclass, field

ROUTES: list[tuple[str, list[str]]] = [
    ("Finance", ["invoice", "budget", "payment", "expense", "tax", "पैसा", "बजट", "बिल", "paisa"]),
    ("Legal & Compliance", ["consent", "rights", "copyright", "policy", "legal", "gdpr", "अधिकार", "कानून"]),
    ("Social Media", ["instagram", "facebook", "youtube", "tiktok", "telegram", "story", "comment",
                      "follower", "post", "social", "reel", "इंस्टाग्राम", "फेसबुक", "यूट्यूब"]),
    ("CTO / Technology", ["code", "deploy", "server", "train", "model", "api", "bug", "tmux",
                          "repo", "laptop", "google cloud", "ai model", "sdk", "मॉडल", "ट्रेन", "लैपटॉप"]),
    ("Marketing", ["client", "lead", "proposal", "marketing", "brand", "outreach", "seo",
                   "website", "netlify", "clinic", "doctor"]),
    ("Content Studio", ["video", "thumbnail", "script", "edit", "storyboard", "scene",
                        "subtitle", "dub", "वीडियो", "गाना", "song"]),
    ("Research", ["research", "खोजो", "search", "analyze", "summary", "compare", "news", "तुलना"]),
    ("HR & Agent Ops", ["agent", "skill", "tool", "import", "export", "create", "hire"]),
    ("Operations", ["schedule", "workflow", "storage", "clean", "backup", "routine", "रोज़"]),
    ("Security", ["permission", "password", "security", "root", "shizuku", "permissions", "सुरक्षा"]),
]

DEPARTMENT_ROLES: dict[str, str] = {
    "CEO (Parth)": "Orchestrator. Owns approval gates, final decisions, the audit log, and "
                   "escalations. Speaks to the owner with a professional, human tone.",
    "CTO / Technology": "Owns code, servers, tmux/Termux, model training, deployments, and the "
                        "'condensed model' R&D track.",
    "Marketing": "Owns lead generation, proposals, outreach sequencing, website building and "
                 "Netlify publishing for clients.",
    "Finance": "Owns invoices, expenses, budgets, spend caps and cost-per-finished-clip accounting.",
    "Social Media": "Owns WhatsApp/Instagram/Facebook/Telegram/YouTube posting, engagement and "
                    "comment/DM triage, with pacing caps.",
    "Legal & Compliance": "Owns consent ledgers (actor likeness), platform policy checks "
                          "(e.g. YouTube July-2025 AI rules), anti-spam and GDPR/CAN-SPAM caps.",
    "HR & Agent Ops": "Owns creating, importing, exporting and reviewing skills/agents/tools.",
    "Research": "Owns web research, summarization and fact-checking with source logging.",
    "Content Studio": "Owns video generation pipelines, storyboards, character sheets, "
                      "continuity and thumbnails.",
    "Operations": "Owns scheduled workflows, storage hygiene, device persistence and routines.",
    "Security": "Owns permission brokering, the prompt-injection firewall and secrets vault.",
}

DEPARTMENT_TOOLS: dict[str, list[str]] = {
    "CEO (Parth)": ["approval-gate", "audit-log", "memory-store"],
    "CTO / Technology": ["terminal-agent", "tmux-bridge", "gcloud-connector", "model-router"],
    "Marketing": ["lead-finder", "proposal-writer", "website-builder", "netlify-deployer"],
    "Finance": ["invoice-drafter", "expense-tracker", "spend-cap-guard"],
    "Social Media": ["whatsapp-connector", "instagram-connector", "facebook-connector",
                     "telegram-connector", "youtube-connector"],
    "Legal & Compliance": ["consent-ledger", "broadcast-safety-limiter"],
    "HR & Agent Ops": ["skill-forger", "skill-package-validator"],
    "Research": ["web-search", "deep-research", "source-logger"],
    "Content Studio": ["video-generator-bridge", "thumbnail-generator", "storyboard-artist",
                       "continuity-checker"],
    "Operations": ["workflow-scheduler", "storage-cleaner", "boot-guardian"],
    "Security": ["permission-broker", "prompt-injection-firewall", "secrets-vault"],
}


@dataclass
class AgentSpec:
    id: str
    name: str
    department: str
    role: str = ""
    mandate: str = ""
    tools: list[str] = field(default_factory=list)


class CompanyOrg:
    def __init__(self) -> None:
        self.departments: dict[str, AgentSpec] = {
            name: AgentSpec(
                id=name.lower().replace(" ", "-").replace("/", "").replace("(", "").replace(")", ""),
                name=name,
                department=name,
                role=role,
                mandate=f"Handle all {name.lower()} responsibilities end-to-end, escalate to CEO on risk.",
                tools=list(DEPARTMENT_TOOLS.get(name, [])),
            )
            for name, role in DEPARTMENT_ROLES.items()
        }

    def route(self, text: str) -> tuple[str, AgentSpec, str]:
        low = " " + (text or "").lower() + " "
        for dept, keywords in ROUTES:
            for kw in keywords:
                if kw in low:
                    return dept, self.departments[dept], kw
        ceo = self.departments["CEO (Parth)"]
        return "CEO (Parth)", ceo, "no department matched — CEO handles it"

    def org_chart(self) -> str:
        lines = ["Parth & Co. — internal organization", "=" * 40, "CEO (Parth) — orchestrator"]
        for name in DEPARTMENT_ROLES:
            if name == "CEO (Parth)":
                continue
            lines.append(f"  └─ {name}  [tools: {', '.join(DEPARTMENT_TOOLS.get(name, [])[:4])}…]")
        return "\n".join(lines)

    def all_agents(self) -> list[AgentSpec]:
        return list(self.departments.values())
