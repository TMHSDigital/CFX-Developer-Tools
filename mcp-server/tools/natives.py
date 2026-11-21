"""
Native function lookup tool.

Searches the native function database (JSON) by name, description, or category.
Supports namespace/category browsing and filtering.
"""

from __future__ import annotations

import json
import os
from collections import Counter

VALID_GAMES = ("gta5", "rdr3")


def _text(value: object) -> str:
    """Return a field as a string, treating None/missing as empty."""
    return "" if value is None else str(value)


def _name_key(value: str) -> str:
    """Normalise a native name so GET_PLAYER_PED, GetPlayerPed and
    getplayerped compare equal."""
    return value.replace("_", "").lower()


def _hash_key(value: str) -> str:
    value = value.strip().lower()
    return value[2:] if value.startswith("0x") else value


def lookup_native(
    query: str,
    game: str = "gta5",
    side: str | None = None,
    data_path: str = "./data",
    category: str | None = None,
) -> str:
    """Search natives by name, description, or category.

    If query is empty and category is None, returns a list of all categories
    with counts. If category is set but query is empty, lists all natives in
    that category.
    """

    game = _text(game).strip().lower() or "gta5"
    if game not in VALID_GAMES:
        return f"Error: invalid game '{game}'. Use one of: {', '.join(VALID_GAMES)}."

    filename = f"natives_{game}.json"
    filepath = os.path.join(data_path, filename)

    if not os.path.exists(filepath):
        return f"Error: native database not found at {filepath}"

    with open(filepath, "r", encoding="utf-8") as f:
        natives = json.load(f)

    if not query and not category:
        return _list_categories(natives, game, side)

    if category:
        category = category.upper()

    results: list[dict] = []

    for native in natives:
        if category and _text(native.get("category")).upper() != category:
            continue

        if side and native.get("side") != side and native.get("side") != "shared":
            continue

        if query:
            query_lower = query.lower()
            name_match = _name_key(query) in _name_key(_text(native.get("name")))
            desc_match = query_lower in _text(native.get("description")).lower()
            cat_match = query_lower in _text(native.get("category")).lower()
            hash_query = _hash_key(query)
            hash_match = bool(hash_query) and hash_query in _hash_key(_text(native.get("hash")))
            if not (name_match or desc_match or cat_match or hash_match):
                continue

        results.append(native)

    if not results:
        parts = [f"No natives found"]
        if query:
            parts.append(f"matching '{query}'")
        if category:
            parts.append(f"in category {category}")
        parts.append(f"for {game}.")
        return " ".join(parts)

    return _format_results(results, query, category)


def _list_categories(natives: list[dict], game: str, side: str | None) -> str:
    """Return a summary of all categories and their native counts."""
    counts: Counter[str] = Counter()
    for native in natives:
        if side and native.get("side") != side and native.get("side") != "shared":
            continue
        counts[_text(native.get("category")) or "UNKNOWN"] += 1

    if not counts:
        return f"No categories found for {game}."

    lines = [f"Native categories for {game} ({sum(counts.values())} total natives):\n"]
    for cat, count in sorted(counts.items()):
        lines.append(f"  {cat:24s} {count:>5d} natives")

    lines.append(f"\nUse category='CATEGORY_NAME' to browse natives in a specific namespace.")
    return "\n".join(lines)


def _format_results(results: list[dict], query: str | None, category: str | None) -> str:
    """Format native search results for display."""
    header_parts = [f"Found {len(results)} native(s)"]
    if query:
        header_parts.append(f"matching '{query}'")
    if category:
        header_parts.append(f"in {category}")
    header = " ".join(header_parts)

    show_limit = 25
    lines: list[str] = [f"{header}:\n"]

    for n in results[:show_limit]:
        dep_marker = " [DEPRECATED]" if n.get("deprecated") else ""
        lines.append(f"  {_text(n.get('name')) or '(unnamed)'}{dep_marker}")

        if n.get("hash"):
            lines.append(f"    Hash: {n['hash']}")

        if n.get("params"):
            params = ", ".join(
                f"{_text(p.get('type'))} {_text(p.get('name'))}".strip()
                for p in n["params"]
                if isinstance(p, dict)
            )
            lines.append(f"    Parameters: ({params})")

        if n.get("return_type") and n["return_type"] != "void":
            lines.append(f"    Returns: {n['return_type']}")

        if n.get("description"):
            desc = _text(n["description"])
            if len(desc) > 300:
                desc = desc[:297] + "..."
            lines.append(f"    {desc}")

        if n.get("side"):
            lines.append(f"    Side: {n['side']}  |  Category: {n.get('category', '')}")

        if n.get("examples"):
            ex = _text(n["examples"])
            if len(ex) > 400:
                ex = ex[:397] + "..."
            lines.append(f"    Example:\n{_indent(ex, 6)}")

        lines.append("")

    if len(results) > show_limit:
        lines.append(f"  ... and {len(results) - show_limit} more. Narrow your search for more specific results.")

    return "\n".join(lines)


def _indent(text: str, spaces: int) -> str:
    """Indent every line of text by a given number of spaces."""
    prefix = " " * spaces
    return "\n".join(prefix + line for line in text.split("\n"))
