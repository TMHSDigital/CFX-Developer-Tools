# Architecture

This document explains how the CFX Developer Tools plugin and companion MCP server work together.

## Overview

CFX Developer Tools is a Cursor IDE plugin that combines:

1. **Skills** - Detailed instructions that teach the AI agent how to perform CFX-specific tasks
2. **Rules** - Coding conventions the AI follows when generating or reviewing code
3. **Snippets** - Copy-paste-ready code patterns for common tasks
4. **Templates** - Complete resource starters for each framework and language
5. **MCP Server** - A Python server that provides tools the AI can call programmatically

## How the plugin loads

When you open a workspace containing this plugin in Cursor:

1. Cursor reads `.cursor-plugin/plugin.json` and registers the plugin
2. Skills from `skills/` become available to the AI agent
3. Rules from `rules/` are applied based on their glob patterns and `alwaysApply` flags
4. The MCP server defined in `.cursor/mcp.json` starts when a tool is first invoked

## Skills

Each skill is a `SKILL.md` file with YAML frontmatter. Skills teach the AI agent domain-specific knowledge:

- **Resource scaffolding** - How to create new resources from scratch
- **Native functions** - How to find and use GTA5/RDR3 native functions
- **fxmanifest** - How to write correct resource manifests
- **Client-server patterns** - Correct event and thread patterns across all runtimes
- **Framework detection** - How to identify ESX/QBCore/Qbox/ox_core/VORP/RSG/standalone
- **Performance optimization** - Best practices for CFX performance
- **NUI development** - How to build in-game web UIs
- **Database integration** - How to use oxmysql for database queries
- **State Bags** - Modern data synchronization using Entity/Player/Global state bags

Skills are activated based on context (file type, user request) and provide the agent with the technical knowledge to generate correct code.

## Rules

Rules are `.mdc` files with frontmatter specifying when they apply:

- `globs` - File patterns that trigger the rule (e.g. `**/*.lua`)
- `alwaysApply` - If true, the rule is always active regardless of file context

Rules enforce conventions like proper event naming, source validation, performance patterns, and manifest formatting.

## MCP server

The MCP server (`mcp-server/server.py`) runs as a local process and exposes tools via the Model Context Protocol:

```
Cursor AI Agent  --(MCP protocol)-->  MCP Server  --(reads)-->  Data Files
                                          |
                                          +--(generates)-->  Resource Files
```

### Tools

| Tool | Purpose |
|------|---------|
| `scaffold_resource_tool` | Creates a new resource directory with boilerplate. Inherits author from workspace. |
| `lookup_native_tool` | Searches natives by name, hash, description, or category. Supports namespace browsing. |
| `generate_manifest_tool` | Generates fxmanifest.lua content. Auto-detects scripts and NUI from workspace. |
| `search_events_tool` | Searches 101 events by name, side, game, or framework |
| `detect_framework_tool` | Scans workspace files to detect ESX, QBCore, Qbox, ox_core, VORP, RSG, or standalone |
| `search_docs_tool` | Searches the FiveM/RedM documentation index by keyword or section |

### Data files

The `mcp-server/data/` directory contains JSON databases updated by CI:

- `natives_gta5.json` - GTA5 native functions (~6000+ natives, 44 categories) -- updated weekly
- `natives_rdr3.json` - RDR3 native functions (~5800+ natives, 84 categories) -- updated weekly
- `events.json` - 101 FiveM/RedM events across CFX, ESX, QBCore, Qbox, ox_core, VORP, RSG, baseevents, and chat
- `docs_index.json` - ~80 documentation pages from docs.fivem.net -- updated monthly

Native database schema:

```json
{
  "name": "GetVehicleMaxSpeed",
  "hash": "0x1B8F0DE5",
  "params": [{"type": "Vehicle", "name": "vehicle"}],
  "return_type": "float",
  "description": "Returns the max speed of the vehicle.",
  "side": "client",
  "category": "VEHICLE",
  "deprecated": false,
  "examples": "```lua\nlocal speed = GetVehicleMaxSpeed(vehicle)\n```"
}
```

Data is fetched from `runtime.fivem.net/doc/` (GTA5, RDR3, CFX natives) and transformed by `.github/scripts/transform_natives.py`.

## Templates

The `templates/` directory contains starter resource structures for:

- **standalone** - No framework dependency
- **esx** - ESX framework boilerplate
- **qbcore** - QBCore framework boilerplate
- **qbox** - Qbox framework boilerplate (modern QBCore successor)
- **oxcore** - ox_core framework boilerplate
- **vorp** - VORP framework boilerplate (RedM)
- **rsg** - RSG framework boilerplate (RedM)
- **javascript** - JavaScript runtime starter with `node_version '22'`
- **csharp** - C# runtime starter
- **nui-vite** - Modern NUI with Vite + React, postMessage bridge
- **nui-svelte** - Modern NUI with Vite + Svelte 5, Runes, postMessage bridge

Templates are used by the scaffolding tool and can also be copied manually.

## Snippets

The `snippets/` directory contains individual code patterns organized by language:

- `lua/` - Thread loops, events, commands, exports, NUI callbacks, configs, state bags, backtick hashing, routing buckets, variable attributes, ACE permissions
- `javascript/` - Tick loops, events, commands, NUI callbacks, state bags
- `csharp/` - Base scripts, commands, tick handlers

Snippets serve as quick-reference patterns that the AI agent can insert into generated code.
