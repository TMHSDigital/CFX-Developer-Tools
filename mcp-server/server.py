"""
CFX Developer Tools - MCP Server

A Model Context Protocol server that provides tools for FiveM/RedM
resource development: scaffolding, native lookup, manifest generation,
event search, documentation search, and framework detection.
"""

import os

from mcp.server.fastmcp import FastMCP

from tools.scaffold import scaffold_resource
from tools.natives import lookup_native
from tools.manifest_gen import generate_manifest
from tools.event_search import search_events
from tools.docs_search import search_docs
from tools.detect_framework import detect_framework
from tools.txadmin import (
    txadmin_server_control,
    txadmin_resource_control,
    txadmin_player_search,
    txadmin_kick_player,
)

mcp = FastMCP("cfx-dev-tools")

NATIVES_PATH = os.environ.get("CFX_NATIVES_PATH", "./data")


@mcp.tool()
def scaffold_resource_tool(
    name: str,
    game: str,
    language: str,
    framework: str,
    workspace_path: str | None = None,
) -> str:
    """Create a new FiveM/RedM resource with boilerplate files.

    Args:
        name: Resource name (lowercase, hyphens allowed)
        game: Target game - gta5, rdr3, or both
        language: Scripting language - lua, javascript, or csharp
        framework: Framework - standalone, esx, qbcore, qbox, oxcore, vorp, or rsg
        workspace_path: Path to existing workspace to inherit author from (optional)
    """
    return scaffold_resource(name, game, language, framework, workspace_path)


@mcp.tool()
def lookup_native_tool(
    query: str = "",
    game: str = "gta5",
    side: str | None = None,
    category: str | None = None,
) -> str:
    """Search for a FiveM/RedM native function by name, description, hash, or category.

    Args:
        query: Search term (name, keyword, hash, or description fragment). Leave empty to browse.
        game: Target game - gta5 or rdr3
        side: Filter by side - client, server, or shared (optional)
        category: Filter by namespace/category - e.g. VEHICLE, PED, PLAYER (optional). Leave both query and category empty to list all categories.
    """
    return lookup_native(query, game, side, NATIVES_PATH, category)


@mcp.tool()
def generate_manifest_tool(
    name: str,
    game: str,
    language: str,
    framework: str,
    scripts: list[str] | None = None,
    dependencies: list[str] | None = None,
    has_nui: bool = False,
    workspace_path: str | None = None,
) -> str:
    """Generate a properly formatted fxmanifest.lua file.

    Args:
        name: Resource name
        game: Target game - gta5, rdr3, or both
        language: Scripting language - lua, javascript, or csharp
        framework: Framework - standalone, esx, qbcore, qbox, oxcore, vorp, or rsg
        scripts: Additional script paths to include
        dependencies: Additional resource dependencies
        has_nui: Whether the resource includes NUI (web UI)
        workspace_path: Path to existing resource directory to auto-detect scripts, author, and NUI (optional)
    """
    return generate_manifest(name, game, language, framework, scripts, dependencies, has_nui, workspace_path)


@mcp.tool()
def search_events_tool(
    query: str = "",
    side: str | None = None,
    game: str | None = None,
    framework: str | None = None,
) -> str:
    """Search for common FiveM/RedM events by name or description.

    Args:
        query: Search term (event name or keyword). Leave empty to see a summary of all events.
        side: Filter by side - client, server, or shared (optional)
        game: Filter by game - gta5 or rdr3 (optional)
        framework: Filter by framework - cfx, esx, qbcore, qbox, oxcore, vorp, rsg, baseevents, or chat (optional)
    """
    return search_events(query, side, game, framework, NATIVES_PATH)


@mcp.tool()
def detect_framework_tool(
    workspace_path: str = ".",
) -> str:
    """Detect which FiveM/RedM framework a resource uses by scanning its files.

    Args:
        workspace_path: Path to the resource directory to scan (defaults to current directory)
    """
    return detect_framework(workspace_path)


@mcp.tool()
def search_docs_tool(
    query: str = "",
    section: str | None = None,
) -> str:
    """Search the FiveM/RedM documentation index by keyword.

    Args:
        query: Search term (topic, function name, or keyword). Leave empty to see index summary.
        section: Filter by section - scripting-manual, scripting-reference, game-references, server-manual, stock-resources, getting-started, developer-docs, or support (optional)
    """
    return search_docs(query, section, NATIVES_PATH)


@mcp.tool()
def txadmin_server_control_tool(action: str) -> str:
    """Start, stop, or restart the FXServer through txAdmin.

    Requires the TXADMIN_USERNAME, TXADMIN_PASSWORD, and optionally TXADMIN_URL
    environment variables to be set. See the txadmin-integration skill.

    Args:
        action: One of start, stop, or restart.
    """
    return txadmin_server_control(action)


@mcp.tool()
def txadmin_resource_control_tool(action: str, resource: str) -> str:
    """Start, stop, restart, or ensure a single server resource through txAdmin.

    Requires txAdmin credentials in the environment (see txadmin-integration skill).

    Args:
        action: One of start, stop, restart, or ensure.
        resource: The resource name (folder name) to act on.
    """
    return txadmin_resource_control(action, resource)


@mcp.tool()
def txadmin_player_search_tool(
    search_value: str = "",
    search_type: str = "playerName",
    filters: str | None = None,
    limit: int = 25,
) -> str:
    """Search players known to the server by name, notes, or identifier.

    Requires txAdmin credentials in the environment (see txadmin-integration skill).

    Args:
        search_value: Text to search for.
        search_type: Search mode - playerName, playerNotes, or playerIds.
        filters: Comma-separated filters - isAdmin, isOnline, isWhitelisted, hasNote (optional).
        limit: Maximum number of players to display (server caps at 100).
    """
    return txadmin_player_search(search_value, search_type, filters, limit)


@mcp.tool()
def txadmin_kick_player_tool(
    netid: int,
    reason: str = "",
    mutex: str = "current",
) -> str:
    """Kick an online player by their server network id (netid) through txAdmin.

    Requires txAdmin credentials in the environment (see txadmin-integration skill).

    Args:
        netid: The player's server id (netid) from the player list.
        reason: Optional kick reason shown to the player.
        mutex: Server instance mutex; 'current' (default) targets the running server.
    """
    return txadmin_kick_player(netid, reason, mutex)


if __name__ == "__main__":
    mcp.run()
