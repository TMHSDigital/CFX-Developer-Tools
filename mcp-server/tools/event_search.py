"""
Event search tool (event_search.py).

Searches the events.json reference database for common FiveM/RedM events.
Supports filtering by side, game, and framework.
"""

from __future__ import annotations

import json
import os
from collections import Counter


def search_events(
    query: str = "",
    side: str | None = None,
    game: str | None = None,
    framework: str | None = None,
    data_path: str = "./data",
) -> str:
    """Search events by name or description with optional filters.

    If query is empty and no filters are set, returns a summary of all
    available events grouped by framework.
    """

    filepath = os.path.join(data_path, "events.json")

    if not os.path.exists(filepath):
        return f"Error: events database not found at {filepath}"

    with open(filepath, "r", encoding="utf-8") as f:
        events = json.load(f)

    if not query and not side and not game and not framework:
        return _list_summary(events)

    results: list[dict] = []

    for event in events:
        if query:
            query_lower = query.lower()
            name_match = query_lower in event.get("name", "").lower()
            desc_match = query_lower in event.get("description", "").lower()
            fw_match = query_lower in event.get("framework", "").lower()
            if not (name_match or desc_match or fw_match):
                continue

        if side and event.get("side") != side and event.get("side") != "shared":
            continue

        if game and event.get("game") != game and event.get("game") != "shared":
            continue

        if framework and event.get("framework") != framework:
            continue

        results.append(event)

    if not results:
        parts = ["No events found"]
        if query:
            parts.append(f"matching '{query}'")
        if framework:
            parts.append(f"in framework {framework}")
        return " ".join(parts) + "."

    return _format_results(results, query, framework)


def _list_summary(events: list[dict]) -> str:
    """Return a summary of events grouped by framework."""
    fw_counts: Counter[str] = Counter()
    side_counts: Counter[str] = Counter()
    for event in events:
        fw_counts[event.get("framework", "unknown")] += 1
        side_counts[event.get("side", "unknown")] += 1

    lines = [f"Event reference database ({len(events)} events):\n"]
    lines.append("By framework:")
    for fw, count in sorted(fw_counts.items()):
        lines.append(f"  {fw:16s} {count:>3d} events")
    lines.append("")
    lines.append("By side:")
    for s, count in sorted(side_counts.items()):
        lines.append(f"  {s:16s} {count:>3d} events")
    lines.append("")
    lines.append("Use framework='esx' or side='server' to filter, or provide a search query.")
    return "\n".join(lines)


def _format_results(results: list[dict], query: str | None, framework: str | None) -> str:
    """Format event search results for display."""
    header_parts = [f"Found {len(results)} event(s)"]
    if query:
        header_parts.append(f"matching '{query}'")
    if framework:
        header_parts.append(f"in {framework}")

    lines: list[str] = [" ".join(header_parts) + ":\n"]

    for e in results[:30]:
        lines.append(f"  {e['name']}")
        if e.get("params"):
            lines.append(f"    Parameters: {', '.join(e['params'])}")
        if e.get("description"):
            lines.append(f"    {e['description']}")
        info_parts = []
        if e.get("side"):
            info_parts.append(f"Side: {e['side']}")
        if e.get("game") and e["game"] != "shared":
            info_parts.append(f"Game: {e['game']}")
        if e.get("framework"):
            info_parts.append(f"Framework: {e['framework']}")
        if info_parts:
            lines.append(f"    {' | '.join(info_parts)}")
        lines.append("")

    if len(results) > 30:
        lines.append(f"  ... and {len(results) - 30} more. Narrow your search.")

    return "\n".join(lines)
