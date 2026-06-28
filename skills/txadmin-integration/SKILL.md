---
title: txAdmin Integration
description: Connect to a running FiveM/RedM server through txAdmin to control the server, manage resources, search players, and kick players
standards-version: 1.10.0
---

# txAdmin Integration

txAdmin is the server management platform that ships with FXServer. It exposes a web panel (default `http://127.0.0.1:40120`) backed by an HTTP API. This skill connects the MCP server to a running txAdmin instance so you can control the server, manage resources, and act on players without leaving your editor.

The four MCP tools are:

| Tool | Action |
|------|--------|
| `txadmin_server_control_tool` | Start, stop, or restart the FXServer |
| `txadmin_resource_control_tool` | Start, stop, restart, or ensure a single resource |
| `txadmin_player_search_tool` | Search players by name, notes, or identifier |
| `txadmin_kick_player_tool` | Kick an online player by netid |

## Authentication

txAdmin authenticates with the admin account you created during setup. The MCP server logs in with `POST /auth/password`, stores the returned session cookie, and echoes the `csrfToken` back in the `x-txadmin-csrftoken` header on every authenticated request. This is handled automatically.

Credentials are read from environment variables and are never passed as tool arguments or written to the repository:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TXADMIN_URL` | No | `http://127.0.0.1:40120` | Base URL of the txAdmin panel |
| `TXADMIN_USERNAME` | Yes | - | Admin username used to log into the panel |
| `TXADMIN_PASSWORD` | Yes | - | Admin password |

### Setting the variables

Set these in the environment that launches the MCP server. For Cursor, add them to the `env` block of the server entry in `.cursor/mcp.json`, referencing your own values rather than hardcoding secrets where possible:

```json
{
  "mcpServers": {
    "cfx-dev-tools": {
      "command": "python",
      "args": ["mcp-server/server.py"],
      "env": {
        "CFX_NATIVES_PATH": "./mcp-server/data",
        "TXADMIN_URL": "http://127.0.0.1:40120",
        "TXADMIN_USERNAME": "your-admin-name",
        "TXADMIN_PASSWORD": "your-admin-password"
      }
    }
  }
}
```

For a terminal session you can export them instead (PowerShell shown):

```powershell
$env:TXADMIN_USERNAME = "your-admin-name"
$env:TXADMIN_PASSWORD = "your-admin-password"
```

Prefer a dedicated admin account with only the permissions you need. The control and player tools require the matching txAdmin permissions (`control.server`, `commands.resources`, `players.kick`); if the account lacks one, txAdmin returns a permission error and the tool reports it.

## Usage

### Server control

```
txadmin_server_control_tool(action="restart")
```

Valid actions: `start`, `stop`, `restart`. A restart with a long spawn delay is handled asynchronously by txAdmin and reports a warning that the restart is scheduled.

### Resource control

```
txadmin_resource_control_tool(action="ensure", resource="my-resource")
```

Valid actions: `start`, `stop`, `restart`, `ensure`. `ensure` starts the resource if stopped and restarts it if already running - the common choice after editing files. txAdmin blocks starting or restarting the `runcode` resource for safety.

### Player search

```
txadmin_player_search_tool(search_value="John", search_type="playerName")
txadmin_player_search_tool(filters="isOnline,isAdmin")
```

`search_type` is one of `playerName`, `playerNotes`, or `playerIds`. `filters` is a comma-separated subset of `isAdmin`, `isOnline`, `isWhitelisted`, `hasNote`. The search spans both online players and the player database, and the server caps results at 100.

### Kick a player

```
txadmin_kick_player_tool(netid=42, reason="AFK too long")
```

`netid` is the player's server id from the live player list. The kick targets the currently running server instance by default.

## Gotchas

- The txAdmin API is not a formally versioned public REST API. If a future txAdmin release changes a route or response shape, the affected tool will report an error rather than silently misbehave; the routes here track the current source.
- If you run txAdmin behind a reverse proxy, make sure it forwards the `x-txadmin-csrftoken` header, or authenticated requests will be rejected.
- A `Could not reach txAdmin` error usually means the panel is not running, or `TXADMIN_URL` points at the wrong host or port.
- Brute-force protection rate-limits the login route. Repeated wrong credentials will lock out the source IP for several minutes.

## Related skills

- `framework-detection` to identify the framework a resource targets before restarting it.
- `performance-optimization` for diagnosing why a resource needs frequent restarts.
