"""Orchestration: scrape the TE calendar, detect due reminders/results,
post them to the right star channel, and persist dedup state."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from build_messages import build_reminder_embed, build_result_embed
from discord_client import DiscordClient
from scraper import fetch_calendar_html, parse_calendar

STATE_PATH = Path(__file__).resolve().parent.parent / "state.json"
REMINDER_WINDOW_MINUTES = 60
STATE_RETENTION_DAYS = 3


def _load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"reminded": {}, "alerted": {}}


def _save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def _prune(state: dict, now: datetime) -> None:
    cutoff = now - timedelta(days=STATE_RETENTION_DAYS)
    for key in ("reminded", "alerted"):
        state[key] = {
            eid: ts for eid, ts in state[key].items()
            if datetime.fromisoformat(ts) >= cutoff
        }


def main() -> None:
    bot_token = os.environ["DISCORD_BOT_TOKEN"]
    channels = {
        1: os.environ["DISCORD_CHANNEL_1STAR"],
        2: os.environ["DISCORD_CHANNEL_2STAR"],
        3: os.environ["DISCORD_CHANNEL_3STAR"],
    }

    client = DiscordClient(bot_token)
    state = _load_state()
    original_state = json.dumps(state, sort_keys=True)

    html = fetch_calendar_html()
    events = parse_calendar(html)

    now = datetime.now(tz=timezone.utc)
    reminder_cutoff = now + timedelta(minutes=REMINDER_WINDOW_MINUTES)

    reminders_sent = 0
    results_sent = 0

    for event in events:
        eid = event["id"]
        scheduled_at = datetime.fromisoformat(event["scheduled_at"])
        channel_id = channels[event["importance"]]

        is_upcoming = now <= scheduled_at <= reminder_cutoff and not event["actual"]
        if is_upcoming and eid not in state["reminded"]:
            embed = build_reminder_embed(event)
            if client.post_message(channel_id, embed):
                state["reminded"][eid] = event["scheduled_at"]
                reminders_sent += 1

        if event["actual"] and eid not in state["alerted"]:
            embed = build_result_embed(event)
            if client.post_message(channel_id, embed):
                state["alerted"][eid] = event["scheduled_at"]
                results_sent += 1

    _prune(state, now)

    print(f"{len(events)} events scanned, {reminders_sent} reminders sent, {results_sent} results sent.")

    if json.dumps(state, sort_keys=True) != original_state:
        _save_state(state)
        print("State updated.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - surface failures clearly in CI logs
        print(f"FATAL: {exc}", file=sys.stderr)
        raise
