"""Fetch and parse the Trading Economics public economic calendar.

No API key needed: the public calendar page is server-rendered HTML,
fetched with a Chrome-impersonating TLS client (curl_cffi) the same way
the CME FedWatch bot fetches CME's settlement data.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

from bs4 import BeautifulSoup
from curl_cffi import requests

from countries import FX_RELEVANT_COUNTRIES

# g=world returns ~99 countries in a single request (page default is a
# curated subset of ~26 majors only).
CALENDAR_URL = "https://tradingeconomics.com/calendar?g=world"

_DATE_CLASS_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_IMPORTANCE_RE = re.compile(r"calendar-date-(\d)")


def fetch_calendar_html() -> str:
    resp = requests.get(CALENDAR_URL, impersonate="chrome", timeout=30)
    resp.raise_for_status()
    return resp.text


def _parse_time(date_str: str, time_text: str) -> Optional[datetime]:
    """Combine the row's date (from its <td class> token) and time text
    (e.g. "01:30 AM") into a UTC datetime. The site's default timezone
    (no cookie set) is UTC, confirmed via the page's timezone <select>."""
    time_text = time_text.strip()
    if not time_text:
        return None
    try:
        dt = datetime.strptime(f"{date_str} {time_text}", "%Y-%m-%d %I:%M %p")
    except ValueError:
        return None
    return dt.replace(tzinfo=timezone.utc)


def parse_calendar(html: str) -> list[dict]:
    """Parse the calendar table into a list of event dicts, filtered to
    FX_RELEVANT_COUNTRIES. Events without a parseable exact time (e.g.
    "Tentative"/all-day releases) are skipped since reminders/alerts need
    a clock time to schedule against."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="calendar")
    if table is None:
        return []

    events = []
    for row in table.find_all("tr", attrs={"data-id": True}):
        country = (row.get("data-country") or "").strip().lower()
        if country not in FX_RELEVANT_COUNTRIES:
            continue

        # recursive=False: cell 1 (flag) contains its own nested <table><tr><td>,
        # diving into it would break column indexing.
        cells = row.find_all("td", recursive=False)
        if len(cells) < 7:
            continue

        date_cell = cells[0]
        date_match = _DATE_CLASS_RE.search(" ".join(date_cell.get("class", [])))
        time_span = date_cell.find("span")
        if not date_match or time_span is None:
            continue

        importance_match = _IMPORTANCE_RE.search(" ".join(time_span.get("class", [])))
        importance = int(importance_match.group(1)) if importance_match else 1
        importance = max(1, min(3, importance))

        scheduled_at = _parse_time(date_match.group(1), time_span.get_text())
        if scheduled_at is None:
            continue

        event_cell = cells[2]
        event_link = event_cell.find("a", class_="calendar-event")
        event_name = event_link.get_text(strip=True) if event_link else row.get("data-event", "")

        previous_cell = cells[4]
        revised_tag = previous_cell.find(id="revised")
        revised_note = revised_tag.get("title", "").strip() if revised_tag else ""
        previous_span = previous_cell.find(id="previous")
        previous_value = (
            previous_span.get_text(strip=True) if previous_span else previous_cell.get_text(strip=True)
        )

        events.append({
            "id": row["data-id"],
            "country": country,
            "event": event_name,
            "category": row.get("data-category", ""),
            "symbol": row.get("data-symbol", ""),
            "scheduled_at": scheduled_at.isoformat(),
            "importance": importance,
            "actual": cells[3].get_text(strip=True),
            "previous": previous_value,
            "previous_revised_note": revised_note,
            "consensus": cells[5].get_text(strip=True),
            "forecast": cells[6].get_text(strip=True),
        })

    return events


if __name__ == "__main__":
    # Quick manual smoke test: python src/scraper.py
    html = fetch_calendar_html()
    parsed = parse_calendar(html)
    print(f"{len(parsed)} events parsed for {len(FX_RELEVANT_COUNTRIES)} whitelisted countries")
    for e in parsed[:10]:
        print(e)
