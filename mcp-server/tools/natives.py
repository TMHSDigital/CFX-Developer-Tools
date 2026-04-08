"""
Native function lookup tool.

Searches the native function database (JSON) by name, description, or category.
Supports namespace/category browsing and filtering.
"""

from __future__ import annotations

import json
import os
from collections import Counter


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
        if category and native.get("category", "").upper() != category:
            continue

        if side and native.get("side") != side and native.get("side") != "shared":
            continue

        if query:
            query_lower = query.lower()
            name_match = query_lower in native.get("name", "").lower()
            desc_match = query_lower in native.get("description", "").lower()
            cat_match = query_lower in native.get("category", "").lower()
            hash_match = query_lower in native.get("hash", "").lower()
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
        counts[native.get("category", "UNKNOWN")] += 1

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
        lines.append(f"  {n['name']}{dep_marker}")

        if n.get("hash"):
            lines.append(f"    Hash: {n['hash']}")

        if n.get("params"):
            params = ", ".join(
                f"{p['type']} {p['name']}" for p in n["params"]
            )
            lines.append(f"    Parameters: ({params})")

        if n.get("return_type") and n["return_type"] != "void":
            lines.append(f"    Returns: {n['return_type']}")

        if n.get("description"):
            desc = n["description"]
            if len(desc) > 300:
                desc = desc[:297] + "..."
            lines.append(f"    {desc}")

        if n.get("side"):
            lines.append(f"    Side: {n['side']}  |  Category: {n.get('category', '')}")

        if n.get("examples"):
            ex = n["examples"]
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
