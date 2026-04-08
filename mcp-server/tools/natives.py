"""
Native function lookup tool.

Searches the native function database (JSON) by name or description.
"""

from __future__ import annotations

import json
import os


def lookup_native(
    query: str,
    game: str = "gta5",
    side: str | None = None,
    data_path: str = "./data",
) -> str:
    """Search natives by name or description and return matching results."""

    filename = f"natives_{game}.json"
    filepath = os.path.join(data_path, filename)

    if not os.path.exists(filepath):
        return f"Error: native database not found at {filepath}"

    with open(filepath, "r", encoding="utf-8") as f:
        natives = json.load(f)

    query_lower = query.lower()
    results: list[dict] = []

    for native in natives:
        name_match = query_lower in native.get("name", "").lower()
        desc_match = query_lower in native.get("description", "").lower()
        category_match = query_lower in native.get("category", "").lower()

        if not (name_match or desc_match or category_match):
            continue

        if side and native.get("side") != side and native.get("side") != "shared":
            continue

        results.append(native)

    if not results:
        return f"No natives found matching '{query}' for {game}."

    output_lines: list[str] = [f"Found {len(results)} native(s) matching '{query}':\n"]

    for n in results[:20]:
        output_lines.append(f"  {n['name']}")
        if n.get("params"):
            params = ", ".join(
                f"{p['type']} {p['name']}" for p in n["params"]
            )
            output_lines.append(f"    Parameters: ({params})")
        if n.get("return_type"):
            output_lines.append(f"    Returns: {n['return_type']}")
        if n.get("description"):
            output_lines.append(f"    {n['description']}")
        if n.get("side"):
            output_lines.append(f"    Side: {n['side']}")
        output_lines.append("")

    return "\n".join(output_lines)
