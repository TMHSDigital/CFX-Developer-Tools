"""
CFX Developer Tools - MCP Server

A Model Context Protocol server that provides tools for FiveM/RedM
resource development: scaffolding, native lookup, manifest generation,
and event search.
"""

import os

from mcp.server.fastmcp import FastMCP

from tools.scaffold import scaffold_resource
from tools.natives import lookup_native
from tools.manifest_gen import generate_manifest
from tools.docs_search import search_events

mcp = FastMCP("cfx-dev-tools")

NATIVES_PATH = os.environ.get("CFX_NATIVES_PATH", "./data")


@mcp.tool()
def scaffold_resource_tool(
    name: str,
    game: str,
    language: str,
    framework: str,
) -> str:
    """Create a new FiveM/RedM resource with boilerplate files.

    Args:
        name: Resource name (lowercase, hyphens allowed)
        game: Target game - gta5, rdr3, or both
        language: Scripting language - lua, javascript, or csharp
        framework: Framework - standalone, esx, qbcore, or oxcore
    """
    return scaffold_resource(name, game, language, framework)


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
) -> str:
    """Generate a properly formatted fxmanifest.lua file.

    Args:
        name: Resource name
        game: Target game - gta5, rdr3, or both
        language: Scripting language - lua, javascript, or csharp
        framework: Framework - standalone, esx, qbcore, or oxcore
        scripts: Additional script paths to include
        dependencies: Additional resource dependencies
        has_nui: Whether the resource includes NUI (web UI)
    """
    return generate_manifest(name, game, language, framework, scripts, dependencies, has_nui)


@mcp.tool()
def search_events_tool(
    query: str,
    side: str | None = None,
) -> str:
    """Search for common FiveM/RedM events by name or description.

    Args:
        query: Search term (event name or keyword)
        side: Filter by side - client or server (optional)
    """
    return search_events(query, side, NATIVES_PATH)


if __name__ == "__main__":
    mcp.run()
