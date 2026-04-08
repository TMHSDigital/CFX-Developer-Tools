"""
Build a local documentation index from docs.fivem.net.

Crawls a curated list of documentation page URLs, extracts the title and
a text snippet, and writes the result to mcp-server/data/docs_index.json.

Run from the repository root:
    python .github/scripts/build_docs_index.py

Requires: requests (included in mcp-server/requirements.txt)
"""

from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.request
import urllib.error

OUTPUT_PATH = "mcp-server/data/docs_index.json"

PAGES: list[dict[str, str]] = [
    # Scripting manual
    {"url": "https://docs.fivem.net/docs/scripting-manual/introduction/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/introduction/introduction-to-resources/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/introduction/creating-your-first-script/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/introduction/creating-your-first-script-javascript/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/introduction/creating-your-first-script-csharp/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/introduction/about-native-functions/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/introduction/fact-sheet/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/runtimes/lua/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/runtimes/javascript/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/runtimes/csharp/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/networking/ids/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/networking/state-bags/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/working-with-events/listening-for-events/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/working-with-events/triggering-events/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/working-with-events/canceling-events/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/nui-development/full-screen-nui/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/nui-development/nui-callbacks/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/nui-development/loading-screens/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/nui-development/dui/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/debugging/using-profiler/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/voice/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/using-scaleform/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/migrating-from-deprecated/chat-messages/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/migrating-from-deprecated/creating-commands/", "section": "scripting-manual"},
    {"url": "https://docs.fivem.net/docs/scripting-manual/using-new-game-features/fuel-consumption/", "section": "scripting-manual"},

    # Scripting reference
    {"url": "https://docs.fivem.net/docs/scripting-reference/resource-manifest/resource-manifest/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/events/list/gameEventTriggered/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/events/list/onClientResourceStart/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/events/list/onResourceStart/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/events/list/playerConnecting/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/events/list/playerDropped/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/events/list/populationPedCreating/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/events/list/rconCommand/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/events/list/respawnPlayerPedEvent/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/convars/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/onesync/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/runtimes/lua/client-functions/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/runtimes/lua/server-functions/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/runtimes/javascript/client-functions/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/runtimes/javascript/server-functions/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/runtimes/csharp/client-functions/", "section": "scripting-reference"},
    {"url": "https://docs.fivem.net/docs/scripting-reference/runtimes/csharp/server-functions/", "section": "scripting-reference"},

    # Game references
    {"url": "https://docs.fivem.net/docs/game-references/blips/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/checkpoints/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/controls/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/data-files/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/game-events/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/gamer-tags/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/hud-colors/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/markers/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/net-game-events/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/ped-models/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/text-formatting/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/vehicle-references/vehicle-models/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/vehicle-references/vehicle-colors/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/weapon-models/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/zones/", "section": "game-references"},
    {"url": "https://docs.fivem.net/docs/game-references/instructional-buttons/", "section": "game-references"},

    # Server manual
    {"url": "https://docs.fivem.net/docs/server-manual/setting-up-a-server/", "section": "server-manual"},
    {"url": "https://docs.fivem.net/docs/server-manual/setting-up-a-server-txadmin/", "section": "server-manual"},
    {"url": "https://docs.fivem.net/docs/server-manual/server-commands/", "section": "server-manual"},
    {"url": "https://docs.fivem.net/docs/server-manual/proxy-setup/", "section": "server-manual"},
    {"url": "https://docs.fivem.net/docs/server-manual/frameworks/", "section": "server-manual"},
    {"url": "https://docs.fivem.net/docs/server-manual/finding-resources/", "section": "server-manual"},

    # Stock resources
    {"url": "https://docs.fivem.net/docs/resources/baseevents/", "section": "stock-resources"},
    {"url": "https://docs.fivem.net/docs/resources/chat/", "section": "stock-resources"},
    {"url": "https://docs.fivem.net/docs/resources/chat/events/chatMessage/", "section": "stock-resources"},
    {"url": "https://docs.fivem.net/docs/resources/mapmanager/", "section": "stock-resources"},
    {"url": "https://docs.fivem.net/docs/resources/sessionmanager/", "section": "stock-resources"},
    {"url": "https://docs.fivem.net/docs/resources/spawnmanager/", "section": "stock-resources"},
    {"url": "https://docs.fivem.net/docs/resources/txAdmin/", "section": "stock-resources"},

    # Getting started
    {"url": "https://docs.fivem.net/docs/getting-started/", "section": "getting-started"},
    {"url": "https://docs.fivem.net/docs/getting-started/prerequisites/", "section": "getting-started"},
    {"url": "https://docs.fivem.net/docs/getting-started/installing-fivem/", "section": "getting-started"},
    {"url": "https://docs.fivem.net/docs/getting-started/create-first-script/", "section": "getting-started"},

    # Developer docs
    {"url": "https://docs.fivem.net/docs/developers/sandbox/", "section": "developer-docs"},
    {"url": "https://docs.fivem.net/docs/developers/script-runtimes/", "section": "developer-docs"},
    {"url": "https://docs.fivem.net/docs/developers/server-security/", "section": "developer-docs"},

    # Support
    {"url": "https://docs.fivem.net/docs/support/client-issues/", "section": "support"},
    {"url": "https://docs.fivem.net/docs/support/server-issues/", "section": "support"},
    {"url": "https://docs.fivem.net/docs/support/resource-faq/", "section": "support"},
    {"url": "https://docs.fivem.net/docs/support/server-debug/", "section": "support"},
]

