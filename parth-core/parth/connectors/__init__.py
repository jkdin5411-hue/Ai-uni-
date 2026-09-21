from .apps import (AssistantConnector, FacebookConnector, GmailConnector,
                   InstagramConnector, TelegramConnector, TikTokConnector,
                   WhatsAppConnector, YouTubeConnector)
from .base import ActionResult, Connector, ConnectorRouter
from .system import (CallReporterConnector, DesktopControlConnector,
                     PhoneControlConnector, TmuxConnector)
from .web import (AIVideoConnector, BrowserConnector, GoogleCloudConnector,
                  LeadFinderConnector, NetlifyConnector, ThumbnailConnector)

__all__ = [
    "ActionResult", "Connector", "ConnectorRouter",
    "WhatsAppConnector", "GmailConnector", "YouTubeConnector", "InstagramConnector",
    "FacebookConnector", "TelegramConnector", "TikTokConnector", "AssistantConnector",
    "PhoneControlConnector", "DesktopControlConnector", "TmuxConnector", "CallReporterConnector",
    "BrowserConnector", "AIVideoConnector", "ThumbnailConnector", "LeadFinderConnector",
    "NetlifyConnector", "GoogleCloudConnector",
]


def default_router(dry_run: bool = True) -> ConnectorRouter:
    """Wire every connector Parth knows (v1: all dry-run safe)."""
    instances = [
        WhatsAppConnector(dry_run), GmailConnector(dry_run), YouTubeConnector(dry_run),
        InstagramConnector(dry_run), FacebookConnector(dry_run), TelegramConnector(dry_run),
        TikTokConnector(dry_run), AssistantConnector(dry_run),
        PhoneControlConnector(dry_run), DesktopControlConnector(dry_run),
        TmuxConnector(dry_run), CallReporterConnector(dry_run),
        BrowserConnector(dry_run), AIVideoConnector(dry_run), ThumbnailConnector(dry_run),
        LeadFinderConnector(dry_run), NetlifyConnector(dry_run), GoogleCloudConnector(dry_run),
    ]
    return ConnectorRouter({c.name: c for c in instances})
