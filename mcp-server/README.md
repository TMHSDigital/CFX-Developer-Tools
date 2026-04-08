# CFX Developer Tools - MCP Server

A Model Context Protocol (MCP) server that provides AI-powered tools for FiveM and RedM resource development.

## Tools

| Tool | Description |
|------|-------------|
| `scaffold_resource_tool` | Create a new resource with boilerplate files |
| `lookup_native_tool` | Search the native function database by name or description |
| `generate_manifest_tool` | Generate a properly formatted fxmanifest.lua |
| `search_events_tool` | Search the event reference database |

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

The server is configured to run automatically via Cursor's MCP integration (see `.cursor/mcp.json`). To run it manually:

```bash
python server.py
```

## Data files

The `data/` directory contains JSON databases:

- `natives_gta5.json` - GTA5 native function reference
- `natives_rdr3.json` - RDR3 native function reference
- `events.json` - Common FiveM/RedM events

These are snapshots used for offline lookup. For the most current data, refer to the official native reference at https://docs.fivem.net/natives/.
