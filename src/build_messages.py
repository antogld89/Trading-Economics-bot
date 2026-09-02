"""Builds Discord embeds for the two event triggers: upcoming reminder and
published result."""

from __future__ import annotations

import re
from datetime import datetime, timezone

_NUMBER_RE = re.compile(r"-?\d[\d,]*\.?\d*")

STAR_LABELS = {1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐"}
STAR_COLORS = {1: 0x5D6D7E, 2: 0xE67E22, 3: 0xB03A2E}  # grey / orange / red


def _parse_number(text: str) -> float | None:
    match = _NUMBER_RE.search((text or "").replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None


def _comparison_arrow(actual: str, reference: str) -> str:
    a, r = _parse_number(actual), _parse_number(reference)
    if a is None or r is None:
        return ""
    if a > r:
        return "▲"
    if a < r:
        return "▼"
    return "="


def _unix_ts(iso_datetime: str) -> int:
    dt = datetime.fromisoformat(iso_datetime)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _country_title(country: str) -> str:
    return country.title()


def build_reminder_embed(event: dict) -> dict:
    ts = _unix_ts(event["scheduled_at"])
    stars = STAR_LABELS.get(event["importance"], "⭐")
    fields = [
        {"name": "Heure", "value": f"<t:{ts}:t> (<t:{ts}:R>)", "inline": True},
        {"name": "Pays", "value": _country_title(event["country"]), "inline": True},
    ]
    if event.get("forecast"):
        fields.append({"name": "Prévision", "value": event["forecast"], "inline": True})
    if event.get("previous"):
        fields.append({"name": "Précédent", "value": event["previous"], "inline": True})

    return {
        "title": f"🔜 {stars} {event['event']}",
        "color": STAR_COLORS.get(event["importance"], STAR_COLORS[1]),
        "fields": fields,
        "footer": {"text": "Trading Economics — rappel avant publication"},
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


def build_result_embed(event: dict) -> dict:
    ts = _unix_ts(event["scheduled_at"])
    stars = STAR_LABELS.get(event["importance"], "⭐")
    arrow_vs_forecast = _comparison_arrow(event["actual"], event.get("forecast", ""))

    fields = [
        {
            "name": "Actual",
            "value": f"**{event['actual']}** {arrow_vs_forecast}".strip(),
            "inline": True,
        },
        {"name": "Prévision", "value": event.get("forecast") or "—", "inline": True},
        {"name": "Précédent", "value": event.get("previous") or "—", "inline": True},
    ]
    if event.get("consensus") and event["consensus"] != event.get("forecast"):
        fields.append({"name": "Consensus", "value": event["consensus"], "inline": True})
    if event.get("previous_revised_note"):
        fields.append({"name": "Note", "value": event["previous_revised_note"], "inline": False})

    return {
        "title": f"📢 {stars} {event['event']}",
        "description": f"{_country_title(event['country'])} • <t:{ts}:t>",
        "color": STAR_COLORS.get(event["importance"], STAR_COLORS[1]),
        "fields": fields,
        "footer": {"text": "Trading Economics — résultat publié"},
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
