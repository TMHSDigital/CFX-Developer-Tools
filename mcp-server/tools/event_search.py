"""
Event search tool (event_search.py).

Searches the events.json reference database for common FiveM/RedM events.
"""

from __future__ import annotations

import json
import os


def search_events(
    query: str,
    side: str | None = None,
    data_path: str = "./data",
) -> str:
    """Search events by name or description and return matching results."""

    filepath = os.path.join(data_path, "events.json")

    if not os.path.exists(filepath):
        return f"Error: events database not found at {filepath}"

    with open(filepath, "r", encoding="utf-8") as f:
        events = json.load(f)

    query_lower = query.lower()
    results: list[dict] = []

    for event in events:
        name_match = query_lower in event.get("name", "").lower()
        desc_match = query_lower in event.get("description", "").lower()

        if not (name_match or desc_match):
            continue

        if side and event.get("side") != side and event.get("side") != "shared":
            continue

        results.append(event)

    if not results:
        return f"No events found matching '{query}'."

    output_lines: list[str] = [f"Found {len(results)} event(s) matching '{query}':\n"]

    for e in results[:20]:
        output_lines.append(f"  {e['name']}")
        if e.get("params"):
            output_lines.append(f"    Parameters: {', '.join(e['params'])}")
        if e.get("description"):
            output_lines.append(f"    {e['description']}")
        if e.get("side"):
            output_lines.append(f"    Side: {e['side']}")
        output_lines.append("")

    return "\n".join(output_lines)