TITLE_RE = re.compile(r"<title[^>]*>([^<]+)</title>", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def extract_title(raw_html: str) -> str:
    """Extract the page title from HTML."""
    match = TITLE_RE.search(raw_html)
    if not match:
        return ""
    title = html.unescape(match.group(1)).strip()
    for suffix in [" | FiveM Documentation", " - Cfx.re Docs"]:
        if title.endswith(suffix):
            title = title[: -len(suffix)].strip()
    return title


def extract_snippet(raw_html: str, max_chars: int = 500) -> str:
    """Extract a text snippet from the main content area."""
    body_start = raw_html.find("<main")
    if body_start == -1:
        body_start = raw_html.find("<article")
    if body_start == -1:
        body_start = raw_html.find("<body")
    if body_start == -1:
        body_start = 0

    chunk = raw_html[body_start : body_start + 10000]
    text = TAG_RE.sub(" ", chunk)
    text = html.unescape(text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text[:max_chars]


def fetch_page(url: str) -> str | None:
    """Fetch a URL and return the HTML content."""
    req = urllib.request.Request(url, headers={"User-Agent": "CFX-Dev-Tools-Indexer/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        print(f"  WARN: failed to fetch {url}: {exc}")
        return None


def build_index() -> list[dict]:
    """Fetch all pages and build the index."""
    index: list[dict] = []
    total = len(PAGES)

    for i, page in enumerate(PAGES, 1):
        url = page["url"]
        section = page["section"]
        print(f"[{i}/{total}] {url}")

        raw_html = fetch_page(url)
        if raw_html is None:
            continue

        title = extract_title(raw_html)
        snippet = extract_snippet(raw_html)

        if not title:
            slug = url.rstrip("/").rsplit("/", 1)[-1]
            title = slug.replace("-", " ").title()

        index.append({
            "title": title,
            "url": url,
            "section": section,
            "snippet": snippet,
        })

        time.sleep(0.3)

    return index


def main() -> None:
    print(f"Building docs index from {len(PAGES)} pages...")
    index = build_index()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nWrote {len(index)} pages to {OUTPUT_PATH}")

    if len(index) < len(PAGES) * 0.8:
        print(f"WARNING: only {len(index)}/{len(PAGES)} pages fetched successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()
