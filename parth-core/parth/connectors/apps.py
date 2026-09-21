"""App connectors: WhatsApp, Gmail, YouTube, Instagram, Facebook, Telegram, TikTok.

v1 executes in dry-run (logs the intended action). The real implementations sit
on the device bridges: Android UI automation (AccessibilityService / Shizuku
UiAutomation) driven by a vision model, or official/unofficial APIs where the
owner has authorized them. Ban-risk pacing caps are enforced in real mode
(docs/04 §2).
"""
from __future__ import annotations

from .base import Connector


class WhatsAppConnector(Connector):
    name = "whatsapp"
    ACTIONS = {
        "open": "open WhatsApp (modded or official) via phone bridge",
        "read_messages": "list unread chats, senders and message contents",
        "reply": "reply to unread conversations (pacing-capped)",
        "create_group": "create a group with given contacts",
        "send_group_message": "send a message to a group (approval-gated)",
    }


class GmailConnector(Connector):
    name = "gmail"
    ACTIONS = {
        "open": "open the Gmail app",
        "read_emails": "list inbox, classify important vs unimportant",
        "delete_unimportant": "delete unimportant emails AFTER owner approval",
        "draft_reply": "draft replies for important emails",
    }


class YouTubeConnector(Connector):
    name = "youtube"
    ACTIONS = {
        "open": "open YouTube (mod app supported)",
        "play_song": "search and play a song",
        "search_trends": "scan trending feed in the niche",
        "set_metadata": "write SEO-friendly title, description, tags",
        "upload_video": "upload video with thumbnail and metadata (approval-gated)",
    }


class InstagramConnector(Connector):
    name = "instagram"
    ACTIONS = {
        "open": "open Instagram (modded supported)",
        "read_dms": "list unread DMs",
        "reply_dms": "reply to DMs (pacing-capped)",
        "reply_comments": "reply to comments in owner's voice",
        "message_followers": "message followers / broadcast groups (approval-gated)",
        "create_group": "create a broadcast group",
        "upload_post": "upload a post (approval-gated)",
        "upload_story": "upload a story (approval-gated)",
    }


class FacebookConnector(Connector):
    name = "facebook"
    ACTIONS = {
        "open": "open Facebook",
        "message_friends": "message friends (approval-gated)",
        "reply_messages": "reply to Messenger conversations",
        "upload_post": "upload a post (approval-gated)",
    }


class TelegramConnector(Connector):
    name = "telegram"
    ACTIONS = {
        "open": "open Telegram",
        "message_contacts": "message contacts (approval-gated)",
        "group_digest": "summarize what's new across groups",
        "notify_groups": "report only what matters to the owner",
    }


class TikTokConnector(Connector):
    name = "tiktok"
    ACTIONS = {
        "open": "open TikTok",
        "upload_post": "upload a post (approval-gated)",
    }


class AssistantConnector(Connector):
    name = "assistant"
    ACTIONS = {
        "general_query": "answer / research / summarize via the model layer",
        "search_web": "web search and summarize with sources, photos and videos",
    }
