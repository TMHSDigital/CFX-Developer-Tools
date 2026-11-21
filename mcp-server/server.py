"""
CFX Developer Tools - MCP Server

A Model Context Protocol server that provides tools for FiveM/RedM
resource development: scaffolding, native lookup, manifest generation,
event search, documentation search, and framework detection.
"""

import os

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from tools.scaffold import scaffold_resource
from tools.natives import lookup_native
from tools.manifest_gen import generate_manifest
from tools.manifest_validate import validate_manifest_report
from tools import knowledge
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

# Tool hints let MCP clients apply approval policies: lookups only read
# local data; the txAdmin control and kick tools change a live server.
READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
DESTRUCTIVE = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=True)

# Skills and rules as MCP resources (cfx://skills/<name>, cfx://rules/<name>)
# and skill prompts (cfx-<name>) for clients without the Cursor plugin.
knowledge.register(mcp)

# Data directory for natives, events and the docs index. Defaults to the
# data/ folder next to this file so the server works from any working
# directory. CFX_DATA_PATH overrides it; CFX_NATIVES_PATH is kept as an alias
# for existing configs.
NATIVES_PATH = (
    os.environ.get("CFX_DATA_PATH")
    or os.environ.get("CFX_NATIVES_PATH")
    or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
def scaffold_resource_tool(
    name: str,
    game: str,
    language: str,
    framework: str,
    workspace_path: str | None = None,
    output_path: str | None = None,
    overwrite: bool = False,
) -> str:
    """Create a new FiveM/RedM resource with boilerplate files.

    The resource is created at <output_path>/<name> (default: workspace_path,
    then the CFX_SCAFFOLD_ROOT env var, then the server's working directory).
    The summary reports the absolute path.

    Args:
        name: Resource name (1-64 chars: lowercase letters, digits, '-' or '_')
        game: Target game - gta5, rdr3, or both
        language: Scripting language - lua, javascript, or csharp
        framework: Framework - standalone, esx, qbcore, qbox, oxcore, vorp, or rsg
        workspace_path: Directory to create the resource in and to inherit the author from an existing fxmanifest.lua (optional)
        output_path: Directory to create the resource in, overriding workspace_path (optional)
        overwrite: Replace generated files in an existing non-empty resource directory (default false)
    """
    return scaffold_resource(
        name, game, language, framework, workspace_path, output_path, overwrite
    )


@mcp.tool(annotations=READ_ONLY)
def lookup_native_tool(
    query: str = "",
    game: str = "gta5",
    side: str | None = None,
    category: str | None = None,
    limit: int = 25,
    offset: int = 0,
    format: str = "text",
) -> str:
    """Search for a FiveM/RedM native function by name, description, hash, or category.

    Results are ranked with exact and prefix name matches first.

    Args:
        query: Search term (name in any case with or without underscores, keyword, hash, or description fragment). Leave empty to browse.
        game: Target game - gta5 or rdr3
        side: Filter by side - client, server, or shared (optional)
        category: Filter by namespace/category - e.g. VEHICLE, PED, PLAYER (optional). Leave both query and category empty to list all categories.
        limit: Results per page, 1-100 (default 25)
        offset: Number of results to skip, for paging (default 0)
        format: "text" (default) or "json" for raw records
    """
    return lookup_native(query, game, side, NATIVES_PATH, category, limit, offset, format)


@mcp.tool(annotations=READ_ONLY)
def generate_manifest_tool(
    name: str,
    game: str,
    language: str,
    framework: str,
    scripts: list[str] | None = None,
    dependencies: list[str] | None = None,
    has_nui: bool = False,
    workspace_path: str | None = None,
    exports: list[str] | None = None,
    server_exports: list[str] | None = None,
    mode: str = "create",
) -> str:
    """Generate fxmanifest.lua content, or propose additions to an existing one.

    The tool returns text and never writes files.

    Args:
        name: Resource name
        game: Target game - gta5, rdr3, or both
        language: Scripting language - lua, javascript, or csharp
        framework: Framework - standalone, esx, qbcore, qbox, oxcore, vorp, or rsg
        scripts: Additional script paths to include
        dependencies: Additional resource dependencies
        has_nui: Whether the resource includes NUI (web UI)
        workspace_path: Path to existing resource directory to auto-detect scripts, author, and NUI (optional; required for mode="update")
        exports: Client export names to declare (optional)
        server_exports: Server export names to declare (optional)
        mode: "create" (default) for a new manifest, or "update" to add scripts, dependencies and exports to workspace_path/fxmanifest.lua while keeping every existing line; returns a diff and the full new content
    """
    return generate_manifest(
        name, game, language, framework, scripts, dependencies, has_nui,
        workspace_path, exports, server_exports, mode,
    )


@mcp.tool(annotations=READ_ONLY)
def validate_manifest_tool(path: str, format: str = "text") -> str:
    """Validate a resource's fxmanifest.lua (the same checks CI runs).

    Checks fx_version 'cerulean', valid games, no lua54/__resource.lua, that
    every script, files and ui_page entry matches a file (missing build output
    such as dist/ is a warning), that ui_page is covered by files, and that
    framework dependencies match the games.

    Args:
        path: Resource directory or path to its fxmanifest.lua
        format: "text" (default) or "json" for {"manifest", "errors", "warnings"}
    """
    return validate_manifest_report(path, format)


@mcp.tool(annotations=READ_ONLY)
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


@mcp.tool(annotations=READ_ONLY)
def detect_framework_tool(
    workspace_path: str = ".",
) -> str:
    """Detect which FiveM/RedM framework a resource uses by scanning its files.

    Args:
        workspace_path: Path to the resource directory to scan (defaults to current directory)
    """
    return detect_framework(workspace_path)


@mcp.tool(annotations=READ_ONLY)
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


@mcp.tool(annotations=DESTRUCTIVE)
def txadmin_server_control_tool(action: str) -> str:
    """Start, stop, or restart the FXServer through txAdmin.

    Requires the TXADMIN_USERNAME, TXADMIN_PASSWORD, and optionally TXADMIN_URL
    environment variables to be set. See the txadmin-integration skill.

    Args:
        action: One of start, stop, or restart.
    """
    return txadmin_server_control(action)


@mcp.tool(annotations=DESTRUCTIVE)
def txadmin_resource_control_tool(action: str, resource: str) -> str:
    """Start, stop, restart, or ensure a single server resource through txAdmin.

    Requires txAdmin credentials in the environment (see txadmin-integration skill).

    Args:
        action: One of start, stop, restart, or ensure.
        resource: The resource name (folder name) to act on.
    """
    return txadmin_resource_control(action, resource)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
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


@mcp.tool(annotations=DESTRUCTIVE)
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
