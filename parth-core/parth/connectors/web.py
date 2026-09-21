"""Web connectors: browser automation, AI video generation, thumbnails,
lead-finding, Netlify deployment and Google Cloud training."""
from __future__ import annotations

from .base import Connector


class BrowserConnector(Connector):
    name = "browser"
    ACTIONS = {
        "open_url": "open a URL",
        "login": "log in with stored/owner-provided credentials (2FA → owner)",
        "fill_form": "fill a form",
        "web_search": "search the web",
        "scrape": "scrape/collect data from pages (robots-aware, rate-capped)",
    }


class AIVideoConnector(Connector):
    """Free AI video platforms (Google Flow-class). Logs in with the owner's
    Gmail, generates the video, downloads it."""

    name = "aivideo"
    ACTIONS = {
        "login_platform": "log in to the AI video platform with owner's Gmail",
        "generate_video": "generate a video from the prompt (retry-capped)",
        "download_video": "download the finished video to the device",
    }


class ThumbnailConnector(Connector):
    name = "thumbnail"
    ACTIONS = {
        "generate_thumbnail": "generate a thumbnail (e.g. via ChatGPT/image model)",
    }


class LeadFinderConnector(Connector):
    """Finds high-value businesses without websites (e.g. dental clinics in
    US/LA/Europe) and collects their full business details."""

    name = "leadfinder"
    ACTIONS = {
        "find_businesses": "find N businesses matching the criteria",
        "collect_details": "collect full business details into the lead database",
        "send_proposals": "send proposal messages (approval-gated, day-capped)",
    }


class NetlifyConnector(Connector):
    name = "netlify"
    ACTIONS = {
        "build_website": "build a premium, animated website from collected details",
        "deploy_site": "deploy to Netlify with the owner's account",
        "get_url": "fetch the deployed site URL",
    }


class GoogleCloudConnector(Connector):
    name = "gcloud"
    ACTIONS = {
        "login": "log in with the owner's account",
        "import_project": "import the training project",
        "start_training": "start a training job (approval-gated, spend-capped)",
    }
