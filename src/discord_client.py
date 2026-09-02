"""Minimal Discord REST client: post a message with an embed to a given channel."""

from __future__ import annotations

import requests

API_BASE = "https://discord.com/api/v10"


class DiscordClient:
    def __init__(self, bot_token: str):
        self._headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
        }

    def post_message(self, channel_id: str, embed: dict) -> str | None:
        """Post a new message with the given embed. Returns the message ID,
        or None if the post failed (logged, non-fatal so one bad event
        doesn't stop the rest of the run)."""
        resp = requests.post(
            f"{API_BASE}/channels/{channel_id}/messages",
            headers=self._headers,
            json={"embeds": [embed]},
            timeout=15,
        )
        if resp.status_code >= 400:
            print(f"WARNING: failed to post to channel {channel_id}: {resp.status_code} {resp.text}")
            return None
        return resp.json().get("id")
