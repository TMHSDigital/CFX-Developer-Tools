# CFX Developer Tools - MCP Server

A Model Context Protocol (MCP) server that provides AI-powered tools for FiveM and RedM resource development.

## Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `scaffold_resource_tool` | `name`, `game` (gta5, rdr3, both), `language` (lua, javascript, csharp), `framework` (standalone, esx, qbcore, qbox, oxcore, vorp, rsg), `workspace_path`?, `output_path`?, `overwrite`? (default false) | Create a resource with boilerplate files at `<output_path or workspace_path>/<name>`. Refuses to write into an existing non-empty directory unless `overwrite` is true. |
| `lookup_native_tool` | `query`?, `game`? (gta5, rdr3; default gta5), `side`? (client, server, shared), `category`? (e.g. VEHICLE) | Search natives by name (any case, with or without underscores), hash, or description; browse categories. |
| `generate_manifest_tool` | `name`, `game`, `language`, `framework`, `scripts`?, `dependencies`?, `has_nui`?, `workspace_path`? | Return `fxmanifest.lua` content; with `workspace_path`, scripts, author and NUI page are detected from the resource. |
| `validate_manifest_tool` | `path` (resource dir or fxmanifest.lua), `format`? (text, json) | Validate a manifest with the same checks CI runs: fx_version, games, lua54, unresolved script/files/ui_page entries (missing `dist/` build output is a warning), ui_page coverage, framework/game mismatch. |
| `search_events_tool` | `query`?, `side`?, `game`? (gta5, rdr3), `framework`? (cfx, esx, qbcore, qbox, oxcore, vorp, rsg, baseevents, chat) | Search the event reference database. |
| `detect_framework_tool` | `workspace_path`? (default `.`) | Detect ESX, QBCore, Qbox, ox_core, VORP, RSG, standalone, or a multi-framework bridge. |
| `search_docs_tool` | `query`?, `section`? (scripting-manual, scripting-reference, game-references, server-manual, stock-resources, getting-started, developer-docs, support) | Search the offline docs.fivem.net index. |
| `txadmin_server_control_tool` | `action` (start, stop, restart) | Control the FXServer through txAdmin. |
| `txadmin_resource_control_tool` | `action` (start, stop, restart, ensure), `resource` | Control one resource through txAdmin. |
| `txadmin_player_search_tool` | `search_value`?, `search_type`? (playerName, playerNotes, playerIds), `filters`? (isAdmin, isOnline, isWhitelisted, hasNote), `limit`? (default 25) | Search players known to the server. |
| `txadmin_kick_player_tool` | `netid`, `reason`?, `mutex`? (default `current`) | Kick an online player by server id. |

`?` marks optional parameters.

## Setup

### Prerequisites

- Python 3.10+
- pip

### Install dependencies

```bash
cd mcp-server
pip install -r requirements.txt
```

### Run the server

The server runs automatically through your MCP client (see the MCP Server section of the main README for Cursor, Claude Code and generic stdio setup). To run it manually:

```bash
python server.py
```

It finds `data/` next to `server.py`, so it can be started from any working directory.

### Run the tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TXADMIN_URL` | No | `http://127.0.0.1:40120` | Base URL of the txAdmin panel |
| `TXADMIN_USERNAME` | For txAdmin tools | - | Admin username used to log into the panel |
| `TXADMIN_PASSWORD` | For txAdmin tools | - | Admin password |
| `CFX_DATA_PATH` | No | `data/` next to `server.py` | Directory with the native, event and docs data. `CFX_NATIVES_PATH` is accepted as an alias. |
| `CFX_SCAFFOLD_ROOT` | No | server working directory | Where `scaffold_resource_tool` creates resources when neither `output_path` nor `workspace_path` is given |

Set the txAdmin credentials in your OS or shell environment, never in a committed file such as `.cursor/mcp.json` (see `skills/txadmin-integration/SKILL.md`).

## Data files

The `data/` directory contains JSON databases:

- `natives_gta5.json` - GTA5 native function reference (game natives plus the CFX platform natives that apply to GTA5)
- `natives_rdr3.json` - RDR3 native function reference (game natives plus the CFX platform natives that apply to RDR3)
- `events.json` - Common FiveM/RedM events
- `docs_index.json` - Offline index of docs.fivem.net pages (title, URL, section, text snippet)

These are snapshots used for offline lookup, refreshed by the `update-natives.yml` and `update-docs-index.yml` workflows. For the most current data, refer to the official native reference at https://docs.fivem.net/natives/.
