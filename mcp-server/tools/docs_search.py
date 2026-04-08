"""
Documentation search tool (docs_search.py).

Searches a local index of FiveM/RedM documentation pages by keyword.
The index is built by .github/scripts/build_docs_index.py and stored
in mcp-server/data/docs_index.json.
"""

from __future__ import annotations

import json
import os
from collections import Counter


VALID_SECTIONS = {
    "scripting-manual",
    "scripting-reference",
    "game-references",
    "server-manual",
    "stock-resources",
    "getting-started",
    "developer-docs",
    "support",
}


def search_docs(
    query: str = "",
    section: str | None = None,
    data_path: str = "./data",
) -> str:
    """Search the documentation index by keyword and optional section filter.

    If query is empty and section is None, returns a summary of the index.
    """

    filepath = os.path.join(data_path, "docs_index.json")

    if not os.path.exists(filepath):
        return f"Error: documentation index not found at {filepath}"

    with open(filepath, "r", encoding="utf-8") as f:
        pages = json.load(f)

    if not query and not section:
        return _list_summary(pages)

    if section and section not in VALID_SECTIONS:
        return (
            f"Error: invalid section '{section}'. "
            f"Valid sections: {', '.join(sorted(VALID_SECTIONS))}"
        )

    results: list[dict] = []

    for page in pages:
        if section and page.get("section") != section:
            continue

        if query:
            query_lower = query.lower()
            title_match = query_lower in page.get("title", "").lower()
            snippet_match = query_lower in page.get("snippet", "").lower()
            url_match = query_lower in page.get("url", "").lower()
            if not (title_match or snippet_match or url_match):
                continue

        results.append(page)

    if not results:
        parts = ["No documentation pages found"]
        if query:
            parts.append(f"matching '{query}'")
        if section:
            parts.append(f"in section {section}")
        return " ".join(parts) + "."

    return _format_results(results, query, section)


def _list_summary(pages: list[dict]) -> str:
    """Return a summary of the documentation index."""
    section_counts: Counter[str] = Counter()
    for page in pages:
        section_counts[page.get("section", "unknown")] += 1

    lines = [f"Documentation index ({len(pages)} pages):\n"]
    for sec, count in sorted(section_counts.items()):
        lines.append(f"  {sec:24s} {count:>3d} pages")
    lines.append("")
    lines.append("Use section='scripting-manual' to browse a section, or provide a search query.")
    return "\n".join(lines)


def _format_results(results: list[dict], query: str | None, section: str | None) -> str:
    """Format documentation search results."""
    header_parts = [f"Found {len(results)} page(s)"]
    if query:
        header_parts.append(f"matching '{query}'")
    if section:
        header_parts.append(f"in {section}")

    lines: list[str] = [" ".join(header_parts) + ":\n"]

    for page in results[:20]:
        lines.append(f"  {page['title']}")
        lines.append(f"    {page['url']}")
        if page.get("snippet"):
            snippet = page["snippet"]
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."
            lines.append(f"    {snippet}")
        lines.append("")

    if len(results) > 20:
        lines.append(f"  ... and {len(results) - 20} more. Narrow your search.")

    return "\n".join(lines)
